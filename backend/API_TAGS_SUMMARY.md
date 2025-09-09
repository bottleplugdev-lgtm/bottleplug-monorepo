# API Tags Summary - BottlePlug Backend

## Overview
This document provides a summary of the organized API endpoints with their respective tags for the BottlePlug backend. The tags help organize the Swagger documentation into logical groups.

## Implemented Tags

### 1. Authentication & User Management (`auth`)
**Description**: Authentication and user management operations including user registration, login, profile management, and driver management.

**Endpoints**:
- User management (CRUD operations)
- Driver management (CRUD operations)
- User sessions (read-only)
- User location management
- Wallet operations
- Firebase authentication

**Status**: ✅ Partially implemented with swagger tags

### 2. Products (`products`)
**Description**: Product catalog management including categories, products, variants, and product information.

**Endpoints**:
- Category management (CRUD operations)
- Product management (CRUD operations)
- Product variants (CRUD operations)
- Product search and filtering
- Featured products, new arrivals, on-sale products

**Status**: ✅ Partially implemented with swagger tags

### 3. Stock (`stock`)
**Description**: Inventory and stock management including stock levels, inventory logs, and stock updates.

**Endpoints**:
- Inventory logs (read-only)
- Product measurements (CRUD operations)
- Stock level updates
- Low stock monitoring

**Status**: ✅ Partially implemented with swagger tags

### 4. Orders (`orders`)
**Description**: Order management, shopping cart, wishlist, and product reviews.

**Endpoints**:
- Order management (CRUD operations)
- Shopping cart operations
- Wishlist management
- Product reviews (CRUD operations)
- Order statistics

**Status**: ⏳ Not yet implemented with swagger tags

### 5. Events (`events`)
**Description**: Event management and RSVP functionality.

**Endpoints**:
- Event management (CRUD operations)
- RSVP management (CRUD operations)

**Status**: ⏳ Not yet implemented with swagger tags

### 6. Newsletter (`newsletter`)
**Description**: Newsletter subscription management and email marketing campaigns.

**Endpoints**:
- Newsletter subscriptions (CRUD operations)
- Newsletter campaigns (CRUD operations)
- Email newsletter (legacy endpoints)

**Status**: ⏳ Not yet implemented with swagger tags

### 7. Deliveries (`deliveries`)
**Description**: Delivery management, driver locations, delivery zones, schedules, and ratings.

**Endpoints**:
- Delivery requests (CRUD operations)
- Driver location tracking
- Delivery zones management
- Driver schedules
- Delivery ratings

**Status**: ⏳ Not yet implemented with swagger tags

### 8. Analytics (`analytics`)
**Description**: Analytics and metrics collection including user metrics, product metrics, order metrics, delivery metrics, revenue metrics, and search analytics.

**Endpoints**:
- Analytics events
- User metrics
- Product metrics
- Order metrics
- Delivery metrics
- Revenue metrics
- Search analytics
- Dashboard data

**Status**: ⏳ Not yet implemented with swagger tags

## Implementation Status

| Module | Status | Notes |
|--------|--------|-------|
| `users` | ✅ Partial | Auth tags implemented |
| `products` | ✅ Partial | Products and Stock tags implemented |
| `orders` | ⏳ Pending | Needs tag implementation |
| `events` | ⏳ Pending | Needs tag implementation |
| `newsletter` | ⏳ Pending | Needs tag implementation |
| `deliveries` | ⏳ Pending | Needs tag implementation |
| `analytics` | ⏳ Pending | Needs tag implementation |

## Next Steps

### 1. Complete Tag Implementation
For each remaining module, add the following to the ViewSets:

```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class YourViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    @swagger_auto_schema(tags=['your_tag'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['your_tag'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    # ... repeat for other methods ...
    
    @swagger_auto_schema(
        tags=['your_tag'],
        operation_description="Description of custom action"
    )
    @action(detail=False, methods=['get'])
    def custom_action(self, request):
        # ... action implementation ...
```

### 2. Tag Mapping
Use the tag mapping from `tanna_backend/api_tags.py`:

```python
TAG_MAPPING = {
    'users': AUTH_TAG,
    'products': PRODUCTS_TAG,
    'orders': ORDERS_TAG,
    'deliveries': DELIVERIES_TAG,
    'analytics': ANALYTICS_TAG,
    'event_management': EVENTS_TAG,
    'events': EVENTS_TAG,
    'email_newsletter': NEWSLETTER_TAG,
    'newsletter': NEWSLETTER_TAG,
}
```

### 3. API Documentation Structure
The organized structure will provide:

- **Logical Grouping**: Endpoints grouped by functionality
- **Better Navigation**: Easy to find related endpoints
- **Clear Documentation**: Each tag has a description
- **Improved Developer Experience**: Better API exploration

### 4. Testing the Implementation
After implementing tags, test the Swagger documentation:

1. Start the development server
2. Navigate to `/swagger/`
3. Verify that endpoints are properly grouped by tags
4. Check that tag descriptions are displayed correctly

## Benefits of Tag Organization

1. **Improved Developer Experience**: Developers can easily find related endpoints
2. **Better Documentation**: Clear separation of concerns
3. **Easier Maintenance**: Related functionality is grouped together
4. **API Versioning**: Tags can help with API versioning strategies
5. **Client Generation**: Better code generation for API clients

## Total Endpoint Count by Tag

| Tag | Estimated Endpoints | Status |
|-----|-------------------|--------|
| `auth` | ~25 | ✅ Implemented |
| `products` | ~20 | ✅ Implemented |
| `stock` | ~15 | ✅ Implemented |
| `orders` | ~25 | ⏳ Pending |
| `events` | ~12 | ⏳ Pending |
| `newsletter` | ~15 | ⏳ Pending |
| `deliveries` | ~30 | ⏳ Pending |
| `analytics` | ~40 | ⏳ Pending |

**Total**: ~182 endpoints across 8 main categories 