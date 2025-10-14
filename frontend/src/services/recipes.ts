import axios from 'axios'
import type { Recipe, RecipeGenerateRequest } from '@/types/api'

const API_BASE = 'http://localhost:8000/api'

export const recipeService = {
  async generateRecipe(data: RecipeGenerateRequest): Promise<Recipe> {
    const token = localStorage.getItem('token')
    const response = await axios.post<Recipe>(`${API_BASE}/recipes/generate/`, data, {
      headers: {
        Authorization: `Token ${token}`,
      },
    })
    return response.data
  },

  async getRecipes(): Promise<Recipe[]> {
    const token = localStorage.getItem('token')
    const response = await axios.get<Recipe[]>(`${API_BASE}/recetas/`, {
      headers: {
        Authorization: `Token ${token}`,
      },
    })
    return response.data
  },

  async saveRecipe(recipe: Recipe): Promise<Recipe> {
    const token = localStorage.getItem('token')
    const response = await axios.post<Recipe>(`${API_BASE}/recetas/`, recipe, {
      headers: {
        Authorization: `Token ${token}`,
      },
    })
    return response.data
  },

  async getRecipeById(id: number): Promise<Recipe> {
    const token = localStorage.getItem('token')
    const response = await axios.get<Recipe>(`${API_BASE}/recetas/${id}/`, {
      headers: {
        Authorization: `Token ${token}`,
      },
    })
    return response.data
  },
}
