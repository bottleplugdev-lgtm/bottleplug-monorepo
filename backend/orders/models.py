from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class OrderReceipt(models.Model):
    """
    Order Receipt model for delivery confirmations
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('signed', 'Signed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Receipt information
    receipt_number = models.CharField(max_length=50, unique=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='receipts')
    
    # Customer information (snapshot)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Receipt details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Delivery information
    delivery_address = models.TextField(blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True)
    delivery_person = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_receipts')
    delivery_person_name = models.CharField(max_length=200, blank=True, null=True)
    delivery_person_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Signature and confirmation
    customer_signature = models.TextField(blank=True, null=True)  # Base64 encoded signature
    signature_date = models.DateTimeField(null=True, blank=True)
    signature_ip = models.GenericIPAddressField(null=True, blank=True)
    signature_user_agent = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    tracking_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'order_receipts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        # Generate receipt number if not provided
        if not self.receipt_number:
            self.receipt_number = self._generate_receipt_number()
        
        super().save(*args, **kwargs)
    
    def _generate_receipt_number(self):
        """Generate unique receipt number"""
        import random
        import string
        
        while True:
            # Format: RCP-YYYYMMDD-XXXXX
            date_part = timezone.now().strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            receipt_number = f"RCP-{date_part}-{random_part}"
            
            if not OrderReceipt.objects.filter(receipt_number=receipt_number).exists():
                return receipt_number
    
    @property
    def is_pending_signature(self):
        return self.status == 'sent'
    
    @property
    def is_signed(self):
        return self.status == 'signed'
    
    @property
    def is_delivered(self):
        return self.status == 'delivered'
    
    def send_to_customer(self):
        """Mark receipt as sent to customer"""
        if self.status == 'pending':
            self.status = 'sent'
            self.sent_at = timezone.now()
            self.save()
            return True
        return False
    
    def sign_by_customer(self, signature_data, ip_address=None, user_agent=None):
        """Mark receipt as signed by customer"""
        if self.status == 'sent':
            self.status = 'signed'
            self.customer_signature = signature_data
            self.signature_date = timezone.now()
            self.signature_ip = ip_address
            self.signature_user_agent = user_agent
            self.signed_at = timezone.now()
            self.save()
            return True
        return False
    
    def mark_delivered(self):
        """Mark receipt as delivered"""
        if self.status == 'signed':
            self.status = 'delivered'
            self.delivered_at = timezone.now()
            self.save()
            return True
        return False
    
    @classmethod
    def create_from_order(cls, order):
        """Create a receipt from an order"""
        receipt = cls.objects.create(
            order=order,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            customer_phone=order.customer_phone,
            total_amount=order.total_amount,
            delivery_address=order.delivery_address,
            delivery_instructions=order.delivery_instructions,
            delivery_person=order.delivery_person,
            delivery_person_name=order.delivery_person_name,
            delivery_person_phone=order.delivery_person_phone,
            notes=f"Receipt for order {order.order_number}"
        )
        return receipt


class Invoice(models.Model):
    """
    Invoice model for billing customers
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_TERMS_CHOICES = [
        ('immediate', 'Immediate'),
        ('net_7', 'Net 7'),
        ('net_15', 'Net 15'),
        ('net_30', 'Net 30'),
        ('net_45', 'Net 45'),
        ('net_60', 'Net 60'),
    ]
    
    # Invoice information
    invoice_number = models.CharField(max_length=50, unique=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='invoices')
    
    # Customer information (snapshot)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField(blank=True, null=True)
    
    # Invoice details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='immediate')
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Delivery fee from order
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Unpaid sum
    
    # Payment information
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    terms_and_conditions = models.TextField(blank=True, null=True)
    company_info = models.JSONField(default=dict, blank=True)  # Store company details
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        # Generate invoice number if not provided
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()
        
        # Calculate totals
        self._calculate_totals()
        
        # Set due date based on payment terms
        if not self.due_date and self.payment_terms != 'immediate':
            self._set_due_date()
        
        super().save(*args, **kwargs)
    
    def _generate_invoice_number(self):
        """Generate unique invoice number"""
        import random
        import string
        
        while True:
            # Format: INV-YYYYMMDD-XXXXX
            date_part = timezone.now().strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            invoice_number = f"INV-{date_part}-{random_part}"
            
            if not Invoice.objects.filter(invoice_number=invoice_number).exists():
                return invoice_number
    
    def _calculate_totals(self):
        """Calculate invoice totals"""
        from decimal import Decimal
        
        # Calculate tax
        self.tax_amount = self.subtotal * (self.tax_rate / Decimal('100'))
        
        # Calculate total (including delivery fee)
        self.total_amount = self.subtotal + self.tax_amount + self.delivery_fee - self.discount_amount
        
        # Calculate balance due
        self.balance_due = self.total_amount - self.amount_paid
        
        # Calculate outstanding amount based on order payment transactions
        self._calculate_outstanding_amount()
    
    def _calculate_outstanding_amount(self):
        """Calculate outstanding amount based on order payment transactions"""
        from decimal import Decimal
        from django.db.models import Sum
        
        # Get successful payment transactions for this order
        from payments.models import PaymentTransaction
        successful_payments = PaymentTransaction.objects.filter(
            order=self.order,
            status='successful'
        )
        
        total_paid = successful_payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        # Calculate outstanding amount
        order_total = Decimal(str(self.order.total_amount))
        outstanding_amount = max(Decimal('0'), order_total - total_paid)
        
        # Set the outstanding amount
        self.outstanding_amount = outstanding_amount
    
    def _set_due_date(self):
        """Set due date based on payment terms"""
        days_map = {
            'net_7': 7,
            'net_15': 15,
            'net_30': 30,
            'net_45': 45,
            'net_60': 60,
        }
        
        if self.payment_terms in days_map:
            from datetime import timedelta
            self.due_date = timezone.now() + timedelta(days=days_map[self.payment_terms])
    
    @property
    def is_paid(self):
        return self.status == 'paid'
    
    @property
    def is_overdue(self):
        if not self.due_date or self.is_paid:
            return False
        return timezone.now() > self.due_date
    
    @property
    def is_draft(self):
        return self.status == 'draft'
    
    @property
    def can_be_sent(self):
        return self.status == 'draft'
    
    @property
    def can_be_paid(self):
        return self.status in ['sent', 'overdue']
    
    def send_invoice(self):
        """Mark invoice as sent"""
        if self.status == 'draft':
            self.status = 'sent'
            self.sent_at = timezone.now()
            self.save()
    
    def mark_as_paid(self, payment_method=None, transaction_id=None):
        """Mark invoice as paid"""
        if self.can_be_paid:
            self.status = 'paid'
            self.amount_paid = self.total_amount
            self.balance_due = 0
            self.payment_method = payment_method
            self.payment_transaction_id = transaction_id
            self.payment_date = timezone.now()
            self.paid_at = timezone.now()
            self.save()
    
    def apply_payment(self, amount, payment_method=None, transaction_id=None):
        """Apply partial payment to invoice"""
        if amount > 0 and self.balance_due > 0:
            payment_amount = min(amount, self.balance_due)
            self.amount_paid += payment_amount
            self.balance_due -= payment_amount
            
            # Recalculate outstanding amount
            self.outstanding_amount = max(Decimal('0'), self.total_amount - self.amount_paid)
            
            if self.balance_due == 0:
                self.status = 'paid'
                self.paid_at = timezone.now()
            
            self.payment_method = payment_method
            self.payment_transaction_id = transaction_id
            self.payment_date = timezone.now()
            self.save()
    
    def cancel_invoice(self):
        """Cancel invoice"""
        if self.status in ['draft', 'sent']:
            self.status = 'cancelled'
            self.save()
    
    @classmethod
    def create_from_order(cls, order, payment_terms='immediate'):
        """Create invoice from order with consideration for partial payments and delivery fees"""
        from decimal import Decimal
        from django.db.models import Sum
        
        # Calculate outstanding amount based on payment transactions
        from payments.models import PaymentTransaction
        successful_payments = PaymentTransaction.objects.filter(
            order=order,
            status='successful'
        )
        
        total_paid = successful_payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        # Calculate outstanding amount
        order_total = Decimal(str(order.total_amount))
        outstanding_amount = max(Decimal('0'), order_total - total_paid)
        
        # Determine invoice amount based on payment status
        if total_paid > 0:
            # There are partial payments, use outstanding amount
            invoice_amount = outstanding_amount
            notes = f"Invoice for order {order.order_number} - Outstanding balance: {outstanding_amount}"
        else:
            # No payments, use full order amount
            invoice_amount = order_total
            notes = f"Invoice for order {order.order_number}"
        
        # Add delivery fee to notes if order is for delivery (not pickup)
        if not order.is_pickup and order.delivery_fee > 0:
            notes += f" (Includes delivery fee: {order.delivery_fee})"
        
        # Create invoice with original order structure but outstanding amount calculation
        invoice = cls.objects.create(
            order=order,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            customer_phone=order.customer_phone,
            customer_address=order.delivery_address,
            subtotal=order.subtotal,
            tax_amount=order.tax,
            tax_rate=Decimal('10.00'),  # Default 10% tax rate
            delivery_fee=order.delivery_fee,  # Include delivery fee from order
            discount_amount=order.discount,
            total_amount=order.total_amount,  # Keep original order total (includes delivery fee)
            payment_terms=payment_terms,
            notes=notes
        )
        
        # Set the outstanding amount to the calculated outstanding amount
        invoice.outstanding_amount = outstanding_amount
        invoice.balance_due = outstanding_amount  # Balance due should be the outstanding amount
        invoice.save()
        
        return invoice


class Order(models.Model):
    """
    Order model for customer purchases
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('ready_for_delivery', 'Ready for Delivery'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Wallet'),
    ]
    
    # Order information
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='orders')
    
    # Customer details (snapshot at time of order)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Delivery/Pickup information
    is_pickup = models.BooleanField(default=False)
    delivery_address = models.TextField(blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True)
    delivery_person = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_orders')
    delivery_person_name = models.CharField(max_length=200, blank=True, null=True)
    delivery_person_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Detailed address fields
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    tracking_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        # Generate order number if not provided
        if not self.order_number:
            self.order_number = self._generate_order_number()
        
        # Calculate totals
        self._calculate_totals()
        
        super().save(*args, **kwargs)
    
    def _generate_order_number(self):
        """Generate unique order number"""
        import random
        import string
        
        while True:
            # Format: ORD-YYYYMMDD-XXXXX
            date_part = timezone.now().strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            order_number = f"ORD-{date_part}-{random_part}"
            
            if not Order.objects.filter(order_number=order_number).exists():
                return order_number
    
    def _calculate_totals(self):
        """Calculate order totals"""
        # If the order hasn't been saved yet, we can't access related items
        if self.pk is None:
            # Set default values for new orders
            self.subtotal = Decimal('0.00')
            self.tax = Decimal('0.00')
            self.total_amount = self.delivery_fee - self.discount
            return
        
        # Calculate totals from related items
        subtotal = sum(item.total_price for item in self.items.all())
        self.subtotal = subtotal
        
        # Calculate tax (example: 10%)
        self.tax = subtotal * Decimal('0.10')
        
        # Calculate total
        self.total_amount = self.subtotal + self.tax + self.delivery_fee - self.discount
    
    @property
    def is_active(self):
        return self.status not in ['delivered', 'cancelled', 'refunded']
    
    @property
    def is_completed(self):
        return self.status == 'delivered'
    
    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'confirmed', 'processing']
    
    def can_transition_to(self, new_status):
        """Check if order can transition to new status"""
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['processing', 'cancelled'],
            'processing': ['ready_for_delivery', 'cancelled'],
            'ready_for_delivery': ['out_for_delivery', 'cancelled'],
            'out_for_delivery': ['delivered', 'cancelled'],
            'delivered': ['refunded'],
            'cancelled': ['pending'],  # Allow reactivation
            'refunded': []
        }
        
        current_valid_transitions = valid_transitions.get(self.status, [])
        return new_status in current_valid_transitions
    
    def update_status(self, new_status, user=None):
        """Update order status with validation"""
        if not self.can_transition_to(new_status):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")
        
        old_status = self.status
        self.status = new_status
        
        # Update delivery times based on status
        if new_status == 'out_for_delivery':
            self.actual_delivery_time = timezone.now()
        elif new_status == 'delivered':
            self.actual_delivery_time = timezone.now()
        
        # Create OrderReceipt when status changes to ready_for_delivery
        if new_status == 'ready_for_delivery' and old_status != 'ready_for_delivery':
            # Check if receipt already exists for this order
            if not self.receipts.exists():
                OrderReceipt.create_from_order(self)
                print(f"OrderReceipt created for order {self.order_number}")
        
        self.save()
        
        # Log status change
        print(f"Order {self.order_number} status changed from {old_status} to {new_status}")
        
        return self


class OrderItem(models.Model):
    """
    Individual items in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    product_variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Item details
    product_name = models.CharField(max_length=200)  # Snapshot of product name
    product_sku = models.CharField(max_length=50)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'order_items'
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Cart(models.Model):
    """
    Shopping cart for users
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
    
    def __str__(self):
        return f"Cart for {self.user.email}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """
    Items in shopping cart
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    product_variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'product', 'product_variant']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        price = self.product_variant.price if self.product_variant else self.product.price
        return price * self.quantity


class Wishlist(models.Model):
    """
    User wishlist
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'wishlist'
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


class Review(models.Model):
    """
    Product reviews
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MinValueValidator(5)])
    title = models.CharField(max_length=200, blank=True, null=True)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product average rating
        self._update_product_rating()
    
    def _update_product_rating(self):
        """Update product's average rating"""
        reviews = self.product.reviews.all()
        if reviews.exists():
            avg_rating = sum(review.rating for review in reviews) / reviews.count()
            self.product.average_rating = round(avg_rating, 2)
            self.product.review_count = reviews.count()
            self.product.save()
