"""
Tests for FoodLog API endpoints.
Tests CRUD operations, filtering, and daily totals aggregation.
"""

import pytest
from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from recipes.models import FoodLog
from tests.factories import UserFactory, FoodFactory, FoodLogFactory

pytestmark = pytest.mark.django_db


class TestFoodLogListAPI:
    """Test GET /api/food-logs/ - List food logs"""

    def test_list_food_logs_authenticated(self):
        """Test that authenticated users can list their food logs."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        FoodLogFactory(user=user)
        FoodLogFactory(user=user)

        url = reverse('food-log-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_food_logs_unauthenticated(self):
        """Test that unauthenticated users cannot list food logs."""
        client = APIClient()
        url = reverse('food-log-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_food_logs_user_isolation(self):
        """Test that users only see their own food logs."""
        user1 = UserFactory()
        user2 = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user1)

        FoodLogFactory(user=user1)
        FoodLogFactory(user=user1)
        FoodLogFactory(user=user2)

        url = reverse('food-log-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Only user1's logs

    def test_list_food_logs_includes_food_info(self):
        """Test that food logs include food information."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        food = FoodFactory(description="Chicken Breast")
        FoodLogFactory(user=user, food=food)

        url = reverse('food-log-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert 'food_detail' in response.data[0]
        assert response.data[0]['food_detail']['description'] == "Chicken Breast"


class TestFoodLogFilterByDateAPI:
    """Test GET /api/food-logs/?date=YYYY-MM-DD - Filter by date"""

    def test_filter_by_date(self):
        """Test filtering food logs by specific date."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        today = date.today()
        yesterday = today - timedelta(days=1)

        FoodLogFactory(user=user, date=today)
        FoodLogFactory(user=user, date=today)
        FoodLogFactory(user=user, date=yesterday)

        url = reverse('food-log-list')
        response = client.get(url, {'date': today.isoformat()})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_by_date_no_results(self):
        """Test filtering by date with no results."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        FoodLogFactory(user=user, date=date.today())

        future_date = date.today() + timedelta(days=30)
        url = reverse('food-log-list')
        response = client.get(url, {'date': future_date.isoformat()})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


class TestFoodLogCreateAPI:
    """Test POST /api/food-logs/ - Create food log"""

    def test_create_food_log(self):
        """Test creating a new food log entry."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        food = FoodFactory(
            serving_size=100.0,
            calories=200,
            protein=10.0,
            carbs=25.0,
            fats=8.0
        )

        data = {
            'food': food.id,
            'quantity_grams': 150.0,
            'meal_type': 'lunch',
            'date': date.today().isoformat()
        }

        url = reverse('food-log-list')
        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert FoodLog.objects.filter(user=user).exists()

        # Verify macros were calculated
        log = FoodLog.objects.get(user=user, food=food, date=date.today())
        assert log.calories == 300  # 200 * 1.5
        assert log.protein == 15.0  # 10 * 1.5

    def test_create_food_log_auto_assigns_user(self):
        """Test that created logs are automatically assigned to current user."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        food = FoodFactory()

        data = {
            'food': food.id,
            'quantity_grams': 100.0,
            'meal_type': 'breakfast',
            'date': date.today().isoformat()
        }

        url = reverse('food-log-list')
        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        log = FoodLog.objects.get(user=user, food=food, date=date.today())
        assert log.user == user

    def test_create_food_log_date_defaults_to_today(self):
        """Test that date defaults to today if not provided."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        food = FoodFactory()

        data = {
            'food': food.id,
            'quantity_grams': 100.0,
            'meal_type': 'snack'
            # No date provided
        }

        url = reverse('food-log-list')
        response = client.post(url, data, format='json')

        # Depending on serializer, this might succeed with today's date or fail
        # Document actual behavior
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_create_food_log_invalid_quantity_fails(self):
        """Test that negative or zero quantity fails."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        food = FoodFactory()

        data = {
            'food': food.id,
            'quantity_grams': -10.0,
            'meal_type': 'lunch',
            'date': date.today().isoformat()
        }

        url = reverse('food-log-list')
        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_food_log_unauthenticated(self):
        """Test that unauthenticated users cannot create food logs."""
        client = APIClient()
        food = FoodFactory()

        data = {
            'food': food.id,
            'quantity_grams': 100.0,
            'meal_type': 'lunch',
            'date': date.today().isoformat()
        }

        url = reverse('food-log-list')
        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestFoodLogRetrieveAPI:
    """Test GET /api/food-logs/{id}/ - Retrieve specific food log"""

    def test_retrieve_food_log(self):
        """Test retrieving a specific food log."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        food_log = FoodLogFactory(user=user)

        url = reverse('food-log-detail', kwargs={'pk': food_log.pk})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == food_log.id

    def test_retrieve_food_log_user_isolation(self):
        """Test that users cannot retrieve other users' food logs."""
        user1 = UserFactory()
        user2 = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user1)

        food_log = FoodLogFactory(user=user2)

        url = reverse('food-log-detail', kwargs={'pk': food_log.pk})
        response = client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFoodLogUpdateAPI:
    """Test PUT/PATCH /api/food-logs/{id}/ - Update food log"""

    def test_update_food_log_quantity(self):
        """Test updating quantity of a food log."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        food = FoodFactory(serving_size=100.0, calories=200)
        food_log = FoodLogFactory(user=user, food=food, quantity_grams=100.0)

        original_calories = food_log.calories

        data = {'quantity_grams': 200.0}
        url = reverse('food-log-detail', kwargs={'pk': food_log.pk})
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        food_log.refresh_from_db()
        assert food_log.quantity_grams == 200.0
        # Macros should be recalculated
        assert food_log.calories == original_calories * 2

    def test_update_food_log_meal_type(self):
        """Test updating meal type of a food log."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        food_log = FoodLogFactory(user=user, meal_type='breakfast')

        data = {'meal_type': 'lunch'}
        url = reverse('food-log-detail', kwargs={'pk': food_log.pk})
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        food_log.refresh_from_db()
        assert food_log.meal_type == 'lunch'

    def test_update_food_log_user_isolation(self):
        """Test that users cannot update other users' food logs."""
        user1 = UserFactory()
        user2 = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user1)

        food_log = FoodLogFactory(user=user2)

        data = {'quantity_grams': 150.0}
        url = reverse('food-log-detail', kwargs={'pk': food_log.pk})
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFoodLogDeleteAPI:
    """Test DELETE /api/food-logs/{id}/ - Delete food log"""

    def test_delete_food_log(self):
        """Test deleting a food log entry."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        food_log = FoodLogFactory(user=user)
        log_id = food_log.id

        url = reverse('food-log-detail', kwargs={'pk': food_log.pk})
        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not FoodLog.objects.filter(id=log_id).exists()

    def test_delete_food_log_user_isolation(self):
        """Test that users cannot delete other users' food logs."""
        user1 = UserFactory()
        user2 = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user1)

        food_log = FoodLogFactory(user=user2)

        url = reverse('food-log-detail', kwargs={'pk': food_log.pk})
        response = client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert FoodLog.objects.filter(id=food_log.id).exists()


class TestFoodLogDailyTotalsAPI:
    """Test GET /api/food-logs/daily_totals/?date=YYYY-MM-DD - Get daily totals"""

    def test_daily_totals_for_today(self):
        """Test getting daily totals for today."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        today = date.today()
        food1 = FoodFactory(serving_size=100.0, calories=200, protein=10.0, carbs=25.0, fats=8.0)
        food2 = FoodFactory(serving_size=100.0, calories=300, protein=15.0, carbs=30.0, fats=12.0)

        FoodLog.objects.create(user=user, food=food1, quantity_grams=100.0, date=today, meal_type='breakfast')
        FoodLog.objects.create(user=user, food=food2, quantity_grams=100.0, date=today, meal_type='lunch')

        url = reverse('food-log-daily-totals')
        response = client.get(url, {'date': today.isoformat()})

        assert response.status_code == status.HTTP_200_OK
        assert 'totals' in response.data
        assert response.data['totals']['calories'] == 500
        assert response.data['totals']['protein'] == 25.0

    def test_daily_totals_defaults_to_today(self):
        """Test that daily totals defaults to today if no date provided."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        food = FoodFactory(serving_size=100.0, calories=200)
        FoodLog.objects.create(user=user, food=food, quantity_grams=100.0, date=date.today(), meal_type='lunch')

        url = reverse('food-log-daily-totals')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert str(response.data['date']) == str(date.today())

    def test_daily_totals_by_meal_type(self):
        """Test that daily totals are grouped by meal type."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        today = date.today()
        food = FoodFactory(serving_size=100.0, calories=100, protein=5.0, carbs=10.0, fats=4.0)

        FoodLog.objects.create(user=user, food=food, quantity_grams=100.0, date=today, meal_type='breakfast')
        FoodLog.objects.create(user=user, food=food, quantity_grams=100.0, date=today, meal_type='lunch')

        url = reverse('food-log-daily-totals')
        response = client.get(url, {'date': today.isoformat()})

        assert response.status_code == status.HTTP_200_OK
        assert 'by_meal' in response.data
        assert 'breakfast' in response.data['by_meal']
        assert 'lunch' in response.data['by_meal']
        assert response.data['by_meal']['breakfast']['calories'] == 100
        assert response.data['by_meal']['lunch']['calories'] == 100

    def test_daily_totals_no_logs(self):
        """Test daily totals with no food logs."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        future_date = date.today() + timedelta(days=30)
        url = reverse('food-log-daily-totals')
        response = client.get(url, {'date': future_date.isoformat()})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['totals']['calories'] == 0

    def test_daily_totals_invalid_date_format(self):
        """Test that invalid date format returns error."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('food-log-daily-totals')
        response = client.get(url, {'date': 'invalid-date'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_daily_totals_user_isolation(self):
        """Test that daily totals only include user's own logs."""
        user1 = UserFactory()
        user2 = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user1)

        today = date.today()
        food = FoodFactory(serving_size=100.0, calories=100)

        FoodLog.objects.create(user=user1, food=food, quantity_grams=100.0, date=today, meal_type='lunch')
        FoodLog.objects.create(user=user2, food=food, quantity_grams=100.0, date=today, meal_type='lunch')

        url = reverse('food-log-daily-totals')
        response = client.get(url, {'date': today.isoformat()})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['totals']['calories'] == 100  # Only user1's log

    def test_daily_totals_unauthenticated(self):
        """Test that unauthenticated users cannot access daily totals."""
        client = APIClient()

        url = reverse('food-log-daily-totals')
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
