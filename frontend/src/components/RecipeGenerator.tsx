import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { recipeService } from '@/services/recipes'
import type { Recipe } from '@/types/api'

const recipeGenerateSchema = z.object({
  meal_type: z.string().min(1, 'Please select a meal type'),
  available_time: z.coerce.number().min(1, 'Time must be at least 1 minute'),
})

type RecipeGenerateFormData = z.infer<typeof recipeGenerateSchema>

export default function RecipeGenerator() {
  const [generatedRecipe, setGeneratedRecipe] = useState<Recipe | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [generateError, setGenerateError] = useState<string>('')
  const [saveSuccess, setSaveSuccess] = useState<string>('')
  const [saveError, setSaveError] = useState<string>('')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RecipeGenerateFormData>({
    resolver: zodResolver(recipeGenerateSchema),
  })

  const onSubmit = async (data: RecipeGenerateFormData) => {
    setIsGenerating(true)
    setGenerateError('')
    setGeneratedRecipe(null)
    setSaveSuccess('')
    setSaveError('')

    try {
      const recipe = await recipeService.generateRecipe(data)
      setGeneratedRecipe(recipe)
    } catch (error) {
      setGenerateError('Failed to generate recipe. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSaveRecipe = async () => {
    if (!generatedRecipe) return

    setIsSaving(true)
    setSaveSuccess('')
    setSaveError('')

    try {
      await recipeService.saveRecipe(generatedRecipe)
      setSaveSuccess('Recipe saved successfully!')
    } catch (error) {
      setSaveError('Failed to save recipe. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Generate Recipe</h1>
        <p className="text-muted-foreground">
          Get AI-powered recipe suggestions based on your preferences
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <div className="space-y-2">
          <Label htmlFor="meal_type">Meal Type</Label>
          <Select
            id="meal_type"
            {...register('meal_type')}
            aria-invalid={errors.meal_type ? 'true' : 'false'}
          >
            <option value="">Select meal type</option>
            <option value="desayuno">Breakfast</option>
            <option value="almuerzo">Lunch</option>
            <option value="cena">Dinner</option>
            <option value="snack">Snack</option>
          </Select>
          {errors.meal_type && (
            <p className="text-sm text-destructive">{errors.meal_type.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="available_time">Available Time (minutes)</Label>
          <Input
            id="available_time"
            type="number"
            placeholder="e.g., 30"
            {...register('available_time')}
            aria-invalid={errors.available_time ? 'true' : 'false'}
          />
          {errors.available_time && (
            <p className="text-sm text-destructive">{errors.available_time.message}</p>
          )}
        </div>

        {generateError && (
          <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
            {generateError}
          </div>
        )}

        <Button
          type="submit"
          className="w-full"
          disabled={isGenerating}
        >
          {isGenerating ? 'Generating recipe...' : 'Generate Recipe'}
        </Button>
      </form>

      {generatedRecipe && (
        <div className="border rounded-lg p-6 space-y-4">
          <div>
            <h2 className="text-2xl font-bold">{generatedRecipe.nombre}</h2>
            <p className="text-sm text-muted-foreground">
              {generatedRecipe.tiempo_min} minutes • {generatedRecipe.tipo}
            </p>
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{generatedRecipe.calorias}</p>
              <p className="text-xs text-muted-foreground">Calories</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{generatedRecipe.proteinas}g</p>
              <p className="text-xs text-muted-foreground">Protein</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{generatedRecipe.carbohidratos}g</p>
              <p className="text-xs text-muted-foreground">Carbs</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{generatedRecipe.grasas}g</p>
              <p className="text-xs text-muted-foreground">Fats</p>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Ingredients</h3>
            <p className="text-sm text-muted-foreground">{generatedRecipe.ingredientes_texto}</p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Instructions</h3>
            <p className="text-sm text-muted-foreground whitespace-pre-line">
              {generatedRecipe.pasos_texto}
            </p>
          </div>

          {saveSuccess && (
            <div className="p-3 text-sm text-green-800 bg-green-100 rounded-md">
              {saveSuccess}
            </div>
          )}

          {saveError && (
            <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
              {saveError}
            </div>
          )}

          <Button
            onClick={handleSaveRecipe}
            className="w-full"
            disabled={isSaving}
            variant="secondary"
          >
            {isSaving ? 'Saving...' : 'Save Recipe'}
          </Button>
        </div>
      )}
    </div>
  )
}
