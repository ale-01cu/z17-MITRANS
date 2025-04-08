from django.db import transaction
from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import status, Response, APIView
from .serializers import ClassificationSerializer, ClassifyCommentByIdSerializer
from rest_framework.generics import GenericAPIView
from apps.comment.serializers import CommentSerializer
from core.errors import Errors
from .models import Classification
from apps.comment.models import Comment
from ..comment import serializers


# Create your views here.
class ClassificationListApiView(generics.ListAPIView):
    queryset = ClassificationSerializer.Meta.model.objects.all()
    serializer_class = ClassificationSerializer


class ClassifyCommentView(APIView):
    serializer_class = CommentSerializer

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Valida todos los campos del Comment
                comment = CommentSerializer(data=request.data)
                comment.is_valid(raise_exception=True)
                comment_obj = comment.save()

                # TODO: Integrar modelo de clasificación real
                classification_result = "positivo"

                Classification.objects.create(
                    comment=comment_obj,
                    classification_type=classification_result
                )

                return Response({
                    "data": {
                        "text": comment_obj.text,
                        "classification": classification_result,
                        "id": comment_obj.id  # ⬅️ Asumiendo que el modelo tiene 'id'
                    }
                }, status=status.HTTP_200_OK)

        except serializers.ValidationError as ve:
            return Response({"error": ve.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # logger.error(f"Error interno: {str(e)}")
            return Response(
                {"detail": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClassifyCommentsByIdView(GenericAPIView):
    serializer_class = ClassifyCommentByIdSerializer

    def post(self, request, *args, **kwargs):
        try:
            comments_ids = ClassifyCommentByIdSerializer(data=request.data)

            if not comments_ids.is_valid():
                return Response(comments_ids.errors,
                                status=status.HTTP_400_BAD_REQUEST
                                )

            comments_classificated = []
            
            # Obtener los IDs validados del serializador - corregido para usar 'data' en lugar de 'ids'
            ids_list = comments_ids.validated_data.get('data', [])

            for comment_id in ids_list:
                try:
                    comment = Comment.objects.get(external_id=comment_id)
                    text = comment.text

                    if not text:
                        continue

                    # TODO Pasar el comentario por el modelo...
                    # Por ahora, asumimos un resultado de clasificación
                    classification_result = "positivo"  # Reemplazar con la predicción real del modelo
                    
                    # Guardar la clasificación
                    classification = Classification.objects.create(
                        comment=comment,
                        classification_type=classification_result
                    )

                    comments_classificated.append({
                        "text": text,
                        "classification": classification_result,
                        "id": comment_id
                    })
                except Comment.DoesNotExist:
                    continue

            return Response({"data": comments_classificated},
                            status=status.HTTP_200_OK
                            )

        except Exception as e:
            return Response({"detail": Errors.INTERNAL_SERVER_ERROR},
                            status=status.HTTP_400_BAD_REQUEST
                            )
