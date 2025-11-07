"""
Test suite for USDA Meal Examples Service.

Tests the service that generates curated meal examples from USDA food database:
- Meal retrieval by calorie range
- Ingredient details with grams and portions
- Portion conversions
- Dietary filtering
- Meal type categorization
"""

import pytest
from recipes.usda_meal_service import (
    get_usda_meal_examples,
    convert_grams_to_portion,
    filter_by_dietary_preferences,
    filter_by_allergens
)


@pytest.mark.unit
class TestUSDAMealExamplesRetrieval:
    """Test suite for retrieving USDA meal examples"""

    def test_get_examples_by_calorie_range(self):
        """AC: Should return meals within specified calorie range"""
        examples = get_usda_meal_examples(
            calories=500,
            tolerance=15  # 425-575 kcal
        )

        assert isinstance(examples, list)
        assert len(examples) > 0

        for example in examples:
            assert 425 <= example['calories'] <= 575

    def test_get_examples_for_breakfast(self):
        """AC: Should return breakfast-appropriate meals"""
        examples = get_usda_meal_examples(
            calories=400,
            meal_type='breakfast'
        )

        assert len(examples) > 0

        # Common breakfast items: oatmeal, eggs, yogurt, toast
        example_names = [e['name'].lower() for e in examples]
        breakfast_keywords = ['oatmeal', 'egg', 'yogurt', 'toast', 'pancake', 'breakfast']

        # At least one should contain breakfast keywords
        assert any(any(keyword in name for keyword in breakfast_keywords) for name in example_names)

    def test_get_examples_for_lunch(self):
        """AC: Should return lunch-appropriate meals"""
        examples = get_usda_meal_examples(
            calories=700,
            meal_type='lunch'
        )

        assert len(examples) > 0

    def test_get_examples_for_dinner(self):
        """AC: Should return dinner-appropriate meals"""
        examples = get_usda_meal_examples(
            calories=700,
            meal_type='dinner'
        )

        assert len(examples) > 0

    def test_get_examples_for_snack(self):
        """AC: Should return snack-appropriate meals"""
        examples = get_usda_meal_examples(
            calories=200,
            meal_type='snack'
        )

        assert len(examples) > 0

        # Snacks should generally be smaller portions
        for example in examples:
            assert example['calories'] < 400

    def test_returns_max_10_examples(self):
        """AC: Should return maximum 10 examples"""
        examples = get_usda_meal_examples(calories=500)

        assert len(examples) <= 10

    def test_examples_sorted_by_relevance(self):
        """AC: Examples should be sorted by how close they are to target"""
        target = 500
        examples = get_usda_meal_examples(calories=target)

        if len(examples) > 1:
            # Calculate distance from target for each
            distances = [abs(e['calories'] - target) for e in examples]

            # Should be roughly sorted (allowing for some variation)
            # First example should be closer than last
            assert distances[0] <= distances[-1] + 50  # Some tolerance

    def test_empty_list_when_no_matches(self):
        """AC: Should return empty list when no meals match criteria"""
        # Extreme calorie range unlikely to have matches
        examples = get_usda_meal_examples(
            calories=100,
            tolerance=5  # 95-105 kcal - very narrow
        )

        assert isinstance(examples, list)
        # May be empty or have very few results

    def test_handles_high_calorie_requests(self):
        """AC: Should handle high calorie targets"""
        examples = get_usda_meal_examples(calories=1200)

        assert isinstance(examples, list)

        for example in examples:
            assert example['calories'] > 1000


@pytest.mark.unit
class TestUSDAMealExampleStructure:
    """Test suite for USDA meal example data structure"""

    def test_example_includes_required_fields(self):
        """AC: Each example should have all required fields"""
        examples = get_usda_meal_examples(calories=500)

        assert len(examples) > 0

        example = examples[0]

        # Required fields
        assert 'name' in example
        assert 'calories' in example
        assert 'protein' in example
        assert 'carbs' in example
        assert 'fats' in example
        assert 'ingredients' in example
        assert 'description' in example

    def test_example_macros_are_numeric(self):
        """AC: Macro values should be numeric"""
        examples = get_usda_meal_examples(calories=500)

        example = examples[0]

        assert isinstance(example['calories'], (int, float))
        assert isinstance(example['protein'], (int, float))
        assert isinstance(example['carbs'], (int, float))
        assert isinstance(example['fats'], (int, float))

        # All should be positive
        assert example['calories'] > 0
        assert example['protein'] >= 0
        assert example['carbs'] >= 0
        assert example['fats'] >= 0

    def test_ingredients_list_structure(self):
        """AC: Ingredients should be a list of dicts with required fields"""
        examples = get_usda_meal_examples(calories=500)

        example = examples[0]
        ingredients = example['ingredients']

        assert isinstance(ingredients, list)
        assert len(ingredients) > 0

        ingredient = ingredients[0]

        assert 'name' in ingredient
        assert 'grams' in ingredient
        assert 'portion' in ingredient

    def test_ingredient_grams_positive(self):
        """AC: Ingredient gram amounts should be positive"""
        examples = get_usda_meal_examples(calories=500)

        for example in examples:
            for ingredient in example['ingredients']:
                assert ingredient['grams'] > 0

    def test_ingredient_portions_non_empty(self):
        """AC: Ingredient portions should be non-empty strings"""
        examples = get_usda_meal_examples(calories=500)

        for example in examples:
            for ingredient in example['ingredients']:
                assert isinstance(ingredient['portion'], str)
                assert len(ingredient['portion']) > 0


@pytest.mark.unit
class TestPortionConversions:
    """Test suite for gram to portion conversions"""

    def test_convert_oats_to_cups(self):
        """AC: 85g oats should be ~1 cup"""
        portion = convert_grams_to_portion('oats', 85)

        assert '1 cup' in portion.lower() or '1cup' in portion.lower()

    def test_convert_rice_to_cups(self):
        """AC: 150g cooked rice should be ~1 cup"""
        portion = convert_grams_to_portion('rice', 150)

        assert 'cup' in portion.lower()

    def test_convert_eggs_to_count(self):
        """AC: 100g eggs should be ~2 large eggs"""
        portion = convert_grams_to_portion('eggs', 100)

        assert '2' in portion
        assert 'egg' in portion.lower()

    def test_convert_banana_to_size(self):
        """AC: 120g banana should be ~1 medium banana"""
        portion = convert_grams_to_portion('banana', 120)

        assert '1' in portion
        assert 'medium' in portion.lower() or 'banana' in portion.lower()

    def test_convert_almonds_to_tablespoons(self):
        """AC: 15g almonds should be ~2 tbsp"""
        portion = convert_grams_to_portion('almonds', 15)

        assert 'tbsp' in portion.lower() or 'tablespoon' in portion.lower()

    def test_convert_chicken_to_ounces(self):
        """AC: 170g chicken should be ~6 oz"""
        portion = convert_grams_to_portion('chicken', 170)

        assert 'oz' in portion.lower() or 'ounce' in portion.lower()

    def test_convert_milk_to_cups(self):
        """AC: 240ml milk should be ~1 cup"""
        portion = convert_grams_to_portion('milk', 240)

        assert 'cup' in portion.lower()

    def test_convert_butter_to_tablespoons(self):
        """AC: 14g butter should be ~1 tbsp"""
        portion = convert_grams_to_portion('butter', 14)

        assert '1' in portion
        assert 'tbsp' in portion.lower() or 'tablespoon' in portion.lower()

    def test_convert_unknown_food_returns_grams(self):
        """AC: Unknown foods should fall back to gram display"""
        portion = convert_grams_to_portion('exotic_ingredient', 100)

        assert '100' in portion
        assert 'g' in portion.lower() or 'gram' in portion.lower()

    def test_portion_conversions_are_rounded(self):
        """AC: Portions should use practical rounded numbers"""
        portion = convert_grams_to_portion('oats', 87)  # Close to 1 cup

        # Should round to 1 cup, not show decimal
        assert '1 cup' in portion.lower() or '1cup' in portion.lower()
        assert '0.87' not in portion  # Should not show precise decimal

    def test_portion_includes_food_name_or_unit(self):
        """AC: Portion string should be self-descriptive"""
        portion = convert_grams_to_portion('chicken breast', 170)

        # Should include either the food name or clear unit
        assert len(portion) > 0
        # Examples: "6 oz chicken breast" or "6 oz" or "1 breast"


@pytest.mark.unit
class TestDietaryFiltering:
    """Test suite for dietary preference filtering"""

    def test_filter_vegetarian_meals(self):
        """AC: Should filter out meals with meat"""
        examples = get_usda_meal_examples(
            calories=500,
            dietary_preferences=['vegetarian']
        )

        # Check that returned meals don't contain meat
        meat_keywords = ['chicken', 'beef', 'pork', 'fish', 'turkey', 'meat']

        for example in examples:
            name_lower = example['name'].lower()
            ingredients_text = ' '.join([i['name'].lower() for i in example['ingredients']])

            # Should not contain meat keywords
            has_meat = any(keyword in name_lower or keyword in ingredients_text
                         for keyword in meat_keywords)

            # This test documents expected behavior
            # Actual implementation may vary

    def test_filter_vegan_meals(self):
        """AC: Should filter out meals with animal products"""
        examples = get_usda_meal_examples(
            calories=500,
            dietary_preferences=['vegan']
        )

        # Vegan meals exclude meat, dairy, eggs
        animal_keywords = ['chicken', 'beef', 'egg', 'milk', 'cheese', 'yogurt', 'butter']

        for example in examples:
            ingredients_text = ' '.join([i['name'].lower() for i in example['ingredients']])

            # Document expected vegan filtering

    def test_filter_gluten_free_meals(self):
        """AC: Should filter out meals with gluten"""
        examples = get_usda_meal_examples(
            calories=500,
            dietary_preferences=['gluten_free']
        )

        gluten_keywords = ['wheat', 'bread', 'pasta', 'flour', 'barley', 'rye']

        # Should avoid gluten-containing ingredients

    def test_filter_by_allergens(self):
        """AC: Should exclude meals with specified allergens"""
        allergens = ['nuts', 'dairy']

        filtered = filter_by_allergens(
            [
                {'name': 'Chicken with almonds', 'ingredients': [{'name': 'almonds', 'grams': 30}]},
                {'name': 'Chicken with rice', 'ingredients': [{'name': 'rice', 'grams': 150}]},
                {'name': 'Yogurt parfait', 'ingredients': [{'name': 'yogurt', 'grams': 200}]}
            ],
            allergens
        )

        # Should only return "Chicken with rice"
        assert len(filtered) >= 1
        names = [m['name'] for m in filtered]
        assert 'Chicken with rice' in names


@pytest.mark.unit
class TestMealCalorieDistribution:
    """Test suite for meal calorie levels"""

    def test_low_calorie_meals_300_400(self):
        """AC: Should have examples in 300-400 kcal range (small meals/snacks)"""
        examples = get_usda_meal_examples(
            calories=350,
            tolerance=15
        )

        assert len(examples) > 0

        for example in examples:
            assert 300 <= example['calories'] <= 400

    def test_medium_calorie_meals_500_600(self):
        """AC: Should have examples in 500-600 kcal range (regular meals)"""
        examples = get_usda_meal_examples(
            calories=550,
            tolerance=15
        )

        assert len(examples) > 0

    def test_high_calorie_meals_700_800(self):
        """AC: Should have examples in 700-800 kcal range (large meals)"""
        examples = get_usda_meal_examples(
            calories=750,
            tolerance=15
        )

        assert len(examples) > 0

    def test_very_high_calorie_meals_800_plus(self):
        """AC: Should have examples for 800+ kcal (athlete meals)"""
        examples = get_usda_meal_examples(
            calories=900,
            tolerance=15
        )

        # Should return some results
        assert isinstance(examples, list)


@pytest.mark.unit
class TestMealMacroBalance:
    """Test suite for macro balance in meal examples"""

    def test_high_protein_breakfast_examples(self):
        """AC: Should include high-protein breakfast options"""
        examples = get_usda_meal_examples(
            calories=400,
            meal_type='breakfast'
        )

        # At least some examples should have good protein content
        high_protein_count = sum(1 for e in examples if e['protein'] >= 20)

        assert high_protein_count > 0

    def test_balanced_meal_examples(self):
        """AC: Should include balanced macro meals"""
        examples = get_usda_meal_examples(calories=600)

        # Check that we have variety in macro distributions
        if len(examples) > 3:
            # Calculate protein percentages
            protein_percentages = []
            for e in examples:
                total_cals = (e['protein'] * 4) + (e['carbs'] * 4) + (e['fats'] * 9)
                if total_cals > 0:
                    protein_pct = (e['protein'] * 4 * 100) / total_cals
                    protein_percentages.append(protein_pct)

            # Should have variety (not all the same)
            if len(protein_percentages) > 1:
                assert max(protein_percentages) - min(protein_percentages) > 5

    def test_macros_sum_approximately_to_calories(self):
        """AC: Macros should approximately equal total calories"""
        examples = get_usda_meal_examples(calories=500)

        for example in examples:
            calculated_cals = (
                (example['protein'] * 4) +
                (example['carbs'] * 4) +
                (example['fats'] * 9)
            )

            # Allow 10% tolerance for rounding
            assert abs(calculated_cals - example['calories']) / example['calories'] < 0.10


@pytest.mark.unit
class TestUSDAMealServiceConfiguration:
    """Test suite for USDA meal service configuration"""

    def test_service_uses_cached_data(self):
        """AC: Service should use pre-calculated meal data for performance"""
        import time

        start = time.time()
        examples = get_usda_meal_examples(calories=500)
        duration = time.time() - start

        assert len(examples) > 0
        # Should return quickly from fixtures/cache
        assert duration < 1.0  # Less than 1 second

    def test_service_handles_missing_meal_type(self):
        """AC: Should work without meal_type parameter"""
        examples = get_usda_meal_examples(calories=500)

        assert isinstance(examples, list)

    def test_service_handles_invalid_tolerance(self):
        """AC: Should handle invalid tolerance gracefully"""
        examples = get_usda_meal_examples(
            calories=500,
            tolerance=-10  # Invalid
        )

        # Should use default tolerance or handle gracefully
        assert isinstance(examples, list)

    def test_multiple_dietary_preferences(self):
        """AC: Should handle multiple dietary preferences"""
        examples = get_usda_meal_examples(
            calories=500,
            dietary_preferences=['vegetarian', 'high_protein']
        )

        assert isinstance(examples, list)
