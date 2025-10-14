import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import LoginForm from './LoginForm'
import { authService } from '@/services/auth'

// Mock the auth service
vi.mock('@/services/auth', () => ({
  authService: {
    login: vi.fn(),
    saveToken: vi.fn(),
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

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form with all fields', () => {
    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    )

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('shows validation error for invalid email', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'invalid-email')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/invalid email/i)).toBeInTheDocument()
    })
  })

  it('shows validation error for empty password', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/password is required/i)).toBeInTheDocument()
    })
  })

  it('successfully logs in user with valid credentials', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      token: 'test-token-123',
      user_id: 1,
      username: 'testuser',
      email: 'test@example.com',
    }

    vi.mocked(authService.login).mockResolvedValue(mockResponse)

    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'testpass123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'testpass123',
      })
      expect(authService.saveToken).toHaveBeenCalledWith('test-token-123', 1)
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('displays error message for incorrect credentials', async () => {
    const user = userEvent.setup()

    vi.mocked(authService.login).mockRejectedValue({
      response: {
        data: {
          error: 'Incorrect email or password',
        },
        status: 401,
      },
    })

    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'wrong@example.com')
    await user.type(passwordInput, 'wrongpass')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/incorrect email or password/i)).toBeInTheDocument()
    })
  })

  it('displays generic error message for network errors', async () => {
    const user = userEvent.setup()

    vi.mocked(authService.login).mockRejectedValue(new Error('Network error'))

    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'testpass123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/login failed/i)).toBeInTheDocument()
    })
  })

  it('disables submit button while submitting', async () => {
    const user = userEvent.setup()

    vi.mocked(authService.login).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    )

    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'testpass123')
    await user.click(submitButton)

    expect(submitButton).toBeDisabled()
  })

  it('has a link to register page', () => {
    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    )

    const registerLink = screen.getByRole('link', { name: /don't have an account/i })
    expect(registerLink).toBeInTheDocument()
    expect(registerLink).toHaveAttribute('href', '/register')
  })
})
