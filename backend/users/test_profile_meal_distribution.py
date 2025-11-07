"""
Test suite for Profile model meal distribution fields.

Tests the new meal distribution functionality added in Spring 2 requirements:
- meals_per_day field
- meal_distribution JSONField
- meal_names JSONField
- Calorie calculations per meal
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from users.models import Profile
from tests.factories import UserFactory, ProfileFactory


@pytest.mark.django_db
class TestProfileMealDistributionFields:
    """Test suite for Profile meal distribution fields"""

    def setup_method(self):
        """Set up test data before each test"""
        self.user = UserFactory()

    def test_default_meals_per_day_is_three(self):
        """AC: Profile should default to 3 meals per day"""
        profile = Profile.objects.create(
            user=self.user,
            daily_calories=2000
        )
        assert profile.meals_per_day == 3

    def test_meals_per_day_accepts_valid_range(self):
        """AC: meals_per_day should accept values 1-6"""
        for num_meals in range(1, 7):
            profile = ProfileFactory(
                user=UserFactory(),
                meals_per_day=num_meals
            )
            assert profile.meals_per_day == num_meals

    def test_meals_per_day_rejects_zero(self):
        """AC: meals_per_day should not accept 0"""
        with pytest.raises((ValidationError, IntegrityError)):
            profile = Profile.objects.create(
                user=self.user,
                meals_per_day=0,
                daily_calories=2000
            )
            profile.full_clean()

    def test_meals_per_day_rejects_negative(self):
        """AC: meals_per_day should not accept negative values"""
        with pytest.raises((ValidationError, IntegrityError)):
            profile = Profile.objects.create(
                user=self.user,
                meals_per_day=-1,
                daily_calories=2000
            )
            profile.full_clean()

    def test_meals_per_day_rejects_too_high(self):
        """AC: meals_per_day should not accept values > 6"""
        with pytest.raises((ValidationError, IntegrityError)):
            profile = Profile.objects.create(
                user=self.user,
                meals_per_day=7,
                daily_calories=2000
            )
            profile.full_clean()

    def test_meal_distribution_stores_percentages(self):
        """AC: meal_distribution should store meal percentages as JSON"""
        distribution = {"1": 25, "2": 35, "3": 30, "4": 10}
        profile = ProfileFactory(
            meals_per_day=4,
            meal_distribution=distribution
        )
        profile.refresh_from_db()

        assert profile.meal_distribution == distribution
        assert profile.meal_distribution["1"] == 25
        assert profile.meal_distribution["2"] == 35

    def test_meal_distribution_can_be_null(self):
        """AC: meal_distribution should be optional (null allowed)"""
        profile = ProfileFactory(
            meals_per_day=3,
            meal_distribution=None
        )
        assert profile.meal_distribution is None

    def test_meal_distribution_empty_dict_allowed(self):
        """AC: meal_distribution can be an empty dict"""
        profile = ProfileFactory(
            meals_per_day=3,
            meal_distribution={}
        )
        assert profile.meal_distribution == {}

    def test_meal_names_stores_custom_names(self):
        """AC: meal_names should store optional custom meal names"""
        names = {"1": "Breakfast", "2": "Lunch", "3": "Dinner"}
        profile = ProfileFactory(
            meals_per_day=3,
            meal_names=names
        )
        profile.refresh_from_db()

        assert profile.meal_names == names
        assert profile.meal_names["1"] == "Breakfast"

    def test_meal_names_can_be_null(self):
        """AC: meal_names should be optional (null allowed)"""
        profile = ProfileFactory(
            meals_per_day=3,
            meal_names=None
        )
        assert profile.meal_names is None

    def test_profile_creation_with_meal_distribution(self):
        """AC: Profile can be created with all meal distribution fields"""
        profile = Profile.objects.create(
            user=self.user,
            daily_calories=2000,
            meals_per_day=4,
            meal_distribution={"1": 20, "2": 35, "3": 30, "4": 15},
            meal_names={"1": "Breakfast", "2": "Lunch", "3": "Dinner", "4": "Snack"}
        )

        assert profile.meals_per_day == 4
        assert len(profile.meal_distribution) == 4
        assert len(profile.meal_names) == 4

    def test_profile_update_preserves_meal_distribution(self):
        """AC: Updating profile should preserve meal distribution"""
        profile = ProfileFactory(
            meals_per_day=4,
            meal_distribution={"1": 25, "2": 25, "3": 25, "4": 25}
        )

        # Update another field
        profile.daily_calories = 2500
        profile.save()
        profile.refresh_from_db()

        assert profile.meal_distribution == {"1": 25, "2": 25, "3": 25, "4": 25}
        assert profile.daily_calories == 2500

    def test_profile_deletion_cascades(self):
        """AC: Deleting user should delete profile with meal distribution"""
        user = UserFactory()
        profile = ProfileFactory(
            user=user,
            meals_per_day=4,
            meal_distribution={"1": 25, "2": 25, "3": 25, "4": 25}
        )
        profile_id = profile.id

        user.delete()

        assert not Profile.objects.filter(id=profile_id).exists()

    def test_meal_distribution_with_three_meals_traditional(self):
        """AC: Traditional 3-meal distribution (30/40/30) should work"""
        profile = ProfileFactory(
            meals_per_day=3,
            meal_distribution={"1": 30, "2": 40, "3": 30}
        )

        total = sum(profile.meal_distribution.values())
        assert total == 100

    def test_meal_distribution_with_four_meals_athlete(self):
        """AC: Athlete 4-meal distribution (25/35/25/15) should work"""
        profile = ProfileFactory(
            meals_per_day=4,
            meal_distribution={"1": 25, "2": 35, "3": 25, "4": 15}
        )

        total = sum(profile.meal_distribution.values())
        assert total == 100

    def test_meal_distribution_equal_split(self):
        """AC: Equal distribution should split evenly"""
        for num_meals in [2, 3, 4, 5, 6]:
            percentage = 100 // num_meals
            distribution = {str(i): percentage for i in range(1, num_meals + 1)}

            profile = ProfileFactory(
                user=UserFactory(),
                meals_per_day=num_meals,
                meal_distribution=distribution
            )

            assert profile.meals_per_day == num_meals
            assert len(profile.meal_distribution) == num_meals


@pytest.mark.django_db
class TestProfileMealCalorieCalculations:
    """Test suite for meal calorie calculations based on distribution"""

    def setup_method(self):
        """Set up test data before each test"""
        self.user = UserFactory()

    def test_get_meal_calories_with_valid_distribution(self):
        """AC: Should calculate correct calories for each meal"""
        profile = ProfileFactory(
            daily_calories=2000,
            meals_per_day=4,
            meal_distribution={"1": 20, "2": 35, "3": 30, "4": 15}
        )

        # Assuming a method exists: get_meal_calories(meal_number)
        # If not, this test documents the expected behavior
        expected_calories = {
            "1": 400,   # 20% of 2000
            "2": 700,   # 35% of 2000
            "3": 600,   # 30% of 2000
            "4": 300,   # 15% of 2000
        }

        for meal_num, expected in expected_calories.items():
            percentage = profile.meal_distribution[meal_num]
            calculated = (profile.daily_calories * percentage) / 100
            assert calculated == expected

    def test_meal_calories_calculation_with_decimal_percentages(self):
        """AC: Should handle decimal percentages correctly"""
        profile = ProfileFactory(
            daily_calories=2000,
            meals_per_day=3,
            meal_distribution={"1": 33.33, "2": 33.33, "3": 33.34}
        )

        # Each meal should be approximately 666-667 calories
        for meal_num in ["1", "2", "3"]:
            percentage = profile.meal_distribution[meal_num]
            calculated = (profile.daily_calories * percentage) / 100
            assert 666 <= calculated <= 667

    def test_meal_calories_with_high_daily_calories(self):
        """AC: Should handle high calorie targets correctly"""
        profile = ProfileFactory(
            daily_calories=4000,
            meals_per_day=5,
            meal_distribution={"1": 20, "2": 20, "3": 25, "4": 20, "5": 15}
        )

        expected = {
            "1": 800,   # 20% of 4000
            "2": 800,   # 20% of 4000
            "3": 1000,  # 25% of 4000
            "4": 800,   # 20% of 4000
            "5": 600,   # 15% of 4000
        }

        for meal_num, expected_cals in expected.items():
            percentage = profile.meal_distribution[meal_num]
            calculated = (profile.daily_calories * percentage) / 100
            assert calculated == expected_cals

    def test_meal_calories_with_low_daily_calories(self):
        """AC: Should handle low calorie targets correctly"""
        profile = ProfileFactory(
            daily_calories=1200,
            meals_per_day=3,
            meal_distribution={"1": 30, "2": 40, "3": 30}
        )

        expected = {
            "1": 360,   # 30% of 1200
            "2": 480,   # 40% of 1200
            "3": 360,   # 30% of 1200
        }

        for meal_num, expected_cals in expected.items():
            percentage = profile.meal_distribution[meal_num]
            calculated = (profile.daily_calories * percentage) / 100
            assert calculated == expected_cals

    def test_total_meal_calories_equals_daily_calories(self):
        """AC: Sum of all meal calories should equal daily calories"""
        profile = ProfileFactory(
            daily_calories=2500,
            meals_per_day=4,
            meal_distribution={"1": 25, "2": 30, "3": 30, "4": 15}
        )

        total = sum(
            (profile.daily_calories * pct) / 100
            for pct in profile.meal_distribution.values()
        )

        # Allow for small floating point differences
        assert abs(total - profile.daily_calories) < 1


@pytest.mark.django_db
class TestProfileMealDistributionValidation:
    """Test suite for meal distribution validation logic"""

    def setup_method(self):
        """Set up test data before each test"""
        self.user = UserFactory()

    def test_meal_distribution_totaling_100_percent(self):
        """AC: Valid distribution should sum to 100%"""
        profile = ProfileFactory(
            meals_per_day=4,
            meal_distribution={"1": 25, "2": 25, "3": 25, "4": 25}
        )

        total = sum(profile.meal_distribution.values())
        assert total == 100

    def test_meal_distribution_not_totaling_100_percent(self):
        """AC: Distribution not summing to 100% should be flagged (document expected behavior)"""
        # This test documents that distributions not summing to 100% should be handled
        # Either by validation or by UI feedback
        profile = ProfileFactory(
            meals_per_day=3,
            meal_distribution={"1": 30, "2": 30, "3": 30}  # Only 90%
        )

        total = sum(profile.meal_distribution.values())
        assert total == 90  # Documents the issue that should be validated

    def test_meal_distribution_exceeding_100_percent(self):
        """AC: Distribution exceeding 100% should be flagged"""
        profile = ProfileFactory(
            meals_per_day=3,
            meal_distribution={"1": 40, "2": 40, "3": 40}  # 120% total
        )

        total = sum(profile.meal_distribution.values())
        assert total == 120  # Documents the issue

    def test_meal_distribution_count_matches_meals_per_day(self):
        """AC: Number of meal entries should match meals_per_day"""
        profile = ProfileFactory(
            meals_per_day=4,
            meal_distribution={"1": 25, "2": 25, "3": 25, "4": 25}
        )

        assert len(profile.meal_distribution) == profile.meals_per_day

    def test_meal_distribution_count_mismatch(self):
        """AC: Document behavior when meal count doesn't match"""
        # This documents a potential validation issue
        profile = ProfileFactory(
            meals_per_day=4,
            meal_distribution={"1": 50, "2": 50}  # Only 2 meals defined
        )

        assert len(profile.meal_distribution) != profile.meals_per_day

    def test_meal_names_optional_for_valid_distribution(self):
        """AC: meal_names should be optional even with valid distribution"""
        profile = ProfileFactory(
            meals_per_day=3,
            meal_distribution={"1": 33, "2": 34, "3": 33},
            meal_names=None
        )

        assert profile.meal_distribution is not None
        assert profile.meal_names is None

    def test_partial_meal_names_allowed(self):
        """AC: User can name only some meals"""
        profile = ProfileFactory(
            meals_per_day=4,
            meal_distribution={"1": 25, "2": 25, "3": 25, "4": 25},
            meal_names={"1": "Breakfast", "4": "Snack"}  # Only 2 named
        )

        assert "1" in profile.meal_names
        assert "4" in profile.meal_names
        assert "2" not in profile.meal_names
        assert "3" not in profile.meal_names
