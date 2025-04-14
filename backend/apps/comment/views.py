from apps.comment.serializers import CommentSerializer, FileUploadSerializer, ClassificationsByCommentsSerializer
from rest_framework import viewsets, filters, generics
from rest_framework.views import status, Response
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from .pagination import ResultsSetPagination
import pandas as pd
from django_filters.rest_framework import DjangoFilterBackend
from core.errors import Errors
from django.db.models import Count
from apps.classification.models import Classification
from apps.source.models import Source
from rest_framework.generics import ListAPIView
from datetime import timedelta
from django.utils import timezone

# Create your views here.
class CommentAPIView(viewsets.ModelViewSet):
    queryset = CommentSerializer.Meta.model.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ResultsSetPagination
    lookup_field = 'external_id'

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    search_fields = [
        'text',
        'post__content',
        'classification__name',
        # 'user_owner_id',
        # 'source_id',
    ]

    filterset_fields = {
        'created_at': ['gte', 'lte', 'exact'],
        'classification__name': ['exact'],
        'user_owner__external_id': ['exact'],
        'source__external_id': ['exact'],
    }

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GetCommentsFromExcelView(GenericAPIView):
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        file_upload_serializer = self.get_serializer(data=request.data)
        if not file_upload_serializer.is_valid():
            return Response(file_upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = file_upload_serializer.validated_data['file']

        try:
            df = pd.read_excel(file)
            columns = df.columns

            if 'text' not in columns:
                return Response(
                    {"detail": Errors.COMMENT_NOT_FOUND},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            comments = [{'text': row.get('text', "")}
                        for _, row in df.iterrows()
                        ]

            comment_serializer = CommentSerializer(data=comments, many=True)
            if not comment_serializer.is_valid():
                raise Exception(Errors.INTERNAL_SERVER_ERROR)

            return Response(comment_serializer.data,
                            status=status.HTTP_201_CREATED
                            )

        except Exception as e:
            return Response(
                {"detail": Errors.INTERNAL_SERVER_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateCommentsView(GenericAPIView):
    serializer_class = CommentSerializer
    queryset = CommentSerializer.Meta.model.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            comments_serializer = CommentSerializer(data=request.data, many=True)

            if comments_serializer.is_valid():
                user = request.user
                source = Source.objects.get(name='Messenger')
                comments = comments_serializer.save(user=user, source_id=source.external_id)

                response_serializer = CommentSerializer(comments, many=True)
                return Response(response_serializer.data,
                                status=status.HTTP_201_CREATED
                                )
            else:
                return Response(comments_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST
                                )

        except Exception as e:
            print("CreateCommentsView Error: " + e.__str__())
            return Response(
                {"detail": Errors.INTERNAL_SERVER_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ClassificationsByCommentsView(GenericAPIView):
    serializer_class = ClassificationsByCommentsSerializer

    def get(self, request, *args, **kwargs):
        try:
            classification_counts = Classification.objects.annotate(
                comment_count=Count('comment')
            ).values('name', 'comment_count')

            result = {
                item['name']: item['comment_count']
                for item in classification_counts
            }
            result = {"data": result}

            response = ClassificationsByCommentsSerializer(data=result)
            if not response.is_valid():
                raise Exception(Errors.COMMENT_INVALID_DATA)

            return Response(response.data, status=status.HTTP_200_OK)


        except Exception as e:
            print("ClassificationsByCommentsView Error: " + e.__str__())
            return Response(
                {"detail": Errors.INTERNAL_SERVER_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )



class NewCommentsListView(generics.ListAPIView):
    """
    Vista para listar comentarios no leídos creados en las últimas 24 horas.
    Opcionalmente filtra por user_id y/o post_id pasados como query params.
    """
    serializer_class = CommentSerializer

    def get_queryset(self):
        # Calcula la fecha y hora de hace 24 horas
        now = timezone.now()
        twenty_four_hours_ago = now - timedelta(hours=24)

        # Filtra comentarios no leídos Y creados desde hace 24 horas
        queryset = CommentSerializer.Meta.model.objects.filter(
            is_read=False,
            created_at__gte=twenty_four_hours_ago # __gte significa "greater than or equal to"
        )

        # Obtiene los parámetros opcionales de la URL
        user_id = self.request.query_params.get('user_id')
        post_id = self.request.query_params.get('post_id')

        # Aplica filtros opcionales si se proporcionaron
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if post_id:
            queryset = queryset.filter(post_id=post_id)

        # Opcional: Ordena los resultados por fecha de creación (más nuevos primero)
        queryset = queryset.order_by('-created_at')

        return queryset


class UrgentCommentsView(ListAPIView):
    """
    API View para listar comentarios clasificados como 'pregunta' o 'denuncia'.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated] # Requiere autenticación
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        """
        Sobrescribe el método para devolver solo los comentarios urgentes.
        """
        # Nombres de las clasificaciones consideradas urgentes
        urgent_classification_names = ['pregunta', 'denuncia']

        # Filtra los comentarios cuya clasificación relacionada (FK)
        # tiene un nombre que está en la lista 'urgent_classification_names'
        queryset = CommentSerializer.Meta.model.objects.filter(
            classification__name__in=urgent_classification_names
        )

        # Optimización: Pre-carga las relaciones que usará el serializer
        # para evitar consultas N+1 a la base de datos.
        queryset = queryset.select_related('classification', 'user', 'source', 'post', 'user_owner')

        # Opcional: Ordena los resultados (ej: los más recientes primero)
        queryset = queryset.order_by('-created_at')

        return queryset