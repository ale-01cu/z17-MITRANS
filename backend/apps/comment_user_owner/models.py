from django.db import models
from simple_history.models import HistoricalRecords
import uuid

# Create your models here.
class UserOwner(models.Model):
    class Meta:
        verbose_name = "Usuario propietario"
        verbose_name_plural = "Usuarios propietarios"

    external_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="ID externo"
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Nombre"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"UserOwner(text={self.name}, created_at={self.created_at})"

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def save(self, *args, **kwargs):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"usro_{unique_id}"
        super().save(*args, **kwargs)


