from django.conf import settings
from django.db import models


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student',
        verbose_name='Usuario asociado'
    )
    address = models.TextField(verbose_name="Dirección")
    birthdate = models.DateField(verbose_name="Fecha de nacimiento")
    phone_number = models.CharField(max_length=10, verbose_name="Número telefónico")
    phone_number_2 = models.CharField(max_length=10, null=True, verbose_name="Número telefónico 2")
    picture = models.ImageField(upload_to='students', verbose_name="Imagen")

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"

    def __str__(self) -> str:
        full_name = f"{self.first_name} {self.last_name}"
        return full_name
