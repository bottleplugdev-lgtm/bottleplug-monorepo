from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import Notification
import json

User = get_user_model()
channel_layer = get_channel_layer()

@shared_task
def send_notification_to_user(user_id, title, message, notification_type='system', data=None):
    """Send notification to a specific user"""
    try:
        user = User.objects.get(id=user_id)
        
        # Create notification in database
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            data=data or {}
        )
        
        # Send real-time notification via WebSocket
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "notification_message",
                "data": {
                    "id": notification.id,
                    "title": title,
                    "message": message,
                    "notification_type": notification_type,
                    "data": data,
                    "created_at": notification.created_at.isoformat()
                }
            }
        )
        
        return f"Notification sent to user {user_id}"
    except User.DoesNotExist:
        return f"User {user_id} not found"

@shared_task
def send_push_notification(user_id, title, message, data=None):
    """Send push notification to mobile device"""
    try:
        user = User.objects.get(id=user_id)
        if hasattr(user, 'push_token') and user.push_token:
            # Import Firebase Admin SDK
            from firebase_admin import messaging
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                ),
                data=data or {},
                token=user.push_token,
            )
            
            response = messaging.send(message)
            return f"Push notification sent: {response}"
        else:
            return f"No push token for user {user_id}"
    except User.DoesNotExist:
        return f"User {user_id} not found"
    except Exception as e:
        return f"Error sending push notification: {str(e)}"

@shared_task
def process_order_update(order_id, status):
    """Process order status updates and notify relevant users"""
    from orders.models import Order
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Notify customer
        send_notification_to_user.delay(
            order.customer.id,
            f"Order #{order.id} Update",
            f"Your order status has been updated to: {status}",
            'order_update',
            {'order_id': order_id, 'status': status}
        )
        
        # Send push notification
        send_push_notification.delay(
            order.customer.id,
            f"Order #{order.id} Update",
            f"Your order is now {status}",
            {'order_id': str(order_id), 'type': 'order_update'}
        )
        
        return f"Order {order_id} notifications sent"
    except Order.DoesNotExist:
        return f"Order {order_id} not found"