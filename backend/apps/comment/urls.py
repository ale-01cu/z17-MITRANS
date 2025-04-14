from rest_framework.routers import DefaultRouter
from .views import (
    CommentAPIView, GetCommentsFromExcelView,
    CreateCommentsView, ClassificationsByCommentsView,
    UnreadCommentsListView, UrgentCommentsView
)
from django.urls import path

router = DefaultRouter()
router.register(f'', CommentAPIView, basename='comment')

urlpatterns = [
    path('upload/', GetCommentsFromExcelView.as_view(), name='get-comments-from-excel'),
    path('create-list/', CreateCommentsView.as_view(), name='create-comments-list'),
    path('classifications/', ClassificationsByCommentsView.as_view(), name='classifications-by-comments'),
    path('unread/', UnreadCommentsListView.as_view(), name='unread-comments-list'),
    path('urgent/', UrgentCommentsView.as_view(), name='urgent-comments'),
] + router.urls