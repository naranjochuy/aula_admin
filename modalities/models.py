from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=60,
        unique=True,
        error_messages={
            "unique": "Ya existe una categoría con este nombre."
        }
    )
    is_active = models.BooleanField(verbose_name="Activo")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def get_detail_fields(self):
        return [
            ("Nombre", self.name, "text"),
            ("Activo", self.is_active, "boolean"),
        ]

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name="Nombre")
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio"
    )
    registration_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de inscripción"
    )
    tuition_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de colegiatura"
    )
    certification_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de certificación"
    )
    exam_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de Examen"
    )
    opening_commission_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Comisión por apertura"
    )
    closing_commission_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Comisión por cierre"
    )
    new_opening_commission_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Comisión por alcanzar la meta"
    )
    threshold_sales_amount = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Ventas para alcanzar nueva comisión"
    )
    commission_amount_general_public = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Comisión por publico en general"
    )
    is_active = models.BooleanField(verbose_name="Activo")
    is_general_public = models.BooleanField(
        verbose_name="Es público en general"
    )

    class Meta:
        verbose_name = "Sub categoría"
        verbose_name_plural = "Sub categorías"

    def get_detail_fields(self):
        return [
            ("Categoría", self.category, "text"),
            ("Nombre", self.name, "text"),
            ("Precio", self.price, "decimal"),
            ("Precio de inscripción", self.registration_price, "decimal"),
            ("Precio de colegiatura", self.tuition_price, "decimal"),
            ("Precio de certificación", self.certification_price, "decimal"),
            ("Precio de Examen", self.exam_price, "decimal"),
            ("Comisión por apertura", self.opening_commission_amount, "decimal"),
            ("Comisión por cierre", self.closing_commission_amount, "decimal"),
            ("Comisión por alcanzar la meta", self.new_opening_commission_amount, "decimal"),
            ("Ventas para alcanzar nueva comisión", self.threshold_sales_amount, "decimal"),
            ("Comisión por público en general", self.commission_amount_general_public, "decimal"),
            ("Es público en general", self.is_general_public, "boolean"),
            ("Activo", self.is_active, "boolean"),
        ]

    def __str__(self):
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"
