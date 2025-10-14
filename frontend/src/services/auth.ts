import axios from 'axios'
import type { RegisterRequest, LoginRequest, AuthResponse } from '@/types/api'

const API_BASE = 'http://localhost:8000/api'

export const authService = {
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await axios.post<AuthResponse>(`${API_BASE}/auth/register/`, data)
    return response.data
  },

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await axios.post<AuthResponse>(`${API_BASE}/auth/login/`, data)
    return response.data
  },

  async logout(): Promise<void> {
    const token = localStorage.getItem('token')
    await axios.post(
      `${API_BASE}/auth/logout/`,
      {},
      {
        headers: {
          Authorization: `Token ${token}`,
        },
      }
    )
    localStorage.removeItem('token')
    localStorage.removeItem('user_id')
  },

  saveToken(token: string, userId: number): void {
    localStorage.setItem('token', token)
    localStorage.setItem('user_id', userId.toString())
  },

  getToken(): string | null {
    return localStorage.getItem('token')
  },

  isAuthenticated(): boolean {
    return !!this.getToken()
  },
}
