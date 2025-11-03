"""
Tests for FoodLog model.
Tests food logging, automatic macro calculations, and daily tracking.
"""

import pytest
from datetime import date, timedelta
from recipes.models import FoodLog
from tests.factories import UserFactory, FoodFactory, FoodLogFactory

pytestmark = pytest.mark.django_db


class TestFoodLogCreation:
    """Test FoodLog model creation and basic functionality."""

    def test_create_food_log(self):
        """Test creating a basic food log entry."""
        user = UserFactory()
        food = FoodFactory(
            serving_size=100.0,
            calories=200,
            protein=10.0,
            carbs=25.0,
            fats=8.0
        )

        food_log = FoodLog.objects.create(
            user=user,
            food=food,
            date=date.today(),
            meal_type='breakfast',
            quantity_grams=100.0
        )

        assert food_log.id is not None
        assert food_log.user == user
        assert food_log.food == food
        assert food_log.quantity_grams == 100.0
        assert food_log.meal_type == 'breakfast'

    def test_food_log_string_representation(self):
        """Test the string representation of a food log."""
        user = UserFactory(username='testuser')
        food = FoodFactory(description='Chicken Breast')
        log_date = date(2024, 1, 15)

        food_log = FoodLogFactory(
            user=user,
            food=food,
            date=log_date
        )

        expected_str = "testuser - Chicken Breast on 2024-01-15"
        assert str(food_log) == expected_str


class TestFoodLogMacroCalculations:
    """Test automatic macro calculations based on quantity."""

    def test_macros_calculated_for_exact_serving_size(self):
        """Test macros calculated when quantity equals serving size."""
        user = UserFactory()
        food = FoodFactory(
            serving_size=100.0,
            calories=200,
            protein=10.0,
            carbs=25.0,
            fats=8.0
        )

        food_log = FoodLog.objects.create(
            user=user,
            food=food,
            quantity_grams=100.0,  # Same as serving size
            meal_type='lunch',
            date=date.today()
        )

        assert food_log.calories == 200
        assert food_log.protein == 10.0
        assert food_log.carbs == 25.0
        assert food_log.fats == 8.0

    def test_macros_calculated_for_double_serving(self):
        """Test macros calculated for double the serving size."""
        user = UserFactory()
        food = FoodFactory(
            serving_size=100.0,
            calories=200,
            protein=10.0,
            carbs=25.0,
            fats=8.0
        )

        food_log = FoodLog.objects.create(
            user=user,
            food=food,
            quantity_grams=200.0,  # Double serving
            meal_type='dinner',
            date=date.today()
        )

        assert food_log.calories == 400  # 200 * 2
        assert food_log.protein == 20.0  # 10 * 2
        assert food_log.carbs == 50.0   # 25 * 2
        assert food_log.fats == 16.0    # 8 * 2

    def test_macros_calculated_for_half_serving(self):
        """Test macros calculated for half the serving size."""
        user = UserFactory()
        food = FoodFactory(
            serving_size=100.0,
            calories=200,
            protein=10.0,
            carbs=25.0,
            fats=8.0
        )

        food_log = FoodLog.objects.create(
            user=user,
            food=food,
            quantity_grams=50.0,  # Half serving
            meal_type='snack',
            date=date.today()
        )

        assert food_log.calories == 100  # 200 * 0.5
        assert food_log.protein == 5.0   # 10 * 0.5
        assert food_log.carbs == 12.5    # 25 * 0.5
        assert food_log.fats == 4.0      # 8 * 0.5

    def test_macros_calculated_for_arbitrary_quantity(self):
        """Test macros calculated for arbitrary quantity."""
        user = UserFactory()
        food = FoodFactory(
            serving_size=244.0,  # 1 cup milk
            calories=150,
            protein=8.0,
            carbs=12.0,
            fats=8.0
        )

        food_log = FoodLog.objects.create(
            user=user,
            food=food,
            quantity_grams=122.0,  # Half cup
            meal_type='breakfast',
            date=date.today()
        )

        # Ratio: 122 / 244 = 0.5
        assert food_log.calories == 75   # 150 * 0.5
        assert food_log.protein == 4.0   # 8 * 0.5
        assert food_log.carbs == 6.0     # 12 * 0.5
        assert food_log.fats == 4.0      # 8 * 0.5

    def test_macros_recalculated_on_quantity_update(self):
        """Test that macros are recalculated when quantity changes."""
        user = UserFactory()
        food = FoodFactory(
            serving_size=100.0,
            calories=200,
            protein=10.0,
            carbs=25.0,
            fats=8.0
        )

        food_log = FoodLog.objects.create(
            user=user,
            food=food,
            quantity_grams=100.0,
            meal_type='lunch',
            date=date.today()
        )

        original_calories = food_log.calories
        assert original_calories == 200

        # Update quantity
        food_log.quantity_grams = 150.0
        food_log.save()

        food_log.refresh_from_db()
        assert food_log.calories == 300  # 200 * 1.5
        assert food_log.protein == 15.0  # 10 * 1.5

    def test_macros_handled_when_food_has_no_nutrition(self):
        """Test macro calculation when food has no nutritional data."""
        user = UserFactory()
        food = FoodFactory(
            serving_size=100.0,
            calories=None,
            protein=None,
            carbs=None,
            fats=None
        )

        food_log = FoodLog.objects.create(
            user=user,
            food=food,
            quantity_grams=100.0,
            meal_type='snack',
            date=date.today()
        )

        assert food_log.calories == 0
        assert food_log.protein == 0.0
        assert food_log.carbs == 0.0
        assert food_log.fats == 0.0


class TestFoodLogMealTypes:
    """Test meal type functionality."""

    def test_create_breakfast_log(self):
        """Test creating a breakfast food log."""
        food_log = FoodLogFactory(meal_type='breakfast')
        assert food_log.meal_type == 'breakfast'

    def test_create_lunch_log(self):
        """Test creating a lunch food log."""
        food_log = FoodLogFactory(meal_type='lunch')
        assert food_log.meal_type == 'lunch'

    def test_create_dinner_log(self):
        """Test creating a dinner food log."""
        food_log = FoodLogFactory(meal_type='dinner')
        assert food_log.meal_type == 'dinner'

    def test_create_snack_log(self):
        """Test creating a snack food log."""
        food_log = FoodLogFactory(meal_type='snack')
        assert food_log.meal_type == 'snack'

    def test_filter_logs_by_meal_type(self):
        """Test filtering logs by meal type."""
        user = UserFactory()
        today = date.today()

        FoodLogFactory(user=user, date=today, meal_type='breakfast')
        FoodLogFactory(user=user, date=today, meal_type='breakfast')
        FoodLogFactory(user=user, date=today, meal_type='lunch')

        breakfast_logs = FoodLog.objects.filter(user=user, date=today, meal_type='breakfast')

        assert breakfast_logs.count() == 2


class TestFoodLogDailyTracking:
    """Test daily food tracking functionality."""

    def test_user_can_log_multiple_foods_per_day(self):
        """Test that users can log multiple foods in one day."""
        user = UserFactory()
        today = date.today()

        FoodLogFactory(user=user, date=today, meal_type='breakfast')
        FoodLogFactory(user=user, date=today, meal_type='lunch')
        FoodLogFactory(user=user, date=today, meal_type='dinner')

        daily_logs = FoodLog.objects.filter(user=user, date=today)

        assert daily_logs.count() == 3

    def test_filter_logs_by_date(self):
        """Test filtering logs by specific date."""
        user = UserFactory()
        today = date.today()
        yesterday = today - timedelta(days=1)

        FoodLogFactory(user=user, date=today)
        FoodLogFactory(user=user, date=today)
        FoodLogFactory(user=user, date=yesterday)

        today_logs = FoodLog.objects.filter(user=user, date=today)

        assert today_logs.count() == 2

    def test_filter_logs_by_date_range(self):
        """Test filtering logs over a date range."""
        user = UserFactory()
        today = date.today()

        # Create logs for past week
        for i in range(7):
            log_date = today - timedelta(days=i)
            FoodLogFactory(user=user, date=log_date)

        # Query last 3 days
        start_date = today - timedelta(days=2)
        recent_logs = FoodLog.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=today
        )

        assert recent_logs.count() == 3

    def test_calculate_daily_totals(self):
        """Test calculating daily macro totals."""
        user = UserFactory()
        today = date.today()

        # Create logs with known macros
        food1 = FoodFactory(serving_size=100.0, calories=200, protein=10.0, carbs=25.0, fats=8.0)
        food2 = FoodFactory(serving_size=100.0, calories=300, protein=15.0, carbs=30.0, fats=12.0)

        FoodLog.objects.create(user=user, food=food1, quantity_grams=100.0, date=today, meal_type='breakfast')
        FoodLog.objects.create(user=user, food=food2, quantity_grams=100.0, date=today, meal_type='lunch')

        # Calculate totals
        daily_logs = FoodLog.objects.filter(user=user, date=today)
        total_calories = sum(log.calories for log in daily_logs)
        total_protein = sum(log.protein for log in daily_logs)

        assert total_calories == 500  # 200 + 300
        assert total_protein == 25.0  # 10 + 15


class TestFoodLogUserIsolation:
    """Test user isolation for food logs."""

    def test_users_have_separate_logs(self):
        """Test that different users have separate food logs."""
        user1 = UserFactory()
        user2 = UserFactory()

        FoodLogFactory(user=user1)
        FoodLogFactory(user=user1)
        FoodLogFactory(user=user2)

        user1_logs = FoodLog.objects.filter(user=user1)
        user2_logs = FoodLog.objects.filter(user=user2)

        assert user1_logs.count() == 2
        assert user2_logs.count() == 1

    def test_user_cannot_see_other_user_logs(self):
        """Test querying only shows user's own logs."""
        user1 = UserFactory()
        user2 = UserFactory()

        FoodLogFactory(user=user1)
        FoodLogFactory(user=user2)

        user1_visible = FoodLog.objects.filter(user=user1)

        assert user1_visible.count() == 1
        assert all(log.user == user1 for log in user1_visible)


class TestFoodLogOrdering:
    """Test ordering of food logs."""

    def test_logs_ordered_by_date_descending(self):
        """Test that logs are ordered by date (most recent first)."""
        user = UserFactory()
        today = date.today()

        # Create logs in random order
        log3 = FoodLogFactory(user=user, date=today - timedelta(days=2))
        log1 = FoodLogFactory(user=user, date=today)
        log2 = FoodLogFactory(user=user, date=today - timedelta(days=1))

        logs = list(FoodLog.objects.filter(user=user))

        # Should be ordered: today, yesterday, 2 days ago
        assert logs[0] == log1
        assert logs[1] == log2
        assert logs[2] == log3


class TestFoodLogDeletion:
    """Test deletion behavior."""

    def test_delete_food_log(self):
        """Test deleting a food log entry."""
        food_log = FoodLogFactory()
        log_id = food_log.id

        food_log.delete()

        assert not FoodLog.objects.filter(id=log_id).exists()

    def test_deleting_user_deletes_logs(self):
        """Test that deleting a user also deletes their food logs."""
        user = UserFactory()
        FoodLogFactory(user=user)
        FoodLogFactory(user=user)

        user_id = user.id

        user.delete()

        remaining_logs = FoodLog.objects.filter(user_id=user_id)
        assert remaining_logs.count() == 0

    def test_deleting_food_deletes_logs(self):
        """Test that deleting a food also deletes related logs."""
        food = FoodFactory()
        FoodLogFactory(food=food)
        FoodLogFactory(food=food)

        food_id = food.id

        food.delete()

        remaining_logs = FoodLog.objects.filter(food_id=food_id)
        assert remaining_logs.count() == 0


class TestFoodLogTimestamps:
    """Test timestamp fields."""

    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        food_log = FoodLogFactory()

        assert food_log.created_at is not None

    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when log is updated."""
        food_log = FoodLogFactory()
        original_updated_at = food_log.updated_at

        # Make a change
        import time
        time.sleep(0.01)
        food_log.quantity_grams = 150.0
        food_log.save()

        food_log.refresh_from_db()
        assert food_log.updated_at > original_updated_at
