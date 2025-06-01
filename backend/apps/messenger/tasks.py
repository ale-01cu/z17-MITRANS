# my_app/tasks.py
from celery import shared_task
from .graphqlAPI import (
    get_conversations,
    get_messages,
    get_message_details
)
from apps.comment_user_owner.models import UserOwner
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

FACEBOOK_PAGE_NAME = settings.FACEBOOK_PAGE_NAME

@shared_task
def messenger_api_task():
    logger.info("Executing messenger_api_task")
