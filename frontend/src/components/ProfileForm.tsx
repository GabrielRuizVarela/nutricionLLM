import { useState, useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { profileService } from '@/services/profile'
import type { Profile } from '@/types/api'

const profileSchema = z.object({
  // Personal Information
  age: z.number().min(1).max(120).optional().or(z.literal('')),
  weight_kg: z.number().min(1).max(500).optional().or(z.literal('')),
  height_cm: z.number().min(1).max(300).optional().or(z.literal('')),
  gender: z.string().optional(),
  activity_level: z.string().optional(),

  // Dietary Information
  goal: z.string().optional(),
  dietary_preferences: z.string().optional(),
  allergies: z.string().optional(),
  dislikes: z.string().optional(),

  // Recipe Preferences
  cuisine_preferences: z.string().optional(),
  cooking_skill_level: z.string().optional(),
  spice_preference: z.string().optional(),

  // Ingredient Management
  preferred_ingredients: z.string().optional(),
  available_ingredients: z.string().optional(),

  // Nutritional Targets
  daily_calorie_target: z.number().min(0).optional().or(z.literal('')),
  daily_protein_target: z.number().min(0).optional().or(z.literal('')),
  daily_carbs_target: z.number().min(0).optional().or(z.literal('')),
  daily_fats_target: z.number().min(0).optional().or(z.literal('')),
})

type ProfileFormData = z.infer<typeof profileSchema>

export default function ProfileForm() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [loadError, setLoadError] = useState<string>('')
  const [successMessage, setSuccessMessage] = useState<string>('')
  const [updateError, setUpdateError] = useState<string>('')

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
    reset,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
  })

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    setIsLoading(true)
    setLoadError('')

    try {
      const data = await profileService.getProfile()
      setProfile(data)
      reset({
        age: data.age || '',
        weight_kg: data.weight_kg || '',
        height_cm: data.height_cm || '',
        gender: data.gender || '',
        activity_level: data.activity_level || '',
        goal: data.goal || '',
        dietary_preferences: data.dietary_preferences || '',
        allergies: data.allergies || '',
        dislikes: data.dislikes || '',
        cuisine_preferences: data.cuisine_preferences || '',
        cooking_skill_level: data.cooking_skill_level || 'beginner',
        spice_preference: data.spice_preference || 'mild',
        preferred_ingredients: data.preferred_ingredients || '',
        available_ingredients: data.available_ingredients || '',
        daily_calorie_target: data.daily_calorie_target || '',
        daily_protein_target: data.daily_protein_target || '',
        daily_carbs_target: data.daily_carbs_target || '',
        daily_fats_target: data.daily_fats_target || '',
      })
    } catch (error) {
      setLoadError('Failed to load profile. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const onSubmit = async (data: ProfileFormData) => {
    setIsSubmitting(true)
    setUpdateError('')
    setSuccessMessage('')

    try {
      // Convert empty strings to undefined for optional number fields
      const payload = {
        ...data,
        age: data.age === '' ? undefined : data.age,
        weight_kg: data.weight_kg === '' ? undefined : data.weight_kg,
        height_cm: data.height_cm === '' ? undefined : data.height_cm,
        daily_calorie_target: data.daily_calorie_target === '' ? undefined : data.daily_calorie_target,
        daily_protein_target: data.daily_protein_target === '' ? undefined : data.daily_protein_target,
        daily_carbs_target: data.daily_carbs_target === '' ? undefined : data.daily_carbs_target,
        daily_fats_target: data.daily_fats_target === '' ? undefined : data.daily_fats_target,
      }

      const updatedProfile = await profileService.updateProfile(payload)
      setProfile(updatedProfile)
      setSuccessMessage('Profile updated successfully!')

      // Scroll to top to show success message
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (error) {
      setUpdateError('Failed to update profile. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <p className="text-center text-muted-foreground">Loading profile...</p>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="p-4 text-sm text-destructive bg-destructive/10 rounded-md">
          {loadError}
        </div>
        <Button onClick={loadProfile} className="mt-4">
          Try Again
        </Button>
      </div>
    )
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Your Profile</h1>
        <div className="text-sm text-muted-foreground space-y-1">
          <p>Username: <span className="font-medium text-foreground">{profile?.username}</span></p>
          <p>Email: <span className="font-medium text-foreground">{profile?.email}</span></p>
        </div>
      </div>

      {successMessage && (
        <div className="p-3 text-sm text-green-800 bg-green-100 dark:text-green-100 dark:bg-green-900/30 rounded-md">
          {successMessage}
        </div>
      )}

      {updateError && (
        <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
          {updateError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Tabs defaultValue="personal" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="personal">Personal</TabsTrigger>
            <TabsTrigger value="dietary">Dietary</TabsTrigger>
            <TabsTrigger value="preferences">Preferences</TabsTrigger>
            <TabsTrigger value="goals">Goals</TabsTrigger>
          </TabsList>

          {/* Personal Information Tab */}
          <TabsContent value="personal" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="age">Age (years)</Label>
                <Input
                  id="age"
                  type="number"
                  placeholder="e.g., 30"
                  {...register('age', { valueAsNumber: true })}
                />
                {errors.age && (
                  <p className="text-sm text-destructive">{errors.age.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="weight_kg">Weight (kg)</Label>
                <Input
                  id="weight_kg"
                  type="number"
                  step="0.1"
                  placeholder="e.g., 70"
                  {...register('weight_kg', { valueAsNumber: true })}
                />
                {errors.weight_kg && (
                  <p className="text-sm text-destructive">{errors.weight_kg.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="height_cm">Height (cm)</Label>
                <Input
                  id="height_cm"
                  type="number"
                  placeholder="e.g., 175"
                  {...register('height_cm', { valueAsNumber: true })}
                />
                {errors.height_cm && (
                  <p className="text-sm text-destructive">{errors.height_cm.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="gender">Gender</Label>
                <Controller
                  name="gender"
                  control={control}
                  render={({ field }) => (
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        { value: 'male', label: 'Male' },
                        { value: 'female', label: 'Female' },
                        { value: 'other', label: 'Other' },
                        { value: 'prefer_not_to_say', label: 'Prefer not to say' },
                      ].map((option) => (
                        <Button
                          key={option.value}
                          type="button"
                          variant={field.value === option.value ? 'default' : 'outline'}
                          onClick={() => field.onChange(option.value)}
                          className="text-xs h-9"
                        >
                          {option.label}
                        </Button>
                      ))}
                    </div>
                  )}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Activity Level</Label>
              <Controller
                name="activity_level"
                control={control}
                render={({ field }) => (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    {[
                      { value: 'sedentary', label: 'Sedentary', desc: 'Little/no exercise' },
                      { value: 'lightly_active', label: 'Lightly Active', desc: '1-3 days/week' },
                      { value: 'moderately_active', label: 'Moderately Active', desc: '3-5 days/week' },
                      { value: 'very_active', label: 'Very Active', desc: '6-7 days/week' },
                      { value: 'extremely_active', label: 'Extremely Active', desc: 'Physical job/2x day' },
                    ].map((option) => (
                      <Button
                        key={option.value}
                        type="button"
                        variant={field.value === option.value ? 'default' : 'outline'}
                        onClick={() => field.onChange(option.value)}
                        className="flex flex-col h-auto py-3"
                      >
                        <span className="font-semibold text-sm">{option.label}</span>
                        <span className="text-xs opacity-80">{option.desc}</span>
                      </Button>
                    ))}
                  </div>
                )}
              />
            </div>

            {/* Calculated Values */}
            {profile?.bmr && (
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <h3 className="font-semibold mb-2">Calculated Metrics</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">BMR:</span>
                    <span className="ml-2 font-semibold">{profile.bmr} kcal/day</span>
                  </div>
                  {profile.tdee && (
                    <div>
                      <span className="text-muted-foreground">TDEE:</span>
                      <span className="ml-2 font-semibold">{profile.tdee} kcal/day</span>
                    </div>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  BMR = Basal Metabolic Rate (calories at rest) | TDEE = Total Daily Energy Expenditure
                </p>
              </div>
            )}
          </TabsContent>

          {/* Dietary Information Tab */}
          <TabsContent value="dietary" className="space-y-4">
            <div className="space-y-2">
              <Label>Primary Goal</Label>
              <Controller
                name="goal"
                control={control}
                render={({ field }) => (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {[
                      { value: 'lose_weight', label: 'Lose Weight' },
                      { value: 'gain_weight', label: 'Gain Weight' },
                      { value: 'maintain_weight', label: 'Maintain Weight' },
                      { value: 'gain_muscle', label: 'Gain Muscle' },
                      { value: 'improve_health', label: 'Improve Health' },
                    ].map((option) => (
                      <Button
                        key={option.value}
                        type="button"
                        variant={field.value === option.value ? 'default' : 'outline'}
                        onClick={() => field.onChange(option.value)}
                      >
                        {option.label}
                      </Button>
                    ))}
                  </div>
                )}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="dietary_preferences">Dietary Preferences</Label>
              <Input
                id="dietary_preferences"
                type="text"
                placeholder="e.g., vegetarian, vegan, keto, paleo"
                {...register('dietary_preferences')}
              />
              <p className="text-xs text-muted-foreground">
                Enter any dietary preferences or restrictions (comma-separated)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allergies" className="text-destructive">
                ⚠️ Allergies (Critical)
              </Label>
              <Input
                id="allergies"
                type="text"
                placeholder="e.g., peanuts, shellfish, dairy"
                {...register('allergies')}
                className="border-destructive/50 focus:border-destructive"
              />
              <p className="text-xs text-destructive">
                These ingredients will be STRICTLY avoided in all recipes
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dislikes">Dislikes</Label>
              <Input
                id="dislikes"
                type="text"
                placeholder="e.g., mushrooms, cilantro, olives"
                {...register('dislikes')}
              />
              <p className="text-xs text-muted-foreground">
                Ingredients you prefer to avoid (will be avoided when possible)
              </p>
            </div>
          </TabsContent>

          {/* Recipe Preferences Tab */}
          <TabsContent value="preferences" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="cuisine_preferences">Preferred Cuisines</Label>
              <Input
                id="cuisine_preferences"
                type="text"
                placeholder="e.g., Italian, Mexican, Asian, Mediterranean"
                {...register('cuisine_preferences')}
              />
              <p className="text-xs text-muted-foreground">
                Your favorite types of cuisine (comma-separated)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="preferred_ingredients">Preferred Ingredients</Label>
              <Input
                id="preferred_ingredients"
                type="text"
                placeholder="e.g., chicken, rice, broccoli, olive oil, garlic"
                {...register('preferred_ingredients')}
              />
              <p className="text-xs text-muted-foreground">
                Ingredients you like to use regularly - these will be prioritized in recipe generation
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="available_ingredients">Available Ingredients</Label>
              <Input
                id="available_ingredients"
                type="text"
                placeholder="e.g., eggs, tomatoes, pasta, cheese, onions"
                {...register('available_ingredients')}
              />
              <p className="text-xs text-muted-foreground">
                Ingredients currently in your pantry - recipes will try to use these when possible
              </p>
            </div>

            <div className="space-y-2">
              <Label>Cooking Skill Level</Label>
              <Controller
                name="cooking_skill_level"
                control={control}
                render={({ field }) => (
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { value: 'beginner', label: 'Beginner', desc: 'Simple recipes' },
                      { value: 'intermediate', label: 'Intermediate', desc: 'Moderate complexity' },
                      { value: 'advanced', label: 'Advanced', desc: 'Complex techniques' },
                    ].map((option) => (
                      <Button
                        key={option.value}
                        type="button"
                        variant={field.value === option.value ? 'default' : 'outline'}
                        onClick={() => field.onChange(option.value)}
                        className="flex flex-col h-auto py-3"
                      >
                        <span className="font-semibold">{option.label}</span>
                        <span className="text-xs opacity-80">{option.desc}</span>
                      </Button>
                    ))}
                  </div>
                )}
              />
            </div>

            <div className="space-y-2">
              <Label>Spice Preference</Label>
              <Controller
                name="spice_preference"
                control={control}
                render={({ field }) => (
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { value: 'mild', label: 'Mild', icon: '😊' },
                      { value: 'medium', label: 'Medium', icon: '🌶️' },
                      { value: 'spicy', label: 'Spicy', icon: '🔥' },
                    ].map((option) => (
                      <Button
                        key={option.value}
                        type="button"
                        variant={field.value === option.value ? 'default' : 'outline'}
                        onClick={() => field.onChange(option.value)}
                        className="flex items-center gap-2"
                      >
                        <span>{option.icon}</span>
                        <span>{option.label}</span>
                      </Button>
                    ))}
                  </div>
                )}
              />
            </div>
          </TabsContent>

          {/* Nutritional Goals Tab */}
          <TabsContent value="goals" className="space-y-4">
            <div className="mb-4 p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">
                Set your daily nutritional targets. These will be divided across your meals for better recipe personalization.
                {profile?.tdee && (
                  <span className="block mt-2 font-semibold">
                    Recommended daily calories based on your TDEE: {profile.tdee} kcal
                  </span>
                )}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="daily_calorie_target">Daily Calories (kcal)</Label>
                <Input
                  id="daily_calorie_target"
                  type="number"
                  placeholder={profile?.tdee ? `e.g., ${profile.tdee}` : "e.g., 2000"}
                  {...register('daily_calorie_target', { valueAsNumber: true })}
                />
                {errors.daily_calorie_target && (
                  <p className="text-sm text-destructive">{errors.daily_calorie_target.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="daily_protein_target">Daily Protein (g)</Label>
                <Input
                  id="daily_protein_target"
                  type="number"
                  placeholder="e.g., 150"
                  {...register('daily_protein_target', { valueAsNumber: true })}
                />
                {errors.daily_protein_target && (
                  <p className="text-sm text-destructive">{errors.daily_protein_target.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="daily_carbs_target">Daily Carbs (g)</Label>
                <Input
                  id="daily_carbs_target"
                  type="number"
                  placeholder="e.g., 200"
                  {...register('daily_carbs_target', { valueAsNumber: true })}
                />
                {errors.daily_carbs_target && (
                  <p className="text-sm text-destructive">{errors.daily_carbs_target.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="daily_fats_target">Daily Fats (g)</Label>
                <Input
                  id="daily_fats_target"
                  type="number"
                  placeholder="e.g., 65"
                  {...register('daily_fats_target', { valueAsNumber: true })}
                />
                {errors.daily_fats_target && (
                  <p className="text-sm text-destructive">{errors.daily_fats_target.message}</p>
                )}
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-6 flex justify-end">
          <Button
            type="submit"
            className="w-full md:w-auto"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </div>
  )
}
