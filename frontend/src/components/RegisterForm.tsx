import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { authService } from '@/services/auth'

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  username: z.string().min(3, 'Username must be at least 3 characters long'),
  password: z.string().min(8, 'Password must be at least 8 characters long'),
})

type RegisterFormData = z.infer<typeof registerSchema>

interface ErrorResponse {
  response?: {
    data?: {
      [key: string]: string[]
    }
    status?: number
  }
}

export default function RegisterForm() {
  const navigate = useNavigate()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string>('')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterFormData) => {
    setIsSubmitting(true)
    setServerError('')

    try {
      const response = await authService.register(data)
      authService.saveToken(response.token, response.user_id)
      navigate('/login')
    } catch (error) {
      const err = error as ErrorResponse
      if (err.response?.data) {
        // Handle field-specific errors from backend
        const errorData = err.response.data
        if (errorData.email) {
          setServerError(errorData.email[0])
        } else if (errorData.password) {
          setServerError(errorData.password[0])
        } else if (errorData.username) {
          setServerError(errorData.username[0])
        } else {
          setServerError('Registration failed. Please try again.')
        }
      } else {
        setServerError('Registration failed. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-md mx-auto space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-bold">Create an account</h1>
        <p className="text-muted-foreground">
          Enter your information to get started
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            {...register('email')}
            aria-invalid={errors.email ? 'true' : 'false'}
          />
          {errors.email && (
            <p className="text-sm text-destructive">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="username">Username</Label>
          <Input
            id="username"
            type="text"
            placeholder="johndoe"
            {...register('username')}
            aria-invalid={errors.username ? 'true' : 'false'}
          />
          {errors.username && (
            <p className="text-sm text-destructive">{errors.username.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            {...register('password')}
            aria-invalid={errors.password ? 'true' : 'false'}
          />
          {errors.password && (
            <p className="text-sm text-destructive">{errors.password.message}</p>
          )}
        </div>

        {serverError && (
          <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
            {serverError}
          </div>
        )}

        <Button
          type="submit"
          className="w-full"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating account...' : 'Register'}
        </Button>
      </form>

      <p className="text-center text-sm">
        <Link to="/login" className="text-muted-foreground hover:text-primary hover:underline">
          Already have an account? Sign in
        </Link>
      </p>
    </div>
  )
}
