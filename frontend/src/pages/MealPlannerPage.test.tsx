/**
 * Tests for MealPlannerPage
 * Tests page-level integration for meal planning
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithProviders, createMockMealPlan } from '@/test/utils'
import MealPlannerPage from './MealPlannerPage'
import { mealPlanningService } from '@/services/mealPlanning'

// Mock the meal planning service
vi.mock('@/services/mealPlanning', () => ({
  mealPlanningService: {
    getByDate: vi.fn(),
    updateMealSlot: vi.fn(),
    clearMealSlot: vi.fn(),
  }
}))

describe('MealPlannerPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Page Rendering', () => {
    it('renders the meal planner page', async () => {
      const mockMealPlan = createMockMealPlan()
      vi.mocked(mealPlanningService.getByDate).mockResolvedValue(mockMealPlan)

      renderWithProviders(<MealPlannerPage />)

      await waitFor(() => {
        expect(screen.getByText('Weekly Meal Plan')).toBeInTheDocument()
      })
    })

    it('renders WeeklyMealPlanner component', async () => {
      const mockMealPlan = createMockMealPlan()
      vi.mocked(mealPlanningService.getByDate).mockResolvedValue(mockMealPlan)

      renderWithProviders(<MealPlannerPage />)

      await waitFor(() => {
        // Verify key elements from WeeklyMealPlanner are present
        expect(screen.getByText('Weekly Meal Plan')).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /previous week/i })).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /next week/i })).toBeInTheDocument()
      })
    })
  })

  describe('Integration', () => {
    it('loads meal plan data on mount', async () => {
      const mockMealPlan = createMockMealPlan({
        week_start_date: '2024-01-01',
        week_end_date: '2024-01-07'
      })
      vi.mocked(mealPlanningService.getByDate).mockResolvedValue(mockMealPlan)

      renderWithProviders(<MealPlannerPage />)

      await waitFor(() => {
        expect(mealPlanningService.getByDate).toHaveBeenCalled()
        const weekText = screen.getByText(/Week of/)
        expect(weekText).toHaveTextContent('2024-01-01')
      })
    })

    it('displays all days of the week', async () => {
      const mockMealPlan = createMockMealPlan()
      vi.mocked(mealPlanningService.getByDate).mockResolvedValue(mockMealPlan)

      renderWithProviders(<MealPlannerPage />)

      await waitFor(() => {
        expect(screen.getByText('Monday')).toBeInTheDocument()
      })

      const days = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
      days.forEach(day => {
        expect(screen.getByText(day)).toBeInTheDocument()
      })
    })

    it('handles API errors gracefully', async () => {
      vi.mocked(mealPlanningService.getByDate).mockRejectedValue(new Error('API Error'))

      renderWithProviders(<MealPlannerPage />)

      await waitFor(() => {
        expect(screen.getByText(/failed to load meal plan/i)).toBeInTheDocument()
      })
    })
  })

  describe('Page Metadata', () => {
    it('is accessible from /meal-planner route', async () => {
      const mockMealPlan = createMockMealPlan()
      vi.mocked(mealPlanningService.getByDate).mockResolvedValue(mockMealPlan)

      renderWithProviders(<MealPlannerPage />, {
        initialRoute: '/meal-planner'
      })

      await waitFor(() => {
        expect(screen.getByText('Weekly Meal Plan')).toBeInTheDocument()
      })
    })
  })
})
