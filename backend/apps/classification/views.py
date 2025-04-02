from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import status, Response
from .serializers import ClassificationSerializer, ClassifyCommentByIdSerializer
from rest_framework.generics import GenericAPIView
from apps.comment.serializers import CommentSerializer
from core.errors import Errors
from .models import Classification
from apps.comment.models import Comment


# Create your views here.
class ClassificationListApiView(generics.ListAPIView):
    queryset = ClassificationSerializer.Meta.model.objects.all()
    serializer_class = ClassificationSerializer


class ClassifyCommentView(GenericAPIView):
    serializer_class = CommentSerializer

    def post(self, request, *args, **kwargs):
        try:
            # Corregido para manejar correctamente los datos del comentario
            comment_data = request.data.get('text')
            
            # Si es un diccionario, usarlo directamente; si es una cadena, crear un diccionario
            if isinstance(comment_data, str):
                comment_data = {'text': comment_data}
                
            comment = CommentSerializer(data=comment_data)

            if not comment.is_valid():
                return Response(comment.errors,
                                status=status.HTTP_400_BAD_REQUEST
                                )

            text = comment.validated_data.get('text', '')

            if not text:
                return Response({"error": "Texto vacío"},
                                status=status.HTTP_400_BAD_REQUEST
                                )

            # Verificar si se necesita source_id para crear un comentario
            if 'source_id' not in comment.validated_data and Comment._meta.get_field('source').null is False:
                # Si source es requerido, añadir un source por defecto o devolver error
                return Response({"error": "Se requiere source_id para crear un comentario"},
                                status=status.HTTP_400_BAD_REQUEST
                                )

            # Guardar el comentario primero
            comment_obj = comment.save()  # Usar el método save del serializador
            
            # TODO Pasar el comentario por el modelo...
            # Por ahora, asumimos un resultado de clasificación
            classification_result = "positivo"  # Reemplazar con la predicción real del modelo
            
            # Guardar la clasificación
            classification = Classification.objects.create(
                comment=comment_obj,
                classification_type=classification_result
            )

            return Response({"data": {"text": text, "classification": classification_result, "id": comment_obj.external_id}},
                            status=status.HTTP_200_OK
                            )

        except Exception as e:
            return Response({"detail": Errors.INTERNAL_SERVER_ERROR},
                            status=status.HTTP_400_BAD_REQUEST
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
