from rest_framework.routers import DefaultRouter
from .views import PostApiView

router = DefaultRouter()
router.register(f'', PostApiView, basename='post')

urlpatterns = router.urls