# Flutterwave Payment Integration Documentation

## 🎯 Overview

This document describes the complete Flutterwave payment integration implemented in the BottlePlug Dashboard. The system supports multiple payment methods for Uganda (UGX currency) and provides a comprehensive payment processing solution.

## 🏗️ Architecture

### Backend Components

#### 1. Django Models (`payments/models.py`)
```python
PaymentMethod - Payment method configuration
PaymentTransaction - Main payment transactions
PaymentWebhook - Webhook data storage
PaymentRefund - Refund management
PaymentPlan - Subscription plans
PaymentSubscription - Recurring payments
```

#### 2. Flutterwave Service (`payments/services.py`)
```python
class FlutterwaveService:
    - create_payment_link() - Create payment URLs
    - verify_payment() - Verify payment status
    - process_webhook() - Handle webhooks
    - create_refund() - Process refunds
    - get_banks() - Get bank list
    - validate_bank_account() - Validate accounts
```

#### 3. API Views (`payments/views.py`)
```python
PaymentTransactionViewSet - CRUD for transactions
PaymentMethodViewSet - Payment methods management
PaymentWebhookViewSet - Webhook processing
PaymentRefundViewSet - Refund management
FlutterwaveUtilityViewSet - Bank utilities
```

### Frontend Components

#### 1. PaymentButton Component (`src/components/PaymentButton.vue`)
- Reusable payment button component
- Supports multiple transaction types
- Handles payment initiation
- Shows payment modal with details

#### 2. Payments Test Page (`src/views/dashboard/Payments.vue`)
- Test payment functionality
- Sample payments for orders, invoices, events
- Configuration display
- Testing instructions

## ⚙️ Configuration

### Environment Variables
```bash
# Required for production
FLUTTERWAVE_SECRET_KEY=your_secret_key_here

# Current configuration
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK-097dab2699e3f44fa1fa051376bd63e5-X
DEFAULT_PAYMENT_CURRENCY=UGX
DEFAULT_PAYMENT_COUNTRY=UG
DEFAULT_PAYMENT_OPTIONS=card,payattitude,barter,bank transfer,ussd
DEFAULT_REDIRECT_URL=boozenation://return
```

### Settings (`tanna_backend/settings.py`)
```python
# Flutterwave Configuration
FLUTTERWAVE_SECRET_KEY = config('FLUTTERWAVE_SECRET_KEY', default='')
FLUTTERWAVE_PUBLIC_KEY = config('FLUTTERWAVE_PUBLIC_KEY', default='FLWPUBK-097dab2699e3f44fa1fa051376bd63e5-X')
FLUTTERWAVE_BASE_URL = config('FLUTTERWAVE_BASE_URL', default='https://api.flutterwave.com/v3')

# Default Payment Settings
DEFAULT_PAYMENT_CURRENCY = config('DEFAULT_PAYMENT_CURRENCY', default='UGX')
DEFAULT_PAYMENT_COUNTRY = config('DEFAULT_PAYMENT_COUNTRY', default='UG')
DEFAULT_PAYMENT_OPTIONS = config('DEFAULT_PAYMENT_OPTIONS', default='card,payattitude,barter,bank transfer,ussd')
DEFAULT_REDIRECT_URL = config('DEFAULT_REDIRECT_URL', default='boozenation://return')
```

## 🔧 API Endpoints

### Payment Transactions
```
GET    /api/v1/payments/transactions/              - List transactions
POST   /api/v1/payments/transactions/              - Create transaction
GET    /api/v1/payments/transactions/{id}/         - Get transaction
PATCH  /api/v1/payments/transactions/{id}/         - Update transaction
DELETE /api/v1/payments/transactions/{id}/         - Delete transaction

POST   /api/v1/payments/transactions/initiate_payment/  - Start payment
POST   /api/v1/payments/transactions/{id}/verify_payment/  - Verify payment
GET    /api/v1/payments/transactions/my_transactions/  - User transactions
GET    /api/v1/payments/transactions/stats/        - Payment statistics
```

### Payment Methods
```
GET    /api/v1/payments/payment-methods/           - List payment methods
GET    /api/v1/payments/payment-methods/by_country/ - Methods by country
```

### Refunds
```
GET    /api/v1/payments/refunds/                   - List refunds
POST   /api/v1/payments/refunds/                   - Create refund
POST   /api/v1/payments/refunds/create_flutterwave_refund/ - Process refund
```

### Flutterwave Utilities
```
GET    /api/v1/payments/flutterwave/banks/         - Get bank list
POST   /api/v1/payments/flutterwave/validate_bank_account/ - Validate account
```

### Webhooks
```
POST   /api/v1/payments/webhooks/flutterwave_webhook/ - Process webhooks
```

## 💳 Supported Payment Methods

### Uganda (UGX)
1. **Credit/Debit Cards**
   - Visa, Mastercard, American Express
   - Minimum: UGX 100
   - Maximum: UGX 7,000,000

2. **Mobile Money**
   - MTN Mobile Money
   - Airtel Money
   - Minimum: UGX 100
   - Maximum: UGX 7,000,000

3. **Bank Transfer**
   - Direct bank transfers
   - Minimum: UGX 1,000
   - Maximum: UGX 3,000,000

4. **USSD**
   - USSD payments
   - Minimum: UGX 100
   - Maximum: UGX 100,000

5. **Barter**
   - Barter payments
   - Minimum: UGX 100
   - Maximum: UGX 100,000

6. **PayAttitude**
   - PayAttitude wallet
   - Minimum: UGX 100
   - Maximum: UGX 100,000

7. **Cash Payment**
   - Cash on delivery
   - Minimum: UGX 0
   - Maximum: Unlimited

## 🔄 Payment Flow

### 1. Payment Initiation
```javascript
// Frontend
const payment = await initiatePayment({
  transaction_type: 'order',
  amount: 25000,
  currency: 'UGX',
  order_id: 123,
  description: 'Payment for order #123'
})
```

### 2. Payment Processing
```python
# Backend
def create_payment_link(self, transaction):
    payload = {
        'tx_ref': transaction.reference,
        'amount': str(transaction.amount),
        'currency': transaction.currency,
        'redirect_url': transaction.redirect_url,
        'customer': {
            'email': transaction.customer_email,
            'name': transaction.customer_name
        },
        'payment_options': self.default_payment_options
    }
    
    # Create payment URL
    response = requests.post(f'{self.base_url}/payments', json=payload)
    return response.json()
```

### 3. Payment Verification
```javascript
// Frontend
const verification = await verifyPayment(transactionId)
if (verification.success && verification.verified) {
  // Payment successful
  updateOrderStatus('paid')
}
```

### 4. Webhook Processing
```python
# Backend
def process_webhook(self, webhook_data, signature):
    # Verify webhook signature
    if not self._verify_webhook_signature(webhook_data, signature):
        return False
    
    # Process payment status
    transaction_id = webhook_data.get('txRef')
    status = webhook_data.get('status')
    
    if status == 'successful':
        self._handle_payment_success(transaction_id, webhook_data)
    elif status == 'failed':
        self._handle_payment_failed(transaction_id, webhook_data)
```

## 🧪 Testing

### 1. Test Payment Flow
1. Navigate to `/dashboard/payments`
2. Click any "Pay" button
3. Review payment details in modal
4. Click "Proceed to Payment"
5. Check payment URL generation

### 2. Test Order Payment
1. Go to `/dashboard/orders`
2. Find an order with payment status "pending"
3. Click the "Pay" button in the actions column
4. Complete payment flow

### 3. Mock Mode
When `FLUTTERWAVE_SECRET_KEY` is not configured:
- System creates mock payment URLs
- No actual API calls to Flutterwave
- Perfect for development and testing
- All payment data still stored in database

## 🚀 Production Setup

### 1. Get Flutterwave Credentials
1. Contact Flutterwave support
2. Request production secret key
3. Set up webhook URL
4. Configure redirect URLs

### 2. Environment Configuration
```bash
# Production settings
FLUTTERWAVE_SECRET_KEY=FLWSECK-xxxxxxxxxxxxxxxxxxxxx
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK-xxxxxxxxxxxxxxxxxxxxx
FLUTTERWAVE_SECRET_HASH=your_webhook_secret_hash
DEFAULT_REDIRECT_URL=https://yourdomain.com/payment/return
```

### 3. Webhook Configuration
```bash
# In Flutterwave Dashboard
Webhook URL: https://yourdomain.com/api/v1/payments/webhooks/flutterwave_webhook/
Secret Hash: your_webhook_secret_hash
```

### 4. SSL Certificate
- Ensure your domain has valid SSL certificate
- Required for webhook communication
- Flutterwave requires HTTPS for webhooks

## 📊 Monitoring & Analytics

### 1. Payment Statistics
```python
# Get payment statistics
GET /api/v1/payments/transactions/stats/

Response:
{
  "total_transactions": 150,
  "total_amount": 2500000,
  "successful_payments": 120,
  "failed_payments": 20,
  "pending_payments": 10,
  "currency": "UGX"
}
```

### 2. Transaction Tracking
- All transactions stored in database
- Complete audit trail
- Payment status tracking
- Refund history

### 3. Admin Interface
- Django admin for payment management
- Transaction monitoring
- Payment method configuration
- Refund processing

## 🔒 Security Features

### 1. Webhook Verification
```python
def _verify_webhook_signature(self, webhook_data, signature):
    # Verify HMAC signature
    expected_signature = hmac.new(
        self.secret_hash.encode(),
        json.dumps(webhook_data, separators=(',', ':')).encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

### 2. Payload Encryption
```python
def _encrypt_payload(self, payload):
    # AES encryption for sensitive data
    if self.encryption_key:
        cipher = AES.new(self.encryption_key, AES.MODE_CBC)
        encrypted = cipher.encrypt(pad(json.dumps(payload).encode(), 16))
        return base64.b64encode(encrypted).decode()
    return payload
```

### 3. Transaction Validation
- Amount validation
- Currency validation
- Customer data validation
- Payment method validation

## 🛠️ Troubleshooting

### Common Issues

#### 1. Payment Not Processing
- Check Flutterwave dashboard for transaction status
- Verify webhook URL configuration
- Check server logs for errors

#### 2. Webhook Not Receiving
- Ensure SSL certificate is valid
- Verify webhook URL is accessible
- Check firewall settings

#### 3. Payment Verification Failing
- Verify secret key configuration
- Check transaction reference format
- Ensure proper error handling

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger('payments').setLevel(logging.DEBUG)
```

## 📈 Performance Optimization

### 1. Database Indexing
```python
class PaymentTransaction(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['customer', 'status']),
        ]
```

### 2. Caching
```python
# Cache payment methods
from django.core.cache import cache

def get_payment_methods(country='UG'):
    cache_key = f'payment_methods_{country}'
    methods = cache.get(cache_key)
    if not methods:
        methods = PaymentMethod.objects.filter(country_code=country, is_active=True)
        cache.set(cache_key, methods, 3600)  # 1 hour
    return methods
```

### 3. Async Processing
```python
# Use Celery for background tasks
from celery import shared_task

@shared_task
def process_payment_webhook(webhook_data):
    # Process webhook asynchronously
    pass
```

## 🔄 Integration Points

### 1. Orders
- Payment buttons in order table
- Automatic order status updates
- Payment tracking per order

### 2. Invoices
- Invoice payment processing
- Payment status tracking
- Automatic invoice updates

### 3. Events
- Event ticket payments
- Payment confirmation
- Attendee tracking

### 4. Order Receipts
- Receipt payment processing
- Delivery confirmation
- Digital signature integration

## 📝 API Examples

### Create Payment
```bash
curl -X POST http://localhost:8000/api/v1/payments/transactions/initiate_payment/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "transaction_type": "order",
    "amount": 25000,
    "currency": "UGX",
    "order_id": 123,
    "description": "Payment for order #123"
  }'
```

### Verify Payment
```bash
curl -X POST http://localhost:8000/api/v1/payments/transactions/123/verify_payment/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Payment Statistics
```bash
curl -X GET http://localhost:8000/api/v1/payments/transactions/stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎯 Conclusion

The Flutterwave payment integration is complete and ready for production use. The system provides:

✅ **Complete Payment Processing**
✅ **Multiple Payment Methods**
✅ **Webhook Integration**
✅ **Security Features**
✅ **Admin Interface**
✅ **Frontend Integration**
✅ **Testing Tools**
✅ **Documentation**

The integration supports all major payment methods for Uganda and provides a robust, scalable payment solution for the BottlePlug Dashboard. 