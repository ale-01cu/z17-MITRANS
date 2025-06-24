from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListUserOwnerView.as_view(), name='list-user-owner'),
    path('<str:pk>/', views.UpdateUserOwnerView.as_view(), name='update-user-owner'),
]