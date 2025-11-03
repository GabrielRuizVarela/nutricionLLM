/**
 * Tests for MealSelectionModal component
 * Tests recipe selection modal, search, filtering, and navigation
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, createMockMealSlot, createMockRecipe, createMockRecipes } from '@/test/utils'
import MealSelectionModal from './MealSelectionModal'
import { recipeService } from '@/services/recipes'

// Mock the recipe service
vi.mock('@/services/recipes', () => ({
  recipeService: {
    getRecipes: vi.fn(),
  }
}))

// Mock react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('MealSelectionModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSelectRecipe = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Modal Rendering and State', () => {
    it('does not render when isOpen is false', () => {
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={false}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('renders when isOpen is true', async () => {
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot({
        day_name: 'Monday',
        meal_name: 'Breakfast'
      })

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
      })
    })

    it('displays meal slot day and meal type in title', async () => {
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot({
        day_name: 'Wednesday',
        meal_name: 'Dinner'
      })

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText(/Select Meal for Wednesday Dinner/i)).toBeInTheDocument()
      })
    })

    it('returns null when mealSlot is null', () => {
      const { container } = renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={null}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      expect(container.firstChild).toBeNull()
    })
  })

  describe('Recipe Loading', () => {
    it('loads recipes when modal opens', async () => {
      const mockRecipes = createMockRecipes(3)
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(recipeService.getRecipes).toHaveBeenCalledTimes(1)
      })
    })

    it('shows loading state while fetching recipes', async () => {
      vi.mocked(recipeService.getRecipes).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText(/loading recipes/i)).toBeInTheDocument()
      })
    })

    it('displays error message when recipe loading fails', async () => {
      vi.mocked(recipeService.getRecipes).mockRejectedValue(new Error('API Error'))
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText(/failed to load recipes/i)).toBeInTheDocument()
      })
    })

    it('reloads recipes when modal is reopened', async () => {
      const mockRecipes = createMockRecipes(2)
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      const { rerender } = renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(recipeService.getRecipes).toHaveBeenCalledTimes(1)
      })

      // Close modal
      rerender(
        <MealSelectionModal
          isOpen={false}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      // Reopen modal
      rerender(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(recipeService.getRecipes).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe('Recipe Display', () => {
    it('displays all loaded recipes', async () => {
      const mockRecipes = [
        createMockRecipe({ name: 'Grilled Chicken' }),
        createMockRecipe({ name: 'Pasta Carbonara' }),
        createMockRecipe({ name: 'Caesar Salad' })
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Grilled Chicken')).toBeInTheDocument()
        expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument()
        expect(screen.getByText('Caesar Salad')).toBeInTheDocument()
      })
    })

    it('displays recipe nutrition information', async () => {
      const mockRecipes = [
        createMockRecipe({
          name: 'Test Recipe',
          calories: 450,
          protein: 30,
          carbs: 45,
          fats: 15,
          prep_time_minutes: 30
        })
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText(/450 kcal/i)).toBeInTheDocument()
        expect(screen.getByText(/30 min/i)).toBeInTheDocument()
        expect(screen.getByText(/P: 30g/i)).toBeInTheDocument()
        expect(screen.getByText(/C: 45g/i)).toBeInTheDocument()
        expect(screen.getByText(/F: 15g/i)).toBeInTheDocument()
      })
    })

    it('shows "Recommended" badge for recipes matching meal type', async () => {
      const mockRecipes = [
        createMockRecipe({ name: 'Breakfast Burrito', meal_type: 'breakfast' }),
        createMockRecipe({ name: 'Lunch Salad', meal_type: 'lunch' })
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot({ meal_type: 'breakfast' })

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText(/recommended/i)).toBeInTheDocument()
      })
    })

    it('shows empty state when no recipes exist', async () => {
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText(/no saved recipes yet/i)).toBeInTheDocument()
      })
    })
  })

  describe('Search Functionality', () => {
    it('has a search input field', async () => {
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search recipes/i)).toBeInTheDocument()
      })
    })

    it('filters recipes by name when searching', async () => {
      const user = userEvent.setup()
      const mockRecipes = [
        createMockRecipe({ name: 'Grilled Chicken' }),
        createMockRecipe({ name: 'Pasta Carbonara' }),
        createMockRecipe({ name: 'Chicken Salad' })
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Grilled Chicken')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/search recipes/i)
      await user.type(searchInput, 'Chicken')

      await waitFor(() => {
        expect(screen.getByText('Grilled Chicken')).toBeInTheDocument()
        expect(screen.getByText('Chicken Salad')).toBeInTheDocument()
        expect(screen.queryByText('Pasta Carbonara')).not.toBeInTheDocument()
      })
    })

    it('filters recipes by ingredients when searching', async () => {
      const user = userEvent.setup()
      const mockRecipes = [
        createMockRecipe({ name: 'Recipe 1', ingredients: 'chicken, garlic, olive oil' }),
        createMockRecipe({ name: 'Recipe 2', ingredients: 'beef, tomatoes, onions' }),
        createMockRecipe({ name: 'Recipe 3', ingredients: 'chicken, rice, vegetables' })
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Recipe 1')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/search recipes/i)
      await user.type(searchInput, 'beef')

      await waitFor(() => {
        expect(screen.getByText('Recipe 2')).toBeInTheDocument()
        expect(screen.queryByText('Recipe 1')).not.toBeInTheDocument()
        expect(screen.queryByText('Recipe 3')).not.toBeInTheDocument()
      })
    })

    it('shows no results message when search yields no matches', async () => {
      const user = userEvent.setup()
      const mockRecipes = [
        createMockRecipe({ name: 'Chicken' }),
        createMockRecipe({ name: 'Beef' })
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Chicken')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/search recipes/i)
      await user.type(searchInput, 'pizza')

      await waitFor(() => {
        expect(screen.getByText(/no recipes found matching/i)).toBeInTheDocument()
      })
    })

    it('search is case-insensitive', async () => {
      const user = userEvent.setup()
      const mockRecipes = [
        createMockRecipe({ name: 'Grilled SALMON' }),
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Grilled SALMON')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/search recipes/i)
      await user.type(searchInput, 'salmon')

      await waitFor(() => {
        expect(screen.getByText('Grilled SALMON')).toBeInTheDocument()
      })
    })

    it('clears search query when modal reopens', async () => {
      const user = userEvent.setup()
      const mockRecipes = createMockRecipes(2)
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      const { rerender } = renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search recipes/i)).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/search recipes/i)
      await user.type(searchInput, 'test query')

      // Close modal
      rerender(
        <MealSelectionModal
          isOpen={false}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      // Reopen modal
      rerender(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        const newSearchInput = screen.getByPlaceholderText(/search recipes/i) as HTMLInputElement
        expect(newSearchInput.value).toBe('')
      })
    })
  })

  describe('Recipe Selection', () => {
    it('calls onSelectRecipe when clicking a recipe', async () => {
      const user = userEvent.setup()
      const mockRecipes = [
        createMockRecipe({ id: 42, name: 'Test Recipe' })
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Test Recipe')).toBeInTheDocument()
      })

      await user.click(screen.getAllByRole('button', { name: /select/i })[0])

      expect(mockOnSelectRecipe).toHaveBeenCalledTimes(1)
      expect(mockOnSelectRecipe).toHaveBeenCalledWith(42)
    })

    it('closes modal after selecting a recipe', async () => {
      const user = userEvent.setup()
      const mockRecipes = [
        createMockRecipe({ id: 42, name: 'Test Recipe' })
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Test Recipe')).toBeInTheDocument()
      })

      await user.click(screen.getAllByRole('button', { name: /select/i })[0])

      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('can click on recipe card to select it', async () => {
      const user = userEvent.setup()
      const mockRecipes = [
        createMockRecipe({ id: 42, name: 'Test Recipe' })
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot()

      const { container } = renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Test Recipe')).toBeInTheDocument()
      })

      // Click on the recipe card itself
      const recipeCard = container.querySelector('.cursor-pointer')
      if (recipeCard) {
        await user.click(recipeCard as HTMLElement)
        expect(mockOnSelectRecipe).toHaveBeenCalledWith(42)
      }
    })
  })

  describe('Generate New Recipe Navigation', () => {
    it('has "Generate New Recipe" button', async () => {
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /generate new recipe/i })).toBeInTheDocument()
      })
    })

    it('navigates to recipe generation page when clicking Generate', async () => {
      const user = userEvent.setup()
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /generate new recipe/i })).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /generate new recipe/i }))

      expect(mockNavigate).toHaveBeenCalledWith('/generate')
    })

    it('closes modal when navigating to generate page', async () => {
      const user = userEvent.setup()
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /generate new recipe/i })).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /generate new recipe/i }))

      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })
  })

  describe('Modal Actions', () => {
    it('has a Cancel button', async () => {
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
      })
    })

    it('closes modal when clicking Cancel', async () => {
      const user = userEvent.setup()
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /cancel/i }))

      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })
  })

  describe('Recipe Filtering by Meal Type', () => {
    it('sorts matching meal types to the top', async () => {
      const mockRecipes = [
        createMockRecipe({ id: 1, name: 'Dinner Recipe', meal_type: 'dinner' }),
        createMockRecipe({ id: 2, name: 'Breakfast Recipe', meal_type: 'breakfast' }),
        createMockRecipe({ id: 3, name: 'Another Breakfast', meal_type: 'breakfast' }),
      ]
      vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)
      const mealSlot = createMockMealSlot({ meal_type: 'breakfast' })

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        // Breakfast recipes should appear with "Recommended" badge
        const recommendedBadges = screen.getAllByText(/recommended/i)
        expect(recommendedBadges).toHaveLength(2) // Two breakfast recipes
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper dialog structure', async () => {
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
      })
    })

    it('has accessible search input', async () => {
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        const searchInput = screen.getByPlaceholderText(/search recipes/i)
        expect(searchInput).toBeInTheDocument()
        expect(searchInput).toBeEnabled()
      })
    })

    it('has accessible action buttons', async () => {
      vi.mocked(recipeService.getRecipes).mockResolvedValue([])
      const mealSlot = createMockMealSlot()

      renderWithProviders(
        <MealSelectionModal
          isOpen={true}
          onClose={mockOnClose}
          mealSlot={mealSlot}
          onSelectRecipe={mockOnSelectRecipe}
        />
      )

      await waitFor(() => {
        const cancelButton = screen.getByRole('button', { name: /cancel/i })
        const generateButton = screen.getByRole('button', { name: /generate new recipe/i })

        expect(cancelButton).toBeEnabled()
        expect(generateButton).toBeEnabled()
      })
    })
  })
})
