from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product, InventoryItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'Initialize inventory items for existing products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing inventory items',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting inventory initialization...')
        
        products = Product.objects.all()
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for product in products:
                inventory, created = InventoryItem.objects.get_or_create(
                    product=product,
                    defaults={
                        'current_stock': product.stock,
                        'available_stock': product.stock,
                        'min_stock_level': product.min_stock_level,
                        'max_stock_level': product.max_stock_level,
                        'reorder_point': max(product.min_stock_level, 10),
                        'reorder_quantity': 100,
                        'is_active': product.status == 'active',
                        'track_quantity': True,
                        'cost_price': product.price * Decimal('0.7') if product.price else None,  # Estimate 70% of selling price
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created inventory for: {product.name}')
                    )
                elif options['update_existing']:
                    # Update existing inventory with current product data
                    inventory.current_stock = product.stock
                    inventory.available_stock = product.stock
                    inventory.min_stock_level = product.min_stock_level
                    inventory.max_stock_level = product.max_stock_level
                    inventory.is_active = product.status == 'active'
                    inventory.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated inventory for: {product.name}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Inventory initialization complete!\n'
                f'Created: {created_count} items\n'
                f'Updated: {updated_count} items'
            )
        )
