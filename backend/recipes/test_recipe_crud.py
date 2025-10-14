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
            "nombre": "Lentil Salad",
            "ingredientes_texto": "1 cup cooked lentils, 1 cucumber, 2 tomatoes, olive oil, lemon",
            "pasos_texto": "1. Drain lentils. 2. Chop vegetables. 3. Mix with oil and lemon.",
            "calorias": 320,
            "proteinas": 18.5,
            "carbohidratos": 45.0,
            "grasas": 8.2,
            "tiempo_min": 10,
            "tipo": "almuerzo"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Receta.objects.filter(nombre="Lentil Salad").exists()

    def test_saved_recipe_is_linked_to_user(self):
        """
        Test that saved recipe is linked to the current user.
        AC: The backend creates a Receta object linked to the current user.
        """
        data = {
            "nombre": "User Recipe",
            "ingredientes_texto": "ingredients",
            "pasos_texto": "1. Step one",
            "calorias": 300,
            "proteinas": 15.0,
            "carbohidratos": 40.0,
            "grasas": 10.0,
            "tiempo_min": 20,
            "tipo": "cena"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        recipe = Receta.objects.get(nombre="User Recipe")
        assert recipe.user == self.test_user

    def test_save_recipe_returns_success_message(self):
        """
        Test that saving recipe returns success indication.
        AC: A success message is shown: "Recipe saved."
        """
        data = {
            "nombre": "Success Recipe",
            "ingredientes_texto": "ingredients",
            "pasos_texto": "1. Cook",
            "calorias": 250,
            "proteinas": 12.0,
            "carbohidratos": 35.0,
            "grasas": 8.0,
            "tiempo_min": 15,
            "tipo": "desayuno"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data or 'nombre' in response.data

    def test_save_recipe_requires_authentication(self):
        """
        Test that saving recipe requires authentication.
        """
        self.client.credentials()  # Remove authentication

        data = {
            "nombre": "Test Recipe",
            "ingredientes_texto": "ingredients",
            "pasos_texto": "steps",
            "calorias": 300,
            "proteinas": 15.0,
            "carbohidratos": 40.0,
            "grasas": 10.0,
            "tiempo_min": 20,
            "tipo": "almuerzo"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_save_recipe_validates_required_fields(self):
        """
        Test that all required fields must be provided.
        AC: Recipe model has all required fields.
        """
        data = {
            "nombre": "Incomplete Recipe"
            # Missing other required fields
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_save_recipe_validates_meal_type_choices(self):
        """
        Test that meal type must be one of valid choices.
        AC: tipo field has choices: desayuno, almuerzo, cena, snack.
        """
        data = {
            "nombre": "Invalid Type Recipe",
            "ingredientes_texto": "ingredients",
            "pasos_texto": "steps",
            "calorias": 300,
            "proteinas": 15.0,
            "carbohidratos": 40.0,
            "grasas": 10.0,
            "tiempo_min": 20,
            "tipo": "invalid_type"
        }
        response = self.client.post(self.recipes_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_save_recipe_validates_positive_values(self):
        """
        Test that numeric fields must be positive.
        """
        data = {
            "nombre": "Negative Calories",
            "ingredientes_texto": "ingredients",
            "pasos_texto": "steps",
            "calorias": -100,  # Invalid
            "proteinas": 15.0,
            "carbohidratos": 40.0,
            "grasas": 10.0,
            "tiempo_min": 20,
            "tipo": "almuerzo"
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
            nombre="Recipe 1",
            ingredientes_texto="ingredients 1",
            pasos_texto="steps 1",
            calorias=300,
            proteinas=15.0,
            carbohidratos=40.0,
            grasas=10.0,
            tiempo_min=20,
            tipo="desayuno"
        )
        Receta.objects.create(
            user=self.test_user,
            nombre="Recipe 2",
            ingredientes_texto="ingredients 2",
            pasos_texto="steps 2",
            calorias=400,
            proteinas=20.0,
            carbohidratos=50.0,
            grasas=15.0,
            tiempo_min=30,
            tipo="almuerzo"
        )
        # Recipe for other user
        Receta.objects.create(
            user=self.other_user,
            nombre="Other User Recipe",
            ingredientes_texto="other ingredients",
            pasos_texto="other steps",
            calorias=350,
            proteinas=18.0,
            carbohidratos=45.0,
            grasas=12.0,
            tiempo_min=25,
            tipo="cena"
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
        recipe_names = [r['nombre'] for r in results]
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
        assert results[0]['nombre'] == "Recipe 2"
        assert results[1]['nombre'] == "Recipe 1"

    def test_recipe_list_includes_essential_info(self):
        """
        Test that recipe list items include essential information.
        AC: Each item shows recipe name, meal type, and creation date.
        """
        response = self.client.get(self.recipes_url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data if isinstance(response.data, list) else response.data['results']

        for recipe in results:
            assert 'nombre' in recipe
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
        assert response.data['nombre'] == recipe.nombre
        assert 'ingredientes_texto' in response.data
        assert 'pasos_texto' in response.data
        assert 'calorias' in response.data

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
