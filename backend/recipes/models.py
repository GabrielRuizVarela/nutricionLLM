from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import datetime, timedelta, date


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


class MealPlan(models.Model):
    """
    Weekly meal plan for a user.
    Each plan represents one week of meals (Monday to Sunday).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    week_start_date = models.DateField(
        help_text="Monday of the week (ISO 8601 week date)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-week_start_date']
        unique_together = [['user', 'week_start_date']]
        verbose_name = 'Meal Plan'
        verbose_name_plural = 'Meal Plans'

    def __str__(self):
        return f"{self.user.username}'s plan for week of {self.week_start_date}"

    @classmethod
    def get_week_start(cls, date=None):
        """
        Get the Monday of the week for a given date.
        If no date provided, uses current date.
        """
        if date is None:
            date = datetime.now().date()
        # Get Monday (weekday 0)
        days_since_monday = date.weekday()
        return date - timedelta(days=days_since_monday)


class MealSlot(models.Model):
    """
    Individual meal slot in a weekly meal plan.
    Represents one meal (breakfast/lunch/dinner) on one day.
    """
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ]

    meal_plan = models.ForeignKey(
        MealPlan,
        on_delete=models.CASCADE,
        related_name='meal_slots'
    )
    day_of_week = models.IntegerField(
        choices=DAY_CHOICES,
        help_text="0 = Monday, 6 = Sunday"
    )
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    recipe = models.ForeignKey(
        Receta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meal_slots'
    )

    # Leftover tracking
    is_leftover = models.BooleanField(
        default=False,
        help_text="True if this meal reuses leftovers from another meal"
    )
    original_meal_slot = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leftover_uses',
        help_text="The original meal this is a leftover from"
    )

    # Optional notes
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['meal_plan', 'day_of_week', 'meal_type']
        unique_together = [['meal_plan', 'day_of_week', 'meal_type']]
        verbose_name = 'Meal Slot'
        verbose_name_plural = 'Meal Slots'

    def __str__(self):
        day_name = self.get_day_of_week_display()
        meal_name = self.get_meal_type_display()
        recipe_name = self.recipe.name if self.recipe else "Empty"
        return f"{day_name} {meal_name}: {recipe_name}"

    def get_date(self):
        """Get the actual date for this meal slot"""
        return self.meal_plan.week_start_date + timedelta(days=self.day_of_week)

    @property
    def date(self):
        """Property accessor for the meal slot's date."""
        return self.get_date()

    @property
    def day_name(self):
        """Property accessor for the day name."""
        return self.get_day_of_week_display()

    @property
    def meal_name(self):
        """Property accessor for the meal type name."""
        return self.get_meal_type_display()


class Food(models.Model):
    """
    USDA Food Database entry.
    Stores food items from USDA FoodData Central branded foods database.
    """
    fdc_id = models.IntegerField(
        unique=True,
        db_index=True,
        help_text="USDA FoodData Central ID"
    )
    description = models.CharField(
        max_length=500,
        db_index=True,
        help_text="Food name/description"
    )
    brand_owner = models.CharField(max_length=200, blank=True)
    barcode = models.CharField(
        max_length=20,
        blank=True,
        db_index=True,
        help_text="UPC/GTIN barcode"
    )
    ingredients = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)

    # Serving size info
    serving_size = models.FloatField(
        null=True,
        blank=True,
        help_text="Serving size amount"
    )
    serving_size_unit = models.CharField(
        max_length=20,
        blank=True,
        help_text="Serving size unit (g, ml, etc.)"
    )

    # Macronutrients per serving
    calories = models.IntegerField(
        null=True,
        blank=True,
        help_text="Calories per serving"
    )
    protein = models.FloatField(
        null=True,
        blank=True,
        help_text="Protein in grams per serving"
    )
    carbs = models.FloatField(
        null=True,
        blank=True,
        help_text="Carbohydrates in grams per serving"
    )
    fats = models.FloatField(
        null=True,
        blank=True,
        help_text="Total fats in grams per serving"
    )
    fiber = models.FloatField(
        null=True,
        blank=True,
        help_text="Fiber in grams per serving"
    )
    sugars = models.FloatField(
        null=True,
        blank=True,
        help_text="Sugars in grams per serving"
    )
    sodium = models.FloatField(
        null=True,
        blank=True,
        help_text="Sodium in mg per serving"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['description']
        verbose_name = 'Food'
        verbose_name_plural = 'Foods'
        indexes = [
            models.Index(fields=['description']),
            models.Index(fields=['fdc_id']),
        ]

    def __str__(self):
        return f"{self.description} ({self.brand_owner})"


class FoodLog(models.Model):
    """
    Daily food log entry for tracking meals and macros.
    Users log foods they eat with quantities.
    """
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_logs')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(default=date.today, db_index=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)

    # Quantity
    quantity_grams = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Quantity in grams"
    )

    # Calculated macros based on quantity
    calories = models.IntegerField(help_text="Calculated calories for this entry")
    protein = models.FloatField(help_text="Calculated protein in grams")
    carbs = models.FloatField(help_text="Calculated carbs in grams")
    fats = models.FloatField(help_text="Calculated fats in grams")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'meal_type', '-created_at']
        verbose_name = 'Food Log'
        verbose_name_plural = 'Food Logs'
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.food.description} on {self.date}"

    def save(self, *args, **kwargs):
        """Calculate macros based on quantity before saving"""
        if self.food and self.quantity_grams:
            # Calculate macros proportionally based on serving size
            if self.food.serving_size and self.food.serving_size > 0:
                ratio = self.quantity_grams / self.food.serving_size

                self.calories = int((self.food.calories or 0) * ratio)
                self.protein = round((self.food.protein or 0) * ratio, 1)
                self.carbs = round((self.food.carbs or 0) * ratio, 1)
                self.fats = round((self.food.fats or 0) * ratio, 1)

        super().save(*args, **kwargs)
