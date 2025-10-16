# Generated migration to rename Spanish fields to English

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='receta',
            old_name='nombre',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='receta',
            old_name='ingredientes_texto',
            new_name='ingredients',
        ),
        migrations.RenameField(
            model_name='receta',
            old_name='pasos_texto',
            new_name='steps',
        ),
        migrations.RenameField(
            model_name='receta',
            old_name='calorias',
            new_name='calories',
        ),
        migrations.RenameField(
            model_name='receta',
            old_name='proteinas',
            new_name='protein',
        ),
        migrations.RenameField(
            model_name='receta',
            old_name='carbohidratos',
            new_name='carbs',
        ),
        migrations.RenameField(
            model_name='receta',
            old_name='grasas',
            new_name='fats',
        ),
        migrations.RenameField(
            model_name='receta',
            old_name='tiempo_min',
            new_name='prep_time_minutes',
        ),
        migrations.RenameField(
            model_name='receta',
            old_name='tipo',
            new_name='meal_type',
        ),
        migrations.AlterField(
            model_name='receta',
            name='meal_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('breakfast', 'Breakfast'),
                    ('lunch', 'Lunch'),
                    ('dinner', 'Dinner'),
                    ('snack', 'Snack')
                ]
            ),
        ),
        migrations.AlterModelOptions(
            name='receta',
            options={'ordering': ['-created_at'], 'verbose_name': 'Recipe', 'verbose_name_plural': 'Recipes'},
        ),
    ]
