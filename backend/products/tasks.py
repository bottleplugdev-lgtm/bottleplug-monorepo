from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Product, InventoryItem
from orders.models import Wishlist, PreOrder
from notifications.services import NotificationService


@shared_task
def monitor_price_changes():
    """
    Monitor price changes and send notifications to users with price alerts
    """
    try:
        # Get all wishlist items with price drop alerts enabled
        wishlist_items = Wishlist.objects.filter(
            price_drop_alerts=True
        ).select_related('user', 'product')
        
        notifications_sent = 0
        
        for wishlist_item in wishlist_items:
            current_price = wishlist_item.current_price
            
            # Check if price has changed since last notification
            if (wishlist_item.last_notified_price and 
                current_price != wishlist_item.last_notified_price):
                
                # Check for price drop
                if current_price < wishlist_item.last_notified_price:
                    price_drop = wishlist_item.last_notified_price - current_price
                    percentage_drop = (price_drop / wishlist_item.last_notified_price) * 100
                    
                    # Send price drop notification
                    NotificationService.notify_user(
                        wishlist_item.user.id,
                        f"Price Drop Alert: {wishlist_item.product.name}",
                        f"Price dropped by UGX {price_drop:.2f} ({percentage_drop:.1f}%)",
                        'price_alert',
                        {
                            'product_id': wishlist_item.product.id,
                            'wishlist_id': wishlist_item.id,
                            'old_price': float(wishlist_item.last_notified_price),
                            'new_price': float(current_price),
                            'savings': float(price_drop),
                            'percentage_drop': float(percentage_drop),
                            'alert_type': 'price_drop'
                        }
                    )
                    notifications_sent += 1
                
                # Check if target price is met
                if (wishlist_item.target_price and 
                    current_price <= wishlist_item.target_price):
                    
                    NotificationService.notify_user(
                        wishlist_item.user.id,
                        f"Target Price Reached: {wishlist_item.product.name}",
                        f"Your target price of UGX {wishlist_item.target_price} has been reached!",
                        'price_alert',
                        {
                            'product_id': wishlist_item.product.id,
                            'wishlist_id': wishlist_item.id,
                            'target_price': float(wishlist_item.target_price),
                            'current_price': float(current_price),
                            'alert_type': 'target_price_met'
                        }
                    )
                    notifications_sent += 1
                
                # Update last notified price
                wishlist_item.update_price_tracking()
        
        print(f"Price monitoring complete. Sent {notifications_sent} notifications.")
        return notifications_sent
        
    except Exception as e:
        print(f"Error in price monitoring: {e}")
        return 0


@shared_task
def monitor_stock_changes():
    """
    Monitor stock changes and send notifications for restock alerts
    """
    try:
        notifications_sent = 0
        
        # Check for items that came back in stock
        inventory_items = InventoryItem.objects.filter(
            is_active=True,
            track_quantity=True,
            available_stock__gt=0
        ).select_related('product')
        
        for inventory in inventory_items:
            # Check wishlist items for this product
            wishlist_items = Wishlist.objects.filter(
                product=inventory.product,
                stock_alerts=True,
                was_in_stock=False  # Was previously out of stock
            ).select_related('user')
            
            for wishlist_item in wishlist_items:
                # Send back in stock notification
                NotificationService.notify_user(
                    wishlist_item.user.id,
                    f"{inventory.product.name} is back in stock!",
                    f"Your wishlist item is now available with {inventory.available_stock} units in stock.",
                    'stock_alert',
                    {
                        'product_id': inventory.product.id,
                        'wishlist_id': wishlist_item.id,
                        'available_stock': inventory.available_stock,
                        'alert_type': 'back_in_stock'
                    }
                )
                notifications_sent += 1
                
                # Update stock tracking
                wishlist_item.update_stock_tracking()
            
            # Check pre-orders for this product
            pre_orders = PreOrder.objects.filter(
                product=inventory.product,
                status='pending',
                notify_when_available=True,
                notification_sent=False
            ).select_related('user')
            
            for pre_order in pre_orders:
                if pre_order.can_be_fulfilled:
                    pre_order.send_availability_notification()
                    notifications_sent += 1
        
        print(f"Stock monitoring complete. Sent {notifications_sent} notifications.")
        return notifications_sent
        
    except Exception as e:
        print(f"Error in stock monitoring: {e}")
        return 0


@shared_task
def check_low_stock_alerts():
    """
    Check for low stock items and send alerts to admin users
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get low stock items
        low_stock_items = InventoryItem.objects.filter(
            is_active=True,
            track_quantity=True,
            available_stock__lte=F('min_stock_level'),
            min_stock_level__gt=0
        ).select_related('product')
        
        if not low_stock_items.exists():
            return 0
        
        # Get admin users
        admin_users = User.objects.filter(is_staff=True)
        notifications_sent = 0
        
        for admin in admin_users:
            # Send summary notification
            low_stock_count = low_stock_items.count()
            product_names = [item.product.name for item in low_stock_items[:5]]
            
            message = f"{low_stock_count} items are running low on stock"
            if low_stock_count > 5:
                message += f". Including: {', '.join(product_names)} and {low_stock_count - 5} more."
            else:
                message += f": {', '.join(product_names)}"
            
            NotificationService.notify_user(
                admin.id,
                "Low Stock Alert",
                message,
                'stock_alert',
                {
                    'alert_type': 'low_stock_summary',
                    'low_stock_count': low_stock_count,
                    'products': [
                        {
                            'id': item.product.id,
                            'name': item.product.name,
                            'current_stock': item.available_stock,
                            'min_stock': item.min_stock_level
                        }
                        for item in low_stock_items
                    ]
                }
            )
            notifications_sent += 1
        
        print(f"Low stock alerts sent to {notifications_sent} admin users.")
        return notifications_sent
        
    except Exception as e:
        print(f"Error in low stock monitoring: {e}")
        return 0


@shared_task
def cleanup_expired_preorders():
    """
    Clean up expired pre-orders
    """
    try:
        expired_preorders = PreOrder.objects.filter(
            status='pending',
            expires_at__lt=timezone.now()
        )
        
        count = 0
        for pre_order in expired_preorders:
            pre_order.status = 'expired'
            pre_order.save()
            
            # Notify user about expiration
            NotificationService.notify_user(
                pre_order.user.id,
                f"Pre-order expired: {pre_order.product.name}",
                f"Your pre-order for {pre_order.quantity} units has expired.",
                'order_update',
                {
                    'pre_order_id': pre_order.id,
                    'product_id': pre_order.product.id,
                    'alert_type': 'pre_order_expired'
                }
            )
            count += 1
        
        print(f"Cleaned up {count} expired pre-orders.")
        return count
        
    except Exception as e:
        print(f"Error cleaning up expired pre-orders: {e}")
        return 0


@shared_task
def update_inventory_from_sales():
    """
    Update inventory levels based on completed sales
    This should be called when orders are completed
    """
    try:
        from orders.models import Order, OrderItem
        
        # Get recently completed orders that haven't been processed for inventory
        recent_orders = Order.objects.filter(
            status='completed',
            updated_at__gte=timezone.now() - timedelta(hours=1)
        ).prefetch_related('items__product')
        
        updated_count = 0
        
        for order in recent_orders:
            for item in order.items.all():
                try:
                    inventory = InventoryItem.objects.get(product=item.product)
                    
                    # Reduce stock by sold quantity
                    inventory.update_stock(
                        inventory.current_stock - item.quantity,
                        movement_type='sale',
                        reference=f"Order #{order.id}",
                        notes=f"Sale of {item.quantity} units"
                    )
                    updated_count += 1
                    
                except InventoryItem.DoesNotExist:
                    # Create inventory item if it doesn't exist
                    InventoryItem.objects.create(
                        product=item.product,
                        current_stock=max(0, item.product.stock - item.quantity),
                        available_stock=max(0, item.product.stock - item.quantity)
                    )
                    updated_count += 1
        
        print(f"Updated inventory for {updated_count} items from recent sales.")
        return updated_count
        
    except Exception as e:
        print(f"Error updating inventory from sales: {e}")
        return 0
