import { auth } from '@/firebase/config'

// Resolve API base URL robustly across envs
const resolveApiBaseUrl = () => {
  let base = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || ''
  const defaultBase = 'http://localhost:8000/api/v1'
  try {
    if (!base) return defaultBase
    // Trim whitespace
    base = String(base).trim()
    // If already absolute http(s)
    if (/^https?:\/\//i.test(base)) return base.replace(/\/?$/, '')
    // If only path like '/api/v1' → attach same host with default backend port 8000
    if (base.startsWith('/')) {
      return `${window.location.protocol}//${window.location.hostname}:8000${base}`.replace(/\/?$/, '')
    }
    // If starts with ':8000' style
    if (base.startsWith(':')) {
      return `${window.location.protocol}//${window.location.hostname}${base}`.replace(/\/?$/, '')
    }
    // Fallback to default
    return defaultBase
  } catch (_) {
    return defaultBase
  }
}

const API_BASE_URL = resolveApiBaseUrl()

// Get device info for API calls
const getDeviceInfo = () => {
  const userAgent = navigator.userAgent
  const platform = /iPhone|iPad|iPod/.test(userAgent) ? 'ios' : 
                   /Android/.test(userAgent) ? 'android' : 'web'
  
  return {
    platform,
    version: '1.0.0',
    device_id: localStorage.getItem('device_id') || generateDeviceId()
  }
}

// Generate unique device ID
const generateDeviceId = () => {
  const deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  localStorage.setItem('device_id', deviceId)
  return deviceId
}

// Get Firebase ID token or fallback to stored backend access token
const getAuthToken = async () => {
  try {
    const user = auth.currentUser
    if (user) {
      return await user.getIdToken()
    }
  } catch (error) {
    console.error('Error getting Firebase ID token:', error)
  }
  // Fallback to backend JWT if available
  const backendToken = localStorage.getItem('access_token')
  if (backendToken) return backendToken
  throw new Error('No authenticated user')
}

// Attempt refresh with backend refresh token
const tryRefreshToken = async () => {
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) return false
  try {
    const response = await fetch(`${API_BASE_URL}/auth/users/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    })
    if (!response.ok) return false
    const data = await response.json()
    if (data && data.access) {
      localStorage.setItem('access_token', data.access)
      return true
    }
    if (data && data.access_token) {
      localStorage.setItem('access_token', data.access_token)
      if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
      return true
    }
    return false
  } catch (e) {
    console.warn('Refresh request failed:', e)
    return false
  }
}

// API request helper
const apiRequest = async (endpoint, options = {}) => {
  try {
    const idToken = await getAuthToken()
    
    const isFormData = options && options.body && (typeof FormData !== 'undefined') && options.body instanceof FormData

    const defaultHeaders = {
      'Authorization': `Bearer ${idToken}`,
      ...(isFormData ? {} : { 'Content-Type': 'application/json' })
    }

    const url = `${API_BASE_URL}${endpoint}`
    console.log('Making API request:', {
      url,
      method: options.method || 'GET',
      headers: { ...defaultHeaders, ...options.headers },
      body: isFormData ? '[FormData]' : options.body
    })

    let response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    })

    console.log('API response status:', response.status)
    console.log('API response headers:', Object.fromEntries(response.headers.entries()))

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('API error response:', errorData)
      
      const error = new Error(errorData.message || errorData.detail || `HTTP error! status: ${response.status}`)
      error.response = errorData
      error.status = response.status
      // Handle 401 by attempting refresh token flow once
      if (response.status === 401) {
        try {
          const refreshed = await tryRefreshToken()
          if (refreshed) {
            // Retry the original request with new token
            const retried = await fetch(url, {
              ...options,
              headers: {
                ...defaultHeaders,
                ...(options.headers || {}),
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
              }
            })
            if (!retried.ok) {
              const retryErr = await retried.json().catch(() => ({}))
              const e = new Error(retryErr.message || retryErr.detail || `HTTP error! status: ${retried.status}`)
              e.status = retried.status
              throw e
            }
            const ct = retried.headers.get('content-type') || ''
            return ct.includes('application/json') ? await retried.json() : await retried.text()
          }
        } catch (refreshErr) {
          console.warn('Token refresh failed:', refreshErr)
        }
        // Hard sign-out
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('session_id')
        localStorage.removeItem('bottleplug_session')
        // Redirect to login and preserve destination
        try { sessionStorage.setItem('intendedDestination', window.location.pathname + window.location.search) } catch (_) {}
        try { window.location.href = '/' } catch (_) {}
      }
      throw error
    }

    const contentType = response.headers.get('content-type') || ''
    const responseData = contentType.includes('application/json') ? await response.json() : await response.text()
    console.log('API response data:', responseData)
    return responseData
  } catch (error) {
    console.error('API request failed:', error)
    throw error
  }
}

// Verify Firebase token with backend
export const verifyFirebaseToken = async () => {
  try {
    const deviceInfo = getDeviceInfo()
    const idToken = await getAuthToken()
    
    const requestBody = {
      id_token: idToken,
      device_info: deviceInfo
    }
    
    console.log('Sending request to backend:', {
      url: `${API_BASE_URL}/auth/users/verify_firebase_token/`,
      headers: {
        'Authorization': `Bearer ${idToken}`,
        'Content-Type': 'application/json'
      },
      body: requestBody
    })
    
    console.log('Request body (JSON):', JSON.stringify(requestBody, null, 2))
    
    const response = await fetch(`${API_BASE_URL}/auth/users/verify_firebase_token/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${idToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })

    console.log('Backend response status:', response.status)
    console.log('Backend response headers:', Object.fromEntries(response.headers.entries()))

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('Backend error response:', errorData)
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
    }

    const responseData = await response.json()
    console.log('Backend success response:', responseData)
    return responseData
  } catch (error) {
    console.error('Firebase token verification failed:', error)
    throw error
  }
}

// ===== DASHBOARD ANALYTICS =====

// Get dashboard statistics
export const getDashboardStats = async (days = 30) => {
  try {
    return await apiRequest(`/analytics/dashboard/stats/?days=${days}`)
  } catch (error) {
    console.error('Failed to get dashboard stats:', error)
    throw error
  }
}

// Get dashboard charts data
export const getDashboardCharts = async (days = 30) => {
  try {
    return await apiRequest(`/analytics/dashboard/charts/?days=${days}`)
  } catch (error) {
    console.error('Failed to get dashboard charts:', error)
    throw error
  }
}

// Get sales data
export const getSalesData = async (days = 30) => {
  try {
    return await apiRequest(`/analytics/dashboard/sales/?days=${days}`)
  } catch (error) {
    console.error('Failed to get sales data:', error)
    throw error
  }
}

// Get order status data
export const getOrderStatusData = async (days = 30) => {
  try {
    return await apiRequest(`/analytics/dashboard/order_status/?days=${days}`)
  } catch (error) {
    console.error('Failed to get order status data:', error)
    throw error
  }
}

// Get revenue data
export const getRevenueData = async (days = 30) => {
  try {
    return await apiRequest(`/analytics/dashboard/revenue/?days=${days}`)
  } catch (error) {
    console.error('Failed to get revenue data:', error)
    throw error
  }
}

// Analytics page specific endpoints removed

// Download invoice PDF (backend-rendered)
export const downloadInvoicePdf = async (invoiceId) => {
  try {
    const idToken = await getAuthToken()
    const url = `${API_BASE_URL}/orders/invoices/${invoiceId}/download_pdf/`
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${idToken}` }
    })
    if (!response.ok) {
      const errorText = await response.text().catch(() => '')
      throw new Error(errorText || `HTTP error! status: ${response.status}`)
    }
    return await response.blob()
  } catch (error) {
    console.error('Failed to download invoice PDF:', error)
    throw error
  }
}

// Get top products
export const getTopProducts = async (days = 30) => {
  try {
    return await apiRequest(`/analytics/dashboard/top_products/?days=${days}`)
  } catch (error) {
    console.error('Failed to get top products:', error)
    throw error
  }
}

// Get recent orders
export const getRecentOrders = async (days = 30) => {
  try {
    return await apiRequest(`/analytics/dashboard/recent_orders/?days=${days}`)
  } catch (error) {
    console.error('Failed to get recent orders:', error)
    throw error
  }
}

// ===== PRODUCTS =====

// Get all products
export const getProducts = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    const url = `/products/products/${queryString ? `?${queryString}` : ''}`
    console.log('API Request URL:', url)
    console.log('API Request Params:', params)
    
    const response = await apiRequest(url)
    console.log('API Response:', response)
    
    return response
  } catch (error) {
    console.error('Failed to get products:', error)
    throw error
  }
}

// Get product by ID
export const getProduct = async (id) => {
  try {
    return await apiRequest(`/products/products/${id}/`)
  } catch (error) {
    console.error('Failed to get product:', error)
    throw error
  }
}

// Get product categories
export const getCategories = async () => {
  try {
    return await apiRequest('/products/categories/')
  } catch (error) {
    console.error('Failed to get categories:', error)
    throw error
  }
}

// Get product statistics
export const getProductStats = async () => {
  try {
    return await apiRequest('/products/products/stats/')
  } catch (error) {
    console.error('Failed to get product stats:', error)
    throw error
  }
}

export const createCategory = async (categoryData) => {
  try {
    // Check if categoryData is FormData (for file uploads)
    if (categoryData instanceof FormData) {
      const idToken = await getAuthToken()
      
      const response = await fetch(`${API_BASE_URL}/products/categories/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          // Don't set Content-Type for FormData, let browser set it with boundary
        },
        body: categoryData
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } else {
      // Handle regular JSON data
      return await apiRequest('/products/categories/', {
        method: 'POST',
        body: JSON.stringify(categoryData)
      })
    }
  } catch (error) {
    console.error('Failed to create category:', error)
    throw error
  }
}

export const createProduct = async (productData) => {
  try {
    // Check if productData is FormData (for file uploads)
    if (productData instanceof FormData) {
      const idToken = await getAuthToken()
      
      const response = await fetch(`${API_BASE_URL}/products/products/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          // Don't set Content-Type for FormData, let browser set it with boundary
        },
        body: productData
      })

      console.log('Product creation response status:', response.status)
      console.log('Product creation response ok:', response.ok)

      if (!response.ok && response.status !== 201) {
        const errorData = await response.json().catch(() => ({}))
        console.error('Product creation error response:', errorData)
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('Product creation result:', result)
      return result
    } else {
      // Handle regular JSON data
      return await apiRequest('/products/products/', {
        method: 'POST',
        body: JSON.stringify(productData)
      })
    }
  } catch (error) {
    console.error('Failed to create product:', error)
    throw error
  }
}

export const updateProduct = async (productId, productData) => {
  try {
    // Check if productData is FormData (for file uploads)
    if (productData instanceof FormData) {
      const idToken = await getAuthToken()
      
      const response = await fetch(`${API_BASE_URL}/products/products/${productId}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          // Don't set Content-Type for FormData, let browser set it with boundary
        },
        body: productData
      })

      if (!response.ok && response.status !== 201) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } else {
      // Handle regular JSON data
      return await apiRequest(`/products/products/${productId}/`, {
        method: 'PUT',
        body: JSON.stringify(productData)
      })
    }
  } catch (error) {
    console.error('Failed to update product:', error)
    throw error
  }
}



export const deleteProduct = async (id) => {
  try {
    return await apiRequest(`/products/products/${id}/`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Failed to delete product:', error)
    throw error
  }
}

// Product Measurements API
export const getProductMeasurements = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams()
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
        queryParams.append(key, params[key])
      }
    })
    
    const queryString = queryParams.toString()
    const url = `/products/measurements/${queryString ? `?${queryString}` : ''}`
    
    return await apiRequest(url)
  } catch (error) {
    console.error('Failed to fetch product measurements:', error)
    throw error
  }
}

export const getProductMeasurement = async (id) => {
  try {
    return await apiRequest(`/products/measurements/${id}/`)
  } catch (error) {
    console.error('Failed to fetch product measurement:', error)
    throw error
  }
}

export const createProductMeasurement = async (measurementData) => {
  try {
    return await apiRequest('/products/measurements/', {
      method: 'POST',
      body: JSON.stringify(measurementData)
    })
  } catch (error) {
    console.error('Failed to create product measurement:', error)
    throw error
  }
}

export const updateProductMeasurement = async (id, measurementData) => {
  try {
    return await apiRequest(`/products/measurements/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(measurementData)
    })
  } catch (error) {
    console.error('Failed to update product measurement:', error)
    throw error
  }
}

export const deleteProductMeasurement = async (id) => {
  try {
    return await apiRequest(`/products/measurements/${id}/`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Failed to delete product measurement:', error)
    throw error
  }
}

export const updateMeasurementStock = async (id, stockData) => {
  try {
    return await apiRequest(`/products/measurements/${id}/update_stock/`, {
      method: 'POST',
      body: JSON.stringify(stockData)
    })
  } catch (error) {
    console.error('Failed to update measurement stock:', error)
    throw error
  }
}

// Stock management endpoints
export const stockIn = async (stockData) => {
  try {
    return await apiRequest('/stock/stock-in/', {
      method: 'POST',
      body: JSON.stringify(stockData)
    })
  } catch (error) {
    console.error('Failed to process stock in:', error)
    throw error
  }
}

export const stockOut = async (stockData) => {
  try {
    return await apiRequest('/stock/stock-out/', {
      method: 'POST',
      body: JSON.stringify(stockData)
    })
  } catch (error) {
    console.error('Failed to process stock out:', error)
    throw error
  }
}

export const getStockHistory = async (productId, params = {}) => {
  try {
    const queryString = new URLSearchParams({ product: productId, ...params }).toString()
    return await apiRequest(`/stock/history/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to get stock history:', error)
    throw error
  }
}

export const updateProductStock = async (productId, stockData) => {
  try {
    return await apiRequest(`/products/products/${productId}/update_stock/`, {
      method: 'POST',
      body: JSON.stringify(stockData)
    })
  } catch (error) {
    console.error('Failed to update product stock:', error)
    throw error
  }
}

export const getMeasurementTypes = async () => {
  try {
    return await apiRequest('/products/measurements/measurements_list/')
  } catch (error) {
    console.error('Failed to fetch measurement types:', error)
    throw error
  }
}

// Search products
export const searchProducts = async (query, params = {}) => {
  try {
    const searchParams = new URLSearchParams({ search: query, ...params })
    return await apiRequest(`/products/products/?${searchParams}`)
  } catch (error) {
    console.error('Failed to search products:', error)
    throw error
  }
}

// ===== ORDERS =====

// Get all orders with advanced date filtering
export const getOrders = async (params = {}) => {
  try {
    // Build query parameters for advanced filtering
    const queryParams = { ...params }
    
    // Handle date filtering
    if (params.dateFilter) {
      queryParams.date_filter = params.dateFilter
    }
    if (params.startDate) {
      queryParams.start_date = params.startDate
    }
    if (params.endDate) {
      queryParams.end_date = params.endDate
    }
    if (params.specificDate) {
      queryParams.specific_date = params.specificDate
    }
    
    const queryString = new URLSearchParams(queryParams).toString()
    const endpoint = `/orders/orders/${queryString ? `?${queryString}` : ''}`
    
    console.log('getOrders API call:', {
      originalParams: params,
      processedParams: queryParams,
      queryString,
      endpoint
    })
    
    return await apiRequest(endpoint)
  } catch (error) {
    console.error('Failed to get orders:', error)
    throw error
  }
}

// Get order by ID
export const getOrder = async (id) => {
  try {
    return await apiRequest(`/orders/orders/${id}/`)
  } catch (error) {
    console.error('Failed to get order:', error)
    throw error
  }
}

export const getOrderPaymentBalance = async (orderId) => {
  try {
    return await apiRequest(`/orders/orders/${orderId}/payment_balance/`)
  } catch (error) {
    console.error('Failed to get order payment balance:', error)
    throw error
  }
}

// Create new order
export const createOrder = async (orderData) => {
  try {
    return await apiRequest('/orders/orders/', {
      method: 'POST',
      body: JSON.stringify(orderData)
    })
  } catch (error) {
    console.error('Failed to create order:', error)
    throw error
  }
}

// Update order
export const updateOrder = async (id, orderData) => {
  try {
    return await apiRequest(`/orders/orders/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(orderData)
    })
  } catch (error) {
    console.error('Failed to update order:', error)
    throw error
  }
}

// Update order status
export const updateOrderStatus = async (id, status) => {
  try {
    console.log('API: updateOrderStatus called with:', { id, status })
    const result = await apiRequest(`/orders/orders/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    })
    console.log('API: updateOrderStatus result:', result)
    return result
  } catch (error) {
    console.error('API: Failed to update order status:', error)
    throw error
  }
}

// Cancel order
export const cancelOrder = async (id, reason = '') => {
  try {
    return await apiRequest(`/orders/orders/${id}/cancel/`, {
      method: 'POST',
      body: JSON.stringify({ cancellation_reason: reason })
    })
  } catch (error) {
    console.error('Failed to cancel order:', error)
    throw error
  }
}

// Confirm order (admin only)
export const confirmOrder = async (id) => {
  try {
    return await apiRequest(`/orders/orders/${id}/confirm/`, {
      method: 'POST'
    })
  } catch (error) {
    console.error('Failed to confirm order:', error)
    throw error
  }
}

// Assign driver to order
export const assignDriverToOrder = async (orderId, driverId) => {
  try {
    return await apiRequest(`/orders/orders/${orderId}/assign_driver/`, {
      method: 'POST',
      body: JSON.stringify({ driver_id: driverId })
    })
  } catch (error) {
    console.error('Failed to assign driver to order:', error)
    throw error
  }
}

// Get order statistics
export const getOrderStats = async () => {
  try {
    return await apiRequest('/orders/orders/basic_stats/')
  } catch (error) {
    console.error('Failed to get order stats:', error)
    throw error
  }
}

// ===== ORDER RECEIPTS =====

// Get all receipts
export const getReceipts = async (params = {}) => {
  try {
    return await apiRequest('/orders/receipts/', { params })
  } catch (error) {
    console.error('Failed to get receipts:', error)
    throw error
  }
}

// Get receipt by ID
export const getReceipt = async (id) => {
  try {
    return await apiRequest(`/orders/receipts/${id}/`)
  } catch (error) {
    console.error('Failed to get receipt:', error)
    throw error
  }
}

// Create receipt
export const createReceipt = async (receiptData) => {
  try {
    return await apiRequest('/orders/receipts/', {
      method: 'POST',
      body: JSON.stringify(receiptData)
    })
  } catch (error) {
    console.error('Failed to create receipt:', error)
    throw error
  }
}

// Update receipt
export const updateReceipt = async (id, receiptData) => {
  try {
    return await apiRequest(`/orders/receipts/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(receiptData)
    })
  } catch (error) {
    console.error('Failed to update receipt:', error)
    throw error
  }
}

// Delete receipt
export const deleteReceipt = async (id) => {
  try {
    return await apiRequest(`/orders/receipts/${id}/`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Failed to delete receipt:', error)
    throw error
  }
}

// Get user's receipts
export const getMyReceipts = async () => {
  try {
    return await apiRequest('/orders/receipts/my_receipts/')
  } catch (error) {
    console.error('Failed to get my receipts:', error)
    throw error
  }
}

// Send receipt to customer
export const sendReceiptToCustomer = async (id) => {
  try {
    return await apiRequest(`/orders/receipts/${id}/send_to_customer/`, {
      method: 'POST'
    })
  } catch (error) {
    console.error('Failed to send receipt to customer:', error)
    throw error
  }
}

// Sign receipt by customer
export const signReceiptByCustomer = async (id, signatureData) => {
  try {
    return await apiRequest(`/orders/receipts/${id}/sign_by_customer/`, {
      method: 'POST',
      body: JSON.stringify({ signature: signatureData })
    })
  } catch (error) {
    console.error('Failed to sign receipt:', error)
    throw error
  }
}

// Mark receipt as delivered
export const markReceiptDelivered = async (id) => {
  try {
    return await apiRequest(`/orders/receipts/${id}/mark_delivered/`, {
      method: 'POST'
    })
  } catch (error) {
    console.error('Failed to mark receipt as delivered:', error)
    throw error
  }
}

// ===== INVOICES =====

// Get all invoices
export const getInvoices = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    const endpoint = `/orders/invoices/${queryString ? `?${queryString}` : ''}`
    
    console.log('getInvoices API call:', {
      params,
      queryString,
      endpoint
    })
    
    return await apiRequest(endpoint)
  } catch (error) {
    console.error('Failed to get invoices:', error)
    throw error
  }
}

// Get invoice by ID
export const getInvoice = async (id) => {
  try {
    return await apiRequest(`/orders/invoices/${id}/`)
  } catch (error) {
    console.error('Failed to get invoice:', error)
    throw error
  }
}

// Create invoice
export const createInvoice = async (invoiceData) => {
  try {
    return await apiRequest('/orders/invoices/', {
      method: 'POST',
      body: JSON.stringify(invoiceData)
    })
  } catch (error) {
    console.error('Failed to create invoice:', error)
    throw error
  }
}

// Update invoice
export const updateInvoice = async (id, invoiceData) => {
  try {
    return await apiRequest(`/orders/invoices/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(invoiceData)
    })
  } catch (error) {
    console.error('Failed to update invoice:', error)
    throw error
  }
}

// Delete invoice
export const deleteInvoice = async (id) => {
  try {
    return await apiRequest(`/orders/invoices/${id}/`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Failed to delete invoice:', error)
    throw error
  }
}

// Get user's invoices
export const getMyInvoices = async () => {
  try {
    return await apiRequest('/orders/invoices/my_invoices/')
  } catch (error) {
    console.error('Failed to get my invoices:', error)
    throw error
  }
}

// Send invoice to customer
export const sendInvoice = async (id) => {
  try {
    return await apiRequest(`/orders/invoices/${id}/send_invoice/`, {
      method: 'POST'
    })
  } catch (error) {
    console.error('Failed to send invoice:', error)
    throw error
  }
}

// Apply payment to invoice
export const applyPayment = async (id, paymentData) => {
  try {
    return await apiRequest(`/orders/invoices/${id}/apply_payment/`, {
      method: 'POST',
      body: JSON.stringify(paymentData)
    })
  } catch (error) {
    console.error('Failed to apply payment:', error)
    throw error
  }
}

// Mark invoice as paid
export const markInvoicePaid = async (id, paymentData = {}) => {
  try {
    return await apiRequest(`/orders/invoices/${id}/mark_paid/`, {
      method: 'POST',
      body: JSON.stringify(paymentData)
    })
  } catch (error) {
    console.error('Failed to mark invoice as paid:', error)
    throw error
  }
}

// Cancel invoice
export const cancelInvoice = async (id) => {
  try {
    return await apiRequest(`/orders/invoices/${id}/cancel_invoice/`, {
      method: 'POST'
    })
  } catch (error) {
    console.error('Failed to cancel invoice:', error)
    throw error
  }
}

// Get invoice statistics
export const getInvoiceStats = async () => {
  try {
    return await apiRequest('/orders/invoices/stats/')
  } catch (error) {
    console.error('Failed to get invoice stats:', error)
    throw error
  }
}

// ===== PAYMENTS =====

// Payment Methods
export const getPaymentMethods = async (params = {}) => {
  try {
    return await apiRequest('/payments/payment-methods/', { params })
  } catch (error) {
    console.error('Failed to get payment methods:', error)
    throw error
  }
}

export const getPaymentMethodsByCountry = async (country = 'NG') => {
  try {
    return await apiRequest(`/payments/payment-methods/by_country/?country=${country}`)
  } catch (error) {
    console.error('Failed to get payment methods by country:', error)
    throw error
  }
}

// Payment Transactions
export const getPaymentTransactions = async (params = {}) => {
  try {
    return await apiRequest('/payments/transactions/', { params })
  } catch (error) {
    console.error('Failed to get payment transactions:', error)
    throw error
  }
}

export const getPaymentTransaction = async (id) => {
  try {
    return await apiRequest(`/payments/transactions/${id}/`)
  } catch (error) {
    console.error('Failed to get payment transaction:', error)
    throw error
  }
}

export const createPaymentTransaction = async (transactionData) => {
  try {
    return await apiRequest('/payments/transactions/', {
      method: 'POST',
      body: JSON.stringify(transactionData)
    })
  } catch (error) {
    console.error('Failed to create payment transaction:', error)
    throw error
  }
}

export const updatePaymentTransaction = async (id, transactionData) => {
  try {
    return await apiRequest(`/payments/transactions/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(transactionData)
    })
  } catch (error) {
    console.error('Failed to update payment transaction:', error)
    throw error
  }
}

export const deletePaymentTransaction = async (id) => {
  try {
    return await apiRequest(`/payments/transactions/${id}/`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Failed to delete payment transaction:', error)
    throw error
  }
}

// Payment Initiation
export const initiatePayment = async (paymentData) => {
  try {
    return await apiRequest('/payments/transactions/initiate_payment/', {
      method: 'POST',
      body: JSON.stringify(paymentData)
    })
  } catch (error) {
    console.error('Failed to initiate payment:', error)
    throw error
  }
}

// Payment Verification
export const verifyPayment = async (transactionId) => {
  try {
    return await apiRequest(`/payments/transactions/${transactionId}/verify_payment/`, {
      method: 'POST'
    })
  } catch (error) {
    console.error('Failed to verify payment:', error)
    throw error
  }
}

// User Payment Transactions
export const getMyPaymentTransactions = async () => {
  try {
    return await apiRequest('/payments/transactions/my_transactions/')
  } catch (error) {
    console.error('Failed to get my payment transactions:', error)
    throw error
  }
}

// Payment Statistics
export const getPaymentStats = async () => {
  try {
    return await apiRequest('/payments/transactions/stats/')
  } catch (error) {
    console.error('Failed to get payment stats:', error)
    throw error
  }
}

// Payment Refunds
export const getPaymentRefunds = async (params = {}) => {
  try {
    return await apiRequest('/payments/refunds/', { params })
  } catch (error) {
    console.error('Failed to get payment refunds:', error)
    throw error
  }
}

export const getPaymentRefund = async (id) => {
  try {
    return await apiRequest(`/payments/refunds/${id}/`)
  } catch (error) {
    console.error('Failed to get payment refund:', error)
    throw error
  }
}

export const createPaymentRefund = async (refundData) => {
  try {
    return await apiRequest('/payments/refunds/', {
      method: 'POST',
      body: JSON.stringify(refundData)
    })
  } catch (error) {
    console.error('Failed to create payment refund:', error)
    throw error
  }
}

export const createFlutterwaveRefund = async (refundData) => {
  try {
    return await apiRequest('/payments/refunds/create_flutterwave_refund/', {
      method: 'POST',
      body: JSON.stringify(refundData)
    })
  } catch (error) {
    console.error('Failed to create Flutterwave refund:', error)
    throw error
  }
}

// Payment Plans
export const getPaymentPlans = async (params = {}) => {
  try {
    return await apiRequest('/payments/plans/', { params })
  } catch (error) {
    console.error('Failed to get payment plans:', error)
    throw error
  }
}

export const getPaymentPlan = async (id) => {
  try {
    return await apiRequest(`/payments/plans/${id}/`)
  } catch (error) {
    console.error('Failed to get payment plan:', error)
    throw error
  }
}

// Payment Subscriptions
export const getPaymentSubscriptions = async (params = {}) => {
  try {
    return await apiRequest('/payments/subscriptions/', { params })
  } catch (error) {
    console.error('Failed to get payment subscriptions:', error)
    throw error
  }
}

export const getPaymentSubscription = async (id) => {
  try {
    return await apiRequest(`/payments/subscriptions/${id}/`)
  } catch (error) {
    console.error('Failed to get payment subscription:', error)
    throw error
  }
}

export const createPaymentSubscription = async (subscriptionData) => {
  try {
    return await apiRequest('/payments/subscriptions/', {
      method: 'POST',
      body: JSON.stringify(subscriptionData)
    })
  } catch (error) {
    console.error('Failed to create payment subscription:', error)
    throw error
  }
}

export const updatePaymentSubscription = async (id, subscriptionData) => {
  try {
    return await apiRequest(`/payments/subscriptions/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(subscriptionData)
    })
  } catch (error) {
    console.error('Failed to update payment subscription:', error)
    throw error
  }
}

export const deletePaymentSubscription = async (id) => {
  try {
    return await apiRequest(`/payments/subscriptions/${id}/`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Failed to delete payment subscription:', error)
    throw error
  }
}

export const getMyPaymentSubscriptions = async () => {
  try {
    return await apiRequest('/payments/subscriptions/my_subscriptions/')
  } catch (error) {
    console.error('Failed to get my payment subscriptions:', error)
    throw error
  }
}

// Flutterwave Utilities
export const getFlutterwaveBanks = async (country = 'NG') => {
  try {
    return await apiRequest(`/payments/flutterwave/banks/?country=${country}`)
  } catch (error) {
    console.error('Failed to get Flutterwave banks:', error)
    throw error
  }
}

export const validateBankAccount = async (accountData) => {
  try {
    return await apiRequest('/payments/flutterwave/validate_bank_account/', {
      method: 'POST',
      body: JSON.stringify(accountData)
    })
  } catch (error) {
    console.error('Failed to validate bank account:', error)
    throw error
  }
}

// Payment Webhooks
export const getPaymentWebhooks = async (params = {}) => {
  try {
    return await apiRequest('/payments/webhooks/', { params })
  } catch (error) {
    console.error('Failed to get payment webhooks:', error)
    throw error
  }
}

export const getPaymentWebhook = async (id) => {
  try {
    return await apiRequest(`/payments/webhooks/${id}/`)
  } catch (error) {
    console.error('Failed to get payment webhook:', error)
    throw error
  }
}

// Payment Receipts
export const getPaymentReceipts = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    return await apiRequest(`/payments/payment_receipts/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to get payment receipts:', error)
    throw error
  }
}

export const downloadPaymentReceiptPdf = async (id) => {
  try {
    const idToken = await getAuthToken()
    const url = `${API_BASE_URL}/payments/payment_receipts/${id}/download_pdf/`
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    })
    if (!response.ok) {
      const errorText = await response.text().catch(() => '')
      throw new Error(errorText || `HTTP error! status: ${response.status}`)
    }
    return await response.blob()
  } catch (error) {
    console.error('Failed to download payment receipt PDF:', error)
    throw error
  }
}

export const syncMissingPaymentReceipts = async () => {
  try {
    return await apiRequest('/payments/payment_receipts/sync_missing/', {
      method: 'POST',
      body: JSON.stringify({})
    })
  } catch (error) {
    console.error('Failed to sync missing payment receipts:', error)
    throw error
  }
}

// Payment Helper Functions
export const createOrderPayment = async (orderId, amount, currency = 'NGN', description = '') => {
  try {
    return await initiatePayment({
      transaction_type: 'order',
      amount: amount,
      currency: currency,
      order_id: orderId,
      description: description || `Payment for order #${orderId}`
    })
  } catch (error) {
    console.error('Failed to create order payment:', error)
    throw error
  }
}

export const createInvoicePayment = async (invoiceId, amount, currency = 'NGN', description = '') => {
  try {
    return await initiatePayment({
      transaction_type: 'invoice',
      amount: amount,
      currency: currency,
      invoice_id: invoiceId,
      description: description || `Payment for invoice #${invoiceId}`
    })
  } catch (error) {
    console.error('Failed to create invoice payment:', error)
    throw error
  }
}

export const createEventPayment = async (eventId, amount, currency = 'NGN', description = '') => {
  try {
    return await initiatePayment({
      transaction_type: 'event',
      amount: amount,
      currency: currency,
      event_id: eventId,
      description: description || `Payment for event #${eventId}`
    })
  } catch (error) {
    console.error('Failed to create event payment:', error)
    throw error
  }
}

export const createReceiptPayment = async (receiptId, amount, currency = 'NGN', description = '') => {
  try {
    return await initiatePayment({
      transaction_type: 'receipt',
      amount: amount,
      currency: currency,
      receipt_id: receiptId,
      description: description || `Payment for receipt #${receiptId}`
    })
  } catch (error) {
    console.error('Failed to create receipt payment:', error)
    throw error
  }
}

// Get user's orders
export const getMyOrders = async () => {
  try {
    return await apiRequest('/orders/orders/my_orders/')
  } catch (error) {
    console.error('Failed to get my orders:', error)
    throw error
  }
}

// ===== CART =====

// Get user's cart
export const getMyCart = async () => {
  try {
    return await apiRequest('/orders/cart/my_cart/')
  } catch (error) {
    console.error('Failed to get my cart:', error)
    throw error
  }
}

// Add item to cart
export const addToCart = async (productId, quantity = 1, productVariantId = null) => {
  try {
    return await apiRequest('/orders/cart/add_item/', {
      method: 'POST',
      body: JSON.stringify({
        product_id: productId,
        quantity: quantity,
        product_variant_id: productVariantId
      })
    })
  } catch (error) {
    console.error('Failed to add item to cart:', error)
    throw error
  }
}

// Update cart item quantity
export const updateCartItem = async (itemId, quantity) => {
  try {
    return await apiRequest('/orders/cart/update_item/', {
      method: 'POST',
      body: JSON.stringify({
        item_id: itemId,
        quantity: quantity
      })
    })
  } catch (error) {
    console.error('Failed to update cart item:', error)
    throw error
  }
}

// Remove item from cart
export const removeFromCart = async (itemId) => {
  try {
    return await apiRequest('/orders/cart/remove_item/', {
      method: 'POST',
      body: JSON.stringify({ item_id: itemId })
    })
  } catch (error) {
    console.error('Failed to remove item from cart:', error)
    throw error
  }
}

// Clear cart
export const clearCart = async () => {
  try {
    return await apiRequest('/orders/cart/clear/', {
      method: 'POST'
    })
  } catch (error) {
    console.error('Failed to clear cart:', error)
    throw error
  }
}

// Checkout cart
export const checkoutCart = async (checkoutData) => {
  try {
    return await apiRequest('/orders/cart/checkout/', {
      method: 'POST',
      body: JSON.stringify(checkoutData)
    })
  } catch (error) {
    console.error('Failed to checkout cart:', error)
    throw error
  }
}

// ===== WISHLIST =====

// Get user's wishlist
export const getMyWishlist = async () => {
  try {
    return await apiRequest('/orders/wishlist/my_wishlist/')
  } catch (error) {
    console.error('Failed to get my wishlist:', error)
    throw error
  }
}

// Add item to wishlist
export const addToWishlist = async (productId) => {
  try {
    return await apiRequest('/orders/wishlist/', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId })
    })
  } catch (error) {
    console.error('Failed to add item to wishlist:', error)
    throw error
  }
}

// Remove item from wishlist
export const removeFromWishlist = async (wishlistItemId) => {
  try {
    return await apiRequest(`/orders/wishlist/${wishlistItemId}/`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Failed to remove item from wishlist:', error)
    throw error
  }
}

// Add wishlist item to cart
export const addWishlistItemToCart = async (wishlistItemId) => {
  try {
    return await apiRequest('/orders/wishlist/add_to_cart/', {
      method: 'POST',
      body: JSON.stringify({ wishlist_item_id: wishlistItemId })
    })
  } catch (error) {
    console.error('Failed to add wishlist item to cart:', error)
    throw error
  }
}

// ===== REVIEWS =====

// Get product reviews
export const getProductReviews = async (productId, params = {}) => {
  try {
    const queryString = new URLSearchParams({ product: productId, ...params }).toString()
    return await apiRequest(`/orders/reviews/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to get product reviews:', error)
    throw error
  }
}

// Create review
export const createReview = async (reviewData) => {
  try {
    return await apiRequest('/orders/reviews/', {
      method: 'POST',
      body: JSON.stringify(reviewData)
    })
  } catch (error) {
    console.error('Failed to create review:', error)
    throw error
  }
}

// Update review
export const updateReview = async (reviewId, reviewData) => {
  try {
    return await apiRequest(`/orders/reviews/${reviewId}/`, {
      method: 'PUT',
      body: JSON.stringify(reviewData)
    })
  } catch (error) {
    console.error('Failed to update review:', error)
    throw error
  }
}

// Delete review
export const deleteReview = async (reviewId) => {
  try {
    return await apiRequest(`/orders/reviews/${reviewId}/`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Failed to delete review:', error)
    throw error
  }
}

// Get user's reviews
export const getMyReviews = async () => {
  try {
    return await apiRequest('/orders/reviews/my_reviews/')
  } catch (error) {
    console.error('Failed to get my reviews:', error)
    throw error
  }
}

// ===== USERS =====

// Get user profile
export const getUserProfile = async () => {
  try {
    return await apiRequest('/auth/users/profile/')
  } catch (error) {
    console.error('Failed to get user profile:', error)
    throw error
  }
}

// Update user profile
export const updateUserProfile = async (userData) => {
  try {
    return await apiRequest('/auth/users/profile/', {
      method: 'PUT',
      body: JSON.stringify(userData)
    })
  } catch (error) {
    console.error('Failed to update user profile:', error)
    throw error
  }
}

// Settings: profile
export const getMyProfile = async () => apiRequest('/auth/users/profile/')
export const patchMyProfile = async (data) => apiRequest('/auth/users/update_profile/', {
  method: 'PATCH',
  body: JSON.stringify(data)
})

// Settings: preferences
export const getMyPreferences = async () => apiRequest('/auth/users/preferences/')
export const updateMyPreferences = async (prefs) => apiRequest('/auth/users/update_preferences/', {
  method: 'PATCH',
  body: JSON.stringify(prefs)
})

// Settings: business info
export const getMyBusiness = async () => apiRequest('/auth/users/business/')
export const updateMyBusiness = async (business) => apiRequest('/auth/users/update_business/', {
  method: 'PATCH',
  body: JSON.stringify(business)
})

// Settings: password
export const changeMyPassword = async (payload) => apiRequest('/auth/users/change_password/', {
  method: 'POST',
  body: JSON.stringify(payload)
})

// Settings: sessions
export const listMySessions = async () => apiRequest('/auth/users/sessions/')
export const revokeMySession = async (sessionId) => apiRequest('/auth/users/revoke_session/', {
  method: 'POST',
  body: JSON.stringify({ session_id: sessionId })
})

// Settings: billing
export const getMyBilling = async () => apiRequest('/auth/users/billing/')

// Settings: sessions revoke all
export const revokeAllMySessions = async (preserveSessionId = null) => apiRequest('/auth/users/revoke_all_sessions/', {
  method: 'POST',
  body: JSON.stringify(preserveSessionId ? { preserve_session_id: preserveSessionId } : {})
})

// Settings: profile image upload
export const uploadProfileImage = async (file) => {
  try {
    const idToken = await getAuthToken()
    const formData = new FormData()
    formData.append('profile_image', file)
    const response = await fetch(`${API_BASE_URL}/auth/users/update_profile/`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${idToken}` },
      body: formData
    })
    if (!response.ok) {
      const text = await response.text().catch(() => '')
      throw new Error(text || `HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Failed to upload profile image:', error)
    throw error
  }
}

// Get all users
export const getUsers = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    return await apiRequest(`/auth/users/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to get users:', error)
    throw error
  }
}

// Get drivers
export const getDrivers = async () => {
  try {
    return await apiRequest('/auth/drivers/')
  } catch (error) {
    console.error('Failed to get drivers:', error)
    throw error
  }
}

// ===== DELIVERIES =====

// Get all deliveries
export const getDeliveries = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    return await apiRequest(`/deliveries/deliveries/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to get deliveries:', error)
    throw error
  }
}

// Get delivery by ID
export const getDelivery = async (id) => {
  try {
    return await apiRequest(`/deliveries/deliveries/${id}/`)
  } catch (error) {
    console.error('Failed to get delivery:', error)
    throw error
  }
}

// Update delivery status
export const updateDeliveryStatus = async (id, status) => {
  try {
    return await apiRequest(`/deliveries/deliveries/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    })
  } catch (error) {
    console.error('Failed to update delivery status:', error)
    throw error
  }
}

// Get user's deliveries
export const getMyDeliveries = async () => {
  try {
    return await apiRequest('/deliveries/deliveries/my_deliveries/')
  } catch (error) {
    console.error('Failed to get my deliveries:', error)
    throw error
  }
}

// ===== EVENTS =====

// Get all events
export const getEvents = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    return await apiRequest(`/events/events/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to get events:', error)
    throw error
  }
}

// Get event by ID
export const getEvent = async (id) => {
  try {
    return await apiRequest(`/events/events/${id}/`)
  } catch (error) {
    console.error('Failed to get event:', error)
    throw error
  }
}

// Create RSVP for current user
export const createRSVP = async ({ event, guest_count = 1, guest_names = [], dietary_restrictions = '', special_requests = '' }) => {
  try {
    return await apiRequest('/events/rsvps/', {
      method: 'POST',
      body: JSON.stringify({ event, guest_count, guest_names, dietary_restrictions, special_requests })
    })
  } catch (error) {
    console.error('Failed to create RSVP:', error)
    throw error
  }
}

// Update RSVP (e.g., status, guest_count)
export const updateRSVP = async (id, data) => {
  try {
    return await apiRequest(`/events/rsvps/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  } catch (error) {
    console.error('Failed to update RSVP:', error)
    throw error
  }
}

// List RSVPs (current user or all for admins)
export const getRSVPs = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    return await apiRequest(`/events/rsvps/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to list RSVPs:', error)
    throw error
  }
}

// Create event
export const createEvent = async (eventData) => {
  try {
    return await apiRequest('/events/events/', {
      method: 'POST',
      body: eventData
    })
  } catch (error) {
    console.error('Failed to create event:', error)
    throw error
  }
}

// Update event
export const updateEvent = async (id, eventData) => {
  try {
    return await apiRequest(`/events/events/${id}/`, {
      method: 'PATCH',
      body: eventData
    })
  } catch (error) {
    console.error('Failed to update event:', error)
    throw error
  }
}

// Delete event
export const deleteEvent = async (id) => {
  try {
    return await apiRequest(`/events/events/${id}/`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Failed to delete event:', error)
    throw error
  }
}

// ===== ANALYTICS EVENTS =====

// Track analytics event
export const trackAnalyticsEvent = async (eventData) => {
  try {
    return await apiRequest('/analytics/events/track_event/', {
      method: 'POST',
      body: JSON.stringify(eventData)
    })
  } catch (error) {
    console.error('Failed to track analytics event:', error)
    throw error
  }
}

// Get analytics events
export const getAnalyticsEvents = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    return await apiRequest(`/analytics/events/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to get analytics events:', error)
    throw error
  }
}

// ===== AUTHENTICATION =====

// Refresh access token
export const refreshAccessToken = async (refreshToken) => {
  try {
    return await apiRequest('/auth/token/refresh/', {
      method: 'POST',
      body: JSON.stringify({
        refresh: refreshToken
      })
    })
  } catch (error) {
    console.error('Failed to refresh token:', error)
    throw error
  }
}

// Logout from backend
export const logoutFromBackend = async (sessionId) => {
  try {
    return await apiRequest(`/auth/users/logout/${sessionId}/`, {
      method: 'POST'
    })
  } catch (error) {
    console.error('Failed to logout from backend:', error)
    throw error
  }
}

// ===== UTILITY FUNCTIONS =====

// Get user's saved addresses
export const getSavedAddresses = async () => {
  try {
    return await apiRequest('/auth/users/addresses/')
  } catch (error) {
    console.error('Failed to get saved addresses:', error)
    throw error
  }
}

// Add new address
export const addAddress = async (addressData) => {
  try {
    return await apiRequest('/auth/users/addresses/', {
      method: 'POST',
      body: JSON.stringify(addressData)
    })
  } catch (error) {
    console.error('Failed to add address:', error)
    throw error
  }
}

// Update wallet balance
export const getWalletBalance = async () => {
  try {
    return await apiRequest('/auth/users/wallet/')
  } catch (error) {
    console.error('Failed to get wallet balance:', error)
    throw error
  }
}

// Update user status
export const updateUserStatus = async (status) => {
  try {
    return await apiRequest('/auth/users/status/', {
      method: 'PUT',
      body: JSON.stringify({ current_status: status })
    })
  } catch (error) {
    console.error('Failed to update user status:', error)
    throw error
  }
}

// Complete Mobile Money Payment Flow (all steps combined)
export const completeMobileMoneyPayment = async (paymentData) => {
  try {
    return await apiRequest('/payments/flutterwave/complete_mobile_money_payment/', {
      method: 'POST',
      body: JSON.stringify(paymentData)
    })
  } catch (error) {
    console.error('Failed to complete mobile money payment:', error)
    throw error
  }
}

// Complete Card Payment Flow (all steps combined)
export const completeCardPayment = async (paymentData) => {
  try {
    return await apiRequest('/payments/flutterwave/complete_card_payment/', {
      method: 'POST',
      body: JSON.stringify(paymentData)
    })
  } catch (error) {
    console.error('Failed to complete card payment:', error)
    throw error
  }
}

export const checkOrderPaymentStatus = async (orderId) => {
  try {
    return await apiRequest(`/payments/transactions/order_payment_status/?order_id=${orderId}`, {
      method: 'GET'
    })
  } catch (error) {
    console.error('Failed to check order payment status:', error)
    throw error
  }
}

// Get payment transactions by order_id field
export const getPaymentTransactionsByOrderId = async (orderId) => {
  try {
    return await apiRequest(`/payments/transactions/?order_id=${orderId}&status=successful`)
  } catch (error) {
    console.error('Failed to get payment transactions by order_id:', error)
    throw error
  }
}

// ===== EXPENSES =====

export const getExpenses = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    return await apiRequest(`/finance/expenses/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to get expenses:', error)
    throw error
  }
}

export const createExpense = async (data) => {
  try {
    return await apiRequest('/finance/expenses/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  } catch (error) {
    console.error('Failed to create expense:', error)
    throw error
  }
}

export const updateExpense = async (id, data) => {
  try {
    return await apiRequest(`/finance/expenses/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  } catch (error) {
    console.error('Failed to update expense:', error)
    throw error
  }
}

export const deleteExpense = async (id) => {
  try {
    return await apiRequest(`/finance/expenses/${id}/`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Failed to delete expense:', error)
    throw error
  }
}

export const getExpenseSummary = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    return await apiRequest(`/finance/expenses/summary/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to get expense summary:', error)
    throw error
  }
}

export const getExpenseCategories = async () => {
  try {
    return await apiRequest('/finance/expenses/categories/')
  } catch (error) {
    console.error('Failed to get expense categories:', error)
    throw error
  }
}

export const getExpenseStats = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    return await apiRequest(`/finance/expenses/stats/${queryString ? `?${queryString}` : ''}`)
  } catch (error) {
    console.error('Failed to get expense stats:', error)
    throw error
  }
}

// Default export for compatibility
const ApiService = {
  baseUrl: API_BASE_URL,
  // Export all the functions as methods
  verifyFirebaseToken,
  getDashboardStats,
  getDashboardCharts,
  getSalesData,
  getOrderStatusData,
  getRevenueData,
  getTopProducts,
  getRecentOrders,
  getProducts,
  getProduct,
  getCategories,
  getProductStats,
  createCategory,
  createProduct,
  updateProduct,
  deleteProduct,
  getProductMeasurements,
  getProductMeasurement,
  createProductMeasurement,
  updateProductMeasurement,
  deleteProductMeasurement,
  updateMeasurementStock,
  stockIn,
  stockOut,
  getStockHistory,
  updateProductStock,
  getMeasurementTypes,
  searchProducts,
  getOrders,
  getOrder,
  getOrderPaymentBalance,
  createOrder,
  updateOrder,
  updateOrderStatus,
  cancelOrder,
  confirmOrder,
  assignDriverToOrder,
  getOrderStats,
  getReceipts,
  getReceipt,
  createReceipt,
  updateReceipt,
  deleteReceipt,
  getMyReceipts,
  sendReceiptToCustomer,
  signReceiptByCustomer,
  markReceiptDelivered,
  getInvoices,
  getInvoice,
  createInvoice,
  updateInvoice,
  deleteInvoice,
  getMyInvoices,
  sendInvoice,
  applyPayment,
  markInvoicePaid,
  cancelInvoice,
  getInvoiceStats,
  getPaymentMethods,
  getPaymentMethodsByCountry,
  getPaymentTransactions,
  getPaymentTransaction,
  createPaymentTransaction,
  updatePaymentTransaction,
  deletePaymentTransaction,
  initiatePayment,
  verifyPayment,
  getMyPaymentTransactions,
  getPaymentStats,
  getPaymentRefunds,
  getPaymentRefund,
  createPaymentRefund,
  createFlutterwaveRefund,
  getPaymentPlans,
  getPaymentPlan,
  getPaymentSubscriptions,
  getPaymentSubscription,
  createPaymentSubscription,
  updatePaymentSubscription,
  deletePaymentSubscription,
  getMyPaymentSubscriptions,
  getFlutterwaveBanks,
  validateBankAccount,
  getPaymentWebhooks,
  getPaymentWebhook,
  createOrderPayment,
  createInvoicePayment,
  createEventPayment,
  createReceiptPayment,
  getMyOrders,
  getMyCart,
  addToCart,
  updateCartItem,
  removeFromCart,
  clearCart,
  checkoutCart,
  getMyWishlist,
  addToWishlist,
  removeFromWishlist,
  addWishlistItemToCart,
  getProductReviews,
  createReview,
  updateReview,
  deleteReview,
  getMyReviews,
  getUserProfile,
  updateUserProfile,
  getUsers,
  getDrivers,
  getDeliveries,
  getDelivery,
  updateDeliveryStatus,
  getMyDeliveries,
  getEvents,
  getEvent,
  createEvent,
  updateEvent,
  deleteEvent,
  trackAnalyticsEvent,
  getAnalyticsEvents,
  refreshAccessToken,
  logoutFromBackend,
  getSavedAddresses,
  addAddress,
  getWalletBalance,
  updateUserStatus,
  completeMobileMoneyPayment,
  completeCardPayment,
  checkOrderPaymentStatus,
  getPaymentTransactionsByOrderId,
  getExpenses,
  createExpense,
  updateExpense,
  deleteExpense,
  getExpenseSummary
}

export default ApiService
