from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    """Manager para CustomUser usando email como identificador."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Correo electrónico', unique=True, max_length=255)
    first_name = models.CharField('Nombre(s)', max_length=30, blank=True)
    last_name = models.CharField('Apellidos', max_length=30, blank=True)
    is_active = models.BooleanField('¿Activo?', default=True)
    is_staff  = models.BooleanField('¿Staff?', default=False)
    date_joined = models.DateTimeField('Fecha de registro', default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.email
