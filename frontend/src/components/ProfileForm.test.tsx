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
  goal: 'lose weight',
  dietary_preferences: 'vegetarian',
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
}

describe('ProfileForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads and displays profile data', async () => {
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
      expect(screen.getByDisplayValue('lose weight')).toBeInTheDocument()
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
      expect(screen.getByLabelText(/goal/i)).toBeInTheDocument()
    })

    const goalInput = screen.getByLabelText(/goal/i)
    await user.clear(goalInput)
    await user.type(goalInput, 'gain muscle')

    expect(goalInput).toHaveValue('gain muscle')
  })

  it('successfully updates profile with valid data', async () => {
    const user = userEvent.setup()
    const updatedProfile = {
      ...mockProfile,
      goal: 'gain muscle',
      dietary_preferences: 'vegan',
    }

    vi.mocked(profileService.getProfile).mockResolvedValue(mockProfile)
    vi.mocked(profileService.updateProfile).mockResolvedValue(updatedProfile)

    render(
      <BrowserRouter>
        <ProfileForm />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByLabelText(/goal/i)).toBeInTheDocument()
    })

    const goalInput = screen.getByLabelText(/goal/i)
    const dietInput = screen.getByLabelText(/dietary preferences/i)
    const submitButton = screen.getByRole('button', { name: /save/i })

    await user.clear(goalInput)
    await user.type(goalInput, 'gain muscle')
    await user.clear(dietInput)
    await user.type(dietInput, 'vegan')
    await user.click(submitButton)

    await waitFor(() => {
      expect(profileService.updateProfile).toHaveBeenCalledWith({
        goal: 'gain muscle',
        dietary_preferences: 'vegan',
      })
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
      expect(screen.getByLabelText(/goal/i)).toBeInTheDocument()
    })

    const submitButton = screen.getByRole('button', { name: /save/i })
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
      expect(screen.getByLabelText(/goal/i)).toBeInTheDocument()
    })

    const submitButton = screen.getByRole('button', { name: /save/i })
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

    render(
      <BrowserRouter>
        <ProfileForm />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByLabelText(/goal/i)).toBeInTheDocument()
    })

    const goalInput = screen.getByLabelText(/goal/i)
    const submitButton = screen.getByRole('button', { name: /save/i })

    await user.clear(goalInput)
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/goal must be at least 1 character/i)).toBeInTheDocument()
    })
  })
})
