import { useState } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
  const [showCustomTime, setShowCustomTime] = useState(false)
  const [instructionsFormat, setInstructionsFormat] = useState<'numbered' | 'bullets'>('numbered')

  const {
    register,
    handleSubmit,
    control,
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

  const formatInstructions = (steps: string) => {
    if (!steps) return []

    // Split by periods followed by space or end of string, or by newlines
    const splitSteps = steps
      .split(/\.\s+|\n+/)
      .map(step => step.trim())
      .filter(step => step.length > 0)

    return splitSteps
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
          <Label>Meal Type</Label>
          <Controller
            name="meal_type"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <div className="grid grid-cols-4 gap-2">
                {[
                  { value: 'breakfast', label: 'Breakfast' },
                  { value: 'lunch', label: 'Lunch' },
                  { value: 'dinner', label: 'Dinner' },
                  { value: 'snack', label: 'Snack' },
                ].map((option) => (
                  <Button
                    key={option.value}
                    type="button"
                    variant={field.value === option.value ? 'default' : 'outline'}
                    onClick={() => field.onChange(option.value)}
                    className="w-full"
                  >
                    {option.label}
                  </Button>
                ))}
              </div>
            )}
          />
          {errors.meal_type && (
            <p className="text-sm text-destructive">{errors.meal_type.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label>Available Time</Label>
          <Controller
            name="available_time"
            control={control}
            defaultValue={0}
            render={({ field }) => (
              <div className="space-y-2">
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { value: 15, label: '15 min' },
                    { value: 30, label: '30 min' },
                    { value: 60, label: '60 min' },
                    { value: -1, label: '60+ min' },
                  ].map((option) => (
                    <Button
                      key={option.value}
                      type="button"
                      variant={
                        (option.value === -1 && showCustomTime) ||
                        (option.value !== -1 && field.value === option.value)
                          ? 'default'
                          : 'outline'
                      }
                      onClick={() => {
                        if (option.value === -1) {
                          setShowCustomTime(true)
                          field.onChange(61)
                        } else {
                          setShowCustomTime(false)
                          field.onChange(option.value)
                        }
                      }}
                      className="w-full"
                    >
                      {option.label}
                    </Button>
                  ))}
                </div>
                {showCustomTime && (
                  <Input
                    type="number"
                    placeholder="Enter minutes"
                    value={field.value || ''}
                    onChange={(e) => field.onChange(Number(e.target.value))}
                    min={61}
                    aria-invalid={errors.available_time ? 'true' : 'false'}
                  />
                )}
              </div>
            )}
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
            <h2 className="text-2xl font-bold">{generatedRecipe.name}</h2>
            <p className="text-sm text-muted-foreground">
              {generatedRecipe.prep_time_minutes} minutes • {generatedRecipe.meal_type}
            </p>
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{generatedRecipe.calories}</p>
              <p className="text-xs text-muted-foreground">Calories</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{generatedRecipe.protein}g</p>
              <p className="text-xs text-muted-foreground">Protein</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{generatedRecipe.carbs}g</p>
              <p className="text-xs text-muted-foreground">Carbs</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{generatedRecipe.fats}g</p>
              <p className="text-xs text-muted-foreground">Fats</p>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Ingredients</h3>
            <p className="text-sm text-muted-foreground">{generatedRecipe.ingredients}</p>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold">Instructions</h3>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant={instructionsFormat === 'numbered' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setInstructionsFormat('numbered')}
                >
                  Numbered
                </Button>
                <Button
                  type="button"
                  variant={instructionsFormat === 'bullets' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setInstructionsFormat('bullets')}
                >
                  Bullets
                </Button>
              </div>
            </div>
            {instructionsFormat === 'numbered' ? (
              <ol className="text-sm text-muted-foreground list-decimal list-inside space-y-1">
                {formatInstructions(generatedRecipe.steps).map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
            ) : (
              <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                {formatInstructions(generatedRecipe.steps).map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ul>
            )}
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
