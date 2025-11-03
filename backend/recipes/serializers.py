"""
Serializers for recipe management and generation.
"""
from rest_framework import serializers
from recipes.models import Receta, MealPlan, MealSlot, Food, FoodLog


class RecipeGenerationSerializer(serializers.Serializer):
    """Serializer for recipe generation request"""
    MEAL_TYPE_CHOICES = ['breakfast', 'lunch', 'dinner', 'snack']

    meal_type = serializers.ChoiceField(
        choices=MEAL_TYPE_CHOICES,
        required=True
    )
    available_time = serializers.IntegerField(
        required=True,
        min_value=1
    )
    available_ingredients = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )


class RecetaSerializer(serializers.ModelSerializer):
    """Serializer for Receta model"""

    class Meta:
        model = Receta
        fields = [
            'id', 'name', 'ingredients', 'steps',
            'calories', 'protein', 'carbs', 'fats',
            'prep_time_minutes', 'meal_type', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """Create a new recipe and link it to the current user"""
        # User is passed from the view's perform_create method
        return Receta.objects.create(**validated_data)


class MealSlotSerializer(serializers.ModelSerializer):
    """Serializer for MealSlot model with recipe details"""
    recipe_detail = RecetaSerializer(source='recipe', read_only=True)
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    meal_name = serializers.CharField(source='get_meal_type_display', read_only=True)
    date = serializers.SerializerMethodField()

    class Meta:
        model = MealSlot
        fields = [
            'id', 'meal_plan', 'day_of_week', 'day_name',
            'meal_type', 'meal_name', 'recipe', 'recipe_detail',
            'is_leftover', 'original_meal_slot', 'notes',
            'date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_date(self, obj):
        """Get the actual date for this meal slot"""
        return obj.get_date()


class MealPlanSerializer(serializers.ModelSerializer):
    """Serializer for MealPlan model with all meal slots"""
    meal_slots = MealSlotSerializer(many=True, read_only=True)
    week_end_date = serializers.SerializerMethodField()

    class Meta:
        model = MealPlan
        fields = [
            'id', 'user', 'week_start_date', 'week_end_date',
            'meal_slots', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_week_end_date(self, obj):
        """Get the Sunday of the week"""
        from datetime import timedelta
        return obj.week_start_date + timedelta(days=6)


class FoodSerializer(serializers.ModelSerializer):
    """Serializer for Food model"""

    class Meta:
        model = Food
        fields = [
            'id', 'fdc_id', 'description', 'brand_owner', 'barcode',
            'ingredients', 'category', 'serving_size', 'serving_size_unit',
            'calories', 'protein', 'carbs', 'fats', 'fiber', 'sugars', 'sodium'
        ]
        read_only_fields = ['id', 'fdc_id']


class FoodLogSerializer(serializers.ModelSerializer):
    """Serializer for FoodLog model"""
    food_detail = FoodSerializer(source='food', read_only=True)
    meal_type_display = serializers.CharField(source='get_meal_type_display', read_only=True)

    class Meta:
        model = FoodLog
        fields = [
            'id', 'user', 'food', 'food_detail', 'date', 'meal_type', 'meal_type_display',
            'quantity_grams', 'calories', 'protein', 'carbs', 'fats',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'calories', 'protein', 'carbs', 'fats', 'created_at', 'updated_at']


class FoodLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating food log entries"""

    class Meta:
        model = FoodLog
        fields = ['food', 'date', 'meal_type', 'quantity_grams']

    def create(self, validated_data):
        # User is set from the view
        return FoodLog.objects.create(**validated_data)
