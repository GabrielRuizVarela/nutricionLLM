"""
Test suite for Profile API with meal distribution fields.

Tests the API endpoints for managing meal distribution:
- GET profile with meal distribution
- POST/PATCH/PUT profile with meal distribution
- Validation and authentication
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from tests.factories import UserFactory, ProfileFactory

User = get_user_model()


@pytest.mark.django_db
class TestProfileMealDistributionAPI:
    """Test suite for Profile API meal distribution functionality"""

    def setup_method(self):
        """Set up test client and authentication before each test"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.profile_url = '/api/profile/'

    def test_get_profile_includes_meal_distribution_fields(self):
        """AC: GET profile should include meals_per_day, meal_distribution, meal_names"""
        profile = ProfileFactory(
            user=self.user,
            meals_per_day=4,
            meal_distribution={"1": 20, "2": 35, "3": 30, "4": 15},
            meal_names={"1": "Breakfast", "2": "Lunch", "3": "Dinner", "4": "Snack"}
        )

        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert 'meals_per_day' in response.data
        assert 'meal_distribution' in response.data
        assert 'meal_names' in response.data
        assert response.data['meals_per_day'] == 4
        assert response.data['meal_distribution'] == {"1": 20, "2": 35, "3": 30, "4": 15}

    def test_get_profile_with_null_meal_distribution(self):
        """AC: Profile without meal distribution should return null fields"""
        profile = ProfileFactory(
            user=self.user,
            meals_per_day=3,
            meal_distribution=None,
            meal_names=None
        )

        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meals_per_day'] == 3
        assert response.data['meal_distribution'] is None
        assert response.data['meal_names'] is None

    def test_create_profile_with_meal_distribution(self):
        """AC: POST should create profile with meal distribution"""
        # Delete existing profile if any
        if hasattr(self.user, 'profile'):
            self.user.profile.delete()

        data = {
            'user': self.user.id,
            'daily_calories': 2000,
            'meals_per_day': 4,
            'meal_distribution': {"1": 25, "2": 35, "3": 25, "4": 15},
            'meal_names': {"1": "Breakfast", "2": "Lunch", "3": "Dinner", "4": "Snack"}
        }

        response = self.client.post(self.profile_url, data, format='json')

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        assert response.data['meals_per_day'] == 4
        assert response.data['meal_distribution']['2'] == 35
        assert response.data['meal_names']['1'] == "Breakfast"

    def test_update_meal_distribution_with_patch(self):
        """AC: PATCH should update only meal distribution fields"""
        profile = ProfileFactory(
            user=self.user,
            daily_calories=2000,
            meals_per_day=3,
            meal_distribution={"1": 33, "2": 34, "3": 33}
        )

        data = {
            'meals_per_day': 4,
            'meal_distribution': {"1": 20, "2": 35, "3": 30, "4": 15},
            'meal_names': {"1": "Breakfast", "2": "Lunch", "3": "Dinner", "4": "Snack"}
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meals_per_day'] == 4
        assert response.data['meal_distribution']['2'] == 35
        assert response.data['daily_calories'] == 2000  # Unchanged

    def test_update_meal_distribution_with_put(self):
        """AC: PUT should update entire profile including meal distribution"""
        profile = ProfileFactory(
            user=self.user,
            daily_calories=2000,
            meals_per_day=3
        )

        data = {
            'daily_calories': 2500,
            'meals_per_day': 4,
            'meal_distribution': {"1": 25, "2": 25, "3": 25, "4": 25},
            'goal': 'maintain'
        }

        response = self.client.put(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meals_per_day'] == 4
        assert response.data['daily_calories'] == 2500

    def test_update_meal_names_independently(self):
        """AC: User should be able to update meal names without changing distribution"""
        profile = ProfileFactory(
            user=self.user,
            meals_per_day=3,
            meal_distribution={"1": 30, "2": 40, "3": 30},
            meal_names=None
        )

        data = {
            'meal_names': {"1": "Breakfast", "2": "Lunch", "3": "Dinner"}
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meal_names']['1'] == "Breakfast"
        assert response.data['meal_distribution'] == {"1": 30, "2": 40, "3": 30}  # Unchanged

    def test_clear_meal_distribution(self):
        """AC: User should be able to clear meal distribution"""
        profile = ProfileFactory(
            user=self.user,
            meals_per_day=4,
            meal_distribution={"1": 25, "2": 25, "3": 25, "4": 25}
        )

        data = {
            'meals_per_day': 3,
            'meal_distribution': None,
            'meal_names': None
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meals_per_day'] == 3
        assert response.data['meal_distribution'] is None

    def test_meal_distribution_persists_after_update(self):
        """AC: Meal distribution should persist after updating other fields"""
        profile = ProfileFactory(
            user=self.user,
            daily_calories=2000,
            meals_per_day=4,
            meal_distribution={"1": 20, "2": 35, "3": 30, "4": 15}
        )

        # Update unrelated field
        data = {'daily_calories': 2500}
        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meal_distribution'] == {"1": 20, "2": 35, "3": 30, "4": 15}
        assert response.data['daily_calories'] == 2500

    def test_unauthorized_access_returns_401(self):
        """AC: Unauthenticated requests should return 401"""
        self.client.credentials()  # Remove authentication

        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_can_only_access_own_profile(self):
        """AC: User should only be able to access their own profile"""
        other_user = UserFactory()
        other_profile = ProfileFactory(
            user=other_user,
            meals_per_day=4,
            meal_distribution={"1": 25, "2": 25, "3": 25, "4": 25}
        )

        # Try to access other user's profile (if endpoint supports ID)
        # This test assumes profile endpoint is user-specific
        response = self.client.get(self.profile_url)

        # Should only see own profile, not other_user's
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == self.user.id


@pytest.mark.django_db
class TestProfileMealDistributionValidationAPI:
    """Test suite for API-level validation of meal distribution"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.profile_url = '/api/profile/'
        self.profile = ProfileFactory(user=self.user)

    def test_meals_per_day_minimum_validation(self):
        """AC: API should reject meals_per_day < 1"""
        data = {'meals_per_day': 0}

        response = self.client.patch(self.profile_url, data, format='json')

        # Should return 400 Bad Request with validation error
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_meals_per_day_maximum_validation(self):
        """AC: API should reject meals_per_day > 6"""
        data = {'meals_per_day': 7}

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_meal_distribution_valid_json_structure(self):
        """AC: meal_distribution should accept valid JSON structure"""
        data = {
            'meal_distribution': {"1": 30, "2": 40, "3": 30}
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meal_distribution'] == {"1": 30, "2": 40, "3": 30}

    def test_meal_distribution_with_string_keys(self):
        """AC: meal_distribution should work with string keys"""
        data = {
            'meal_distribution': {"1": 25, "2": 25, "3": 25, "4": 25}
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_meal_distribution_with_decimal_percentages(self):
        """AC: meal_distribution should accept decimal percentages"""
        data = {
            'meal_distribution': {"1": 33.33, "2": 33.33, "3": 33.34}
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meal_distribution']["1"] == 33.33

    def test_meal_names_with_unicode_characters(self):
        """AC: meal_names should support unicode characters"""
        data = {
            'meal_names': {
                "1": "Desayuno",
                "2": "Almuerzo",
                "3": "Cena"
            }
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meal_names']["1"] == "Desayuno"

    def test_meal_names_with_long_strings(self):
        """AC: meal_names should handle reasonable length strings"""
        data = {
            'meal_names': {
                "1": "Very Long Breakfast Name With Many Words"
            }
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_empty_meal_distribution_allowed(self):
        """AC: Empty meal_distribution dict should be allowed"""
        data = {'meal_distribution': {}}

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meal_distribution'] == {}


@pytest.mark.django_db
class TestProfileMealDistributionPresets:
    """Test suite for meal distribution preset configurations"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.profile_url = '/api/profile/'
        self.profile = ProfileFactory(user=self.user, daily_calories=2000)

    def test_equal_distribution_preset(self):
        """AC: Equal distribution should split evenly across meals"""
        for num_meals in [2, 3, 4, 5, 6]:
            percentage = 100 // num_meals
            remainder = 100 % num_meals

            distribution = {}
            for i in range(1, num_meals + 1):
                # Give remainder to last meal
                distribution[str(i)] = percentage + (remainder if i == num_meals else 0)

            data = {
                'meals_per_day': num_meals,
                'meal_distribution': distribution
            }

            response = self.client.patch(self.profile_url, data, format='json')

            assert response.status_code == status.HTTP_200_OK
            assert response.data['meals_per_day'] == num_meals
            total = sum(response.data['meal_distribution'].values())
            assert total == 100

    def test_traditional_distribution_preset(self):
        """AC: Traditional 3-meal distribution (30/40/30) should work"""
        data = {
            'meals_per_day': 3,
            'meal_distribution': {"1": 30, "2": 40, "3": 30},
            'meal_names': {"1": "Breakfast", "2": "Lunch", "3": "Dinner"}
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meal_distribution'] == {"1": 30, "2": 40, "3": 30}
        assert sum(response.data['meal_distribution'].values()) == 100

    def test_athlete_distribution_preset(self):
        """AC: Athlete 4-meal distribution (25/35/25/15) should work"""
        data = {
            'meals_per_day': 4,
            'meal_distribution': {"1": 25, "2": 35, "3": 25, "4": 15},
            'meal_names': {
                "1": "Breakfast",
                "2": "Lunch",
                "3": "Dinner",
                "4": "Post-Workout Snack"
            }
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meal_distribution'] == {"1": 25, "2": 35, "3": 25, "4": 15}
        assert sum(response.data['meal_distribution'].values()) == 100

    def test_custom_distribution(self):
        """AC: User should be able to create custom distributions"""
        data = {
            'meals_per_day': 5,
            'meal_distribution': {
                "1": 15,  # Small breakfast
                "2": 10,  # Mid-morning snack
                "3": 30,  # Large lunch
                "4": 30,  # Large dinner
                "5": 15   # Evening snack
            }
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert sum(response.data['meal_distribution'].values()) == 100


@pytest.mark.django_db
class TestProfileResponseFormat:
    """Test suite for API response format and structure"""

    def setup_method(self):
        """Set up test client and authentication"""
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.profile_url = '/api/profile/'

    def test_response_includes_all_profile_fields(self):
        """AC: Response should include traditional and new meal fields"""
        profile = ProfileFactory(
            user=self.user,
            daily_calories=2000,
            meals_per_day=4,
            meal_distribution={"1": 20, "2": 35, "3": 30, "4": 15},
            meal_names={"1": "Breakfast", "2": "Lunch"}
        )

        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK

        # Traditional fields
        assert 'daily_calories' in response.data
        assert 'user' in response.data

        # New meal distribution fields
        assert 'meals_per_day' in response.data
        assert 'meal_distribution' in response.data
        assert 'meal_names' in response.data

    def test_response_meal_distribution_is_dict(self):
        """AC: meal_distribution should be returned as dict, not string"""
        profile = ProfileFactory(
            user=self.user,
            meal_distribution={"1": 25, "2": 25, "3": 25, "4": 25}
        )

        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data['meal_distribution'], dict)
        assert response.data['meal_distribution']["1"] == 25

    def test_response_with_null_values(self):
        """AC: Null meal fields should be properly represented"""
        profile = ProfileFactory(
            user=self.user,
            meals_per_day=3,
            meal_distribution=None,
            meal_names=None
        )

        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meal_distribution'] is None
        assert response.data['meal_names'] is None
