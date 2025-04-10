from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>\w+)/(?P<user_type>\w+)/$', ChatConsumer.as_asgi()),

    # Ruta alternativa sin room_name (para compatibilidad)
    re_path(r'^ws/chat/(?P<user_type>\w+)/$', ChatConsumer.as_asgi()),
]