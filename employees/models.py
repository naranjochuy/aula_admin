from django.conf import settings
from django.db import models, transaction


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee',
        verbose_name='Usuario asociado'
    )
    address = models.TextField(verbose_name="Dirección")
    birthdate = models.DateField(verbose_name="Fecha de nacimiento")
    commission_general_public = models.BooleanField(verbose_name="Recibe comisión por público en general")
    phone_number = models.CharField(max_length=10, verbose_name="Número telefónico")
    phone_number_2 = models.CharField(max_length=10, null=True, verbose_name="Número telefónico 2")
    picture = models.ImageField(upload_to='employees', verbose_name="Imagen")
    reference = models.CharField(
        max_length=6,
        unique=True,
        verbose_name="Referencia"
    )

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"

    def get_detail_fields(self):
        return [
            ("Imagen", self.picture, "image"),
            ("Correo electrónico", self.user.email, "text"),
            ("Nombre(s)", self.user.first_name, "text"),
            ("Apellidos", self.user.last_name, "text"),
            ("Referencia", self.reference, "text"),
            ("Dirección", self.address, "text"),
            ("Fecha de nacimiento", self.birthdate, "date"),
            ("Número telefónico", self.phone_number, "text"),
            ("Número telefónico 2", self.phone_number_2, "text"),
            ("Recibe comisión por público en general", self.commission_general_public, "boolean"),
            ("Activo", self.user.is_active, "boolean"),
        ]

    @transaction.atomic
    def delete(self, *args, **kwargs):
        related_user = self.user
        super().delete(*args, **kwargs)
        if related_user:
            related_user.delete()
