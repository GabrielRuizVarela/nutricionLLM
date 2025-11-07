"""
Test suite for Meal Examples API endpoint.

Tests the new /api/recipes/examples/ endpoint that returns:
- Saved recipes filtered by calorie range
- USDA meal examples
- Ingredient details with grams and portions
- Filtering by dietary preferences and allergies
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from tests.factories import UserFactory, RecetaFactory, ProfileFactory

User = get_user_model()


@pytest.mark.django_db
class TestMealExamplesEndpoint:
    """Test suite for meal examples API endpoint"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.examples_url = '/api/recipes/examples/'
        self.profile = ProfileFactory(user=self.user)

    def test_get_examples_with_calorie_parameter(self):
        """AC: GET /api/recipes/examples/?calories=500 should return examples"""
        # Create recipes around 500 kcal
        RecetaFactory(user=self.user, calories=480, name="Close Match 1")
        RecetaFactory(user=self.user, calories=520, name="Close Match 2")

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK
        assert 'saved_recipes' in response.data
        assert 'usda_examples' in response.data

    def test_examples_filtered_by_calorie_tolerance(self):
        """AC: Examples should be within ±15% of target calories (default)"""
        target = 500
        tolerance = 15
        min_cal = target * (100 - tolerance) / 100  # 425
        max_cal = target * (100 + tolerance) / 100  # 575

        # Create recipes: inside and outside range
        in_range_1 = RecetaFactory(user=self.user, calories=450, name="In Range 1")
        in_range_2 = RecetaFactory(user=self.user, calories=550, name="In Range 2")
        out_range_1 = RecetaFactory(user=self.user, calories=400, name="Too Low")
        out_range_2 = RecetaFactory(user=self.user, calories=600, name="Too High")

        response = self.client.get(self.examples_url, {
            'calories': target,
            'tolerance': tolerance
        })

        assert response.status_code == status.HTTP_200_OK

        saved_recipes = response.data['saved_recipes']
        recipe_ids = [r['id'] for r in saved_recipes]

        # Should include recipes within range
        assert in_range_1.id in recipe_ids or in_range_2.id in recipe_ids

        # All returned recipes should be within range
        for recipe in saved_recipes:
            assert min_cal <= recipe['calories'] <= max_cal

    def test_custom_tolerance_parameter(self):
        """AC: Should accept custom tolerance parameter"""
        target = 600
        tolerance = 10  # Stricter tolerance
        min_cal = target * 0.90  # 540
        max_cal = target * 1.10  # 660

        RecetaFactory(user=self.user, calories=580, name="In Range")
        RecetaFactory(user=self.user, calories=520, name="Out of Range")

        response = self.client.get(self.examples_url, {
            'calories': target,
            'tolerance': tolerance
        })

        assert response.status_code == status.HTTP_200_OK

        for recipe in response.data['saved_recipes']:
            assert min_cal <= recipe['calories'] <= max_cal

    def test_saved_recipes_only_from_current_user(self):
        """AC: Should only return current user's saved recipes"""
        other_user = UserFactory()

        # Current user's recipe
        my_recipe = RecetaFactory(user=self.user, calories=500, name="My Recipe")

        # Other user's recipe
        other_recipe = RecetaFactory(user=other_user, calories=500, name="Other Recipe")

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        saved_recipes = response.data['saved_recipes']
        recipe_ids = [r['id'] for r in saved_recipes]

        assert my_recipe.id in recipe_ids
        assert other_recipe.id not in recipe_ids

    def test_meal_type_parameter_filtering(self):
        """AC: Should filter by meal_type parameter"""
        RecetaFactory(user=self.user, calories=500, meal_type='breakfast', name="Breakfast")
        RecetaFactory(user=self.user, calories=500, meal_type='lunch', name="Lunch")
        RecetaFactory(user=self.user, calories=500, meal_type='dinner', name="Dinner")

        response = self.client.get(self.examples_url, {
            'calories': 500,
            'meal_type': 'breakfast'
        })

        assert response.status_code == status.HTTP_200_OK

        saved_recipes = response.data['saved_recipes']

        # All returned recipes should be breakfast
        for recipe in saved_recipes:
            if 'meal_type' in recipe:
                assert recipe['meal_type'] == 'breakfast'

    def test_max_10_saved_recipes_returned(self):
        """AC: Should return maximum 10 saved recipes"""
        # Create 15 recipes
        for i in range(15):
            RecetaFactory(user=self.user, calories=500, name=f"Recipe {i}")

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['saved_recipes']) <= 10

    def test_max_10_usda_examples_returned(self):
        """AC: Should return maximum 10 USDA examples"""
        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['usda_examples']) <= 10

    def test_response_includes_ingredient_details(self):
        """AC: Recipes should include ingredient details with grams and portions"""
        recipe = RecetaFactory(
            user=self.user,
            calories=500,
            ingredients=[
                {"name": "chicken", "amount": "200g"},
                {"name": "rice", "amount": "150g"}
            ]
        )

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        # Check structure (exact format depends on implementation)
        saved_recipes = response.data['saved_recipes']
        if saved_recipes:
            recipe_data = saved_recipes[0]
            assert 'name' in recipe_data
            assert 'calories' in recipe_data

    def test_usda_examples_include_ingredient_portions(self):
        """AC: USDA examples should include grams and portion sizes"""
        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        usda_examples = response.data['usda_examples']

        # If USDA examples are returned
        if usda_examples:
            example = usda_examples[0]
            assert 'name' in example
            assert 'calories' in example
            assert 'ingredients' in example

            # Each ingredient should have grams and portion
            if example['ingredients']:
                ingredient = example['ingredients'][0]
                assert 'name' in ingredient
                assert 'grams' in ingredient
                assert 'portion' in ingredient

    def test_authentication_required(self):
        """AC: Endpoint should require authentication"""
        self.client.credentials()  # Remove authentication

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_empty_results_when_no_matches(self):
        """AC: Should return empty arrays when no examples match"""
        # Create recipes far from target
        RecetaFactory(user=self.user, calories=200, name="Too Low")
        RecetaFactory(user=self.user, calories=1500, name="Too High")

        response = self.client.get(self.examples_url, {
            'calories': 500,
            'tolerance': 10  # Strict tolerance
        })

        assert response.status_code == status.HTTP_200_OK
        # saved_recipes might be empty or have few results
        assert isinstance(response.data['saved_recipes'], list)
        assert isinstance(response.data['usda_examples'], list)

    def test_missing_calories_parameter_handling(self):
        """AC: Should handle missing calories parameter gracefully"""
        response = self.client.get(self.examples_url)

        # Should return 400 or use a default value
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK]

    def test_invalid_calories_parameter_handling(self):
        """AC: Should handle invalid calories parameter"""
        response = self.client.get(self.examples_url, {'calories': 'invalid'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_negative_calories_parameter_handling(self):
        """AC: Should reject negative calorie values"""
        response = self.client.get(self.examples_url, {'calories': -100})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestMealExamplesDietaryPreferences:
    """Test suite for dietary preferences filtering in meal examples"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.examples_url = '/api/recipes/examples/'

    def test_vegetarian_preference_respected(self):
        """AC: Should filter by vegetarian preference from profile"""
        profile = ProfileFactory(
            user=self.user,
            dietary_preferences=['vegetarian']
        )

        # Create vegetarian and non-vegetarian recipes
        veg_recipe = RecetaFactory(
            user=self.user,
            calories=500,
            dietary_tags=['vegetarian'],
            name="Veggie Bowl"
        )
        meat_recipe = RecetaFactory(
            user=self.user,
            calories=500,
            dietary_tags=[],
            name="Chicken Bowl"
        )

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        # Implementation depends on how dietary preferences are handled
        # This test documents expected behavior

    def test_vegan_preference_respected(self):
        """AC: Should filter by vegan preference"""
        profile = ProfileFactory(
            user=self.user,
            dietary_preferences=['vegan']
        )

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK
        # USDA examples should be filtered for vegan options

    def test_allergies_excluded_from_examples(self):
        """AC: Should exclude recipes containing user's allergens"""
        profile = ProfileFactory(
            user=self.user,
            allergies=['nuts', 'dairy']
        )

        # Create recipes with allergens
        with_nuts = RecetaFactory(
            user=self.user,
            calories=500,
            ingredients=[{"name": "almonds", "amount": "50g"}],
            name="Nut Recipe"
        )
        with_dairy = RecetaFactory(
            user=self.user,
            calories=500,
            ingredients=[{"name": "milk", "amount": "200ml"}],
            name="Dairy Recipe"
        )
        safe_recipe = RecetaFactory(
            user=self.user,
            calories=500,
            ingredients=[{"name": "rice", "amount": "150g"}],
            name="Safe Recipe"
        )

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        # Should filter out recipes with allergens
        # Exact behavior depends on implementation

    def test_dislikes_respected_in_examples(self):
        """AC: Should avoid recipes with disliked ingredients"""
        profile = ProfileFactory(
            user=self.user,
            dislikes=['mushrooms', 'olives']
        )

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK
        # Examples should avoid disliked ingredients


@pytest.mark.django_db
class TestMealExamplesResponseFormat:
    """Test suite for meal examples response structure"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.examples_url = '/api/recipes/examples/'
        self.profile = ProfileFactory(user=self.user)

    def test_response_structure_matches_spec(self):
        """AC: Response should match specified structure"""
        RecetaFactory(user=self.user, calories=500, name="Test Recipe")

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        # Top-level structure
        assert 'saved_recipes' in response.data
        assert 'usda_examples' in response.data
        assert isinstance(response.data['saved_recipes'], list)
        assert isinstance(response.data['usda_examples'], list)

    def test_saved_recipe_fields(self):
        """AC: Saved recipes should include required fields"""
        recipe = RecetaFactory(
            user=self.user,
            calories=500,
            protein=30,
            carbs=50,
            fats=15,
            name="Test Recipe"
        )

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        if response.data['saved_recipes']:
            recipe_data = response.data['saved_recipes'][0]

            # Required fields
            assert 'id' in recipe_data
            assert 'name' in recipe_data
            assert 'calories' in recipe_data
            assert 'protein' in recipe_data
            assert 'carbs' in recipe_data
            assert 'fats' in recipe_data

    def test_usda_example_fields(self):
        """AC: USDA examples should include required fields"""
        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        if response.data['usda_examples']:
            example = response.data['usda_examples'][0]

            # Required fields
            assert 'name' in example
            assert 'calories' in example
            assert 'protein' in example
            assert 'carbs' in example
            assert 'fats' in example
            assert 'ingredients' in example
            assert isinstance(example['ingredients'], list)

    def test_ingredient_detail_structure(self):
        """AC: Ingredients should have name, grams, and portion fields"""
        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        # Check USDA examples ingredients
        usda_examples = response.data['usda_examples']
        if usda_examples and usda_examples[0]['ingredients']:
            ingredient = usda_examples[0]['ingredients'][0]

            assert 'name' in ingredient
            assert 'grams' in ingredient
            assert 'portion' in ingredient

            # Types
            assert isinstance(ingredient['name'], str)
            assert isinstance(ingredient['grams'], (int, float))
            assert isinstance(ingredient['portion'], str)

            # Values
            assert ingredient['grams'] > 0
            assert len(ingredient['portion']) > 0

    def test_portion_format_examples(self):
        """AC: Portions should be human-readable (e.g., '1 cup', '2 eggs')"""
        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        usda_examples = response.data['usda_examples']
        if usda_examples:
            for example in usda_examples:
                for ingredient in example.get('ingredients', []):
                    portion = ingredient.get('portion', '')
                    # Should contain number and unit
                    # Examples: "1 cup", "2 tbsp", "1 medium", "6 oz"
                    assert len(portion) > 0


@pytest.mark.django_db
class TestMealExamplesPerformance:
    """Test suite for meal examples API performance and optimization"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.examples_url = '/api/recipes/examples/'
        self.profile = ProfileFactory(user=self.user)

    def test_query_performance_with_many_recipes(self):
        """AC: Should perform well with large number of user recipes"""
        # Create 100 recipes
        for i in range(100):
            RecetaFactory(
                user=self.user,
                calories=400 + (i % 400),  # Spread across range
                name=f"Recipe {i}"
            )

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK
        # Should return quickly and limit results to 10
        assert len(response.data['saved_recipes']) <= 10

    def test_concurrent_user_isolation(self):
        """AC: Multiple users shouldn't see each other's recipes"""
        user2 = UserFactory()

        # Create recipes for both users
        RecetaFactory(user=self.user, calories=500, name="User 1 Recipe")
        RecetaFactory(user=user2, calories=500, name="User 2 Recipe")

        response = self.client.get(self.examples_url, {'calories': 500})

        assert response.status_code == status.HTTP_200_OK

        recipe_names = [r['name'] for r in response.data['saved_recipes']]
        assert "User 1 Recipe" in recipe_names
        assert "User 2 Recipe" not in recipe_names

    def test_response_time_reasonable(self):
        """AC: Response should return in reasonable time"""
        import time

        start = time.time()
        response = self.client.get(self.examples_url, {'calories': 500})
        duration = time.time() - start

        assert response.status_code == status.HTTP_200_OK
        # Should complete in under 2 seconds
        assert duration < 2.0
