"""
Tests for Recipe Saving and Listing (US6, US7, US8)
Following TDD approach - these tests are written before implementation.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from recipes.models import Receta


@pytest.mark.django_db
class TestRecipeSaving:
    """Test suite for recipe saving functionality (US6-7)"""

    def setup_method(self):
        """Set up test client and create authenticated user before each test"""
        self.client = APIClient()
        self.recipes_url = '/api/recetas/'

        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_save_recipe_with_valid_data(self):
        """
        Test that user can save a recipe with all required fields.
        AC: POST request to /api/recetas/ creates a Receta object.
        """
        data = {
            "name": "Lentil Salad",
            "ingredients": "1 cup cooked lentils, 1 cucumber, 2 tomatoes, olive oil, lemon",
            "steps": "1. Drain lentils. 2. Chop vegetables. 3. Mix with oil and lemon.",
            "calories": 320,
            "protein": 18.5,
            "carbs": 45.0,
            "fats": 8.2,
            "prep_time_minutes": 10,
            "meal_type": "lunch"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Receta.objects.filter(name="Lentil Salad").exists()

    def test_saved_recipe_is_linked_to_user(self):
        """
        Test that saved recipe is linked to the current user.
        AC: The backend creates a Receta object linked to the current user.
        """
        data = {
            "name": "User Recipe",
            "ingredients": "ingredients",
            "steps": "1. Step one",
            "calories": 300,
            "protein": 15.0,
            "carbs": 40.0,
            "fats": 10.0,
            "prep_time_minutes": 20,
            "meal_type": "dinner"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        recipe = Receta.objects.get(name="User Recipe")
        assert recipe.user == self.test_user

    def test_save_recipe_returns_success_message(self):
        """
        Test that saving recipe returns success indication.
        AC: A success message is shown: "Recipe saved."
        """
        data = {
            "name": "Success Recipe",
            "ingredients": "ingredients",
            "steps": "1. Cook",
            "calories": 250,
            "protein": 12.0,
            "carbs": 35.0,
            "fats": 8.0,
            "prep_time_minutes": 15,
            "meal_type": "breakfast"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data or 'name' in response.data

    def test_save_recipe_requires_authentication(self):
        """
        Test that saving recipe requires authentication.
        """
        self.client.credentials()  # Remove authentication

        data = {
            "name": "Test Recipe",
            "ingredients": "ingredients",
            "steps": "steps",
            "calories": 300,
            "protein": 15.0,
            "carbs": 40.0,
            "fats": 10.0,
            "prep_time_minutes": 20,
            "meal_type": "lunch"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_save_recipe_validates_required_fields(self):
        """
        Test that all required fields must be provided.
        AC: Recipe model has all required fields.
        """
        data = {
            "name": "Incomplete Recipe"
            # Missing other required fields
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_save_recipe_validates_meal_type_choices(self):
        """
        Test that meal type must be one of valid choices.
        AC: meal_type field has choices: breakfast, lunch, dinner, snack.
        """
        data = {
            "name": "Invalid Type Recipe",
            "ingredients": "ingredients",
            "steps": "steps",
            "calories": 300,
            "protein": 15.0,
            "carbs": 40.0,
            "fats": 10.0,
            "prep_time_minutes": 20,
            "meal_type": "invalid_type"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_save_recipe_validates_positive_values(self):
        """
        Test that numeric fields must be positive.
        """
        data = {
            "name": "Negative Calories",
            "ingredients": "ingredients",
            "steps": "steps",
            "calories": -100,  # Invalid
            "protein": 15.0,
            "carbs": 40.0,
            "fats": 10.0,
            "prep_time_minutes": 20,
            "meal_type": "lunch"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRecipeList:
    """Test suite for viewing saved recipes list (US8)"""

    def setup_method(self):
        """Set up test client and create test data before each test"""
        self.client = APIClient()
        self.recipes_url = '/api/recetas/'

        # Create test users
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

        self.token = Token.objects.create(user=self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Create some test recipes
        Receta.objects.create(
            user=self.test_user,
            name="Recipe 1",
            ingredients="ingredients 1",
            steps="steps 1",
            calories=300,
            protein=15.0,
            carbs=40.0,
            fats=10.0,
            prep_time_minutes=20,
            tipo="breakfast"
        )
        Receta.objects.create(
            user=self.test_user,
            name="Recipe 2",
            ingredients="ingredients 2",
            steps="steps 2",
            calories=400,
            protein=20.0,
            carbs=50.0,
            fats=15.0,
            prep_time_minutes=30,
            tipo="lunch"
        )
        # Recipe for other user
        Receta.objects.create(
            user=self.other_user,
            name="Other User Recipe",
            ingredients="other ingredients",
            steps="other steps",
            calories=350,
            protein=18.0,
            carbs=45.0,
            fats=12.0,
            prep_time_minutes=25,
            tipo="dinner"
        )

    def test_get_user_recipes_list(self):
        """
        Test that user can retrieve their saved recipes.
        AC: User sees a list of saved recipes.
        """
        response = self.client.get(self.recipes_url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list) or 'results' in response.data

    def test_recipes_list_shows_only_user_recipes(self):
        """
        Test that user only sees their own recipes.
        AC: Only recipes belonging to the current user are displayed.
        """
        response = self.client.get(self.recipes_url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data if isinstance(response.data, list) else response.data['results']

        # Should have 2 recipes (not 3, excluding other user's recipe)
        assert len(results) == 2
        recipe_names = [r['name'] for r in results]
        assert "Recipe 1" in recipe_names
        assert "Recipe 2" in recipe_names
        assert "Other User Recipe" not in recipe_names

    def test_recipes_list_ordered_by_most_recent(self):
        """
        Test that recipes are ordered from most recent to oldest.
        AC: The list is ordered from most recent to oldest.
        """
        response = self.client.get(self.recipes_url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data if isinstance(response.data, list) else response.data['results']

        # Most recent should be Recipe 2 (created last)
        assert results[0]['name'] == "Recipe 2"
        assert results[1]['name'] == "Recipe 1"

    def test_recipe_list_includes_essential_info(self):
        """
        Test that recipe list items include essential information.
        AC: Each item shows recipe name, meal type, and creation date.
        """
        response = self.client.get(self.recipes_url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data if isinstance(response.data, list) else response.data['results']

        for recipe in results:
            assert 'name' in recipe
            assert 'tipo' in recipe
            assert 'created_at' in recipe

    def test_get_recipe_detail(self):
        """
        Test that user can view full recipe details.
        AC: Clicking a recipe opens its detailed view.
        """
        recipe = Receta.objects.filter(user=self.test_user).first()
        detail_url = f'{self.recipes_url}{recipe.id}/'

        response = self.client.get(detail_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == recipe.name
        assert 'ingredients' in response.data
        assert 'steps' in response.data
        assert 'calories' in response.data

    def test_recipe_list_requires_authentication(self):
        """
        Test that viewing recipes requires authentication.
        """
        self.client.credentials()  # Remove authentication
        response = self.client.get(self.recipes_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_view_other_user_recipe_detail(self):
        """
        Test that user cannot view another user's recipe details.
        """
        other_recipe = Receta.objects.get(user=self.other_user)
        detail_url = f'{self.recipes_url}{other_recipe.id}/'

        response = self.client.get(detail_url)

        # Should either be 404 (not found) or 403 (forbidden)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]
