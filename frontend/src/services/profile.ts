import axios from 'axios'
import type { Profile, ProfileUpdateRequest } from '@/types/api'

const API_BASE = 'http://localhost:8000/api'

export const profileService = {
  async getProfile(): Promise<Profile> {
    const token = localStorage.getItem('token')
    const response = await axios.get<Profile>(`${API_BASE}/profile/`, {
      headers: {
        Authorization: `Token ${token}`,
      },
    })
    return response.data
  },

  async updateProfile(data: ProfileUpdateRequest): Promise<Profile> {
    const token = localStorage.getItem('token')
    const response = await axios.patch<Profile>(`${API_BASE}/profile/`, data, {
      headers: {
        Authorization: `Token ${token}`,
      },
    })
    return response.data
  },
}
