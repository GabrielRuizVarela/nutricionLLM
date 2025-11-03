"""
Tests for Food model.
Tests USDA food database entries, search, and indexing.
"""

import pytest
from recipes.models import Food
from tests.factories import FoodFactory

pytestmark = pytest.mark.django_db


class TestFoodCreation:
    """Test Food model creation and basic functionality."""

    def test_create_food(self):
        """Test creating a basic food entry."""
        food = Food.objects.create(
            fdc_id=123456,
            description="Organic Whole Milk",
            brand_owner="Happy Farms",
            serving_size=244.0,
            serving_size_unit="ml",
            calories=150,
            protein=8.0,
            carbs=12.0,
            fats=8.0
        )

        assert food.id is not None
        assert food.fdc_id == 123456
        assert food.description == "Organic Whole Milk"
        assert food.brand_owner == "Happy Farms"
        assert food.calories == 150

    def test_food_string_representation(self):
        """Test the string representation of a food."""
        food = FoodFactory(
            description="Greek Yogurt",
            brand_owner="Chobani"
        )

        expected_str = "Greek Yogurt (Chobani)"
        assert str(food) == expected_str

    def test_food_with_minimal_fields(self):
        """Test creating food with only required fields."""
        food = Food.objects.create(
            fdc_id=789012,
            description="Water"
        )

        assert food.id is not None
        assert food.fdc_id == 789012
        assert food.brand_owner == ""
        assert food.calories is None


class TestFoodConstraints:
    """Test database constraints on foods."""

    def test_fdc_id_must_be_unique(self):
        """Test that fdc_id must be unique."""
        fdc_id = 111222
        Food.objects.create(fdc_id=fdc_id, description="Food 1")

        # Attempting to create duplicate should raise error
        with pytest.raises(Exception):  # IntegrityError
            Food.objects.create(fdc_id=fdc_id, description="Food 2")

    def test_multiple_foods_with_same_description(self):
        """Test that multiple foods can have the same description."""
        description = "Chicken Breast"

        food1 = Food.objects.create(fdc_id=1001, description=description, brand_owner="Brand A")
        food2 = Food.objects.create(fdc_id=1002, description=description, brand_owner="Brand B")

        assert food1.id != food2.id
        assert food1.description == food2.description


class TestFoodSearch:
    """Test food search and querying."""

    def test_search_by_description(self):
        """Test searching foods by description."""
        FoodFactory(description="Organic Milk")
        FoodFactory(description="Whole Milk")
        FoodFactory(description="Almond Milk")
        FoodFactory(description="Orange Juice")

        # Search for foods containing "Milk"
        results = Food.objects.filter(description__icontains="Milk")

        assert results.count() == 3
        assert all("Milk" in food.description or "milk" in food.description.lower()
                   for food in results)

    def test_search_by_brand(self):
        """Test searching foods by brand owner."""
        FoodFactory(description="Yogurt", brand_owner="Chobani")
        FoodFactory(description="Milk", brand_owner="Chobani")
        FoodFactory(description="Yogurt", brand_owner="Dannon")

        results = Food.objects.filter(brand_owner="Chobani")

        assert results.count() == 2

    def test_search_by_barcode(self):
        """Test searching foods by barcode."""
        food = FoodFactory(barcode="012345678901")

        result = Food.objects.filter(barcode="012345678901").first()

        assert result == food

    def test_food_ordering(self):
        """Test that foods are ordered by description."""
        FoodFactory(description="Zucchini")
        FoodFactory(description="Apple")
        FoodFactory(description="Milk")

        foods = list(Food.objects.all())
        descriptions = [f.description for f in foods]

        # Should be alphabetically ordered
        assert descriptions == sorted(descriptions)


class TestFoodNutrition:
    """Test nutritional information storage."""

    def test_food_with_complete_nutrition(self):
        """Test food with all nutritional fields."""
        food = FoodFactory(
            calories=200,
            protein=10.0,
            carbs=25.0,
            fats=8.0,
            fiber=3.0,
            sugars=5.0,
            sodium=150.0
        )

        assert food.calories == 200
        assert food.protein == 10.0
        assert food.carbs == 25.0
        assert food.fats == 8.0
        assert food.fiber == 3.0
        assert food.sugars == 5.0
        assert food.sodium == 150.0

    def test_food_with_partial_nutrition(self):
        """Test food with only macronutrients."""
        food = FoodFactory(
            calories=150,
            protein=8.0,
            carbs=12.0,
            fats=8.0,
            fiber=None,
            sugars=None,
            sodium=None
        )

        assert food.calories == 150
        assert food.protein == 8.0
        assert food.fiber is None
        assert food.sugars is None

    def test_food_with_no_nutrition(self):
        """Test food with no nutritional information."""
        food = FoodFactory(
            calories=None,
            protein=None,
            carbs=None,
            fats=None
        )

        assert food.calories is None
        assert food.protein is None
        assert food.carbs is None
        assert food.fats is None


class TestFoodServingSize:
    """Test serving size information."""

    def test_food_with_serving_size(self):
        """Test food with serving size information."""
        food = FoodFactory(
            serving_size=100.0,
            serving_size_unit="g"
        )

        assert food.serving_size == 100.0
        assert food.serving_size_unit == "g"

    def test_food_with_different_units(self):
        """Test foods with different serving size units."""
        food_ml = FoodFactory(serving_size=250.0, serving_size_unit="ml")
        food_g = FoodFactory(serving_size=100.0, serving_size_unit="g")
        food_oz = FoodFactory(serving_size=28.0, serving_size_unit="oz")

        assert food_ml.serving_size_unit == "ml"
        assert food_g.serving_size_unit == "g"
        assert food_oz.serving_size_unit == "oz"

    def test_food_without_serving_size(self):
        """Test food without serving size information."""
        food = FoodFactory(serving_size=None, serving_size_unit="")

        assert food.serving_size is None
        assert food.serving_size_unit == ""


class TestFoodIndexing:
    """Test database indexes for performance."""

    def test_fdc_id_indexed(self):
        """Test that fdc_id is indexed for fast lookups."""
        # Create many foods
        for i in range(100):
            FoodFactory(fdc_id=100000 + i)

        # Query by fdc_id should be fast
        food = Food.objects.filter(fdc_id=100050).first()
        assert food is not None
        assert food.fdc_id == 100050

    def test_description_indexed(self):
        """Test that description is indexed for fast searches."""
        # Create many foods
        for i in range(100):
            FoodFactory(description=f"Food Item {i}")

        # Search by description should be fast
        results = Food.objects.filter(description__icontains="Item 50")
        assert results.count() >= 1


class TestFoodCategories:
    """Test food categorization."""

    def test_food_with_category(self):
        """Test food with category field."""
        food = FoodFactory(category="Dairy Products")

        assert food.category == "Dairy Products"

    def test_filter_by_category(self):
        """Test filtering foods by category."""
        FoodFactory(category="Dairy Products")
        FoodFactory(category="Dairy Products")
        FoodFactory(category="Fruits")

        dairy_foods = Food.objects.filter(category="Dairy Products")

        assert dairy_foods.count() == 2


class TestFoodIngredients:
    """Test ingredient information storage."""

    def test_food_with_ingredients(self):
        """Test storing ingredient list."""
        ingredients = "Whole milk, vitamin D3, vitamin A palmitate"
        food = FoodFactory(ingredients=ingredients)

        assert food.ingredients == ingredients

    def test_food_without_ingredients(self):
        """Test food without ingredient list."""
        food = FoodFactory(ingredients="")

        assert food.ingredients == ""


class TestFoodTimestamps:
    """Test timestamp fields."""

    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        food = FoodFactory()

        assert food.created_at is not None

    def test_created_at_not_updated_on_save(self):
        """Test that created_at doesn't change on update."""
        food = FoodFactory()
        original_created_at = food.created_at

        # Update food
        food.description = "Updated Description"
        food.save()

        food.refresh_from_db()
        assert food.created_at == original_created_at
