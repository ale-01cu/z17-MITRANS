from django.db import models
from django.core.validators import RegexValidator
from simple_history.models import HistoricalRecords
from apps.user.models import Entity
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

    facebook_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="ID de usuario en Facebook",
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Nombre"
    )

    phone_number = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[5-7]\d{7}$',
                message='El numero debe de tener 8 digitos y comenzar por 5, 6 o 7 (Ej: 51234567)'
            )
        ],
        help_text="Ej: 51234567 (8 dígitos, sin '+53', espacios o guiones).",
        null=True,
        blank=True
    )

    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name='Correo',
        null=True,
        blank=True
    )

    province = models.CharField(
        max_length=50,
        verbose_name="Provincia",
        null=True,
        blank=True
    )

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        verbose_name='Entidad'
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


