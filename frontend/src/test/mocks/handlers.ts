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
      nombre: 'Ensalada de Lentejas',
      ingredientes_texto: '1 cup cooked lentils, 1 cucumber, 2 tomatoes, olive oil, lemon',
      pasos_texto: '1. Drain lentils. 2. Chop vegetables. 3. Mix with oil and lemon.',
      calorias: 320,
      proteinas: 18.5,
      carbohidratos: 45.0,
      grasas: 8.2,
      tiempo_min: 10,
      tipo: body.meal_type,
    })
  }),

  http.get(`${API_BASE}/recetas/`, () => {
    return HttpResponse.json([
      {
        id: 1,
        nombre: 'Ensalada de Lentejas',
        ingredientes_texto: 'lentils, cucumber, tomatoes',
        pasos_texto: '1. Cook. 2. Mix.',
        calorias: 320,
        proteinas: 18.5,
        carbohidratos: 45.0,
        grasas: 8.2,
        tiempo_min: 10,
        tipo: 'almuerzo',
        created_at: '2025-01-01T00:00:00Z',
      },
      {
        id: 2,
        nombre: 'Smoothie Verde',
        ingredientes_texto: 'spinach, banana, almond milk',
        pasos_texto: '1. Blend all ingredients.',
        calorias: 150,
        proteinas: 5.0,
        carbohidratos: 25.0,
        grasas: 3.0,
        tiempo_min: 5,
        tipo: 'desayuno',
        created_at: '2025-01-02T00:00:00Z',
      },
    ])
  }),

  http.post(`${API_BASE}/recetas/`, async ({ request }) => {
    const body = await request.json() as {
      nombre: string
      ingredientes_texto: string
      pasos_texto: string
      calorias: number
      proteinas: number
      carbohidratos: number
      grasas: number
      tiempo_min: number
      tipo: string
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
      nombre: 'Ensalada de Lentejas',
      ingredientes_texto: 'lentils, cucumber, tomatoes',
      pasos_texto: '1. Cook. 2. Mix.',
      calorias: 320,
      proteinas: 18.5,
      carbohidratos: 45.0,
      grasas: 8.2,
      tiempo_min: 10,
      tipo: 'almuerzo',
      created_at: '2025-01-01T00:00:00Z',
    })
  }),
]
