import { toast } from 'vue3-toastify'

class ErrorHandler {
  constructor() {
    this.errorMessages = {
      // Network errors
      'Network Error': 'Unable to connect to the server. Please check your internet connection and try again.',
      'Failed to fetch': 'Unable to connect to the server. Please check your internet connection and try again.',
      'Request timeout': 'The request took too long. Please try again.',
      
      // HTTP status codes
      400: 'Please check your input and try again.',
      401: 'Your session has expired. Please log in again.',
      403: 'You don\'t have permission to perform this action.',
      404: 'The requested information could not be found.',
      409: 'This resource already exists.',
      422: 'Please check your input and try again.',
      429: 'Too many requests. Please wait a moment and try again.',
      500: 'Our servers are experiencing issues. Please try again later.',
      502: 'Our servers are experiencing issues. Please try again later.',
      503: 'Our servers are temporarily unavailable. Please try again later.',
      504: 'The request took too long. Please try again.',
      
      // Authentication errors
      'auth/user-not-found': 'No account found with this email address.',
      'auth/wrong-password': 'Incorrect password. Please try again.',
      'auth/email-already-in-use': 'An account with this email already exists.',
      'auth/weak-password': 'Password is too weak. Please choose a stronger password.',
      'auth/invalid-email': 'Please enter a valid email address.',
      'auth/user-disabled': 'This account has been disabled.',
      'auth/too-many-requests': 'Too many failed attempts. Please try again later.',
      'auth/network-request-failed': 'Network error. Please check your connection.',
      
      // Business logic errors
      'event_full': 'This event is full.',
      'event_cancelled': 'This event has been cancelled.',
      'event_ended': 'This event has already ended.',
      'already_rsvpd': 'You have already RSVP\'d for this event.',
      'product_out_of_stock': 'This product is out of stock.',
      'cart_empty': 'Your cart is empty.',
      'invalid_promo_code': 'Invalid promo code.',
      'payment_failed': 'Payment failed. Please try again.',
      'order_not_found': 'Order not found.',
      'delivery_not_found': 'Delivery not found.',
      'user_not_found': 'User not found.',
      'profile_update_failed': 'Failed to update profile.',
      'password_mismatch': 'Passwords do not match.',
      'current_password_incorrect': 'Current password is incorrect.',
      'email_already_exists': 'An account with this email already exists.',
      'phone_already_exists': 'An account with this phone number already exists.',
      'invalid_phone': 'Please enter a valid phone number.',
      'invalid_address': 'Please enter a valid address.',
      'invalid_zip_code': 'Please enter a valid ZIP code.',
      'invalid_card_number': 'Please enter a valid card number.',
      'invalid_expiry_date': 'Please enter a valid expiry date.',
      'invalid_cvv': 'Please enter a valid CVV.',
      'card_declined': 'Card was declined. Please try a different card.',
      'insufficient_funds': 'Insufficient funds. Please try a different payment method.',
      'expired_card': 'Card has expired. Please use a different card.',
      'invalid_coupon': 'Invalid coupon code.',
      'coupon_expired': 'Coupon has expired.',
      'coupon_already_used': 'Coupon has already been used.',
      'minimum_order_not_met': 'Order does not meet minimum requirements.',
      'delivery_not_available': 'Delivery is not available for this location.',
      'pickup_not_available': 'Pickup is not available at this time.',
      'store_closed': 'Store is currently closed.',
      'maintenance_mode': 'System is under maintenance. Please try again later.',
      'feature_not_available': 'This feature is not available.',
      'file_too_large': 'File is too large. Please choose a smaller file.',
      'invalid_file_type': 'Invalid file type. Please choose a different file.',
      'upload_failed': 'File upload failed. Please try again.',
      'delete_failed': 'Failed to delete item. Please try again.',
      'save_failed': 'Failed to save changes. Please try again.',
      'load_failed': 'Failed to load data. Please try again.',
      'search_failed': 'Search failed. Please try again.',
      'filter_failed': 'Failed to apply filters. Please try again.',
      'sort_failed': 'Failed to sort results. Please try again.',
      'export_failed': 'Failed to export data. Please try again.',
      'import_failed': 'Failed to import data. Please try again.',
      'sync_failed': 'Failed to sync data. Please try again.',
      'backup_failed': 'Failed to create backup. Please try again.',
      'restore_failed': 'Failed to restore data. Please try again.',
      'update_failed': 'Failed to update. Please try again.',
      'create_failed': 'Failed to create. Please try again.',
      'delete_confirmation_required': 'Please confirm deletion.',
      'unsaved_changes': 'You have unsaved changes. Please save or discard them.',
      'session_expired': 'Your session has expired. Please log in again.',
      'permission_denied': 'You don\'t have permission to perform this action.',
      'validation_failed': 'Please check your input and try again.',
      'rate_limit_exceeded': 'Too many requests. Please wait a moment and try again.',
      'service_unavailable': 'Service is temporarily unavailable. Please try again later.',
      'bad_gateway': 'Server error. Please try again later.',
      'gateway_timeout': 'Request timeout. Please try again.',
      'internal_server_error': 'An unexpected error occurred. Please try again later.',
      'not_implemented': 'This feature is not implemented yet.',
      'bad_request': 'Invalid request. Please check your input.',
      'unauthorized': 'Please log in to continue.',
      'forbidden': 'Access denied.',
      'not_found': 'The requested resource was not found.',
      'method_not_allowed': 'This operation is not allowed.',
      'not_acceptable': 'Request not acceptable.',
      'conflict': 'Resource conflict. Please try again.',
      'gone': 'The requested resource is no longer available.',
      'length_required': 'Content length is required.',
      'precondition_failed': 'Precondition failed.',
      'payload_too_large': 'Request payload is too large.',
      'uri_too_long': 'Request URI is too long.',
      'unsupported_media_type': 'Unsupported media type.',
      'range_not_satisfiable': 'Range not satisfiable.',
      'expectation_failed': 'Expectation failed.',
      'i_am_a_teapot': 'Server error.',
      'misdirected_request': 'Misdirected request.',
      'unprocessable_entity': 'Unprocessable entity.',
      'locked': 'Resource is locked.',
      'failed_dependency': 'Failed dependency.',
      'too_early': 'Request too early.',
      'upgrade_required': 'Upgrade required.',
      'precondition_required': 'Precondition required.',
      'too_many_requests': 'Too many requests.',
      'request_header_fields_too_large': 'Request header fields too large.',
      'unavailable_for_legal_reasons': 'Unavailable for legal reasons.',
      'internal_server_error': 'Internal server error.',
      'not_implemented': 'Not implemented.',
      'bad_gateway': 'Bad gateway.',
      'service_unavailable': 'Service unavailable.',
      'gateway_timeout': 'Gateway timeout.',
      'http_version_not_supported': 'HTTP version not supported.',
      'variant_also_negotiates': 'Variant also negotiates.',
      'insufficient_storage': 'Insufficient storage.',
      'loop_detected': 'Loop detected.',
      'not_extended': 'Not extended.',
      'network_authentication_required': 'Network authentication required.',
    }
  }

  /**
   * Handle API errors and display user-friendly messages
   */
  handleApiError(error, context = '') {
    let userMessage = 'Something went wrong. Please try again.'
    let technicalMessage = error.message || 'Unknown error'
    let errorType = 'unknown'
    
    // Handle different error types
    if (error.userMessage) {
      // Error already processed by API service
      userMessage = error.userMessage
      technicalMessage = error.technicalMessage
      errorType = error.type || 'api'
    } else if (error.status) {
      // HTTP error
      userMessage = this.errorMessages[error.status] || userMessage
      errorType = 'http'
    } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
      // Network error
      userMessage = this.errorMessages['Network Error']
      errorType = 'network'
    } else if (error.code) {
      // Firebase/auth error
      userMessage = this.errorMessages[error.code] || userMessage
      errorType = 'auth'
    } else if (error.message) {
      // Generic error with message
      userMessage = this.errorMessages[error.message] || error.message
      errorType = 'generic'
    }

    // Log technical details for debugging
    console.error(`Error [${context}]:`, {
      userMessage,
      technicalMessage,
      errorType,
      originalError: error,
      timestamp: new Date().toISOString()
    })

    // Show user-friendly message
    this.showError(userMessage, context)

    return {
      userMessage,
      technicalMessage,
      errorType,
      context
    }
  }

  /**
   * Show error message to user
   */
  showError(message, context = '') {
    toast.error(message, {
      position: 'top-right',
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      theme: 'light',
    })
  }

  /**
   * Show success message to user
   */
  showSuccess(message, context = '') {
    toast.success(message, {
      position: 'top-right',
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      theme: 'light',
    })
  }

  /**
   * Show warning message to user
   */
  showWarning(message, context = '') {
    toast.warning(message, {
      position: 'top-right',
      autoClose: 4000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      theme: 'light',
    })
  }

  /**
   * Show info message to user
   */
  showInfo(message, context = '') {
    toast.info(message, {
      position: 'top-right',
      autoClose: 4000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      theme: 'light',
    })
  }

  /**
   * Handle form validation errors
   */
  handleValidationError(errors, context = '') {
    if (typeof errors === 'object') {
      Object.keys(errors).forEach(field => {
        const message = errors[field]
        this.showError(`${field}: ${message}`, context)
      })
    } else if (Array.isArray(errors)) {
      errors.forEach(error => {
        this.showError(error, context)
      })
    } else {
      this.showError(errors, context)
    }
  }

  /**
   * Handle async operations with error handling
   */
  async handleAsync(operation, context = '') {
    try {
      const result = await operation()
      return { success: true, data: result }
    } catch (error) {
      const errorInfo = this.handleApiError(error, context)
      return { success: false, error: errorInfo }
    }
  }

  /**
   * Handle async operations with success message
   */
  async handleAsyncWithSuccess(operation, successMessage, context = '') {
    const result = await this.handleAsync(operation, context)
    if (result.success) {
      this.showSuccess(successMessage, context)
    }
    return result
  }

  /**
   * Handle async operations with loading state
   */
  async handleAsyncWithLoading(operation, loadingRef, context = '') {
    if (loadingRef) {
      loadingRef.value = true
    }
    
    try {
      const result = await operation()
      return { success: true, data: result }
    } catch (error) {
      const errorInfo = this.handleApiError(error, context)
      return { success: false, error: errorInfo }
    } finally {
      if (loadingRef) {
        loadingRef.value = false
      }
    }
  }

  /**
   * Handle async operations with loading and success message
   */
  async handleAsyncWithLoadingAndSuccess(operation, loadingRef, successMessage, context = '') {
    const result = await this.handleAsyncWithLoading(operation, loadingRef, context)
    if (result.success) {
      this.showSuccess(successMessage, context)
    }
    return result
  }
}

export default new ErrorHandler() 