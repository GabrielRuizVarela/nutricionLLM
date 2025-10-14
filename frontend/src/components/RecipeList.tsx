import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { recipeService } from '@/services/recipes'
import type { Recipe } from '@/types/api'

export default function RecipeList() {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    loadRecipes()
  }, [])

  const loadRecipes = async () => {
    setIsLoading(true)
    setError('')

    try {
      const data = await recipeService.getRecipes()
      setRecipes(data)
    } catch (err) {
      setError('Failed to load recipes. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="w-full max-w-6xl mx-auto p-6">
        <p className="text-center text-muted-foreground">Loading recipes...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full max-w-6xl mx-auto p-6 space-y-4">
        <div className="p-4 text-sm text-destructive bg-destructive/10 rounded-md">
          {error}
        </div>
        <Button onClick={loadRecipes}>Try Again</Button>
      </div>
    )
  }

  if (recipes.length === 0) {
    return (
      <div className="w-full max-w-6xl mx-auto p-6 text-center space-y-4">
        <h2 className="text-2xl font-bold">No recipes found</h2>
        <p className="text-muted-foreground">
          You haven't saved any recipes yet. Start generating recipes to build your collection!
        </p>
        <Link to="/generate">
          <Button>Generate Your First Recipe</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Your Saved Recipes</h1>
        <p className="text-muted-foreground">
          {recipes.length} {recipes.length === 1 ? 'recipe' : 'recipes'} saved
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {recipes.map((recipe) => (
          <article
            key={recipe.id}
            className="border rounded-lg p-6 space-y-4 hover:shadow-lg transition-shadow"
          >
            <div>
              <h2 className="text-xl font-bold">{recipe.nombre}</h2>
              <p className="text-sm text-muted-foreground">
                {recipe.tiempo_min} minutes • {recipe.tipo}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-lg font-bold text-primary">{recipe.calorias}</p>
                <p className="text-xs text-muted-foreground">Calories</p>
              </div>
              <div>
                <p className="text-lg font-bold text-primary">{recipe.proteinas}g</p>
                <p className="text-xs text-muted-foreground">Protein</p>
              </div>
              <div>
                <p className="text-lg font-bold text-primary">{recipe.carbohidratos}g</p>
                <p className="text-xs text-muted-foreground">Carbs</p>
              </div>
              <div>
                <p className="text-lg font-bold text-primary">{recipe.grasas}g</p>
                <p className="text-xs text-muted-foreground">Fats</p>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold mb-1">Ingredients</h3>
              <p className="text-sm text-muted-foreground line-clamp-2">
                {recipe.ingredientes_texto}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-semibold mb-1">Instructions</h3>
              <p className="text-sm text-muted-foreground line-clamp-3">
                {recipe.pasos_texto}
              </p>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
