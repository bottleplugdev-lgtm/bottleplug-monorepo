from rest_framework import serializers
from .models import (
    PaymentMethod, PaymentTransaction, PaymentWebhook, 
    PaymentRefund, PaymentPlan, PaymentSubscription, PaymentReceipt
)


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Payment method serializer"""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'payment_type', 'is_active', 'min_amount', 
            'max_amount', 'processing_fee', 'fixed_fee', 'flutterwave_code',
            'country_code', 'currency', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Basic payment transaction serializer"""
    payment_method = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'transaction_id', 'reference', 'transaction_type', 'status',
            'amount', 'currency', 'fee', 'net_amount', 'customer_name',
            'customer_email', 'payment_url', 'payment_method', 'order_id', 'invoice', 'event', 'receipt',
            'created_at', 'paid_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'reference', 'net_amount', 'created_at', 'paid_at'
        ]
    
    def get_payment_method(self, obj):
        """Return payment method type as string"""
        if obj.payment_method:
            return obj.payment_method.payment_type
        return obj.payment_type or 'unknown'


class PaymentTransactionDetailSerializer(serializers.ModelSerializer):
    """Detailed payment transaction serializer"""
    payment_method = PaymentMethodSerializer(read_only=True)
    payment_method_type = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'transaction_id', 'reference', 'flutterwave_reference',
            'transaction_type', 'status', 'amount', 'currency', 'fee', 'net_amount',
            'payment_method', 'payment_method_type', 'payment_type', 'order', 'invoice', 'event', 'receipt',
            'customer', 'customer_name', 'customer_email', 'customer_phone',
            'payment_url', 'redirect_url', 'callback_url', 'description',
            'created_at', 'updated_at', 'paid_at', 'expired_at', 'metadata'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'reference', 'flutterwave_reference',
            'net_amount', 'created_at', 'updated_at', 'paid_at', 'expired_at'
        ]
    
    def get_payment_method_type(self, obj):
        """Return payment method type as string"""
        if obj.payment_method:
            return obj.payment_method.payment_type
        return obj.payment_type or 'unknown'


class PaymentTransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment transactions"""
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'transaction_type', 'amount', 'currency', 'order', 'invoice', 
            'event', 'receipt', 'payment_method', 'payment_type', 'description', 
            'redirect_url', 'callback_url', 'metadata'
        ]
    
    def validate(self, data):
        from payments.models import PaymentMethod
        
        # Get payment type from payment_method or payment_type field
        payment_type = None
        payment_method_obj = None
        
        # Use initial_data to get the raw ID, not the converted object
        payment_method_id = self.initial_data.get('payment_method')
        if payment_method_id:
            payment_method_obj = PaymentMethod.objects.get(id=payment_method_id)
            payment_type = payment_method_obj.payment_type
        elif data.get('payment_type'):
            payment_type = data['payment_type']
        
        if not payment_type:
            raise serializers.ValidationError("Payment type must be specified either through payment_method or payment_type")
        
        # Get required fields for this payment type
        from payments.models import PaymentTransaction
        all_required_fields = PaymentTransaction.get_required_fields_for_payment_type(PaymentTransaction(), payment_type)
        
        # Remove customer fields since they're set automatically in create method
        customer_fields = ['customer', 'customer_email', 'customer_name', 'customer_phone']
        required_fields = [field for field in all_required_fields if field not in customer_fields]
        
        # Check for missing required fields
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            raise serializers.ValidationError(
                f"Missing required fields for {payment_type} payment: {', '.join(missing_fields)}"
            )
        
        # Validate amount against payment method limits
        amount = data.get('amount')
        if amount and payment_method_obj:
            # Check minimum amount
            if payment_method_obj.min_amount and amount < payment_method_obj.min_amount:
                raise serializers.ValidationError(
                    f"Amount must be at least {payment_method_obj.min_amount} {payment_method_obj.currency}"
                )
            
            # Check maximum amount (except for cash which is unlimited)
            if payment_method_obj.max_amount and amount > payment_method_obj.max_amount:
                raise serializers.ValidationError(
                    f"Amount cannot exceed {payment_method_obj.max_amount} {payment_method_obj.currency}"
                )
        
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['customer'] = request.user
            validated_data['customer_name'] = request.user.get_full_name() or request.user.email
            validated_data['customer_email'] = request.user.email
            # Set customer_phone with a default value if not provided
            validated_data['customer_phone'] = getattr(request.user, 'phone', '') or '0000000000'
        
        return super().create(validated_data)


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """Payment webhook serializer"""
    
    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'webhook_id', 'transaction', 'event_type', 'webhook_data',
            'processed', 'processing_error', 'received_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'webhook_id', 'received_at', 'processed_at'
        ]


class PaymentRefundSerializer(serializers.ModelSerializer):
    """Payment refund serializer"""
    
    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'refund_id', 'reference', 'original_transaction', 'amount',
            'reason', 'status', 'created_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'refund_id', 'reference', 'created_at', 'processed_at'
        ]


class PaymentRefundCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment refunds"""
    
    class Meta:
        model = PaymentRefund
        fields = ['original_transaction', 'amount', 'reason']
    
    def validate_amount(self, value):
        transaction = self.initial_data.get('original_transaction')
        if transaction:
            try:
                from .models import PaymentTransaction
                payment_transaction = PaymentTransaction.objects.get(id=transaction)
                if value > payment_transaction.amount:
                    raise serializers.ValidationError("Refund amount cannot exceed original payment amount")
            except PaymentTransaction.DoesNotExist:
                raise serializers.ValidationError("Invalid payment transaction")
        return value


class PaymentPlanSerializer(serializers.ModelSerializer):
    """Payment plan serializer"""
    
    class Meta:
        model = PaymentPlan
        fields = [
            'id', 'name', 'description', 'amount', 'currency', 'interval',
            'interval_count', 'flutterwave_plan_id', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentSubscriptionSerializer(serializers.ModelSerializer):
    """Payment subscription serializer"""
    plan = PaymentPlanSerializer(read_only=True)
    
    class Meta:
        model = PaymentSubscription
        fields = [
            'id', 'subscription_id', 'customer', 'plan', 'status', 'start_date',
            'end_date', 'next_payment_date', 'flutterwave_subscription_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'subscription_id', 'created_at', 'updated_at'
        ]


class PaymentSubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment subscriptions"""
    
    class Meta:
        model = PaymentSubscription
        fields = ['plan', 'start_date', 'next_payment_date']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['customer'] = request.user
        
        return super().create(validated_data)


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating payments"""
    transaction_type = serializers.ChoiceField(choices=PaymentTransaction.TRANSACTION_TYPES)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='NGN')
    order_id = serializers.IntegerField(required=False)
    invoice_id = serializers.IntegerField(required=False)
    event_id = serializers.IntegerField(required=False)
    receipt_id = serializers.IntegerField(required=False)
    payment_method_id = serializers.IntegerField(required=False)
    payment_details = serializers.JSONField(required=False)
    description = serializers.CharField(required=False)
    redirect_url = serializers.URLField(required=False)
    callback_url = serializers.URLField(required=False)
    metadata = serializers.JSONField(required=False)
    
    def validate(self, data):
        # Ensure at least one related entity is provided
        related_entities = ['order_id', 'invoice_id', 'event_id', 'receipt_id']
        if not any(data.get(field) for field in related_entities):
            raise serializers.ValidationError("At least one related entity must be provided")
        
        # Validate amount against payment method limits
        amount = data.get('amount')
        payment_method_id = data.get('payment_method_id')
        
        if amount and payment_method_id:
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id)
                
                # Check minimum amount
                if payment_method.min_amount and amount < payment_method.min_amount:
                    raise serializers.ValidationError(
                        f"Amount must be at least {payment_method.min_amount} {payment_method.currency}"
                    )
                
                # Check maximum amount (except for cash which is unlimited)
                if payment_method.max_amount and amount > payment_method.max_amount:
                    raise serializers.ValidationError(
                        f"Amount cannot exceed {payment_method.max_amount} {payment_method.currency}"
                    )
                    
            except PaymentMethod.DoesNotExist:
                raise serializers.ValidationError("Invalid payment method")
        
        return data


class PaymentVerifySerializer(serializers.Serializer):
    """Serializer for verifying payments"""
    transaction_id = serializers.CharField()
    reference = serializers.CharField()


class PaymentWebhookSerializer(serializers.Serializer):
    """Serializer for processing webhooks"""
    event = serializers.CharField()
    data = serializers.JSONField()
    signature = serializers.CharField(required=False)


class BankAccountValidationSerializer(serializers.Serializer):
    """Serializer for bank account validation"""
    account_number = serializers.CharField()
    account_bank = serializers.CharField()


class PaymentStatsSerializer(serializers.Serializer):
    """Serializer for payment statistics"""
    total_transactions = serializers.IntegerField()
    successful_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    pending_transactions = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_fees = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    refunds_count = serializers.IntegerField()
    refunds_amount = serializers.DecimalField(max_digits=10, decimal_places=2) 


class PaymentReceiptSerializer(serializers.ModelSerializer):
    """Payment receipt serializer"""
    class Meta:
        model = PaymentReceipt
        fields = '__all__'