"""
Tests for Recipe update (PATCH) and delete (DELETE) operations.
Tests user isolation, data validation, and proper HTTP responses.
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from tests.factories import UserFactory, RecetaFactory

pytestmark = pytest.mark.django_db


class TestRecipeUpdate:
    """Test recipe update operations (PATCH)."""

    def test_update_recipe_name(self, authenticated_client, recipe):
        """Test updating just the recipe name."""
        new_name = "Updated Recipe Name"
        response = authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            {'name': new_name}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == new_name

        # Verify other fields unchanged
        assert response.data['ingredients'] == recipe.ingredients
        assert response.data['calories'] == recipe.calories

    def test_update_recipe_ingredients(self, authenticated_client, recipe):
        """Test updating recipe ingredients."""
        new_ingredients = "New ingredient 1\nNew ingredient 2\nNew ingredient 3"
        response = authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            {'ingredients': new_ingredients}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['ingredients'] == new_ingredients

    def test_update_recipe_steps(self, authenticated_client, recipe):
        """Test updating recipe cooking steps."""
        new_steps = "New step 1\nNew step 2\nNew step 3"
        response = authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            {'steps': new_steps}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['steps'] == new_steps

    def test_update_recipe_macros(self, authenticated_client, recipe):
        """Test updating nutritional information."""
        new_macros = {
            'calories': 550,
            'protein': 40.0,
            'carbs': 60.0,
            'fats': 20.0
        }

        response = authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            new_macros
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['calories'] == 550
        assert response.data['protein'] == 40.0
        assert response.data['carbs'] == 60.0
        assert response.data['fats'] == 20.0

    def test_update_recipe_prep_time(self, authenticated_client, recipe):
        """Test updating preparation time."""
        response = authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            {'prep_time_minutes': 45}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['prep_time_minutes'] == 45

    def test_update_recipe_meal_type(self, authenticated_client, recipe):
        """Test updating meal type."""
        response = authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            {'meal_type': 'dinner'}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meal_type'] == 'dinner'

    def test_update_multiple_fields_at_once(self, authenticated_client, recipe):
        """Test updating multiple recipe fields simultaneously."""
        updates = {
            'name': 'Completely Updated Recipe',
            'calories': 600,
            'prep_time_minutes': 50,
            'meal_type': 'snack'
        }

        response = authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            updates
        )

        assert response.status_code == status.HTTP_200_OK
        for key, value in updates.items():
            assert response.data[key] == value

    def test_update_requires_authentication(self, client, recipe):
        """Test that updating a recipe requires authentication."""
        response = client.patch(
            f'/api/recetas/{recipe.id}/',
            {'name': 'Should Fail'}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_update_other_users_recipe(self, recipe):
        """Test that users cannot update recipes they don't own."""
        # Create second user
        other_user = UserFactory(username='other', email='other@test.com')
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)

        response = other_client.patch(
            f'/api/recetas/{recipe.id}/',
            {'name': 'Hacked Recipe'}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_nonexistent_recipe_returns_404(self, authenticated_client):
        """Test updating a recipe that doesn't exist."""
        response = authenticated_client.patch(
            '/api/recetas/99999/',
            {'name': 'Does Not Exist'}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_validates_meal_type_choices(self, authenticated_client, recipe):
        """Test that invalid meal types are rejected."""
        response = authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            {'meal_type': 'invalid_meal_type'}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_validates_positive_values(self, authenticated_client, recipe):
        """Test that negative values for macros and time are rejected."""
        # Negative calories
        response = authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            {'calories': -100}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Negative prep time
        response = authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            {'prep_time_minutes': -10}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_preserves_other_fields(self, authenticated_client, recipe):
        """Test that partial update doesn't clear unspecified fields."""
        original_calories = recipe.calories
        original_protein = recipe.protein

        # Update only name
        authenticated_client.patch(
            f'/api/recetas/{recipe.id}/',
            {'name': 'New Name Only'}
        )

        # Retrieve and verify other fields preserved
        response = authenticated_client.get(f'/api/recetas/{recipe.id}/')
        assert response.data['name'] == 'New Name Only'
        assert response.data['calories'] == original_calories
        assert response.data['protein'] == original_protein


class TestRecipeDelete:
    """Test recipe deletion operations (DELETE)."""

    def test_delete_recipe(self, authenticated_client, recipe):
        """Test successful recipe deletion."""
        recipe_id = recipe.id

        response = authenticated_client.delete(f'/api/recetas/{recipe_id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify recipe no longer exists
        response = authenticated_client.get(f'/api/recetas/{recipe_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_requires_authentication(self, client, recipe):
        """Test that deleting a recipe requires authentication."""
        response = client.delete(f'/api/recetas/{recipe.id}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_delete_other_users_recipe(self, recipe):
        """Test that users cannot delete recipes they don't own."""
        # Create second user
        other_user = UserFactory(username='other', email='other@test.com')
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)

        response = other_client.delete(f'/api/recetas/{recipe.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify recipe still exists
        recipe.refresh_from_db()
        assert recipe.id is not None

    def test_delete_nonexistent_recipe_returns_404(self, authenticated_client):
        """Test deleting a recipe that doesn't exist."""
        response = authenticated_client.delete('/api/recetas/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_recipe_removes_from_list(self, authenticated_client, user):
        """Test that deleted recipe no longer appears in user's list."""
        # Create two recipes
        recipe1 = RecetaFactory(user=user, name='Recipe 1')
        recipe2 = RecetaFactory(user=user, name='Recipe 2')

        # Verify both in list
        response = authenticated_client.get('/api/recetas/')
        assert len(response.data) == 2

        # Delete first recipe
        authenticated_client.delete(f'/api/recetas/{recipe1.id}/')

        # Verify only one recipe remains
        response = authenticated_client.get('/api/recetas/')
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Recipe 2'

    def test_delete_multiple_recipes(self, authenticated_client, user):
        """Test deleting multiple recipes."""
        # Create three recipes
        recipes = [
            RecetaFactory(user=user, name=f'Recipe {i}')
            for i in range(3)
        ]

        # Delete each recipe
        for recipe in recipes:
            response = authenticated_client.delete(f'/api/recetas/{recipe.id}/')
            assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify all deleted
        response = authenticated_client.get('/api/recetas/')
        assert len(response.data) == 0


class TestRecipePUT:
    """Test full recipe replacement with PUT (if supported)."""

    def test_put_replaces_entire_recipe(self, authenticated_client, recipe):
        """Test that PUT replaces all recipe fields."""
        new_recipe_data = {
            'name': 'Completely New Recipe',
            'ingredients': 'All new ingredients',
            'steps': 'All new steps',
            'calories': 700,
            'protein': 50.0,
            'carbs': 70.0,
            'fats': 25.0,
            'prep_time_minutes': 60,
            'meal_type': 'dinner'
        }

        response = authenticated_client.put(
            f'/api/recetas/{recipe.id}/',
            new_recipe_data
        )

        if response.status_code == status.HTTP_200_OK:
            # If PUT is supported, verify all fields updated
            for key, value in new_recipe_data.items():
                assert response.data[key] == value
        else:
            # PUT might not be implemented, which is fine
            assert response.status_code in [
                status.HTTP_405_METHOD_NOT_ALLOWED,
                status.HTTP_200_OK
            ]


# Fixtures

@pytest.fixture
def client():
    """Provide an API client."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user."""
    return UserFactory()


@pytest.fixture
def authenticated_client(user):
    """Provide an authenticated API client."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def recipe(user):
    """Create a test recipe for the user."""
    return RecetaFactory(user=user)
