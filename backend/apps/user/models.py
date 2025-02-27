from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords


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


class UserAccount(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Cuenta de Usuario'
        verbose_name_plural = 'Cuentas de Usuarios'

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

    create_at = models.DateTimeField(
        verbose_name='Fecha de creado',
        auto_now_add=True
    )

    history = HistoricalRecords()
    objects = UserAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name',
    ]

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return self.email
