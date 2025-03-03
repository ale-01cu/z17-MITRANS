from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import PostSerializer, PostCreateSerializer
from .pagination import ResultsSetPagination


# Create your views here.
class PostApiView(viewsets.ModelViewSet):
    queryset = PostSerializer.Meta.model.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ResultsSetPagination
    lookup_field = 'external_id'

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
