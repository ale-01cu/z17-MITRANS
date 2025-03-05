from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import status, Response
from .serializers import ClassificationSerializer, ClassifyCommentByIdSerializer
from rest_framework.generics import GenericAPIView
from apps.comment.serializers import CommentSerializer
from core.errors import Errors


# Create your views here.
class ClassificationListApiView(generics.ListAPIView):
    queryset = ClassificationSerializer.Meta.model.objects.all()
    serializer_class = ClassificationSerializer


class ClassifyCommentView(GenericAPIView):
    serializer_class = CommentSerializer

    def post(self, request, *args, **kwargs):
        try:
            comment = CommentSerializer(data=request.data.get('text'))

            if not comment.is_valid():
                return Response(comment.errors,
                                status=status.HTTP_400_BAD_REQUEST
                                )

            text = comment.validated_data['text']

            if not text:
                return Response({"error": "Texto vacío"},
                                status=status.HTTP_400_BAD_REQUEST
                                )

            # TODO Pasar el comentario por el modelo...
            #
            #
            #

            return Response({"data": {"text": text, "classification": ""}},
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

            for id in comments_ids:
                comment = CommentSerializer.Meta.model.objects.get(external_id=id)
                text = comment.text

                if not text:
                    continue

                # TODO Pasar el comentario por el modelo...
                #
                #

                comments_classificated.append({"text": text})

            comments_serializer = CommentSerializer(comments_classificated, many=True)
            comments_serializer.validate()
            return Response(comments_serializer.data,
                            status=status.HTTP_200_OK
                            )

        except Exception as e:
            return Response({"detail": Errors.INTERNAL_SERVER_ERROR},
                            status=status.HTTP_400_BAD_REQUEST
                            )
