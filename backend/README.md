# Tanna Backend - Django REST API

A comprehensive Django REST API backend for the Tanna alcohol and beverage management system, supporting multiple frontend applications including Vue.js dashboards, Flutter mobile apps, and delivery services.

## Features

- **Multi-Platform Support**: Unified backend for Vue.js dashboards, Flutter mobile apps, and delivery services
- **Firebase Authentication**: Secure authentication using Firebase tokens
- **Comprehensive Data Models**: Users, Products, Orders, Deliveries, Analytics
- **RESTful API**: Full CRUD operations with Django REST Framework
- **PostgreSQL Database**: Robust relational database for production use
- **Analytics & Reporting**: Built-in analytics and metrics tracking
- **CORS Support**: Cross-origin resource sharing for frontend integration

## Project Structure

```
tanna_backend/
├── tanna_backend/          # Main Django project
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── users/                 # User management app
├── products/              # Product management app
├── orders/                # Order management app
├── deliveries/            # Delivery management app
├── analytics/             # Analytics and metrics app
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
└── README.md             # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Firebase project with authentication enabled

### 1. Clone and Install Dependencies

```bash
cd /Users/mc/tanna/backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=tanna_backend
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Firebase Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=path/to/serviceAccountKey.json
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb tanna_backend

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Firebase Service Account

Download your Firebase service account key from the Firebase Console:
1. Go to Project Settings > Service Accounts
2. Click "Generate new private key"
3. Save the JSON file and update the path in your `.env` file

### 5. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`

## API Endpoints

### Authentication
- `POST /api/v1/auth/firebase/` - Firebase token authentication

### Users
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/me/` - Get current user profile
- `PUT /api/v1/users/me/` - Update current user profile
- `GET /api/v1/users/drivers/` - List drivers
- `GET /api/v1/users/drivers/nearby/` - Find nearby drivers

### Products
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/search/` - Search products
- `GET /api/v1/products/featured/` - Get featured products
- `GET /api/v1/products/new/` - Get new products
- `GET /api/v1/products/sale/` - Get products on sale

### Orders
- `GET /api/v1/orders/` - List orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/my_orders/` - Get user's orders
- `POST /api/v1/orders/{id}/cancel/` - Cancel order

### Cart & Wishlist
- `GET /api/v1/cart/my_cart/` - Get user's cart
- `POST /api/v1/cart/add_item/` - Add item to cart
- `PUT /api/v1/cart/update_item/` - Update cart item
- `DELETE /api/v1/cart/remove_item/` - Remove cart item
- `POST /api/v1/cart/checkout/` - Checkout cart

### Deliveries
- `GET /api/v1/deliveries/` - List delivery requests
- `POST /api/v1/deliveries/` - Create delivery request
- `GET /api/v1/deliveries/my_deliveries/` - Get user's deliveries
- `POST /api/v1/deliveries/{id}/accept/` - Accept delivery (driver)

### Analytics
- `GET /api/v1/analytics/dashboard/stats/` - Dashboard statistics
- `GET /api/v1/analytics/dashboard/charts/` - Chart data
- `GET /api/v1/analytics/events/` - Analytics events
- `POST /api/v1/analytics/events/track_event/` - Track event

## Frontend Integration

### Firebase Authentication Flow

1. **Sign In**: Use Firebase Auth in your frontend applications
2. **Get Token**: After successful authentication, get the Firebase ID token
3. **API Calls**: Include the token in the Authorization header:
   ```
   Authorization: Bearer <firebase_id_token>
   ```

### Example API Call

```javascript
// Vue.js/JavaScript
const response = await fetch('http://localhost:8000/api/v1/users/me/', {
  headers: {
    'Authorization': `Bearer ${firebaseIdToken}`,
    'Content-Type': 'application/json'
  }
});

// Flutter/Dart
final response = await http.get(
  Uri.parse('http://localhost:8000/api/v1/users/me/'),
  headers: {
    'Authorization': 'Bearer $firebaseIdToken',
    'Content-Type': 'application/json',
  },
);
```

## Data Models

### User Types
- **Customer**: Regular users who can place orders
- **Driver**: Delivery personnel with location tracking
- **Admin**: System administrators with full access

### Product Features
- Categories and subcategories
- Variants (size, color, etc.)
- Bulk pricing
- Inventory tracking
- Reviews and ratings

### Order Management
- Cart and wishlist functionality
- Order status tracking
- Payment processing
- Delivery assignment

### Delivery System
- Real-time driver location
- Delivery zones and fees
- Driver schedules
- Delivery ratings

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations <app_name>
python manage.py migrate
```

### Admin Interface
Access the Django admin at `http://localhost:8000/admin/` to manage data.

## Production Deployment

### Environment Variables
Set `DEBUG=False` and configure production database settings.

### Static Files
```bash
python manage.py collectstatic
```

### Database
Use a production PostgreSQL instance with proper backups.

### Security
- Use HTTPS in production
- Configure proper CORS settings
- Set secure `SECRET_KEY`
- Enable Firebase App Check

## Support

For issues and questions:
1. Check the Django logs
2. Verify Firebase configuration
3. Ensure database connectivity
4. Check CORS settings for frontend integration

## License

This project is part of the Tanna alcohol and beverage management system. 