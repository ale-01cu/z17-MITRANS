# celery.py
import os
from celery import Celery

# Establece la configuración de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Usa la configuración de Django para Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carga las tareas desde todas las aplicaciones registradas en Django
app.autodiscover_tasks()