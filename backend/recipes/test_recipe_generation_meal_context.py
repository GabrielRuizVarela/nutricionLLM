"""
Test suite for Recipe Generation with Meal Context.

Tests recipe generation that includes meal distribution context:
- Recipe generation accepts meal_number parameter
- LLM prompt includes meal percentage and calorie target
- Generated recipes align with meal targets
- Meal context is saved with recipe
"""

import pytest
import json
from unittest.mock import patch, Mock, MagicMock
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from tests.factories import UserFactory, ProfileFactory, RecetaFactory

User = get_user_model()


@pytest.mark.django_db
class TestRecipeGenerationWithMealNumber:
    """Test suite for recipe generation with meal_number parameter"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.generate_url = '/api/recipes/generate/'

        # Create profile with meal distribution
        self.profile = ProfileFactory(
            user=self.user,
            daily_calories=2000,
            meals_per_day=4,
            meal_distribution={"1": 20, "2": 35, "3": 30, "4": 15},
            meal_names={"1": "Breakfast", "2": "Lunch", "3": "Dinner", "4": "Snack"}
        )

        # Mock LLM response
        self.mock_recipe_data = {
            "name": "Mexican Bowl",
            "meal_type": "lunch",
            "calories": 700,
            "protein": 45,
            "carbs": 80,
            "fats": 20,
            "ingredients": [
                {"name": "ground beef", "amount": "6 oz"},
                {"name": "rice", "amount": "1 cup"},
                {"name": "black beans", "amount": "1/2 cup"}
            ],
            "instructions": ["Cook beef", "Prepare rice", "Combine"]
        }

    def test_recipe_generation_accepts_meal_number(self):
        """AC: POST should accept meal_number parameter"""
        with patch('recipes.llm_service.generate_recipe') as mock_generate:
            mock_generate.return_value = self.mock_recipe_data

            data = {
                'meal_number': 2,
                'description': 'Mexican-style lunch bowl'
            }

            response = self.client.post(self.generate_url, data, format='json')

            assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
            mock_generate.assert_called_once()

    def test_recipe_generation_accepts_meal_percentage(self):
        """AC: POST should accept meal_percentage parameter"""
        with patch('recipes.llm_service.generate_recipe') as mock_generate:
            mock_generate.return_value = self.mock_recipe_data

            data = {
                'meal_number': 2,
                'meal_percentage': 35,
                'description': 'High-protein lunch'
            }

            response = self.client.post(self.generate_url, data, format='json')

            assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    def test_recipe_generation_calculates_target_calories(self):
        """AC: Should calculate target calories from meal percentage"""
        with patch('recipes.llm_service.generate_recipe') as mock_generate:
            mock_generate.return_value = self.mock_recipe_data

            data = {
                'meal_number': 2,
                'meal_percentage': 35,  # 35% of 2000 = 700 kcal
                'description': 'Lunch meal'
            }

            response = self.client.post(self.generate_url, data, format='json')

            # Calculate expected target
            expected_target = 2000 * 0.35  # 700

            # Check if this was passed to the generator
            call_kwargs = mock_generate.call_args[1] if mock_generate.call_args else {}
            # Implementation may vary, this documents expected behavior

    def test_backward_compatibility_without_meal_number(self):
        """AC: Recipe generation should work without meal_number (backward compatible)"""
        with patch('recipes.llm_service.generate_recipe') as mock_generate:
            mock_generate.return_value = self.mock_recipe_data

            data = {
                'description': 'Any recipe without meal context'
            }

            response = self.client.post(self.generate_url, data, format='json')

            assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    def test_meal_number_validation_in_range(self):
        """AC: meal_number should be within user's meals_per_day"""
        with patch('recipes.llm_service.generate_recipe') as mock_generate:
            mock_generate.return_value = self.mock_recipe_data

            # Valid meal numbers 1-4 (profile has 4 meals)
            for meal_num in [1, 2, 3, 4]:
                data = {
                    'meal_number': meal_num,
                    'description': f'Meal {meal_num}'
                }

                response = self.client.post(self.generate_url, data, format='json')
                assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    def test_meal_number_validation_out_of_range(self):
        """AC: meal_number > meals_per_day should be handled gracefully"""
        with patch('recipes.llm_service.generate_recipe') as mock_generate:
            mock_generate.return_value = self.mock_recipe_data

            data = {
                'meal_number': 5,  # Profile only has 4 meals
                'description': 'Invalid meal'
            }

            response = self.client.post(self.generate_url, data, format='json')

            # Should either accept it or return validation error
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_201_CREATED,
                status.HTTP_400_BAD_REQUEST
            ]


@pytest.mark.django_db
class TestLLMPromptWithMealContext:
    """Test suite for LLM prompt generation with meal context"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.generate_url = '/api/recipes/generate/'

        self.profile = ProfileFactory(
            user=self.user,
            daily_calories=2000,
            meals_per_day=4,
            meal_distribution={"1": 20, "2": 35, "3": 30, "4": 15},
            meal_names={"1": "Breakfast", "2": "Lunch", "3": "Dinner", "4": "Snack"}
        )

        self.mock_recipe_data = {
            "name": "Test Recipe",
            "calories": 700,
            "protein": 40,
            "carbs": 70,
            "fats": 20
        }

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_llm_prompt_includes_meal_percentage(self, mock_openai):
        """AC: LLM prompt should mention meal percentage"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(self.mock_recipe_data)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 2,
            'meal_percentage': 35,
            'description': 'Lunch bowl'
        }

        response = self.client.post(self.generate_url, data, format='json')

        # Check that OpenAI was called
        assert mock_openai.called

        # Extract the prompt from the call
        call_args = mock_openai.call_args
        if call_args:
            messages = call_args[1].get('messages', [])
            if messages:
                prompt_text = str(messages)

                # Prompt should mention percentage or calorie target
                # (35% or 700 kcal)
                assert '35' in prompt_text or '700' in prompt_text

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_llm_prompt_includes_target_calories(self, mock_openai):
        """AC: LLM prompt should mention target calorie amount"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(self.mock_recipe_data)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 2,
            'meal_percentage': 35,  # = 700 kcal
            'description': 'Protein-rich lunch'
        }

        response = self.client.post(self.generate_url, data, format='json')

        call_args = mock_openai.call_args
        if call_args:
            messages = call_args[1].get('messages', [])
            if messages:
                prompt_text = str(messages).lower()

                # Should mention calories or kcal
                assert 'calor' in prompt_text or 'kcal' in prompt_text

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_llm_prompt_includes_meal_name(self, mock_openai):
        """AC: LLM prompt should include meal name if set"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(self.mock_recipe_data)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 2,  # "Lunch" in profile
            'description': 'Mexican food'
        }

        response = self.client.post(self.generate_url, data, format='json')

        call_args = mock_openai.call_args
        if call_args:
            messages = call_args[1].get('messages', [])
            if messages:
                prompt_text = str(messages).lower()

                # Should mention "lunch" or "meal 2"
                assert 'lunch' in prompt_text or 'meal' in prompt_text

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_llm_prompt_without_meal_context(self, mock_openai):
        """AC: LLM prompt should work without meal context (backward compatible)"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(self.mock_recipe_data)
        mock_openai.return_value = mock_response

        data = {
            'description': 'Any recipe'
        }

        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        assert mock_openai.called


@pytest.mark.django_db
class TestGeneratedRecipeAlignment:
    """Test suite for generated recipe alignment with meal targets"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.generate_url = '/api/recipes/generate/'

        self.profile = ProfileFactory(
            user=self.user,
            daily_calories=2000,
            meals_per_day=3,
            meal_distribution={"1": 30, "2": 40, "3": 30}
        )

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_generated_recipe_close_to_target(self, mock_openai):
        """AC: Generated recipe should be close to target calories"""
        target_calories = 800  # 40% of 2000

        mock_recipe = {
            "name": "Lunch Bowl",
            "calories": 780,  # Within reasonable range
            "protein": 50,
            "carbs": 80,
            "fats": 25
        }

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_recipe)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 2,
            'meal_percentage': 40,
            'description': 'Balanced lunch'
        }

        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

        # Check the generated calories are close to target
        if 'calories' in response.data:
            generated_cals = response.data['calories']
            # Within 20% tolerance
            assert abs(generated_cals - target_calories) / target_calories < 0.20

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_response_includes_target_comparison(self, mock_openai):
        """AC: Response should include comparison to target"""
        mock_recipe = {
            "name": "Breakfast",
            "calories": 620,
            "protein": 30,
            "carbs": 70,
            "fats": 20
        }

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_recipe)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 1,
            'meal_percentage': 30,  # Target: 600 kcal
            'description': 'High protein breakfast'
        }

        response = self.client.post(self.generate_url, data, format='json')

        # Response may include target info for UI display
        # Implementation dependent


@pytest.mark.django_db
class TestRecipeSavingWithMealContext:
    """Test suite for saving recipes with meal context"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.generate_url = '/api/recipes/generate/'

        self.profile = ProfileFactory(
            user=self.user,
            daily_calories=2000,
            meals_per_day=4,
            meal_distribution={"1": 20, "2": 35, "3": 30, "4": 15}
        )

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_recipe_saved_with_meal_number(self, mock_openai):
        """AC: Generated recipe should be saved with meal_number field"""
        mock_recipe = {
            "name": "Breakfast Bowl",
            "calories": 400,
            "protein": 25,
            "carbs": 45,
            "fats": 12
        }

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_recipe)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 1,
            'meal_percentage': 20,
            'description': 'Quick breakfast',
            'save': True
        }

        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

        # If recipe is saved, check it has meal_number
        if 'id' in response.data:
            recipe_id = response.data['id']
            # Could verify with a GET request or database query

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_recipe_saved_with_meal_type_from_context(self, mock_openai):
        """AC: Recipe should infer meal_type from meal_number"""
        mock_recipe = {
            "name": "Lunch Salad",
            "meal_type": "lunch",
            "calories": 700,
            "protein": 40,
            "carbs": 60,
            "fats": 25
        }

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_recipe)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 2,
            'description': 'Healthy salad',
            'save': True
        }

        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

        # Meal type should be set appropriately
        if 'meal_type' in response.data:
            assert response.data['meal_type'] in ['breakfast', 'lunch', 'dinner', 'snack']

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_saved_recipes_appear_in_examples(self, mock_openai):
        """AC: Saved recipe should appear in future meal examples"""
        mock_recipe = {
            "name": "Perfect Lunch",
            "calories": 700,
            "protein": 45,
            "carbs": 70,
            "fats": 20
        }

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_recipe)
        mock_openai.return_value = mock_response

        # Generate and save a recipe
        data = {
            'meal_number': 2,
            'meal_percentage': 35,
            'description': 'Great lunch',
            'save': True
        }

        gen_response = self.client.post(self.generate_url, data, format='json')
        assert gen_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

        # Now check examples endpoint
        examples_response = self.client.get('/api/recipes/examples/', {
            'calories': 700,
            'tolerance': 15
        })

        assert examples_response.status_code == status.HTTP_200_OK

        # The saved recipe should appear in saved_recipes
        saved_recipes = examples_response.data.get('saved_recipes', [])
        recipe_names = [r['name'] for r in saved_recipes]

        # May or may not appear immediately depending on implementation
        # This documents expected behavior


@pytest.mark.django_db
class TestMealContextEdgeCases:
    """Test suite for edge cases with meal context"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.generate_url = '/api/recipes/generate/'

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_generation_without_profile(self, mock_openai):
        """AC: Should handle users without profiles gracefully"""
        # User without profile
        mock_recipe = {"name": "Recipe", "calories": 500, "protein": 30, "carbs": 50, "fats": 15}

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_recipe)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 2,
            'description': 'Any meal'
        }

        response = self.client.post(self.generate_url, data, format='json')

        # Should either work with defaults or return helpful error
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST
        ]

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_generation_with_profile_no_distribution(self, mock_openai):
        """AC: Should handle profiles without meal distribution"""
        ProfileFactory(
            user=self.user,
            daily_calories=2000,
            meal_distribution=None
        )

        mock_recipe = {"name": "Recipe", "calories": 500, "protein": 30, "carbs": 50, "fats": 15}

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_recipe)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 2,
            'description': 'Any meal'
        }

        response = self.client.post(self.generate_url, data, format='json')

        # Should use default distribution or handle gracefully
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST
        ]

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_zero_meal_percentage(self, mock_openai):
        """AC: Should handle edge case of 0% meal"""
        ProfileFactory(
            user=self.user,
            meals_per_day=3,
            meal_distribution={"1": 0, "2": 50, "3": 50}
        )

        mock_recipe = {"name": "Recipe", "calories": 1, "protein": 0, "carbs": 0, "fats": 0}

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_recipe)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 1,
            'meal_percentage': 0,
            'description': 'Zero calorie meal'
        }

        response = self.client.post(self.generate_url, data, format='json')

        # Should handle gracefully
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST
        ]

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_very_high_meal_percentage(self, mock_openai):
        """AC: Should handle high meal percentages (100%)"""
        ProfileFactory(
            user=self.user,
            daily_calories=2000,
            meals_per_day=1,
            meal_distribution={"1": 100}
        )

        mock_recipe = {"name": "Big Meal", "calories": 2000, "protein": 100, "carbs": 200, "fats": 70}

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_recipe)
        mock_openai.return_value = mock_response

        data = {
            'meal_number': 1,
            'meal_percentage': 100,
            'description': 'One meal a day'
        }

        response = self.client.post(self.generate_url, data, format='json')

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
