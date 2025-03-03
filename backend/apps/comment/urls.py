from rest_framework.routers import DefaultRouter
from .views import CommentAPIView

router = DefaultRouter()
router.register(f'', CommentAPIView, basename='comment')

urlpatterns = router.urls