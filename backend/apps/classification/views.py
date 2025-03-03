from django.shortcuts import render
from rest_framework import generics
from .serializers import ClassificationSerializer


# Create your views here.
class ClassificationListApiView(generics.ListAPIView):
    queryset = ClassificationSerializer.Meta.model.objects.all()
    serializer_class = ClassificationSerializer
