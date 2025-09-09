from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class PaymentMethod(models.Model):
    """
    Payment method configuration for Flutterwave
    """
    PAYMENT_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('ussd', 'USSD'),
        ('qr', 'QR Code'),
        ('barter', 'Barter'),
        ('mpesa', 'M-Pesa'),
        ('gh_mo_mo', 'Ghana Mobile Money'),
        ('ug_mo_mo', 'Uganda Mobile Money'),
        ('franc_mo_mo', 'Francophone Mobile Money'),
        ('emz_mo_mo', 'EMZ Mobile Money'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('payattitude', 'PayAttitude'),
        ('cash', 'Cash Payment'),
    ]
    
    name = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    is_active = models.BooleanField(default=True)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    processing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Flutterwave specific
    flutterwave_code = models.CharField(max_length=50, unique=True)
    country_code = models.CharField(max_length=3, default='NG')
    currency = models.CharField(max_length=3, default='NGN')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_payment_type_display()})"


class PaymentTransaction(models.Model):
    """
    Main payment transaction model
    """
    TRANSACTION_TYPES = [
        ('order', 'Order Payment'),
        ('invoice', 'Invoice Payment'),
        ('event', 'Event Payment'),
        ('subscription', 'Subscription Payment'),
        ('refund', 'Refund'),
        ('transfer', 'Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('successful', 'Successful'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('reversed', 'Reversed'),
    ]
    
    # Transaction identification
    transaction_id = models.CharField(max_length=100, unique=True)
    reference = models.CharField(max_length=100, unique=True)
    flutterwave_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment method
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    payment_type = models.CharField(max_length=20, blank=True, null=True)
    
    # Related entities
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    invoice = models.ForeignKey('orders.Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    receipt = models.ForeignKey('orders.OrderReceipt', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    # Customer information
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='payments')
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    customer_name = models.CharField(max_length=200)
    
    # Payment details
    payment_url = models.URLField(blank=True, null=True)
    redirect_url = models.URLField(blank=True, null=True)
    callback_url = models.URLField(blank=True, null=True)
    
    # Flutterwave response data
    flutterwave_response = models.JSONField(default=dict, blank=True)
    flutterwave_webhook_data = models.JSONField(default=dict, blank=True)
    
    # Flutterwave specific IDs
    flutterwave_charge_id = models.CharField(max_length=100, blank=True, null=True)
    flutterwave_customer_id = models.CharField(max_length=100, blank=True, null=True)
    flutterwave_payment_method_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Idempotency tracking
    idempotency_cache_hit = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    
    # Additional information
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.customer_name} ({self.amount} {self.currency})"
    
    def save(self, *args, **kwargs):
        # Generate transaction ID if not provided
        if not self.transaction_id:
            self.transaction_id = self._generate_transaction_id()
        
        # Generate reference if not provided
        if not self.reference:
            self.reference = self._generate_reference()
        
        # Set payment_type from payment_method if not provided
        if self.payment_method and not self.payment_type:
            self.payment_type = self.payment_method.payment_type
        
        # Validate payment method requirements
        self._validate_payment_method_requirements()
        
        # Calculate net amount
        self.net_amount = self.amount - self.fee
        
        # Set expiration time for pending transactions (30 minutes)
        if self.status == 'pending' and not self.expired_at:
            from datetime import timedelta
            self.expired_at = timezone.now() + timedelta(minutes=30)
        
        super().save(*args, **kwargs)
    
    def _validate_payment_method_requirements(self):
        """Validate that required fields are provided based on payment type"""
        if not self.payment_type:
            return
        
        # Required fields for all payment types
        required_fields = {
            'amount': 'Amount is required for all payment types',
            'currency': 'Currency is required for all payment types',
            'customer': 'Customer is required for all payment types',
            'customer_email': 'Customer email is required for all payment types',
            'customer_name': 'Customer name is required for all payment types',
        }
        
        # Additional requirements based on payment type
        if self.payment_type == 'card':
            required_fields.update({
                'redirect_url': 'Redirect URL is required for card payments',
                'callback_url': 'Callback URL is required for card payments',
            })
        elif self.payment_type == 'mobile_money':
            required_fields.update({
                'customer_phone': 'Customer phone number is required for mobile money payments',
            })
            # Only require redirect_url for mobile money if no Flutterwave charge ID (complete flows don't need it)
            if not self.flutterwave_charge_id:
                required_fields.update({
                    'redirect_url': 'Redirect URL is required for mobile money payments',
                })
        elif self.payment_type == 'cash':
            # Cash payments have minimal requirements
            pass
        
        # Validate required fields
        missing_fields = []
        for field, message in required_fields.items():
            if not getattr(self, field, None):
                missing_fields.append(message)
        
        if missing_fields:
            raise ValueError(f"Payment validation failed: {'; '.join(missing_fields)}")
        
        # Validate amount limits based on payment method
        if self.payment_method:
            if self.amount < self.payment_method.min_amount:
                raise ValueError(
                    f"Amount {self.amount} is below minimum {self.payment_method.min_amount} "
                    f"for {self.payment_method.name}"
                )
            
            if self.payment_method.max_amount and self.amount > self.payment_method.max_amount:
                raise ValueError(
                    f"Amount {self.amount} exceeds maximum {self.payment_method.max_amount} "
                    f"for {self.payment_method.name}"
                )
    
    def get_required_fields_for_payment_type(self, payment_type):
        """Get list of required fields for a specific payment type"""
        base_fields = [
            'amount', 'currency', 'customer', 'customer_email', 'customer_name'
        ]
        
        if payment_type == 'card':
            return base_fields + ['redirect_url', 'callback_url']
        elif payment_type == 'mobile_money':
            # For mobile money, redirect_url is only required if no Flutterwave charge ID
            # Complete mobile money flows don't need redirect URLs
            return base_fields + ['customer_phone']
        elif payment_type == 'cash':
            return base_fields
        else:
            return base_fields
    
    def _generate_transaction_id(self):
        """Generate unique transaction ID"""
        return f"TXN-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    def _generate_reference(self):
        """Generate unique reference"""
        return f"REF-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    @property
    def is_successful(self):
        return self.status == 'successful'
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def is_failed(self):
        return self.status in ['failed', 'cancelled', 'expired']
    
    @property
    def is_expired(self):
        if self.expired_at:
            return timezone.now() > self.expired_at
        return False
    
    def mark_as_paid(self):
        """Mark transaction as paid"""
        self.status = 'successful'
        self.paid_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, reason=None):
        """Mark transaction as failed"""
        self.status = 'failed'
        if reason:
            self.metadata['failure_reason'] = reason
        self.save()
    
    def mark_as_expired(self):
        """Mark transaction as expired"""
        self.status = 'expired'
        self.save()


class PaymentWebhook(models.Model):
    """
    Store Flutterwave webhook data for audit
    """
    webhook_id = models.CharField(max_length=100, unique=True)
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='webhooks')
    
    # Webhook data
    event_type = models.CharField(max_length=50)
    webhook_data = models.JSONField()
    
    # Processing status
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)
    
    # Timestamps
    received_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_webhooks'
        ordering = ['-received_at']
    
    def __str__(self):
        return f"Webhook {self.webhook_id} - {self.event_type}"


class PaymentRefund(models.Model):
    """
    Payment refund model
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]
    
    # Refund identification
    refund_id = models.CharField(max_length=100, unique=True)
    reference = models.CharField(max_length=100, unique=True)
    
    # Original transaction
    original_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Flutterwave response
    flutterwave_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund {self.refund_id} - {self.amount}"
    
    def save(self, *args, **kwargs):
        # Generate refund ID if not provided
        if not self.refund_id:
            self.refund_id = f"REFUND-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Generate reference if not provided
        if not self.reference:
            self.reference = f"REFUND-REF-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        super().save(*args, **kwargs)


class PaymentReceipt(models.Model):
    """
    Payment receipt model for confirmed payments (cash, mobile_money, card, etc.)
    This is distinct from OrderReceipt (which is a delivery/confirmation receipt).
    """
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('void', 'Void'),
    ]

    # Identity
    receipt_number = models.CharField(max_length=50, unique=True)

    # Relations
    transaction = models.OneToOneField('payments.PaymentTransaction', on_delete=models.CASCADE, related_name='payment_receipt')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_receipts')
    invoice = models.ForeignKey('orders.Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_receipts')
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_receipts')

    # Customer snapshot
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True, null=True)

    # Payment details snapshot
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='NGN')
    payment_method_name = models.CharField(max_length=100, blank=True, null=True)
    payment_type = models.CharField(max_length=20, blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    notes = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_receipts'
        ordering = ['-created_at']

    def __str__(self):
        return f"PaymentReceipt {self.receipt_number} - {self.customer_name} ({self.amount} {self.currency})"

    def save(self, *args, **kwargs):
        # Generate receipt number if not provided
        if not self.receipt_number:
            self.receipt_number = self._generate_receipt_number()
        super().save(*args, **kwargs)

    def _generate_receipt_number(self):
        """Generate unique payment receipt number"""
        import random
        import string

        while True:
            date_part = timezone.now().strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            receipt_number = f"PAY_RCP_{date_part}_{random_part}"
            if not PaymentReceipt.objects.filter(receipt_number=receipt_number).exists():
                return receipt_number

class PaymentPlan(models.Model):
    """
    Recurring payment plans for subscriptions
    """
    INTERVAL_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Plan details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    interval_count = models.IntegerField(default=1)
    
    # Flutterwave plan ID
    flutterwave_plan_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Plan status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_plans'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.amount} {self.currency}"


class PaymentSubscription(models.Model):
    """
    Subscription model for recurring payments
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('paused', 'Paused'),
    ]
    
    # Subscription details
    subscription_id = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name='subscriptions')
    
    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField()
    
    # Flutterwave subscription ID
    flutterwave_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Subscription {self.subscription_id} - {self.customer.email}"
    
    def save(self, *args, **kwargs):
        # Generate subscription ID if not provided
        if not self.subscription_id:
            self.subscription_id = f"SUB-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        super().save(*args, **kwargs)
