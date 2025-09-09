import { defineStore } from 'pinia'
import { get_orders, get_my_orders, get_order, get_order_stats } from '../services/api'
import { calculate_order_balance, format_balance_display, get_payment_status_text, get_payment_status_class } from '../utils/order_utils'

export const use_orders_store = defineStore('orders_store', {
	state: () => ({
		orders: [],
		current_order: null,
		order_stats: null,
		orders_with_balance: [], // Store calculated orders with balance
		is_loading: false,
		error_message: '',
		next_page_url: null,
		_cache: new Map()
	}),
	
	getters: {
		total_orders: (state) => state.orders.length,
		pending_orders: (state) => state.orders.filter(order => order.status === 'pending'),
		processing_orders: (state) => state.orders.filter(order => order.status === 'processing'),
		shipped_orders: (state) => state.orders.filter(order => order.status === 'shipped'),
		delivered_orders: (state) => state.orders.filter(order => order.status === 'delivered'),
		cancelled_orders: (state) => state.orders.filter(order => order.status === 'cancelled'),
		
		// Get orders with outstanding balances
		orders_with_outstanding_balance: (state) => {
			return state.orders_with_balance.filter(order => !order.is_fully_paid)
		},
		
		// Get fully paid orders
		fully_paid_orders: (state) => {
			return state.orders_with_balance.filter(order => order.is_fully_paid)
		}
	},
	
	actions: {
		async fetch_orders(params = {}) {
			try {
				this.is_loading = true
				const cache_key = JSON.stringify(params || {})
				
				if (this._cache.has(cache_key)) {
					const cached = this._cache.get(cache_key)
					this.orders = cached.orders
					this.next_page_url = cached.next_page_url
					return
				}
				
				const data = await get_orders(params)
				const list = data?.results || data || []
				
				this.orders = list
				this.next_page_url = data?.next || ''
				
				// Cache the result
				this._cache.set(cache_key, {
					orders: list,
					next_page_url: this.next_page_url
				})
				
				// Calculate balances for all orders
				await this.calculate_all_order_balances()
				
			} catch (error) {
				console.error('Failed to fetch orders:', error)
				this.error_message = 'Failed to load orders'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async fetch_my_orders(params = {}) {
			try {
				this.is_loading = true
				const data = await get_my_orders(params)
				const list = data?.results || data || []
				
				this.orders = list
				this.next_page_url = data?.next || ''
				
				// Calculate balances for all orders
				await this.calculate_all_order_balances()
				
			} catch (error) {
				console.error('Failed to fetch my orders:', error)
				this.error_message = 'Failed to load your orders'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async fetch_order(order_id) {
			try {
				const order = await get_order(order_id)
				this.current_order = order
				return order
			} catch (error) {
				console.error('Failed to fetch order:', error)
				this.error_message = 'Failed to load order details'
				throw error
			}
		},
		
		async fetch_order_stats() {
			try {
				const stats = await get_order_stats()
				this.order_stats = stats
				return stats
			} catch (error) {
				console.error('Failed to fetch order stats:', error)
				throw error
			}
		},
		
		// Calculate balance for all orders
		async calculate_all_order_balances() {
			console.log('=== CALCULATING BALANCES FOR ALL ORDERS ===')
			const orders_with_balance = []
			
			for (const order of this.orders) {
				try {
					const { outstanding_balance, is_fully_paid, paid_amount } = await calculate_order_balance(order)
					
					orders_with_balance.push({
						...order,
						outstanding_balance,
						is_fully_paid,
						paid_amount,
						balance_display: format_balance_display(outstanding_balance, is_fully_paid),
						payment_status_text: get_payment_status_text(order, []), // Pass empty array since we're using API
						payment_status_class: get_payment_status_class(order, []) // Pass empty array since we're using API
					})
				} catch (error) {
					console.error(`Failed to calculate balance for order ${order.id}:`, error)
					// Add order with default values
					orders_with_balance.push({
						...order,
						outstanding_balance: order.total_amount,
						is_fully_paid: false,
						paid_amount: 0,
						balance_display: format_balance_display(order.total_amount, false),
						payment_status_text: 'Unpaid',
						payment_status_class: 'payment_status_unpaid'
					})
				}
			}
			
			this.orders_with_balance = orders_with_balance
			console.log('=== END CALCULATING BALANCES ===')
		},
		
		// Get balance information for a specific order
		async get_order_balance(order_id) {
			const order = this.orders.find(o => o.id === order_id)
			if (!order) {
				throw new Error(`Order ${order_id} not found`)
			}
			
			return await calculate_order_balance(order)
		},
		
		clear_cache() {
			this._cache.clear()
		}
	}
}) 