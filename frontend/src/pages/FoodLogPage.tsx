/**
 * FoodLogPage
 * Page wrapper for daily food logging functionality
 */

import DailyFoodLog from '@/components/DailyFoodLog'

export default function FoodLogPage() {
  return (
    <main className="flex-1 container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Food Diary</h1>
        <p className="text-gray-600 mt-2">
          Track your daily food intake and monitor your nutrition goals
        </p>
      </div>
      <DailyFoodLog />
    </main>
  )
}
