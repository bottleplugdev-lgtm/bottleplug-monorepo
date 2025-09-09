# API Endpoints Organization by Tags

This document organizes all API endpoints in the BottlePlug backend into their respective tags for better API documentation and organization.

## API Base URL
- **Base URL**: `/api/v1/`
- **Alternative Auth URL**: `/auth/` (direct access without api/v1 prefix)

## 1. Authentication & User Management (`auth`)

### User Management
- `GET /api/v1/auth/users/` - List all users
- `POST /api/v1/auth/users/` - Create new user
- `GET /api/v1/auth/users/{id}/` - Get user details
- `PUT /api/v1/auth/users/{id}/` - Update user
- `PATCH /api/v1/auth/users/{id}/` - Partial update user
- `DELETE /api/v1/auth/users/{id}/` - Delete user
- `POST /api/v1/auth/users/verify_firebase_token/` - Verify Firebase token

### Driver Management
- `GET /api/v1/auth/drivers/` - List all drivers
- `POST /api/v1/auth/drivers/` - Create new driver
- `GET /api/v1/auth/drivers/{id}/` - Get driver details
- `PUT /api/v1/auth/drivers/{id}/` - Update driver
- `PATCH /api/v1/auth/drivers/{id}/` - Partial update driver
- `DELETE /api/v1/auth/drivers/{id}/` - Delete driver

### User Sessions
- `GET /api/v1/auth/sessions/` - List user sessions
- `POST /api/v1/auth/sessions/` - Create session
- `GET /api/v1/auth/sessions/{id}/` - Get session details
- `PUT /api/v1/auth/sessions/{id}/` - Update session
- `PATCH /api/v1/auth/sessions/{id}/` - Partial update session
- `DELETE /api/v1/auth/sessions/{id}/` - Delete session

### User Features
- `GET /api/v1/auth/location/` - Get user location
- `POST /api/v1/auth/location/` - Update user location
- `GET /api/v1/auth/wallet/` - Get user wallet
- `POST /api/v1/auth/wallet/` - Update wallet
- `POST /api/v1/auth/firebase-auth/` - Firebase authentication

## 2. Products (`products`)

### Categories
- `GET /api/v1/products/categories/` - List all categories
- `POST /api/v1/products/categories/` - Create new category
- `GET /api/v1/products/categories/{id}/` - Get category details
- `PUT /api/v1/products/categories/{id}/` - Update category
- `PATCH /api/v1/products/categories/{id}/` - Partial update category
- `DELETE /api/v1/products/categories/{id}/` - Delete category
- `DELETE /api/v1/products/categories/bulk_delete/` - Bulk delete categories

### Products
- `GET /api/v1/products/products/` - List all products
- `POST /api/v1/products/products/` - Create new product
- `GET /api/v1/products/products/{id}/` - Get product details
- `PUT /api/v1/products/products/{id}/` - Update product
- `PATCH /api/v1/products/products/{id}/` - Partial update product
- `DELETE /api/v1/products/products/{id}/` - Delete product
- `GET /api/v1/products/products/search/` - Search products
- `GET /api/v1/products/products/featured/` - Get featured products
- `GET /api/v1/products/products/new_arrivals/` - Get new arrivals
- `GET /api/v1/products/products/on_sale/` - Get products on sale
- `DELETE /api/v1/products/products/bulk_delete/` - Bulk delete products

### Product Variants
- `GET /api/v1/products/variants/` - List all variants
- `POST /api/v1/products/variants/` - Create new variant
- `GET /api/v1/products/variants/{id}/` - Get variant details
- `PUT /api/v1/products/variants/{id}/` - Update variant
- `PATCH /api/v1/products/variants/{id}/` - Partial update variant
- `DELETE /api/v1/products/variants/{id}/` - Delete variant

## 3. Stock (`stock`)

### Inventory Management
- `GET /api/v1/products/inventory-logs/` - List inventory logs
- `POST /api/v1/products/inventory-logs/` - Create inventory log
- `GET /api/v1/products/inventory-logs/{id}/` - Get inventory log details
- `PUT /api/v1/products/inventory-logs/{id}/` - Update inventory log
- `PATCH /api/v1/products/inventory-logs/{id}/` - Partial update inventory log
- `DELETE /api/v1/products/inventory-logs/{id}/` - Delete inventory log

### Product Measurements
- `GET /api/v1/products/measurements/` - List product measurements
- `POST /api/v1/products/measurements/` - Create measurement
- `GET /api/v1/products/measurements/{id}/` - Get measurement details
- `PUT /api/v1/products/measurements/{id}/` - Update measurement
- `PATCH /api/v1/products/measurements/{id}/` - Partial update measurement
- `DELETE /api/v1/products/measurements/{id}/` - Delete measurement

### Stock Operations
- `POST /api/v1/products/products/{id}/update_stock/` - Update product stock levels
- `GET /api/v1/products/products/low_stock/` - Get products with low stock
- `POST /api/v1/products/measurements/{id}/update_stock/` - Update measurement stock

## 4. Orders (`orders`)

### Order Management
- `GET /api/v1/orders/orders/` - List all orders
- `POST /api/v1/orders/orders/` - Create new order
- `GET /api/v1/orders/orders/{id}/` - Get order details
- `PUT /api/v1/orders/orders/{id}/` - Update order
- `PATCH /api/v1/orders/orders/{id}/` - Partial update order
- `DELETE /api/v1/orders/orders/{id}/` - Delete order
- `GET /api/v1/orders/orders/my_orders/` - Get current user's orders
- `GET /api/v1/orders/orders/order_stats/` - Get order statistics

### Shopping Cart
- `GET /api/v1/orders/cart/` - Get user's cart
- `POST /api/v1/orders/cart/` - Add item to cart
- `GET /api/v1/orders/cart/{id}/` - Get cart item details
- `PUT /api/v1/orders/cart/{id}/` - Update cart item
- `PATCH /api/v1/orders/cart/{id}/` - Partial update cart item
- `DELETE /api/v1/orders/cart/{id}/` - Remove item from cart
- `POST /api/v1/orders/cart/clear/` - Clear cart
- `POST /api/v1/orders/cart/checkout/` - Checkout cart

### Wishlist
- `GET /api/v1/orders/wishlist/` - Get user's wishlist
- `POST /api/v1/orders/wishlist/` - Add item to wishlist
- `GET /api/v1/orders/wishlist/{id}/` - Get wishlist item details
- `PUT /api/v1/orders/wishlist/{id}/` - Update wishlist item
- `PATCH /api/v1/orders/wishlist/{id}/` - Partial update wishlist item
- `DELETE /api/v1/orders/wishlist/{id}/` - Remove item from wishlist

### Reviews
- `GET /api/v1/orders/reviews/` - List all reviews
- `POST /api/v1/orders/reviews/` - Create new review
- `GET /api/v1/orders/reviews/{id}/` - Get review details
- `PUT /api/v1/orders/reviews/{id}/` - Update review
- `PATCH /api/v1/orders/reviews/{id}/` - Partial update review
- `DELETE /api/v1/orders/reviews/{id}/` - Delete review

## 5. Events (`events`)

### Event Management
- `GET /api/v1/events/events/` - List all events
- `POST /api/v1/events/events/` - Create new event
- `GET /api/v1/events/events/{id}/` - Get event details
- `PUT /api/v1/events/events/{id}/` - Update event
- `PATCH /api/v1/events/events/{id}/` - Partial update event
- `DELETE /api/v1/events/events/{id}/` - Delete event

### RSVPs
- `GET /api/v1/events/rsvps/` - List all RSVPs
- `POST /api/v1/events/rsvps/` - Create RSVP
- `GET /api/v1/events/rsvps/{id}/` - Get RSVP details
- `PUT /api/v1/events/rsvps/{id}/` - Update RSVP
- `PATCH /api/v1/events/rsvps/{id}/` - Partial update RSVP
- `DELETE /api/v1/events/rsvps/{id}/` - Delete RSVP

## 6. Newsletter (`newsletter`)

### Newsletter Subscriptions
- `GET /api/v1/newsletter/subscriptions/` - List subscriptions
- `POST /api/v1/newsletter/subscriptions/` - Create subscription
- `GET /api/v1/newsletter/subscriptions/{id}/` - Get subscription details
- `PUT /api/v1/newsletter/subscriptions/{id}/` - Update subscription
- `PATCH /api/v1/newsletter/subscriptions/{id}/` - Partial update subscription
- `DELETE /api/v1/newsletter/subscriptions/{id}/` - Delete subscription

### Newsletter Campaigns
- `GET /api/v1/newsletter/campaigns/` - List campaigns
- `POST /api/v1/newsletter/campaigns/` - Create campaign
- `GET /api/v1/newsletter/campaigns/{id}/` - Get campaign details
- `PUT /api/v1/newsletter/campaigns/{id}/` - Update campaign
- `PATCH /api/v1/newsletter/campaigns/{id}/` - Partial update campaign
- `DELETE /api/v1/newsletter/campaigns/{id}/` - Delete campaign

### Email Newsletter (Legacy)
- `POST /api/v1/newsletter/subscribe/` - Subscribe to newsletter
- `POST /api/v1/newsletter/unsubscribe/` - Unsubscribe from newsletter

## 7. Deliveries (`deliveries`)

### Delivery Requests
- `GET /api/v1/deliveries/deliveries/` - List all delivery requests
- `POST /api/v1/deliveries/deliveries/` - Create delivery request
- `GET /api/v1/deliveries/deliveries/{id}/` - Get delivery details
- `PUT /api/v1/deliveries/deliveries/{id}/` - Update delivery
- `PATCH /api/v1/deliveries/deliveries/{id}/` - Partial update delivery
- `DELETE /api/v1/deliveries/deliveries/{id}/` - Delete delivery
- `GET /api/v1/deliveries/deliveries/my_deliveries/` - Get user's deliveries
- `POST /api/v1/deliveries/deliveries/{id}/accept/` - Accept delivery (driver)
- `POST /api/v1/deliveries/deliveries/{id}/complete/` - Complete delivery
- `POST /api/v1/deliveries/deliveries/{id}/cancel/` - Cancel delivery

### Driver Locations
- `GET /api/v1/deliveries/driver-locations/` - List driver locations
- `POST /api/v1/deliveries/driver-locations/` - Update driver location
- `GET /api/v1/deliveries/driver-locations/{id}/` - Get driver location
- `PUT /api/v1/deliveries/driver-locations/{id}/` - Update driver location
- `PATCH /api/v1/deliveries/driver-locations/{id}/` - Partial update driver location
- `DELETE /api/v1/deliveries/driver-locations/{id}/` - Delete driver location

### Delivery Zones
- `GET /api/v1/deliveries/delivery-zones/` - List delivery zones
- `POST /api/v1/deliveries/delivery-zones/` - Create delivery zone
- `GET /api/v1/deliveries/delivery-zones/{id}/` - Get zone details
- `PUT /api/v1/deliveries/delivery-zones/{id}/` - Update zone
- `PATCH /api/v1/deliveries/delivery-zones/{id}/` - Partial update zone
- `DELETE /api/v1/deliveries/delivery-zones/{id}/` - Delete zone

### Driver Schedules
- `GET /api/v1/deliveries/driver-schedules/` - List driver schedules
- `POST /api/v1/deliveries/driver-schedules/` - Create schedule
- `GET /api/v1/deliveries/driver-schedules/{id}/` - Get schedule details
- `PUT /api/v1/deliveries/driver-schedules/{id}/` - Update schedule
- `PATCH /api/v1/deliveries/driver-schedules/{id}/` - Partial update schedule
- `DELETE /api/v1/deliveries/driver-schedules/{id}/` - Delete schedule

### Delivery Ratings
- `GET /api/v1/deliveries/delivery-ratings/` - List delivery ratings
- `POST /api/v1/deliveries/delivery-ratings/` - Create rating
- `GET /api/v1/deliveries/delivery-ratings/{id}/` - Get rating details
- `PUT /api/v1/deliveries/delivery-ratings/{id}/` - Update rating
- `PATCH /api/v1/deliveries/delivery-ratings/{id}/` - Partial update rating
- `DELETE /api/v1/deliveries/delivery-ratings/{id}/` - Delete rating

## 8. Analytics (`analytics`)

### Analytics Events
- `GET /api/v1/analytics/events/` - List analytics events
- `POST /api/v1/analytics/events/` - Create analytics event
- `GET /api/v1/analytics/events/{id}/` - Get event details
- `PUT /api/v1/analytics/events/{id}/` - Update event
- `PATCH /api/v1/analytics/events/{id}/` - Partial update event
- `DELETE /api/v1/analytics/events/{id}/` - Delete event

### User Metrics
- `GET /api/v1/analytics/user-metrics/` - List user metrics
- `POST /api/v1/analytics/user-metrics/` - Create user metric
- `GET /api/v1/analytics/user-metrics/{id}/` - Get metric details
- `PUT /api/v1/analytics/user-metrics/{id}/` - Update metric
- `PATCH /api/v1/analytics/user-metrics/{id}/` - Partial update metric
- `DELETE /api/v1/analytics/user-metrics/{id}/` - Delete metric

### Product Metrics
- `GET /api/v1/analytics/product-metrics/` - List product metrics
- `POST /api/v1/analytics/product-metrics/` - Create product metric
- `GET /api/v1/analytics/product-metrics/{id}/` - Get metric details
- `PUT /api/v1/analytics/product-metrics/{id}/` - Update metric
- `PATCH /api/v1/analytics/product-metrics/{id}/` - Partial update metric
- `DELETE /api/v1/analytics/product-metrics/{id}/` - Delete metric

### Order Metrics
- `GET /api/v1/analytics/order-metrics/` - List order metrics
- `POST /api/v1/analytics/order-metrics/` - Create order metric
- `GET /api/v1/analytics/order-metrics/{id}/` - Get metric details
- `PUT /api/v1/analytics/order-metrics/{id}/` - Update metric
- `PATCH /api/v1/analytics/order-metrics/{id}/` - Partial update metric
- `DELETE /api/v1/analytics/order-metrics/{id}/` - Delete metric

### Delivery Metrics
- `GET /api/v1/analytics/delivery-metrics/` - List delivery metrics
- `POST /api/v1/analytics/delivery-metrics/` - Create delivery metric
- `GET /api/v1/analytics/delivery-metrics/{id}/` - Get metric details
- `PUT /api/v1/analytics/delivery-metrics/{id}/` - Update metric
- `PATCH /api/v1/analytics/delivery-metrics/{id}/` - Partial update metric
- `DELETE /api/v1/analytics/delivery-metrics/{id}/` - Delete metric

### Revenue Metrics
- `GET /api/v1/analytics/revenue-metrics/` - List revenue metrics
- `POST /api/v1/analytics/revenue-metrics/` - Create revenue metric
- `GET /api/v1/analytics/revenue-metrics/{id}/` - Get metric details
- `PUT /api/v1/analytics/revenue-metrics/{id}/` - Update metric
- `PATCH /api/v1/analytics/revenue-metrics/{id}/` - Partial update metric
- `DELETE /api/v1/analytics/revenue-metrics/{id}/` - Delete metric

### Search Analytics
- `GET /api/v1/analytics/search-analytics/` - List search analytics
- `POST /api/v1/analytics/search-analytics/` - Create search analytics
- `GET /api/v1/analytics/search-analytics/{id}/` - Get analytics details
- `PUT /api/v1/analytics/search-analytics/{id}/` - Update analytics
- `PATCH /api/v1/analytics/search-analytics/{id}/` - Partial update analytics
- `DELETE /api/v1/analytics/search-analytics/{id}/` - Delete analytics

### Dashboard
- `GET /api/v1/analytics/dashboard/` - Get dashboard data
- `POST /api/v1/analytics/dashboard/` - Create dashboard entry
- `GET /api/v1/analytics/dashboard/{id}/` - Get dashboard entry details
- `PUT /api/v1/analytics/dashboard/{id}/` - Update dashboard entry
- `PATCH /api/v1/analytics/dashboard/{id}/` - Partial update dashboard entry
- `DELETE /api/v1/analytics/dashboard/{id}/` - Delete dashboard entry

## Tag Summary

| Tag | Description | Endpoint Count |
|-----|-------------|----------------|
| `auth` | Authentication & User Management | ~25 endpoints |
| `products` | Product Catalog Management | ~20 endpoints |
| `stock` | Inventory & Stock Management | ~15 endpoints |
| `orders` | Order Management & Shopping | ~25 endpoints |
| `events` | Event Management | ~12 endpoints |
| `newsletter` | Newsletter & Email Marketing | ~15 endpoints |
| `deliveries` | Delivery & Driver Management | ~30 endpoints |
| `analytics` | Analytics & Metrics | ~40 endpoints |

**Total Endpoints**: ~182 endpoints across 8 main categories