from django.db import models
from simple_history.models import HistoricalRecords
import uuid


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
    text = models.CharField(
        max_length=200,
        verbose_name="Comentario"
    )
    user = models.ForeignKey(
        'user.UserAccount',
        on_delete=models.CASCADE,
        verbose_name="Usuario"
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
        verbose_name="Clasificación",
        default=None,
        null=True
    )
    source = models.ForeignKey(
        'source.Source',
        on_delete=models.CASCADE,
        verbose_name="Fuente",
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
