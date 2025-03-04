from apps.comment.serializers import CommentSerializer, FileUploadSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view, parser_classes
from rest_framework.views import status, Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from .pagination import ResultsSetPagination
import pandas as pd


# Create your views here.
class CommentAPIView(viewsets.ModelViewSet):
    queryset = CommentSerializer.Meta.model.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ResultsSetPagination
    lookup_field = 'external_id'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@parser_classes([MultiPartParser])
def get_comments_from_excel(request, *args, **kwargs):
    serializer = FileUploadSerializer(data=request.data)
    user = request.user

    if serializer.is_valid():
        file = serializer.validated_data['file']

        try:
            # Leer el archivo Excel con pandas
            df = pd.read_excel(file)
            columns = df.columns

            if 'text' not in columns:
                return Response(
                    {"error": f"Estructura invalida."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            comments = []

            # Iterar sobre cada fila del DataFrame
            for index, row in df.iterrows():
                text = row.get('text', "")
                comment = {'text': text}
                comments.append(comment)

            serializer = CommentSerializer(data=comments, many=True)

            if serializer.is_valid():
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            else:
                raise Exception("Invalid Data")

        except Exception as e:
            return Response(
                {"error": f"Error al procesar el archivo: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                        )


@api_view(['POST'])
def create_comments_list(request, *args, **kwargs):
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