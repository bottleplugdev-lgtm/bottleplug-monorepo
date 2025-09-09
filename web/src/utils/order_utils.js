/**
 * Order utility functions for calculating balances and payment status
 */

/**
 * Calculate outstanding balance for an order
 * @param {Object} order - Order object
 * @param {Array} payments - Array of payment transactions for the order (deprecated, will use API call)
 * @returns {Object} - { outstanding_balance, is_fully_paid, paid_amount }
 */
export async function calculate_order_balance(order) {
	if (!order || !order.total_amount) {
		return {
			outstanding_balance: 0,
			is_fully_paid: true,
			paid_amount: 0
		}
	}

	const total_amount = Number(order.total_amount) || 0
	const order_id = order.id
	
	console.log(`=== CALCULATING BALANCE FOR ORDER ${order_id} ===`)
	console.log('Order total amount:', total_amount)
	
	try {
		// Use the new endpoint to get payments for this specific order
		const { get_payments_by_order } = await import('../services/api')
		const response = await get_payments_by_order(order_id, 'successful')
		
		console.log('Payments API response:', response)
		
		if (!response.success) {
			console.error('Failed to fetch payments for order:', response.error)
			return {
				outstanding_balance: total_amount,
				is_fully_paid: false,
				paid_amount: 0
			}
		}
		
		const paid_amount = Number(response.total_paid) || 0
		const payment_count = response.payment_count || 0
		
		console.log(`Order ${order_id} - Found ${payment_count} successful payments, total paid: ${paid_amount}`)
		
		// Calculate outstanding balance
		const outstanding_balance = Math.max(0, total_amount - paid_amount)
		
		// Check if fully paid
		const is_fully_paid = outstanding_balance <= 0
		
		console.log(`Order ${order_id} final calculation:`, {
			total_amount,
			paid_amount,
			outstanding_balance,
			is_fully_paid,
			payment_count
		})
		console.log(`=== END CALCULATION FOR ORDER ${order_id} ===`)
		
		return {
			outstanding_balance,
			is_fully_paid,
			paid_amount
		}
		
	} catch (error) {
		console.error(`Error calculating balance for order ${order_id}:`, error)
		return {
			outstanding_balance: total_amount,
			is_fully_paid: false,
			paid_amount: 0
		}
	}
}

/**
 * Format balance display text - matches dashboard approach
 * @param {number} outstanding_balance - Outstanding balance amount
 * @param {boolean} is_fully_paid - Whether order is fully paid
 * @returns {string} - Formatted balance text
 */
export function format_balance_display(outstanding_balance, is_fully_paid) {
	const amount = Number(outstanding_balance) || 0
	return new Intl.NumberFormat('en-UG', {
		style: 'currency',
		currency: 'UGX',
		minimumFractionDigits: 0
	}).format(amount)
}

/**
 * Get balance status class for styling
 * @param {boolean} is_fully_paid - Whether order is fully paid
 * @returns {string} - CSS class name
 */
export function get_balance_status_class(is_fully_paid) {
	return is_fully_paid ? 'balance_cleared' : 'balance_outstanding'
}

/**
 * Get payment status text
 * @param {Object} order - Order object
 * @param {Array} payments - Array of payment transactions
 * @returns {string} - Payment status text
 */
export function get_payment_status_text(order, payments = []) {
	const { is_fully_paid, paid_amount } = calculate_order_balance(order, payments)
	
	if (is_fully_paid) {
		return 'Fully Paid'
	}
	
	if (paid_amount > 0) {
		return 'Partially Paid'
	}
	
	return 'Unpaid'
}

/**
 * Get payment status class for styling
 * @param {Object} order - Order object
 * @param {Array} payments - Array of payment transactions
 * @returns {string} - CSS class name
 */
export function get_payment_status_class(order, payments = []) {
	const { is_fully_paid, paid_amount } = calculate_order_balance(order, payments)
	
	if (is_fully_paid) {
		return 'payment_status_paid'
	}
	
	if (paid_amount > 0) {
		return 'payment_status_partial'
	}
	
	return 'payment_status_unpaid'
}
