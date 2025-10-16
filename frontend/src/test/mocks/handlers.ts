import { http, HttpResponse } from 'msw'

const API_BASE = 'http://localhost:8000/api'

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE}/auth/register/`, async ({ request }) => {
    const body = await request.json() as { email: string; username: string; password: string }

    if (body.email === 'existing@example.com') {
      return HttpResponse.json(
        { email: ['An account with this email already exists.'] },
        { status: 400 }
      )
    }

    if (body.password && body.password.length < 8) {
      return HttpResponse.json(
        { password: ['Password must be at least 8 characters long.'] },
        { status: 400 }
      )
    }

    return HttpResponse.json({
      token: 'test-token-123',
      user_id: 1,
      username: body.username,
      email: body.email,
    }, { status: 201 })
  }),

  http.post(`${API_BASE}/auth/login/`, async ({ request }) => {
    const body = await request.json() as { email: string; password: string }

    if (body.email === 'test@example.com' && body.password === 'testpass123') {
      return HttpResponse.json({
        token: 'test-token-123',
        user_id: 1,
        username: 'testuser',
        email: 'test@example.com',
      })
    }

    return HttpResponse.json(
      { error: 'Incorrect email or password' },
      { status: 401 }
    )
  }),

  http.post(`${API_BASE}/auth/logout/`, () => {
    return HttpResponse.json({ message: 'Successfully logged out' })
  }),

  // Profile endpoints
  http.get(`${API_BASE}/profile/`, () => {
    return HttpResponse.json({
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      goal: 'lose weight',
      dietary_preferences: 'vegetarian',
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    })
  }),

  http.patch(`${API_BASE}/profile/`, async ({ request }) => {
    const body = await request.json() as { goal?: string; dietary_preferences?: string }

    return HttpResponse.json({
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      goal: body.goal || 'lose weight',
      dietary_preferences: body.dietary_preferences || 'vegetarian',
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    })
  }),

  // Recipe endpoints
  http.post(`${API_BASE}/recipes/generate/`, async ({ request }) => {
    const body = await request.json() as { meal_type: string; available_time: number }

    if (!body.meal_type || !body.available_time) {
      return HttpResponse.json(
        { error: 'meal_type and available_time are required' },
        { status: 400 }
      )
    }

    return HttpResponse.json({
      name: 'Lentil Salad',
      ingredients: '1 cup cooked lentils, 1 cucumber, 2 tomatoes, olive oil, lemon',
      steps: '1. Drain lentils. 2. Chop vegetables. 3. Mix with oil and lemon.',
      calories: 320,
      protein: 18.5,
      carbs: 45.0,
      fats: 8.2,
      prep_time_minutes: 10,
      meal_type: body.meal_type,
    })
  }),

  http.get(`${API_BASE}/recetas/`, () => {
    return HttpResponse.json([
      {
        id: 1,
        name: 'Lentil Salad',
        ingredients: 'lentils, cucumber, tomatoes',
        steps: '1. Cook. 2. Mix.',
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
        name: 'Green Smoothie',
        ingredients: 'spinach, banana, almond milk',
        steps: '1. Blend all ingredients.',
        calories: 150,
        protein: 5.0,
        carbs: 25.0,
        fats: 3.0,
        prep_time_minutes: 5,
        meal_type: 'breakfast',
        created_at: '2025-01-02T00:00:00Z',
      },
    ])
  }),

  http.post(`${API_BASE}/recetas/`, async ({ request }) => {
    const body = await request.json() as {
      name: string
      ingredients: string
      steps: string
      calories: number
      protein: number
      carbs: number
      fats: number
      prep_time_minutes: number
      meal_type: string
    }

    return HttpResponse.json(
      {
        id: 3,
        ...body,
        created_at: new Date().toISOString(),
      },
      { status: 201 }
    )
  }),

  http.get(`${API_BASE}/recetas/:id/`, ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      name: 'Lentil Salad',
      ingredients: 'lentils, cucumber, tomatoes',
      steps: '1. Cook. 2. Mix.',
      calories: 320,
      protein: 18.5,
      carbs: 45.0,
      fats: 8.2,
      prep_time_minutes: 10,
      meal_type: 'lunch',
      created_at: '2025-01-01T00:00:00Z',
    })
  }),
]
