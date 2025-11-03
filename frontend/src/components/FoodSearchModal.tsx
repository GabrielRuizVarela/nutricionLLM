/**
 * FoodSearchModal Component
 * Allows users to search USDA food database and log food entries
 */

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Label } from '@/components/ui/label'
import type { Food, FoodLogCreateRequest } from '@/types/api'
import { searchFoods, createFoodLog } from '@/services/foodLogging'

interface FoodSearchModalProps {
  isOpen: boolean
  onClose: () => void
  date: string // YYYY-MM-DD
  mealType: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  onFoodLogged: () => void // Callback after successfully logging food
}

export default function FoodSearchModal({
  isOpen,
  onClose,
  date,
  mealType,
  onFoodLogged
}: FoodSearchModalProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<Food[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [selectedFood, setSelectedFood] = useState<Food | null>(null)
  const [quantity, setQuantity] = useState('')
  const [isLogging, setIsLogging] = useState(false)
  const [error, setError] = useState('')

  // Debounced search
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSearchResults([])
      return
    }

    const timeoutId = setTimeout(() => {
      handleSearch()
    }, 500)

    return () => clearTimeout(timeoutId)
  }, [searchQuery])

  const handleSearch = async () => {
    if (searchQuery.length < 2) return

    setIsSearching(true)
    setError('')

    try {
      const results = await searchFoods(searchQuery)
      setSearchResults(results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search foods')
    } finally {
      setIsSearching(false)
    }
  }

  const handleSelectFood = (food: Food) => {
    setSelectedFood(food)
    setQuantity(food.serving_size?.toString() || '100')
  }

  const handleLogFood = async () => {
    if (!selectedFood || !quantity) {
      setError('Please select a food and enter quantity')
      return
    }

    const quantityNum = parseFloat(quantity)
    if (isNaN(quantityNum) || quantityNum <= 0) {
      setError('Please enter a valid quantity')
      return
    }

    setIsLogging(true)
    setError('')

    try {
      const logData: FoodLogCreateRequest = {
        food: selectedFood.id,
        date,
        meal_type: mealType,
        quantity_grams: quantityNum
      }

      await createFoodLog(logData)

      // Reset and close
      setSelectedFood(null)
      setQuantity('')
      setSearchQuery('')
      setSearchResults([])
      onFoodLogged()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log food')
    } finally {
      setIsLogging(false)
    }
  }

  const calculateMacros = () => {
    if (!selectedFood || !quantity) return null

    const quantityNum = parseFloat(quantity)
    if (isNaN(quantityNum) || quantityNum <= 0 || !selectedFood.serving_size) return null

    const ratio = quantityNum / selectedFood.serving_size
    return {
      calories: Math.round((selectedFood.calories || 0) * ratio),
      protein: ((selectedFood.protein || 0) * ratio).toFixed(1),
      carbs: ((selectedFood.carbs || 0) * ratio).toFixed(1),
      fats: ((selectedFood.fats || 0) * ratio).toFixed(1)
    }
  }

  const macros = calculateMacros()

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>
            Log Food - {mealType.charAt(0).toUpperCase() + mealType.slice(1)}
          </DialogTitle>
          <DialogDescription>
            Search the USDA food database and add to your {mealType} for {date}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Search Input */}
          <div>
            <Label htmlFor="food-search">Search Foods</Label>
            <Input
              id="food-search"
              type="text"
              placeholder="Search for a food (e.g., 'chicken breast', 'apple')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              disabled={isLogging}
            />
            {isSearching && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Searching...</p>
            )}
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && !selectedFood && (
            <div>
              <Label>Search Results ({searchResults.length})</Label>
              <ScrollArea className="h-[300px] border border-gray-200 dark:border-gray-700 rounded-md p-2 mt-2">
                <div className="space-y-2">
                  {searchResults.map((food) => (
                    <button
                      key={food.id}
                      onClick={() => handleSelectFood(food)}
                      className="w-full text-left p-3 border border-gray-200 dark:border-gray-700 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                    >
                      <div className="font-medium">{food.description}</div>
                      {food.brand_owner && (
                        <div className="text-sm text-gray-600 dark:text-gray-400">{food.brand_owner}</div>
                      )}
                      <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        Serving: {food.serving_size} {food.serving_size_unit} |
                        Cal: {food.calories} |
                        P: {food.protein}g |
                        C: {food.carbs}g |
                        F: {food.fats}g
                      </div>
                    </button>
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}

          {/* Selected Food */}
          {selectedFood && (
            <div className="space-y-4 border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
              <div>
                <Label>Selected Food</Label>
                <div className="mt-2">
                  <div className="font-medium">{selectedFood.description}</div>
                  {selectedFood.brand_owner && (
                    <div className="text-sm text-gray-600 dark:text-gray-400">{selectedFood.brand_owner}</div>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSelectedFood(null)
                    setQuantity('')
                  }}
                  className="mt-2"
                >
                  Change Food
                </Button>
              </div>

              <div>
                <Label htmlFor="quantity">
                  Quantity ({selectedFood.serving_size_unit || 'grams'})
                </Label>
                <Input
                  id="quantity"
                  type="number"
                  min="0.1"
                  step="0.1"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  placeholder={`Enter quantity in ${selectedFood.serving_size_unit || 'grams'}`}
                  disabled={isLogging}
                />
                {selectedFood.serving_size && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    Standard serving: {selectedFood.serving_size} {selectedFood.serving_size_unit}
                  </p>
                )}
              </div>

              {/* Calculated Macros */}
              {macros && (
                <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md p-3">
                  <Label>Nutritional Information for {quantity} {selectedFood.serving_size_unit}</Label>
                  <div className="grid grid-cols-4 gap-4 mt-2 text-center">
                    <div>
                      <div className="text-2xl font-bold">{macros.calories}</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">Calories</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{macros.protein}g</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">Protein</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{macros.carbs}g</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">Carbs</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{macros.fats}g</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">Fats</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="text-red-600 dark:text-red-400 text-sm p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
              {error}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-2 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button variant="outline" onClick={onClose} disabled={isLogging}>
              Cancel
            </Button>
            {selectedFood && (
              <Button onClick={handleLogFood} disabled={isLogging || !quantity}>
                {isLogging ? 'Logging...' : 'Log Food'}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
