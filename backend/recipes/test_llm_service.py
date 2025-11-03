"""
Tests for LLM service (OpenAI recipe generation).
Tests prompt generation, JSON parsing, retry logic, and error handling.
"""

import pytest
import json
import responses
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from users.models import Profile
from recipes.llm_service import generate_recipe_with_llm
from tests.factories import UserFactory, ProfileFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestLLMPromptGeneration:
    """Test that LLM prompts are generated correctly with user profile data."""

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_prompt_includes_user_profile_data(self, mock_openai):
        """Test that the prompt includes all relevant profile information."""
        # Setup
        user = UserFactory()
        profile = ProfileFactory(
            user=user,
            age=30,
            weight_kg=75.0,
            dietary_preferences='Vegetarian',
            allergies='Peanuts',
            cuisine_preferences='Italian, Mexican',
            cooking_skill_level='intermediate',
            available_ingredients='Pasta, tomatoes, cheese'
        )

        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                'name': 'Test Recipe',
                'ingredients': 'Test ingredients',
                'steps': 'Test steps',
                'calories': 400,
                'protein': 20,
                'carbs': 50,
                'fats': 10,
                'prep_time_minutes': 30,
                'meal_type': 'lunch'
            })))
        ]
        mock_openai.return_value = mock_response

        # Call function
        generate_recipe_with_llm(profile, 'lunch', 30)

        # Verify OpenAI was called
        assert mock_openai.called

        # Get the actual call arguments
        call_args = mock_openai.call_args
        messages = call_args[1]['messages']
        user_message = next(msg for msg in messages if msg['role'] == 'user')
        prompt = user_message['content']

        # Verify profile data is in prompt
        assert 'Vegetarian' in prompt
        assert 'Peanuts' in prompt
        assert 'Italian' in prompt
        assert 'intermediate' in prompt
        assert 'Pasta' in prompt

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_prompt_includes_meal_type_and_time(self, mock_openai):
        """Test that meal type and available time are included in the prompt."""
        user = UserFactory()
        profile = ProfileFactory(user=user)

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                'name': 'Breakfast Bowl',
                'ingredients': 'Oats, berries',
                'steps': 'Mix and serve',
                'calories': 300,
                'protein': 10,
                'carbs': 50,
                'fats': 5,
                'prep_time_minutes': 10,
                'meal_type': 'breakfast'
            })))
        ]
        mock_openai.return_value = mock_response

        generate_recipe_with_llm(profile, 'breakfast', 15)

        call_args = mock_openai.call_args
        messages = call_args[1]['messages']
        user_message = next(msg for msg in messages if msg['role'] == 'user')
        prompt = user_message['content']

        assert 'breakfast' in prompt.lower()
        assert '15' in prompt

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_prompt_includes_nutritional_targets(self, mock_openai):
        """Test that nutritional targets are included when set."""
        user = UserFactory()
        profile = ProfileFactory(
            user=user,
            daily_calorie_target=2000,
            daily_protein_target=150
        )

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                'name': 'Protein Bowl',
                'ingredients': 'Chicken, rice',
                'steps': 'Cook and combine',
                'calories': 500,
                'protein': 40,
                'carbs': 60,
                'fats': 10,
                'prep_time_minutes': 25,
                'meal_type': 'lunch'
            })))
        ]
        mock_openai.return_value = mock_response

        generate_recipe_with_llm(profile, 'lunch', 30)

        call_args = mock_openai.call_args
        messages = call_args[1]['messages']
        user_message = next(msg for msg in messages if msg['role'] == 'user')
        prompt = user_message['content']

        assert '2000' in prompt or 'calorie' in prompt.lower()


class TestLLMJSONParsing:
    """Test JSON parsing and validation of LLM responses."""

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_successful_json_parsing(self, mock_openai):
        """Test that valid JSON is parsed correctly."""
        user = UserFactory()
        profile = ProfileFactory(user=user)

        recipe_data = {
            'name': 'Grilled Chicken',
            'ingredients': 'Chicken breast, spices',
            'steps': 'Season and grill',
            'calories': 350,
            'protein': 45,
            'carbs': 5,
            'fats': 15,
            'prep_time_minutes': 20,
            'meal_type': 'lunch'
        }

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps(recipe_data)))
        ]
        mock_openai.return_value = mock_response

        result = generate_recipe_with_llm(profile, 'lunch', 30)

        assert result['name'] == 'Grilled Chicken'
        assert result['calories'] == 350
        assert result['protein'] == 45

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_malformed_json_triggers_retry(self, mock_openai):
        """Test that malformed JSON triggers a retry."""
        user = UserFactory()
        profile = ProfileFactory(user=user)

        # First response: malformed JSON
        # Second response: valid JSON
        valid_recipe = {
            'name': 'Valid Recipe',
            'ingredients': 'Test',
            'steps': 'Test',
            'calories': 400,
            'protein': 30,
            'carbs': 40,
            'fats': 15,
            'prep_time_minutes': 25,
            'meal_type': 'lunch'
        }

        mock_openai.side_effect = [
            MagicMock(choices=[
                MagicMock(message=MagicMock(content='{"invalid": json'))
            ]),
            MagicMock(choices=[
                MagicMock(message=MagicMock(content=json.dumps(valid_recipe)))
            ])
        ]

        result = generate_recipe_with_llm(profile, 'lunch', 30)

        # Should have been called twice (original + retry)
        assert mock_openai.call_count == 2
        # Should return the valid recipe from second attempt
        assert result['name'] == 'Valid Recipe'

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_two_failed_attempts_raises_error(self, mock_openai):
        """Test that two failed JSON parse attempts raises an error."""
        user = UserFactory()
        profile = ProfileFactory(user=user)

        # Both responses have malformed JSON
        mock_openai.side_effect = [
            MagicMock(choices=[
                MagicMock(message=MagicMock(content='{"invalid": json}'))
            ]),
            MagicMock(choices=[
                MagicMock(message=MagicMock(content='also not valid'))
            ])
        ]

        with pytest.raises(Exception) as exc_info:
            generate_recipe_with_llm(profile, 'lunch', 30)

        assert 'Failed to generate recipe' in str(exc_info.value)
        assert mock_openai.call_count == 2


class TestLLMModelConfiguration:
    """Test that the correct model and parameters are used."""

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_uses_gpt4o_model(self, mock_openai):
        """Test that GPT-4o model is used."""
        user = UserFactory()
        profile = ProfileFactory(user=user)

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                'name': 'Test',
                'ingredients': 'Test',
                'steps': 'Test',
                'calories': 400,
                'protein': 20,
                'carbs': 50,
                'fats': 10,
                'prep_time_minutes': 30,
                'meal_type': 'lunch'
            })))
        ]
        mock_openai.return_value = mock_response

        generate_recipe_with_llm(profile, 'lunch', 30)

        call_args = mock_openai.call_args
        assert call_args[1]['model'] == 'gpt-4o'

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_uses_correct_temperature(self, mock_openai):
        """Test that temperature is set to 0.7 for creativity."""
        user = UserFactory()
        profile = ProfileFactory(user=user)

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                'name': 'Test',
                'ingredients': 'Test',
                'steps': 'Test',
                'calories': 400,
                'protein': 20,
                'carbs': 50,
                'fats': 10,
                'prep_time_minutes': 30,
                'meal_type': 'lunch'
            })))
        ]
        mock_openai.return_value = mock_response

        generate_recipe_with_llm(profile, 'lunch', 30)

        call_args = mock_openai.call_args
        assert call_args[1]['temperature'] == 0.7


class TestLLMErrorHandling:
    """Test error handling for API failures."""

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_openai_api_error_raises_exception(self, mock_openai):
        """Test that OpenAI API errors are properly raised."""
        user = UserFactory()
        profile = ProfileFactory(user=user)

        mock_openai.side_effect = Exception("OpenAI API Error")

        with pytest.raises(Exception) as exc_info:
            generate_recipe_with_llm(profile, 'lunch', 30)

        assert "OpenAI API Error" in str(exc_info.value)

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_empty_response_handles_gracefully(self, mock_openai):
        """Test handling of empty or null responses."""
        user = UserFactory()
        profile = ProfileFactory(user=user)

        mock_response = MagicMock()
        mock_response.choices = []
        mock_openai.return_value = mock_response

        with pytest.raises(Exception):
            generate_recipe_with_llm(profile, 'lunch', 30)


class TestLLMRecipeValidation:
    """Test that generated recipes have all required fields."""

    @patch('recipes.llm_service.client.chat.completions.create')
    def test_recipe_has_all_required_fields(self, mock_openai):
        """Test that the returned recipe has all necessary fields."""
        user = UserFactory()
        profile = ProfileFactory(user=user)

        recipe_data = {
            'name': 'Complete Recipe',
            'ingredients': 'Ingredient 1, Ingredient 2',
            'steps': 'Step 1\nStep 2',
            'calories': 450,
            'protein': 30.5,
            'carbs': 45.0,
            'fats': 15.5,
            'prep_time_minutes': 35,
            'meal_type': 'dinner'
        }

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps(recipe_data)))
        ]
        mock_openai.return_value = mock_response

        result = generate_recipe_with_llm(profile, 'dinner', 40)

        # Verify all fields present
        required_fields = ['name', 'ingredients', 'steps', 'calories', 'protein',
                          'carbs', 'fats', 'prep_time_minutes', 'meal_type']
        for field in required_fields:
            assert field in result
            assert result[field] is not None
