from django.shortcuts import render
from rest_framework import generics
from .serializers import UserOwnerSerializer
from .models import UserOwner

# Create your views here.
class ListUserOwnerView(generics.ListAPIView):
    queryset = UserOwner.objects.all()
    serializer_class = UserOwnerSerializer