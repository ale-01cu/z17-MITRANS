from django.shortcuts import render
from apps.comment.serializers import CommentSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .pagination import ResultsSetPagination


# Create your views here.
class CommentAPIView(viewsets.ModelViewSet):
    queryset = CommentSerializer.Meta.model.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ResultsSetPagination
    lookup_field = 'external_id'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
