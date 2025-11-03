"""
Tests for Food Search API endpoint.
Tests USDA food database search functionality.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import UserFactory, FoodFactory

pytestmark = pytest.mark.django_db


class TestFoodSearchAPI:
    """Test GET /api/foods/search/?q=query - Search foods"""

    def test_search_foods_by_description(self):
        """Test searching foods by description."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create test foods
        FoodFactory(description="Organic Whole Milk")
        FoodFactory(description="Almond Milk")
        FoodFactory(description="Coconut Milk")
        FoodFactory(description="Orange Juice")

        url = reverse('food-search')
        response = client.get(url, {'q': 'Milk'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # Three foods with "Milk"
        descriptions = [food['description'] for food in response.data]
        assert all('Milk' in desc for desc in descriptions)

    def test_search_foods_by_brand(self):
        """Test searching foods by brand owner."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        FoodFactory(description="Greek Yogurt", brand_owner="Chobani")
        FoodFactory(description="Vanilla Yogurt", brand_owner="Chobani")
        FoodFactory(description="Plain Yogurt", brand_owner="Dannon")

        url = reverse('food-search')
        response = client.get(url, {'q': 'Chobani'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert all(food['brand_owner'] == 'Chobani' for food in response.data)

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        FoodFactory(description="Chicken Breast")

        url = reverse('food-search')

        # Try different cases
        response1 = client.get(url, {'q': 'chicken'})
        response2 = client.get(url, {'q': 'CHICKEN'})
        response3 = client.get(url, {'q': 'ChIcKeN'})

        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response3.status_code == status.HTTP_200_OK
        assert len(response1.data) == 1
        assert len(response2.data) == 1
        assert len(response3.data) == 1

    def test_search_partial_match(self):
        """Test that search matches partial strings."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        FoodFactory(description="Strawberry Yogurt")

        url = reverse('food-search')
        response = client.get(url, {'q': 'berry'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert 'Strawberry' in response.data[0]['description']

    def test_search_limits_to_20_results(self):
        """Test that search returns maximum 20 results."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create 30 foods with "Protein" in description
        for i in range(30):
            FoodFactory(description=f"Protein Bar {i}")

        url = reverse('food-search')
        response = client.get(url, {'q': 'Protein'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 20  # Limited to 20

    def test_search_results_ordered_alphabetically(self):
        """Test that search results are ordered by description."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        FoodFactory(description="Zucchini Bread")
        FoodFactory(description="Apple Bread")
        FoodFactory(description="Banana Bread")

        url = reverse('food-search')
        response = client.get(url, {'q': 'Bread'})

        assert response.status_code == status.HTTP_200_OK
        descriptions = [food['description'] for food in response.data]
        assert descriptions == sorted(descriptions)

    def test_search_query_too_short_fails(self):
        """Test that query must be at least 2 characters."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('food-search')
        response = client.get(url, {'q': 'a'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_search_empty_query_fails(self):
        """Test that empty query returns error."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('food-search')
        response = client.get(url, {'q': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_missing_query_param_fails(self):
        """Test that missing query parameter returns error."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('food-search')
        response = client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_no_results(self):
        """Test search with no matching results."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        FoodFactory(description="Apple")

        url = reverse('food-search')
        response = client.get(url, {'q': 'xyz123notfound'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_search_unauthenticated_fails(self):
        """Test that unauthenticated users cannot search foods."""
        client = APIClient()

        url = reverse('food-search')
        response = client.get(url, {'q': 'milk'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_search_returns_nutritional_info(self):
        """Test that search results include nutritional information."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        FoodFactory(
            description="Test Food",
            calories=200,
            protein=10.0,
            carbs=25.0,
            fats=8.0,
            serving_size=100.0,
            serving_size_unit="g"
        )

        url = reverse('food-search')
        response = client.get(url, {'q': 'Test'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        food = response.data[0]
        assert food['calories'] == 200
        assert food['protein'] == 10.0
        assert food['carbs'] == 25.0
        assert food['fats'] == 8.0
        assert food['serving_size'] == 100.0
        assert food['serving_size_unit'] == "g"

    def test_search_whitespace_trimmed(self):
        """Test that whitespace is trimmed from query."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        FoodFactory(description="Milk")

        url = reverse('food-search')
        response = client.get(url, {'q': '  Milk  '})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
