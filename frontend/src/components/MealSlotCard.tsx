import { useState } from 'react'
import { Button } from '@/components/ui/button'
import type { MealSlot } from '@/types/api'

interface MealSlotCardProps {
  mealSlot: MealSlot
  onAddMeal: (mealSlot: MealSlot) => void
  onClearMeal: (mealSlot: MealSlot) => void
}

export default function MealSlotCard({ mealSlot, onAddMeal, onClearMeal }: MealSlotCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  const isEmpty = !mealSlot.recipe

  return (
    <div
      className="border rounded-lg p-3 min-h-[120px] hover:shadow-md transition-shadow relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {isEmpty ? (
        <div className="flex items-center justify-center h-full">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onAddMeal(mealSlot)}
            className="w-full"
          >
            + Add Meal
          </Button>
        </div>
      ) : (
        <div className="space-y-2">
          {mealSlot.is_leftover && (
            <span className="inline-block text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 px-2 py-0.5 rounded">
              Leftover
            </span>
          )}

          <h4 className="font-semibold text-sm line-clamp-2">
            {mealSlot.recipe_detail?.name}
          </h4>

          {mealSlot.recipe_detail && (
            <div className="text-xs text-muted-foreground space-y-1">
              <div className="flex items-center gap-2">
                <span>🔥 {mealSlot.recipe_detail.calories} kcal</span>
                <span>⏱️ {mealSlot.recipe_detail.prep_time_minutes} min</span>
              </div>

              <div className="text-xs">
                P: {mealSlot.recipe_detail.protein}g •
                C: {mealSlot.recipe_detail.carbs}g •
                F: {mealSlot.recipe_detail.fats}g
              </div>
            </div>
          )}

          {mealSlot.notes && (
            <p className="text-xs text-muted-foreground italic mt-2">
              {mealSlot.notes}
            </p>
          )}

          {isHovered && (
            <div className="absolute top-1 right-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  onClearMeal(mealSlot)
                }}
                className="h-6 w-6 p-0 text-xs hover:bg-destructive hover:text-destructive-foreground"
              >
                ×
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
