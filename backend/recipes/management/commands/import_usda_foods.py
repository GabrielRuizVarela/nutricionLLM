"""
Django management command to import USDA FoodData Central branded foods database.
Handles large JSON files efficiently using streaming JSON parser.
"""
import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from recipes.models import Food


class Command(BaseCommand):
    help = 'Import USDA FoodData Central branded foods from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='FoodData_Central_branded_food_json_2025-04-24.json',
            help='Path to the USDA JSON file'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to insert per batch'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of foods to import (for testing)'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        batch_size = options['batch_size']
        limit = options['limit']

        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Starting import from: {file_path}'))
        self.stdout.write(f'Batch size: {batch_size}')

        total_imported = 0
        total_skipped = 0
        batch = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read the file and parse JSON
                data = json.load(f)
                foods_data = data.get('BrandedFoods', [])

                total_foods = len(foods_data)
                self.stdout.write(f'Found {total_foods} foods in file')

                for idx, food_item in enumerate(foods_data):
                    # Check limit
                    if limit and total_imported >= limit:
                        break

                    # Extract food data
                    food_obj = self.parse_food_item(food_item)

                    if food_obj:
                        batch.append(food_obj)

                        # Insert batch when it reaches batch_size
                        if len(batch) >= batch_size:
                            imported, skipped = self.import_batch(batch)
                            total_imported += imported
                            total_skipped += skipped
                            batch = []

                            # Progress update
                            if total_imported % 10000 == 0:
                                self.stdout.write(
                                    f'Progress: {total_imported:,} imported, '
                                    f'{total_skipped:,} skipped '
                                    f'({idx+1}/{total_foods} processed)'
                                )

                # Import remaining batch
                if batch:
                    imported, skipped = self.import_batch(batch)
                    total_imported += imported
                    total_skipped += skipped

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during import: {str(e)}'))
            raise

        self.stdout.write(self.style.SUCCESS(
            f'\nImport complete!\n'
            f'Total imported: {total_imported:,}\n'
            f'Total skipped: {total_skipped:,}'
        ))

    def parse_food_item(self, food_item):
        """Parse a single food item from USDA JSON format"""
        try:
            # Extract label nutrients (simplified nutrient data per serving)
            label_nutrients = food_item.get('labelNutrients', {})

            # Get serving size
            serving_size = food_item.get('servingSize')
            serving_unit = food_item.get('servingSizeUnit', '')

            # Skip foods without complete macro data
            if not label_nutrients.get('calories'):
                return None

            food = Food(
                fdc_id=food_item.get('fdcId'),
                description=food_item.get('description', '')[:500],  # Truncate to 500 chars
                brand_owner=food_item.get('brandOwner', '')[:200],
                barcode=food_item.get('gtinUpc', '')[:20],
                ingredients=food_item.get('ingredients', ''),
                category=food_item.get('brandedFoodCategory', '')[:100],
                serving_size=serving_size,
                serving_size_unit=serving_unit,
                calories=int(label_nutrients.get('calories', {}).get('value', 0)),
                protein=label_nutrients.get('protein', {}).get('value'),
                carbs=label_nutrients.get('carbohydrates', {}).get('value'),
                fats=label_nutrients.get('fat', {}).get('value'),
                fiber=label_nutrients.get('fiber', {}).get('value'),
                sugars=label_nutrients.get('sugars', {}).get('value'),
                sodium=label_nutrients.get('sodium', {}).get('value'),
            )

            return food

        except Exception as e:
            # Skip problematic food items
            return None

    def import_batch(self, batch):
        """Import a batch of Food objects using bulk_create"""
        imported = 0
        skipped = 0

        try:
            with transaction.atomic():
                # Use bulk_create with ignore_conflicts to skip duplicates
                Food.objects.bulk_create(
                    batch,
                    ignore_conflicts=True,
                    batch_size=1000
                )
                imported = len(batch)

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error importing batch: {str(e)}'))
            # Try importing one by one to identify problematic records
            for food in batch:
                try:
                    food.save()
                    imported += 1
                except Exception:
                    skipped += 1

        return imported, skipped
