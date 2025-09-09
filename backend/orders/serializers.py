from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem, Wishlist, Review, OrderReceipt, Invoice


class OrderReceiptSerializer(serializers.ModelSerializer):
    """Basic OrderReceipt serializer"""
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = OrderReceipt
        fields = [
            'id', 'receipt_number', 'order', 'order_number', 'customer_name', 
            'customer_email', 'customer_phone', 'status', 'total_amount',
            'delivery_address', 'delivery_instructions', 'delivery_person_name',
            'delivery_person_phone', 'created_at', 'sent_at', 'signed_at', 
            'delivered_at', 'notes'
        ]
        read_only_fields = ['id', 'receipt_number', 'created_at', 'sent_at', 'signed_at', 'delivered_at']


class OrderReceiptDetailSerializer(serializers.ModelSerializer):
    """Detailed OrderReceipt serializer"""
    order = serializers.SerializerMethodField()
    delivery_person = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderReceipt
        fields = [
            'id', 'receipt_number', 'order', 'customer_name', 'customer_email', 
            'customer_phone', 'status', 'total_amount', 'delivery_address', 
            'delivery_instructions', 'delivery_person', 'delivery_person_name',
            'delivery_person_phone', 'customer_signature', 'signature_date',
            'signature_ip', 'signature_user_agent', 'created_at', 'sent_at', 
            'signed_at', 'delivered_at', 'notes', 'tracking_data'
        ]
        read_only_fields = ['id', 'receipt_number', 'created_at', 'sent_at', 'signed_at', 'delivered_at']
    
    def get_order(self, obj):
        from .serializers import OrderSerializer
        return OrderSerializer(obj.order).data
    
    def get_delivery_person(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.delivery_person).data if obj.delivery_person else None


class OrderReceiptCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating receipts"""
    
    class Meta:
        model = OrderReceipt
        fields = [
            'order', 'notes'
        ]
    
    def create(self, validated_data):
        order = validated_data['order']
        return OrderReceipt.create_from_order(order)


class OrderReceiptUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating receipts"""
    
    class Meta:
        model = OrderReceipt
        fields = [
            'status', 'customer_signature', 'signature_ip', 'signature_user_agent',
            'notes', 'tracking_data'
        ]
    
    def update(self, instance, validated_data):
        # Handle status-specific updates
        if 'status' in validated_data:
            new_status = validated_data['status']
            if new_status == 'sent':
                instance.send_to_customer()
            elif new_status == 'signed':
                signature_data = validated_data.get('customer_signature')
                ip_address = validated_data.get('signature_ip')
                user_agent = validated_data.get('signature_user_agent')
                instance.sign_by_customer(signature_data, ip_address, user_agent)
            elif new_status == 'delivered':
                instance.mark_delivered()
        
        return super().update(instance, validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.CharField(source='product.image', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_image', 'product_variant',
            'product_sku', 'quantity', 'unit_price', 'total_price', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """Basic Order serializer"""
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name', 'customer_email',
            'customer_phone', 'status', 'payment_status', 'payment_method',
            'subtotal', 'tax', 'delivery_fee', 'discount', 'total_amount',
            'is_pickup', 'delivery_address', 'delivery_instructions', 
            'address_line1', 'address_line2', 'city', 'district', 'state', 
            'postal_code', 'country', 'estimated_delivery_time',
            'actual_delivery_time', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed Order serializer"""
    items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.SerializerMethodField()
    delivery_person = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name', 'customer_email',
            'customer_phone', 'status', 'payment_status', 'payment_method',
            'payment_transaction_id', 'subtotal', 'tax', 'delivery_fee', 'discount',
            'total_amount', 'is_pickup', 'delivery_address', 'delivery_instructions',
            'address_line1', 'address_line2', 'city', 'district', 'state', 
            'postal_code', 'country', 'delivery_person', 'delivery_person_name', 
            'delivery_person_phone', 'estimated_delivery_time', 'actual_delivery_time', 
            'created_at', 'updated_at', 'notes', 'cancellation_reason', 'tracking_data', 'items'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']
    
    def get_customer(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.customer).data if obj.customer else None
    
    def get_delivery_person(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.delivery_person).data if obj.delivery_person else None


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    items = serializers.ListField(child=serializers.DictField(), write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_email', 'customer_phone', 'payment_method',
            'is_pickup', 'delivery_address', 'delivery_instructions', 'notes',
            'address_line1', 'address_line2', 'city', 'district', 'state', 
            'postal_code', 'country',
            # Accept delivery fee during creation
            'delivery_fee',
            'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        customer = self.context['request'].user
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            customer_name=validated_data.get('customer_name', customer.full_name),
            customer_email=validated_data.get('customer_email', customer.email),
            customer_phone=validated_data.get('customer_phone', customer.phone_number),
            payment_method=validated_data.get('payment_method', 'cash'),
            is_pickup=validated_data.get('is_pickup', False),
            delivery_address=validated_data.get('delivery_address'),
            delivery_instructions=validated_data.get('delivery_instructions'),
            address_line1=validated_data.get('address_line1'),
            address_line2=validated_data.get('address_line2'),
            city=validated_data.get('city'),
            district=validated_data.get('district'),
            state=validated_data.get('state'),
            postal_code=validated_data.get('postal_code'),
            country=validated_data.get('country'),
            notes=validated_data.get('notes'),
            # Store delivery fee if provided (0 by default)
            delivery_fee=validated_data.get('delivery_fee', 0),
        )
        
        # Create order items
        for item_data in items_data:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            
            try:
                from products.models import Product
                product = Product.objects.get(id=product_id)
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.sku,
                    quantity=quantity,
                    unit_price=product.price,
                )
                
                # Update product stock
                product.update_stock(-quantity)
                
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with id {product_id} does not exist")
        
        # Recalculate totals after all items are created
        order._calculate_totals()
        order.save()
        
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating orders with partial updates and cost calculations"""
    items = serializers.ListField(child=serializers.DictField(), required=False, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            # Customer information
            'customer_name', 'customer_email', 'customer_phone',
            
            # Order details
            'status', 'payment_status', 'payment_method', 'payment_transaction_id',
            
            # Delivery information
            'is_pickup', 'delivery_address', 'delivery_instructions',
            'delivery_person', 'delivery_person_name', 'delivery_person_phone',
            'address_line1', 'address_line2', 'city', 'district', 'state', 
            'postal_code', 'country',
            
            # Pricing (optional - will be calculated if items are provided)
            'subtotal', 'tax', 'delivery_fee', 'discount', 'total_amount',
            
            # Timestamps
            'estimated_delivery_time', 'actual_delivery_time',
            
            # Additional information
            'notes', 'cancellation_reason', 'tracking_data',
            
            # Items (for updating order items)
            'items'
        ]
    
    def update(self, instance, validated_data):
        """Update order with automatic cost calculations"""
        items_data = validated_data.pop('items', None)
        
        # Update order fields
        for field, value in validated_data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        
        # Handle items update if provided
        if items_data is not None:
            # Clear existing items
            from .models import OrderItem
            OrderItem.objects.filter(order=instance).delete()
            
            # Create new items
            for item_data in items_data:
                product_id = item_data.get('product_id')
                quantity = item_data.get('quantity', 1)
                
                if product_id:
                    from products.models import Product
                    try:
                        product = Product.objects.get(id=product_id)
                        OrderItem.objects.create(
                            order=instance,
                            product=product,
                            product_name=product.name,
                            product_sku=product.sku or '',
                            quantity=quantity,
                            unit_price=product.price,
                            total_price=product.price * quantity
                        )
                    except Product.DoesNotExist:
                        continue
        
        # Recalculate totals if items were updated or pricing fields were changed
        if items_data is not None or any(field in validated_data for field in ['subtotal', 'tax', 'delivery_fee', 'discount']):
            instance._calculate_totals()
        
        instance.save()
        return instance


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.CharField(source='product.image', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_name', 'product_image', 'product_price',
            'product_variant', 'quantity', 'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items', 'total_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for adding items to cart"""
    
    class Meta:
        model = CartItem
        fields = ['product', 'product_variant', 'quantity']
    
    def create(self, validated_data):
        user = self.context['request'].user
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Check if item already exists in cart
        existing_item = CartItem.objects.filter(
            cart=cart,
            product=validated_data['product'],
            product_variant=validated_data.get('product_variant')
        ).first()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += validated_data.get('quantity', 1)
            existing_item.save()
            return existing_item
        else:
            # Create new item
            return CartItem.objects.create(cart=cart, **validated_data)


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating cart items"""
    
    class Meta:
        model = CartItem
        fields = ['quantity']


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.CharField(source='product.image', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = Wishlist
        fields = [
            'id', 'user', 'product', 'product_name', 'product_image',
            'product_price', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user']
    
    def create(self, validated_data):
        """Automatically set the user from the request"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_name', 'product', 'product_name', 'order',
            'rating', 'title', 'comment', 'is_verified_purchase',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    
    class Meta:
        model = Review
        fields = ['product', 'order', 'rating', 'title', 'comment']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return Review.objects.create(**validated_data)


class OrderStatsSerializer(serializers.Serializer):
    """Serializer for order statistics"""
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class OrderFilterSerializer(serializers.Serializer):
    """Serializer for order filtering"""
    status = serializers.CharField(max_length=20, required=False)
    payment_status = serializers.CharField(max_length=20, required=False)
    payment_method = serializers.CharField(max_length=20, required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    min_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False) 


# ===== INVOICE SERIALIZERS =====

class InvoiceSerializer(serializers.ModelSerializer):
    """Basic invoice serializer"""
    customer_name = serializers.CharField(read_only=True)
    invoice_number = serializers.CharField(read_only=True)
    order = OrderSerializer(read_only=True)  # Include order data for filtering
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'order', 'customer_name', 'customer_email', 
            'customer_phone', 'status', 'payment_terms', 'due_date', 'subtotal',
            'tax_amount', 'tax_rate', 'delivery_fee', 'discount_amount', 'total_amount',
            'amount_paid', 'balance_due', 'outstanding_amount', 'created_at', 'sent_at', 'paid_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'customer_name', 'customer_email', 
            'customer_phone', 'subtotal', 'tax_amount', 'total_amount',
            'amount_paid', 'balance_due', 'created_at', 'sent_at', 'paid_at'
        ]


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Detailed invoice serializer with nested data"""
    order = OrderSerializer(read_only=True)
    customer_name = serializers.CharField(read_only=True)
    invoice_number = serializers.CharField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'order', 'customer_name', 'customer_email', 
            'customer_phone', 'customer_address', 'status', 'payment_terms', 
            'due_date', 'subtotal', 'tax_amount', 'tax_rate', 'delivery_fee', 'discount_amount', 
            'total_amount', 'amount_paid', 'balance_due', 'outstanding_amount', 'payment_method',
            'payment_transaction_id', 'payment_date', 'created_at', 'sent_at', 
            'paid_at', 'updated_at', 'notes', 'terms_and_conditions', 'company_info'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'customer_name', 'customer_email', 
            'customer_phone', 'customer_address', 'subtotal', 'tax_amount', 
            'total_amount', 'amount_paid', 'balance_due', 'created_at', 
            'sent_at', 'paid_at', 'updated_at'
        ]


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invoices"""
    invoice_date = serializers.DateField(required=False, write_only=True)
    due_date = serializers.DateField(required=False, write_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'order', 'payment_terms', 'tax_rate', 'delivery_fee', 'discount_amount', 
            'invoice_date', 'due_date', 'notes', 'terms_and_conditions', 'company_info'
        ]
    
    def create(self, validated_data):
        order = validated_data.get('order')
        if not order:
            raise serializers.ValidationError("Order is required")
        
        # Check for existing invoices for this order
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        existing_invoices = Invoice.objects.filter(order=order)
        
        # Check if there are any invoices with non-expired due dates
        today = timezone.now().date()
        non_expired_invoices = existing_invoices.filter(
            due_date__gte=today,
            status__in=['draft', 'sent']
        ).exclude(status='paid')
        
        if non_expired_invoices.exists():
            # Get the most recent non-expired invoice
            latest_invoice = non_expired_invoices.order_by('-created_at').first()
            days_until_due = (latest_invoice.due_date.date() - today).days
            
            if days_until_due > 0:
                raise serializers.ValidationError(
                    f"Cannot create new invoice. Order #{order.order_number} already has an active invoice "
                    f"(#{latest_invoice.invoice_number}) with due date {latest_invoice.due_date.strftime('%Y-%m-%d')} "
                    f"({days_until_due} days remaining)."
                )
            elif days_until_due == 0:
                raise serializers.ValidationError(
                    f"Cannot create new invoice. Order #{order.order_number} already has an active invoice "
                    f"(#{latest_invoice.invoice_number}) due today."
                )
        
        # Check if there are any invoices with expired due dates but still in draft/sent status
        expired_invoices = existing_invoices.filter(
            due_date__lt=today,
            status__in=['draft', 'sent']
        ).exclude(status='paid')
        
        if expired_invoices.exists():
            # Allow creating new invoice if previous ones are expired
            pass
        
        # Create invoice using the model's create_from_order method
        payment_terms = validated_data.get('payment_terms', 'immediate')
        invoice = Invoice.create_from_order(order, payment_terms)
        
        # Update additional fields if provided
        if 'tax_rate' in validated_data:
            invoice.tax_rate = validated_data['tax_rate']
        if 'discount_amount' in validated_data:
            invoice.discount_amount = validated_data['discount_amount']
        if 'notes' in validated_data:
            invoice.notes = validated_data['notes']
        if 'terms_and_conditions' in validated_data:
            invoice.terms_and_conditions = validated_data['terms_and_conditions']
        if 'company_info' in validated_data:
            invoice.company_info = validated_data['company_info']
        
        # Handle custom dates if provided
        if 'due_date' in validated_data and validated_data['due_date']:
            # Convert date string to datetime
            due_date_str = validated_data['due_date']
            if isinstance(due_date_str, str):
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                invoice.due_date = timezone.make_aware(due_date)
            else:
                invoice.due_date = due_date_str
        
        invoice.save()
        return invoice


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating invoices"""
    
    class Meta:
        model = Invoice
        fields = [
            'status', 'payment_terms', 'tax_rate', 'delivery_fee', 'discount_amount', 
            'amount_paid', 'payment_method', 'payment_transaction_id',
            'notes', 'terms_and_conditions', 'company_info'
        ]
        read_only_fields = ['amount_paid']  # Use apply_payment method instead
    
    def update(self, instance, validated_data):
        # Handle status changes
        if 'status' in validated_data:
            new_status = validated_data['status']
            if new_status == 'sent' and instance.can_be_sent:
                instance.send_invoice()
            elif new_status == 'cancelled':
                instance.cancel_invoice()
        
        # Handle payment application
        if 'amount_paid' in validated_data:
            amount = validated_data['amount_paid']
            payment_method = validated_data.get('payment_method')
            transaction_id = validated_data.get('payment_transaction_id')
            instance.apply_payment(amount, payment_method, transaction_id)
        
        # Update other fields
        for field, value in validated_data.items():
            if field not in ['status', 'amount_paid']:
                setattr(instance, field, value)
        
        instance.save()
        return instance


class InvoicePaymentSerializer(serializers.Serializer):
    """Serializer for invoice payments"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.CharField(max_length=50, required=False)
    transaction_id = serializers.CharField(max_length=100, required=False)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than 0")
        return value


class InvoiceStatsSerializer(serializers.Serializer):
    """Serializer for invoice statistics"""
    total_invoices = serializers.IntegerField()
    draft_invoices = serializers.IntegerField()
    sent_invoices = serializers.IntegerField()
    paid_invoices = serializers.IntegerField()
    overdue_invoices = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_outstanding = serializers.DecimalField(max_digits=10, decimal_places=2) 