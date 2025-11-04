/**
 * Tests for FoodLogPage
 * Tests page-level integration for food logging
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithProviders, createMockDailyTotals, createMockProfile } from '@/test/utils'
import FoodLogPage from './FoodLogPage'
import * as foodLoggingService from '@/services/foodLogging'
import { profileService } from '@/services/profile'

// Mock the services
vi.mock('@/services/foodLogging', () => ({
  getFoodLogs: vi.fn(),
  getDailyTotals: vi.fn(),
  deleteFoodLog: vi.fn(),
  getTodayDate: () => '2024-01-15',
  formatDate: (date: Date) => date.toISOString().split('T')[0]
}))

vi.mock('@/services/profile', () => ({
  profileService: {
    getProfile: vi.fn()
  }
}))

describe('FoodLogPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Page Rendering', () => {
    it('renders the food log page', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<FoodLogPage />)

      await waitFor(() => {
        expect(screen.getByText('Food Diary')).toBeInTheDocument()
      })
    })

    it('displays page title and description', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<FoodLogPage />)

      await waitFor(() => {
        expect(screen.getByText('Food Diary')).toBeInTheDocument()
        expect(screen.getByText(/Track your daily food intake/i)).toBeInTheDocument()
      })
    })

    it('renders DailyFoodLog component', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<FoodLogPage />)

      await waitFor(() => {
        // Verify key elements from DailyFoodLog are present
        expect(screen.getByText('Daily Totals')).toBeInTheDocument()
        expect(screen.getByText('Breakfast')).toBeInTheDocument()
      })
    })
  })

  describe('Integration', () => {
    it('loads food logs on mount', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<FoodLogPage />)

      await waitFor(() => {
        expect(foodLoggingService.getFoodLogs).toHaveBeenCalled()
        expect(foodLoggingService.getDailyTotals).toHaveBeenCalled()
      })
    })

    it('displays all meal sections', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<FoodLogPage />)

      await waitFor(() => {
        expect(screen.getByText('Breakfast')).toBeInTheDocument()
        expect(screen.getByText('Lunch')).toBeInTheDocument()
        expect(screen.getByText('Dinner')).toBeInTheDocument()
        expect(screen.getByText('Snacks')).toBeInTheDocument()
      })
    })

    it('handles API errors gracefully', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockRejectedValue(new Error('API Error'))
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<FoodLogPage />)

      await waitFor(() => {
        expect(screen.getByText(/API Error/i)).toBeInTheDocument()
      })
    })
  })

  describe('Page Metadata', () => {
    it('is accessible from /food-log route', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<FoodLogPage />, {
        initialRoute: '/food-log'
      })

      await waitFor(() => {
        expect(screen.getByText('Food Diary')).toBeInTheDocument()
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper heading structure', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<FoodLogPage />)

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /food diary/i })).toBeInTheDocument()
      })
    })
  })
})
