from rest_framework import generics
from .serializers import FileUploadSerializer
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
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Validación básica del serializer
        device_type = request.query_params.get('device_type', 'desktop').lower()
        if device_type not in ['mobile', 'desktop']:
            device_type = 'desktop'

        file_upload_serializer = FileUploadSerializer(data=request.data)

        if not file_upload_serializer.is_valid():
            return Response(file_upload_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        file = file_upload_serializer.validated_data['file']

        # 1. Validación de extensión del archivo
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        extension_validator = FileExtensionValidator(allowed_extensions)

        try:
            extension_validator(file)
        except ValidationError:
            return Response(
                {"detail": f"Formato de archivo no soportado. Formatos permitidos: {', '.join(allowed_extensions)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Validación del tipo MIME
        valid_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
        if file.content_type not in valid_mime_types:
            return Response(
                {"detail": f"Tipo MIME no válido. Tipos permitidos: {', '.join(valid_mime_types)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Validación del tamaño del archivo (ejemplo: máximo 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if file.size > max_size:
            return Response(
                {"detail": "El archivo es demasiado grande. Tamaño máximo permitido: 5MB"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Validación de que sea una imagen válida (intentando abrirla)
        # try:
        #     # Leemos el archivo en memoria sin guardarlo
        #     image = Image.open(io.BytesIO(file.read()))
        #     # Verificamos que sea una imagen válida
        #     image.verify()
        #     # Volvemos al inicio del archivo para futuras operaciones
        #     file.seek(0)
        # except Exception as e:
        #     return Response(
        #         {"detail": "El archivo no es una imagen válida o está corrupta"},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # Si pasa todas las validaciones, procesamos la imagen
        try:
            file_bytes = file.read()  # Leer bytes del archivo
            np_array = np.frombuffer(file_bytes, np.uint8)  # Convertir a numpy array
            img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)  # Decodificar a imagen OpenCV
            text = img_to_text(image=img)
            sentences = [line.strip() for line in text.split('\n') if line.strip()]

            # Creamos lista de diccionarios con ID único
            sentences_with_ids = [
                {
                    "id": str(uuid.uuid4()),  # Generamos un UUID único para cada oración
                    "text": sentence
                }
                for sentence in sentences
            ]

            return Response(
                sentences_with_ids,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print('Error: ', e)
            return Response(
                {"detail": "Error al procesar la imagen. Por favor intente con otra imagen."},
                status=status.HTTP_400_BAD_REQUEST,
            )