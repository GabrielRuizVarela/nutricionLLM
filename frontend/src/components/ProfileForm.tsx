import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { profileService } from '@/services/profile'
import type { Profile } from '@/types/api'

const profileSchema = z.object({
  goal: z.string().min(1, 'Goal must be at least 1 character long'),
  dietary_preferences: z.string().min(1, 'Dietary preferences must be at least 1 character long'),
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
        goal: data.goal,
        dietary_preferences: data.dietary_preferences,
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
      const updatedProfile = await profileService.updateProfile(data)
      setProfile(updatedProfile)
      setSuccessMessage('Profile updated successfully!')
    } catch (error) {
      setUpdateError('Failed to update profile. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="w-full max-w-md mx-auto p-6">
        <p className="text-center text-muted-foreground">Loading profile...</p>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="w-full max-w-md mx-auto p-6">
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
    <div className="w-full max-w-md mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Your Profile</h1>
        <div className="text-sm text-muted-foreground space-y-1">
          <p>Username: <span className="font-medium text-foreground">{profile?.username}</span></p>
          <p>Email: <span className="font-medium text-foreground">{profile?.email}</span></p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <div className="space-y-2">
          <Label htmlFor="goal">Goal</Label>
          <Input
            id="goal"
            type="text"
            placeholder="e.g., lose weight, gain muscle"
            {...register('goal')}
            aria-invalid={errors.goal ? 'true' : 'false'}
          />
          {errors.goal && (
            <p className="text-sm text-destructive">{errors.goal.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="dietary_preferences">Dietary Preferences</Label>
          <Input
            id="dietary_preferences"
            type="text"
            placeholder="e.g., vegetarian, vegan, no restrictions"
            {...register('dietary_preferences')}
            aria-invalid={errors.dietary_preferences ? 'true' : 'false'}
          />
          {errors.dietary_preferences && (
            <p className="text-sm text-destructive">{errors.dietary_preferences.message}</p>
          )}
        </div>

        {successMessage && (
          <div className="p-3 text-sm text-green-800 bg-green-100 rounded-md">
            {successMessage}
          </div>
        )}

        {updateError && (
          <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
            {updateError}
          </div>
        )}

        <Button
          type="submit"
          className="w-full"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : 'Save Changes'}
        </Button>
      </form>
    </div>
  )
}
