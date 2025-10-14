# NutriAI Backend - TDD Implementation

## Overview
This backend was developed following **Test-Driven Development (TDD)** principles. All 8 user stories from the requirements have been implemented with comprehensive test coverage.

## TDD Approach

### RED → GREEN → REFACTOR
1. **RED**: Write failing tests first based on acceptance criteria
2. **GREEN**: Implement minimal code to make tests pass
3. **REFACTOR**: Improve code while keeping tests green

## Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── pytest.ini
├── nutriai_project/
│   ├── settings.py (DRF + Token Auth configured)
│   └── urls.py
├── users/
│   ├── models.py (Profile model)
│   ├── serializers.py (RegisterSerializer, ProfileSerializer)
│   ├── views.py (Register, Login, Logout, Profile)
│   ├── urls.py
│   ├── test_registration.py (10 tests)
│   ├── test_login.py (10 tests)
│   ├── test_logout.py (6 tests)
│   └── test_profile.py (11 tests)
└── recipes/
    ├── models.py (Receta model)
    ├── serializers.py (RecipeGeneration, Receta)
    ├── views.py (RecipeGeneration, RecetaViewSet)
    ├── llm_service.py (LLM integration)
    ├── urls.py
    ├── test_recipe_generation.py (11 tests)
    └── test_recipe_crud.py (16 tests)
```

## User Stories Implementation

### ✅ US1: User Registration
**Files:**
- Tests: `users/test_registration.py` (10 tests)
- Implementation: `users/views.py::RegisterView`

**Test Coverage:**
- Valid registration with email and password
- User + Profile auto-creation
- Password validation (min 8 chars)
- Email validation
- Duplicate email detection
- Password hashing verification
- Token return for auto-login
- Missing fields validation

**API Endpoint:** `POST /api/auth/register/`

---

### ✅ US2: User Login
**Files:**
- Tests: `users/test_login.py` (10 tests)
- Implementation: `users/views.py::LoginView`

**Test Coverage:**
- Successful login with valid credentials
- User info return with token
- Incorrect password handling
- Incorrect email handling
- Required fields validation
- Token authentication
- Token consistency across logins

**API Endpoint:** `POST /api/auth/login/`

---

### ✅ US3: User Logout
**Files:**
- Tests: `users/test_logout.py` (6 tests)
- Implementation: `users/views.py::LogoutView`

**Test Coverage:**
- Successful logout
- Token deletion from database
- Authentication requirement
- Protected routes inaccessible after logout
- Already logged out token handling

**API Endpoint:** `POST /api/auth/logout/`

---

### ✅ US4: Profile Management
**Files:**
- Tests: `users/test_profile.py` (11 tests)
- Implementation: `users/views.py::ProfileView`

**Test Coverage:**
- Profile retrieval
- Auto-creation on registration
- Goal field update
- Dietary preferences update
- Both fields simultaneous update
- Data persistence
- Authentication requirement
- Empty values allowed
- User isolation (can't view others)

**API Endpoints:**
- `GET /api/profile/`
- `PATCH /api/profile/`

---

### ✅ US5: Generate Recipe Using LLM
**Files:**
- Tests: `recipes/test_recipe_generation.py` (11 tests)
- Implementation:
  - `recipes/llm_service.py::LLMService`
  - `recipes/views.py::RecipeGenerationView`

**Test Coverage:**
- Successful generation with valid LLM response
- Meal type requirement
- Available time requirement
- User profile data usage
- Meal type choices validation
- Malformed JSON retry logic
- Failure after two attempts
- Authentication requirement
- Optional ingredients field
- Correct model and temperature parameters

**API Endpoint:** `POST /api/recipes/generate/`

**LLM Integration:**
- URL: `http://localhost:1234/v1/chat/completions`
- Model: `llama3:8b`
- Temperature: `0.4`
- Retry logic with correction prompt

---

### ✅ US6-7: View & Save Recipe
**Files:**
- Tests: `recipes/test_recipe_crud.py` (8 save tests)
- Implementation: `recipes/views.py::RecetaViewSet`

**Test Coverage:**
- Save with valid data
- User-recipe linking
- Success response
- Authentication requirement
- Required fields validation
- Meal type validation
- Positive values validation

**API Endpoint:** `POST /api/recetas/`

---

### ✅ US8: View Saved Recipes List
**Files:**
- Tests: `recipes/test_recipe_crud.py` (8 list tests)
- Implementation: `recipes/views.py::RecetaViewSet`

**Test Coverage:**
- List user recipes
- User isolation (only own recipes)
- Ordering (newest first)
- Essential info inclusion
- Recipe detail view
- Authentication requirement
- Cannot view others' recipes

**API Endpoints:**
- `GET /api/recetas/` - List
- `GET /api/recetas/{id}/` - Detail

---

## Test Statistics

### Total Tests: 64
- User Registration: 10 tests
- User Login: 10 tests
- User Logout: 6 tests
- Profile Management: 11 tests
- Recipe Generation: 11 tests
- Recipe Saving: 8 tests
- Recipe List: 8 tests

### Test Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest users/test_registration.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run only user tests
pytest users/ -v

# Run only recipe tests
pytest recipes/ -v
```

## Database Models

### Profile Model
```python
class Profile(models.Model):
    user = OneToOneField(User)
    goal = TextField(blank=True)
    dietary_preferences = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Receta Model
```python
class Receta(models.Model):
    user = ForeignKey(User)
    nombre = CharField(max_length=200)
    ingredientes_texto = TextField()
    pasos_texto = TextField()
    calorias = PositiveIntegerField()
    proteinas = FloatField()
    carbohidratos = FloatField()
    grasas = FloatField()
    tiempo_min = PositiveIntegerField()
    tipo = CharField(choices=[...])  # desayuno, almuerzo, cena, snack
    created_at = DateTimeField(auto_now_add=True)
```

## Authentication

**Method:** Token-based authentication using Django REST Framework

**Headers:**
```
Authorization: Token <user-token>
```

**Token Management:**
- Obtained on registration/login
- Stored in database (authtoken_token table)
- Deleted on logout
- Required for all protected endpoints

## Dependencies

```
Django==4.2.11
djangorestframework==3.15.1
httpx==0.27.0
pytest==8.1.1
pytest-django==4.8.0
factory-boy==3.3.0
responses==0.25.0
python-dotenv==1.0.1
django-cors-headers==4.3.1
```

## Setup Instructions

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run tests
pytest

# Run development server
python manage.py runserver
```

## API Documentation

### Base URL
`http://localhost:8000/api`

### Endpoints Summary

**Authentication:**
- `POST /auth/register/` - Register new user
- `POST /auth/login/` - Login user
- `POST /auth/logout/` - Logout user (requires auth)

**Profile:**
- `GET /profile/` - Get user profile (requires auth)
- `PATCH /profile/` - Update profile (requires auth)

**Recipes:**
- `POST /recipes/generate/` - Generate recipe (requires auth)
- `POST /recetas/` - Save recipe (requires auth)
- `GET /recetas/` - List user recipes (requires auth)
- `GET /recetas/{id}/` - Get recipe detail (requires auth)

## TDD Benefits Demonstrated

1. **Confidence in Code**: All features verified by tests
2. **Regression Prevention**: Tests catch breaking changes
3. **Documentation**: Tests serve as living documentation
4. **Design Improvement**: TDD led to cleaner architecture
5. **Faster Debugging**: Failing tests pinpoint issues
6. **Refactoring Safety**: Can improve code with confidence

## Next Steps

1. ✅ Run all tests to verify GREEN status
2. 🔄 Initialize React frontend with Vite + TypeScript
3. 🔄 Write frontend component tests
4. 🔄 Implement frontend integration
5. 🔄 End-to-end testing

---

**Generated using TDD methodology**
**All acceptance criteria from requirements.md verified through automated tests**
