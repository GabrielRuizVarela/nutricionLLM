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
        available_ingredients: str = "",
        # New profile fields
        allergies: str = "",
        dislikes: str = "",
        cuisine_preferences: str = "",
        cooking_skill_level: str = "",
        spice_preference: str = "",
        daily_calorie_target: Optional[int] = None,
        daily_protein_target: Optional[int] = None,
        daily_carbs_target: Optional[int] = None,
        daily_fats_target: Optional[int] = None,
        # Ingredient management
        preferred_ingredients: str = "",
    ) -> Dict:
        """
        Generate a recipe using LLM Studio with comprehensive user profile data.

        Args:
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            available_time: Available time in minutes
            goal: User's nutritional goal
            dietary_preferences: User's dietary preferences
            available_ingredients: Ingredients currently in pantry
            allergies: Food allergies to avoid
            dislikes: Disliked ingredients to avoid
            cuisine_preferences: Preferred cuisines
            cooking_skill_level: User's cooking skill (beginner, intermediate, advanced)
            spice_preference: Spice level preference (mild, medium, spicy)
            daily_calorie_target: Target calories per meal
            daily_protein_target: Target protein per meal
            daily_carbs_target: Target carbs per meal
            daily_fats_target: Target fats per meal
            preferred_ingredients: Ingredients user likes to use regularly

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
            available_ingredients=available_ingredients,
            allergies=allergies,
            dislikes=dislikes,
            cuisine_preferences=cuisine_preferences,
            cooking_skill_level=cooking_skill_level,
            spice_preference=spice_preference,
            daily_calorie_target=daily_calorie_target,
            daily_protein_target=daily_protein_target,
            daily_carbs_target=daily_carbs_target,
            daily_fats_target=daily_fats_target,
            preferred_ingredients=preferred_ingredients
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
        available_ingredients: str,
        allergies: str = "",
        dislikes: str = "",
        cuisine_preferences: str = "",
        cooking_skill_level: str = "",
        spice_preference: str = "",
        daily_calorie_target: Optional[int] = None,
        daily_protein_target: Optional[int] = None,
        daily_carbs_target: Optional[int] = None,
        daily_fats_target: Optional[int] = None,
        preferred_ingredients: str = ""
    ) -> str:
        """Build the initial prompt for recipe generation with comprehensive profile data"""
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

User context and requirements:"""

        prompt_parts = [base_prompt]

        # Primary meal requirements
        prompt_parts.append(f"- Meal type: {meal_type}")
        prompt_parts.append(f"- Available time: {available_time} minutes")

        # Safety: Allergies (CRITICAL - must avoid)
        if allergies:
            prompt_parts.append(f"- ⚠️  ALLERGIES (MUST AVOID): {allergies}")

        # User preferences
        if goal:
            prompt_parts.append(f"- Goal: {goal}")

        if dietary_preferences:
            prompt_parts.append(f"- Dietary preferences: {dietary_preferences}")

        if dislikes:
            prompt_parts.append(f"- Dislikes (avoid if possible): {dislikes}")

        # Recipe style preferences
        if cuisine_preferences:
            prompt_parts.append(f"- Preferred cuisines: {cuisine_preferences}")

        if cooking_skill_level:
            skill_hints = {
                'beginner': 'simple techniques, minimal steps, common ingredients',
                'intermediate': 'moderate complexity, some specialized techniques allowed',
                'advanced': 'complex techniques welcome, gourmet ingredients acceptable'
            }
            hint = skill_hints.get(cooking_skill_level, '')
            prompt_parts.append(f"- Cooking skill level: {cooking_skill_level} ({hint})")

        if spice_preference:
            prompt_parts.append(f"- Spice preference: {spice_preference}")

        # Nutritional targets
        if daily_calorie_target:
            # Assume 3 meals per day, so divide by 3 for per-meal target
            target_per_meal = daily_calorie_target // 3
            prompt_parts.append(f"- Target calories for this meal: approximately {target_per_meal} kcal")

        if daily_protein_target:
            target_per_meal = daily_protein_target // 3
            prompt_parts.append(f"- Target protein for this meal: approximately {target_per_meal}g")

        if daily_carbs_target:
            target_per_meal = daily_carbs_target // 3
            prompt_parts.append(f"- Target carbs for this meal: approximately {target_per_meal}g")

        if daily_fats_target:
            target_per_meal = daily_fats_target // 3
            prompt_parts.append(f"- Target fats for this meal: approximately {target_per_meal}g")

        # Ingredient preferences and availability
        if preferred_ingredients:
            prompt_parts.append(f"- Preferred ingredients (use these when possible): {preferred_ingredients}")

        if available_ingredients:
            prompt_parts.append(f"- Available ingredients (prioritize these): {available_ingredients}")

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
