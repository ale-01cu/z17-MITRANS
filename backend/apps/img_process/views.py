from django.shortcuts import render
from rest_framework import generics
from .serializers import FileUploadSerializer

# Create your views here.
class ImgToTextView(generics.GenericAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request):
        pass
