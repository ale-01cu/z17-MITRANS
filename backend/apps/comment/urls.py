from rest_framework.routers import DefaultRouter
from .views import CommentAPIView, GetCommentsFromExcelView, CreateCommentsListView
from django.urls import path

router = DefaultRouter()
router.register(f'', CommentAPIView, basename='comment')

urlpatterns = [
    path('upload/', GetCommentsFromExcelView.as_view(), name='get-comments-from-excel'),
    path('create-list/', CreateCommentsListView.as_view(), name='create-comments-list'),
] + router.urls