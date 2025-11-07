# Recipe Generator Enhancement Plan

## Overview

Transform RecipeGenerator to connect with user profile, display preferences as tags, align macros with goals, sync ingredient management, and provide meal examples with flexible calorie distribution.

## Your Requirements

1. Profile preferences as editable tags - dietary preferences, allergies, dislikes, cuisine
2. Macro alignment with profile goals - show targets with custom distribution
3. Ingredient sync - connect with available_ingredients and preferred_ingredients from profile
4. Reference display - show relevant profile data while generating
5. Flexible calorie distribution - customize how calories are split across meals
6. Recipe examples - Show example meals for each meal slot based on calorie targets

## Implementation Steps

### 1. Backend: Add Meal Distribution Fields to Profile

Add to Profile model:
- `meals_per_day` (IntegerField, default=3)
- `meal_distribution` (JSONField) - Example: `{"1": 25, "2": 35, "3": 30, "4": 10}`
- `meal_names` (JSONField, optional) - Example: `{"1": "Breakfast", "2": "Lunch"}`

Create migration and update serializer.

### 2. ProfileForm: Add Meal Distribution Section with Examples

In the "Goals" tab, add "Meal Distribution" section:

**Components:**
- Number input: "Meals per day" (1-6, default: 3)
- Dynamic sliders for each meal with:
  - Percentage slider (0-100%)
  - Optional name input (e.g., "Breakfast", "Lunch")
  - Calculated calories display (e.g., "500 kcal")
  - **NEW**: "View Examples" button for each meal

**Slider Features:**
- Real-time total validation: "Total: 100%" (green if correct)
- Preset buttons:
  - "Equal Distribution": Divides evenly
  - "Traditional": 30/40/30
  - "Athlete": 25/35/25/15

**Recipe Examples Feature:**

When user clicks "View Examples" button for a meal:

Expandable section appears below the meal slider showing:

- Title: "Example Meals for [Meal Name] (~500 kcal)"

- **NEW: Display Toggle** at top right:
  - [Macros %] [Grams] [Portions]
  - Switches how food quantities are displayed

- Two tabs:

  - "Saved Recipes": User's saved recipes that fit this meal

  - "USDA Examples": Pre-built meal suggestions from USDA data

**Saved Recipes Tab:**
- Filter user's saved recipes by:
  - Calorie range: ±15% of target (425-575 kcal for 500 target)
  - Meal type if specified
  - Dietary preferences respected
- Display: Recipe name, calories, macros, quick view button
- "Generate similar" button to create variation

**USDA Examples Tab:**
- Show 5-10 pre-curated meal examples from USDA database
- Filter by:
  - Calorie target ±15%
  - User's dietary preferences (vegetarian, etc.)
  - Exclude allergies
- Example meals displayed with quantity toggle:
  - **Macros % view**: "Oatmeal with banana and almonds (480 kcal) - P: 45% | C: 40% | F: 15%"
  - **Grams view**: "Oatmeal with banana and almonds (480 kcal) - 85g oats, 120g banana, 15g almonds"
  - **Portions view**: "Oatmeal with banana and almonds (480 kcal) - 1 cup oats, 1 medium banana, 2 tbsp almonds"
- Each shows: Name, calories, protein, carbs, fats (in selected format)
- "Use as inspiration" button to copy to recipe generator

**Visual Display in Profile:**
```
Meal Distribution:
┌─────────────────────────────────────────┐
│ Meals per day: [4 ▼]                   │
│                                         │
│ Meal 1 [Breakfast____] [View Examples] │
│ ▓▓▓░░░░░░░ 20% (400 kcal)             │
│                                         │
│ ↓ Example Meals for Breakfast (~400 kcal) │
│                        [Macros %] [g] [Portions] │
│ ┌─────────────────────────────────────┐ │
│ │ [Saved Recipes] [USDA Examples]     │ │
│ │                                     │ │
│ │ • Protein Pancakes - 480 kcal       │ │
│ │   150g flour, 2 eggs, 30g protein   │ │
│ │                                     │ │
│ │ • Oatmeal Bowl - 390 kcal           │ │
│ │   1 cup oats, 1 banana, 2 tbsp nuts │ │
│ │                                     │ │
│ │ • Greek Yogurt Parfait - 420 kcal   │ │
│ │   200g yogurt, 1/2 cup berries      │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Meal 2 [Lunch________] [View Examples] │
│ ▓▓▓▓▓▓▓░░░ 35% (700 kcal)             │
│                                         │
│ Meal 3 [Dinner_______] [View Examples] │
│ ▓▓▓▓▓▓░░░░ 30% (600 kcal)             │
│                                         │
│ Meal 4 [Snack________] [View Examples] │
│ ▓▓░░░░░░░░ 15% (300 kcal)             │
│                                         │
│ Total: 100% ✓                           │
└─────────────────────────────────────────┘
[Equal] [Traditional] [Athlete]
```

### 3. Backend: Add Examples Endpoint

Create new API endpoint:
```
GET /api/recipes/examples/?calories=500&meal_type=breakfast&tolerance=15
```

**Response:**
```json
{
  "saved_recipes": [
    {
      "id": 1,
      "name": "Protein Pancakes",
      "calories": 480,
      "protein": 35,
      "carbs": 45,
      "fats": 12,
      "ingredients": [
        {"name": "flour", "grams": 150, "portion": "1.5 cups"},
        {"name": "eggs", "grams": 100, "portion": "2 large eggs"},
        {"name": "protein powder", "grams": 30, "portion": "1 scoop"}
      ]
    }
  ],
  "usda_examples": [
    {
      "name": "Oatmeal Bowl",
      "calories": 490,
      "protein": 15,
      "carbs": 75,
      "fats": 10,
      "description": "Classic breakfast",
      "ingredients": [
        {"name": "oats", "grams": 85, "portion": "1 cup"},
        {"name": "banana", "grams": 120, "portion": "1 medium"},
        {"name": "almonds", "grams": 15, "portion": "2 tbsp"}
      ]
    }
  ]
}
```

**Implementation:**
- Filter user's recipes by calorie range
- Query USDA Food database for common meals/combinations
- Include ingredient breakdown with grams AND portions
- Respect dietary preferences and allergies
- Return max 10 of each type

### 4. Frontend Type Updates

```typescript
interface Profile {
  meals_per_day: number
  meal_distribution: { [key: string]: number }
  meal_names?: { [key: string]: string }
}

interface IngredientDetail {
  name: string
  grams: number
  portion: string  // e.g., "1 cup", "2 eggs"
  protein_percent?: number
  carbs_percent?: number
  fats_percent?: number
}

interface MealExample {
  name: string
  calories: number
  protein: number
  carbs: number
  fats: number
  source: 'saved' | 'usda'
  id?: number  // if saved recipe
  ingredients: IngredientDetail[]
}

type QuantityDisplayMode = 'macros_percent' | 'grams' | 'portions'
```

### 5. RecipeGenerator Component Enhancement

**Add Profile Integration:**
- Fetch profile with meal distribution
- Display meal examples inline when relevant

**Add UI Sections (4 new areas):**

**A) Profile Context Tags (Top of form)**
- Dietary preferences, allergies, dislikes, cuisine as chips
- Each tag has "×" to disable temporarily
- "Edit Profile" link

**B) Macro Goals Card (Collapsible section)**
- Meal Selection Dropdown:
  - "Which meal?: Meal 1 (20% - 400 kcal), Meal 2 (35% - 700 kcal), ..."
  - Shows name if set: "Breakfast (20% - 400 kcal)"
- Target Display:
  - "Target for this meal: ~700 kcal | ~58g protein | ~58g carbs | ~17g fats"
- **NEW**: Quick Examples Link:
  - "Need inspiration? View example meals for this target"
  - Opens expandable section below showing examples (same component as ProfileForm)
  - Filtered for selected meal's calorie target
  - **NEW**: Each example has "Generate Recipe" button
  - When clicked, stays on same page and replaces the form inputs with the example's details
  - Form becomes pre-filled with the example meal info
  - User can then click main "Generate" button or modify first
- Toggle: "Use Profile Goals" vs "Custom for this recipe"

**C) Ingredients Section (Enhanced)**
- Available/Preferred tabs
- Editable ingredient lists
- "Sync to Profile" button

**D) Quick Filters**
- Cuisine, skill level, spice preference

### 6. Recipe Results Enhancement

- Compare generated recipe to selected meal target
- Visual progress bars
- "Save to Recipes" to add to user's collection (available for future examples)

### 7. Create USDA Meal Examples Service

Create a curated list of common meals with USDA data:
- Pre-calculate macros for typical portions
- Store as fixtures or seed data
- Categories: breakfast, lunch, dinner, snacks
- Various calorie levels: 300, 400, 500, 600, 700, 800+ kcal
- **IMPORTANT**: Include both gram weights AND portion sizes for all ingredients
  - Example: "85g (1 cup) oats", "120g (1 medium) banana", "100g (2 large) eggs"

## File Changes Required

### Backend:
1. `backend/users/models.py` - Add meal distribution fields
2. `backend/users/migrations/` - Create migration
3. `backend/users/serializers.py` - Add new fields
4. `backend/recipes/views.py` - Add examples endpoint with ingredient details, pass meal info to LLM
5. `backend/recipes/llm_service.py` - Accept meal_percentage
6. `backend/recipes/serializers.py` - Add meal_number field, ingredient detail fields
7. `backend/recipes/fixtures/` - Create USDA meal examples data with portions (optional)

### Frontend:
1. `frontend/src/types/api.ts` - Update interfaces with ingredient details and display mode
2. `frontend/src/components/ProfileForm.tsx` - Add meal distribution + examples
3. `frontend/src/components/MealExamplesSection.tsx` - **NEW** component for inline examples display with quantity toggle
4. `frontend/src/components/RecipeGenerator.tsx` - Add 4 sections + meal selector + examples link + pre-fill from example
5. `frontend/src/services/recipes.ts` - Add `getMealExamples()` function

## Example User Flow

### Profile Setup:
1. User goes to Profile → Goals tab
2. Sets "Meals per day: 4"
3. Four sliders appear
4. Adjusts distribution: 20% / 35% / 30% / 15%
5. Names meals: "Breakfast" / "Lunch" / "Dinner" / "Snack"
6. Sees calories: 400 / 700 / 600 / 300 kcal
7. Clicks "View Examples" for Breakfast (400 kcal)
8. Section expands below showing:
   - Toggle: [Macros %] [g] [Portions] ← Switches between "P:45% C:40% F:15%", "85g, 120g, 15g", "1 cup, 1 banana, 2 tbsp"
   - Saved: "Protein Pancakes (480 kcal)" - displays "150g flour, 2 eggs, 30g protein" when in Portions mode
   - USDA: "Oatmeal with banana (390 kcal)" - shows "1 cup oats, 1 medium banana, 2 tbsp almonds"
9. Gets ideas for meal planning with practical quantities

### Recipe Generation:
1. Opens Recipe Generator
2. Selects "Meal 2 - Lunch (35% - 700 kcal)"
3. Macro card shows target: ~700 kcal
4. Clicks "Need inspiration? View examples"
5. Section expands showing examples for 700 kcal lunches:
   - Toggle: [Macros %] [g] [**Portions**] ← User selects Portions view
   - Saved: "Chicken Stir-Fry (680 kcal)" - shows "6oz chicken, 2 cups vegetables, 1 cup rice"
   - USDA:
     - "Grilled chicken salad (720 kcal)" - shows "8oz chicken, 3 cups lettuce, 2 tbsp dressing"
     - "Burrito bowl (690 kcal)" - shows "6oz beef, 1 cup rice, 1/2 cup beans, 1/4 avocado" [Generate Recipe]
6. Gets inspired by burrito bowl
7. Clicks "Generate Recipe" button next to "Burrito bowl"
8. **NEW**: Examples section collapses, main form pre-fills with:
   - Meal type: Lunch (700 kcal)
   - Suggested ingredients: beef, rice, beans, avocado
   - Cuisine: Mexican
   - Description hint: "Bowl-style meal similar to burrito bowl"
9. User can modify or click "Generate" immediately
10. Generates "Mexican-style bowl" recipe
11. Result: 695 kcal ✓

## Benefits

- ✅ Visual meal distribution with sliders
- ✅ Context-aware meal examples based on calorie targets
- ✅ Two sources: User's own recipes + USDA database
- ✅ Inspiration and meal planning aid
- ✅ Helps users visualize what X calories looks like
- ✅ Encourages recipe saving (builds personal library)
- ✅ Respects dietary preferences and allergies in examples
- ✅ Available in both Profile (planning) and Recipe Generator (generating)
- ✅ Inline expansion provides seamless UX without modal interruption
- ✅ **Multiple quantity display formats** - users can see macros as %, grams, or practical portions
- ✅ **One-click recipe generation from examples** - streamlined workflow from inspiration to generation
- ✅ **Practical portion sizes** - "2 eggs" and "1 cup" instead of just grams makes meal planning intuitive
