from django.db import models
import uuid

# Create your models here.
class Source(models.Model):
    class Meta:
        verbose_name = "Fuente"
        verbose_name_plural = "Fuentes"

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
    description = models.CharField(
        max_length=200,
        verbose_name="Descripción"
    )
    url = models.URLField(
        max_length=200,
        verbose_name="URL"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    def __str__(self):
        return f"Source(name={self.name}, url={self.url}, created_at={self.created_at})"

    def save(self, *args, **kwargs):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"src_{unique_id}"
        super().save(*args, **kwargs)