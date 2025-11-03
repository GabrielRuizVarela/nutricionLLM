import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { recipeService } from '@/services/recipes'
import type { MealSlot, Recipe } from '@/types/api'

interface MealSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  mealSlot: MealSlot | null
  onSelectRecipe: (recipeId: number) => void
}

export default function MealSelectionModal({
  isOpen,
  onClose,
  mealSlot,
  onSelectRecipe,
}: MealSelectionModalProps) {
  const navigate = useNavigate()
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [filteredRecipes, setFilteredRecipes] = useState<Recipe[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadRecipes()
      setSearchQuery('')
    }
  }, [isOpen])

  useEffect(() => {
    filterRecipes()
  }, [recipes, searchQuery, mealSlot])

  const loadRecipes = async () => {
    setIsLoading(true)
    setError('')

    try {
      const data = await recipeService.getRecipes()
      setRecipes(data)
    } catch (err) {
      setError('Failed to load recipes. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const filterRecipes = () => {
    if (!mealSlot) {
      setFilteredRecipes([])
      return
    }

    let filtered = recipes

    // Filter by meal type (prefer matching meal types, but show all)
    // We'll sort matching meal types to the top
    filtered = [...recipes].sort((a, b) => {
      const aMatches = a.meal_type === mealSlot.meal_type
      const bMatches = b.meal_type === mealSlot.meal_type
      if (aMatches && !bMatches) return -1
      if (!aMatches && bMatches) return 1
      return 0
    })

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (recipe) =>
          recipe.name.toLowerCase().includes(query) ||
          recipe.ingredients.toLowerCase().includes(query)
      )
    }

    setFilteredRecipes(filtered)
  }

  const handleSelectRecipe = (recipeId: number) => {
    onSelectRecipe(recipeId)
    onClose()
  }

  const handleGenerateNew = () => {
    // Navigate to recipe generation page
    navigate('/generate')
    onClose()
  }

  if (!mealSlot) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>
            Select Meal for {mealSlot.day_name} {mealSlot.meal_name}
          </DialogTitle>
          <DialogDescription>
            Choose a recipe from your saved recipes or generate a new one
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Search bar */}
          <Input
            placeholder="Search recipes by name or ingredients..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />

          {/* Generate new recipe button */}
          <Button
            onClick={handleGenerateNew}
            className="w-full"
            variant="outline"
          >
            + Generate New Recipe
          </Button>

          {/* Error message */}
          {error && (
            <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
              {error}
            </div>
          )}

          {/* Loading state */}
          {isLoading && (
            <div className="text-center py-8 text-muted-foreground">
              Loading recipes...
            </div>
          )}

          {/* Recipe list */}
          {!isLoading && filteredRecipes.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              {searchQuery ? 'No recipes found matching your search.' : 'No saved recipes yet. Generate your first recipe!'}
            </div>
          )}

          {!isLoading && filteredRecipes.length > 0 && (
            <ScrollArea className="h-[400px] pr-4">
              <div className="space-y-2">
                {filteredRecipes.map((recipe) => (
                  <div
                    key={recipe.id}
                    className="border rounded-lg p-4 hover:bg-muted/50 transition-colors cursor-pointer"
                    onClick={() => handleSelectRecipe(recipe.id!)}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold">{recipe.name}</h4>
                          {recipe.meal_type === mealSlot.meal_type && (
                            <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                              Recommended
                            </span>
                          )}
                        </div>

                        <div className="text-sm text-muted-foreground">
                          <div className="flex items-center gap-4">
                            <span>🔥 {recipe.calories} kcal</span>
                            <span>⏱️ {recipe.prep_time_minutes} min</span>
                            <span className="capitalize">{recipe.meal_type}</span>
                          </div>
                          <div className="mt-1">
                            P: {recipe.protein}g • C: {recipe.carbs}g • F: {recipe.fats}g
                          </div>
                        </div>

                        <p className="text-xs text-muted-foreground line-clamp-2">
                          {recipe.ingredients}
                        </p>
                      </div>

                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleSelectRecipe(recipe.id!)
                        }}
                      >
                        Select
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}

          {/* Action buttons */}
          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
