/**
 * Tests for foodLogging service
 * Tests API integration for food search and logging operations
 */

import { describe, it, expect, vi, beforeEach, afterEach, beforeAll, afterAll } from 'vitest'
import {
  searchFoods,
  getFoodLogs,
  createFoodLog,
  deleteFoodLog,
  getDailyTotals,
  formatDate,
  getTodayDate
} from './foodLogging'
import { createMockFood, createMockFoodLog, createMockDailyTotals, setupAuth, clearLocalStorage } from '@/test/utils'
import { server } from '@/test/mocks/server'

// Mock fetch
const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

describe('foodLogging Service', () => {
  // Disable MSW for these tests since we're mocking fetch directly
  beforeAll(() => {
    server.close()
  })

  afterAll(() => {
    server.listen({ onUnhandledRequest: 'error' })
  })

  beforeEach(() => {
    vi.clearAllMocks()
    setupAuth()
  })

  afterEach(() => {
    clearLocalStorage()
  })

  describe('searchFoods', () => {
    it('searches foods with valid query', async () => {
      const mockFoods = [createMockFood()]
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockFoods
      } as Response)

      const result = await searchFoods('chicken')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/foods/search/?q=chicken',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Token test-token-12345'
          })
        })
      )
      expect(result).toEqual(mockFoods)
    })

    it('URL encodes search query', async () => {
      const mockFoods = [createMockFood()]
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockFoods
      } as Response)

      await searchFoods('chicken breast')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('chicken%20breast'),
        expect.any(Object)
      )
    })

    it('throws error for queries less than 2 characters', async () => {
      await expect(searchFoods('c')).rejects.toThrow('Search query must be at least 2 characters')
      expect(mockFetch).not.toHaveBeenCalled()
    })

    it('throws error for empty query', async () => {
      await expect(searchFoods('')).rejects.toThrow('Search query must be at least 2 characters')
    })

    it('throws error when not authenticated', async () => {
      clearLocalStorage()

      await expect(searchFoods('chicken')).rejects.toThrow('Authentication required')
    })

    it('handles API errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        json: async () => ({ error: 'Food not found' })
      } as Response)

      await expect(searchFoods('chicken')).rejects.toThrow('Food not found')
    })

    it('returns array of foods', async () => {
      const mockFoods = [
        createMockFood({ description: 'Food 1' }),
        createMockFood({ description: 'Food 2' })
      ]
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockFoods
      } as Response)

      const result = await searchFoods('test')

      expect(result).toBeInstanceOf(Array)
      expect(result).toHaveLength(2)
    })
  })

  describe('getFoodLogs', () => {
    it('fetches food logs without date filter', async () => {
      const mockLogs = [createMockFoodLog()]
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockLogs
      } as Response)

      const result = await getFoodLogs()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/food-logs/',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Token test-token-12345'
          })
        })
      )
      expect(result).toEqual(mockLogs)
    })

    it('fetches food logs for specific date', async () => {
      const mockLogs = [createMockFoodLog()]
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockLogs
      } as Response)

      const result = await getFoodLogs('2024-01-15')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/food-logs/?date=2024-01-15',
        expect.any(Object)
      )
      expect(result).toEqual(mockLogs)
    })

    it('throws error when not authenticated', async () => {
      clearLocalStorage()

      await expect(getFoodLogs()).rejects.toThrow('Authentication required')
    })

    it('handles API errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false
      } as Response)

      await expect(getFoodLogs()).rejects.toThrow('Failed to fetch food logs')
    })

    it('returns array of food logs', async () => {
      const mockLogs = [
        createMockFoodLog(),
        createMockFoodLog()
      ]
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockLogs
      } as Response)

      const result = await getFoodLogs()

      expect(result).toBeInstanceOf(Array)
      expect(result).toHaveLength(2)
    })
  })

  describe('createFoodLog', () => {
    it('creates food log with valid data', async () => {
      const mockLog = createMockFoodLog()
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockLog
      } as Response)

      const data = {
        food: 42,
        date: '2024-01-15',
        meal_type: 'breakfast' as const,
        quantity_grams: 100
      }

      const result = await createFoodLog(data)

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/food-logs/',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Token test-token-12345',
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify(data)
        })
      )
      expect(result).toEqual(mockLog)
    })

    it('throws error when not authenticated', async () => {
      clearLocalStorage()

      const data = {
        food: 42,
        date: '2024-01-15',
        meal_type: 'breakfast' as const,
        quantity_grams: 100
      }

      await expect(createFoodLog(data)).rejects.toThrow('Authentication required')
    })

    it('handles validation errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        json: async () => ({ error: 'Invalid quantity' })
      } as Response)

      const data = {
        food: 42,
        date: '2024-01-15',
        meal_type: 'breakfast' as const,
        quantity_grams: -10
      }

      await expect(createFoodLog(data)).rejects.toThrow('Invalid quantity')
    })

    it('returns created food log with calculated macros', async () => {
      const mockLog = createMockFoodLog({
        calories: 300,
        protein: 25,
        carbs: 30,
        fats: 12
      })
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockLog
      } as Response)

      const data = {
        food: 42,
        date: '2024-01-15',
        meal_type: 'breakfast' as const,
        quantity_grams: 150
      }

      const result = await createFoodLog(data)

      expect(result.calories).toBe(300)
      expect(result.protein).toBe(25)
      expect(result.carbs).toBe(30)
      expect(result.fats).toBe(12)
    })

    it('includes all required fields in request', async () => {
      const mockLog = createMockFoodLog()
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockLog
      } as Response)

      const data = {
        food: 42,
        date: '2024-01-15',
        meal_type: 'dinner' as const,
        quantity_grams: 200
      }

      await createFoodLog(data)

      const callArgs = mockFetch.mock.calls[0]
      const body = JSON.parse(callArgs[1]?.body as string)

      expect(body).toHaveProperty('food', 42)
      expect(body).toHaveProperty('date', '2024-01-15')
      expect(body).toHaveProperty('meal_type', 'dinner')
      expect(body).toHaveProperty('quantity_grams', 200)
    })
  })

  describe('deleteFoodLog', () => {
    it('deletes food log by ID', async () => {
      mockFetch.mockResolvedValue({
        ok: true
      } as Response)

      await deleteFoodLog(123)

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/food-logs/123/',
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            'Authorization': 'Token test-token-12345'
          })
        })
      )
    })

    it('throws error when not authenticated', async () => {
      clearLocalStorage()

      await expect(deleteFoodLog(123)).rejects.toThrow('Authentication required')
    })

    it('handles API errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false
      } as Response)

      await expect(deleteFoodLog(123)).rejects.toThrow('Failed to delete food log')
    })

    it('handles 404 not found', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404
      } as Response)

      await expect(deleteFoodLog(999)).rejects.toThrow()
    })
  })

  describe('getDailyTotals', () => {
    it('fetches daily totals without date', async () => {
      const mockTotals = createMockDailyTotals()
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockTotals
      } as Response)

      const result = await getDailyTotals()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/food-logs/daily_totals/',
        expect.objectContaining({
          method: 'GET'
        })
      )
      expect(result).toEqual(mockTotals)
    })

    it('fetches daily totals for specific date', async () => {
      const mockTotals = createMockDailyTotals({ date: '2024-01-15' })
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockTotals
      } as Response)

      const result = await getDailyTotals('2024-01-15')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/food-logs/daily_totals/?date=2024-01-15',
        expect.any(Object)
      )
      expect(result.date).toBe('2024-01-15')
    })

    it('throws error when not authenticated', async () => {
      clearLocalStorage()

      await expect(getDailyTotals()).rejects.toThrow('Authentication required')
    })

    it('handles API errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false
      } as Response)

      await expect(getDailyTotals()).rejects.toThrow('Failed to fetch daily totals')
    })

    it('returns totals with meal breakdown', async () => {
      const mockTotals = createMockDailyTotals({
        totals: { calories: 1850, protein: 125, carbs: 200, fats: 65 },
        by_meal: {
          breakfast: { calories: 450, protein: 30, carbs: 50, fats: 15 },
          lunch: { calories: 650, protein: 45, carbs: 70, fats: 22 },
          dinner: { calories: 750, protein: 50, carbs: 80, fats: 28 },
          snack: { calories: null, protein: null, carbs: null, fats: null }
        }
      })
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockTotals
      } as Response)

      const result = await getDailyTotals()

      expect(result.totals.calories).toBe(1850)
      expect(result.by_meal.breakfast.calories).toBe(450)
      expect(result.by_meal.lunch.calories).toBe(650)
      expect(result.by_meal.dinner.calories).toBe(750)
    })
  })

  describe('Utility Functions', () => {
    describe('formatDate', () => {
      it('formats date to YYYY-MM-DD', () => {
        const date = new Date('2024-01-15T12:00:00Z')
        expect(formatDate(date)).toBe('2024-01-15')
      })

      it('pads single digit months and days', () => {
        const date = new Date('2024-03-05T12:00:00Z')
        expect(formatDate(date)).toBe('2024-03-05')
      })
    })

    describe('getTodayDate', () => {
      it('returns today date in YYYY-MM-DD format', () => {
        const result = getTodayDate()
        expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/)
      })

      it('returns valid date string', () => {
        const result = getTodayDate()
        const date = new Date(result)
        expect(date).toBeInstanceOf(Date)
        expect(date.toString()).not.toBe('Invalid Date')
      })
    })
  })

  describe('Authentication', () => {
    it('includes auth token in all requests', async () => {
      localStorage.setItem('token', 'my-auth-token')

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => []
      } as Response)

      await searchFoods('test')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Token my-auth-token'
          })
        })
      )
    })

    it('fails gracefully when token is missing', async () => {
      clearLocalStorage()

      await expect(searchFoods('test')).rejects.toThrow('Authentication required')
      await expect(getFoodLogs()).rejects.toThrow('Authentication required')
      await expect(createFoodLog({ food: 1, date: '2024-01-01', meal_type: 'breakfast', quantity_grams: 100 }))
        .rejects.toThrow('Authentication required')
      await expect(deleteFoodLog(1)).rejects.toThrow('Authentication required')
      await expect(getDailyTotals()).rejects.toThrow('Authentication required')
    })
  })

  describe('API Endpoints', () => {
    it('uses correct base URL for all endpoints', async () => {
      const baseUrl = 'http://localhost:8000/api'

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => []
      } as Response)

      await searchFoods('test')
      expect(mockFetch.mock.calls[0][0]).toContain(baseUrl)

      await getFoodLogs()
      expect(mockFetch.mock.calls[1][0]).toContain(baseUrl)

      await getDailyTotals()
      expect(mockFetch.mock.calls[2][0]).toContain(baseUrl)
    })
  })

  describe('Error Handling', () => {
    it('handles network errors', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'))

      await expect(searchFoods('test')).rejects.toThrow('Network error')
    })

    it('handles timeout errors', async () => {
      mockFetch.mockRejectedValue(new Error('Request timeout'))

      await expect(getFoodLogs()).rejects.toThrow('Request timeout')
    })

    it('handles malformed responses', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => { throw new Error('Invalid JSON') }
      } as Response)

      await expect(searchFoods('test')).rejects.toThrow('Invalid JSON')
    })
  })
})
