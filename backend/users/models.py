from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    """
    User profile model that extends the Django User model.
    Stores nutritional goals and dietary preferences for recipe generation.
    """
    # Core relationship
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # === PERSONAL INFORMATION ===
    age = models.IntegerField(
        null=True,
        blank=True,
        help_text="Age in years"
    )
    weight_kg = models.FloatField(
        null=True,
        blank=True,
        help_text="Weight in kilograms"
    )
    height_cm = models.IntegerField(
        null=True,
        blank=True,
        help_text="Height in centimeters"
    )

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        default='',
        help_text="Gender"
    )

    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('lightly_active', 'Lightly Active (exercise 1-3 days/week)'),
        ('moderately_active', 'Moderately Active (exercise 3-5 days/week)'),
        ('very_active', 'Very Active (exercise 6-7 days/week)'),
        ('extremely_active', 'Extremely Active (physical job or training twice/day)'),
    ]
    activity_level = models.CharField(
        max_length=20,
        choices=ACTIVITY_LEVEL_CHOICES,
        blank=True,
        default='',
        help_text="Activity level"
    )

    # === DIETARY INFORMATION ===
    GOAL_CHOICES = [
        ('lose_weight', 'Lose Weight'),
        ('gain_weight', 'Gain Weight'),
        ('maintain_weight', 'Maintain Weight'),
        ('gain_muscle', 'Gain Muscle'),
        ('improve_health', 'Improve Health'),
    ]
    goal = models.CharField(
        max_length=20,
        choices=GOAL_CHOICES,
        blank=True,
        default='',
        help_text="Primary nutritional goal"
    )

    dietary_preferences = models.TextField(
        blank=True,
        help_text="Dietary preferences (e.g., 'vegetarian, gluten-free')"
    )

    allergies = models.TextField(
        blank=True,
        help_text="Food allergies (e.g., 'peanuts, shellfish, dairy')"
    )

    dislikes = models.TextField(
        blank=True,
        help_text="Disliked ingredients (e.g., 'mushrooms, cilantro')"
    )

    # === RECIPE PREFERENCES ===
    cuisine_preferences = models.TextField(
        blank=True,
        help_text="Preferred cuisines (e.g., 'Italian, Mexican, Asian')"
    )

    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    cooking_skill_level = models.CharField(
        max_length=20,
        choices=SKILL_LEVEL_CHOICES,
        default='beginner',
        help_text="Cooking skill level"
    )

    SPICE_PREFERENCE_CHOICES = [
        ('mild', 'Mild'),
        ('medium', 'Medium'),
        ('spicy', 'Spicy'),
    ]
    spice_preference = models.CharField(
        max_length=10,
        choices=SPICE_PREFERENCE_CHOICES,
        default='mild',
        help_text="Spice preference"
    )

    # === INGREDIENT MANAGEMENT ===
    preferred_ingredients = models.TextField(
        blank=True,
        help_text="Ingredients you like to use regularly (e.g., 'chicken, rice, broccoli, olive oil')"
    )
    available_ingredients = models.TextField(
        blank=True,
        help_text="Ingredients you currently have in your pantry (e.g., 'eggs, tomatoes, pasta, cheese')"
    )

    # === NUTRITIONAL TARGETS ===
    daily_calorie_target = models.IntegerField(
        null=True,
        blank=True,
        help_text="Daily calorie target (kcal)"
    )
    daily_protein_target = models.IntegerField(
        null=True,
        blank=True,
        help_text="Daily protein target (grams)"
    )
    daily_carbs_target = models.IntegerField(
        null=True,
        blank=True,
        help_text="Daily carbohydrates target (grams)"
    )
    daily_fats_target = models.IntegerField(
        null=True,
        blank=True,
        help_text="Daily fats target (grams)"
    )

    # === MEAL DISTRIBUTION (Spring 2) ===
    meals_per_day = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text="Number of meals per day (1-6)"
    )
    meal_distribution = models.JSONField(
        default=dict,
        blank=True,
        help_text="Calorie percentage distribution per meal (e.g., {'1': 30, '2': 40, '3': 30})"
    )
    meal_names = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom meal names (e.g., {'1': 'Breakfast', '2': 'Lunch', '3': 'Dinner'})"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

    def get_meal_calories(self, meal_number):
        """
        Calculate calorie target for a specific meal based on distribution.

        Args:
            meal_number: Meal number (1-indexed)

        Returns:
            int: Calorie target for the meal, or None if not configured
        """
        if not self.daily_calorie_target or not self.meal_distribution:
            return None

        meal_key = str(meal_number)
        percentage = self.meal_distribution.get(meal_key)

        if percentage is None:
            return None

        return int(self.daily_calorie_target * percentage / 100)

    def get_default_meal_names(self):
        """
        Get default meal names based on meals_per_day.

        Returns:
            dict: Dictionary mapping meal numbers to default names
        """
        default_names = {
            1: {1: 'Meal 1'},
            2: {1: 'Meal 1', 2: 'Meal 2'},
            3: {1: 'Breakfast', 2: 'Lunch', 3: 'Dinner'},
            4: {1: 'Breakfast', 2: 'Lunch', 3: 'Dinner', 4: 'Snack'},
            5: {1: 'Breakfast', 2: 'Morning Snack', 3: 'Lunch', 4: 'Afternoon Snack', 5: 'Dinner'},
            6: {1: 'Breakfast', 2: 'Morning Snack', 3: 'Lunch', 4: 'Afternoon Snack', 5: 'Dinner', 6: 'Evening Snack'}
        }
        return default_names.get(self.meals_per_day, {})

    def calculate_bmr(self):
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation.
        Returns None if required fields are missing.
        """
        if not all([self.weight_kg, self.height_cm, self.age, self.gender]):
            return None

        # Mifflin-St Jeor Equation
        if self.gender == 'male':
            bmr = (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age) + 5
        elif self.gender == 'female':
            bmr = (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age) - 161
        else:
            # Use average for other genders
            bmr = (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age) - 78

        return int(bmr)

    def calculate_tdee(self):
        """
        Calculate Total Daily Energy Expenditure.
        Returns None if BMR cannot be calculated.
        """
        bmr = self.calculate_bmr()
        if not bmr or not self.activity_level:
            return None

        # Activity multipliers
        multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extremely_active': 1.9,
        }

        multiplier = multipliers.get(self.activity_level, 1.2)
        return int(bmr * multiplier)

    @property
    def bmr(self):
        """
        Property accessor for BMR.
        Returns calculated BMR or None if required fields are missing.
        """
        return self.calculate_bmr()

    @property
    def tdee(self):
        """
        Property accessor for TDEE.
        Returns calculated TDEE or None if BMR/activity level are missing.
        """
        return self.calculate_tdee()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a User is created."""
    if created:
        Profile.objects.create(user=instance)
