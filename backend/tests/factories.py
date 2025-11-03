"""
Test data factories for creating model instances.
Uses factory_boy to generate realistic test data.
"""

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from recipes.models import Receta, MealPlan, MealSlot, Food, FoodLog

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class ProfileFactory(DjangoModelFactory):
    """Factory for creating test user profiles."""
    class Meta:
        model = 'users.Profile'

    user = factory.SubFactory(UserFactory)

    # Personal Information
    age = 30
    weight_kg = 70.0
    height_cm = 175.0
    gender = 'male'
    activity_level = 'moderately_active'

    # Dietary Information
    goal = 'maintain_weight'
    dietary_preferences = 'No restrictions'
    allergies = ''
    dislikes = ''

    # Recipe Preferences
    cuisine_preferences = 'Mediterranean, Italian'
    cooking_skill_level = 'intermediate'
    spice_preference = 'medium'

    # Ingredient Management
    preferred_ingredients = 'chicken, rice, vegetables'
    available_ingredients = 'onions, garlic, olive oil'

    # Nutritional Targets
    daily_calorie_target = 2000
    daily_protein_target = 150
    daily_carbs_target = 200
    daily_fats_target = 65


class RecetaFactory(DjangoModelFactory):
    """Factory for creating test recipes."""
    class Meta:
        model = Receta

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f'Test Recipe {n}')
    ingredients = 'Ingredient 1\nIngredient 2\nIngredient 3'
    steps = 'Step 1: Do this\nStep 2: Do that\nStep 3: Finish'
    calories = 450
    protein = 30.0
    carbs = 45.0
    fats = 15.0
    prep_time_minutes = 30
    meal_type = 'lunch'


class MealPlanFactory(DjangoModelFactory):
    """Factory for creating test meal plans."""
    class Meta:
        model = MealPlan

    user = factory.SubFactory(UserFactory)
    week_start_date = factory.Sequence(
        lambda n: (date.today() - timedelta(days=date.today().weekday())) + timedelta(weeks=n)
    )

    @factory.post_generation
    def create_slots(obj, create, extracted, **kwargs):
        """Auto-create meal slots after meal plan creation.

        To disable slot creation, pass create_slots=False:
            MealPlanFactory(create_slots=False)
        """
        if not create:
            return

        # Allow tests to disable auto-creation of slots
        if extracted is False:
            return

        meal_types = ['breakfast', 'lunch', 'dinner']
        for day in range(7):  # Monday (0) to Sunday (6)
            for meal_type in meal_types:
                MealSlotFactory(
                    meal_plan=obj,
                    day_of_week=day,
                    meal_type=meal_type
                )


class MealSlotFactory(DjangoModelFactory):
    """Factory for creating test meal slots."""
    class Meta:
        model = MealSlot

    meal_plan = factory.SubFactory(MealPlanFactory)
    day_of_week = 0  # Monday
    meal_type = 'breakfast'
    recipe = None
    is_leftover = False
    original_meal_slot = None
    notes = ''


class FoodFactory(DjangoModelFactory):
    """Factory for creating test USDA foods."""
    class Meta:
        model = Food

    fdc_id = factory.Sequence(lambda n: 100000 + n)
    description = factory.Sequence(lambda n: f'Test Food Item {n}')
    brand_owner = 'Test Brand'
    barcode = factory.Sequence(lambda n: f'12345678{n:04d}')
    ingredients = 'Test ingredients'
    category = 'Test Category'
    serving_size = 100.0
    serving_size_unit = 'g'
    calories = 200
    protein = 10.0
    carbs = 25.0
    fats = 8.0
    fiber = 3.0
    sugars = 5.0
    sodium = 150.0


class FoodLogFactory(DjangoModelFactory):
    """Factory for creating test food log entries."""
    class Meta:
        model = FoodLog

    user = factory.SubFactory(UserFactory)
    food = factory.SubFactory(FoodFactory)
    date = factory.LazyFunction(date.today)
    meal_type = 'breakfast'
    quantity_grams = 100.0
    # Macros auto-calculated by model's save() method
    calories = 0
    protein = 0.0
    carbs = 0.0
    fats = 0.0


# Specialized factories for common scenarios

class BreakfastRecipeFactory(RecetaFactory):
    """Factory for breakfast recipes."""
    meal_type = 'breakfast'
    name = factory.Sequence(lambda n: f'Breakfast Recipe {n}')
    calories = 400
    protein = 20.0
    carbs = 50.0
    fats = 12.0
    prep_time_minutes = 15


class LunchRecipeFactory(RecetaFactory):
    """Factory for lunch recipes."""
    meal_type = 'lunch'
    name = factory.Sequence(lambda n: f'Lunch Recipe {n}')
    calories = 550
    protein = 35.0
    carbs = 60.0
    fats = 18.0
    prep_time_minutes = 30


class DinnerRecipeFactory(RecetaFactory):
    """Factory for dinner recipes."""
    meal_type = 'dinner'
    name = factory.Sequence(lambda n: f'Dinner Recipe {n}')
    calories = 650
    protein = 40.0
    carbs = 55.0
    fats = 22.0
    prep_time_minutes = 45


class SnackRecipeFactory(RecetaFactory):
    """Factory for snack recipes."""
    meal_type = 'snack'
    name = factory.Sequence(lambda n: f'Snack Recipe {n}')
    calories = 200
    protein = 8.0
    carbs = 25.0
    fats = 8.0
    prep_time_minutes = 10


class HighProteinFoodFactory(FoodFactory):
    """Factory for high-protein foods."""
    description = factory.Sequence(lambda n: f'High Protein Food {n}')
    brand_owner = 'Protein Brand'
    calories = 150
    protein = 25.0
    carbs = 5.0
    fats = 3.0


class LowCalorieFoodFactory(FoodFactory):
    """Factory for low-calorie foods."""
    description = factory.Sequence(lambda n: f'Low Calorie Food {n}')
    brand_owner = 'Healthy Brand'
    calories = 50
    protein = 2.0
    carbs = 10.0
    fats = 0.5
