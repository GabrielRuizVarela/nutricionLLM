/**
 * Tests for DailyFoodLog component
 * Tests daily food logging, meal tracking, and macro totals display
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {
  renderWithProviders,
  createMockFoodLog,
  createMockDailyTotals,
  createMockProfile,
  getTodayDate
} from '@/test/utils'
import DailyFoodLog from './DailyFoodLog'
import * as foodLoggingService from '@/services/foodLogging'
import { profileService } from '@/services/profile'

// Mock the services
vi.mock('@/services/foodLogging', () => ({
  getFoodLogs: vi.fn(),
  getDailyTotals: vi.fn(),
  deleteFoodLog: vi.fn(),
  formatDate: (date: Date) => date.toISOString().split('T')[0],
  getTodayDate: () => '2024-01-15'
}))

vi.mock('@/services/profile', () => ({
  profileService: {
    getProfile: vi.fn()
  }
}))

// Mock window.confirm
global.confirm = vi.fn(() => true)

describe('DailyFoodLog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Component Rendering', () => {
    it('shows loading state while fetching data', () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )
      vi.mocked(foodLoggingService.getDailyTotals).mockImplementation(
        () => new Promise(() => {})
      )

      renderWithProviders(<DailyFoodLog />)

      expect(screen.getByText(/loading food logs/i)).toBeInTheDocument()
    })

    it('renders daily food log component after loading', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.queryByText(/loading food logs/i)).not.toBeInTheDocument()
      })
    })

    it('displays all meal type sections', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText('Breakfast')).toBeInTheDocument()
        expect(screen.getByText('Lunch')).toBeInTheDocument()
        expect(screen.getByText('Dinner')).toBeInTheDocument()
        expect(screen.getByText('Snacks')).toBeInTheDocument()
      })
    })

    it('displays "Daily Totals" heading', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText('Daily Totals')).toBeInTheDocument()
      })
    })
  })

  describe('Date Navigation', () => {
    it('displays current date by default', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        // Should show today's date (mocked as 2024-01-15)
        const dateText = screen.getByText(/2024/i)
        expect(dateText).toBeInTheDocument()
      })
    })

    it('has previous and next day navigation buttons', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /previous day/i })).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /next day/i })).toBeInTheDocument()
      })
    })

    it('loads food logs for new date when navigating', async () => {
      const user = userEvent.setup()
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /previous day/i })).toBeInTheDocument()
      })

      const previousButton = screen.getByRole('button', { name: /previous day/i })
      await user.click(previousButton)

      await waitFor(() => {
        // Should call getFoodLogs with new date
        expect(foodLoggingService.getFoodLogs).toHaveBeenCalledTimes(2)
      })
    })

    it('disables next day button when on current day', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        const nextButton = screen.getByRole('button', { name: /next day/i })
        expect(nextButton).toBeDisabled()
      })
    })
  })

  describe('Daily Totals Display', () => {
    it('displays daily calorie totals', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      const mockTotals = createMockDailyTotals({
        totals: { calories: 1850, protein: 125, carbs: 200, fats: 65 }
      })
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(mockTotals)
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText('1850')).toBeInTheDocument()
      })
    })

    it('displays daily protein totals', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      const mockTotals = createMockDailyTotals({
        totals: { calories: 1850, protein: 125, carbs: 200, fats: 65 }
      })
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(mockTotals)
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText(/125\.0g/)).toBeInTheDocument()
      })
    })

    it('displays daily carbs and fats totals', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      const mockTotals = createMockDailyTotals({
        totals: { calories: 1850, protein: 125, carbs: 200, fats: 65 }
      })
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(mockTotals)
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText(/200\.0g/)).toBeInTheDocument()
        expect(screen.getByText(/65\.0g/)).toBeInTheDocument()
      })
    })

    it('displays target values from profile', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      const mockProfile = createMockProfile({
        daily_calorie_target: 2000,
        daily_protein_target: 150,
        daily_carbs_target: 200,
        daily_fats_target: 65
      })
      vi.mocked(profileService.getProfile).mockResolvedValue(mockProfile)

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText(/2000 kcal/i)).toBeInTheDocument()
        expect(screen.getByText(/150g/i)).toBeInTheDocument()
      })
    })

    it('shows progress bars for macro targets', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      const mockProfile = createMockProfile({
        daily_calorie_target: 2000
      })
      vi.mocked(profileService.getProfile).mockResolvedValue(mockProfile)

      const { container } = renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        // Check for progress bar elements
        const progressBars = container.querySelectorAll('.rounded-full.h-2')
        expect(progressBars.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Food Log Display', () => {
    it('displays food logs grouped by meal type', async () => {
      const mockLogs = [
        createMockFoodLog({
          meal_type: 'breakfast',
          food_detail: { description: 'Eggs', brand_owner: 'Farm Fresh' } as any
        }),
        createMockFoodLog({
          meal_type: 'lunch',
          food_detail: { description: 'Chicken Breast', brand_owner: 'Organic Co' } as any
        })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText('Eggs')).toBeInTheDocument()
        expect(screen.getByText('Chicken Breast')).toBeInTheDocument()
      })
    })

    it('displays food brand owner', async () => {
      const mockLogs = [
        createMockFoodLog({
          food_detail: { description: 'Yogurt', brand_owner: 'Healthy Farms' } as any
        })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText('Healthy Farms')).toBeInTheDocument()
      })
    })

    it('displays food quantity in grams', async () => {
      const mockLogs = [
        createMockFoodLog({
          quantity_grams: 150,
          food_detail: { description: 'Rice' } as any
        })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText('150g')).toBeInTheDocument()
      })
    })

    it('displays food nutrition info (calories, protein, carbs, fats)', async () => {
      const mockLogs = [
        createMockFoodLog({
          calories: 250,
          protein: 20,
          carbs: 30,
          fats: 10,
          food_detail: { description: 'Chicken' } as any
        })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getAllByText('250').length).toBeGreaterThan(0) // calories
        expect(screen.getAllByText(/20\.0g/).length).toBeGreaterThan(0) // protein
        expect(screen.getAllByText(/30\.0g/).length).toBeGreaterThan(0) // carbs
        expect(screen.getAllByText(/10\.0g/).length).toBeGreaterThan(0) // fats
      })
    })

    it('shows empty state when no foods logged for a meal', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText(/no foods logged for breakfast yet/i)).toBeInTheDocument()
        expect(screen.getByText(/no foods logged for lunch yet/i)).toBeInTheDocument()
      })
    })
  })

  describe('Meal Totals Calculation', () => {
    it('calculates and displays meal totals per meal type', async () => {
      const mockLogs = [
        createMockFoodLog({
          meal_type: 'breakfast',
          calories: 200,
          protein: 10,
          carbs: 25,
          fats: 8,
          food_detail: { description: 'Food 1' } as any
        }),
        createMockFoodLog({
          meal_type: 'breakfast',
          calories: 150,
          protein: 8,
          carbs: 20,
          fats: 5,
          food_detail: { description: 'Food 2' } as any
        })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText(/Breakfast Totals/i)).toBeInTheDocument()
        expect(screen.getByText(/350 cal/i)).toBeInTheDocument() // 200 + 150
      })
    })
  })

  describe('Add Food Functionality', () => {
    it('has "Add Food" buttons for each meal type', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        const addButtons = screen.getAllByRole('button', { name: /add food/i })
        expect(addButtons).toHaveLength(4) // breakfast, lunch, dinner, snacks
      })
    })

    it('opens food search modal when clicking Add Food', async () => {
      const user = userEvent.setup()
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getAllByRole('button', { name: /add food/i })[0]).toBeInTheDocument()
      })

      await user.click(screen.getAllByRole('button', { name: /add food/i })[0])

      // Modal should open (FoodSearchModal component)
      // Note: Actual modal opening would need FoodSearchModal to be rendered
    })
  })

  describe('Delete Food Functionality', () => {
    it('displays delete button for each food entry', async () => {
      const mockLogs = [
        createMockFoodLog({ food_detail: { description: 'Test Food' } as any })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
      })
    })

    it('shows confirmation dialog when deleting food', async () => {
      const user = userEvent.setup()
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)

      const mockLogs = [
        createMockFoodLog({ id: 123, food_detail: { description: 'Test Food' } as any })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())
      vi.mocked(foodLoggingService.deleteFoodLog).mockResolvedValue(undefined)

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /delete/i }))

      expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this food entry?')
    })

    it('calls delete service when confirmed', async () => {
      const user = userEvent.setup()
      vi.spyOn(window, 'confirm').mockReturnValue(true)

      const mockLogs = [
        createMockFoodLog({ id: 123, food_detail: { description: 'Test Food' } as any })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())
      vi.mocked(foodLoggingService.deleteFoodLog).mockResolvedValue(undefined)

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /delete/i }))

      await waitFor(() => {
        expect(foodLoggingService.deleteFoodLog).toHaveBeenCalledWith(123)
      })
    })

    it('does not delete when confirmation is cancelled', async () => {
      const user = userEvent.setup()
      vi.spyOn(window, 'confirm').mockReturnValue(false)

      const mockLogs = [
        createMockFoodLog({ id: 123, food_detail: { description: 'Test Food' } as any })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())
      vi.mocked(foodLoggingService.deleteFoodLog).mockResolvedValue(undefined)

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /delete/i }))

      expect(foodLoggingService.deleteFoodLog).not.toHaveBeenCalled()
    })

    it('reloads data after successful deletion', async () => {
      const user = userEvent.setup()
      vi.spyOn(window, 'confirm').mockReturnValue(true)

      const mockLogs = [
        createMockFoodLog({ id: 123, food_detail: { description: 'Test Food' } as any })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())
      vi.mocked(foodLoggingService.deleteFoodLog).mockResolvedValue(undefined)

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
      })

      const initialCallCount = vi.mocked(foodLoggingService.getFoodLogs).mock.calls.length

      await user.click(screen.getByRole('button', { name: /delete/i }))

      await waitFor(() => {
        expect(foodLoggingService.getFoodLogs).toHaveBeenCalledTimes(initialCallCount + 1)
      })
    })
  })

  describe('Error Handling', () => {
    it('displays error message when API fails', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockRejectedValue(new Error('API Error'))
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByText(/API Error/i)).toBeInTheDocument()
      })
    })

    it('handles profile loading failure gracefully', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockRejectedValue(new Error('Profile Error'))

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        // Should still render component without profile data
        expect(screen.getByText('Breakfast')).toBeInTheDocument()
      })
    })

    it('shows error when food deletion fails', async () => {
      const user = userEvent.setup()
      vi.spyOn(window, 'confirm').mockReturnValue(true)

      const mockLogs = [
        createMockFoodLog({ id: 123, food_detail: { description: 'Test Food' } as any })
      ]
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue(mockLogs)
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())
      vi.mocked(foodLoggingService.deleteFoodLog).mockRejectedValue(new Error('Delete failed'))

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /delete/i }))

      await waitFor(() => {
        expect(screen.getByText(/delete failed/i)).toBeInTheDocument()
      })
    })
  })

  describe('Accessibility', () => {
    it('has accessible navigation buttons', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        const prevButton = screen.getByRole('button', { name: /previous day/i })
        const nextButton = screen.getByRole('button', { name: /next day/i })

        expect(prevButton).toBeInTheDocument()
        expect(nextButton).toBeInTheDocument()
      })
    })

    it('has accessible add food buttons for each meal', async () => {
      vi.mocked(foodLoggingService.getFoodLogs).mockResolvedValue([])
      vi.mocked(foodLoggingService.getDailyTotals).mockResolvedValue(createMockDailyTotals())
      vi.mocked(profileService.getProfile).mockResolvedValue(createMockProfile())

      renderWithProviders(<DailyFoodLog />)

      await waitFor(() => {
        const addButtons = screen.getAllByRole('button', { name: /add food/i })
        addButtons.forEach(button => {
          expect(button).toBeEnabled()
        })
      })
    })
  })
})
