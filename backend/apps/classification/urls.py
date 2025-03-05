from django.urls import path
from .views import ClassificationListApiView, ClassifyCommentView, ClassifyCommentsByIdView

urlpatterns = [
    path('', ClassificationListApiView.as_view(), name='classification-list'),
    path('classify-comment/', ClassifyCommentView.as_view(), name='classify-comment'),
    path('classify-comments-by-id/', ClassifyCommentsByIdView.as_view(), name='classify-comments-by-id'),
]