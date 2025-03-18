from django.urls import path
from .views import ImgToTextView

urlpatterns = [
    path('img-to-text', ImgToTextView.as_view(), name='Extract image text'),
]