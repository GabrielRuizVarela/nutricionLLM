"""
Views for recipe generation, saving, and listing.
"""
import logging
from datetime import datetime, timedelta, date
from django.db.models import Q, Sum
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from recipes.models import Receta, MealPlan, MealSlot, Food, FoodLog
from recipes.serializers import (
    RecipeGenerationSerializer,
    RecetaSerializer,
    MealPlanSerializer,
    MealSlotSerializer,
    FoodSerializer,
    FoodLogSerializer,
    FoodLogCreateSerializer
)
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

        # Generate recipe using LLM with comprehensive profile data
        try:
            llm_service = LLMService()
            recipe_data = llm_service.generate_recipe(
                meal_type=meal_type,
                available_time=available_time,
                goal=profile.goal,
                dietary_preferences=profile.dietary_preferences,
                available_ingredients=available_ingredients,
                # New profile fields for enhanced personalization
                allergies=profile.allergies,
                dislikes=profile.dislikes,
                cuisine_preferences=profile.cuisine_preferences,
                cooking_skill_level=profile.cooking_skill_level,
                spice_preference=profile.spice_preference,
                daily_calorie_target=profile.daily_calorie_target,
                daily_protein_target=profile.daily_protein_target,
                daily_carbs_target=profile.daily_carbs_target,
                daily_fats_target=profile.daily_fats_target,
                # Ingredient management
                preferred_ingredients=profile.preferred_ingredients
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


class MealPlanViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing weekly meal plans.

    Endpoints:
    - GET /api/meal-plans/ - List user's meal plans
    - GET /api/meal-plans/current/ - Get current week's plan (creates if doesn't exist)
    - GET /api/meal-plans/{id}/ - Retrieve specific meal plan
    - POST /api/meal-plans/ - Create a new meal plan for a specific week
    - DELETE /api/meal-plans/{id}/ - Delete a meal plan
    """
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only meal plans belonging to the current user"""
        return MealPlan.objects.filter(user=self.request.user).prefetch_related('meal_slots__recipe')

    def perform_create(self, serializer):
        """Save the meal plan and link it to the current user"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get or create the meal plan for the current week.
        Returns the plan with all meal slots (creates empty slots if new plan).
        """
        week_start = MealPlan.get_week_start()

        # Get or create the meal plan for this week
        meal_plan, created = MealPlan.objects.get_or_create(
            user=request.user,
            week_start_date=week_start
        )

        # If newly created, initialize empty meal slots (7 days × 3 meals = 21 slots)
        if created:
            self._create_empty_slots(meal_plan)

        serializer = self.get_serializer(meal_plan)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """
        Get or create the meal plan for a specific date.
        Query param: ?date=YYYY-MM-DD
        """
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'error': 'date parameter is required (format: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        week_start = MealPlan.get_week_start(target_date)

        # Get or create the meal plan for this week
        meal_plan, created = MealPlan.objects.get_or_create(
            user=request.user,
            week_start_date=week_start
        )

        # If newly created, initialize empty meal slots
        if created:
            self._create_empty_slots(meal_plan)

        serializer = self.get_serializer(meal_plan)
        return Response(serializer.data)

    def _create_empty_slots(self, meal_plan):
        """Create 21 empty meal slots (7 days × 3 meals) for a new meal plan"""
        meal_types = ['breakfast', 'lunch', 'dinner']
        slots = []

        for day in range(7):  # Monday (0) to Sunday (6)
            for meal_type in meal_types:
                slots.append(MealSlot(
                    meal_plan=meal_plan,
                    day_of_week=day,
                    meal_type=meal_type
                ))

        MealSlot.objects.bulk_create(slots)


class MealSlotViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing individual meal slots.

    Endpoints:
    - GET /api/meal-slots/ - List user's meal slots
    - GET /api/meal-slots/{id}/ - Retrieve specific meal slot
    - PUT/PATCH /api/meal-slots/{id}/ - Update meal slot (assign recipe, mark as leftover, etc.)
    - DELETE /api/meal-slots/{id}/ - Clear a meal slot (remove recipe assignment)
    """
    serializer_class = MealSlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only meal slots belonging to the current user's meal plans"""
        return MealSlot.objects.filter(
            meal_plan__user=self.request.user
        ).select_related('recipe', 'meal_plan', 'original_meal_slot')

    def update(self, request, *args, **kwargs):
        """
        Update a meal slot.
        Allows assigning/removing recipes, marking as leftover, adding notes.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Verify the meal slot belongs to the user
        if instance.meal_plan.user != request.user:
            return Response(
                {'error': 'You do not have permission to modify this meal slot'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class FoodSearchView(APIView):
    """
    API endpoint for searching foods from USDA database.

    GET /api/foods/search/?q=chicken
    - Returns top 20 matching foods
    - Searches in description and brand_owner
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()

        if not query or len(query) < 2:
            return Response(
                {'error': 'Query must be at least 2 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Search in description and brand_owner (case-insensitive)
        foods = Food.objects.filter(
            Q(description__icontains=query) | Q(brand_owner__icontains=query)
        ).order_by('description')[:20]

        serializer = FoodSerializer(foods, many=True)
        return Response(serializer.data)


class FoodLogViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing daily food logs.

    Endpoints:
    - GET /api/food-logs/ - List user's food logs
    - GET /api/food-logs/?date=YYYY-MM-DD - Filter by date
    - GET /api/food-logs/daily_totals/?date=YYYY-MM-DD - Get macro totals for a day
    - POST /api/food-logs/ - Log a new food entry
    - DELETE /api/food-logs/{id}/ - Remove food entry
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only food logs belonging to the current user"""
        queryset = FoodLog.objects.filter(user=self.request.user).select_related('food')

        # Filter by date if provided
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)

        return queryset

    def get_serializer_class(self):
        """Use different serializer for create vs list/retrieve"""
        if self.action == 'create':
            return FoodLogCreateSerializer
        return FoodLogSerializer

    def perform_create(self, serializer):
        """Save the food log and link it to the current user"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def daily_totals(self, request):
        """
        Get daily macro totals for a specific date.
        Query param: ?date=YYYY-MM-DD (defaults to today)
        """
        date_param = request.query_params.get('date')

        if date_param:
            try:
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = date.today()

        # Get all food logs for this date
        logs = FoodLog.objects.filter(
            user=request.user,
            date=target_date
        )

        # Calculate totals
        totals = logs.aggregate(
            total_calories=Sum('calories'),
            total_protein=Sum('protein'),
            total_carbs=Sum('carbs'),
            total_fats=Sum('fats')
        )

        # Group by meal type
        meal_totals = {}
        for meal_type, _ in FoodLog.MEAL_TYPE_CHOICES:
            meal_logs = logs.filter(meal_type=meal_type)
            meal_totals[meal_type] = meal_logs.aggregate(
                calories=Sum('calories'),
                protein=Sum('protein'),
                carbs=Sum('carbs'),
                fats=Sum('fats')
            )

        return Response({
            'date': target_date,
            'totals': {
                'calories': totals['total_calories'] or 0,
                'protein': round(totals['total_protein'] or 0, 1),
                'carbs': round(totals['total_carbs'] or 0, 1),
                'fats': round(totals['total_fats'] or 0, 1),
            },
            'by_meal': meal_totals
        })
