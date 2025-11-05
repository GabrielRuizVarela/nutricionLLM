# NutriAI - AI-Powered Nutrition & Recipe Management System

A full-stack application that uses AI (via Ollama) to generate personalized recipes based on user preferences, dietary restrictions, and nutritional goals.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Deployment Guide](#local-deployment-guide)
  - [1. Ollama Setup](#1-ollama-setup)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Frontend Setup](#3-frontend-setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [API Documentation](#api-documentation)

---

## Features

### Core Functionality
- **User Authentication**: Secure registration and login system with token-based authentication
- **User Profiles**: Comprehensive profile management with personal info, dietary preferences, and nutritional targets
- **AI Recipe Generation**: Generate personalized recipes using Ollama-powered LLMs based on:
  - Meal type (breakfast, lunch, dinner, snack)
  - Available time
  - Dietary preferences (vegetarian, vegan, etc.)
  - Allergies and dislikes
  - Nutritional goals and targets
  - Available ingredients
  - Cuisine preferences
  - Cooking skill level
- **Recipe Management**: Save, view, edit, and delete generated recipes
- **Food Logging**: Track daily food intake with USDA FoodData Central integration
- **Meal Planning**: Create and manage weekly meal plans
- **Nutritional Tracking**: Monitor calories, protein, carbs, and fats
- **BMR/TDEE Calculations**: Automatic calculation based on user profile

### Advanced Features
- Recipe search and filtering
- Nutritional summaries
- Meal slot management
- Ingredient availability tracking

---

## Tech Stack

### Backend
- **Framework**: Django 4.2.11
- **API**: Django REST Framework 3.15.1
- **Database**: SQLite (development)
- **AI Integration**: Ollama via HTTP API
- **Testing**: pytest 8.1.1, pytest-django 4.8.0
- **Authentication**: Token-based authentication

### Frontend
- **Framework**: React 19.1.1
- **Build Tool**: Vite
- **Language**: TypeScript
- **UI Components**: Radix UI, Tailwind CSS
- **Forms**: React Hook Form with Zod validation
- **Routing**: React Router v7
- **HTTP Client**: Axios
- **Testing**: Vitest 3.2.4, Testing Library

### AI/LLM
- **LLM Runtime**: Ollama
- **Default Model**: qwen3:4b (configurable)
- **API**: OpenAI-compatible API

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python**: 3.9 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **Ollama**: Latest version
- **Git**: For cloning the repository

### System Requirements
- **OS**: macOS, Linux, or Windows
- **RAM**: 8GB minimum (16GB recommended for running larger LLM models)
- **Disk Space**: 10GB minimum (models can be large)

---

## Local Deployment Guide

### 1. Ollama Setup

Ollama is the LLM runtime that powers the recipe generation feature.

#### Step 1.1: Install Ollama

**macOS:**
```bash
# Download and install from official website
curl -fsSL https://ollama.com/install.sh | sh

# Or using Homebrew
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download the installer from [ollama.com](https://ollama.com/download)

#### Step 1.2: Start Ollama Service

```bash
# Start Ollama server (runs on http://localhost:11434 by default)
ollama serve
```

Keep this terminal open or run it in the background.

#### Step 1.3: Pull the Required Model

Open a new terminal and pull the model:

```bash
# Default model used in this project
ollama pull qwen3:4b

# Alternative models you can use:
# ollama pull llama3:8b        # Larger, more capable (requires more RAM)
# ollama pull mistral:7b        # Good balance
# ollama pull phi3:mini         # Smaller, faster
```

#### Step 1.4: Verify Ollama is Running

```bash
# Test the API
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:4b",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

You should receive a JSON response with the model's reply.

#### Model Recommendations

| Model | Size | RAM Required | Use Case |
|-------|------|--------------|----------|
| `qwen3:4b` | ~2.5GB | 8GB | **Default** - Fast, good quality |
| `phi3:mini` | ~2.2GB | 6GB | Fastest, smaller responses |
| `mistral:7b` | ~4.1GB | 12GB | Better reasoning |
| `llama3:8b` | ~4.7GB | 16GB | Highest quality |

---

### 2. Backend Setup

#### Step 2.1: Clone the Repository

```bash
git clone <repository-url>
cd nutricionLLM
```

#### Step 2.2: Create Python Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

#### Step 2.3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Step 2.4: Configure Ollama Settings (Optional)

The default configuration uses Ollama with `qwen3:4b`. If you want to use a different model:

```bash
# Edit backend/nutriai_project/settings.py
nano nutriai_project/settings.py
```

Find and modify these lines:
```python
# Ollama configuration
LLM_STUDIO_URL = "http://localhost:11434/v1/chat/completions"
LLM_STUDIO_MODEL = "qwen3:4b"  # Change to your preferred model
```

#### Step 2.5: Run Database Migrations

```bash
python manage.py migrate
```

This will create the SQLite database with all required tables.

#### Step 2.6: Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user for Django admin panel.

#### Step 2.7: Load USDA FoodData (Optional)

If you want to use the food logging feature with USDA data:

```bash
# Note: The FoodData_Central_branded_food_json_2025-04-24.json file
# is large (~3GB) and is not included in the repository
# Download it from: https://fdc.nal.usda.gov/download-datasets.html

# Place the file in the backend directory, then load it:
python manage.py shell
>>> from recipes.management.commands import load_food_data
>>> # Run the import script
```

---

### 3. Frontend Setup

#### Step 3.1: Install Node Dependencies

```bash
cd ../frontend  # From backend directory
npm install
```

#### Step 3.2: Configure API Endpoint (if needed)

The frontend is configured to connect to `http://localhost:8000/api` by default.

If you need to change this:
```bash
# Edit frontend/src/services/api.ts
nano src/services/api.ts
```

Modify the `API_BASE` constant:
```typescript
export const API_BASE = 'http://localhost:8000/api'
```

---

## Running the Application

You'll need **three** terminal windows:

### Terminal 1: Ollama Service

```bash
ollama serve
```

Keep this running. You should see:
```
Listening on 127.0.0.1:11434
```

### Terminal 2: Django Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python manage.py runserver
```

The backend will start at: **http://localhost:8000**

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### Terminal 3: React Frontend

```bash
cd frontend
npm run dev
```

The frontend will start at: **http://localhost:5173**

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### Access the Application

Open your browser and navigate to: **http://localhost:5173**

---

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=recipes --cov=users

# Run specific test file
python -m pytest recipes/test_recipe_crud.py

# Run tests excluding slow LLM tests
python -m pytest --ignore=recipes/test_llm_service.py --ignore=recipes/test_recipe_generation.py
```

**Current Test Status:**
- Total: 279 tests
- Passing: 278 tests
- Skipped: 1 test
- Coverage: ~95%

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run coverage
```

**Current Test Status:**
- Total: 267 tests
- Passing: 267 tests
- Coverage: 100%

---

## Project Structure

```
nutricionLLM/
├── backend/                    # Django backend
│   ├── nutriai_project/       # Django project settings
│   │   ├── settings.py        # Main configuration (Ollama config here)
│   │   ├── urls.py            # URL routing
│   │   └── wsgi.py
│   ├── recipes/               # Recipes app
│   │   ├── models.py          # Recipe, MealPlan, Food models
│   │   ├── views.py           # API endpoints
│   │   ├── serializers.py     # DRF serializers
│   │   ├── llm_service.py     # Ollama integration
│   │   └── tests/             # Recipe tests
│   ├── users/                 # Users app
│   │   ├── models.py          # User Profile model
│   │   ├── views.py           # Auth & profile endpoints
│   │   ├── serializers.py     # User serializers
│   │   └── tests/             # User tests
│   ├── db.sqlite3             # SQLite database
│   ├── manage.py              # Django management script
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── RecipeGenerator.tsx   # Main recipe generation UI
│   │   │   ├── ProfileForm.tsx       # User profile management
│   │   │   ├── RecipeList.tsx        # Recipe listing
│   │   │   └── ...
│   │   ├── services/          # API service layer
│   │   │   ├── recipes.ts     # Recipe API calls
│   │   │   ├── auth.ts        # Authentication
│   │   │   └── profile.ts     # Profile management
│   │   ├── pages/             # Page components
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # Entry point
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
│
└── README.md                   # This file
```

---

## Configuration

### Backend Configuration

#### Key Settings (backend/nutriai_project/settings.py)

```python
# Ollama Configuration
LLM_STUDIO_URL = "http://localhost:11434/v1/chat/completions"
LLM_STUDIO_MODEL = "qwen3:4b"

# Timezone
TIME_ZONE = 'America/Buenos_Aires'

# CORS (for local development)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Environment Variables (Optional)

Create a `.env` file in the backend directory:

```bash
# backend/.env
DEBUG=True
SECRET_KEY=your-secret-key-here
LLM_STUDIO_URL=http://localhost:11434/v1/chat/completions
LLM_STUDIO_MODEL=qwen3:4b
```

### Switching Between LLM Models

To use a different model:

1. Pull the model with Ollama:
   ```bash
   ollama pull llama3:8b
   ```

2. Update settings.py:
   ```python
   LLM_STUDIO_MODEL = "llama3:8b"
   ```

3. Restart the Django server

---

## Troubleshooting

### Ollama Issues

#### Issue: "Connection refused" when generating recipes

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# If not running, start it:
ollama serve
```

#### Issue: "Model not found"

**Solution:**
```bash
# List available models
ollama list

# Pull the required model
ollama pull qwen3:4b
```

#### Issue: Recipe generation is slow

**Solutions:**
1. Use a smaller model: `phi3:mini` or `qwen3:4b`
2. Ensure Ollama is using GPU acceleration (if available)
3. Check CPU/RAM usage - close unnecessary applications

#### Issue: Recipe generation returns incomplete data

**Solution:**
- Check the backend logs for detailed error messages
- The error message will now be displayed in the frontend
- Try using a larger model like `mistral:7b` for better JSON compliance

### Backend Issues

#### Issue: "No module named 'django'"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: Database errors

**Solution:**
```bash
# Reset the database
rm db.sqlite3
python manage.py migrate
```

#### Issue: CORS errors in browser console

**Solution:**
Check `CORS_ALLOWED_ORIGINS` in settings.py includes your frontend URL.

### Frontend Issues

#### Issue: "Cannot connect to backend"

**Solution:**
1. Verify backend is running on http://localhost:8000
2. Check `API_BASE` in `src/services/api.ts`
3. Check browser console for specific errors

#### Issue: npm install fails

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### General Issues

#### Issue: Port already in use

**Solutions:**
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 5173)
lsof -ti:5173 | xargs kill -9

# Ollama (port 11434)
lsof -ti:11434 | xargs kill -9
```

---

## API Documentation

### Authentication Endpoints

#### Register
```http
POST /api/register/
Content-Type: application/json

{
  "username": "user@example.com",
  "email": "user@example.com",
  "password": "password123"
}

Response: 201 Created
{
  "username": "user@example.com",
  "email": "user@example.com",
  "token": "abc123..."
}
```

#### Login
```http
POST /api/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

Response: 200 OK
{
  "token": "abc123..."
}
```

### Recipe Endpoints

#### Generate Recipe (uses Ollama)
```http
POST /api/recipes/generate/
Authorization: Token abc123...
Content-Type: application/json

{
  "meal_type": "dinner",
  "available_time": 30,
  "available_ingredients": "chicken, rice, broccoli"
}

Response: 200 OK
{
  "name": "Chicken Stir-Fry with Rice",
  "ingredients": "chicken breast, rice, broccoli, soy sauce, garlic",
  "steps": "1. Cook rice. 2. Season chicken. 3. Stir-fry vegetables...",
  "calories": 450,
  "protein": 35.0,
  "carbs": 55.0,
  "fats": 10.0,
  "prep_time_minutes": 25,
  "meal_type": "dinner"
}
```

#### Save Recipe
```http
POST /api/recetas/
Authorization: Token abc123...
Content-Type: application/json

{
  "name": "Chicken Stir-Fry",
  "ingredients": "...",
  "steps": "...",
  "calories": 450,
  "protein": 35.0,
  "carbs": 55.0,
  "fats": 10.0,
  "prep_time_minutes": 25,
  "meal_type": "dinner"
}

Response: 201 Created
```

#### List User's Recipes
```http
GET /api/recetas/
Authorization: Token abc123...

Response: 200 OK
[
  {
    "id": 1,
    "name": "Chicken Stir-Fry",
    "meal_type": "dinner",
    "calories": 450,
    ...
  }
]
```

### Profile Endpoints

#### Get Profile
```http
GET /api/profile/
Authorization: Token abc123...

Response: 200 OK
{
  "id": 1,
  "username": "user@example.com",
  "age": 30,
  "weight_kg": 70,
  "height_cm": 175,
  "goal": "lose weight",
  "dietary_preferences": "vegetarian",
  "bmr": 1650,
  "tdee": 2280,
  ...
}
```

#### Update Profile
```http
PATCH /api/profile/
Authorization: Token abc123...
Content-Type: application/json

{
  "goal": "build muscle",
  "dietary_preferences": "high protein",
  "daily_calorie_target": 2500
}

Response: 200 OK
```

---

## Contributing

### Running Tests Before Committing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

- **Backend**: Follow PEP 8
- **Frontend**: ESLint configuration included

---

## License

This project is for educational purposes.

---

## Support

For issues and questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Ollama logs: `ollama logs`
3. Check Django logs in the terminal running `manage.py runserver`
4. Check browser console for frontend errors

---

## Version History

- **v1.0.0** - Initial release with Ollama integration
  - Full recipe generation with AI
  - User authentication and profiles
  - Recipe management
  - Food logging
  - Meal planning
  - 278 backend tests passing
  - 267 frontend tests passing (100% coverage)
