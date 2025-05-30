from django.db import models

# Create your models here.
class Conversation(models.Model):
    # ID de messenger
    id_messenger = models.AutoField(primary_key=True)

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
    updated_time = models.DateTimeField(auto_now_add=True)

    # Fecha de creación de la conversación en esta base de datos
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}'


class Message(models.Model):
    # ID de messenger
    id_messenger = models.AutoField(primary_key=True)
    message_id = models.CharField(max_length=255, unique=True)

    # Relacion de 1 a muchos con la conversación
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    # Relacion de 1 a muchos con el usuario que envió el mensaje
    sender = models.ForeignKey(
        'comment_user_owner.UserOwner',
        on_delete=models.CASCADE,
        verbose_name="Usuario Propietario",
        default=None,
        null=True
    )

    # Texto del mensaje
    content = models.TextField()

    # Fecha de creacion del mensaje en messenger
    created_time = models.DateTimeField(auto_now_add=True)

    # Fecha de creacion del mensaje en esta base de datos
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username}: {self.content}'


class LastProcessedMessage(models.Model):
    last_message_id = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)