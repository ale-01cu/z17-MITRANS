from rest_framework import generics
from .serializers import FileUploadSerializer
from rest_framework.parsers import MultiPartParser
from rest_framework.views import status, Response
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from apps.img_process.img_to_text import img_to_text

# Create your views here.
class ImgToTextView(generics.GenericAPIView):
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser]

    def post(self, request):
        # Validación básica del serializer
        file_upload_serializer = self.get_serializer(data=request.data)
        if not file_upload_serializer.is_valid():
            return Response(file_upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            texts = img_to_text(image_path=file)
            return Response({'data': texts}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "Error al procesar la imagen. Por favor intente con otra imagen."},
                status=status.HTTP_400_BAD_REQUEST,
            )