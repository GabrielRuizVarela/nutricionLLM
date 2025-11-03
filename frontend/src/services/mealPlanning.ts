/**
 * API service for meal planning operations
 */
import axios from 'axios'
import type { MealPlan, MealSlot, MealSlotUpdateRequest } from '@/types/api'

const API_URL = 'http://localhost:8000/api'

// Get auth token from localStorage
const getAuthToken = () => localStorage.getItem('token')

// Create axios instance with auth header
const apiClient = axios.create({
  baseURL: API_URL,
})

apiClient.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

export const mealPlanningService = {
  /**
   * Get the current week's meal plan (auto-creates if doesn't exist)
   */
  getCurrentWeek: async (): Promise<MealPlan> => {
    const response = await apiClient.get<MealPlan>('/meal-plans/current/')
    return response.data
  },

  /**
   * Get meal plan for a specific date
   * @param date YYYY-MM-DD format
   */
  getByDate: async (date: string): Promise<MealPlan> => {
    const response = await apiClient.get<MealPlan>(`/meal-plans/by_date/?date=${date}`)
    return response.data
  },

  /**
   * List all meal plans for the user
   */
  listMealPlans: async (): Promise<MealPlan[]> => {
    const response = await apiClient.get<MealPlan[]>('/meal-plans/')
    return response.data
  },

  /**
   * Get a specific meal plan by ID
   */
  getMealPlan: async (id: number): Promise<MealPlan> => {
    const response = await apiClient.get<MealPlan>(`/meal-plans/${id}/`)
    return response.data
  },

  /**
   * Update a meal slot (assign recipe, mark as leftover, etc.)
   */
  updateMealSlot: async (id: number, data: MealSlotUpdateRequest): Promise<MealSlot> => {
    const response = await apiClient.patch<MealSlot>(`/meal-slots/${id}/`, data)
    return response.data
  },

  /**
   * Clear a meal slot (remove recipe assignment)
   */
  clearMealSlot: async (id: number): Promise<MealSlot> => {
    const response = await apiClient.patch<MealSlot>(`/meal-slots/${id}/`, {
      recipe: null,
      is_leftover: false,
      original_meal_slot: null,
      notes: ''
    })
    return response.data
  },

  /**
   * Delete a meal plan
   */
  deleteMealPlan: async (id: number): Promise<void> => {
    await apiClient.delete(`/meal-plans/${id}/`)
  },
}
