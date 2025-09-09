from django.core.management.base import BaseCommand
from products.models import Category

DEFAULT_CATEGORIES = [
    {"name": "Red Wine", "description": "Rich and full-bodied red wines."},
    {"name": "White Wine", "description": "Crisp and refreshing white wines."},
    {"name": "Champagne", "description": "Sparkling wines from Champagne and beyond."},
    {"name": "Whisky", "description": "Aged whiskies from around the world."},
    {"name": "Vodka", "description": "Premium and flavored vodkas."},
    {"name": "Gin", "description": "Classic and contemporary gins."},
    {"name": "Rum", "description": "Light, dark, and spiced rums."},
    {"name": "Rosé", "description": "Elegant and vibrant rosé wines."},
    {"name": "Beer", "description": "Craft and classic beers."},
]

class Command(BaseCommand):
    help = 'Seed default alcohol categories into the database using the Category model'

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for index, item in enumerate(DEFAULT_CATEGORIES):
            name = item["name"].strip()
            description = item.get("description", "")

            category, was_created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'is_active': True,
                    'sort_order': index
                }
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {name}"))
            else:
                changed = False
                if category.description != description:
                    category.description = description
                    changed = True
                if category.sort_order != index:
                    category.sort_order = index
                    changed = True
                if not category.is_active:
                    category.is_active = True
                    changed = True
                if changed:
                    category.save(update_fields=['description', 'sort_order', 'is_active'])
                    updated += 1
                    self.stdout.write(self.style.WARNING(f"Updated: {name}"))
        total = Category.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Done. Created={created}, Updated={updated}, Total={total}"))