import { analytics } from '@/firebase/config'
import { logEvent } from 'firebase/analytics'

// Analytics service for tracking user interactions and business metrics
export const AnalyticsService = {
  // User authentication events
  trackLogin: (method) => {
    logEvent(analytics, 'login', {
      method: method // 'email', 'google'
    })
  },

  trackSignUp: (method) => {
    logEvent(analytics, 'sign_up', {
      method: method
    })
  },

  trackLogout: () => {
    logEvent(analytics, 'logout')
  },

  // Dashboard navigation
  trackPageView: (pageName) => {
    logEvent(analytics, 'page_view', {
      page_name: pageName
    })
  },

  // Product management
  trackProductCreated: (productName, category) => {
    logEvent(analytics, 'product_created', {
      product_name: productName,
      category: category
    })
  },

  trackProductEdited: (productName) => {
    logEvent(analytics, 'product_edited', {
      product_name: productName
    })
  },

  trackProductDeleted: (productName) => {
    logEvent(analytics, 'product_deleted', {
      product_name: productName
    })
  },

  // Order management
  trackOrderCreated: (orderValue, itemCount) => {
    logEvent(analytics, 'order_created', {
      value: orderValue,
      currency: 'USD',
      items: itemCount
    })
  },

  trackOrderStatusChanged: (orderId, newStatus) => {
    logEvent(analytics, 'order_status_changed', {
      order_id: orderId,
      status: newStatus
    })
  },

  // Customer management
  trackCustomerAdded: (customerType) => {
    logEvent(analytics, 'customer_added', {
      customer_type: customerType // 'retail', 'wholesale'
    })
  },

  // Stock management
  trackStockIn: (productName, quantity) => {
    logEvent(analytics, 'stock_in', {
      product_name: productName,
      quantity: quantity
    })
  },

  trackStockOut: (productName, quantity) => {
    logEvent(analytics, 'stock_out', {
      product_name: productName,
      quantity: quantity
    })
  },

  // Financial tracking
  trackRevenueAdded: (amount, source) => {
    logEvent(analytics, 'revenue_added', {
      value: amount,
      currency: 'USD',
      source: source
    })
  },

  trackExpenseAdded: (amount, category) => {
    logEvent(analytics, 'expense_added', {
      value: amount,
      currency: 'USD',
      category: category
    })
  },

  // Search and filtering
  trackSearch: (searchTerm, page) => {
    logEvent(analytics, 'search', {
      search_term: searchTerm,
      page: page
    })
  },

  trackFilterApplied: (filterType, filterValue) => {
    logEvent(analytics, 'filter_applied', {
      filter_type: filterType,
      filter_value: filterValue
    })
  },

  // Error tracking
  trackError: (errorType, errorMessage) => {
    logEvent(analytics, 'error', {
      error_type: errorType,
      error_message: errorMessage
    })
  },

  // Feature usage
  trackFeatureUsed: (featureName) => {
    logEvent(analytics, 'feature_used', {
      feature_name: featureName
    })
  },

  // Event management
  trackEventCreated: (eventName, eventType, maxAttendees) => {
    logEvent(analytics, 'event_created', {
      event_name: eventName,
      event_type: eventType,
      max_attendees: maxAttendees
    })
  },

  trackEventEdited: (eventName, eventType) => {
    logEvent(analytics, 'event_edited', {
      event_name: eventName,
      event_type: eventType
    })
  },

  trackEventCancelled: (eventName, eventType) => {
    logEvent(analytics, 'event_cancelled', {
      event_name: eventName,
      event_type: eventType
    })
  },

  trackAttendeeRegistered: (eventName, attendeeType) => {
    logEvent(analytics, 'attendee_registered', {
      event_name: eventName,
      attendee_type: attendeeType // 'customer', 'guest', 'vip'
    })
  },

  trackEventCompleted: (eventName, eventType, attendeeCount) => {
    logEvent(analytics, 'event_completed', {
      event_name: eventName,
      event_type: eventType,
      attendee_count: attendeeCount
    })
  }
}

export default AnalyticsService 