import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import RegisterForm from './RegisterForm'
import { authService } from '@/services/auth'

// Mock the auth service
vi.mock('@/services/auth', () => ({
  authService: {
    register: vi.fn(),
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

describe('RegisterForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders registration form with all fields', () => {
    render(
      <BrowserRouter>
        <RegisterForm />
      </BrowserRouter>
    )

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument()
  })

  it('shows validation error for invalid email', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <RegisterForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const submitButton = screen.getByRole('button', { name: /register/i })

    await user.type(emailInput, 'invalid-email')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/invalid email/i)).toBeInTheDocument()
    })
  })

  it('shows validation error for short username', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <RegisterForm />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/username/i)
    const submitButton = screen.getByRole('button', { name: /register/i })

    await user.type(usernameInput, 'ab')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/username must be at least 3 characters/i)).toBeInTheDocument()
    })
  })

  it('shows validation error for short password', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <RegisterForm />
      </BrowserRouter>
    )

    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /register/i })

    await user.type(passwordInput, 'short')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument()
    })
  })

  it('successfully registers user with valid data', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      token: 'test-token-123',
      user_id: 1,
      username: 'testuser',
      email: 'test@example.com',
    }

    vi.mocked(authService.register).mockResolvedValue(mockResponse)

    render(
      <BrowserRouter>
        <RegisterForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /register/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'testpass123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(authService.register).toHaveBeenCalledWith({
        email: 'test@example.com',
        username: 'testuser',
        password: 'testpass123',
      })
      expect(authService.saveToken).toHaveBeenCalledWith('test-token-123', 1)
      expect(mockNavigate).toHaveBeenCalledWith('/login')
    })
  })

  it('displays error message when email already exists', async () => {
    const user = userEvent.setup()

    vi.mocked(authService.register).mockRejectedValue({
      response: {
        data: {
          email: ['An account with this email already exists.'],
        },
        status: 400,
      },
    })

    render(
      <BrowserRouter>
        <RegisterForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /register/i })

    await user.type(emailInput, 'existing@example.com')
    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'testpass123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/an account with this email already exists/i)).toBeInTheDocument()
    })
  })

  it('displays generic error message for network errors', async () => {
    const user = userEvent.setup()

    vi.mocked(authService.register).mockRejectedValue(new Error('Network error'))

    render(
      <BrowserRouter>
        <RegisterForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /register/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'testpass123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/registration failed/i)).toBeInTheDocument()
    })
  })

  it('disables submit button while submitting', async () => {
    const user = userEvent.setup()

    vi.mocked(authService.register).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    )

    render(
      <BrowserRouter>
        <RegisterForm />
      </BrowserRouter>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /register/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'testpass123')
    await user.click(submitButton)

    expect(submitButton).toBeDisabled()
  })

  it('has a link to login page', () => {
    render(
      <BrowserRouter>
        <RegisterForm />
      </BrowserRouter>
    )

    const loginLink = screen.getByRole('link', { name: /already have an account/i })
    expect(loginLink).toBeInTheDocument()
    expect(loginLink).toHaveAttribute('href', '/login')
  })
})
