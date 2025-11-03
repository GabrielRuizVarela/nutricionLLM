"""
Tests for extended Profile fields.
Tests all personal info, dietary preferences, recipe settings, and nutritional targets.
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import Profile

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestPersonalInformationFields:
    """Test personal information fields (age, weight, height, gender, activity_level)."""

    def test_update_all_personal_info_fields(self, client):
        """Test updating all personal information fields at once."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        data = {
            'age': 28,
            'weight_kg': 68.5,
            'height_cm': 172.0,
            'gender': 'female',
            'activity_level': 'lightly_active'
        }

        response = client.patch('/api/profile/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['age'] == 28
        assert response.data['weight_kg'] == 68.5
        assert response.data['height_cm'] == 172.0
        assert response.data['gender'] == 'female'
        assert response.data['activity_level'] == 'lightly_active'

    def test_activity_level_choices(self, client):
        """Test that only valid activity levels are accepted."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        valid_levels = ['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active']

        for level in valid_levels:
            response = client.patch('/api/profile/', {'activity_level': level})
            assert response.status_code == status.HTTP_200_OK
            assert response.data['activity_level'] == level

    def test_gender_choices(self, client):
        """Test that only valid gender values are accepted."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        valid_genders = ['male', 'female', 'other', 'prefer_not_to_say']

        for gender in valid_genders:
            response = client.patch('/api/profile/', {'gender': gender})
            assert response.status_code == status.HTTP_200_OK
            assert response.data['gender'] == gender

    def test_personal_info_persists(self, client):
        """Test that personal info changes are persisted."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        # Update
        client.patch('/api/profile/', {'age': 35, 'weight_kg': 82.0})

        # Retrieve
        response = client.get('/api/profile/')
        assert response.data['age'] == 35
        assert response.data['weight_kg'] == 82.0


class TestDietaryInformationFields:
    """Test dietary information fields (goal, dietary_preferences, allergies, dislikes)."""

    def test_update_goal_field(self, client):
        """Test updating the goal field."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        valid_goals = ['lose_weight', 'gain_weight', 'maintain_weight', 'gain_muscle', 'improve_health']

        for goal in valid_goals:
            response = client.patch('/api/profile/', {'goal': goal})
            assert response.status_code == status.HTTP_200_OK
            assert response.data['goal'] == goal

    def test_update_dietary_preferences(self, client):
        """Test updating dietary preferences text field."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        preferences = "Vegetarian, low carb, Mediterranean diet"
        response = client.patch('/api/profile/', {'dietary_preferences': preferences})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['dietary_preferences'] == preferences

    def test_update_allergies(self, client):
        """Test updating allergies field."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        allergies = "Peanuts, shellfish, dairy"
        response = client.patch('/api/profile/', {'allergies': allergies})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['allergies'] == allergies

    def test_update_dislikes(self, client):
        """Test updating dislikes field."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        dislikes = "Cilantro, olives, mushrooms"
        response = client.patch('/api/profile/', {'dislikes': dislikes})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['dislikes'] == dislikes

    def test_dietary_fields_can_be_empty(self, client):
        """Test that dietary fields can be left empty."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        response = client.patch('/api/profile/', {
            'dietary_preferences': '',
            'allergies': '',
            'dislikes': ''
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['dietary_preferences'] == ''
        assert response.data['allergies'] == ''
        assert response.data['dislikes'] == ''


class TestRecipePreferenceFields:
    """Test recipe preference fields (cuisine, skill level, spice preference)."""

    def test_update_cuisine_preferences(self, client):
        """Test updating cuisine preferences."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        cuisines = "Italian, Mexican, Thai, Japanese"
        response = client.patch('/api/profile/', {'cuisine_preferences': cuisines})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['cuisine_preferences'] == cuisines

    def test_update_cooking_skill_level(self, client):
        """Test updating cooking skill level."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        valid_skills = ['beginner', 'intermediate', 'advanced']

        for skill in valid_skills:
            response = client.patch('/api/profile/', {'cooking_skill_level': skill})
            assert response.status_code == status.HTTP_200_OK
            assert response.data['cooking_skill_level'] == skill

    def test_update_spice_preference(self, client):
        """Test updating spice preference."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        valid_spice = ['mild', 'medium', 'spicy']

        for spice in valid_spice:
            response = client.patch('/api/profile/', {'spice_preference': spice})
            assert response.status_code == status.HTTP_200_OK
            assert response.data['spice_preference'] == spice


class TestIngredientManagementFields:
    """Test ingredient management fields (preferred, available ingredients)."""

    def test_update_preferred_ingredients(self, client):
        """Test updating preferred ingredients."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        ingredients = "Chicken, salmon, quinoa, broccoli"
        response = client.patch('/api/profile/', {'preferred_ingredients': ingredients})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['preferred_ingredients'] == ingredients

    def test_update_available_ingredients(self, client):
        """Test updating available ingredients."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        ingredients = "Onions, garlic, tomatoes, olive oil, rice"
        response = client.patch('/api/profile/', {'available_ingredients': ingredients})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['available_ingredients'] == ingredients

    def test_ingredient_fields_can_be_empty(self, client):
        """Test that ingredient fields can be empty."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        response = client.patch('/api/profile/', {
            'preferred_ingredients': '',
            'available_ingredients': ''
        })

        assert response.status_code == status.HTTP_200_OK


class TestNutritionalTargetFields:
    """Test nutritional target fields (calories, protein, carbs, fats)."""

    def test_update_all_nutritional_targets(self, client):
        """Test updating all nutritional target fields."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        targets = {
            'daily_calorie_target': 2200,
            'daily_protein_target': 165,
            'daily_carbs_target': 220,
            'daily_fats_target': 75
        }

        response = client.patch('/api/profile/', targets)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['daily_calorie_target'] == 2200
        assert response.data['daily_protein_target'] == 165
        assert response.data['daily_carbs_target'] == 220
        assert response.data['daily_fats_target'] == 75

    def test_update_individual_target_fields(self, client):
        """Test updating nutritional targets individually."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

        # Update calories only
        response = client.patch('/api/profile/', {'daily_calorie_target': 1800})
        assert response.data['daily_calorie_target'] == 1800

        # Update protein only
        response = client.patch('/api/profile/', {'daily_protein_target': 120})
        assert response.data['daily_protein_target'] == 120

        # Update carbs only
        response = client.patch('/api/profile/', {'daily_carbs_target': 150})
        assert response.data['daily_carbs_target'] == 150

        # Update fats only
        response = client.patch('/api/profile/', {'daily_fats_target': 50})
        assert response.data['daily_fats_target'] == 50

    def test_nutritional_targets_can_be_null(self, client):
        """Test that nutritional targets can be null (not set)."""
        user = User.objects.create_user(username='test', email='test@test.com', password='test123')
        client.force_authenticate(user=user)

<<<<<<< HEAD
        # First set some values
        response = client.patch('/api/profile/', {
            'daily_calorie_target': 2000,
            'daily_protein_target': 150
        })
        assert response.status_code == status.HTTP_200_OK

        # Now clear them by setting to empty string (which converts to null)
        response = client.patch('/api/profile/', {
            'daily_calorie_target': '',
            'daily_protein_target': ''
        })

        assert response.status_code == status.HTTP_200_OK
        # Verify they were cleared (null in DB)
        user.profile.refresh_from_db()
        assert user.profile.daily_calorie_target is None
        assert user.profile.daily_protein_target is None
=======
        response = client.get('/api/profile/')

        # Default targets might be null
        # Setting them to null should work
        response = client.patch('/api/profile/', {
            'daily_calorie_target': None,
            'daily_protein_target': None
        })

        assert response.status_code == status.HTTP_200_OK
>>>>>>> 146c2b18 (feat: general functionalities changes)


class TestCompleteProfileUpdate:
    """Test updating multiple field categories at once."""

    def test_update_complete_profile(self, client):
        """Test updating all profile fields in a single request."""
        user = User.objects.create_user(username='complete', email='complete@test.com', password='test123')
        client.force_authenticate(user=user)

        complete_data = {
            # Personal info
            'age': 32,
            'weight_kg': 78.5,
            'height_cm': 178.0,
            'gender': 'male',
            'activity_level': 'moderately_active',

            # Dietary info
            'goal': 'gain_muscle',
            'dietary_preferences': 'High protein, whole foods',
            'allergies': 'None',
            'dislikes': 'Liver',

            # Recipe preferences
            'cuisine_preferences': 'Mediterranean, Asian',
            'cooking_skill_level': 'intermediate',
            'spice_preference': 'medium',

            # Ingredients
            'preferred_ingredients': 'Chicken, fish, vegetables',
            'available_ingredients': 'Pantry staples, fresh produce',

            # Nutritional targets
            'daily_calorie_target': 2500,
            'daily_protein_target': 180,
            'daily_carbs_target': 250,
            'daily_fats_target': 80
        }

        response = client.patch('/api/profile/', complete_data)

        assert response.status_code == status.HTTP_200_OK

        # Verify all fields were updated
        for key, value in complete_data.items():
            assert response.data[key] == value

        # Verify BMR and TDEE were calculated
        assert response.data['bmr'] is not None
        assert response.data['tdee'] is not None

    def test_partial_profile_update_preserves_other_fields(self, client):
        """Test that updating some fields doesn't clear others."""
        user = User.objects.create_user(username='partial', email='partial@test.com', password='test123')
        client.force_authenticate(user=user)

        # Set initial data
        initial_data = {
            'age': 30,
            'weight_kg': 75.0,
            'dietary_preferences': 'Vegetarian'
        }
        client.patch('/api/profile/', initial_data)

        # Update only one field
        client.patch('/api/profile/', {'goal': 'lose_weight'})

        # Retrieve and verify all fields still present
        response = client.get('/api/profile/')
        assert response.data['age'] == 30
        assert response.data['weight_kg'] == 75.0
        assert response.data['dietary_preferences'] == 'Vegetarian'
        assert response.data['goal'] == 'lose_weight'


@pytest.fixture
def client():
    """Provide an API client."""
    return APIClient()
