import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutriai_project.settings')
django.setup()

from recipes.models import Food

print(f'Total foods in database: {Food.objects.count()}')
print('\nSample foods:')
for f in Food.objects.all()[:5]:
    print(f'  - {f.description[:50]} ({f.brand_owner[:20]}) - {f.calories} kcal, P:{f.protein}g C:{f.carbs}g F:{f.fats}g')
