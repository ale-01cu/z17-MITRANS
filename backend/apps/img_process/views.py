from rest_framework import generics
from .serializers import MultipleFileUploadSerializer
from rest_framework.parsers import MultiPartParser
from rest_framework.views import status, Response
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from apps.img_process.img_to_text import img_to_text
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import cv2
import numpy as np
import uuid

# Create your views here.
class ImgToTextView(APIView):
    # Usa el nuevo serializer
    serializer_class = MultipleFileUploadSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # device_type ya no se obtiene de query_params si lo mueves al serializer
        # device_type = request.query_params.get('device_type', 'desktop').lower()
        # if device_type not in ['mobile', 'desktop']:
        #     device_type = 'desktop'

        # Valida usando el serializer de múltiples archivos
        serializer = self.serializer_class(data=request.data) # Usar self.get_serializer es buena práctica

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        # Obtenemos la LISTA de archivos validados
        files = serializer.validated_data['files']

        # --- Constantes de Validación ---
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        extension_validator = FileExtensionValidator(allowed_extensions)
        valid_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
        max_size = 5 * 1024 * 1024  # 5MB

        # --- Lista para almacenar los resultados de cada imagen ---
        results = []

        # --- Itera sobre cada archivo subido ---
        for file in files:
            file_result = {
                "filename": file.name,
                "status": "processing", # Estado inicial
                "data": None,
                "error": None
            }

            try:
                # 1. Validación de extensión
                try:
                    extension_validator(file)
                except ValidationError:
                    raise ValidationError(f"Formato de archivo no soportado ({file.name}). Formatos permitidos: {', '.join(allowed_extensions)}")

                # 2. Validación del tipo MIME
                if file.content_type not in valid_mime_types:
                    raise ValidationError(f"Tipo MIME no válido ({file.name} - {file.content_type}). Tipos permitidos: {', '.join(valid_mime_types)}")

                # 3. Validación del tamaño
                if file.size > max_size:
                    raise ValidationError(f"El archivo '{file.name}' es demasiado grande ({file.size / 1024 / 1024:.2f}MB). Tamaño máximo: {max_size / 1024 / 1024}MB")

                # 4. Validación de imagen válida (opcional pero recomendado)
                # try:
                #     file.seek(0) # Asegurarse de estar al inicio del stream
                #     image_pil = Image.open(io.BytesIO(file.read()))
                #     image_pil.verify()
                #     file.seek(0) # Volver al inicio para cv2
                # except Exception as img_err:
                #     print(f"Error verifying {file.name}: {img_err}")
                #     raise ValidationError(f"El archivo '{file.name}' no es una imagen válida o está corrupta.")


                # --- Procesamiento de la imagen (si pasa validaciones) ---
                file.seek(0) # Asegurarse de estar al inicio antes de leer para cv2
                file_bytes = file.read()
                np_array = np.frombuffer(file_bytes, np.uint8)
                img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                # Verifica si cv2 pudo decodificar la imagen
                if img is None:
                     raise ValueError(f"No se pudo decodificar la imagen '{file.name}'. Puede estar corrupta o no ser un formato de imagen válido.")

                text = img_to_text(image=img)
                sentences = [line.strip() for line in text.split('\n') if line.strip()]

                sentences_with_ids = [
                    {"id": str(uuid.uuid4()), "text": sentence}
                    for sentence in sentences
                ]

                file_result["status"] = "success"
                file_result["data"] = sentences_with_ids

            except ValidationError as e:
                # Captura errores de validación específicos
                print(f"Validation Error for {file.name}: {e.message}")
                file_result["status"] = "validation_error"
                file_result["error"] = e.message # Usa el mensaje de la validación
            except ValueError as e:
                 # Captura errores específicos como el de cv2.imdecode
                print(f"Value Error for {file.name}: {e}")
                file_result["status"] = "processing_error"
                file_result["error"] = str(e)
            except Exception as e:
                # Captura cualquier otro error durante el procesamiento
                print(f"Processing Error for {file.name}: {e}") # Loguea el error real
                file_result["status"] = "processing_error"
                file_result["error"] = "Error desconocido al procesar la imagen." # Mensaje genérico al usuario

            # Añade el resultado (éxito o error) de este archivo a la lista general
            results.append(file_result)

        # Devuelve la lista de resultados para todas las imágenes
        return Response(results, status=status.HTTP_200_OK)