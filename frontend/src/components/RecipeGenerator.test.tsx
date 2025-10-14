import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import RecipeGenerator from './RecipeGenerator'
import { recipeService } from '@/services/recipes'

// Mock the recipe service
vi.mock('@/services/recipes', () => ({
  recipeService: {
    generateRecipe: vi.fn(),
    saveRecipe: vi.fn(),
  },
}))

const mockGeneratedRecipe = {
  nombre: 'Ensalada de Lentejas',
  ingredientes_texto: '1 cup cooked lentils, 1 cucumber, 2 tomatoes, olive oil, lemon',
  pasos_texto: '1. Drain lentils. 2. Chop vegetables. 3. Mix with oil and lemon.',
  calorias: 320,
  proteinas: 18.5,
  carbohidratos: 45.0,
  grasas: 8.2,
  tiempo_min: 10,
  tipo: 'almuerzo',
}

describe('RecipeGenerator', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders recipe generation form', () => {
    render(
      <BrowserRouter>
        <RecipeGenerator />
      </BrowserRouter>
    )

    expect(screen.getByLabelText(/meal type/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/available time/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /generate recipe/i })).toBeInTheDocument()
  })

  it('shows validation error for missing meal type', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <RecipeGenerator />
      </BrowserRouter>
    )

    const submitButton = screen.getByRole('button', { name: /generate recipe/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/please select a meal type/i)).toBeInTheDocument()
    })
  })

  it('shows validation error for invalid time', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <RecipeGenerator />
      </BrowserRouter>
    )

    const timeInput = screen.getByLabelText(/available time/i)
    const submitButton = screen.getByRole('button', { name: /generate recipe/i })

    await user.type(timeInput, '0')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/time must be at least 1 minute/i)).toBeInTheDocument()
    })
  })

  it('successfully generates recipe with valid input', async () => {
    const user = userEvent.setup()

    vi.mocked(recipeService.generateRecipe).mockResolvedValue(mockGeneratedRecipe)

    render(
      <BrowserRouter>
        <RecipeGenerator />
      </BrowserRouter>
    )

    const mealTypeSelect = screen.getByLabelText(/meal type/i)
    const timeInput = screen.getByLabelText(/available time/i)
    const submitButton = screen.getByRole('button', { name: /generate recipe/i })

    await user.selectOptions(mealTypeSelect, 'almuerzo')
    await user.type(timeInput, '15')
    await user.click(submitButton)

    await waitFor(() => {
      expect(recipeService.generateRecipe).toHaveBeenCalledWith({
        meal_type: 'almuerzo',
        available_time: 15,
      })
    })
  })

  it('displays generated recipe on success', async () => {
    const user = userEvent.setup()

    vi.mocked(recipeService.generateRecipe).mockResolvedValue(mockGeneratedRecipe)

    render(
      <BrowserRouter>
        <RecipeGenerator />
      </BrowserRouter>
    )

    const mealTypeSelect = screen.getByLabelText(/meal type/i)
    const timeInput = screen.getByLabelText(/available time/i)
    const submitButton = screen.getByRole('button', { name: /generate recipe/i })

    await user.selectOptions(mealTypeSelect, 'almuerzo')
    await user.type(timeInput, '15')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Ensalada de Lentejas')).toBeInTheDocument()
      expect(screen.getByText(/320/)).toBeInTheDocument() // calories
      expect(screen.getByText(/18.5/)).toBeInTheDocument() // protein
    })
  })

  it('shows loading state during generation', async () => {
    const user = userEvent.setup()

    vi.mocked(recipeService.generateRecipe).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    )

    render(
      <BrowserRouter>
        <RecipeGenerator />
      </BrowserRouter>
    )

    const mealTypeSelect = screen.getByLabelText(/meal type/i)
    const timeInput = screen.getByLabelText(/available time/i)
    const submitButton = screen.getByRole('button', { name: /generate recipe/i })

    await user.selectOptions(mealTypeSelect, 'almuerzo')
    await user.type(timeInput, '15')
    await user.click(submitButton)

    expect(screen.getByText(/generating/i)).toBeInTheDocument()
  })

  it('shows error message when generation fails', async () => {
    const user = userEvent.setup()

    vi.mocked(recipeService.generateRecipe).mockRejectedValue(
      new Error('Generation failed')
    )

    render(
      <BrowserRouter>
        <RecipeGenerator />
      </BrowserRouter>
    )

    const mealTypeSelect = screen.getByLabelText(/meal type/i)
    const timeInput = screen.getByLabelText(/available time/i)
    const submitButton = screen.getByRole('button', { name: /generate recipe/i })

    await user.selectOptions(mealTypeSelect, 'almuerzo')
    await user.type(timeInput, '15')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/failed to generate recipe/i)).toBeInTheDocument()
    })
  })

  it('allows saving generated recipe', async () => {
    const user = userEvent.setup()
    const savedRecipe = { ...mockGeneratedRecipe, id: 1 }

    vi.mocked(recipeService.generateRecipe).mockResolvedValue(mockGeneratedRecipe)
    vi.mocked(recipeService.saveRecipe).mockResolvedValue(savedRecipe)

    render(
      <BrowserRouter>
        <RecipeGenerator />
      </BrowserRouter>
    )

    // Generate recipe first
    const mealTypeSelect = screen.getByLabelText(/meal type/i)
    const timeInput = screen.getByLabelText(/available time/i)
    const submitButton = screen.getByRole('button', { name: /generate recipe/i })

    await user.selectOptions(mealTypeSelect, 'almuerzo')
    await user.type(timeInput, '15')
    await user.click(submitButton)

    // Wait for recipe to be displayed
    await waitFor(() => {
      expect(screen.getByText('Ensalada de Lentejas')).toBeInTheDocument()
    })

    // Save the recipe
    const saveButton = screen.getByRole('button', { name: /save recipe/i })
    await user.click(saveButton)

    await waitFor(() => {
      expect(recipeService.saveRecipe).toHaveBeenCalledWith(mockGeneratedRecipe)
      expect(screen.getByText(/recipe saved successfully/i)).toBeInTheDocument()
    })
  })

  it('shows error when save fails', async () => {
    const user = userEvent.setup()

    vi.mocked(recipeService.generateRecipe).mockResolvedValue(mockGeneratedRecipe)
    vi.mocked(recipeService.saveRecipe).mockRejectedValue(new Error('Save failed'))

    render(
      <BrowserRouter>
        <RecipeGenerator />
      </BrowserRouter>
    )

    // Generate recipe first
    const mealTypeSelect = screen.getByLabelText(/meal type/i)
    const timeInput = screen.getByLabelText(/available time/i)
    const submitButton = screen.getByRole('button', { name: /generate recipe/i })

    await user.selectOptions(mealTypeSelect, 'almuerzo')
    await user.type(timeInput, '15')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Ensalada de Lentejas')).toBeInTheDocument()
    })

    // Try to save
    const saveButton = screen.getByRole('button', { name: /save recipe/i })
    await user.click(saveButton)

    await waitFor(() => {
      expect(screen.getByText(/failed to save recipe/i)).toBeInTheDocument()
    })
  })
})
