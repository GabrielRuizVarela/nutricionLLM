import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import MealSlotCard from '@/components/MealSlotCard'
import MealSelectionModal from '@/components/MealSelectionModal'
import { mealPlanningService } from '@/services/mealPlanning'
import type { MealPlan, MealSlot } from '@/types/api'

export default function WeeklyMealPlanner() {
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [currentDate, setCurrentDate] = useState(new Date())
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedSlot, setSelectedSlot] = useState<MealSlot | null>(null)

  useEffect(() => {
    loadMealPlan()
  }, [currentDate])

  const loadMealPlan = async () => {
    setIsLoading(true)
    setError('')

    try {
      const dateStr = formatDate(currentDate)
      const plan = await mealPlanningService.getByDate(dateStr)
      setMealPlan(plan)
    } catch (err) {
      setError('Failed to load meal plan. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const navigateWeek = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate)
    newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7))
    setCurrentDate(newDate)
  }

  const goToCurrentWeek = () => {
    setCurrentDate(new Date())
  }

  const formatDate = (date: Date): string => {
    return date.toISOString().split('T')[0]
  }

  const handleAddMeal = (mealSlot: MealSlot) => {
    setSelectedSlot(mealSlot)
    setIsModalOpen(true)
  }

  const handleSelectRecipe = async (recipeId: number) => {
    if (!selectedSlot) return

    try {
      const updated = await mealPlanningService.updateMealSlot(selectedSlot.id, {
        recipe: recipeId,
      })

      // Update the meal plan state
      if (mealPlan) {
        const updatedSlots = mealPlan.meal_slots.map(slot =>
          slot.id === updated.id ? updated : slot
        )
        setMealPlan({ ...mealPlan, meal_slots: updatedSlots })
      }

      setError('')
    } catch (err) {
      console.error('Failed to assign recipe:', err)
      setError('Failed to assign recipe. Please try again.')
    }
  }

  const handleClearMeal = async (mealSlot: MealSlot) => {
    try {
      const updated = await mealPlanningService.clearMealSlot(mealSlot.id)

      // Update the meal plan state
      if (mealPlan) {
        const updatedSlots = mealPlan.meal_slots.map(slot =>
          slot.id === updated.id ? updated : slot
        )
        setMealPlan({ ...mealPlan, meal_slots: updatedSlots })
      }
    } catch (err) {
      console.error('Failed to clear meal slot:', err)
      setError('Failed to clear meal. Please try again.')
    }
  }

  const getMealSlotsByDay = (dayOfWeek: number) => {
    if (!mealPlan) return []
    return mealPlan.meal_slots
      .filter(slot => slot.day_of_week === dayOfWeek)
      .sort((a, b) => {
        const mealOrder = { breakfast: 0, lunch: 1, dinner: 2 }
        return mealOrder[a.meal_type] - mealOrder[b.meal_type]
      })
  }

  const getDailyTotals = (dayOfWeek: number) => {
    const slots = getMealSlotsByDay(dayOfWeek)
    return slots.reduce(
      (totals, slot) => {
        if (slot.recipe_detail) {
          totals.calories += slot.recipe_detail.calories
          totals.protein += slot.recipe_detail.protein
          totals.carbs += slot.recipe_detail.carbs
          totals.fats += slot.recipe_detail.fats
        }
        return totals
      },
      { calories: 0, protein: 0, carbs: 0, fats: 0 }
    )
  }

  if (isLoading) {
    return (
      <div className="w-full max-w-7xl mx-auto p-6">
        <p className="text-center text-muted-foreground">Loading meal plan...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full max-w-7xl mx-auto p-6">
        <div className="p-4 text-sm text-destructive bg-destructive/10 rounded-md">
          {error}
        </div>
        <Button onClick={loadMealPlan} className="mt-4">
          Try Again
        </Button>
      </div>
    )
  }

  if (!mealPlan) return null

  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  const mealTypes: Array<'breakfast' | 'lunch' | 'dinner'> = ['breakfast', 'lunch', 'dinner']

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      {/* Header with week navigation */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Weekly Meal Plan</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Week of {mealPlan.week_start_date} to {mealPlan.week_end_date}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => navigateWeek('prev')}
          >
            ← Previous Week
          </Button>
          <Button
            variant="outline"
            onClick={goToCurrentWeek}
          >
            Current Week
          </Button>
          <Button
            variant="outline"
            onClick={() => navigateWeek('next')}
          >
            Next Week →
          </Button>
        </div>
      </div>

      {/* Meal plan grid */}
      <div className="border rounded-lg overflow-hidden">
        {/* Header row with day names */}
        <div className="grid grid-cols-8 gap-0 bg-muted">
          <div className="p-3 font-semibold border-r">Meal</div>
          {dayNames.map((day) => (
            <div key={day} className="p-3 font-semibold text-center border-r last:border-r-0">
              {day}
            </div>
          ))}
        </div>

        {/* Meal rows */}
        {mealTypes.map((mealType) => (
          <div key={mealType} className="grid grid-cols-8 gap-0 border-t">
            {/* Meal type label */}
            <div className="p-3 font-medium border-r bg-muted/50 flex items-center">
              {mealType.charAt(0).toUpperCase() + mealType.slice(1)}
            </div>

            {/* Meal slots for each day */}
            {dayNames.map((_, dayIndex) => {
              const slots = getMealSlotsByDay(dayIndex)
              const slot = slots.find(s => s.meal_type === mealType)

              return (
                <div key={dayIndex} className="p-2 border-r last:border-r-0">
                  {slot && (
                    <MealSlotCard
                      mealSlot={slot}
                      onAddMeal={handleAddMeal}
                      onClearMeal={handleClearMeal}
                    />
                  )}
                </div>
              )
            })}
          </div>
        ))}

        {/* Daily totals row */}
        <div className="grid grid-cols-8 gap-0 border-t bg-muted/30">
          <div className="p-3 font-semibold border-r">Daily Totals</div>
          {dayNames.map((_, dayIndex) => {
            const totals = getDailyTotals(dayIndex)
            return (
              <div key={dayIndex} className="p-3 text-xs border-r last:border-r-0">
                <div className="font-semibold">{totals.calories} kcal</div>
                <div className="text-muted-foreground">
                  P: {totals.protein.toFixed(0)}g •
                  C: {totals.carbs.toFixed(0)}g •
                  F: {totals.fats.toFixed(0)}g
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Meal selection modal */}
      <MealSelectionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        mealSlot={selectedSlot}
        onSelectRecipe={handleSelectRecipe}
      />
    </div>
  )
}
