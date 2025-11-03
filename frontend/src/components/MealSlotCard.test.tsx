/**
 * Tests for MealSlotCard component
 * Tests individual meal slot display, interaction, and state management
 */

import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, createMockMealSlot, createMockRecipe } from '@/test/utils'
import MealSlotCard from './MealSlotCard'

describe('MealSlotCard', () => {
  const mockOnAddMeal = vi.fn()
  const mockOnClearMeal = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Empty Meal Slot', () => {
    it('displays "Add Meal" button when slot is empty', () => {
      const emptySlot = createMockMealSlot({
        recipe: null,
        recipe_detail: null
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={emptySlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      const addButton = screen.getByRole('button', { name: /add meal/i })
      expect(addButton).toBeInTheDocument()
    })

    it('calls onAddMeal when clicking "Add Meal" button', async () => {
      const user = userEvent.setup()
      const emptySlot = createMockMealSlot({
        recipe: null,
        recipe_detail: null
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={emptySlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      const addButton = screen.getByRole('button', { name: /add meal/i })
      await user.click(addButton)

      expect(mockOnAddMeal).toHaveBeenCalledTimes(1)
      expect(mockOnAddMeal).toHaveBeenCalledWith(emptySlot)
    })

    it('does not display recipe information when slot is empty', () => {
      const emptySlot = createMockMealSlot({
        recipe: null,
        recipe_detail: null
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={emptySlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      expect(screen.queryByText(/kcal/i)).not.toBeInTheDocument()
      expect(screen.queryByText(/min/i)).not.toBeInTheDocument()
    })
  })

  describe('Filled Meal Slot', () => {
    it('displays recipe name when slot has a recipe', () => {
      const recipe = createMockRecipe({ name: 'Grilled Salmon with Vegetables' })
      const filledSlot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={filledSlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      expect(screen.getByText('Grilled Salmon with Vegetables')).toBeInTheDocument()
    })

    it('displays calories information', () => {
      const recipe = createMockRecipe({ calories: 450 })
      const filledSlot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={filledSlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      expect(screen.getByText(/450 kcal/i)).toBeInTheDocument()
    })

    it('displays prep time information', () => {
      const recipe = createMockRecipe({ prep_time_minutes: 30 })
      const filledSlot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={filledSlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      expect(screen.getByText(/30 min/i)).toBeInTheDocument()
    })

    it('displays macronutrient breakdown (protein, carbs, fats)', () => {
      const recipe = createMockRecipe({
        protein: 30,
        carbs: 45,
        fats: 15
      })
      const filledSlot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={filledSlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      expect(screen.getByText(/P: 30g/i)).toBeInTheDocument()
      expect(screen.getByText(/C: 45g/i)).toBeInTheDocument()
      expect(screen.getByText(/F: 15g/i)).toBeInTheDocument()
    })

    it('does not display "Add Meal" button when slot is filled', () => {
      const recipe = createMockRecipe()
      const filledSlot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={filledSlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      expect(screen.queryByRole('button', { name: /add meal/i })).not.toBeInTheDocument()
    })
  })

  describe('Leftover Badge', () => {
    it('displays "Leftover" badge when meal is marked as leftover', () => {
      const recipe = createMockRecipe()
      const leftoverSlot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe,
        is_leftover: true
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={leftoverSlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      expect(screen.getByText(/leftover/i)).toBeInTheDocument()
    })

    it('does not display "Leftover" badge for regular meals', () => {
      const recipe = createMockRecipe()
      const regularSlot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe,
        is_leftover: false
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={regularSlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      expect(screen.queryByText(/leftover/i)).not.toBeInTheDocument()
    })
  })

  describe('Notes Display', () => {
    it('displays notes when present', () => {
      const recipe = createMockRecipe()
      const slotWithNotes = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe,
        notes: 'Double the recipe for meal prep'
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={slotWithNotes}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      expect(screen.getByText('Double the recipe for meal prep')).toBeInTheDocument()
    })

    it('does not display notes section when notes are empty', () => {
      const recipe = createMockRecipe()
      const slotWithoutNotes = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe,
        notes: ''
      })

      const { container } = renderWithProviders(
        <MealSlotCard
          mealSlot={slotWithoutNotes}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      // Check that there's no italic text (which is used for notes)
      const italicElements = container.querySelectorAll('p.italic')
      expect(italicElements.length).toBe(0)
    })
  })

  describe('Clear Meal Functionality', () => {
    it('shows clear button on hover for filled slots', async () => {
      const user = userEvent.setup()
      const recipe = createMockRecipe()
      const filledSlot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe
      })

      const { container } = renderWithProviders(
        <MealSlotCard
          mealSlot={filledSlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      // Get the card container
      const card = container.querySelector('div[class*="border"]')
      expect(card).toBeTruthy()

      if (card) {
        // Hover over the card
        await user.hover(card)

        // Clear button should be visible (×)
        const clearButton = screen.queryByRole('button', { name: /×/i })
        expect(clearButton).toBeInTheDocument()
      }
    })

    it('calls onClearMeal when clicking clear button', async () => {
      const user = userEvent.setup()
      const recipe = createMockRecipe()
      const filledSlot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe
      })

      const { container } = renderWithProviders(
        <MealSlotCard
          mealSlot={filledSlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      // Hover to show clear button
      const card = container.querySelector('div[class*="border"]')
      if (card) {
        await user.hover(card)

        const clearButton = screen.getByRole('button', { name: /×/i })
        await user.click(clearButton)

        expect(mockOnClearMeal).toHaveBeenCalledTimes(1)
        expect(mockOnClearMeal).toHaveBeenCalledWith(filledSlot)
      }
    })
  })

  describe('Visual States', () => {
    it('has hover shadow effect', () => {
      const emptySlot = createMockMealSlot({
        recipe: null,
        recipe_detail: null
      })

      const { container } = renderWithProviders(
        <MealSlotCard
          mealSlot={emptySlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      const card = container.querySelector('div[class*="hover:shadow"]')
      expect(card).toBeTruthy()
    })

    it('has minimum height for consistent layout', () => {
      const emptySlot = createMockMealSlot({
        recipe: null,
        recipe_detail: null
      })

      const { container } = renderWithProviders(
        <MealSlotCard
          mealSlot={emptySlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      const card = container.querySelector('div[class*="min-h"]')
      expect(card).toBeTruthy()
    })
  })

  describe('Edge Cases', () => {
    it('handles recipe with zero values gracefully', () => {
      const recipe = createMockRecipe({
        calories: 0,
        protein: 0,
        carbs: 0,
        fats: 0,
        prep_time_minutes: 0
      })
      const slot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={slot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      expect(screen.getByText(/0 kcal/i)).toBeInTheDocument()
      expect(screen.getByText(/0 min/i)).toBeInTheDocument()
      expect(screen.getByText(/P: 0g/i)).toBeInTheDocument()
    })

    it('handles very long recipe names with line clamping', () => {
      const recipe = createMockRecipe({
        name: 'This is an extremely long recipe name that should be truncated to prevent layout issues'
      })
      const slot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe
      })

      const { container } = renderWithProviders(
        <MealSlotCard
          mealSlot={slot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      // Check that the name has line-clamp class
      const nameElement = container.querySelector('.line-clamp-2')
      expect(nameElement).toBeTruthy()
      expect(nameElement?.textContent).toContain('extremely long recipe name')
    })

    it('handles missing recipe detail gracefully', () => {
      const slot = createMockMealSlot({
        recipe: 123,
        recipe_detail: null // Recipe ID exists but details are missing
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={slot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      // Should not crash and should not show recipe info
      expect(screen.queryByText(/kcal/i)).not.toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has accessible button for adding meals', () => {
      const emptySlot = createMockMealSlot({
        recipe: null,
        recipe_detail: null
      })

      renderWithProviders(
        <MealSlotCard
          mealSlot={emptySlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      const addButton = screen.getByRole('button', { name: /add meal/i })
      expect(addButton).toBeInTheDocument()
      expect(addButton).toBeEnabled()
    })

    it('has accessible button for clearing meals', async () => {
      const user = userEvent.setup()
      const recipe = createMockRecipe()
      const filledSlot = createMockMealSlot({
        recipe: recipe.id,
        recipe_detail: recipe
      })

      const { container } = renderWithProviders(
        <MealSlotCard
          mealSlot={filledSlot}
          onAddMeal={mockOnAddMeal}
          onClearMeal={mockOnClearMeal}
        />
      )

      const card = container.querySelector('div[class*="border"]')
      if (card) {
        await user.hover(card)

        const clearButton = screen.getByRole('button', { name: /×/i })
        expect(clearButton).toBeInTheDocument()
        expect(clearButton).toBeEnabled()
      }
    })
  })
})
