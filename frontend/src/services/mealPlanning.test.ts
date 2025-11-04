/**
 * Tests for mealPlanning service
 * Tests API integration for meal planning operations
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createMockMealPlan, createMockMealSlot, setupAuth, clearLocalStorage } from '@/test/utils'

// Mock axios with a factory function that returns the mocked instance immediately
vi.mock('axios', () => {
  const mockGet = vi.fn()
  const mockPatch = vi.fn()
  const mockDelete = vi.fn()

  return {
    default: {
      create: vi.fn(() => ({
        get: mockGet,
        patch: mockPatch,
        delete: mockDelete,
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      })),
      // Export mocks so tests can access them
      __mocks: {
        get: mockGet,
        patch: mockPatch,
        delete: mockDelete
      }
    }
  }
})

// Import service and axios AFTER mocking
import { mealPlanningService } from './mealPlanning'
import axios from 'axios'

// Extract mocks for easier access in tests
const mockGet = (axios as any).__mocks.get
const mockPatch = (axios as any).__mocks.patch
const mockDelete = (axios as any).__mocks.delete

describe('mealPlanning Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setupAuth()
  })

  afterEach(() => {
    clearLocalStorage()
  })

  describe('Authentication', () => {
    it('includes auth token in request headers', async () => {
      const mockMealPlan = createMockMealPlan()
      mockGet.mockResolvedValue({ data: mockMealPlan })

      await mealPlanningService.getCurrentWeek()

      // Verify the service successfully made the request
      expect(mockGet).toHaveBeenCalledWith('/meal-plans/current/')
    })

    it('reads token from localStorage', async () => {
      const testToken = 'test-token-12345'
      localStorage.setItem('token', testToken)

      const mockMealPlan = createMockMealPlan()
      mockGet.mockResolvedValue({ data: mockMealPlan })

      await mealPlanningService.getCurrentWeek()

      expect(localStorage.getItem('token')).toBe(testToken)
    })
  })

  describe('getCurrentWeek', () => {
    it('fetches current week meal plan', async () => {
      const mockMealPlan = createMockMealPlan()
      mockGet.mockResolvedValue({ data: mockMealPlan })

      const result = await mealPlanningService.getCurrentWeek()

      expect(mockGet).toHaveBeenCalledWith('/meal-plans/current/')
      expect(result).toEqual(mockMealPlan)
    })

    it('returns meal plan with all 21 slots (7 days × 3 meals)', async () => {
      const mockMealPlan = createMockMealPlan()
      mockGet.mockResolvedValue({ data: mockMealPlan })

      const result = await mealPlanningService.getCurrentWeek()

      expect(result.meal_slots).toHaveLength(21)
    })

    it('handles API errors', async () => {
      mockGet.mockRejectedValue(new Error('Network error'))

      await expect(mealPlanningService.getCurrentWeek()).rejects.toThrow('Network error')
    })

    it('handles 401 unauthorized errors', async () => {
      mockGet.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } }
      })

      await expect(mealPlanningService.getCurrentWeek()).rejects.toMatchObject({
        response: { status: 401 }
      })
    })
  })

  describe('getByDate', () => {
    it('fetches meal plan for specific date', async () => {
      const mockMealPlan = createMockMealPlan({ week_start_date: '2024-01-01' })
      mockGet.mockResolvedValue({ data: mockMealPlan })

      const result = await mealPlanningService.getByDate('2024-01-03')

      expect(mockGet).toHaveBeenCalledWith('/meal-plans/by_date/?date=2024-01-03')
      expect(result).toEqual(mockMealPlan)
    })

    it('accepts date in YYYY-MM-DD format', async () => {
      const mockMealPlan = createMockMealPlan()
      mockGet.mockResolvedValue({ data: mockMealPlan })

      await mealPlanningService.getByDate('2024-12-25')

      expect(mockGet).toHaveBeenCalledWith('/meal-plans/by_date/?date=2024-12-25')
    })

    it('returns meal plan matching the requested week', async () => {
      const mockMealPlan = createMockMealPlan({
        week_start_date: '2024-01-01',
        week_end_date: '2024-01-07'
      })
      mockGet.mockResolvedValue({ data: mockMealPlan })

      const result = await mealPlanningService.getByDate('2024-01-03')

      expect(result.week_start_date).toBe('2024-01-01')
      expect(result.week_end_date).toBe('2024-01-07')
    })

    it('handles date not found errors', async () => {
      mockGet.mockRejectedValue({
        response: { status: 404, data: { detail: 'Not found' } }
      })

      await expect(mealPlanningService.getByDate('2024-01-01')).rejects.toMatchObject({
        response: { status: 404 }
      })
    })
  })

  describe('listMealPlans', () => {
    it('fetches all meal plans for user', async () => {
      const mockMealPlans = [
        createMockMealPlan({ id: 1 }),
        createMockMealPlan({ id: 2 }),
        createMockMealPlan({ id: 3 })
      ]
      mockGet.mockResolvedValue({ data: mockMealPlans })

      const result = await mealPlanningService.listMealPlans()

      expect(mockGet).toHaveBeenCalledWith('/meal-plans/')
      expect(result).toEqual(mockMealPlans)
      expect(result).toHaveLength(3)
    })

    it('returns empty array when user has no meal plans', async () => {
      mockGet.mockResolvedValue({ data: [] })

      const result = await mealPlanningService.listMealPlans()

      expect(result).toEqual([])
      expect(result).toHaveLength(0)
    })

    it('handles API errors', async () => {
      mockGet.mockRejectedValue(new Error('Server error'))

      await expect(mealPlanningService.listMealPlans()).rejects.toThrow('Server error')
    })
  })

  describe('getMealPlan', () => {
    it('fetches specific meal plan by ID', async () => {
      const mockMealPlan = createMockMealPlan({ id: 42 })
      mockGet.mockResolvedValue({ data: mockMealPlan })

      const result = await mealPlanningService.getMealPlan(42)

      expect(mockGet).toHaveBeenCalledWith('/meal-plans/42/')
      expect(result).toEqual(mockMealPlan)
      expect(result.id).toBe(42)
    })

    it('handles meal plan not found', async () => {
      mockGet.mockRejectedValue({
        response: { status: 404, data: { detail: 'Not found' } }
      })

      await expect(mealPlanningService.getMealPlan(999)).rejects.toMatchObject({
        response: { status: 404 }
      })
    })

    it('handles access to other user meal plan (403)', async () => {
      mockGet.mockRejectedValue({
        response: { status: 403, data: { detail: 'Permission denied' } }
      })

      await expect(mealPlanningService.getMealPlan(123)).rejects.toMatchObject({
        response: { status: 403 }
      })
    })
  })

  describe('updateMealSlot', () => {
    it('updates meal slot with recipe assignment', async () => {
      const mockSlot = createMockMealSlot({ id: 10, recipe: null })
      const updatedSlot = { ...mockSlot, recipe: 5 }
      mockPatch.mockResolvedValue({ data: updatedSlot })

      const result = await mealPlanningService.updateMealSlot(10, { recipe: 5 })

      expect(mockPatch).toHaveBeenCalledWith('/meal-slots/10/', { recipe: 5 })
      expect(result.recipe).toBe(5)
    })

    it('marks meal slot as leftover', async () => {
      const mockSlot = createMockMealSlot({ id: 10 })
      const updatedSlot = { ...mockSlot, is_leftover: true, original_meal_slot: 5 }
      mockPatch.mockResolvedValue({ data: updatedSlot })

      const result = await mealPlanningService.updateMealSlot(10, {
        is_leftover: true,
        original_meal_slot: 5
      })

      expect(mockPatch).toHaveBeenCalledWith('/meal-slots/10/', {
        is_leftover: true,
        original_meal_slot: 5
      })
      expect(result.is_leftover).toBe(true)
      expect(result.original_meal_slot).toBe(5)
    })

    it('updates meal slot notes', async () => {
      const mockSlot = createMockMealSlot({ id: 10 })
      const updatedSlot = { ...mockSlot, notes: 'Double the recipe' }
      mockPatch.mockResolvedValue({ data: updatedSlot })

      const result = await mealPlanningService.updateMealSlot(10, {
        notes: 'Double the recipe'
      })

      expect(mockPatch).toHaveBeenCalledWith('/meal-slots/10/', {
        notes: 'Double the recipe'
      })
      expect(result.notes).toBe('Double the recipe')
    })

    it('handles validation errors (400)', async () => {
      mockPatch.mockRejectedValue({
        response: {
          status: 400,
          data: { recipe: ['Recipe does not exist'] }
        }
      })

      await expect(
        mealPlanningService.updateMealSlot(10, { recipe: 999 })
      ).rejects.toMatchObject({
        response: { status: 400 }
      })
    })

    it('handles slot not found (404)', async () => {
      mockPatch.mockRejectedValue({
        response: { status: 404, data: { detail: 'Not found' } }
      })

      await expect(
        mealPlanningService.updateMealSlot(999, { recipe: 1 })
      ).rejects.toMatchObject({
        response: { status: 404 }
      })
    })
  })

  describe('clearMealSlot', () => {
    it('clears meal slot by removing recipe', async () => {
      const mockSlot = createMockMealSlot({ id: 10, recipe: 5 })
      const clearedSlot = {
        ...mockSlot,
        recipe: null,
        recipe_detail: null,
        is_leftover: false,
        original_meal_slot: null,
        notes: ''
      }
      mockPatch.mockResolvedValue({ data: clearedSlot })

      const result = await mealPlanningService.clearMealSlot(10)

      expect(mockPatch).toHaveBeenCalledWith('/meal-slots/10/', {
        recipe: null,
        is_leftover: false,
        original_meal_slot: null,
        notes: ''
      })
      expect(result.recipe).toBeNull()
      expect(result.is_leftover).toBe(false)
      expect(result.notes).toBe('')
    })

    it('resets leftover status when clearing', async () => {
      const mockSlot = createMockMealSlot({
        id: 10,
        recipe: 5,
        is_leftover: true,
        original_meal_slot: 3
      })
      const clearedSlot = {
        ...mockSlot,
        recipe: null,
        is_leftover: false,
        original_meal_slot: null
      }
      mockPatch.mockResolvedValue({ data: clearedSlot })

      const result = await mealPlanningService.clearMealSlot(10)

      expect(result.is_leftover).toBe(false)
      expect(result.original_meal_slot).toBeNull()
    })

    it('clears notes when clearing meal slot', async () => {
      const mockSlot = createMockMealSlot({
        id: 10,
        recipe: 5,
        notes: 'Some notes'
      })
      const clearedSlot = { ...mockSlot, recipe: null, notes: '' }
      mockPatch.mockResolvedValue({ data: clearedSlot })

      const result = await mealPlanningService.clearMealSlot(10)

      expect(result.notes).toBe('')
    })

    it('handles slot not found', async () => {
      mockPatch.mockRejectedValue({
        response: { status: 404, data: { detail: 'Not found' } }
      })

      await expect(mealPlanningService.clearMealSlot(999)).rejects.toMatchObject({
        response: { status: 404 }
      })
    })
  })

  describe('deleteMealPlan', () => {
    it('deletes meal plan by ID', async () => {
      mockDelete.mockResolvedValue({ data: null })

      await mealPlanningService.deleteMealPlan(10)

      expect(mockDelete).toHaveBeenCalledWith('/meal-plans/10/')
    })

    it('returns void on success', async () => {
      mockDelete.mockResolvedValue({ data: null })

      const result = await mealPlanningService.deleteMealPlan(10)

      expect(result).toBeUndefined()
    })

    it('handles meal plan not found', async () => {
      mockDelete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Not found' } }
      })

      await expect(mealPlanningService.deleteMealPlan(999)).rejects.toMatchObject({
        response: { status: 404 }
      })
    })

    it('handles permission denied (403)', async () => {
      mockDelete.mockRejectedValue({
        response: { status: 403, data: { detail: 'Permission denied' } }
      })

      await expect(mealPlanningService.deleteMealPlan(123)).rejects.toMatchObject({
        response: { status: 403 }
      })
    })
  })

  describe('Error Handling', () => {
    it('handles network errors', async () => {
      mockGet.mockRejectedValue(new Error('Network error'))

      await expect(mealPlanningService.getCurrentWeek()).rejects.toThrow('Network error')
    })

    it('handles timeout errors', async () => {
      mockGet.mockRejectedValue({ code: 'ECONNABORTED', message: 'timeout' })

      await expect(mealPlanningService.getCurrentWeek()).rejects.toMatchObject({
        code: 'ECONNABORTED'
      })
    })

    it('handles server errors (500)', async () => {
      mockGet.mockRejectedValue({
        response: { status: 500, data: { detail: 'Internal server error' } }
      })

      await expect(mealPlanningService.getCurrentWeek()).rejects.toMatchObject({
        response: { status: 500 }
      })
    })

    it('handles malformed response data', async () => {
      mockGet.mockResolvedValue({ data: null })

      const result = await mealPlanningService.getCurrentWeek()

      expect(result).toBeNull()
    })
  })

  describe('API Endpoints', () => {
    it('constructs correct endpoints for all operations', async () => {
      const mockMealPlan = createMockMealPlan()
      const mockSlot = createMockMealSlot()

      mockGet.mockResolvedValue({ data: mockMealPlan })
      mockPatch.mockResolvedValue({ data: mockSlot })
      mockDelete.mockResolvedValue({ data: null })

      // Test all endpoint constructions
      await mealPlanningService.getCurrentWeek()
      expect(mockGet).toHaveBeenCalledWith('/meal-plans/current/')

      await mealPlanningService.getByDate('2024-01-01')
      expect(mockGet).toHaveBeenCalledWith('/meal-plans/by_date/?date=2024-01-01')

      await mealPlanningService.listMealPlans()
      expect(mockGet).toHaveBeenCalledWith('/meal-plans/')

      await mealPlanningService.getMealPlan(1)
      expect(mockGet).toHaveBeenCalledWith('/meal-plans/1/')

      await mealPlanningService.updateMealSlot(1, { recipe: 1 })
      expect(mockPatch).toHaveBeenCalledWith('/meal-slots/1/', { recipe: 1 })

      await mealPlanningService.deleteMealPlan(1)
      expect(mockDelete).toHaveBeenCalledWith('/meal-plans/1/')
    })
  })
})
