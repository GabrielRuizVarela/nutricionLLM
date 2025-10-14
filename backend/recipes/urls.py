"""
URL patterns for recipe endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipes.views import RecipeGenerationView, RecetaViewSet

# Create a router for the viewset
router = DefaultRouter()
router.register(r'recetas', RecetaViewSet, basename='receta')

urlpatterns = [
    path('recipes/generate/', RecipeGenerationView.as_view(), name='recipe-generate'),
    path('', include(router.urls)),
]
