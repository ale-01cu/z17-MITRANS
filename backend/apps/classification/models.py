from django.db import models
from simple_history.models import HistoricalRecords
import uuid

# Create your models here.
class Classification(models.Model):
    class Meta:
        verbose_name = "Clasificación"
        verbose_name_plural = "Clasificaciones"

    external_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="ID externo"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"clas_{unique_id}"
        super().save(*args, **kwargs)