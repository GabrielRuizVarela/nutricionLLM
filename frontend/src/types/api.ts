// Auth types
export interface RegisterRequest {
  email: string
  username: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  token: string
  user_id: number
  username: string
  email: string
}

export interface ErrorResponse {
  [key: string]: string[]
}

// Profile types
export interface Profile {
  id: number
  username: string
  email: string

  // Personal Information
  age?: number
  weight_kg?: number
  height_cm?: number
  gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say' | ''
  activity_level?: 'sedentary' | 'lightly_active' | 'moderately_active' | 'very_active' | 'extremely_active' | ''

  // Dietary Information
  goal?: 'lose_weight' | 'gain_weight' | 'maintain_weight' | 'gain_muscle' | 'improve_health' | ''
  dietary_preferences?: string
  allergies?: string
  dislikes?: string

  // Recipe Preferences
  cuisine_preferences?: string
  cooking_skill_level?: 'beginner' | 'intermediate' | 'advanced'
  spice_preference?: 'mild' | 'medium' | 'spicy'

  // Ingredient Management
  preferred_ingredients?: string
  available_ingredients?: string

  // Nutritional Targets
  daily_calorie_target?: number
  daily_protein_target?: number
  daily_carbs_target?: number
  daily_fats_target?: number

  // Calculated fields (read-only)
  bmr?: number | null
  tdee?: number | null

  // Timestamps
  created_at: string
  updated_at: string
}

export interface ProfileUpdateRequest {
  // Personal Information
  age?: number
  weight_kg?: number
  height_cm?: number
  gender?: string
  activity_level?: string

  // Dietary Information
  goal?: string
  dietary_preferences?: string
  allergies?: string
  dislikes?: string

  // Recipe Preferences
  cuisine_preferences?: string
  cooking_skill_level?: string
  spice_preference?: string

  // Ingredient Management
  preferred_ingredients?: string
  available_ingredients?: string

  // Nutritional Targets
  daily_calorie_target?: number
  daily_protein_target?: number
  daily_carbs_target?: number
  daily_fats_target?: number
}

// Recipe types
export interface RecipeGenerateRequest {
  meal_type: string
  available_time: number
}

export interface Recipe {
  id?: number
  name: string
  ingredients: string
  steps: string
  calories: number
  protein: number
  carbs: number
  fats: number
  prep_time_minutes: number
  meal_type: string
  created_at?: string
}

export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack'

// Meal Planning types
export interface MealSlot {
  id: number
  meal_plan: number
  day_of_week: number // 0 = Monday, 6 = Sunday
  day_name: string // Display name (e.g., "Monday")
  meal_type: 'breakfast' | 'lunch' | 'dinner'
  meal_name: string // Display name (e.g., "Breakfast")
  recipe: number | null
  recipe_detail: Recipe | null
  is_leftover: boolean
  original_meal_slot: number | null
  notes: string
  date: string // YYYY-MM-DD format
  created_at: string
  updated_at: string
}

export interface MealPlan {
  id: number
  user: number
  week_start_date: string // YYYY-MM-DD (Monday)
  week_end_date: string // YYYY-MM-DD (Sunday)
  meal_slots: MealSlot[]
  created_at: string
  updated_at: string
}

export interface MealSlotUpdateRequest {
  recipe?: number | null
  is_leftover?: boolean
  original_meal_slot?: number | null
  notes?: string
}

// Food Database types
export interface Food {
  id: number
  fdc_id: number
  description: string
  brand_owner: string
  barcode: string
  ingredients: string
  category: string
  serving_size: number | null
  serving_size_unit: string
  calories: number | null
  protein: number | null
  carbs: number | null
  fats: number | null
  fiber: number | null
  sugars: number | null
  sodium: number | null
}

export interface FoodLog {
  id: number
  user: number
  food: number
  food_detail: Food
  date: string // YYYY-MM-DD
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  meal_type_display: string
  quantity_grams: number
  calories: number
  protein: number
  carbs: number
  fats: number
  created_at: string
  updated_at: string
}

export interface FoodLogCreateRequest {
  food: number
  date: string // YYYY-MM-DD
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  quantity_grams: number
}

export interface DailyNutritionTotals {
  date: string
  totals: {
    calories: number
    protein: number
    carbs: number
    fats: number
  }
  by_meal: {
    [mealType: string]: {
      calories: number | null
      protein: number | null
      carbs: number | null
      fats: number | null
    }
  }
}
