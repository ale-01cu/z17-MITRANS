from django.db import models
import uuid
from simple_history.models import HistoricalRecords


class Post(models.Model):
    class Meta:
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"

    external_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="ID externo"
    )
    content = models.CharField(
        max_length=200,
        verbose_name="Texto"
    )
    user = models.ForeignKey(
        'user.UserAccount',
        on_delete=models.CASCADE,
        verbose_name="Usuario"
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
        return self.content

    def save(self, *args, **kwargs):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"post_{unique_id}"
        super().save(*args, **kwargs)
