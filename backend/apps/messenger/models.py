from django.db import models
from simple_history.models import HistoricalRecords
import uuid

# Create your models here.
class Conversation(models.Model):
    # ID de messenger
    messenger_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="ID de Messenger",
    )

    # ID del usuario con el que se ha iniciado la conversación
    user = models.ForeignKey(
        'comment_user_owner.UserOwner',
        on_delete=models.CASCADE,
        verbose_name="Usuario Propietario",
        default=None,
        null=True
    )

    # Link de la conversación en messenger
    link = models.CharField(
        max_length=100,
        verbose_name="Link de la conversación"
    )

    # Fecha de creación de la conversación en messenger
    messenger_updated_at = models.DateTimeField(
        verbose_name="Fecha de modificación en messenger"
    )

    # Fecha de creación de la conversación en esta base de datos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.user.name}'


    def save(self, *args, **kwargs):
        if not self.messenger_id:
            unique_id = uuid.uuid4().hex
            self.messenger_id = f"conv_{unique_id}"
        super().save(*args, **kwargs)