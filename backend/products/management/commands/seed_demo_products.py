import io
import os
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Category, Product, ProductMeasurement


DEMO_PRODUCTS = [
    {
        'name': "Château Margaux 2015",
        'category': 'Red Wine',
        'sku': 'CHM-2015-750',
        'price': 1299.00,
        'original_price': 1529.00,
        'is_featured': True,
        'is_new': False,
        'is_on_sale': True,
        'stock': 5,
        'average_rating': 4.9,
        'image_url': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=800&h=800&fit=crop',
        'measurement': {'measurement': 'fifth', 'quantity': '750ml', 'price': 1299.00, 'original_price': 1529.00, 'is_default': True},
    },
    {
        'name': 'Dom Pérignon 2012',
        'category': 'Champagne',
        'sku': 'DP-2012-750',
        'price': 399.00,
        'original_price': None,
        'is_featured': True,
        'is_new': False,
        'is_on_sale': False,
        'stock': 12,
        'average_rating': 4.8,
        'image_url': 'https://images.unsplash.com/photo-1547595628-c61a29f496f0?w=800&h=800&fit=crop',
        'measurement': {'measurement': 'fifth', 'quantity': '750ml', 'price': 399.00, 'original_price': None, 'is_default': True},
    },
    {
        'name': 'Macallan 25 Year',
        'category': 'Whisky',
        'sku': 'MAC-25YO-750',
        'price': 2499.00,
        'original_price': None,
        'is_featured': True,
        'is_new': False,
        'is_on_sale': False,
        'stock': 3,
        'average_rating': 4.9,
        'image_url': 'https://images.unsplash.com/photo-1527281400683-1aae777175f8?w=800&h=800&fit=crop',
        'measurement': {'measurement': 'fifth', 'quantity': '750ml', 'price': 2499.00, 'original_price': None, 'is_default': True},
    },
    {
        'name': 'Opus One 2018',
        'category': 'Red Wine',
        'sku': 'OPUS-2018-750',
        'price': 549.00,
        'original_price': 609.00,
        'is_featured': True,
        'is_new': True,
        'is_on_sale': True,
        'stock': 8,
        'average_rating': 4.7,
        'image_url': 'https://images.unsplash.com/photo-1506377247746-6fdee8c9cd92?w=800&h=800&fit=crop',
        'measurement': {'measurement': 'fifth', 'quantity': '750ml', 'price': 549.00, 'original_price': 609.00, 'is_default': True},
    },
]


def download_image(url: str) -> ContentFile | None:
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        filename = os.path.basename(urlparse(url).path) or 'image.jpg'
        return ContentFile(resp.content, name=filename)
    except Exception:
        return None


class Command(BaseCommand):
    help = "Seed demo categories and products used by the web frontend"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding demo products...'))

        # Ensure categories
        name_to_category: dict[str, Category] = {}
        for p in DEMO_PRODUCTS:
            cat_name = p['category']
            if cat_name not in name_to_category:
                category, _ = Category.objects.get_or_create(name=cat_name, defaults={'is_active': True})
                name_to_category[cat_name] = category

        created, updated = 0, 0
        for item in DEMO_PRODUCTS:
            category = name_to_category[item['category']]
            product, was_created = Product.objects.update_or_create(
                sku=item['sku'],
                defaults={
                    'name': item['name'],
                    'category': category,
                    'price': item['price'],
                    'original_price': item['original_price'],
                    'is_featured': item['is_featured'],
                    'is_new': item['is_new'],
                    'is_on_sale': item['is_on_sale'],
                    'stock': item['stock'],
                    'average_rating': item.get('average_rating'),
                    'status': 'active',
                }
            )

            if was_created:
                created += 1
            else:
                updated += 1

            # Set main image
            if item.get('image_url') and not product.image:
                image_file = download_image(item['image_url'])
                if image_file:
                    product.image.save(image_file.name, image_file, save=True)

            # Ensure a default measurement exists/updated
            m = item.get('measurement')
            if m:
                pm, _ = ProductMeasurement.objects.update_or_create(
                    product=product,
                    measurement=m['measurement'],
                    quantity=m.get('quantity'),
                    defaults={
                        'price': m['price'],
                        'original_price': m.get('original_price'),
                        'is_active': True,
                        'is_default': m.get('is_default', True),
                        'sort_order': 0,
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'Seed complete. Created: {created}, Updated: {updated}'))

