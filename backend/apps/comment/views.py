from apps.comment.serializers import CommentSerializer, FileUploadSerializer, ClassificationsByCommentsSerializer
from rest_framework import viewsets, filters
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
