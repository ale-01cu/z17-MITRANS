from rest_framework.routers import DefaultRouter
from .views import CommentAPIView, get_comments_from_excel, create_comments_list
from django.urls import path

router = DefaultRouter()
router.register(f'', CommentAPIView, basename='comment')

urlpatterns = [
    path('upload/', get_comments_from_excel, name='get-comments-from-excel'),
    path('create-list/', create_comments_list, name='create-comments-list'),
] + router.urls