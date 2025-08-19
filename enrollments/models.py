from django.core.validators import MinValueValidator
from django.db import models
from employees.models import Employee
from modalities.models import SubCategory
from students.models import Student


class Enrollment(models.Model):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, verbose_name="Sub categoría")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Estudiante")
    registered_by = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Registrado por")
    reference = models.CharField(max_length=6, verbose_name="Referencia")
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")


    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
