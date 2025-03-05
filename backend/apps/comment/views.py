from apps.comment.serializers import CommentSerializer, FileUploadSerializer
from rest_framework import viewsets, filters
from rest_framework.views import status, Response
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from .pagination import ResultsSetPagination
import pandas as pd
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.
class CommentAPIView(viewsets.ModelViewSet):
    queryset = CommentSerializer.Meta.model.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ResultsSetPagination
    lookup_field = 'external_id'

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        'text',
        'post__content',
        'classification__name',
    ]

    filterset_fields = {
        'created_at': ['gte', 'lte', 'exact'],
    }

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GetCommentsFromExcelView(GenericAPIView):
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        # Paso 1: Validar los datos enviados con FileUploadSerializer
        file_upload_serializer = self.get_serializer(data=request.data)
        if not file_upload_serializer.is_valid():
            return Response(file_upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Paso 2: Obtener el archivo del serializador validado
        file = file_upload_serializer.validated_data['file']

        try:
            # Leer el archivo Excel con pandas
            df = pd.read_excel(file)
            columns = df.columns

            # Verificar que la columna 'text' exista
            if 'text' not in columns:
                return Response(
                    {"error": "Estructura inválida. Falta la columna 'text'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Procesar cada fila del DataFrame y crear comentarios
            comments = [{'text': row.get('text', "")} for _, row in df.iterrows()]

            # Serializar los comentarios con CommentSerializer
            comment_serializer = CommentSerializer(data=comments, many=True)
            if not comment_serializer.is_valid():
                raise Exception("Datos de comentario no válidos")

            # Devolver los datos serializados como respuesta
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Capturar cualquier excepción y devolver un mensaje de error
            return Response(
                {"error": f"Error al procesar el archivo: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateCommentsListView(GenericAPIView):
    serializer_class = CommentSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        try:
            comments_serializer = CommentSerializer(data=request.data, many=True)

            if comments_serializer.is_valid():
                user = request.user
                comments = comments_serializer.save(user=user)

                response_serializer = CommentSerializer(comments, many=True)
                return Response(response_serializer.data,
                                status=status.HTTP_201_CREATED
                                )
            else:
                return Response(comments_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST
                                )

        except Exception as e:
            return Response(
                {"error": f"Error al procesar el archivo: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
