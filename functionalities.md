# NutriAI - Application Functionalities Summary

## Table of Contents
1. [Backend API Endpoints](#backend-api-endpoints)
2. [Frontend Pages & Routes](#frontend-pages--routes)
3. [Database Models](#database-models)
4. [Frontend Components](#frontend-components)
5. [Services](#services)
6. [Features by Phase](#features-by-phase)

---

## Backend API Endpoints

### Authentication (`backend/users/`)

#### File: `backend/users/views.py`
- **POST** `/api/register/` - Register new user
  - Request: `{ email, username, password }`
  - Response: `{ token, user_id, username, email }`
  - Creates user account and authentication token

- **POST** `/api/login/` - User login
  - Request: `{ email, password }`
  - Response: `{ token, user_id, username, email }`
  - Authenticates user and returns token

- **POST** `/api/logout/` - User logout
  - Headers: `Authorization: Token {token}`
  - Invalidates authentication token

### User Profile (`backend/users/`)

#### File: `backend/users/views.py`
- **GET** `/api/profile/` - Get user profile
  - Headers: `Authorization: Token {token}`
  - Response: Complete profile with personal info, dietary preferences, nutritional targets
  - Auto-calculates BMR and TDEE

- **PATCH** `/api/profile/` - Update user profile
  - Headers: `Authorization: Token {token}`
  - Request: Partial profile data (any fields)
  - Response: Updated profile with recalculated BMR/TDEE

#### Profile Fields:
- **Personal:** age, weight_kg, height_cm, gender, activity_level
- **Dietary:** goal, dietary_preferences, allergies, dislikes
- **Recipe Preferences:** cuisine_preferences, cooking_skill_level, spice_preference
- **Ingredients:** preferred_ingredients, available_ingredients
- **Targets:** daily_calorie_target, daily_protein_target, daily_carbs_target, daily_fats_target
- **Calculated:** bmr (Basal Metabolic Rate), tdee (Total Daily Energy Expenditure)

### Recipe Management (`backend/recipes/`)

#### File: `backend/recipes/views.py`

- **POST** `/api/generate/` - Generate AI recipe
  - Headers: `Authorization: Token {token}`
  - Request: `{ meal_type, available_time }`
  - Response: AI-generated recipe with name, ingredients, steps, macros
  - Uses OpenAI GPT-4 with user's profile preferences

- **GET** `/api/recetas/` - List all user recipes
  - Headers: `Authorization: Token {token}`
  - Response: Array of all user's saved recipes
  - Ordered by creation date (newest first)

- **POST** `/api/recetas/` - Create recipe manually
  - Headers: `Authorization: Token {token}`
  - Request: Recipe data (name, ingredients, steps, macros, etc.)
  - Response: Created recipe object

- **GET** `/api/recetas/{id}/` - Get specific recipe
  - Headers: `Authorization: Token {token}`
  - Response: Single recipe details

- **PATCH** `/api/recetas/{id}/` - Update recipe
  - Headers: `Authorization: Token {token}`
  - Request: Partial recipe data
  - Response: Updated recipe

- **DELETE** `/api/recetas/{id}/` - Delete recipe
  - Headers: `Authorization: Token {token}`
  - Response: 204 No Content

### Meal Planning (`backend/recipes/`)

#### File: `backend/recipes/views.py`

- **GET** `/api/meal-plans/` - List all meal plans
  - Headers: `Authorization: Token {token}`
  - Response: Array of meal plans with slots and recipes
  - Each plan spans Monday-Sunday

- **POST** `/api/meal-plans/` - Create meal plan
  - Headers: `Authorization: Token {token}`
  - Request: `{ week_start_date }` (YYYY-MM-DD, must be Monday)
  - Response: Meal plan with 21 empty slots (7 days × 3 meals)
  - Auto-generates breakfast, lunch, dinner slots for each day

- **GET** `/api/meal-plans/{id}/` - Get specific meal plan
  - Headers: `Authorization: Token {token}`
  - Response: Meal plan with all slots and recipe details

- **DELETE** `/api/meal-plans/{id}/` - Delete meal plan
  - Headers: `Authorization: Token {token}`
  - Response: 204 No Content

- **GET** `/api/meal-plans/by_date/` - Get meal plan by date
  - Headers: `Authorization: Token {token}`
  - Query: `?date=YYYY-MM-DD`
  - Response: Meal plan for the week containing that date
  - Auto-creates plan if none exists

#### Meal Slots

- **GET** `/api/meal-slots/` - List all meal slots
  - Headers: `Authorization: Token {token}`
  - Response: Array of meal slots

- **PATCH** `/api/meal-slots/{id}/` - Update meal slot
  - Headers: `Authorization: Token {token}`
  - Request: `{ recipe?, is_leftover?, original_meal_slot?, notes? }`
  - Response: Updated slot with recipe details
  - Use this to assign recipes to slots or mark as leftovers

- **DELETE** `/api/meal-slots/{id}/clear/` - Clear meal slot
  - Headers: `Authorization: Token {token}`
  - Response: Cleared slot (recipe removed)

### Food Database & Logging (`backend/recipes/`)

#### File: `backend/recipes/views.py`

- **GET** `/api/foods/search/` - Search USDA food database
  - Headers: `Authorization: Token {token}`
  - Query: `?q=chicken` (min 2 characters)
  - Response: Array of matching foods (max 20 results)
  - Searches by description and brand name
  - Database contains 1,000+ USDA branded foods

- **GET** `/api/food-logs/` - List food logs
  - Headers: `Authorization: Token {token}`
  - Query: `?date=YYYY-MM-DD` (optional, defaults to today)
  - Response: Array of food logs for specified date
  - Includes full food details and calculated macros

- **POST** `/api/food-logs/` - Create food log entry
  - Headers: `Authorization: Token {token}`
  - Request: `{ food, date, meal_type, quantity_grams }`
  - Response: Food log with auto-calculated macros
  - Macros calculated based on quantity and serving size

- **DELETE** `/api/food-logs/{id}/` - Delete food log
  - Headers: `Authorization: Token {token}`
  - Response: 204 No Content

- **GET** `/api/food-logs/daily_totals/` - Get daily nutrition totals
  - Headers: `Authorization: Token {token}`
  - Query: `?date=YYYY-MM-DD` (optional, defaults to today)
  - Response:
    ```json
    {
      "date": "2025-10-18",
      "totals": {
        "calories": 1850,
        "protein": 125.5,
        "carbs": 200.3,
        "fats": 65.2
      },
      "by_meal": {
        "breakfast": { "calories": 450, ... },
        "lunch": { "calories": 650, ... },
        "dinner": { "calories": 750, ... },
        "snack": { "calories": 0, ... }
      }
    }
    ```

---

## Frontend Pages & Routes

### Public Routes

#### File: `frontend/src/pages/RegisterPage.tsx`
- **Route:** `/register`
- **Capability:** User registration form
- Collects email, username, password
- Validates password length (min 8 characters)
- Auto-login after successful registration

#### File: `frontend/src/pages/LoginPage.tsx`
- **Route:** `/login`
- **Capability:** User login form
- Email and password authentication
- Stores token in localStorage
- Redirects to home after login

### Protected Routes (Require Authentication)

#### File: `frontend/src/pages/HomePage.tsx`
- **Route:** `/`
- **Capability:** Dashboard/Landing page
- Welcome message
- Navigation to key features

#### File: `frontend/src/pages/ProfilePage.tsx`
- **Route:** `/profile`
- **Capability:** User profile management
- Edit personal information (age, weight, height, gender, activity level)
- Set dietary preferences and goals
- Manage allergies and dislikes
- Set recipe preferences (cuisine, skill level, spice)
- Manage ingredient lists (preferred, available)
- Set daily nutritional targets
- View calculated BMR and TDEE

#### File: `frontend/src/pages/GenerateRecipePage.tsx`
- **Route:** `/generate`
- **Capability:** AI recipe generation
- Select meal type (breakfast, lunch, dinner, snack)
- Choose available cooking time
- Generate personalized recipes using AI
- Based on user's profile, preferences, and available ingredients
- View generated recipe with ingredients, steps, and macros
- Save generated recipes to collection

#### File: `frontend/src/pages/RecipesPage.tsx`
- **Route:** `/recipes`
- **Capability:** Recipe collection management
- View all saved recipes
- Filter by meal type
- Search recipes by name/ingredients
- View recipe details (ingredients, steps, macros, prep time)
- Delete recipes

#### File: `frontend/src/pages/MealPlannerPage.tsx`
- **Route:** `/meal-planner`
- **Capability:** Weekly meal planning
- View 7-day meal plan (Monday-Sunday)
- 3 meals per day (breakfast, lunch, dinner)
- Navigate between weeks
- Assign recipes to meal slots
- Mark meals as leftovers
- Add notes to meals
- Auto-creates meal plan if none exists
- Visual calendar layout

#### File: `frontend/src/pages/FoodLogPage.tsx`
- **Route:** `/food-log`
- **Capability:** Daily food logging and tracking
- Search USDA food database (1,000+ foods)
- Log foods for breakfast, lunch, dinner, snacks
- Specify quantity in grams or serving units
- View daily nutrition totals
- Progress bars toward daily targets
- Navigate between dates
- View/delete logged foods
- Meal-by-meal breakdown
- Auto-calculated macros

---

## Database Models

### User Models (`backend/users/models.py`)

#### User (Django built-in)
- Standard Django user with email, username, password

#### Profile
- **Relations:** OneToOne with User
- **Personal Info:** age, weight_kg, height_cm, gender, activity_level
- **Dietary Info:** goal, dietary_preferences, allergies, dislikes
- **Recipe Preferences:** cuisine_preferences, cooking_skill_level, spice_preference
- **Ingredients:** preferred_ingredients, available_ingredients
- **Targets:** daily_calorie_target, daily_protein_target, daily_carbs_target, daily_fats_target
- **Calculated Fields:** bmr, tdee (auto-calculated on save)
- **Methods:**
  - `calculate_bmr()` - Mifflin-St Jeor equation
  - `calculate_tdee()` - BMR × activity multiplier

### Recipe Models (`backend/recipes/models.py`)

#### Receta (Recipe)
- **Relations:** ForeignKey to User
- **Fields:**
  - name (recipe title)
  - ingredients (text)
  - steps (text)
  - calories, protein, carbs, fats (nutritional info)
  - prep_time_minutes
  - meal_type (breakfast, lunch, dinner, snack)
  - created_at, updated_at
- **Indexes:** meal_type, created_at
- **Ordering:** -created_at (newest first)

#### MealPlan
- **Relations:** ForeignKey to User
- **Fields:**
  - week_start_date (Monday, YYYY-MM-DD)
  - week_end_date (Sunday, auto-calculated)
  - created_at, updated_at
- **Relations:** meal_slots (reverse ForeignKey)
- **Indexes:** user, week_start_date
- **Constraints:** Unique together (user, week_start_date)

#### MealSlot
- **Relations:**
  - ForeignKey to MealPlan
  - ForeignKey to Receta (nullable)
  - ForeignKey to self (original_meal_slot, for leftovers)
- **Fields:**
  - day_of_week (0-6, Monday-Sunday)
  - meal_type (breakfast, lunch, dinner)
  - is_leftover (boolean)
  - notes (text)
  - date (YYYY-MM-DD, auto-calculated)
  - created_at, updated_at
- **Properties:**
  - day_name (e.g., "Monday")
  - meal_name (e.g., "Breakfast")
- **Indexes:** meal_plan, date, meal_type

#### Food (USDA Database)
- **Fields:**
  - fdc_id (USDA unique ID)
  - description (food name)
  - brand_owner
  - barcode
  - ingredients (text)
  - category
  - serving_size, serving_size_unit
  - calories, protein, carbs, fats, fiber, sugars, sodium
- **Indexes:** fdc_id (unique), description, barcode
- **Source:** USDA FoodData Central branded foods (1,000+ imported)

#### FoodLog
- **Relations:**
  - ForeignKey to User
  - ForeignKey to Food
- **Fields:**
  - date (YYYY-MM-DD)
  - meal_type (breakfast, lunch, dinner, snack)
  - quantity_grams
  - calories, protein, carbs, fats (auto-calculated)
  - created_at, updated_at
- **Methods:**
  - `save()` - Auto-calculates macros based on quantity
- **Indexes:** user, date, meal_type
- **Ordering:** created_at

---

## Frontend Components

### Layout Components

#### File: `frontend/src/components/Navbar.tsx`
- Navigation bar with app branding
- Conditional rendering (authenticated vs public)
- Links: Home, Profile, Recipes, Meal Planner, Food Diary
- Theme toggle (light/dark mode)
- Logout button

#### File: `frontend/src/components/ProtectedRoute.tsx`
- Route guard component
- Checks authentication token
- Redirects to login if not authenticated

#### File: `frontend/src/components/ThemeProvider.tsx`
- Dark/light mode context provider
- Persists theme preference to localStorage

#### File: `frontend/src/components/ThemeToggle.tsx`
- Theme switcher button
- Toggle between light/dark mode

### Profile Components

#### File: `frontend/src/components/ProfileForm.tsx`
- Comprehensive profile editing form
- Sections:
  - Personal Information
  - Dietary Information
  - Recipe Preferences
  - Ingredient Management
  - Nutritional Targets
- Real-time validation
- Displays calculated BMR/TDEE
- Auto-saves on submit

### Recipe Components

#### File: `frontend/src/components/RecipeCard.tsx`
- Display recipe in card format
- Shows name, meal type, prep time
- Displays macros (calories, protein, carbs, fats)
- Ingredients and steps preview
- Delete button

### Meal Planning Components

#### File: `frontend/src/components/WeeklyMealPlanner.tsx`
- 7-day calendar grid view
- Week navigation (previous/next)
- Displays all meal slots with recipes
- Click to add/change recipes
- Leftover indicators
- Notes display
- Integrates MealSlotCard and MealSelectionModal

#### File: `frontend/src/components/MealSlotCard.tsx`
- Individual meal slot display
- Shows assigned recipe or "Add Meal" button
- Recipe name, calories, and macros
- Add/Edit/Clear actions
- Visual leftover indicator

#### File: `frontend/src/components/MealSelectionModal.tsx`
- Dialog for selecting recipes for meal slots
- Search/filter recipes
- Filter by meal type (matching slot)
- Recipe list with details
- Click to assign recipe
- "Generate New Recipe" button
- Closes after selection

### Food Logging Components

#### File: `frontend/src/components/DailyFoodLog.tsx`
- Main food diary interface
- Date navigation
- Daily nutrition totals with progress bars
- Grouped by meal type (4 sections)
- Each meal section shows:
  - List of logged foods
  - Individual food macros
  - Meal totals
  - "Add Food" button
- Delete food entries
- Integrates FoodSearchModal
- Dark mode support

#### File: `frontend/src/components/FoodSearchModal.tsx`
- Search USDA food database
- Real-time search (debounced)
- Display search results with details
- Select food and specify quantity
- Preview calculated macros based on quantity
- Adjustable serving sizes
- Submit to log food
- Dark mode support

### UI Components (shadcn/ui)

#### File: `frontend/src/components/ui/button.tsx`
- Reusable button component
- Variants: default, outline, ghost, destructive
- Sizes: sm, default, lg

#### File: `frontend/src/components/ui/input.tsx`
- Text input component
- Form integration

#### File: `frontend/src/components/ui/label.tsx`
- Form label component

#### File: `frontend/src/components/ui/select.tsx`
- Dropdown select component
- Multi-option selection

#### File: `frontend/src/components/ui/textarea.tsx`
- Multi-line text input

#### File: `frontend/src/components/ui/card.tsx`
- Card container component
- Parts: Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter
- Dark mode border support

#### File: `frontend/src/components/ui/dialog.tsx`
- Modal dialog component
- Used for meal selection and food search
- Overlay and content sections

#### File: `frontend/src/components/ui/scroll-area.tsx`
- Scrollable container
- Used in modals for long lists

#### File: `frontend/src/components/ui/tabs.tsx`
- Tab navigation component

---

## Services

### Backend Services

#### File: `backend/recipes/llm_service.py`
- **Function:** `generate_recipe_with_llm(user_profile, meal_type, available_time)`
- OpenAI GPT-4o integration
- Generates personalized recipes based on:
  - User's dietary preferences and restrictions
  - Nutritional targets
  - Available ingredients
  - Cooking skill level
  - Cuisine preferences
  - Meal type and time constraints
- Returns structured JSON with recipe details

#### File: `backend/recipes/management/commands/import_usda_foods.py`
- Management command: `python manage.py import_usda_foods`
- Imports USDA FoodData Central JSON file
- Batch processing (1,000 foods per batch)
- Options:
  - `--limit N` - Import only N foods
  - `--batch-size N` - Batch size for bulk insert
- Parses nutrients and serving sizes
- Handles duplicates (skips by fdc_id)

### Frontend Services

#### File: `frontend/src/services/auth.ts`
- **authService:**
  - `register(email, username, password)` - Create account
  - `login(email, password)` - Authenticate user
  - `logout()` - Invalidate token
  - `isAuthenticated()` - Check login status
  - `getToken()` - Retrieve stored token

#### File: `frontend/src/services/profile.ts`
- **profileService:**
  - `getProfile()` - Fetch user profile
  - `updateProfile(data)` - Update profile fields

#### File: `frontend/src/services/recipes.ts`
- **recipeService:**
  - `generateRecipe(meal_type, available_time)` - Generate AI recipe
  - `getRecipes()` - Fetch all recipes
  - `deleteRecipe(id)` - Remove recipe

#### File: `frontend/src/services/mealPlanning.ts`
- **mealPlanningService:**
  - `getMealPlanByDate(date)` - Get/create meal plan for date
  - `updateMealSlot(id, data)` - Assign recipe or mark leftover
  - `clearMealSlot(id)` - Remove recipe from slot

#### File: `frontend/src/services/foodLogging.ts`
- **Functions:**
  - `searchFoods(query)` - Search USDA database
  - `getFoodLogs(date?)` - Get logs for date
  - `createFoodLog(data)` - Log food entry
  - `deleteFoodLog(id)` - Remove log entry
  - `getDailyTotals(date?)` - Get nutrition totals
  - `formatDate(date)` - Format date to YYYY-MM-DD
  - `getTodayDate()` - Get current date string

---

## Features by Phase

### Phase 1: Core Recipe Generation ✅
- User registration and authentication
- Profile management with preferences
- AI-powered recipe generation
- Recipe collection and management
- BMR/TDEE calculation

**Files Involved:**
- Backend: `users/`, `recipes/views.py`, `recipes/llm_service.py`
- Frontend: `RegisterPage`, `LoginPage`, `ProfilePage`, `GenerateRecipePage`, `RecipesPage`

### Phase 2: Weekly Meal Planning ✅
- 7-day meal planner
- Recipe assignment to meal slots
- Leftover tracking
- Week navigation
- Meal selection modal

**Files Involved:**
- Backend: `recipes/models.py` (MealPlan, MealSlot), `recipes/views.py`
- Frontend: `MealPlannerPage`, `WeeklyMealPlanner`, `MealSlotCard`, `MealSelectionModal`

### Phase 3: Food Logging & Tracking ✅
- USDA food database integration (1,000+ foods)
- Daily food logging
- Meal-by-meal tracking
- Nutrition totals and progress
- Date navigation
- Food search and selection

**Files Involved:**
- Backend: `recipes/models.py` (Food, FoodLog), `recipes/views.py`, `import_usda_foods.py`
- Frontend: `FoodLogPage`, `DailyFoodLog`, `FoodSearchModal`, `foodLogging.ts`

### Future Enhancements (Not Yet Implemented)
- Import full USDA database (452,998 foods)
- Barcode scanning
- Custom food creation
- Recipe favorites/ratings
- Meal plan templates
- Shopping list generation
- Nutrition reports and charts
- Export data to CSV/PDF
- Mobile app
- Social features (share recipes)

---

## Technology Stack

### Backend
- **Framework:** Django 4.2.11
- **API:** Django REST Framework
- **Database:** SQLite (development)
- **AI:** OpenAI GPT-4o
- **Authentication:** Token-based (DRF)
- **Python Version:** 3.9+

### Frontend
- **Framework:** React 18
- **Language:** TypeScript
- **Build Tool:** Vite
- **Routing:** React Router v6
- **UI Library:** shadcn/ui (Radix UI)
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios + Fetch API
- **Theme:** Light/Dark mode support

### External APIs
- **OpenAI GPT-4o** - Recipe generation
- **USDA FoodData Central** - Food database (offline JSON)

---

## API Authentication

All protected endpoints require authentication using Token-based authentication:

```
Authorization: Token {your_token_here}
```

Token is obtained from `/api/login/` or `/api/register/` endpoints and stored in localStorage on the frontend.

---

## Data Flow Examples

### Recipe Generation Flow
1. User fills form on `/generate` page
2. Frontend calls `POST /api/generate/`
3. Backend fetches user profile
4. Backend calls OpenAI API with profile context
5. AI generates personalized recipe
6. Backend saves recipe to database
7. Frontend displays recipe
8. User can save to collection

### Meal Planning Flow
1. User navigates to `/meal-planner`
2. Frontend calls `GET /api/meal-plans/by_date/?date=2025-10-18`
3. Backend creates meal plan if not exists
4. Frontend displays 21 meal slots (7 days × 3 meals)
5. User clicks "Add Meal" on a slot
6. Modal opens with recipe list
7. User selects recipe
8. Frontend calls `PATCH /api/meal-slots/{id}/`
9. Backend updates slot with recipe
10. Frontend refreshes to show assigned recipe

### Food Logging Flow
1. User navigates to `/food-log`
2. Frontend calls `GET /api/food-logs/?date=2025-10-18`
3. Frontend calls `GET /api/food-logs/daily_totals/?date=2025-10-18`
4. Displays logged foods and daily totals
5. User clicks "Add Food" for a meal
6. Modal opens, user searches for food
7. Frontend calls `GET /api/foods/search/?q=chicken`
8. User selects food, enters quantity
9. Modal calculates and displays macros
10. User clicks "Log Food"
11. Frontend calls `POST /api/food-logs/`
12. Backend auto-calculates macros and saves
13. Frontend refreshes to show new entry

---

## Environment Variables

### Backend (`backend/.env`)
```
SECRET_KEY=your-django-secret-key
DEBUG=True
OPENAI_API_KEY=your-openai-api-key
```

### Frontend
No environment variables required (API URL hardcoded to localhost:8000)

---

## Development Commands

### Backend
```bash
# Start server
cd backend
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Import USDA foods (limit 1000)
python manage.py import_usda_foods --limit 1000

# Import all USDA foods (452,998 - takes 30-60 min)
python manage.py import_usda_foods

# Create superuser
python manage.py createsuperuser
```

### Frontend
```bash
# Start dev server
cd frontend
npm run dev

# Install dependencies
npm install

# Add shadcn component
npx shadcn@latest add [component-name]
```

---

## Current Status

### Completed ✅
- ✅ User authentication and profile management
- ✅ AI recipe generation with personalization
- ✅ Recipe collection and management
- ✅ Weekly meal planning with calendar view
- ✅ USDA food database integration (1,000 foods)
- ✅ Daily food logging with macro tracking
- ✅ Dark mode support
- ✅ Responsive design

### In Progress 🚧
- None

### Planned 📋
- Full USDA database import (452,998 foods)
- Barcode scanning
- Custom foods
- Shopping lists
- Nutrition reports

---

**Last Updated:** October 29, 2025
**Version:** 1.0.0 (MVP Complete)
