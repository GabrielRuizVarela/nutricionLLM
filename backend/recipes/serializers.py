"""
Serializers for recipe management and generation.
"""
from rest_framework import serializers
from recipes.models import Receta


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
