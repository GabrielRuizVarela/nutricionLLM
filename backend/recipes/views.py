"""
Views for recipe generation, saving, and listing.
"""
import logging
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from recipes.models import Receta
from recipes.serializers import RecipeGenerationSerializer, RecetaSerializer
from recipes.llm_service import LLMService

logger = logging.getLogger(__name__)


class RecipeGenerationView(APIView):
    """
    API endpoint for generating recipes using LLM (US5).

    POST /api/recipes/generate/
    - Generates a personalized recipe using LLM Studio
    - Uses user's profile data (goal, dietary_preferences)
    - Returns recipe data without saving
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Validate input
        serializer = RecipeGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get validated data
        meal_type = serializer.validated_data['meal_type']
        available_time = serializer.validated_data['available_time']
        available_ingredients = serializer.validated_data.get('available_ingredients', '')

        # Get user profile data
        profile = request.user.profile
        goal = profile.goal
        dietary_preferences = profile.dietary_preferences

        # Generate recipe using LLM
        try:
            llm_service = LLMService()
            recipe_data = llm_service.generate_recipe(
                meal_type=meal_type,
                available_time=available_time,
                goal=goal,
                dietary_preferences=dietary_preferences,
                available_ingredients=available_ingredients
            )

            # LLM now returns English field names that match our model directly
            return Response(recipe_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Recipe generation failed: {str(e)}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecetaViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing recipes (US6, US7, US8).

    Endpoints:
    - GET /api/recetas/ - List user's recipes (US8)
    - GET /api/recetas/{id}/ - Retrieve recipe detail (US6)
    - POST /api/recetas/ - Save a new recipe (US7)
    - PUT/PATCH /api/recetas/{id}/ - Update recipe
    - DELETE /api/recetas/{id}/ - Delete recipe
    """
    serializer_class = RecetaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return only recipes belonging to the current user.
        AC: Only recipes belonging to the current user are displayed.
        Ordered from most recent to oldest.
        AC: The list is ordered from most recent to oldest.
        """
        return Receta.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Save the recipe and link it to the current user.
        AC: The backend creates a Receta object linked to the current user.
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new recipe.
        AC: Clicking "Save Recipe" sends POST to /api/recetas/
        AC: Success message shown: "Recipe saved."
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
