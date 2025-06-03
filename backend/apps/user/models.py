from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords
import uuid




class Entity(models.Model):
    class Meta:
        verbose_name = 'Entidad'
        verbose_name_plural = 'Entidades'

    external_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="ID externo"
    )

    name = models.CharField(
        max_length=120,
        unique=True,
        verbose_name='Nombre de Usuario'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
    )

    created_at = models.DateTimeField(
        verbose_name='Fecha de creado',
        auto_now_add=True
    )

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"enty_{unique_id}"
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name


class FacebookPage(models.Model):
    class Meta:
        verbose_name = 'Página de Facebook'
        verbose_name_plural = 'Páginas de Facebook'

    external_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="ID externo"
    )

    entity = models.OneToOneField(
        Entity,
        on_delete=models.CASCADE,
        verbose_name='Entidad'
    )

    facebook_access_token = models.CharField(
        max_length=255,
        null=True,
        verbose_name='Token de acceso a Facebook'
    )

    facebook_page_id = models.CharField(
        max_length=255,
        null=True,
        verbose_name='ID de la página de Facebook'
    )

    facebook_page_name = models.CharField(
        max_length=255,
        null=True,
        verbose_name='Nombre de la página de Facebook'
    )

    created_at = models.DateTimeField(
        verbose_name='Fecha de creado',
        auto_now_add=True
    )

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"fb_page_{unique_id}"
        super().save(*args, **kwargs)



class UserAccountManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Nombre de usuario requerido.')

        user = self.model(username=username, **extra_fields)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password=None, **extra_fields):
        user = self.create_user(username, password, **extra_fields)

        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


ROLE_CHOICES = [
    ('superuser', 'Super Usuario'),
    ('manager', 'Gestor'),
    ('consultant', 'Consultor'),
]

class UserAccount(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Cuenta de Usuario'
        verbose_name_plural = 'Cuentas de Usuarios'

    external_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="ID externo"
    )

    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name='Correo'
    )

    username = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Nombre de Usuario'
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name='Nombre'
    )

    last_name = models.CharField(
        max_length=255,
        verbose_name='Apellidos'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
    )

    is_staff = models.BooleanField(
        default=False,
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='consultant',
        verbose_name="Rol"
    )

    created_at = models.DateTimeField(
        verbose_name='Fecha de creado',
        auto_now_add=True
    )


    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        verbose_name='Entidad',
        null=True,
        blank=True,
    )

    history = HistoricalRecords()
    objects = UserAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name',
        'password'
    ]

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def save(self, *args, **kwargs):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"user_{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
