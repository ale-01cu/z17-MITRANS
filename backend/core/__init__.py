from .celery import app as celery_app
from .startup_tasks import StartupConfig

__all__ = ("celery_app",)

default_app_config = 'core.startup_tasks.StartupConfig'