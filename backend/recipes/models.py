from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Receta(models.Model):
    """
    Recipe model that stores generated recipes linked to users.
    Contains nutritional information and preparation details.
    """
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=200)
    ingredients = models.TextField(
        help_text="Comma-separated list of ingredients"
    )
    steps = models.TextField(
        help_text="Numbered steps separated by periods"
    )
    calories = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    protein = models.FloatField(validators=[MinValueValidator(0)])
    carbs = models.FloatField(validators=[MinValueValidator(0)])
    fats = models.FloatField(validators=[MinValueValidator(0)])
    prep_time_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Preparation time in minutes"
    )
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return f"{self.name} ({self.meal_type}) - {self.user.username}"
