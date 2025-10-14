"""
LLM Service for recipe generation using LLM Studio.
"""
import json
import httpx
from django.conf import settings
from typing import Dict, Optional


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
            return recipe_data

        # If parsing failed, retry with correction prompt
        correction_prompt = self._build_correction_prompt(response_text)
        corrected_response = self._call_llm(correction_prompt)

        recipe_data = self._parse_recipe_json(corrected_response)

        if recipe_data:
            return recipe_data

        # Both attempts failed
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
        base_prompt = """Eres un asistente nutricional experto. Genera una receta en formato JSON con EXACTAMENTE estos campos:
- nombre (string)
- ingredientes (string, lista separada por comas)
- pasos (string, pasos numerados separados por puntos)
- calorias (int)
- proteinas (float)
- carbohidratos (float)
- grasas (float)
- tiempo_min (int)
- tipo (string: desayuno, almuerzo, cena o snack)

Contexo del usuario:"""

        prompt_parts = [base_prompt]

        if goal:
            prompt_parts.append(f"- Objetivo: {goal}")

        if dietary_preferences:
            prompt_parts.append(f"- Preferencias: {dietary_preferences}")

        prompt_parts.append(f"- Tipo de comida: {meal_type}")
        prompt_parts.append(f"- Tiempo disponible: {available_time} minutos")

        if available_ingredients:
            prompt_parts.append(f"- Ingredientes disponibles: {available_ingredients}")

        prompt_parts.append("\nResponde SOLO con el objeto JSON. Nada de texto adicional.")

        return "\n".join(prompt_parts)

    def _build_correction_prompt(self, original_response: str) -> str:
        """Build a correction prompt for malformed JSON"""
        return f"""The following text contains a recipe but is not valid JSON. Extract the information and output ONLY a valid JSON object with these fields: nombre, ingredientes, pasos, calorias, proteinas, carbohidratos, grasas, tiempo_min, tipo.

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
            response = httpx.post(
                self.url,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()

            data = response.json()
            return data['choices'][0]['message']['content']

        except Exception as e:
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
                'nombre', 'ingredientes', 'pasos', 'calorias',
                'proteinas', 'carbohidratos', 'grasas', 'tiempo_min', 'tipo'
            ]

            if all(field in recipe_data for field in required_fields):
                return recipe_data

            return None

        except json.JSONDecodeError:
            return None
        except Exception:
            return None
