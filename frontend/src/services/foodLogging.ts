/**
 * Food Logging API Service
 * Handles food search and daily food logging functionality
 */

import type {
  Food,
  FoodLog,
  FoodLogCreateRequest,
  DailyNutritionTotals
} from '@/types/api'

const API_BASE_URL = 'http://localhost:8000/api'

/**
 * Get authentication token from localStorage
 */
function getAuthToken(): string | null {
  return localStorage.getItem('token')
}

/**
 * Search for foods in the USDA database
 * @param query - Search query (minimum 2 characters)
 * @returns Array of matching foods (max 20 results)
 */
export async function searchFoods(query: string): Promise<Food[]> {
  if (!query || query.trim().length < 2) {
    throw new Error('Search query must be at least 2 characters')
  }

  const token = getAuthToken()
  if (!token) {
    throw new Error('Authentication required')
  }

  const response = await fetch(
    `${API_BASE_URL}/foods/search/?q=${encodeURIComponent(query)}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
    }
  )

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Failed to search foods')
  }

  return response.json()
}

/**
 * Get user's food logs for a specific date
 * @param date - Date in YYYY-MM-DD format (defaults to today)
 * @returns Array of food logs for the specified date
 */
export async function getFoodLogs(date?: string): Promise<FoodLog[]> {
  const token = getAuthToken()
  if (!token) {
    throw new Error('Authentication required')
  }

  let url = `${API_BASE_URL}/food-logs/`
  if (date) {
    url += `?date=${date}`
  }

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error('Failed to fetch food logs')
  }

  return response.json()
}

/**
 * Create a new food log entry
 * @param data - Food log creation data
 * @returns Created food log with calculated macros
 */
export async function createFoodLog(data: FoodLogCreateRequest): Promise<FoodLog> {
  const token = getAuthToken()
  if (!token) {
    throw new Error('Authentication required')
  }

  const response = await fetch(`${API_BASE_URL}/food-logs/`, {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Failed to create food log')
  }

  return response.json()
}

/**
 * Delete a food log entry
 * @param id - Food log ID to delete
 */
export async function deleteFoodLog(id: number): Promise<void> {
  const token = getAuthToken()
  if (!token) {
    throw new Error('Authentication required')
  }

  const response = await fetch(`${API_BASE_URL}/food-logs/${id}/`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Token ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Failed to delete food log')
  }
}

/**
 * Get daily nutrition totals for a specific date
 * @param date - Date in YYYY-MM-DD format (defaults to today)
 * @returns Daily totals and breakdown by meal type
 */
export async function getDailyTotals(date?: string): Promise<DailyNutritionTotals> {
  const token = getAuthToken()
  if (!token) {
    throw new Error('Authentication required')
  }

  let url = `${API_BASE_URL}/food-logs/daily_totals/`
  if (date) {
    url += `?date=${date}`
  }

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error('Failed to fetch daily totals')
  }

  return response.json()
}

/**
 * Format date to YYYY-MM-DD
 */
export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0]
}

/**
 * Get today's date in YYYY-MM-DD format
 */
export function getTodayDate(): string {
  return formatDate(new Date())
}
