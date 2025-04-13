from django.db import transaction
from rest_framework import generics
from rest_framework.views import status, Response, APIView
from .serializers import ClassificationSerializer, ClassifyCommentByIdSerializer, CommentTextSerializer
from rest_framework.generics import GenericAPIView
from apps.comment.serializers import CommentSerializer
from core.errors import Errors
from .models import Classification
from apps.comment.models import Comment
from rest_framework import serializers
from apps.classification.ml.model_loader import predict_comment_label
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class ClassificationListApiView(generics.ListAPIView):
    queryset = ClassificationSerializer.Meta.model.objects.all()
    serializer_class = ClassificationSerializer


class ClassifyCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Valida solo el campo 'text'
                serializer = CommentTextSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                text = serializer.validated_data['text']  # Extrae el texto validado

                # Clasifica el comentario
                classification_result = predict_comment_label(text)

                return Response({
                    "data": {
                        "text": text,
                        "classification": classification_result,
                        # 'id' ya no es necesario, pues no se guarda en la base de datos
                    }
                }, status=status.HTTP_200_OK)

        except serializers.ValidationError as ve:
            return Response({"error": ve.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"detail": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClassifyCommentsByIdsView(GenericAPIView):
    permission_classes = [IsAuthenticated]  # Opcional

    def get(self, request, *args, **kwargs):
        try:
            # 1. Obtener la lista de IDs desde el query param 'ids' (ej: ?ids=1,2,3)
            ids_str = request.query_params.get('ids', '')
            ids_list = [id.strip() for id in ids_str.split(',') if id.strip()]

            if not ids_list:
                return Response(
                    {"detail": "Se requiere al menos un ID en el parámetro 'ids'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. Procesar cada comentario
            results = []
            for comment_id in ids_list:
                try:
                    comment = Comment.objects.get(external_id=comment_id)
                    classification = predict_comment_label(comment.text)
                    results.append({
                        "id": comment.external_id,
                        "text": comment.text,
                        "classification": classification
                    })
                except Comment.DoesNotExist:
                    results.append({
                        "id": comment_id,
                        "error": "Comentario no encontrado"
                    })

            return Response({"data": results}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
