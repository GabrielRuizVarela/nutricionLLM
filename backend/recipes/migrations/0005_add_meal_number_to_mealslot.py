# Generated migration for adding meal_number field to MealSlot

from django.db import migrations, models
import django.core.validators


def populate_meal_numbers(apps, schema_editor):
    """Populate meal_number for existing MealSlot records"""
    MealSlot = apps.get_model('recipes', 'MealSlot')

    # Map meal types to meal numbers
    meal_type_to_number = {
        'breakfast': 1,
        'lunch': 2,
        'dinner': 3,
    }

    for slot in MealSlot.objects.all():
        slot.meal_number = meal_type_to_number.get(slot.meal_type, 1)
        slot.save(update_fields=['meal_number'])


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_food_foodlog_food_recipes_foo_descrip_6f6793_idx_and_more'),
    ]

    operations = [
        # Add meal_number field with default
        migrations.AddField(
            model_name='mealslot',
            name='meal_number',
            field=models.IntegerField(
                default=1,
                help_text='Which meal this is (1-6) within the day',
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),

        # Populate meal_number for existing records
        migrations.RunPython(populate_meal_numbers, reverse_code=migrations.RunPython.noop),

        # Update meal_type field to remove choices and increase max_length
        migrations.AlterField(
            model_name='mealslot',
            name='meal_type',
            field=models.CharField(
                max_length=50,
                help_text="Name of the meal (e.g., 'Breakfast', 'Meal 1')"
            ),
        ),

        # Remove old unique_together constraint
        migrations.AlterUniqueTogether(
            name='mealslot',
            unique_together=set(),
        ),

        # Add new unique_together constraint with meal_number
        migrations.AlterUniqueTogether(
            name='mealslot',
            unique_together={('meal_plan', 'day_of_week', 'meal_number')},
        ),

        # Update ordering
        migrations.AlterModelOptions(
            name='mealslot',
            options={
                'ordering': ['meal_plan', 'day_of_week', 'meal_number'],
                'verbose_name': 'Meal Slot',
                'verbose_name_plural': 'Meal Slots'
            },
        ),
    ]
