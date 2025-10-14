import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import Navbar from './Navbar'
import { authService } from '@/services/auth'

// Mock the auth service
vi.mock('@/services/auth', () => ({
  authService: {
    logout: vi.fn(),
    isAuthenticated: vi.fn(),
  },
}))

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('Navbar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the app name', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false)

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    expect(screen.getByText(/nutriai/i)).toBeInTheDocument()
  })

  it('shows navigation links when authenticated', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(true)

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /profile/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /recipes/i })).toBeInTheDocument()
  })

  it('shows logout button when authenticated', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(true)

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument()
  })

  it('does not show logout button when not authenticated', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false)

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    expect(screen.queryByRole('button', { name: /logout/i })).not.toBeInTheDocument()
  })

  it('shows login and register links when not authenticated', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false)

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    expect(screen.getByRole('link', { name: /login/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /register/i })).toBeInTheDocument()
  })

  it('calls logout and navigates to login page when logout is clicked', async () => {
    const user = userEvent.setup()
    vi.mocked(authService.isAuthenticated).mockReturnValue(true)
    vi.mocked(authService.logout).mockResolvedValue()

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    const logoutButton = screen.getByRole('button', { name: /logout/i })
    await user.click(logoutButton)

    await waitFor(() => {
      expect(authService.logout).toHaveBeenCalled()
      expect(mockNavigate).toHaveBeenCalledWith('/login')
    })
  })

  it('handles logout errors gracefully', async () => {
    const user = userEvent.setup()
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    vi.mocked(authService.isAuthenticated).mockReturnValue(true)
    vi.mocked(authService.logout).mockRejectedValue(new Error('Logout failed'))

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    const logoutButton = screen.getByRole('button', { name: /logout/i })
    await user.click(logoutButton)

    await waitFor(() => {
      expect(authService.logout).toHaveBeenCalled()
      expect(mockNavigate).toHaveBeenCalledWith('/login')
    })

    consoleErrorSpy.mockRestore()
  })
})
