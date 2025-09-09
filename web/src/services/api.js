import axios from 'axios'
import { get_auth_instance } from '../stores/auth'
import { toast_error } from '../lib/toast'

function resolve_api_base_url() {
	const envUrl = import.meta.env.VITE_API_BASE_URL
	if (envUrl) return envUrl.replace(/\/$/, '')
	// Default to same-origin Nginx proxy path
	return '/api/v1'
}

export const API_BASE_URL = resolve_api_base_url()

async function get_headers() {
        const headers = { 
                'Content-Type': 'application/json',
                'X-Platform': 'web',
                'X-App-Version': '1.0.0'
        }
        
        // Always try to get user token first (if user is signed in)
        const auth = get_auth_instance()
        const currentUser = auth.currentUser
        let token = ''
        
        // Check if user is signed in (not anonymous)
        if (currentUser && !currentUser.isAnonymous) {
                try {
                        token = await currentUser.getIdToken()
                        console.log('Using Firebase ID token for signed-in user')
                } catch (error) {
                        console.error('Failed to get ID token:', error)
                        token = localStorage.getItem('firebase_id_token') || ''
                }
        }
        
        if (token) {
                // User is signed in - use their Firebase token
                headers['Authorization'] = `Bearer ${token}`
                console.log('Using signed-in user token for API request')
        } else {
                // No signed-in user - use web token for anonymous access
                const web_token = 'bottleplug-web-token-2024'
                headers['Authorization'] = `Bearer ${web_token}`
                console.log('Using web token for anonymous access')
        }
        
        return headers
}

// Enhanced error handling with user-friendly messages
function handle_error(error, context) {
	let userMessage = 'Something went wrong. Please try again.'
	let technicalMessage = error.toString()

	if (error.response) {
		const status = error.response.status
		switch (status) {
			case 401:
				userMessage = 'Your session has expired. Please log in again.'
				break
			case 403:
				userMessage = 'You don\'t have permission to perform this action.'
				break
			case 404:
				userMessage = 'The requested information could not be found.'
				break
			case 422:
				userMessage = 'Please check your input and try again.'
				break
			case 429:
				userMessage = 'Too many requests. Please wait a moment and try again.'
				break
			case 500:
			case 502:
			case 503:
			case 504:
				userMessage = 'Our servers are experiencing issues. Please try again later.'
				break
		}
		technicalMessage = `HTTP ${status}: ${error.response.statusText}`
	} else if (error.request) {
		userMessage = 'Unable to connect to the server. Please check your internet connection.'
		technicalMessage = 'Network error: Unable to reach the server'
	} else if (error.code === 'ECONNABORTED') {
		userMessage = 'The request took too long. Please check your connection and try again.'
		technicalMessage = 'Request timeout'
	}

	console.error(`API Error [${context}]:`, technicalMessage)
	return { userMessage, technicalMessage, context }
}

async function with_retry(fn, { attempts = 2 } = {}) {
	let lastErr
	for (let i = 0; i < attempts; i++) {
		try { 
			return await fn() 
		} catch (e) { 
			lastErr = e
			if (i === attempts - 1) {
				const error = handle_error(e, 'api_request')
				toast_error(error.userMessage)
				throw error
			}
		}
	}
	throw lastErr
}

async function api_get(path, params = {}) {
        const url = `${API_BASE_URL}${path}`
        return with_retry(async () => axios.get(url, { 
                params, 
                headers: await get_headers(),
                timeout: 10000
        }).then(r => r.data))
}

async function api_post(path, data = {}) {
        const url = `${API_BASE_URL}${path}`
        console.log('api_post called:', { path, url, data })
        return with_retry(async () => axios.post(url, data, { 
                headers: await get_headers(),
                timeout: 10000
        }).then(r => r.data))
}

async function api_patch(path, data = {}) {
        const url = `${API_BASE_URL}${path}`
        return with_retry(async () => axios.patch(url, data, { 
                headers: await get_headers(),
                timeout: 10000
        }).then(r => r.data))
}

async function api_delete(path) {
        const url = `${API_BASE_URL}${path}`
        return with_retry(async () => axios.delete(url, { 
                headers: await get_headers(),
                timeout: 10000
        }).then(r => r.data))
}

export async function api_get_url(full_url) {
	// For pagination 'next' absolute URLs
	return with_retry(async () => axios.get(full_url, { 
		headers: await get_headers(),
		timeout: 10000
	}).then(r => r.data))
}

// Test connection to backend
export async function test_connection() {
	try {
		console.log('Testing connection to:', API_BASE_URL)
		const response = await axios.get(`${API_BASE_URL}/products/categories/`, {
			headers: { 'Content-Type': 'application/json' },
			timeout: 10000
		})
		console.log('Connection test response:', response.status)
		return response.status === 200 || response.status === 401
	} catch (error) {
		console.log('Connection test failed:', error.message)
		return false
	}
}

// ===== PRODUCTS =====
export async function get_products(params = {}) {
        return api_get('/products/products/', params, false) // Use web token
}

export async function get_categories(params = {}) {
        return api_get('/products/categories/', params, false) // Use web token
}

export async function get_product(product_id) {
        if (!product_id) throw new Error('product_id is required')
        return api_get(`/products/products/${product_id}/`, {}, false) // Use web token
}

export async function get_product_category(product_id) {
        if (!product_id) throw new Error('product_id is required')
        return api_get(`/products/products/${product_id}/category/`, {}, false) // Use web token
}

export async function get_featured_products(params = {}) {
        return api_get('/products/products/featured/', params, false) // Use web token
}

export async function get_new_arrivals(params = {}) {
        return api_get('/products/products/new/', params, false) // Use web token
}

export async function get_on_sale(params = {}) {
        return api_get('/products/products/on_sale/', params, false) // Use web token
}

export async function search_products(params = {}) {
        return api_get('/products/products/search/', params, false) // Use web token
}

// ===== AUTH & USER MANAGEMENT =====
// Note: Firebase authentication is handled automatically by the backend
// when Firebase tokens are included in the Authorization header
// No separate verification endpoint is needed

export async function get_user_profile() {
	return api_get('/auth/users/me/')
}

export async function update_user_profile(profile_data) {
	return api_patch('/auth/users/me/', profile_data)
}

export async function get_user_stats() {
	return api_get('/auth/users/stats/')
}

export async function update_user_location(location_data) {
	return api_post('/auth/location/', location_data)
}

// ===== CART =====
export async function get_cart() {
        return api_get('/orders/cart/my_cart/', {}) // Dynamic auth
}

export async function add_to_cart(payload) {
        // payload: { product: id, quantity, variant }
        console.log('add_to_cart called with payload:', payload)
        console.log('Making POST request to: /orders/cart/add_item/')
        return api_post('/orders/cart/add_item/', payload) // Dynamic auth
}

export async function update_cart_item(item_id, payload) {
        return api_post('/orders/cart/update_item/', { item_id, ...payload }) // Dynamic auth
}

export async function remove_cart_item(item_id) {
        return api_post('/orders/cart/remove_item/', { item_id }) // Dynamic auth
}

export async function clear_cart() {
        return api_post('/orders/cart/clear/', {}) // Dynamic auth
}

export async function checkout_cart(payload = {}) {
	return api_post('/orders/cart/checkout/', payload) // Dynamic auth
}

// ===== ORDERS =====
export async function get_orders(params = {}) {
        return api_get('/orders/orders/', params) // Dynamic auth
}

export async function get_my_orders(params = {}) {
        return api_get('/orders/orders/my_orders/', params) // Dynamic auth
}

export async function get_order(order_id) {
        return api_get(`/orders/orders/${order_id}/`, {}) // Dynamic auth
}

export async function get_order_stats() {
        return api_get('/orders/orders/order_stats/', {}) // Dynamic auth
}

// ===== WISHLIST =====
export async function get_wishlist(params = {}) {
        // Always use web token for wishlist reading
        const url = `${API_BASE_URL}/orders/wishlist/`
        console.log('Getting wishlist with web token:', url)
        return with_retry(async () => axios.get(url, { 
                headers: {
                        'Content-Type': 'application/json',
                        'X-Platform': 'web',
                        'X-App-Version': '1.0.0',
                        'Authorization': 'Bearer bottleplug-web-token-2024'
                },
                timeout: 10000
        }).then(r => r.data))
}

export async function add_to_wishlist(payload) {
        return api_post('/orders/wishlist/', payload) // Dynamic auth for writing
}

export async function remove_wishlist_item(item_id) {
        return api_delete(`/orders/wishlist/${item_id}/`) // Dynamic auth for writing
}

export async function move_wishlist_to_cart(wishlist_id) {
        return api_post('/orders/wishlist/add_to_cart/', { wishlist_id }) // Dynamic auth
}

// ===== REVIEWS =====
export async function get_reviews(params = {}) {
	return api_get('/orders/reviews/', params)
}

export async function create_review(payload) {
	return api_post('/orders/reviews/', payload)
}

export async function update_review(review_id, payload) {
	return api_patch(`/orders/reviews/${review_id}/`, payload)
}

export async function delete_review(review_id) {
	return api_delete(`/orders/reviews/${review_id}/`)
}

// ===== EVENTS =====
export async function get_events(params = {}) {
	return api_get('/events/events/', params)
}

export async function get_event(event_id) {
	return api_get(`/events/events/${event_id}/`)
}

// ===== RSVPS =====
export async function get_event_rsvps(event_id) {
        return api_get(`/events/events/${event_id}/rsvps/`, {}) // Dynamic auth
}

export async function get_my_rsvps(params = {}) {
        return api_get('/events/rsvps/', params) // Dynamic auth
}

export async function get_payments_by_event(event_id) {
        return api_get(`/payments/transactions/event_payment_status/?event_id=${event_id}`) // Dynamic auth
}

export async function create_rsvp(data) {
        // data: { event: id, guests, note }
        return api_post('/events/rsvps/', data) // Dynamic auth
}

export async function update_rsvp(rsvp_id, data) {
        return api_patch(`/events/rsvps/${rsvp_id}/`, data) // Dynamic auth
}

export async function delete_rsvp(rsvp_id) {
        return api_delete(`/events/rsvps/${rsvp_id}/`) // Dynamic auth
}

// ===== PAYMENTS =====
export async function get_payment_methods(params = {}) {
        return api_get('/payments/payment-methods/', params) // Dynamic auth
}

export async function get_my_transactions(params = {}) {
	return api_get('/payments/transactions/my_transactions/', params) // Dynamic auth
}

export async function get_payments_by_order(order_id, status = 'successful') {
	return api_get(`/payments/transactions/by_order/?order_id=${order_id}&status=${status}`) // Dynamic auth
}

export async function initiate_payment(data) {
        // data includes: transaction_type, amount, currency, description, order_id|event_id, payment_details, payment_method_id
        return api_post('/payments/transactions/initiate_payment/', data) // Dynamic auth
}

export async function complete_mobile_money_payment(payment_data) {
        // payment_data includes: customer_data, mobile_money_data, charge_data, order_id
        return api_post('/payments/flutterwave/complete_mobile_money_payment/', payment_data) // Dynamic auth
}

export async function verify_payment(transaction_id) {
        return api_post(`/payments/transactions/${transaction_id}/verify_payment/`, {}) // Dynamic auth
}

// ===== DELIVERIES =====
export async function get_deliveries(params = {}) {
	return api_get('/orders/delivery-tracking/deliverable_orders/', params)
}

export async function get_my_deliveries(params = {}) {
	return api_get('/orders/delivery-tracking/active_deliveries/', params)
}

export async function track_delivery(order_number) {
	return api_get(`/orders/delivery-tracking/track_by_order_number/?order_number=${order_number}`)
}

export async function get_delivery_stats() {
	return api_get('/orders/delivery-tracking/delivery_stats/')
}

export async function get_delivery_instructions() {
	return api_get('/orders/delivery-tracking/deliverable_orders/')
}

export async function save_delivery_instructions(instructions) {
	return api_post('/orders/delivery-tracking/deliverable_orders/', instructions)
}

// ===== NOTIFICATIONS =====
export async function get_notifications(params = {}) {
	return api_get('/notifications/', params)
}

export async function mark_notification_read(notification_id) {
	return api_post(`/notifications/${notification_id}/mark_read/`)
}

export async function mark_all_notifications_read() {
	return api_post('/notifications/mark_all_read/')
}

export async function register_push_token(token, platform = 'web') {
	return api_post('/notifications/register/', { token, platform })
}

// ===== ANALYTICS =====
export async function track_event(event_type, event_data = {}) {
	return api_post('/analytics/events/', {
		event_type,
		event_data
	})
}

export async function get_user_metrics(params = {}) {
	return api_get('/analytics/user-metrics/', params)
}

export async function get_product_metrics(params = {}) {
	return api_get('/analytics/product-metrics/', params)
}

export async function get_order_metrics(params = {}) {
	return api_get('/analytics/order-metrics/', params)
}

export async function get_delivery_metrics(params = {}) {
	return api_get('/analytics/delivery-metrics/', params)
}

export async function get_revenue_metrics(params = {}) {
	return api_get('/analytics/revenue-metrics/', params)
}

export async function get_search_analytics(params = {}) {
	return api_get('/analytics/search-analytics/', params)
}

export async function get_dashboard_data(params = {}) {
	return api_get('/analytics/dashboard/', params)
}

// ===== NEWSLETTER =====
export async function create_newsletter_subscription(email) {
	return api_post('/newsletter/subscriptions/', { email })
}

export async function get_newsletter_campaigns(params = {}) {
	return api_get('/newsletter/campaigns/', params)
}

// ===== MOBILE CONFIG =====
export async function get_mobile_config() {
	return api_get('/mobile/config/')
}
