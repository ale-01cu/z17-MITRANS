from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListUserOwnerView.as_view()),
]