// Mock Analytics Service - No API calls to prevent errors

class AnalyticsService {
	constructor() {
		this.session_id = 'mock-session-' + Date.now()
		this.session_start_time = Date.now()
		this.page_views = []
		this.user_actions = []
		this.is_initialized = true
	}

	// Mock initialization - does nothing
	async init() {
		console.log('Mock analytics initialized (no API calls)')
	}

	// Mock tracking methods - do nothing
	async track_page_view(data = {}) {
		console.log('Mock: track_page_view', data)
	}

	async track_user_action(action, data = {}) {
		console.log('Mock: track_user_action', action, data)
	}

	async track_event(event_type, data = {}) {
		console.log('Mock: track_event', event_type, data)
	}

	async track_add_to_cart(product_id, product_name, quantity, price) {
		console.log('Mock: track_add_to_cart', product_id, product_name, quantity, price)
	}

	async track_product_search(query) {
		console.log('Mock: track_product_search', query)
	}

	async track_user_login(method = 'email') {
		console.log('Mock: track_user_login', method)
	}

	async track_user_logout() {
		console.log('Mock: track_user_logout')
	}

	async track_payment_initiated(amount, currency, payment_method) {
		console.log('Mock: track_payment_initiated', amount, currency, payment_method)
	}

	async track_payment_completed(transaction_id, amount, currency) {
		console.log('Mock: track_payment_completed', transaction_id, amount, currency)
	}

	async track_payment_failed(amount, currency, error_reason) {
		console.log('Mock: track_payment_failed', amount, currency, error_reason)
	}

	async track_add_to_wishlist(product_id, product_name) {
		console.log('Mock: track_add_to_wishlist', product_id, product_name)
	}

	async track_remove_from_wishlist(product_id, product_name) {
		console.log('Mock: track_remove_from_wishlist', product_id, product_name)
	}

	async track_event_view(event_id, event_name) {
		console.log('Mock: track_event_view', event_id, event_name)
	}

	async track_rsvp_event(event_id, event_name, guests_count = 1) {
		console.log('Mock: track_rsvp_event', event_id, event_name, guests_count)
	}

	async track_coupon_applied(coupon_code, discount_amount) {
		console.log('Mock: track_coupon_applied', coupon_code, discount_amount)
	}

	// Get analytics summary
	get_session_summary() {
		return {
			session_id: this.session_id,
			duration_ms: Date.now() - this.session_start_time,
			page_views_count: this.page_views.length,
			user_actions_count: this.user_actions.length,
			page_views: this.page_views,
			user_actions: this.user_actions
		}
	}
}

// Create singleton instance
export const analytics = new AnalyticsService()

// Export for manual initialization if needed
export default analytics 