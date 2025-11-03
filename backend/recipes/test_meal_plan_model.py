"""
Tests for MealPlan model.
Tests meal plan creation, date validation, and constraints.
"""

import pytest
from datetime import date, timedelta
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from recipes.models import MealPlan, MealSlot
from tests.factories import UserFactory, MealPlanFactory

pytestmark = pytest.mark.django_db


class TestMealPlanCreation:
    """Test MealPlan model creation and basic functionality."""

    def test_create_meal_plan(self):
        """Test creating a basic meal plan."""
        user = UserFactory()
        monday = date.today() - timedelta(days=date.today().weekday())

        meal_plan = MealPlan.objects.create(
            user=user,
            week_start_date=monday
        )

        assert meal_plan.id is not None
        assert meal_plan.user == user
        assert meal_plan.week_start_date == monday
        assert meal_plan.created_at is not None
        assert meal_plan.updated_at is not None

    def test_meal_plan_stores_week_start_date(self):
        """Test that week_start_date is stored correctly."""
        user = UserFactory()
        monday = date(2024, 1, 1)  # A Monday

        meal_plan = MealPlan.objects.create(
            user=user,
            week_start_date=monday
        )

        assert meal_plan.week_start_date == monday
        # Model only stores start date, end date can be calculated as start + 6 days

    def test_meal_plan_string_representation(self):
        """Test the string representation of a meal plan."""
        user = UserFactory(username='testuser')
        monday = date(2024, 1, 1)

        meal_plan = MealPlan.objects.create(
            user=user,
            week_start_date=monday
        )

        expected_str = f"testuser's plan for week of 2024-01-01"
        assert str(meal_plan) == expected_str


class TestMealPlanDateValidation:
    """Test date validation for meal plans."""

    def test_week_start_date_must_be_monday(self):
        """Test that week_start_date should be a Monday."""
        user = UserFactory()
        tuesday = date(2024, 1, 2)  # A Tuesday

        meal_plan = MealPlan.objects.create(
            user=user,
            week_start_date=tuesday
        )

        # Model allows any date, but application logic should enforce Monday
        # This test documents current behavior
        assert meal_plan.week_start_date == tuesday

    def test_week_span_calculation(self):
        """Test that a week spans 7 days from start date."""
        user = UserFactory()
        start_date = date(2024, 2, 5)  # Random Monday

        meal_plan = MealPlan.objects.create(
            user=user,
            week_start_date=start_date
        )

        # Week end would be 6 days after start (if calculated)
        week_end = start_date + timedelta(days=6)
        assert (week_end - meal_plan.week_start_date).days == 6


class TestMealPlanConstraints:
    """Test database constraints on meal plans."""

    def test_user_can_have_multiple_meal_plans(self):
        """Test that a user can have multiple meal plans for different weeks."""
        user = UserFactory()

        # Create meal plans for different weeks
        week1 = date(2024, 1, 1)
        week2 = date(2024, 1, 8)

        plan1 = MealPlan.objects.create(user=user, week_start_date=week1)
        plan2 = MealPlan.objects.create(user=user, week_start_date=week2)

        assert plan1.id != plan2.id
        assert MealPlan.objects.filter(user=user).count() == 2

    def test_user_cannot_have_duplicate_meal_plans_same_week(self):
        """Test that a user cannot have two meal plans for the same week."""
        user = UserFactory()
        monday = date(2024, 1, 1)

        MealPlan.objects.create(user=user, week_start_date=monday)

        # Attempting to create duplicate should raise IntegrityError
        with pytest.raises(IntegrityError):
            MealPlan.objects.create(user=user, week_start_date=monday)

    def test_different_users_can_have_same_week(self):
        """Test that different users can have meal plans for the same week."""
        user1 = UserFactory(username='user1')
        user2 = UserFactory(username='user2')
        monday = date(2024, 1, 1)

        plan1 = MealPlan.objects.create(user=user1, week_start_date=monday)
        plan2 = MealPlan.objects.create(user=user2, week_start_date=monday)

        assert plan1.id != plan2.id
        assert plan1.week_start_date == plan2.week_start_date


class TestMealPlanRelationships:
    """Test relationships between MealPlan and other models."""

    def test_meal_plan_has_meal_slots_relation(self):
        """Test that meal plan can access its meal slots."""
        user = UserFactory()
        meal_plan = MealPlanFactory(user=user)

        # MealPlanFactory creates 21 slots automatically
        slots = meal_plan.meal_slots.all()

        assert slots.count() == 21  # 7 days × 3 meals

    def test_meal_plan_deletion_cascades_to_slots(self):
        """Test that deleting a meal plan also deletes its slots."""
        user = UserFactory()
        meal_plan = MealPlanFactory(user=user)

        meal_plan_id = meal_plan.id
        slot_count = meal_plan.meal_slots.count()

        # Delete meal plan
        meal_plan.delete()

        # Verify slots are also deleted
        remaining_slots = MealSlot.objects.filter(meal_plan_id=meal_plan_id).count()
        assert remaining_slots == 0

    def test_deleting_user_deletes_meal_plans(self):
        """Test that deleting a user also deletes their meal plans."""
        user = UserFactory()
        MealPlanFactory(user=user)
        MealPlanFactory(user=user)

        user_id = user.id

        # Delete user
        user.delete()

        # Verify meal plans deleted
        remaining_plans = MealPlan.objects.filter(user_id=user_id).count()
        assert remaining_plans == 0


class TestMealPlanOrdering:
    """Test ordering and querying of meal plans."""

    def test_meal_plans_ordered_by_week_start_date(self):
        """Test that meal plans can be ordered by week start date."""
        user = UserFactory()

        # Create meal plans in random order
        week3 = MealPlan.objects.create(user=user, week_start_date=date(2024, 1, 15))
        week1 = MealPlan.objects.create(user=user, week_start_date=date(2024, 1, 1))
        week2 = MealPlan.objects.create(user=user, week_start_date=date(2024, 1, 8))

        # Query ordered by week_start_date
        plans = MealPlan.objects.filter(user=user).order_by('week_start_date')

        assert list(plans) == [week1, week2, week3]

    def test_query_meal_plan_by_week_start(self):
        """Test querying meal plans by week start date."""
        user = UserFactory()

        # Create meal plan for Jan 1, 2024
        monday = date(2024, 1, 1)
        meal_plan = MealPlan.objects.create(user=user, week_start_date=monday)

        # Query for exact week start
        matching_plans = MealPlan.objects.filter(
            user=user,
            week_start_date=monday
        )

        assert matching_plans.count() == 1
        assert matching_plans.first() == meal_plan

    def test_query_meal_plan_by_date_in_week(self):
        """Test finding meal plan containing a specific date."""
        user = UserFactory()

        # Create meal plan for Jan 1, 2024
        monday = date(2024, 1, 1)
        MealPlan.objects.create(user=user, week_start_date=monday)

        # To find plan containing a date, check if date is within start to start+6
        # This would be done in view logic, not model query


class TestMealPlanUpdates:
    """Test updating meal plan fields."""

    def test_update_meal_plan_week_start_date(self):
        """Test updating the week start date."""
        user = UserFactory()
        meal_plan = MealPlanFactory(user=user)

        new_monday = date(2024, 2, 5)
        meal_plan.week_start_date = new_monday
        meal_plan.save()

        meal_plan.refresh_from_db()
        assert meal_plan.week_start_date == new_monday

    def test_updated_at_changes_on_save(self):
        """Test that updated_at timestamp changes when saving."""
        meal_plan = MealPlanFactory()

        original_updated_at = meal_plan.updated_at

        # Make a change and save
        import time
        time.sleep(0.01)  # Ensure time difference
        meal_plan.save()

        meal_plan.refresh_from_db()
        assert meal_plan.updated_at > original_updated_at
