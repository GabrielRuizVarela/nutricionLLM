/**
 * Tests for FoodSearchModal component
 * Tests food search, selection, quantity input, and logging functionality
 */

import { describe, it, expect, vi, beforeEach, afterEach, beforeAll, afterAll } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, createMockFood, createMockFoods } from '@/test/utils'
import FoodSearchModal from './FoodSearchModal'
import * as foodLoggingService from '@/services/foodLogging'
import { server } from '@/test/mocks/server'

// Mock the food logging service
vi.mock('@/services/foodLogging', () => ({
  searchFoods: vi.fn(),
  createFoodLog: vi.fn()
}))

describe('FoodSearchModal', () => {
  const mockOnClose = vi.fn()
  const mockOnFoodLogged = vi.fn()

  // Disable MSW for these tests since we're mocking the service directly
  beforeAll(() => {
    server.close()
  })

  afterAll(() => {
    server.listen({ onUnhandledRequest: 'error' })
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('Modal Rendering', () => {
    it('does not render when closed', () => {
      renderWithProviders(
        <FoodSearchModal
          isOpen={false}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('renders when open', () => {
      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('displays meal type in title', () => {
      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="lunch"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      expect(screen.getByText(/Log Food - Lunch/i)).toBeInTheDocument()
    })

    it('displays date in description', () => {
      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      expect(screen.getByText(/2024-01-15/)).toBeInTheDocument()
    })

    it('has search input field', () => {
      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      expect(screen.getByLabelText(/search foods/i)).toBeInTheDocument()
    })
  })

  describe('Food Search', () => {
    it('does not search when query is less than 2 characters', async () => {
      vi.useFakeTimers()

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'c' } })

      await vi.advanceTimersByTimeAsync(1000)

      expect(foodLoggingService.searchFoods).not.toHaveBeenCalled()

      vi.useRealTimers()
    })

    it('searches when query is 2 or more characters', async () => {
      const mockFoods = createMockFoods(3)
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })

      await waitFor(() => {
        expect(foodLoggingService.searchFoods).toHaveBeenCalledWith('chicken')
      }, { timeout: 2000 })
    })

    it('debounces search input (waits 500ms)', async () => {
      vi.useFakeTimers()

      const mockFoods = createMockFoods(3)
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chi' } })

      // Before 500ms
      await vi.advanceTimersByTimeAsync(400)
      expect(foodLoggingService.searchFoods).not.toHaveBeenCalled()

      // After 500ms
      await vi.advanceTimersByTimeAsync(100)
      await vi.runAllTimersAsync()

      expect(foodLoggingService.searchFoods).toHaveBeenCalledTimes(1)

      vi.useRealTimers()
    })

    it('shows searching indicator while searching', async () => {
      const user = userEvent.setup({ delay: null })
      vi.mocked(foodLoggingService.searchFoods).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText(/searching/i)).toBeInTheDocument()
      })
    })

    it('displays search results after search completes', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = [
        createMockFood({ description: 'Chicken Breast' }),
        createMockFood({ description: 'Chicken Thigh' })
      ]
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken Breast')).toBeInTheDocument()
        expect(screen.getByText('Chicken Thigh')).toBeInTheDocument()
      })
    })

    it('shows result count', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = createMockFoods(5)
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText(/Search Results \(5\)/i)).toBeInTheDocument()
      })
    })

    it('displays nutrition info in search results', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = [
        createMockFood({
          description: 'Chicken',
          calories: 165,
          protein: 31,
          carbs: 0,
          fats: 3.6,
          serving_size: 100,
          serving_size_unit: 'g'
        })
      ]
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText(/Serving: 100 g/i)).toBeInTheDocument()
        expect(screen.getByText(/Cal: 165/i)).toBeInTheDocument()
        expect(screen.getByText(/P: 31g/i)).toBeInTheDocument()
      })
    })

    it('displays brand owner if available', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = [
        createMockFood({
          description: 'Protein Bar',
          brand_owner: 'Health Co'
        })
      ]
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'protein' } })


      await waitFor(() => {
        expect(screen.getByText('Health Co')).toBeInTheDocument()
      })
    })

    it('handles search errors gracefully', async () => {
      const user = userEvent.setup({ delay: null })
      vi.mocked(foodLoggingService.searchFoods).mockRejectedValue(new Error('Search failed'))

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText(/Search failed/i)).toBeInTheDocument()
      })
    })
  })

  describe('Food Selection', () => {
    it('selects food when clicking on search result', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = [
        createMockFood({ description: 'Chicken Breast', serving_size: 100 })
      ]
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken Breast')).toBeInTheDocument()
      })

      const foodResult = screen.getByText('Chicken Breast')
      await user.click(foodResult)

      await waitFor(() => {
        expect(screen.getByText(/Selected Food/i)).toBeInTheDocument()
      })
    })

    it('pre-fills quantity with serving size', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = [
        createMockFood({ description: 'Apple', serving_size: 182 })
      ]
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'apple' } })


      await waitFor(() => {
        expect(screen.getByText('Apple')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Apple'))

      await waitFor(() => {
        const quantityInput = screen.getByLabelText(/quantity/i) as HTMLInputElement
        expect(quantityInput.value).toBe('182')
      })
    })

    it('allows changing selected food', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = [
        createMockFood({ description: 'Apple' })
      ]
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'apple' } })


      await waitFor(() => {
        expect(screen.getByText('Apple')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Apple'))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /change food/i })).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /change food/i }))

      await waitFor(() => {
        expect(screen.queryByText(/Selected Food/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('Macro Calculation', () => {
    it('calculates macros based on quantity', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = [
        createMockFood({
          description: 'Chicken',
          serving_size: 100,
          calories: 165,
          protein: 31,
          carbs: 0,
          fats: 3.6
        })
      ]
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Chicken'))

      await waitFor(() => {
        // For 100g (default), should show original values
        expect(screen.getByText(/165/)).toBeInTheDocument() // calories
      })
    })

    it('recalculates macros when quantity changes', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = [
        createMockFood({
          description: 'Chicken',
          serving_size: 100,
          calories: 165,
          protein: 31,
          carbs: 0,
          fats: 3.6
        })
      ]
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Chicken'))

      await waitFor(() => {
        expect(screen.getByLabelText(/quantity/i)).toBeInTheDocument()
      })

      const quantityInput = screen.getByLabelText(/quantity/i)
      await user.clear(quantityInput)
      await user.type(quantityInput, '200')

      await waitFor(() => {
        // For 200g (double), should show doubled values
        expect(screen.getByText(/330/)).toBeInTheDocument() // 165 * 2
      })
    })

    it('displays nutritional information for selected quantity', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = [
        createMockFood({
          description: 'Chicken',
          serving_size: 100,
          serving_size_unit: 'g',
          calories: 165,
          protein: 31,
          carbs: 0,
          fats: 3.6
        })
      ]
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Chicken'))

      await waitFor(() => {
        expect(screen.getByText(/Nutritional Information for/i)).toBeInTheDocument()
        expect(screen.getByText(/Calories/i)).toBeInTheDocument()
        expect(screen.getByText(/Protein/i)).toBeInTheDocument()
        expect(screen.getByText(/Carbs/i)).toBeInTheDocument()
        expect(screen.getByText(/Fats/i)).toBeInTheDocument()
      })
    })
  })

  describe('Food Logging', () => {
    it('has disabled Log Food button when no food is selected', () => {
      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      expect(screen.queryByRole('button', { name: /log food/i })).not.toBeInTheDocument()
    })

    it('enables Log Food button when food and quantity are selected', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFoods = [
        createMockFood({ description: 'Chicken', serving_size: 100 })
      ]
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue(mockFoods)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Chicken'))

      await waitFor(() => {
        const logButton = screen.getByRole('button', { name: /log food/i })
        expect(logButton).toBeInTheDocument()
        expect(logButton).not.toBeDisabled()
      })
    })

    it('calls createFoodLog with correct data when logging food', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFood = createMockFood({
        id: 42,
        description: 'Chicken',
        serving_size: 100
      })
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue([mockFood])
      vi.mocked(foodLoggingService.createFoodLog).mockResolvedValue({} as any)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Chicken'))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /log food/i })).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /log food/i }))

      await waitFor(() => {
        expect(foodLoggingService.createFoodLog).toHaveBeenCalledWith({
          food: 42,
          date: '2024-01-15',
          meal_type: 'breakfast',
          quantity_grams: 100
        })
      })
    })

    it('closes modal after successful logging', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFood = createMockFood({ description: 'Chicken', serving_size: 100 })
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue([mockFood])
      vi.mocked(foodLoggingService.createFoodLog).mockResolvedValue({} as any)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Chicken'))
      await user.click(screen.getByRole('button', { name: /log food/i }))

      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalled()
      })
    })

    it('calls onFoodLogged callback after successful logging', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFood = createMockFood({ description: 'Chicken', serving_size: 100 })
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue([mockFood])
      vi.mocked(foodLoggingService.createFoodLog).mockResolvedValue({} as any)

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Chicken'))
      await user.click(screen.getByRole('button', { name: /log food/i }))

      await waitFor(() => {
        expect(mockOnFoodLogged).toHaveBeenCalled()
      })
    })

    it('shows error when logging fails', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFood = createMockFood({ description: 'Chicken', serving_size: 100 })
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue([mockFood])
      vi.mocked(foodLoggingService.createFoodLog).mockRejectedValue(new Error('Failed to log food'))

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Chicken'))
      await user.click(screen.getByRole('button', { name: /log food/i }))

      await waitFor(() => {
        expect(screen.getByText(/Failed to log food/i)).toBeInTheDocument()
      })
    })

    it('validates quantity before logging', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFood = createMockFood({ description: 'Chicken', serving_size: 100 })
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue([mockFood])

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Chicken'))

      const quantityInput = screen.getByLabelText(/quantity/i)
      await user.clear(quantityInput)
      await user.type(quantityInput, '-5')

      await user.click(screen.getByRole('button', { name: /log food/i }))

      await waitFor(() => {
        expect(screen.getByText(/Please enter a valid quantity/i)).toBeInTheDocument()
      })

      expect(foodLoggingService.createFoodLog).not.toHaveBeenCalled()
    })
  })

  describe('Modal Actions', () => {
    it('has cancel button', () => {
      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
    })

    it('closes modal when cancel is clicked', async () => {
      const user = userEvent.setup()

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      await user.click(screen.getByRole('button', { name: /cancel/i }))

      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('Accessibility', () => {
    it('has proper dialog structure', () => {
      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('has labeled search input', () => {
      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      expect(searchInput).toBeInTheDocument()
      expect(searchInput).toBeEnabled()
    })

    it('has labeled quantity input after food selection', async () => {
      const user = userEvent.setup({ delay: null })
      const mockFood = createMockFood({ description: 'Chicken', serving_size: 100 })
      vi.mocked(foodLoggingService.searchFoods).mockResolvedValue([mockFood])

      renderWithProviders(
        <FoodSearchModal
          isOpen={true}
          onClose={mockOnClose}
          date="2024-01-15"
          mealType="breakfast"
          onFoodLogged={mockOnFoodLogged}
        />
      )

      const searchInput = screen.getByLabelText(/search foods/i)
      fireEvent.change(searchInput, { target: { value: 'chicken' } })


      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Chicken'))

      await waitFor(() => {
        const quantityInput = screen.getByLabelText(/quantity/i)
        expect(quantityInput).toBeInTheDocument()
        expect(quantityInput).toBeEnabled()
      })
    })
  })
})
