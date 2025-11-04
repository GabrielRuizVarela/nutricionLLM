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
  name: 'Ensalada de Lentejas',
  ingredients: '1 cup cooked lentils, 1 cucumber, 2 tomatoes, olive oil, lemon',
  instructions: '1. Drain lentils. 2. Chop vegetables. 3. Mix with oil and lemon.',
  calories: 320,
  protein: 18.5,
  carbs: 45.0,
  fats: 8.2,
  prep_time_minutes: 10,
  meal_type: 'lunch',
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

    expect(screen.getByText(/meal type/i)).toBeInTheDocument()
    expect(screen.getByText(/available time/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /breakfast/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /15 min/i })).toBeInTheDocument()
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

    // Click 60+ min button to show custom time input
    const customTimeButton = screen.getByRole('button', { name: /60\+ min/i })
    await user.click(customTimeButton)

    // Find the custom time input and enter invalid value
    const timeInput = screen.getByPlaceholderText(/enter minutes/i)
    await user.clear(timeInput)
    await user.type(timeInput, '0')

    const submitButton = screen.getByRole('button', { name: /generate recipe/i })
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

    // Click Lunch button for meal type
    const lunchButton = screen.getByRole('button', { name: /lunch/i })
    await user.click(lunchButton)

    // Click 15 min button for time
    const time15Button = screen.getByRole('button', { name: /15 min/i })
    await user.click(time15Button)

    const submitButton = screen.getByRole('button', { name: /generate recipe/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(recipeService.generateRecipe).toHaveBeenCalledWith({
        meal_type: 'lunch',
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

    const lunchButton = screen.getByRole('button', { name: /lunch/i })
    await user.click(lunchButton)

    const time15Button = screen.getByRole('button', { name: /15 min/i })
    await user.click(time15Button)

    const submitButton = screen.getByRole('button', { name: /generate recipe/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Ensalada de Lentejas')).toBeInTheDocument()
      expect(screen.getAllByText(/320/).length).toBeGreaterThan(0) // calories
      expect(screen.getAllByText(/18\.5/).length).toBeGreaterThan(0) // protein
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

    const lunchButton = screen.getByRole('button', { name: /lunch/i })
    await user.click(lunchButton)

    const time15Button = screen.getByRole('button', { name: /15 min/i })
    await user.click(time15Button)

    const submitButton = screen.getByRole('button', { name: /generate recipe/i })
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

    const lunchButton = screen.getByRole('button', { name: /lunch/i })
    await user.click(lunchButton)

    const time15Button = screen.getByRole('button', { name: /15 min/i })
    await user.click(time15Button)

    const submitButton = screen.getByRole('button', { name: /generate recipe/i })
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
    const lunchButton = screen.getByRole('button', { name: /lunch/i })
    await user.click(lunchButton)

    const time15Button = screen.getByRole('button', { name: /15 min/i })
    await user.click(time15Button)

    const submitButton = screen.getByRole('button', { name: /generate recipe/i })
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
    const lunchButton = screen.getByRole('button', { name: /lunch/i })
    await user.click(lunchButton)

    const time15Button = screen.getByRole('button', { name: /15 min/i })
    await user.click(time15Button)

    const submitButton = screen.getByRole('button', { name: /generate recipe/i })
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
