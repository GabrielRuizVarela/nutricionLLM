"""
Tests for Recipe Generation with LLM (US5)
Following TDD approach - these tests are written before implementation.
"""
import pytest
import json
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest.mock import patch, Mock
import responses


@pytest.mark.django_db
class TestRecipeGeneration:
    """Test suite for LLM recipe generation functionality (US5)"""

    def setup_method(self):
        """Set up test client and create authenticated user before each test"""
        self.client = APIClient()
        self.generate_url = '/api/recipes/generate/'

        # Create a test user with profile
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Update profile with goal and preferences
        self.test_user.profile.goal = 'lose weight'
        self.test_user.profile.dietary_preferences = 'vegetarian'
        self.test_user.profile.save()

        self.token = Token.objects.create(user=self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    @responses.activate
    def test_successful_recipe_generation_with_valid_llm_response(self):
        """
        Test successful recipe generation with valid LLM response.
        AC: The system sends POST request to LLM Studio and returns recipe.
        """
        # Mock LLM response
        mock_recipe = {
            "nombre": "Ensalada de Lentejas",
            "ingredientes": "lentejas, tomate, pepino, aceite",
            "pasos": "1. Cocinar lentejas. 2. Picar verduras. 3. Mezclar.",
            "calorias": 320,
            "proteinas": 18.5,
            "carbohidratos": 45.0,
            "grasas": 8.2,
            "tiempo_min": 25,
            "tipo": "almuerzo"
        }

        responses.add(
            responses.POST,
            'http://localhost:1234/v1/chat/completions',
            json={'choices': [{'message': {'content': json.dumps(mock_recipe)}}]},
            status=200
        )

        data = {
            'meal_type': 'almuerzo',
            'available_time': 30,
            'available_ingredients': 'lentejas, tomate'
        }
        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'nombre' in response.data
        assert 'ingredientes' in response.data or 'ingredientes_texto' in response.data
        assert 'calorias' in response.data

    def test_recipe_generation_requires_meal_type(self):
        """
        Test that meal_type is required.
        AC: Form includes dropdown for meal_type.
        """
        data = {
            'available_time': 30
        }
        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'meal_type' in str(response.data).lower() or 'required' in str(response.data).lower()

    def test_recipe_generation_requires_available_time(self):
        """
        Test that available_time is required.
        AC: Form includes numeric input for available_time.
        """
        data = {
            'meal_type': 'desayuno'
        }
        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_recipe_generation_uses_user_profile_data(self):
        """
        Test that recipe generation uses user's goal and dietary_preferences.
        AC: Backend constructs prompt using user's goal and dietary_preferences.
        """
        with patch('httpx.post') as mock_post:
            mock_response = Mock()
            mock_recipe = {
                "nombre": "Test Recipe",
                "ingredientes": "test ingredients",
                "pasos": "1. Test step",
                "calorias": 300,
                "proteinas": 15.0,
                "carbohidratos": 40.0,
                "grasas": 10.0,
                "tiempo_min": 20,
                "tipo": "desayuno"
            }
            mock_response.json.return_value = {
                'choices': [{'message': {'content': json.dumps(mock_recipe)}}]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            data = {
                'meal_type': 'desayuno',
                'available_time': 20
            }
            response = self.client.post(self.generate_url, data, format='json')

            # Verify that httpx.post was called
            assert mock_post.called
            # Verify that the prompt includes user profile data
            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            prompt_content = request_data['messages'][0]['content']
            assert 'lose weight' in prompt_content.lower() or 'vegetarian' in prompt_content.lower()

    def test_recipe_generation_validates_meal_type_choices(self):
        """
        Test that meal_type must be one of the valid choices.
        AC: Dropdown has options: desayuno, almuerzo, cena, snack.
        """
        data = {
            'meal_type': 'invalid_meal_type',
            'available_time': 30
        }
        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @responses.activate
    def test_recipe_generation_handles_malformed_json_with_retry(self):
        """
        Test that system retries with correction prompt if JSON is invalid.
        AC: If validation fails, a second LLM call is made with correction prompt.
        """
        # First call returns malformed JSON
        responses.add(
            responses.POST,
            'http://localhost:1234/v1/chat/completions',
            json={'choices': [{'message': {'content': 'This is not valid JSON'}}]},
            status=200
        )

        # Second call (retry) returns valid JSON
        valid_recipe = {
            "nombre": "Retry Recipe",
            "ingredientes": "test",
            "pasos": "1. Test",
            "calorias": 300,
            "proteinas": 15.0,
            "carbohidratos": 40.0,
            "grasas": 10.0,
            "tiempo_min": 20,
            "tipo": "desayuno"
        }
        responses.add(
            responses.POST,
            'http://localhost:1234/v1/chat/completions',
            json={'choices': [{'message': {'content': json.dumps(valid_recipe)}}]},
            status=200
        )

        data = {
            'meal_type': 'desayuno',
            'available_time': 20
        }
        response = self.client.post(self.generate_url, data, format='json')

        # Should succeed after retry
        assert response.status_code == status.HTTP_200_OK
        # Verify two calls were made
        assert len(responses.calls) == 2

    @responses.activate
    def test_recipe_generation_fails_after_two_attempts(self):
        """
        Test that system returns error if both LLM attempts fail.
        AC: If both attempts fail, display "Could not generate a recipe."
        """
        # Both calls return invalid JSON
        for _ in range(2):
            responses.add(
                responses.POST,
                'http://localhost:1234/v1/chat/completions',
                json={'choices': [{'message': {'content': 'Invalid JSON'}}]},
                status=200
            )

        data = {
            'meal_type': 'cena',
            'available_time': 30
        }
        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR or \
               response.status_code == status.HTTP_400_BAD_REQUEST
        error_message = str(response.data).lower()
        assert 'could not generate' in error_message or 'error' in error_message

    def test_recipe_generation_requires_authentication(self):
        """
        Test that recipe generation requires authentication.
        """
        self.client.credentials()  # Remove authentication
        data = {
            'meal_type': 'desayuno',
            'available_time': 20
        }
        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_available_ingredients_is_optional(self):
        """
        Test that available_ingredients is optional.
        AC: Form has optional text field for available_ingredients.
        """
        with patch('httpx.post') as mock_post:
            mock_response = Mock()
            mock_recipe = {
                "nombre": "Test Recipe",
                "ingredientes": "any ingredients",
                "pasos": "1. Cook",
                "calorias": 300,
                "proteinas": 15.0,
                "carbohidratos": 40.0,
                "grasas": 10.0,
                "tiempo_min": 20,
                "tipo": "snack"
            }
            mock_response.json.return_value = {
                'choices': [{'message': {'content': json.dumps(mock_recipe)}}]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            # Request without available_ingredients
            data = {
                'meal_type': 'snack',
                'available_time': 15
            }
            response = self.client.post(self.generate_url, data, format='json')

            assert response.status_code == status.HTTP_200_OK

    @responses.activate
    def test_llm_request_uses_correct_model_and_temperature(self):
        """
        Test that LLM request uses correct model and temperature.
        AC: System sends request with model "llama3:8b" and temperature 0.4.
        """
        mock_recipe = {
            "nombre": "Test",
            "ingredientes": "test",
            "pasos": "1. Test",
            "calorias": 300,
            "proteinas": 15.0,
            "carbohidratos": 40.0,
            "grasas": 10.0,
            "tiempo_min": 20,
            "tipo": "almuerzo"
        }

        def request_callback(request):
            payload = json.loads(request.body)
            # Verify model and temperature
            assert payload.get('model') == 'llama3:8b'
            assert payload.get('temperature') == 0.4
            return (200, {}, json.dumps({'choices': [{'message': {'content': json.dumps(mock_recipe)}}]}))

        responses.add_callback(
            responses.POST,
            'http://localhost:1234/v1/chat/completions',
            callback=request_callback,
            content_type='application/json'
        )

        data = {
            'meal_type': 'almuerzo',
            'available_time': 30
        }
        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
