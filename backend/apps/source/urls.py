from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListSourcesView.as_view()),
]