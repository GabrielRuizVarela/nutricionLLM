/**
 * Frontend test utilities
 * Provides custom render functions, mock data factories, and helper functions
 */

import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@/components/ThemeProvider'
import type {
  User,
  Profile,
  Recipe,
  MealPlan,
  MealSlot,
  Food,
  FoodLog,
  DailyNutritionTotals
} from '@/types/api'

// ========== CUSTOM RENDER FUNCTIONS ==========

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialRoute?: string
}

/**
 * Custom render with all providers (Router, Theme, etc.)
 */
export function renderWithProviders(
  ui: ReactElement,
  {
    initialRoute = '/',
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  window.history.pushState({}, 'Test page', initialRoute)

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <ThemeProvider defaultTheme="light" storageKey="test-ui-theme">
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </ThemeProvider>
    )
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

/**
 * Setup localStorage with auth token
 */
export function setupAuthToken(token: string = 'test-token-12345') {
  localStorage.setItem('token', token)
}

/**
 * Clear all localStorage
 */
export function clearLocalStorage() {
  localStorage.clear()
}

/**
 * Setup authenticated state
 */
export function setupAuth() {
  setupAuthToken()
  return 'test-token-12345'
}

// ========== MOCK DATA FACTORIES ==========

let userIdCounter = 1
let recipeIdCounter = 1
let mealPlanIdCounter = 1
let mealSlotIdCounter = 1
let foodIdCounter = 1
let foodLogIdCounter = 1

/**
 * Create a mock user
 */
export function createMockUser(overrides: Partial<User> = {}): User {
  const id = userIdCounter++
  return {
    id,
    username: `testuser${id}`,
    email: `testuser${id}@example.com`,
    ...overrides
  }
}

/**
 * Create a mock profile
 */
export function createMockProfile(overrides: Partial<Profile> = {}): Profile {
  const user = createMockUser()
  return {
    id: user.id,
    username: user.username,
    email: user.email,
    age: 30,
    weight_kg: 70,
    height_cm: 175,
    gender: 'male',
    activity_level: 'moderately_active',
    goal: 'maintain_weight',
    dietary_preferences: 'No restrictions',
    allergies: '',
    dislikes: '',
    cuisine_preferences: 'Italian, Mexican',
    cooking_skill_level: 'intermediate',
    spice_preference: 'medium',
    preferred_ingredients: 'chicken, rice, vegetables',
    available_ingredients: 'onions, garlic, olive oil',
    daily_calorie_target: 2000,
    daily_protein_target: 150,
    daily_carbs_target: 200,
    daily_fats_target: 65,
    bmr: 1680,
    tdee: 2310,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...overrides
  }
}

/**
 * Create a mock recipe
 */
export function createMockRecipe(overrides: Partial<Recipe> = {}): Recipe {
  const id = recipeIdCounter++
  return {
    id,
    name: `Test Recipe ${id}`,
    ingredients: 'Ingredient 1\nIngredient 2\nIngredient 3',
    steps: 'Step 1\nStep 2\nStep 3',
    calories: 450,
    protein: 30,
    carbs: 45,
    fats: 15,
    prep_time_minutes: 30,
    meal_type: 'lunch',
    created_at: '2024-01-01T00:00:00Z',
    ...overrides
  }
}

/**
 * Create multiple mock recipes
 */
export function createMockRecipes(count: number, overrides: Partial<Recipe> = {}): Recipe[] {
  return Array.from({ length: count }, () => createMockRecipe(overrides))
}

/**
 * Create a mock meal slot
 */
export function createMockMealSlot(overrides: Partial<MealSlot> = {}): MealSlot {
  const id = mealSlotIdCounter++
  return {
    id,
    meal_plan: 1,
    day_of_week: 0,
    day_name: 'Monday',
    meal_type: 'breakfast',
    meal_name: 'Breakfast',
    recipe: null,
    recipe_detail: null,
    is_leftover: false,
    original_meal_slot: null,
    notes: '',
    date: '2024-01-01',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...overrides
  }
}

/**
 * Create a complete week of meal slots (21 slots)
 */
export function createMockWeekSlots(mealPlanId: number = 1): MealSlot[] {
  const slots: MealSlot[] = []
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  const meals: Array<['breakfast' | 'lunch' | 'dinner', string]> = [
    ['breakfast', 'Breakfast'],
    ['lunch', 'Lunch'],
    ['dinner', 'Dinner']
  ]

  days.forEach((dayName, dayIndex) => {
    meals.forEach(([mealType, mealName]) => {
      slots.push(createMockMealSlot({
        meal_plan: mealPlanId,
        day_of_week: dayIndex,
        day_name: dayName,
        meal_type: mealType,
        meal_name: mealName,
        date: `2024-01-0${dayIndex + 1}`
      }))
    })
  })

  return slots
}

/**
 * Create a mock meal plan
 */
export function createMockMealPlan(overrides: Partial<MealPlan> = {}): MealPlan {
  const id = mealPlanIdCounter++
  return {
    id,
    user: 1,
    week_start_date: '2024-01-01',
    week_end_date: '2024-01-07',
    meal_slots: createMockWeekSlots(id),
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...overrides
  }
}

/**
 * Create a mock food item
 */
export function createMockFood(overrides: Partial<Food> = {}): Food {
  const id = foodIdCounter++
  return {
    id,
    fdc_id: 100000 + id,
    description: `Test Food ${id}`,
    brand_owner: 'Test Brand',
    barcode: `12345678${id.toString().padStart(4, '0')}`,
    ingredients: 'Test ingredients',
    category: 'Test Category',
    serving_size: 100,
    serving_size_unit: 'g',
    calories: 200,
    protein: 10,
    carbs: 25,
    fats: 8,
    fiber: 3,
    sugars: 5,
    sodium: 150,
    ...overrides
  }
}

/**
 * Create multiple mock foods
 */
export function createMockFoods(count: number, overrides: Partial<Food> = {}): Food[] {
  return Array.from({ length: count }, () => createMockFood(overrides))
}

/**
 * Create a mock food log entry
 */
export function createMockFoodLog(overrides: Partial<FoodLog> = {}): FoodLog {
  const id = foodLogIdCounter++
  const food = createMockFood()
  return {
    id,
    user: 1,
    food: food.id,
    food_detail: food,
    date: '2024-01-01',
    meal_type: 'breakfast',
    meal_type_display: 'Breakfast',
    quantity_grams: 100,
    calories: 200,
    protein: 10,
    carbs: 25,
    fats: 8,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...overrides
  }
}

/**
 * Create mock daily nutrition totals
 */
export function createMockDailyTotals(overrides: Partial<DailyNutritionTotals> = {}): DailyNutritionTotals {
  return {
    date: '2024-01-01',
    totals: {
      calories: 1850,
      protein: 125,
      carbs: 200,
      fats: 65
    },
    by_meal: {
      breakfast: { calories: 450, protein: 30, carbs: 50, fats: 15 },
      lunch: { calories: 650, protein: 45, carbs: 70, fats: 22 },
      dinner: { calories: 750, protein: 50, carbs: 80, fats: 28 },
      snack: { calories: null, protein: null, carbs: null, fats: null }
    },
    ...overrides
  }
}

// ========== HELPER FUNCTIONS ==========

/**
 * Wait for async updates
 */
export function waitForAsync() {
  return new Promise(resolve => setTimeout(resolve, 0))
}

/**
 * Get today's date in YYYY-MM-DD format
 */
export function getTodayDate(): string {
  return new Date().toISOString().split('T')[0]
}

/**
 * Get Monday of current week
 */
export function getThisMonday(): string {
  const today = new Date()
  const dayOfWeek = today.getDay()
  const monday = new Date(today)
  monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1))
  return monday.toISOString().split('T')[0]
}

/**
 * Format date offset from today
 */
export function getDateOffset(daysOffset: number): string {
  const date = new Date()
  date.setDate(date.getDate() + daysOffset)
  return date.toISOString().split('T')[0]
}

/**
 * Create meal type display name
 */
export function getMealTypeDisplay(mealType: string): string {
  const displays: Record<string, string> = {
    breakfast: 'Breakfast',
    lunch: 'Lunch',
    dinner: 'Dinner',
    snack: 'Snacks'
  }
  return displays[mealType] || mealType
}

/**
 * Reset all ID counters (useful between tests)
 */
export function resetIdCounters() {
  userIdCounter = 1
  recipeIdCounter = 1
  mealPlanIdCounter = 1
  mealSlotIdCounter = 1
  foodIdCounter = 1
  foodLogIdCounter = 1
}

// ========== CUSTOM MATCHERS ==========

/**
 * Check if element has accessible name
 */
export function hasAccessibleName(element: HTMLElement, name: string): boolean {
  const accessibleName = element.getAttribute('aria-label') || element.textContent
  return accessibleName?.includes(name) || false
}

// ========== EXPORT ALL ==========

export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'
