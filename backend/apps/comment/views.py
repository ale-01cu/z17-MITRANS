from django.http import HttpResponse
from apps.comment.serializers import (
    CommentSerializer, FileUploadSerializer,
    ClassificationsByCommentsSerializer, CommentFromExcelSerializer
)
from rest_framework import viewsets, filters, generics
from rest_framework.views import status, Response, APIView
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
from datetime import timedelta, datetime
from django.utils import timezone
from django.utils.timezone import now
from openpyxl import Workbook
import uuid
import logging
from typing import Dict, Any, List, Optional
from rest_framework.request import Request
from django.core.exceptions import ObjectDoesNotExist
logger = logging.getLogger(__name__)


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
        'user_owner__name',
        'source__name',
        'created_at',
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

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        # 1. Filtro por entidad del usuario autenticado (si no es superusuario)
        # if self.request.user.entity is None return empty value
        if user.is_superuser:
            return queryset.all()

        if hasattr(user, 'entity') and user.entity:
            queryset = queryset.filter(entity=user.entity).select_related('entity')

        else:
            return queryset.none()

        # 2. Filtro opcional por horas (manteniendo la lógica existente)
        hours = self.request.query_params.get('last_hours')
        if hours:
            try:
                hours = int(hours)
                time_threshold = now() - timedelta(hours=hours)
                queryset = queryset.filter(created_at__gte=time_threshold)
            except ValueError:
                pass  # Ignorar si el parámetro no es válido

        return queryset


REQUIRED_FIELDS: List[str] = ['Comentario', 'Fuente']
OPTIONAL_FIELDS_MAPPING: Dict[str, str] = {
    'id': 'ID',
    'text': 'Comentario',
    'source': 'Fuente',
    'user': 'Usuario',
    'user_owner': 'Usuario Propietario',
    'classification': 'Clasificación',
    'created_at': 'Fecha de creación',
}


class GetCommentsFromExcelView(APIView):
    """
    API View para cargar un archivo Excel, extraer comentarios y devolverlos
    en formato JSON después de validarlos.
    """
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Maneja la solicitud POST para procesar el archivo Excel cargado.

        Args:
            request: El objeto de solicitud HTTP.

        Returns:
            Una respuesta HTTP con los comentarios validados o un error.
        """
        # 1. Validar el archivo cargado
        file_upload_serializer = FileUploadSerializer(data=request.data)
        if not file_upload_serializer.is_valid():
            logger.warning(f"Validación de carga de archivo fallida: {file_upload_serializer.errors}")
            return Response(
                {"detail": "Error en la carga del archivo.", "errors": file_upload_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        file = file_upload_serializer.validated_data['file']

        try:
            # 2. Leer el archivo Excel
            # Añadir 'engine='openpyxl'' si sólo se soportan archivos .xlsx
            try:
                # Intentar leer como flotante para detectar mejor números como IDs
                df = pd.read_excel(file, dtype=str)
                # Reemplazar NaN (que puede venir de celdas vacías) por None o strings vacíos donde sea apropiado
                df = df.fillna("")
            except (pd.errors.ParserError, ValueError, ImportError, Exception) as e:
                # Captura errores comunes de lectura/parseo de pandas o dependencias faltantes (xlrd, openpyxl)
                logger.error(f"Error al leer el archivo Excel: {e}", exc_info=True)
                return Response(
                    {
                        "detail": f"No se pudo leer el archivo Excel. Asegúrate de que el formato es correcto y no está corrupto. Error: {type(e).__name__}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.info(f"Archivo Excel leído correctamente. Columnas: {df.columns.tolist()}")

            # 3. Verificar que los campos obligatorios estén presentes
            missing_fields = [field for field in REQUIRED_FIELDS if field not in df.columns]
            if missing_fields:
                logger.warning(f"Faltan columnas obligatorias en el archivo: {missing_fields}")
                return Response(
                    {
                        "detail": f"Los siguientes campos obligatorios faltan en el archivo Excel: {', '.join(missing_fields)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 4. Convertir el DataFrame a una lista de diccionarios
            comments_data: List[Dict[str, Any]] = []
            for index, row in df.iterrows():
                try:
                    comment_id = row.get(OPTIONAL_FIELDS_MAPPING['id'], None)
                    # Asegurar que el ID sea siempre un string, incluso si viene como número
                    comment_id_str = str(comment_id).strip() if comment_id and str(comment_id).strip() else None

                    if not comment_id_str:
                        comment_id_str = str(uuid.uuid4())

                    classification_name = str(row.get(OPTIONAL_FIELDS_MAPPING['classification'], "")).strip()
                    classification_obj: Optional[Classification] = None  # Start with None

                    if classification_name:  # Only lookup if name exists
                        try:
                            # --- Database Lookup ---
                            classification_obj = Classification.objects.get(name__iexact=classification_name)
                            # print(f"Fila {row_number}: Clasificación encontrada: {classification_obj}") # Optional debug print

                        except ObjectDoesNotExist:
                            error_msg = f"La clasificación '{classification_name}' no existe en la base de datos."
                            logger.warning(error_msg)
                            return Response({"detail": error_msg}, status=status.HTTP_400_BAD_REQUEST)

                        except Exception as e:
                            logger.error(
                                f"Error buscando clasificación '{classification_name}'",
                                exc_info=True)
                            return Response(
                                {"detail": f"Error interno al buscar la clasificación"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    comment_data = {
                        'id': comment_id_str,
                        'text': str(row.get(OPTIONAL_FIELDS_MAPPING['text'], "")).strip(),
                        # Asegurar string y quitar espacios
                        'source': str(row.get(OPTIONAL_FIELDS_MAPPING['source'], "")).strip(),
                        # Asegurar string y quitar espacios
                        'user': str(row.get(OPTIONAL_FIELDS_MAPPING['user'])) if row.get(
                            OPTIONAL_FIELDS_MAPPING['user']) else None,
                        'user_owner': str(row.get(OPTIONAL_FIELDS_MAPPING['user_owner'])) if row.get(
                            OPTIONAL_FIELDS_MAPPING['user_owner']) else None,
                        'classification_id': classification_obj.external_id if classification_obj else None,
                        'classification_name': classification_obj.name if classification_obj else None,
                        'created_at': row.get(OPTIONAL_FIELDS_MAPPING['created_at']) or None,
                        # Aceptar varios formatos de 'vacío'
                    }
                    comments_data.append(comment_data)

                except (KeyError, AttributeError, TypeError) as e:
                    # Captura errores si una columna esperada (incluso opcional) causa problemas al accederla o convertirla
                    logger.error(f"Error procesando la fila {index + 2} del Excel: {e}. Data: {row.to_dict()}",
                                 exc_info=True)
                    return Response(
                        {
                            "detail": f"Error al procesar los datos en la fila {index + 2} del archivo Excel. Verifique los tipos de datos y el contenido. Error: {type(e).__name__}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if not comments_data:
                logger.info("El archivo Excel no contiene filas de datos procesables.")
                return Response(
                    {"detail": "El archivo Excel está vacío o no contiene datos válidos."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 5. Validar los datos extraídos con el serializador de comentarios
            comment_serializer = CommentFromExcelSerializer(data=comments_data, many=True)
            if not comment_serializer.is_valid():
                logger.warning(f"Validación de datos de comentarios fallida: {comment_serializer.errors}")
                # Podrías querer mostrar sólo el primer error o un resumen
                # error_detail = next(iter(comment_serializer.errors.values()))[0] if comment_serializer.errors else "Error desconocido"
                return Response(
                    {"detail": "Los datos extraídos del Excel no son válidos.", "errors": comment_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 6. Devolver los datos validados
            logger.info(f"Procesados {len(comment_serializer.data)} comentarios exitosamente.")
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)  # Mantenido 201 como solicitado

        except Exception as e:
            # Captura cualquier otro error inesperado
            logger.exception(
                f"Error interno inesperado al procesar el archivo Excel: {e}")  # logger.exception incluye traceback
            return Response(
                {
                    "detail": "Ocurrió un error interno en el servidor al procesar el archivo. Por favor, contacte al administrador."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ExportCommentsExcel(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener el parámetro opcional 'ids' de la solicitud
        ids_param = request.query_params.get('ids', None)

        # Filtrar los comentarios según los IDs proporcionados o obtener todos
        if ids_param:
            try:
                # Convertir los IDs de cadena separada por comas a una lista de enteros
                ids_list = list(ids_param.split(','))
                comments = CommentSerializer.Meta.model.objects.filter(external_id__in=ids_list)
            except ValueError:
                print("Error: Los IDs deben ser números enteros separados por comas.")
                # Manejar el caso en que los IDs no sean números válidos
                return Response({"error": "Los IDs deben ser números enteros separados por comas."}, status=400)
        else:
            # Si no se proporcionan IDs, obtener todos los comentarios
            comments = CommentSerializer.Meta.model.objects.all()

        # Serializar los comentarios
        serializer = CommentSerializer(comments, many=True)

        # Crear el libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Comentarios"

        # Escribir los encabezados
        headers = [
            "ID", "Comentario", "Usuario",
            "Usuario Propietario", "Clasificación",
            "Fuente", "Fecha de creación"
        ]
        ws.append(headers)

        # Escribir los datos
        for comment in serializer.data:
            print("comment: ", comment)
            ws.append([
                comment['id'],
                comment['text'],
                comment['user']['username'] if comment['user'] is not None else None,
                comment['user_owner']['name'] if comment['user_owner'] is not None else None,
                comment['classification']['name'] if comment['classification'] is not None else None,
                comment['source']['name'],
                comment['created_at'],
            ])

        # Configurar la respuesta HTTP
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"comentarios_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename={filename}'

        # Guardar el libro de Excel en la respuesta
        wb.save(response)

        return response


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
        twenty_four_hours_ago = now - timedelta(hours=72)

        # Filtra comentarios no leídos Y creados desde hace 24 horas
        queryset = CommentSerializer.Meta.model.objects.filter(
            created_at__gte=twenty_four_hours_ago  # __gte significa "greater than or equal to"
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
    permission_classes = [IsAuthenticated]  # Requiere autenticación
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        """
        Sobrescribe el método para devolver solo los comentarios urgentes.
        """
        # Nombres de las clasificaciones consideradas urgentes
        urgent_classification_names = ['pregunta', 'denuncia']

        # Filtra los comentarios cuya clasificación relacionada (FK)
        # tiene un nombre que está en la lista 'urgent_classification_names'
        now = timezone.now()
        twenty_four_hours_ago = now - timedelta(hours=24)

        queryset = CommentSerializer.Meta.model.objects.filter(
            created_at__gte=twenty_four_hours_ago,  # __gte significa "greater than or equal to"
            classification__name__in=urgent_classification_names
        )

        # Optimización: Pre-carga las relaciones que usará el serializer
        # para evitar consultas N+1 a la base de datos.
        queryset = queryset.select_related('classification', 'user', 'source', 'post', 'user_owner')

        # Opcional: Ordena los resultados (ej: los más recientes primero)
        queryset = queryset.order_by('-created_at')

        return queryset
