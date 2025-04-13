from django.db import transaction
from rest_framework import generics
from rest_framework.views import status, Response, APIView
from .serializers import ClassificationSerializer, CommentTextSerializer, MultipleCommentObjectSerializer
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
    # Referencia al nuevo serializer que espera la lista de objetos
    serializer_class = MultipleCommentObjectSerializer

    def post(self, request, *args, **kwargs):
        # Instancia y valida usando el serializer para la lista de objetos
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as ve:
            # Error de validación del formato de entrada (ej: falta 'items',
            # 'items' no es lista, objetos inválidos dentro de la lista)
            return Response({"error": "Invalid input format.", "details": ve.detail}, status=status.HTTP_400_BAD_REQUEST)

        # Extrae la LISTA de objetos validados (cada objeto es un diccionario)
        comment_objects = serializer.validated_data['items']

        results = []

        # Itera sobre cada objeto de comentario recibido
        for comment_obj in comment_objects:
            current_id = comment_obj['id']
            current_text = comment_obj['text']
            result_item = {
                "id": current_id,
                "text": current_text, # Opcional: incluir el texto original en la respuesta
                "classification": None,
                "error": None
            }

            try:
                # Clasifica el texto del objeto actual
                classification_result = predict_comment_label(current_text)
                classification_obj = Classification.objects.get(name=classification_result)
                serializer = ClassificationSerializer(classification_obj)
                classification_dict = serializer.data
                result_item["classification"] = classification_dict

            except Exception as e:
                # Error específico durante la clasificación de ESTE texto
                print(f"Error classifying text for ID {current_id}: {e}") # Loguea el error
                result_item["error"] = f"Error during classification for this item." # Mensaje genérico

            # Añade el resultado (éxito o error) para este ID a la lista
            results.append(result_item)

        # Devuelve la lista completa de resultados, cada uno asociado a su ID
        return Response({"data": results}, status=status.HTTP_200_OK)


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
                status_item = {"id": comment_id,
                               "text": None,
                               'classification': None,
                               "error": None, "status": None
                               }
                try:
                    comment = Comment.objects.get(external_id=comment_id)
                    classification_label = predict_comment_label(comment.text)
                    status_item['text'] = comment.text

                    # Obtiene el objeto Classification correspondiente
                    try:
                        classification_obj = Classification.objects.get(name=classification_label)
                        serializer = ClassificationSerializer(classification_obj)
                        classification_dict = serializer.data
                        status_item['classification'] = classification_dict

                        # --- Actualiza y Guarda el Comentario ---
                        comment.classification = classification_obj  # Asigna el objeto FK
                        comment.save(update_fields=['classification'])  # Guarda solo el campo modificado
                        # ---------------------------------------

                        status_item['status'] = 'updated'

                    except Classification.DoesNotExist:
                        # Error: La etiqueta predicha no existe en la BD
                        # NO se actualiza el comentario. La transacción general puede continuar o detenerse.
                        # Aquí elegimos continuar pero marcar este ID con error.
                        error_msg = f"Classification label '{classification_label}' not found in DB."
                        print(f"Error for comment {comment_id}: {error_msg}")  # Loguear
                        status_item['status'] = 'error'
                        status_item['error'] = error_msg

                    except Exception as pred_err:
                        # Captura otros errores durante predicción o obtención de Classification
                        error_msg = f"Error predicting/fetching classification: {pred_err}"
                        print(f"Error for comment {comment_id}: {error_msg}")
                        status_item['status'] = 'error'
                        status_item['error'] = error_msg


                except Comment.DoesNotExist:
                    # Error: Comentario no encontrado
                    status_item['status'] = 'error'
                    status_item['error'] = 'Comment not found'

                except Exception as e:
                    # Captura otros errores (ej. al guardar comment.save())
                    # ¡ESTE TIPO DE ERROR SÍ DEBERÍA ROMPER LA TRANSACCIÓN!
                    # Podemos relanzarlo o manejarlo y retornar un 500 general.
                    # Por simplicidad aquí, lo registramos y marcamos como error.
                    # Pero si save() falla, la transacción hará rollback.
                    print(f"Critical error processing comment {comment_id}: {e}")
                    status_item['status'] = 'error'
                    status_item['error'] = f'Server error during processing: {e}'

                results.append(status_item)

            return Response({"data": results}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




