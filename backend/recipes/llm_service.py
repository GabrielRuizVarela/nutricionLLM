"""
LLM Service for recipe generation using LLM Studio.
"""
import json
import logging
import httpx
from django.conf import settings
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with LLM Studio API"""

    def __init__(self):
        self.url = settings.LLM_STUDIO_URL
        self.model = settings.LLM_STUDIO_MODEL

    def generate_recipe(
        self,
        meal_type: str,
        available_time: int,
        goal: str = "",
        dietary_preferences: str = "",
        available_ingredients: str = ""
    ) -> Dict:
        """
        Generate a recipe using LLM Studio.

        Args:
            meal_type: Type of meal (desayuno, almuerzo, cena, snack)
            available_time: Available time in minutes
            goal: User's nutritional goal
            dietary_preferences: User's dietary preferences
            available_ingredients: Available ingredients (optional)

        Returns:
            Dictionary containing recipe data

        Raises:
            Exception: If recipe generation fails after retry
        """
        # Construct the prompt
        prompt = self._build_prompt(
            meal_type=meal_type,
            available_time=available_time,
            goal=goal,
            dietary_preferences=dietary_preferences,
            available_ingredients=available_ingredients
        )

        # Try to generate recipe
        response_text = self._call_llm(prompt)

        # Try to parse JSON
        recipe_data = self._parse_recipe_json(response_text)

        if recipe_data:
            logger.info("Recipe generated and parsed successfully")
            return recipe_data

        # If parsing failed, retry with correction prompt
        logger.warning(f"Initial JSON parsing failed. Response was: {response_text[:500]}...")
        correction_prompt = self._build_correction_prompt(response_text)
        corrected_response = self._call_llm(correction_prompt)

        recipe_data = self._parse_recipe_json(corrected_response)

        if recipe_data:
            logger.info("Recipe parsed successfully after correction")
            return recipe_data

        # Both attempts failed
        logger.error(f"Failed to parse recipe after retry. Last response: {corrected_response[:500]}...")
        raise Exception("Could not generate a valid recipe. Please try again.")

    def _build_prompt(
        self,
        meal_type: str,
        available_time: int,
        goal: str,
        dietary_preferences: str,
        available_ingredients: str
    ) -> str:
        """Build the initial prompt for recipe generation"""
        base_prompt = """You are a nutrition expert assistant. Generate a recipe in JSON format with EXACTLY these fields:
- name (string)
- ingredients (string, comma-separated list)
- steps (string, numbered steps separated by periods)
- calories (int)
- protein (float in grams)
- carbs (float in grams)
- fats (float in grams)
- prep_time_minutes (int)
- meal_type (string: breakfast, lunch, dinner, or snack)

User context:"""

        prompt_parts = [base_prompt]

        if goal:
            prompt_parts.append(f"- Goal: {goal}")

        if dietary_preferences:
            prompt_parts.append(f"- Dietary preferences: {dietary_preferences}")

        prompt_parts.append(f"- Meal type: {meal_type}")
        prompt_parts.append(f"- Available time: {available_time} minutes")

        if available_ingredients:
            prompt_parts.append(f"- Available ingredients: {available_ingredients}")

        prompt_parts.append("\nRespond ONLY with the JSON object. No additional text.")

        return "\n".join(prompt_parts)

    def _build_correction_prompt(self, original_response: str) -> str:
        """Build a correction prompt for malformed JSON"""
        return f"""The following text contains a recipe but is not valid JSON. Extract the information and output ONLY a valid JSON object with these fields: name, ingredients, steps, calories, protein, carbs, fats, prep_time_minutes, meal_type.

Text: '{original_response}'

Output only valid JSON, nothing else."""

    def _call_llm(self, prompt: str) -> str:
        """
        Make a call to LLM Studio API.

        Args:
            prompt: The prompt to send

        Returns:
            The response content from LLM

        Raises:
            Exception: If API call fails
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.4
        }

        try:
            logger.info(f"Calling LLM API at {self.url} with model {self.model}")
            logger.debug(f"Prompt: {prompt[:200]}...")  # Log first 200 chars

            response = httpx.post(
                self.url,
                json=payload,
                timeout=600.0  # 10 minutes for local LLM processing
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"LLM API response received successfully")
            logger.debug(f"Response: {str(data)[:200]}...")

            return data['choices'][0]['message']['content']

        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}", exc_info=True)
            raise Exception(f"LLM API call failed: {str(e)}")

    def _parse_recipe_json(self, response_text: str) -> Optional[Dict]:
        """
        Try to parse recipe JSON from response.

        Args:
            response_text: The response text from LLM

        Returns:
            Parsed recipe dictionary or None if parsing fails
        """
        try:
            # Try to parse as JSON
            recipe_data = json.loads(response_text.strip())

            # Validate required fields
            required_fields = [
                'name', 'ingredients', 'steps', 'calories',
                'protein', 'carbs', 'fats', 'prep_time_minutes', 'meal_type'
            ]

            if all(field in recipe_data for field in required_fields):
                return recipe_data

            return None

        except json.JSONDecodeError:
            return None
        except Exception:
            return None
