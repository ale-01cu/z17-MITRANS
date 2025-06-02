from django.db import models

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
    link = models.CharField(max_length=100)

    # Fecha de creación de la conversación en messenger
    messenger_updated_at = models.DateTimeField(
        verbose_name="Fecha de modificación en messenger"
    )

    # Fecha de creación de la conversación en esta base de datos
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.name}'