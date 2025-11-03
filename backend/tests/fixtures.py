"""
Common test fixtures and mock data for backend tests.
"""

import json
import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from tests.factories import UserFactory, ProfileFactory

User = get_user_model()


# Sample recipe data
SAMPLE_RECIPE_DATA = {
    'name': 'Grilled Chicken Salad',
    'ingredients': 'Chicken breast\nMixed greens\nCherry tomatoes\nOlive oil',
    'steps': '1. Grill chicken\n2. Prepare salad\n3. Combine and serve',
    'calories': 400,
    'protein': 35.0,
    'carbs': 20.0,
    'fats': 18.0,
    'prep_time_minutes': 25,
    'meal_type': 'lunch'
}


# Sample LLM responses
SAMPLE_LLM_RECIPE_RESPONSE = {
    'name': 'Mediterranean Chicken Bowl',
    'ingredients': '300g chicken breast\n1 cup quinoa\n1 cucumber\n1 cup cherry tomatoes\n1/4 cup feta cheese\n2 tbsp olive oil\nLemon juice',
    'steps': '1. Cook quinoa according to package instructions\n2. Season and grill chicken breast\n3. Dice cucumber and halve tomatoes\n4. Combine all ingredients in a bowl\n5. Drizzle with olive oil and lemon juice\n6. Top with crumbled feta',
    'calories': 520,
    'protein': 42.0,
    'carbs': 45.0,
    'fats': 18.0,
    'prep_time_minutes': 30,
    'meal_type': 'lunch'
}


# Malformed LLM response (for testing retry logic)
MALFORMED_LLM_RESPONSE = '{"name": "Incomplete Recipe", "ingredients": "Some ingredients"'


# Sample USDA food data
SAMPLE_USDA_FOOD_DATA = {
    'fdc_id': 123456,
    'description': 'Chicken Breast, Grilled',
    'brand_owner': 'Generic',
    'barcode': '',
    'ingredients': 'Chicken',
    'category': 'Poultry',
    'serving_size': 100.0,
    'serving_size_unit': 'g',
    'calories': 165,
    'protein': 31.0,
    'carbs': 0.0,
    'fats': 3.6,
    'fiber': 0.0,
    'sugars': 0.0,
    'sodium': 74.0
}


# Sample USDA JSON import data structure
SAMPLE_USDA_IMPORT_DATA = {
    'BrandedFoods': [
        {
            'fdcId': 789012,
            'description': 'PREMIUM PROTEIN BAR',
            'brandOwner': 'Test Nutrition Co.',
            'gtinUpc': '012345678901',
            'ingredients': 'PROTEIN BLEND, NUTS, CHOCOLATE',
            'brandedFoodCategory': 'Snacks',
            'servingSize': 60.0,
            'servingSizeUnit': 'g',
            'foodNutrients': [
                {'nutrient': {'name': 'Energy', 'unitName': 'KCAL'}, 'amount': 220},
                {'nutrient': {'name': 'Protein', 'unitName': 'G'}, 'amount': 20},
                {'nutrient': {'name': 'Carbohydrate, by difference', 'unitName': 'G'}, 'amount': 22},
                {'nutrient': {'name': 'Total lipid (fat)', 'unitName': 'G'}, 'amount': 8},
                {'nutrient': {'name': 'Fiber, total dietary', 'unitName': 'G'}, 'amount': 3},
                {'nutrient': {'name': 'Sugars, total including NLEA', 'unitName': 'G'}, 'amount': 2},
                {'nutrient': {'name': 'Sodium, Na', 'unitName': 'MG'}, 'amount': 180}
            ]
        },
        {
            'fdcId': 789013,
            'description': 'GREEK YOGURT, PLAIN',
            'brandOwner': 'Dairy Farms Inc.',
            'gtinUpc': '098765432109',
            'ingredients': 'CULTURED MILK',
            'brandedFoodCategory': 'Dairy',
            'servingSize': 150.0,
            'servingSizeUnit': 'g',
            'foodNutrients': [
                {'nutrient': {'name': 'Energy', 'unitName': 'KCAL'}, 'amount': 100},
                {'nutrient': {'name': 'Protein', 'unitName': 'G'}, 'amount': 17},
                {'nutrient': {'name': 'Carbohydrate, by difference', 'unitName': 'G'}, 'amount': 6},
                {'nutrient': {'name': 'Total lipid (fat)', 'unitName': 'G'}, 'amount': 0.7},
                {'nutrient': {'name': 'Sugars, total including NLEA', 'unitName': 'G'}, 'amount': 5},
                {'nutrient': {'name': 'Sodium, Na', 'unitName': 'MG'}, 'amount': 50}
            ]
        }
    ]
}


# Pytest fixtures

@pytest.fixture
def api_client():
    """Return an API client for making requests."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user."""
    return UserFactory()


@pytest.fixture
def profile(user):
    """Create a test profile for user."""
    return ProfileFactory(user=user)


@pytest.fixture
def authenticated_client(user):
    """Return an authenticated API client."""
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def authenticated_client_with_profile(user, profile):
    """Return an authenticated API client with a complete profile."""
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def second_user():
    """Create a second test user for isolation tests."""
    return UserFactory(username='testuser2', email='testuser2@example.com')


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for recipe generation."""
    return {
        'choices': [
            {
                'message': {
                    'content': json.dumps(SAMPLE_LLM_RECIPE_RESPONSE)
                }
            }
        ]
    }


@pytest.fixture
def mock_openai_malformed_response():
    """Mock malformed OpenAI API response."""
    return {
        'choices': [
            {
                'message': {
                    'content': MALFORMED_LLM_RESPONSE
                }
            }
        ]
    }


@pytest.fixture
def this_monday():
    """Return this week's Monday date."""
    today = date.today()
    return today - timedelta(days=today.weekday())


@pytest.fixture
def next_monday():
    """Return next week's Monday date."""
    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    return this_monday + timedelta(days=7)


@pytest.fixture
def meal_type_choices():
    """Return valid meal type choices."""
    return ['breakfast', 'lunch', 'dinner', 'snack']


@pytest.fixture
def activity_level_choices():
    """Return valid activity level choices."""
    return ['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active']


@pytest.fixture
def goal_choices():
    """Return valid goal choices."""
    return ['lose_weight', 'gain_weight', 'maintain_weight', 'gain_muscle', 'improve_health']


# Helper functions

def create_complete_profile(user):
    """
    Create a complete profile with all fields populated.
    Useful for testing calculations and full profile scenarios.
    """
    return ProfileFactory(
        user=user,
        age=30,
        weight_kg=75.0,
        height_cm=180.0,
        gender='male',
        activity_level='moderately_active',
        goal='maintain_weight',
        dietary_preferences='Mediterranean diet',
        allergies='None',
        dislikes='Cilantro',
        cuisine_preferences='Italian, Mexican, Thai',
        cooking_skill_level='intermediate',
        spice_preference='medium',
        preferred_ingredients='Chicken, Rice, Vegetables',
        available_ingredients='Onions, Garlic, Tomatoes',
        daily_calorie_target=2200,
        daily_protein_target=165,
        daily_carbs_target=220,
        daily_fats_target=75
    )


def get_auth_token(user):
    """Get or create an auth token for a user."""
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


def make_authenticated_request(client, user, method, url, data=None):
    """
    Make an authenticated request with proper headers.

    Args:
        client: APIClient instance
        user: User instance
        method: HTTP method ('get', 'post', 'patch', 'delete')
        url: URL to request
        data: Optional request data

    Returns:
        Response object
    """
    token = get_auth_token(user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    method_func = getattr(client, method.lower())
    if data:
        return method_func(url, data, format='json')
    return method_func(url)
