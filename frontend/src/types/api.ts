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
  goal: string
  dietary_preferences: string
  created_at: string
  updated_at: string
}

export interface ProfileUpdateRequest {
  goal?: string
  dietary_preferences?: string
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
