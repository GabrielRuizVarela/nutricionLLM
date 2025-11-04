import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import RecipeList from './RecipeList'
import { recipeService } from '@/services/recipes'

// Mock the recipe service
vi.mock('@/services/recipes', () => ({
  recipeService: {
    getRecipes: vi.fn(),
  },
}))

const mockRecipes = [
  {
    id: 1,
    name: 'Ensalada de Lentejas',
    ingredients: 'lentils, cucumber, tomatoes',
    instructions: '1. Cook. 2. Mix.',
    calories: 320,
    protein: 18.5,
    carbs: 45.0,
    fats: 8.2,
    prep_time_minutes: 10,
    meal_type: 'lunch',
    created_at: '2025-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Smoothie Verde',
    ingredients: 'spinach, banana, almond milk',
    instructions: '1. Blend all ingredients.',
    calories: 150,
    protein: 5.0,
    carbs: 25.0,
    fats: 3.0,
    prep_time_minutes: 5,
    meal_type: 'breakfast',
    created_at: '2025-01-02T00:00:00Z',
  },
]

describe('RecipeList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading state while fetching recipes', () => {
    vi.mocked(recipeService.getRecipes).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    render(
      <BrowserRouter>
        <RecipeList />
      </BrowserRouter>
    )

    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('loads and displays saved recipes', async () => {
    vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)

    render(
      <BrowserRouter>
        <RecipeList />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Ensalada de Lentejas')).toBeInTheDocument()
      expect(screen.getByText('Smoothie Verde')).toBeInTheDocument()
    })
  })

  it('displays recipe nutritional information', async () => {
    vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)

    render(
      <BrowserRouter>
        <RecipeList />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/320/)).toBeInTheDocument() // calories
      expect(screen.getByText(/18.5/)).toBeInTheDocument() // protein
    })
  })

  it('displays recipe time and type', async () => {
    vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)

    render(
      <BrowserRouter>
        <RecipeList />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/10 minutes/i)).toBeInTheDocument()
      expect(screen.getByText(/5 minutes/i)).toBeInTheDocument()
    })
  })

  it('shows empty state when no recipes', async () => {
    vi.mocked(recipeService.getRecipes).mockResolvedValue([])

    render(
      <BrowserRouter>
        <RecipeList />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/no recipes found/i)).toBeInTheDocument()
      expect(screen.getByText(/start generating recipes/i)).toBeInTheDocument()
    })
  })

  it('shows error message when loading fails', async () => {
    vi.mocked(recipeService.getRecipes).mockRejectedValue(
      new Error('Failed to load')
    )

    render(
      <BrowserRouter>
        <RecipeList />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/failed to load recipes/i)).toBeInTheDocument()
    })
  })

  it('has a button to retry loading on error', async () => {
    vi.mocked(recipeService.getRecipes).mockRejectedValue(
      new Error('Failed to load')
    )

    render(
      <BrowserRouter>
        <RecipeList />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()
    })
  })

  it('displays recipes in a grid layout', async () => {
    vi.mocked(recipeService.getRecipes).mockResolvedValue(mockRecipes)

    render(
      <BrowserRouter>
        <RecipeList />
      </BrowserRouter>
    )

    await waitFor(() => {
      const recipeCards = screen.getAllByRole('article')
      expect(recipeCards).toHaveLength(2)
    })
  })
})
