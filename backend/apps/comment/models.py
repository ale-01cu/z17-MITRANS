from django.db import models
from simple_history.models import HistoricalRecords
import uuid
from apps.messenger.models import Conversation
from apps.user.models import Entity


# Create your models here.
class Comment(models.Model):
    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"

    external_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="ID externo"
    )

    messenger_id = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
        verbose_name="ID de Messenger",
        null=True
    )

    text = models.TextField(
        verbose_name="Comentario"
    )
    user = models.ForeignKey(
        'user.UserAccount',
        on_delete=models.CASCADE,
        verbose_name="Usuario",
        default=None,
        null=True
    )

    user_owner = models.ForeignKey(
        'comment_user_owner.UserOwner',
        on_delete=models.CASCADE,
        verbose_name="Usuario Propietario",
        default=None,
        null=True
    )

    post = models.ForeignKey(
        'post.Post',
        on_delete=models.CASCADE,
        verbose_name="Post",
        default=None,
        null=True
    )
    classification = models.ForeignKey(
        'classification.Classification',
        on_delete=models.CASCADE,
        related_name="comments",
        default=None,
        null=True
    )
    source = models.ForeignKey(
        'source.Source',
        on_delete=models.CASCADE,
        verbose_name="Fuente",
    )

    messenger_conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE
    )

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        verbose_name='Entidad'
    )

    messenger_created_at = models.DateTimeField(
        verbose_name="Fecha de creación en messenger"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"Comment(text={self.text}, user={self.user}, created_at={self.created_at})"


    @property
    def _history_user(self):
        return self.changed_by


    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


    def save(self, *args, **kwargs):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"comm_{unique_id}"
        super().save(*args, **kwargs)
