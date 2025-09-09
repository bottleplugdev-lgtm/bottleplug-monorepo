from firebase_admin import messaging
from django.contrib.auth import get_user_model
from .tasks import send_notification_to_user, send_push_notification

User = get_user_model()

class NotificationService:
    @staticmethod
    def notify_user(user_id, title, message, notification_type='system', data=None, send_push=True):
        """Send both in-app and push notifications to a user"""
        # Send in-app notification
        send_notification_to_user.delay(user_id, title, message, notification_type, data)
        
        # Send push notification if enabled
        if send_push:
            send_push_notification.delay(user_id, title, message, data)
    
    @staticmethod
    def notify_order_update(order):
        """Notify customer about order updates"""
        NotificationService.notify_user(
            order.customer.id,
            f"Order #{order.id} Update",
            f"Your order status: {order.status}",
            'order_update',
            {'order_id': order.id, 'status': order.status}
        )
    
    @staticmethod
    def notify_delivery_update(delivery):
        """Notify customer about delivery updates"""
        NotificationService.notify_user(
            delivery.order.customer.id,
            f"Delivery Update",
            f"Your delivery is {delivery.status}",
            'delivery_update',
            {'delivery_id': delivery.id, 'status': delivery.status}
        )