"""
Tests for dynamic meal slots based on user's meals_per_day setting.

Tests verify that meal slots are created correctly for 1-6 meals per day
and that custom meal names from the user's profile are used.
"""
import pytest
from datetime import date
from django.contrib.auth.models import User
from users.models import Profile
from recipes.models import MealPlan, MealSlot


@pytest.mark.django_db
class TestDynamicMealSlotCreation:
    """Test that meal slots are created based on user's meals_per_day setting"""

    def setup_method(self):
        """Create a test user for each test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_creates_7_slots_for_1_meal_per_day(self):
        """Test creating meal plan with 1 meal per day (7 total slots)"""
        # Set profile to 1 meal per day
        self.profile.meals_per_day = 1
        self.profile.meal_names = {'1': 'OMAD'}
        self.profile.save()

        # Create meal plan (without auto-creating slots)
        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        # Manually create slots (simulating the view's _create_empty_slots)
        from recipes.views import MealPlanViewSet
        view = MealPlanViewSet()
        view._create_empty_slots(meal_plan)

        # Should create 7 slots (1 per day × 7 days)
        assert MealSlot.objects.filter(meal_plan=meal_plan).count() == 7

        # All slots should be meal_number 1
        slots = MealSlot.objects.filter(meal_plan=meal_plan)
        assert all(slot.meal_number == 1 for slot in slots)

        # All slots should have the custom name "OMAD"
        assert all(slot.meal_type == 'OMAD' for slot in slots)

    def test_creates_14_slots_for_2_meals_per_day(self):
        """Test creating meal plan with 2 meals per day (14 total slots)"""
        # Set profile to 2 meals per day
        self.profile.meals_per_day = 2
        self.profile.meal_names = {'1': 'Brunch', '2': 'Dinner'}
        self.profile.save()

        # Create meal plan
        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        from recipes.views import MealPlanViewSet
        view = MealPlanViewSet()
        view._create_empty_slots(meal_plan)

        # Should create 14 slots (2 per day × 7 days)
        assert MealSlot.objects.filter(meal_plan=meal_plan).count() == 14

        # Check meal numbers are correct
        monday_slots = MealSlot.objects.filter(meal_plan=meal_plan, day_of_week=0).order_by('meal_number')
        assert len(monday_slots) == 2
        assert monday_slots[0].meal_number == 1
        assert monday_slots[0].meal_type == 'Brunch'
        assert monday_slots[1].meal_number == 2
        assert monday_slots[1].meal_type == 'Dinner'

    def test_creates_21_slots_for_3_meals_per_day_default(self):
        """Test creating meal plan with 3 meals per day (21 total slots - default)"""
        # Set profile to 3 meals (default)
        self.profile.meals_per_day = 3
        self.profile.meal_names = {'1': 'Breakfast', '2': 'Lunch', '3': 'Dinner'}
        self.profile.save()

        # Create meal plan
        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        from recipes.views import MealPlanViewSet
        view = MealPlanViewSet()
        view._create_empty_slots(meal_plan)

        # Should create 21 slots (3 per day × 7 days)
        assert MealSlot.objects.filter(meal_plan=meal_plan).count() == 21

        # Check custom names
        breakfast_slots = MealSlot.objects.filter(meal_plan=meal_plan, meal_number=1)
        assert all(slot.meal_type == 'Breakfast' for slot in breakfast_slots)

        lunch_slots = MealSlot.objects.filter(meal_plan=meal_plan, meal_number=2)
        assert all(slot.meal_type == 'Lunch' for slot in lunch_slots)

        dinner_slots = MealSlot.objects.filter(meal_plan=meal_plan, meal_number=3)
        assert all(slot.meal_type == 'Dinner' for slot in dinner_slots)

    def test_creates_28_slots_for_4_meals_per_day(self):
        """Test creating meal plan with 4 meals per day (28 total slots)"""
        # Set profile to 4 meals per day
        self.profile.meals_per_day = 4
        self.profile.meal_names = {
            '1': 'Breakfast',
            '2': 'Lunch',
            '3': 'Dinner',
            '4': 'Snack'
        }
        self.profile.save()

        # Create meal plan
        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        from recipes.views import MealPlanViewSet
        view = MealPlanViewSet()
        view._create_empty_slots(meal_plan)

        # Should create 28 slots (4 per day × 7 days)
        assert MealSlot.objects.filter(meal_plan=meal_plan).count() == 28

        # Verify each day has all 4 meals
        for day in range(7):
            day_slots = MealSlot.objects.filter(
                meal_plan=meal_plan,
                day_of_week=day
            ).order_by('meal_number')
            assert len(day_slots) == 4
            assert [s.meal_number for s in day_slots] == [1, 2, 3, 4]

    def test_creates_35_slots_for_5_meals_per_day(self):
        """Test creating meal plan with 5 meals per day (35 total slots)"""
        # Set profile to 5 meals per day
        self.profile.meals_per_day = 5
        self.profile.meal_names = {
            '1': 'Breakfast',
            '2': 'Mid-Morning Snack',
            '3': 'Lunch',
            '4': 'Afternoon Snack',
            '5': 'Dinner'
        }
        self.profile.save()

        # Create meal plan
        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        from recipes.views import MealPlanViewSet
        view = MealPlanViewSet()
        view._create_empty_slots(meal_plan)

        # Should create 35 slots (5 per day × 7 days)
        assert MealSlot.objects.filter(meal_plan=meal_plan).count() == 35

        # Check meal names
        meal_2_slots = MealSlot.objects.filter(meal_plan=meal_plan, meal_number=2)
        assert all(slot.meal_type == 'Mid-Morning Snack' for slot in meal_2_slots)

    def test_creates_42_slots_for_6_meals_per_day(self):
        """Test creating meal plan with 6 meals per day (42 total slots)"""
        # Set profile to 6 meals per day
        self.profile.meals_per_day = 6
        self.profile.meal_names = {
            '1': 'Meal 1',
            '2': 'Meal 2',
            '3': 'Meal 3',
            '4': 'Meal 4',
            '5': 'Meal 5',
            '6': 'Meal 6'
        }
        self.profile.save()

        # Create meal plan
        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        from recipes.views import MealPlanViewSet
        view = MealPlanViewSet()
        view._create_empty_slots(meal_plan)

        # Should create 42 slots (6 per day × 7 days)
        assert MealSlot.objects.filter(meal_plan=meal_plan).count() == 42

        # Verify all 6 meals exist for each day
        for day in range(7):
            day_slots = MealSlot.objects.filter(
                meal_plan=meal_plan,
                day_of_week=day
            ).order_by('meal_number')
            assert len(day_slots) == 6
            assert [s.meal_number for s in day_slots] == [1, 2, 3, 4, 5, 6]

    def test_uses_default_meal_names_when_not_specified(self):
        """Test that default meal names are used when user doesn't specify custom names"""
        # Set meals_per_day but no custom names
        self.profile.meals_per_day = 4
        self.profile.meal_names = {}  # Empty
        self.profile.save()

        # Create meal plan
        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        from recipes.views import MealPlanViewSet
        view = MealPlanViewSet()
        view._create_empty_slots(meal_plan)

        # Check that default names "Meal 1", "Meal 2", etc. are used
        monday_slots = MealSlot.objects.filter(
            meal_plan=meal_plan,
            day_of_week=0
        ).order_by('meal_number')

        assert monday_slots[0].meal_type == 'Meal 1'
        assert monday_slots[1].meal_type == 'Meal 2'
        assert monday_slots[2].meal_type == 'Meal 3'
        assert monday_slots[3].meal_type == 'Meal 4'

    def test_defaults_to_3_meals_when_not_configured(self):
        """Test that system defaults to 3 meals per day when user hasn't configured it"""
        # Profile should already have meals_per_day=3 by default
        # Just verify the default is 3
        assert self.profile.meals_per_day == 3

        # Create meal plan
        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        from recipes.views import MealPlanViewSet
        view = MealPlanViewSet()
        view._create_empty_slots(meal_plan)

        # Should create 21 slots (default 3 meals per day)
        assert MealSlot.objects.filter(meal_plan=meal_plan).count() == 21

    def test_meal_slots_ordered_by_meal_number(self):
        """Test that meal slots are correctly ordered by meal_number"""
        self.profile.meals_per_day = 3
        self.profile.save()

        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        from recipes.views import MealPlanViewSet
        view = MealPlanViewSet()
        view._create_empty_slots(meal_plan)

        # Get Monday's slots
        monday_slots = MealSlot.objects.filter(
            meal_plan=meal_plan,
            day_of_week=0
        )

        # Should be ordered by meal_number
        ordered_nums = list(monday_slots.values_list('meal_number', flat=True))
        assert ordered_nums == sorted(ordered_nums)

    def test_unique_constraint_on_meal_plan_day_meal_number(self):
        """Test that unique constraint prevents duplicate meal slots"""
        self.profile.meals_per_day = 3
        self.profile.save()

        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        # Create first slot
        MealSlot.objects.create(
            meal_plan=meal_plan,
            day_of_week=0,
            meal_number=1,
            meal_type='Breakfast'
        )

        # Try to create duplicate slot (same day, same meal_number)
        with pytest.raises(Exception):  # Should raise IntegrityError
            MealSlot.objects.create(
                meal_plan=meal_plan,
                day_of_week=0,
                meal_number=1,
                meal_type='Breakfast 2'
            )


@pytest.mark.django_db
class TestMealSlotSerialization:
    """Test that meal_number is properly serialized in API responses"""

    def setup_method(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_meal_number_included_in_serialized_output(self):
        """Test that meal_number field is included in serializer output"""
        from recipes.serializers import MealSlotSerializer

        self.profile.meals_per_day = 4
        self.profile.save()

        meal_plan = MealPlan.objects.create(
            user=self.user,
            week_start_date=date(2024, 1, 1)
        )

        meal_slot = MealSlot.objects.create(
            meal_plan=meal_plan,
            day_of_week=0,
            meal_number=2,
            meal_type='Lunch'
        )

        serializer = MealSlotSerializer(meal_slot)
        data = serializer.data

        # Check that meal_number is in the output
        assert 'meal_number' in data
        assert data['meal_number'] == 2
        assert data['meal_type'] == 'Lunch'
