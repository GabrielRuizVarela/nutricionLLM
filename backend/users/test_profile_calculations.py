"""
Tests for Profile BMR and TDEE calculations.
Tests the Mifflin-St Jeor equation for BMR and activity multipliers for TDEE.
"""

import pytest
from django.contrib.auth import get_user_model
from users.models import Profile

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestBMRCalculation:
    """Test Basal Metabolic Rate (BMR) calculations using Mifflin-St Jeor equation."""

    def test_bmr_calculation_for_male(self):
        """Test BMR calculation for male user."""
        user = User.objects.create_user(username='john', email='john@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        # Set profile data
        profile.age = 30
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.gender = 'male'
        profile.save()

        # Expected BMR for male: (10 × 75) + (6.25 × 180) - (5 × 30) + 5
        # = 750 + 1125 - 150 + 5 = 1730
        expected_bmr = 1730
        assert profile.bmr == expected_bmr

    def test_bmr_calculation_for_female(self):
        """Test BMR calculation for female user."""
        user = User.objects.create_user(username='jane', email='jane@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.age = 25
        profile.weight_kg = 60.0
        profile.height_cm = 165.0
        profile.gender = 'female'
        profile.save()

        # Expected BMR for female: (10 × 60) + (6.25 × 165) - (5 × 25) - 161
        # = 600 + 1031.25 - 125 - 161 = 1345.25 ≈ 1345
        expected_bmr = 1345
        assert profile.bmr == expected_bmr

    def test_bmr_returns_none_when_required_fields_missing(self):
        """Test that BMR is None when required fields are missing."""
        user = User.objects.create_user(username='incomplete', email='incomplete@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        # No age, weight, height, or gender set
        assert profile.bmr is None

    def test_bmr_returns_none_when_age_missing(self):
        """Test that BMR is None when age is missing."""
        user = User.objects.create_user(username='noage', email='noage@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.gender = 'male'
        # age not set
        profile.save()

        assert profile.bmr is None

    def test_bmr_returns_none_when_weight_missing(self):
        """Test that BMR is None when weight is missing."""
        user = User.objects.create_user(username='noweight', email='noweight@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.age = 30
        profile.height_cm = 180.0
        profile.gender = 'male'
        # weight_kg not set
        profile.save()

        assert profile.bmr is None

    def test_bmr_returns_none_when_height_missing(self):
        """Test that BMR is None when height is missing."""
        user = User.objects.create_user(username='noheight', email='noheight@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.age = 30
        profile.weight_kg = 75.0
        profile.gender = 'male'
        # height_cm not set
        profile.save()

        assert profile.bmr is None

    def test_bmr_returns_none_when_gender_missing(self):
        """Test that BMR is None when gender is missing."""
        user = User.objects.create_user(username='nogender', email='nogender@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.age = 30
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        # gender not set
        profile.save()

        assert profile.bmr is None

    def test_bmr_auto_calculated_on_save(self):
        """Test that BMR is automatically calculated when profile is saved."""
        user = User.objects.create_user(username='auto', email='auto@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        assert profile.bmr is None  # Initially None

        # Set required fields
        profile.age = 35
        profile.weight_kg = 80.0
        profile.height_cm = 175.0
        profile.gender = 'male'
        profile.save()

        # BMR should be auto-calculated
        # (10 × 80) + (6.25 × 175) - (5 × 35) + 5 = 800 + 1093.75 - 175 + 5 = 1723.75 ≈ 1723 (int conversion)
        assert profile.bmr == 1723

    def test_bmr_recalculated_when_data_changes(self):
        """Test that BMR is recalculated when profile data changes."""
        user = User.objects.create_user(username='change', email='change@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        # Initial data
        profile.age = 30
        profile.weight_kg = 70.0
        profile.height_cm = 170.0
        profile.gender = 'male'
        profile.save()

        initial_bmr = profile.bmr
        assert initial_bmr is not None

        # Change weight
        profile.weight_kg = 80.0
        profile.save()

        # BMR should be different
        assert profile.bmr != initial_bmr
        assert profile.bmr > initial_bmr  # Higher weight = higher BMR


class TestTDEECalculation:
    """Test Total Daily Energy Expenditure (TDEE) calculations."""

    def test_tdee_sedentary(self):
        """Test TDEE calculation for sedentary activity level."""
        user = User.objects.create_user(username='sedentary', email='sedentary@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.age = 30
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.gender = 'male'
        profile.activity_level = 'sedentary'
        profile.save()

        # BMR = 1730, TDEE = 1730 × 1.2 = 2076
        expected_tdee = int(1730 * 1.2)
        assert profile.tdee == expected_tdee

    def test_tdee_lightly_active(self):
        """Test TDEE calculation for lightly active level."""
        user = User.objects.create_user(username='light', email='light@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.age = 30
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.gender = 'male'
        profile.activity_level = 'lightly_active'
        profile.save()

        # BMR = 1730, TDEE = 1730 × 1.375 = 2378.75 ≈ 2379
        expected_tdee = int(1730 * 1.375)
        assert profile.tdee == expected_tdee

    def test_tdee_moderately_active(self):
        """Test TDEE calculation for moderately active level."""
        user = User.objects.create_user(username='moderate', email='moderate@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.age = 30
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.gender = 'male'
        profile.activity_level = 'moderately_active'
        profile.save()

        # BMR = 1730, TDEE = 1730 × 1.55 = 2681.5 ≈ 2682
        expected_tdee = int(1730 * 1.55)
        assert profile.tdee == expected_tdee

    def test_tdee_very_active(self):
        """Test TDEE calculation for very active level."""
        user = User.objects.create_user(username='veryactive', email='veryactive@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.age = 30
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.gender = 'male'
        profile.activity_level = 'very_active'
        profile.save()

        # BMR = 1730, TDEE = 1730 × 1.725 = 2984.25 ≈ 2984
        expected_tdee = int(1730 * 1.725)
        assert profile.tdee == expected_tdee

    def test_tdee_extremely_active(self):
        """Test TDEE calculation for extremely active level."""
        user = User.objects.create_user(username='extreme', email='extreme@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.age = 30
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.gender = 'male'
        profile.activity_level = 'extremely_active'
        profile.save()

        # BMR = 1730, TDEE = 1730 × 1.9 = 3287
        expected_tdee = int(1730 * 1.9)
        assert profile.tdee == expected_tdee

    def test_tdee_returns_none_when_bmr_is_none(self):
        """Test that TDEE is None when BMR cannot be calculated."""
        user = User.objects.create_user(username='nobmr', email='nobmr@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.activity_level = 'moderately_active'
        # No age, weight, height, gender
        profile.save()

        assert profile.tdee is None

    def test_tdee_returns_none_when_activity_level_missing(self):
        """Test that TDEE is None when activity level is not set."""
        user = User.objects.create_user(username='noactivity', email='noactivity@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        profile.age = 30
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.gender = 'male'
        # activity_level not set
        profile.save()

        assert profile.bmr is not None
        assert profile.tdee is None

    def test_tdee_auto_calculated_on_save(self):
        """Test that TDEE is automatically calculated when profile is saved."""
        user = User.objects.create_user(username='autotdee', email='autotdee@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        assert profile.tdee is None  # Initially None

        # Set required fields
        profile.age = 30
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.gender = 'male'
        profile.activity_level = 'moderately_active'
        profile.save()

        # TDEE should be auto-calculated
        assert profile.tdee is not None
        assert profile.tdee > profile.bmr  # TDEE should always be greater than BMR

    def test_tdee_recalculated_when_activity_level_changes(self):
        """Test that TDEE is recalculated when activity level changes."""
        user = User.objects.create_user(username='activitychange', email='activitychange@test.com', password='test123')
        profile = Profile.objects.get(user=user)

        # Initial sedentary
        profile.age = 30
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.gender = 'male'
        profile.activity_level = 'sedentary'
        profile.save()

        sedentary_tdee = profile.tdee

        # Change to very active
        profile.activity_level = 'very_active'
        profile.save()

        # TDEE should be much higher
        assert profile.tdee > sedentary_tdee
        assert profile.tdee == int(profile.bmr * 1.725)
