"""
URL patterns for recipe endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipes.views import (
    RecipeGenerationView,
    RecetaViewSet,
    MealPlanViewSet,
    MealSlotViewSet,
    FoodSearchView,
    FoodLogViewSet
)

# Create a router for the viewsets
router = DefaultRouter()
router.register(r'recetas', RecetaViewSet, basename='receta')
router.register(r'meal-plans', MealPlanViewSet, basename='meal-plan')
router.register(r'meal-slots', MealSlotViewSet, basename='meal-slot')
router.register(r'food-logs', FoodLogViewSet, basename='food-log')

urlpatterns = [
    path('recipes/generate/', RecipeGenerationView.as_view(), name='recipe-generate'),
    path('foods/search/', FoodSearchView.as_view(), name='food-search'),
    path('', include(router.urls)),
]
