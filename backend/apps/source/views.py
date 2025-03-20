from django.shortcuts import render
from rest_framework import generics
from .models import Source
from .serializers import SourceSerializer

# Create your views here.
class ListSourcesView(generics.ListAPIView):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer

