/**
 * DailyFoodLog Component
 * Displays daily food logs grouped by meal type with macro totals
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import FoodSearchModal from './FoodSearchModal'
import type { FoodLog, DailyNutritionTotals, Profile } from '@/types/api'
import { getFoodLogs, getDailyTotals, deleteFoodLog, formatDate, getTodayDate } from '@/services/foodLogging'
import { profileService } from '@/services/profile'

const MEAL_TYPES = [
  { value: 'breakfast', label: 'Breakfast' },
  { value: 'lunch', label: 'Lunch' },
  { value: 'dinner', label: 'Dinner' },
  { value: 'snack', label: 'Snacks' }
] as const

type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack'

export default function DailyFoodLog() {
  const [selectedDate, setSelectedDate] = useState(getTodayDate())
  const [foodLogs, setFoodLogs] = useState<FoodLog[]>([])
  const [dailyTotals, setDailyTotals] = useState<DailyNutritionTotals | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedMealType, setSelectedMealType] = useState<MealType>('breakfast')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadData()
    loadProfile()
  }, [selectedDate])

  const loadData = async () => {
    setIsLoading(true)
    setError('')

    try {
      const [logs, totals] = await Promise.all([
        getFoodLogs(selectedDate),
        getDailyTotals(selectedDate)
      ])
      setFoodLogs(logs)
      setDailyTotals(totals)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load food logs')
    } finally {
      setIsLoading(false)
    }
  }

  const loadProfile = async () => {
    try {
      const profileData = await profileService.getProfile()
      setProfile(profileData)
    } catch (err) {
      console.error('Failed to load profile:', err)
    }
  }

  const handleAddFood = (mealType: MealType) => {
    setSelectedMealType(mealType)
    setIsModalOpen(true)
  }

  const handleDeleteFood = async (logId: number) => {
    if (!confirm('Are you sure you want to delete this food entry?')) {
      return
    }

    try {
      await deleteFoodLog(logId)
      await loadData() // Reload data after deletion
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete food log')
    }
  }

  const handleDateChange = (direction: 'prev' | 'next') => {
    const currentDate = new Date(selectedDate)
    if (direction === 'prev') {
      currentDate.setDate(currentDate.getDate() - 1)
    } else {
      currentDate.setDate(currentDate.getDate() + 1)
    }
    setSelectedDate(formatDate(currentDate))
  }

  const getLogsForMeal = (mealType: MealType): FoodLog[] => {
    return foodLogs.filter(log => log.meal_type === mealType)
  }

  const getMealTotals = (mealType: MealType) => {
    const logs = getLogsForMeal(mealType)
    return logs.reduce(
      (acc, log) => ({
        calories: acc.calories + log.calories,
        protein: acc.protein + log.protein,
        carbs: acc.carbs + log.carbs,
        fats: acc.fats + log.fats
      }),
      { calories: 0, protein: 0, carbs: 0, fats: 0 }
    )
  }

  const getProgressPercentage = (current: number, target: number | undefined): number => {
    if (!target || target === 0) return 0
    return Math.min((current / target) * 100, 100)
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Loading food logs...</div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Date Navigation */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Button variant="outline" onClick={() => handleDateChange('prev')}>
              ← Previous Day
            </Button>
            <CardTitle className="text-2xl">
              {new Date(selectedDate).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </CardTitle>
            <Button
              variant="outline"
              onClick={() => handleDateChange('next')}
              disabled={selectedDate >= getTodayDate()}
            >
              Next Day →
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Daily Totals */}
      {dailyTotals && (
        <Card>
          <CardHeader>
            <CardTitle>Daily Totals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-6">
              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Calories</div>
                <div className="text-3xl font-bold">{dailyTotals.totals.calories}</div>
                {profile?.daily_calorie_target && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    / {profile.daily_calorie_target} kcal
                  </div>
                )}
                {profile?.daily_calorie_target && (
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${getProgressPercentage(
                          dailyTotals.totals.calories,
                          profile.daily_calorie_target
                        )}%`
                      }}
                    />
                  </div>
                )}
              </div>

              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Protein</div>
                <div className="text-3xl font-bold">{dailyTotals.totals.protein.toFixed(1)}g</div>
                {profile?.daily_protein_target && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    / {profile.daily_protein_target}g
                  </div>
                )}
                {profile?.daily_protein_target && (
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                    <div
                      className="bg-green-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${getProgressPercentage(
                          dailyTotals.totals.protein,
                          profile.daily_protein_target
                        )}%`
                      }}
                    />
                  </div>
                )}
              </div>

              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Carbs</div>
                <div className="text-3xl font-bold">{dailyTotals.totals.carbs.toFixed(1)}g</div>
                {profile?.daily_carbs_target && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    / {profile.daily_carbs_target}g
                  </div>
                )}
                {profile?.daily_carbs_target && (
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                    <div
                      className="bg-yellow-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${getProgressPercentage(
                          dailyTotals.totals.carbs,
                          profile.daily_carbs_target
                        )}%`
                      }}
                    />
                  </div>
                )}
              </div>

              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Fats</div>
                <div className="text-3xl font-bold">{dailyTotals.totals.fats.toFixed(1)}g</div>
                {profile?.daily_fats_target && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    / {profile.daily_fats_target}g
                  </div>
                )}
                {profile?.daily_fats_target && (
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                    <div
                      className="bg-red-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${getProgressPercentage(
                          dailyTotals.totals.fats,
                          profile.daily_fats_target
                        )}%`
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Meal Sections */}
      {MEAL_TYPES.map(({ value, label }) => {
        const mealLogs = getLogsForMeal(value)
        const mealTotals = getMealTotals(value)

        return (
          <Card key={value}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{label}</CardTitle>
                <Button onClick={() => handleAddFood(value)}>
                  + Add Food
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {mealLogs.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                  No foods logged for {label.toLowerCase()} yet
                </p>
              ) : (
                <div className="space-y-3">
                  {mealLogs.map((log) => (
                    <div
                      key={log.id}
                      className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="font-medium">{log.food_detail.description}</div>
                        {log.food_detail.brand_owner && (
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {log.food_detail.brand_owner}
                          </div>
                        )}
                        <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                          {log.quantity_grams}g
                        </div>
                      </div>
                      <div className="flex items-center space-x-6 mr-4">
                        <div className="text-center">
                          <div className="font-bold">{log.calories}</div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">cal</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold">{log.protein.toFixed(1)}g</div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">protein</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold">{log.carbs.toFixed(1)}g</div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">carbs</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold">{log.fats.toFixed(1)}g</div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">fats</div>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteFood(log.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        Delete
                      </Button>
                    </div>
                  ))}

                  {/* Meal Totals */}
                  <div className="border-t border-gray-200 dark:border-gray-700 pt-3 mt-3">
                    <div className="flex items-center justify-between font-bold">
                      <div>{label} Totals</div>
                      <div className="flex space-x-6">
                        <div>{mealTotals.calories} cal</div>
                        <div>{mealTotals.protein.toFixed(1)}g protein</div>
                        <div>{mealTotals.carbs.toFixed(1)}g carbs</div>
                        <div>{mealTotals.fats.toFixed(1)}g fats</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )
      })}

      {/* Error Message */}
      {error && (
        <div className="text-red-600 dark:text-red-400 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
          {error}
        </div>
      )}

      {/* Food Search Modal */}
      <FoodSearchModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        date={selectedDate}
        mealType={selectedMealType}
        onFoodLogged={loadData}
      />
    </div>
  )
}
