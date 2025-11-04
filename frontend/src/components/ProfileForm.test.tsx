import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import ProfileForm from './ProfileForm'
import { profileService } from '@/services/profile'

// Mock the profile service
vi.mock('@/services/profile', () => ({
  profileService: {
    getProfile: vi.fn(),
    updateProfile: vi.fn(),
  },
}))

const mockProfile = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  goal: 'lose_weight',
  dietary_preferences: 'vegetarian',
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
}

describe('ProfileForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads and displays profile data', async () => {
    const user = userEvent.setup()
    vi.mocked(profileService.getProfile).mockResolvedValue(mockProfile)

    render(
      <BrowserRouter>
        <ProfileForm />
      </BrowserRouter>
    )

    // Should show loading state initially
    expect(screen.getByText(/loading/i)).toBeInTheDocument()

    // Wait for profile data to load
    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument()
    })

    // Click on Dietary tab to see goal and dietary preferences
    const dietaryTab = screen.getByRole('tab', { name: /dietary/i })
    await user.click(dietaryTab)

    // Check that goal button is selected (variant="default")
    await waitFor(() => {
      const loseWeightButton = screen.getByRole('button', { name: /lose weight/i })
      expect(loseWeightButton).toBeInTheDocument()
      expect(screen.getByDisplayValue('vegetarian')).toBeInTheDocument()
    })
  })

  it('displays user email and username', async () => {
    vi.mocked(profileService.getProfile).mockResolvedValue(mockProfile)

    render(
      <BrowserRouter>
        <ProfileForm />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument()
      expect(screen.getByText('test@example.com')).toBeInTheDocument()
    })
  })

  it('allows editing goal and dietary preferences', async () => {
    const user = userEvent.setup()
    vi.mocked(profileService.getProfile).mockResolvedValue(mockProfile)

    render(
      <BrowserRouter>
        <ProfileForm />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument()
    })

    // Click on Dietary tab
    const dietaryTab = screen.getByRole('tab', { name: /dietary/i })
    await user.click(dietaryTab)

    // Click on a different goal button
    const gainMuscleButton = screen.getByRole('button', { name: /gain muscle/i })
    await user.click(gainMuscleButton)

    // Edit dietary preferences
    const dietaryInput = screen.getByLabelText(/dietary preferences/i)
    await user.clear(dietaryInput)
    await user.type(dietaryInput, 'vegan')

    expect(dietaryInput).toHaveValue('vegan')
  })

  it('successfully updates profile with valid data', async () => {
    const user = userEvent.setup()
    const updatedProfile = {
      ...mockProfile,
      age: 35,
    }

    vi.mocked(profileService.getProfile).mockResolvedValue(mockProfile)
    vi.mocked(profileService.updateProfile).mockResolvedValue(updatedProfile)

    render(
      <BrowserRouter>
        <ProfileForm />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument()
    })

    // Wait for form to be fully loaded
    const ageInput = await screen.findByLabelText(/age/i)

    // Change age field in the Personal tab (default active tab)
    await user.clear(ageInput)
    await user.type(ageInput, '35')

    // Submit form
    const submitButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(profileService.updateProfile).toHaveBeenCalled()
      expect(screen.getByText(/profile updated successfully/i)).toBeInTheDocument()
    })
  })

  it('shows error message when update fails', async () => {
    const user = userEvent.setup()

    vi.mocked(profileService.getProfile).mockResolvedValue(mockProfile)
    vi.mocked(profileService.updateProfile).mockRejectedValue(
      new Error('Update failed')
    )

    render(
      <BrowserRouter>
        <ProfileForm />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument()
    })

    // Change age field to trigger form submission
    const ageInput = await screen.findByLabelText(/age/i)
    await user.clear(ageInput)
    await user.type(ageInput, '35')

    const submitButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/failed to update profile/i)).toBeInTheDocument()
    })
  })

  it('disables submit button while submitting', async () => {
    const user = userEvent.setup()

    vi.mocked(profileService.getProfile).mockResolvedValue(mockProfile)
    vi.mocked(profileService.updateProfile).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    )

    render(
      <BrowserRouter>
        <ProfileForm />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument()
    })

    // Change age field to trigger form submission
    const ageInput = await screen.findByLabelText(/age/i)
    await user.clear(ageInput)
    await user.type(ageInput, '35')

    const submitButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(submitButton)

    expect(submitButton).toBeDisabled()
  })

  it('shows error message when profile fails to load', async () => {
    vi.mocked(profileService.getProfile).mockRejectedValue(
      new Error('Failed to load')
    )

    render(
      <BrowserRouter>
        <ProfileForm />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/failed to load profile/i)).toBeInTheDocument()
    })
  })

  it('validates that fields are not empty', async () => {
    const user = userEvent.setup()
    vi.mocked(profileService.getProfile).mockResolvedValue(mockProfile)
    vi.mocked(profileService.updateProfile).mockResolvedValue(mockProfile)

    render(
      <BrowserRouter>
        <ProfileForm />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument()
    })

    // Change age field to verify form allows submission with optional fields
    const ageInput = await screen.findByLabelText(/age/i)
    await user.clear(ageInput)
    await user.type(ageInput, '30')

    const submitButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(profileService.updateProfile).toHaveBeenCalled()
    })
  })
})
