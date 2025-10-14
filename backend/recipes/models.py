from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Receta(models.Model):
    """
    Recipe model that stores generated recipes linked to users.
    Contains nutritional information and preparation details.
    """
    MEAL_TYPE_CHOICES = [
        ('desayuno', 'Desayuno'),
        ('almuerzo', 'Almuerzo'),
        ('cena', 'Cena'),
        ('snack', 'Snack'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    nombre = models.CharField(max_length=200)
    ingredientes_texto = models.TextField(
        help_text="Comma-separated list of ingredients"
    )
    pasos_texto = models.TextField(
        help_text="Numbered steps separated by periods"
    )
    calorias = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    proteinas = models.FloatField(validators=[MinValueValidator(0)])
    carbohidratos = models.FloatField(validators=[MinValueValidator(0)])
    grasas = models.FloatField(validators=[MinValueValidator(0)])
    tiempo_min = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Preparation time in minutes"
    )
    tipo = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Receta'
        verbose_name_plural = 'Recetas'

    def __str__(self):
        return f"{self.nombre} ({self.tipo}) - {self.user.username}"
