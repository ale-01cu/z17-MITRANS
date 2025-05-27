from django.apps import AppConfig
# from django_celery_beat.models import PeriodicTask, IntervalSchedule

class MessengerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.messenger'


    # def ready(self):
    #     schedule, created = IntervalSchedule.objects.get_or_create(
    #         every=1,
    #         period=IntervalSchedule.SECONDS,
    #     )
    #     PeriodicTask.objects.get_or_create(
    #         interval=schedule,
    #         name='Obtener mensajes de messenger cada 1 minuto',
    #         task='apps.messenger.tasks.fetch_and_store_api_data',
    #     )