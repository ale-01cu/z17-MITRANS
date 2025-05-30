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

app.conf.beat_schedule = {
    'tarea-periodica-cada-5-minutos': {
        'task': 'core.startup_tasks.tarea_periodica',
        'schedule': 300.0,  # 300 segundos = 5 minutos
    },
    'fetch-api-data-every-second': {
        'task': 'apps.messenger.tasks.fetch_and_store_api_data',
        'schedule': 5,
    },
    # Puedes añadir más tareas programadas aquí
    # 'add-every-30-seconds': {
    #     'task': 'myapp.tasks.add',
    #     'schedule': 30.0,
    #     'args': (16, 16)
    # },
    # También puedes usar crontab para programaciones más complejas
    # 'add-every-monday-morning': {
    #     'task': 'myapp.tasks.add',
    #     'schedule': crontab(hour=7, minute=30, day_of_week=1),
    #     'args': (16, 16),
    # },
}
app.conf.timezone = 'UTC' # O tu zona horaria