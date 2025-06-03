"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.jwt')),

    # Generación del esquema OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Documentación con Swagger
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Documentación con Redoc
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/comment/', include('apps.comment.urls')),
    path('api/classification/', include('apps.classification.urls')),
    path('api/post/', include('apps.post.urls')),
    path('api/source/', include('apps.source.urls')),
    path('api/img-proc/', include('apps.img_process.urls')),
    path('api/user-owner/', include('apps.comment_user_owner.urls')),
    path('api/stats/', include('apps.stats.urls')),
    path('api/users/', include('apps.user.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
