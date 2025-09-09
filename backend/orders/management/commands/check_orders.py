from django.core.management.base import BaseCommand
from orders.models import Order
from users.models import User


class Command(BaseCommand):
    help = 'Check orders and users in the database'

    def handle(self, *args, **options):
        # Check all users
        users = User.objects.all()
        self.stdout.write(f"Total users: {users.count()}")
        
        for user in users:
            self.stdout.write(f"User: {user.email} (ID: {user.id}, Type: {user.user_type})")
        
        # Check all orders
        orders = Order.objects.all()
        self.stdout.write(f"\nTotal orders: {orders.count()}")
        
        for order in orders:
            self.stdout.write(f"Order: {order.order_number} (Customer: {order.customer.email if order.customer else 'None'})")
        
        # Check orders by user type
        customer_users = User.objects.filter(user_type='customer')
        admin_users = User.objects.filter(user_type='admin')
        
        self.stdout.write(f"\nCustomer users: {customer_users.count()}")
        self.stdout.write(f"Admin users: {admin_users.count()}")
        
        # Check orders for each customer
        for customer in customer_users:
            customer_orders = Order.objects.filter(customer=customer)
            self.stdout.write(f"Orders for {customer.email}: {customer_orders.count()}") 