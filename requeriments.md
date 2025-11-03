# NutriAI MVP – User Stories with Acceptance Criteria

## 1. User Registration

**As a** new user,  
**I want to** register with email and password,  
**so that** I can create an account and use the application.

### Acceptance Criteria
- The registration form requires a valid email and a password (minimum 8 characters).
- If the email is already registered, the system displays: "An account with this email already exists."
- Upon successful registration, a Django `User` and an associated `Profile` are created.
- The user is automatically logged in and redirected to the recipe generation form.
- Passwords are stored hashed (never in plain text).

---

## 2. User Login

**As a** registered user,  
**I want to** log in with my credentials,  
**so that** I can access my recipes and generate new ones.

### Acceptance Criteria
- The login form requires email and password.
- Invalid credentials display: "Incorrect email or password."
- On successful login, the frontend receives an authentication token (DRF token or JWT).
- The token is stored in `localStorage` for subsequent API requests.
- The user is redirected to the recipe generation form.

---

## 3. User Logout

**As a** logged-in user,  
**I want to** log out at any time,  
**so that** I can protect my privacy on shared devices.

### Acceptance Criteria
- A "Log out" button is visible in the navigation bar when authenticated.
- Clicking it removes the authentication token from `localStorage`.
- The user is redirected to the login page.
- Protected routes are no longer accessible without re-authentication.

---

## 4. Complete/Edit User Profile

**As a** user,  
**I want to** complete my profile with a nutritional goal and dietary preferences,  
**so that** generated recipes are personalized.

### Acceptance Criteria
- On first login or from the "My Profile" page, the user sees a form with:
  - A text field for `goal` (e.g., "lose weight", "gain muscle")
  - A text field for `dietary_preferences` (e.g., "vegetarian, gluten-free")
- These values are saved in the `Profile` model linked to the user.
- The user can edit these fields at any time.
- Updated profile data is used in subsequent recipe generation prompts.

---

## 5. Generate Recipe Using LLM

**As a** user,  
**I want to** fill out a form and generate a personalized recipe using an LLM,  
**so that** I don’t have to think about what to cook.

### Acceptance Criteria
- The form includes:
  - A dropdown for `meal_type`: "desayuno", "almuerzo", "cena", or "snack"
  - A numeric input for `available_time` (in minutes)
  - An optional text field for `available_ingredients`
- On submission, a loading state shows: "Generating recipe…"
- The backend constructs a prompt using:
  - User’s `goal` and `dietary_preferences` (from Profile)
  - Form inputs (`meal_type`, `available_time`, `available_ingredients`)
- The system sends a POST request to LLM Studio at `http://localhost:1234/v1/chat/completions` with the following payload:

```json
{
  "model": "llama3:8b",
  "messages": [
    {
      "role": "user",
      "content": "Eres un asistente nutricional experto. Genera una receta en formato JSON con EXACTAMENTE estos campos:\n- nombre (string)\n- ingredientes (string, lista separada por comas)\n- pasos (string, pasos numerados separados por puntos)\n- calorias (int)\n- proteinas (float)\n- carbohidratos (float)\n- grasas (float)\n- tiempo_min (int)\n- tipo (string: desayuno, almuerzo, cena o snack)\n\nContexto del usuario:\n- Objetivo: [goal]\n- Preferencias: [dietary_preferences]\n- Tipo de comida: [meal_type]\n- Tiempo disponible: [available_time] minutos\n- Ingredientes disponibles: [available_ingredients]\n\nResponde SOLO con el objeto JSON. Nada de texto adicional."
    }
  ],
  "temperature": 0.4
}
```

- The response is parsed and validated against the expected recipe schema.
- If validation fails, a second LLM call is made with a correction prompt:
  > "The following text contains a recipe but is not valid JSON. Extract the information and output ONLY a valid JSON object with these fields: nombre, ingredientes, pasos, calorias, proteinas, carbohidratos, grasas, tiempo_min, tipo. Text: '[original_response]'"
- If both attempts fail, the frontend displays: "Could not generate a recipe. Please try again."

---

## 6. View Generated Recipe

**As a** user,  
**I want to** see the generated recipe with all its details,  
**so that** I can cook it.

### Acceptance Criteria
- The recipe is displayed with:
  - **Name** (prominently)
  - **Ingredients** as plain text (e.g., "1 avocado, 2 eggs, salt")
  - **Steps** as plain text (e.g., "1. Boil eggs. 2. Slice avocado.")
  - **Macronutrients**: calories (int), protein (float), carbs (float), fats (float)
  - **Prep time** (e.g., "10 min")
  - **Meal type** (e.g., "Lunch")
- The UI is clean and responsive (mobile-friendly).
- A "Save Recipe" button appears below the recipe.

---

## 7. Save Recipe

**As a** user,  
**I want to** save the generated recipe,  
**so that** I can access it later.

### Acceptance Criteria
- Clicking "Save Recipe" sends a POST request to `/api/recetas/` with the recipe data.
- The backend creates a `Receta` object in the database linked to the current user.
- A success message is shown: "Recipe saved."
- The recipe appears immediately in the user’s saved recipes list (without page reload).

**Expected JSON structure for saving:**
```json
{
  "nombre": "Lentil Salad",
  "ingredientes_texto": "1 cup cooked lentils, 1 cucumber, 2 tomatoes, olive oil, lemon",
  "pasos_texto": "1. Drain lentils. 2. Chop vegetables. 3. Mix with oil and lemon.",
  "calorias": 320,
  "proteinas": 18.5,
  "carbohidratos": 45.0,
  "grasas": 8.2,
  "tiempo_min": 10,
  "tipo": "almuerzo"
}
```

---

## 8. View Saved Recipes List

**As a** user,  
**I want to** see a list of my saved recipes,  
**so that** I can reuse them.

### Acceptance Criteria
- A "My Recipes" link is available in the navigation.
- The list is ordered from most recent to oldest.
- Each item shows: recipe name, meal type, and creation date.
- Clicking a recipe opens its detailed view (same as generated recipe view).
- Only recipes belonging to the current user are displayed.

---

## Technical Notes

- **Frontend**: React (Vite + TypeScript), Axios, React Router
- **Backend**: Django 5, Django REST Framework, httpx
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Token-based (DRF TokenAuthentication)
- **LLM Integration**: LLM Studio running locally at `http://localhost:1234`
- **Recipe Model Fields**:
  - `nombre` (CharField)
  - `ingredientes_texto` (TextField)
  - `pasos_texto` (TextField)
  - `calorias` (PositiveIntegerField)
  - `proteinas`, `carbohidratos`, `grasas` (FloatField)
  - `tiempo_min` (PositiveIntegerField)
  - `tipo` (CharField with choices)
  - `user` (ForeignKey to User)


Story 1 – Log Daily Foods & Track Macros

Acceptance Criteria

User can search and select foods from a USDA-backed database.

User can add or remove foods from their daily log.

Each food entry displays:

Name

Quantity (grams or units)

Auto-calculated macros (calories, protein, carbs, fats)

Daily totals update in real time as foods are added/removed.

Logs are stored per date and can be viewed/edited for past or future dates.

Data persists across sessions (no loss on refresh).

Story 2 – Set & Adjust Nutrition Goals

Acceptance Criteria

User can set or edit daily targets for calories, protein, carbs, and fats in their profile.

Default goals are auto-calculated from user stats (age, weight, goal type).

Dashboard shows progress bars or ratios (e.g., “Protein: 90g / 120g”).

Goals apply to all future dates unless explicitly overridden for a specific day.

Updated goals immediately reflect in macro tracking displays.

Story 3 – Create a Blank Weekly Meal Plan

Acceptance Criteria

System displays a 7×3 grid (days: Mon–Sun × meals: breakfast, lunch, dinner).

Each cell shows an “Add meal” button when empty.

User can navigate to past or future weeks.

Week navigation updates the grid and data persistently.

Grid layout remains responsive across desktop and mobile.

Story 4 – Assign Recipes to Meal Slots

Acceptance Criteria

Clicking “Add meal” opens a modal or panel offering:

User’s saved recipes, and

A “Generate new recipe” option (via LLM).

Assigned meals display:

Recipe name

Calories

Prep time

Assigning a recipe updates that day’s macro totals automatically.

Assigned recipes are persisted per week/day/meal slot.

Reassigning or removing meals immediately updates displayed macros.

Story 5 – Manage Preferred & Available Ingredients

Acceptance Criteria

User profile includes two editable lists:

Preferred ingredients

Available ingredients

Both lists support:

Tag or comma-separated entry

Add/remove/edit actions

Recipe generation prompts always include preferred ingredients.

Recipe generation prioritizes available ingredients.

LLM prompts explicitly include:

“Use these preferred ingredients: [preferred_list]”

“Prioritize these available ingredients: [available_list]”

Lists persist across sessions and can be updated anytime.

Story 6 – Auto-Fill Plan Based on Ingredients

Acceptance Criteria

Clicking “Auto-fill week” triggers generation of 21 meals (7 days × 3 meals).

Each generated meal uses:

User’s nutrition goals (to fill remaining macros)

Preferred and available ingredient lists

Meal type context (e.g., breakfast vs. dinner)

Generation failures mark the slot as empty with error indicator.

Successfully generated meals are saved to the recipe library.

The grid updates to show new meals immediately after generation.

User can edit or replace any auto-filled meal manually.

Story 7 – Generate Shopping List from Plan

Acceptance Criteria

System aggregates all ingredients from assigned recipes for the selected week.

Ingredients are grouped by category (e.g., produce, dairy, pantry).

Quantities are summed and normalized (e.g., “chicken breast: 1200g”).

Items already in Available ingredients list are marked as “✅ In pantry.”

User can export the shopping list (PDF, CSV, or text).

Any changes to the plan auto-refresh the list.

Story 8 – Adjust Plan Based on Leftovers

Acceptance Criteria

When adding a meal, user can select “Use leftovers from [Day]”.

Leftover meals:

Show a reuse icon

Contribute no new ingredients to the shopping list

Still count macros toward daily totals

Selecting leftovers links to the original recipe for quick reference.

Removing or changing the original recipe updates linked leftover meals.

Leftover status persists across sessions and exports correctly to the plan view.