from django.contrib import admin
from recipes.models import Receta, MealPlan, MealSlot, Food, FoodLog


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('name', 'meal_type', 'user', 'calories', 'prep_time_minutes', 'created_at')
    list_filter = ('meal_type', 'created_at')
    search_fields = ('name', 'user__username')
    ordering = ('-created_at',)


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'week_start_date', 'created_at')
    list_filter = ('week_start_date', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-week_start_date',)


@admin.register(MealSlot)
class MealSlotAdmin(admin.ModelAdmin):
    list_display = ('meal_plan', 'day_of_week', 'meal_type', 'recipe', 'is_leftover')
    list_filter = ('day_of_week', 'meal_type', 'is_leftover')
    search_fields = ('meal_plan__user__username', 'recipe__name')
    ordering = ('meal_plan', 'day_of_week', 'meal_type')


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('fdc_id', 'description', 'brand_owner', 'calories', 'protein', 'carbs', 'fats')
    list_filter = ('category',)
    search_fields = ('description', 'brand_owner', 'barcode')
    ordering = ('description',)


@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'food', 'date', 'meal_type', 'quantity_grams', 'calories')
    list_filter = ('date', 'meal_type')
    search_fields = ('user__username', 'food__description')
    ordering = ('-date', 'meal_type')
