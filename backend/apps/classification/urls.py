from django.urls import path
from .views import ClassificationListApiView

urlpatterns = [
    path('', ClassificationListApiView.as_view(), name='classification-list'),
]