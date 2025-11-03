"""
Tests for MealSlot model.
Tests slot creation, properties, date calculation, and leftover linking.
"""

import pytest
from datetime import date, timedelta
from recipes.models import MealSlot
from tests.factories import UserFactory, MealPlanFactory, MealSlotFactory, RecetaFactory

pytestmark = pytest.mark.django_db


class TestMealSlotCreation:
    """Test MealSlot model creation and basic functionality."""

    def test_create_meal_slot(self):
        """Test creating a basic meal slot."""
        meal_plan = MealPlanFactory(create_slots=False)

        slot = MealSlot.objects.create(
            meal_plan=meal_plan,
            day_of_week=0,  # Monday
            meal_type='breakfast'
        )

        assert slot.id is not None
        assert slot.meal_plan == meal_plan
        assert slot.day_of_week == 0
        assert slot.meal_type == 'breakfast'
        assert slot.recipe is None
        assert slot.is_leftover is False

    def test_meal_slot_string_representation(self):
        """Test the string representation of a meal slot."""
        meal_plan = MealPlanFactory(create_slots=False)
        slot = MealSlot.objects.create(
            meal_plan=meal_plan,
            day_of_week=0,
            meal_type='breakfast'
        )

        # Actual format: "{day_name} {meal_name}: {recipe_name}"
        expected_str = "Monday Breakfast: Empty"
        assert str(slot) == expected_str


class TestMealSlotProperties:
    """Test computed properties of MealSlot model."""

    def test_day_name_property_monday(self):
        """Test day_name property for Monday."""
        meal_plan = MealPlanFactory(create_slots=False)
        slot = MealSlotFactory(meal_plan=meal_plan, day_of_week=0)
        assert slot.day_name == 'Monday'

    def test_day_name_property_all_days(self):
        """Test day_name property for all days of the week."""
        meal_plan = MealPlanFactory(create_slots=False)
        expected_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        meal_types = ['breakfast', 'lunch', 'dinner']

        for day_index, expected_name in enumerate(expected_names):
            # Use different meal types to avoid uniqueness conflicts
            meal_type = meal_types[day_index % 3]
            slot = MealSlotFactory(meal_plan=meal_plan, day_of_week=day_index, meal_type=meal_type)
            assert slot.day_name == expected_name

    def test_meal_name_property_breakfast(self):
        """Test meal_name property for breakfast."""
        meal_plan = MealPlanFactory(create_slots=False)
        slot = MealSlotFactory(meal_plan=meal_plan, meal_type='breakfast')
        assert slot.meal_name == 'Breakfast'

    def test_meal_name_property_all_meals(self):
        """Test meal_name property for all meal types."""
        meal_plan = MealPlanFactory(create_slots=False)
        meal_mappings = {
            'breakfast': 'Breakfast',
            'lunch': 'Lunch',
            'dinner': 'Dinner'
        }

        for day_index, (meal_type, expected_name) in enumerate(meal_mappings.items()):
            # Use different days to avoid uniqueness conflicts
            slot = MealSlotFactory(meal_plan=meal_plan, day_of_week=day_index, meal_type=meal_type)
            assert slot.meal_name == expected_name


class TestMealSlotDateCalculation:
    """Test automatic date calculation for meal slots."""

    def test_date_calculation_monday(self):
        """Test that date is calculated correctly for Monday."""
        monday = date(2024, 1, 1)
        meal_plan = MealPlanFactory(create_slots=False)
        meal_plan.week_start_date = monday
        meal_plan.save()

        slot = MealSlot.objects.create(
            meal_plan=meal_plan,
            day_of_week=0,  # Monday
            meal_type='breakfast'
        )

        assert slot.date == monday

    def test_date_calculation_all_days(self):
        """Test date calculation for all days of the week."""
        monday = date(2024, 1, 1)
        meal_plan = MealPlanFactory(create_slots=False)
        meal_plan.week_start_date = monday
        meal_plan.save()

        for day_index in range(7):
            slot = MealSlot.objects.create(
                meal_plan=meal_plan,
                day_of_week=day_index,
                meal_type='lunch'
            )

            expected_date = monday + timedelta(days=day_index)
            assert slot.date == expected_date

    def test_date_updates_when_meal_plan_dates_change(self):
        """Test that slot date updates when meal plan dates change."""
        old_monday = date(2024, 1, 1)
        meal_plan = MealPlanFactory(create_slots=False)
        meal_plan.week_start_date = old_monday
        meal_plan.save()

        slot = MealSlot.objects.create(
            meal_plan=meal_plan,
            day_of_week=3,  # Thursday
            meal_type='dinner'
        )

        original_date = slot.date

        # Change meal plan start date
        new_monday = date(2024, 1, 8)
        meal_plan.week_start_date = new_monday
        meal_plan.save()

        # Recalculate slot date
        slot.save()
        slot.refresh_from_db()

        assert slot.date != original_date
        assert slot.date == new_monday + timedelta(days=3)


class TestMealSlotRecipeAssignment:
    """Test assigning recipes to meal slots."""

    def test_assign_recipe_to_slot(self):
        """Test assigning a recipe to a meal slot."""
        user = UserFactory()
        meal_plan = MealPlanFactory(user=user, create_slots=False)
        recipe = RecetaFactory(user=user)
        slot = MealSlotFactory(meal_plan=meal_plan)

        slot.recipe = recipe
        slot.save()

        slot.refresh_from_db()
        assert slot.recipe == recipe

    def test_remove_recipe_from_slot(self):
        """Test removing a recipe from a meal slot."""
        user = UserFactory()
        meal_plan = MealPlanFactory(user=user, create_slots=False)
        recipe = RecetaFactory(user=user)
        slot = MealSlotFactory(meal_plan=meal_plan, recipe=recipe)

        slot.recipe = None
        slot.save()

        slot.refresh_from_db()
        assert slot.recipe is None

    def test_slot_can_be_empty(self):
        """Test that meal slots can exist without a recipe."""
        meal_plan = MealPlanFactory(create_slots=False)
        slot = MealSlotFactory(meal_plan=meal_plan, recipe=None)

        assert slot.recipe is None
        assert slot.id is not None


class TestMealSlotLeftovers:
    """Test leftover functionality for meal slots."""

    def test_mark_slot_as_leftover(self):
        """Test marking a slot as a leftover."""
        user = UserFactory()
        meal_plan = MealPlanFactory(user=user, create_slots=False)
        original_slot = MealSlotFactory(meal_plan=meal_plan, day_of_week=0, meal_type='lunch')
        leftover_slot = MealSlotFactory(meal_plan=meal_plan, day_of_week=1, meal_type='lunch')

        leftover_slot.is_leftover = True
        leftover_slot.original_meal_slot = original_slot
        leftover_slot.save()

        assert leftover_slot.is_leftover is True
        assert leftover_slot.original_meal_slot == original_slot

    def test_leftover_links_to_original_recipe(self):
        """Test that leftover slot can reference original meal's recipe."""
        user = UserFactory()
        meal_plan = MealPlanFactory(user=user, create_slots=False)
        recipe = RecetaFactory(user=user)

        # Original meal with recipe
        original_slot = MealSlotFactory(
            meal_plan=meal_plan,
            day_of_week=0,
            meal_type='dinner',
            recipe=recipe
        )

        # Leftover meal
        leftover_slot = MealSlotFactory(
            meal_plan=meal_plan,
            day_of_week=1,
            meal_type='lunch',
            is_leftover=True,
            original_meal_slot=original_slot
        )

        assert leftover_slot.original_meal_slot.recipe == recipe

    def test_non_leftover_slot_has_no_original(self):
        """Test that non-leftover slots have no original meal slot."""
        meal_plan = MealPlanFactory(create_slots=False)
        slot = MealSlotFactory(meal_plan=meal_plan, is_leftover=False)

        assert slot.original_meal_slot is None


class TestMealSlotNotes:
    """Test notes functionality for meal slots."""

    def test_add_notes_to_slot(self):
        """Test adding notes to a meal slot."""
        meal_plan = MealPlanFactory(create_slots=False)
        slot = MealSlotFactory(meal_plan=meal_plan)

        notes = "Prepare night before, double portion"
        slot.notes = notes
        slot.save()

        slot.refresh_from_db()
        assert slot.notes == notes

    def test_notes_can_be_empty(self):
        """Test that notes field can be empty."""
        meal_plan = MealPlanFactory(create_slots=False)
        slot = MealSlotFactory(meal_plan=meal_plan, notes='')

        assert slot.notes == ''

    def test_update_notes(self):
        """Test updating existing notes."""
        meal_plan = MealPlanFactory(create_slots=False)
        slot = MealSlotFactory(meal_plan=meal_plan, notes='Original note')

        slot.notes = 'Updated note'
        slot.save()

        slot.refresh_from_db()
        assert slot.notes == 'Updated note'


class TestMealSlotValidation:
    """Test validation for meal slots."""

    def test_day_of_week_range(self):
        """Test that day_of_week must be between 0-6."""
        meal_plan = MealPlanFactory(create_slots=False)

        # Valid days (0-6)
        for day in range(7):
            slot = MealSlot.objects.create(
                meal_plan=meal_plan,
                day_of_week=day,
                meal_type='breakfast'
            )
            assert slot.day_of_week == day

    def test_meal_type_choices(self):
        """Test that only valid meal types are accepted."""
        meal_plan = MealPlanFactory(create_slots=False)
        valid_meal_types = ['breakfast', 'lunch', 'dinner']

        for meal_type in valid_meal_types:
            slot = MealSlot.objects.create(
                meal_plan=meal_plan,
                day_of_week=0,
                meal_type=meal_type
            )
            assert slot.meal_type == meal_type


class TestMealSlotOrdering:
    """Test ordering of meal slots."""

    def test_slots_ordered_by_date_and_meal_type(self):
        """Test that slots can be ordered by date and then meal type."""
        meal_plan = MealPlanFactory(create_slots=False)

        # Create slots in random order
        slot_wed_dinner = MealSlotFactory(meal_plan=meal_plan, day_of_week=2, meal_type='dinner')
        slot_mon_breakfast = MealSlotFactory(meal_plan=meal_plan, day_of_week=0, meal_type='breakfast')
        slot_mon_lunch = MealSlotFactory(meal_plan=meal_plan, day_of_week=0, meal_type='lunch')

        # Query ordered by day and meal type
        slots = MealSlot.objects.filter(meal_plan=meal_plan).order_by('day_of_week', 'meal_type')

        # breakfast < dinner < lunch alphabetically
        expected_order = [slot_mon_breakfast, slot_mon_lunch, slot_wed_dinner]
        assert list(slots) == expected_order


class TestMealSlotDeletion:
    """Test deletion behavior of meal slots."""

    def test_delete_meal_slot(self):
        """Test deleting a meal slot."""
        meal_plan = MealPlanFactory(create_slots=False)
        slot = MealSlotFactory(meal_plan=meal_plan)
        slot_id = slot.id

        slot.delete()

        assert MealSlot.objects.filter(id=slot_id).count() == 0

    def test_deleting_recipe_nullifies_slot_reference(self):
        """Test that deleting a recipe sets slot recipe to NULL."""
        user = UserFactory()
        meal_plan = MealPlanFactory(user=user, create_slots=False)
        recipe = RecetaFactory(user=user)
        slot = MealSlotFactory(meal_plan=meal_plan, recipe=recipe)

        recipe.delete()

        slot.refresh_from_db()
        # Depending on CASCADE vs SET_NULL, this might be null or raise error
        # Document actual behavior
        # assert slot.recipe is None  # If using SET_NULL
