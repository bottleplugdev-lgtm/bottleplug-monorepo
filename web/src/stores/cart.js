import { defineStore } from 'pinia'
import { get_cart, add_to_cart, update_cart_item, remove_cart_item, clear_cart, checkout_cart } from '../services/api'

export const use_cart_store = defineStore('cart_store', {
	state: () => ({
		items: [],
		is_loading: false,
		error_message: '',
		_cache: new Map()
	}),
	
	getters: {
		total_quantity(state) {
			return state.items.reduce((sum, item) => sum + (item.quantity || 0), 0)
		},
		total_amount(state) {
			return state.items.reduce((sum, item) => {
				// Calculate item total: use subtotal/total_price if available, otherwise calculate unit_price * quantity
				const item_total = item.subtotal || item.total_price || (item.unit_price * item.quantity) || 0
				return sum + Number(item_total)
			}, 0)
		},
		is_empty(state) {
			return state.items.length === 0
		},
		item_count(state) {
			return state.items.length
		}
	},
	
	actions: {
		async fetch_cart() {
			try {
				this.is_loading = true
				const data = await get_cart()
				this.items = data?.results || data?.items || data || []
				console.log('Cart fetched successfully:', this.items.length, 'items')
			} catch (error) {
				console.error('Failed to fetch cart:', error)
				this.error_message = 'Failed to load cart'
				// If it's an authentication error, don't throw - just set empty cart
				if (error.response?.status === 401 || error.response?.status === 403) {
					console.log('User not authenticated, setting empty cart')
					this.items = []
				} else {
					throw error
				}
			} finally {
				this.is_loading = false
			}
		},
		
		clear_cart_state() {
			this.items = []
			this.error_message = ''
			console.log('Cart state cleared')
		},
		
		async add_item({ product, quantity = 1, variant = null }) {
			try {
				await add_to_cart({ product, quantity, variant })
				await this.fetch_cart()
				return true
			} catch (error) {
				console.error('Failed to add item to cart:', error)
				this.error_message = 'Failed to add item to cart'
				throw error
			}
		},
		
		async update_item(item_id, payload) {
			try {
				await update_cart_item(item_id, payload)
				await this.fetch_cart()
				return true
			} catch (error) {
				console.error('Failed to update cart item:', error)
				this.error_message = 'Failed to update cart item'
				throw error
			}
		},
		
		async remove_item(item_id) {
			try {
				await remove_cart_item(item_id)
				await this.fetch_cart()
				return true
			} catch (error) {
				console.error('Failed to remove cart item:', error)
				this.error_message = 'Failed to remove cart item'
				throw error
			}
		},
		
		async clear() {
			try {
				await clear_cart()
				await this.fetch_cart()
				return true
			} catch (error) {
				console.error('Failed to clear cart:', error)
				this.error_message = 'Failed to clear cart'
				throw error
			}
		},
		
		async checkout(payload = {}) {
			try {
				const result = await checkout_cart(payload)
				// Clear cart after successful checkout
				await this.fetch_cart()
				return result
			} catch (error) {
				console.error('Failed to checkout:', error)
				this.error_message = 'Failed to checkout'
				throw error
			}
		},
		
		clear_cache() {
			this._cache.clear()
		},
		
		get_item_by_product_id(product_id) {
			return this.items.find(item => item.product === product_id || item.product?.id === product_id)
		},
		
		is_product_in_cart(product_id) {
			return this.items.some(item => item.product === product_id || item.product?.id === product_id)
		},
		
		// Helper function to calculate item total
		get_item_total(item) {
			return item.subtotal || item.total_price || (item.unit_price * item.quantity) || 0
		}
	}
})

