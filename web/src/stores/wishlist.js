import { defineStore } from 'pinia'
import { get_wishlist, add_to_wishlist, remove_wishlist_item, move_wishlist_to_cart } from '../services/api'

export const use_wishlist_store = defineStore('wishlist_store', {
	state: () => ({
		items: [],
		is_loading: false,
		error_message: '',
		next_page_url: null,
		_cache: new Map()
	}),
	
	getters: {
		total_items: (state) => state.items.length,
		is_empty: (state) => state.items.length === 0
	},
	
	actions: {
		async fetch_wishlist(params = {}) {
			try {
				this.is_loading = true
				const cache_key = JSON.stringify(params || {})
				
				if (this._cache.has(cache_key)) {
					const cached = this._cache.get(cache_key)
					this.items = cached.items
					this.next_page_url = cached.next_page_url
					return
				}
				
				const data = await get_wishlist(params)
				const list = data?.results || data || []
				
				this.items = list
				this.next_page_url = data?.next || ''
				
				// Cache the result
				this._cache.set(cache_key, {
					items: list,
					next_page_url: this.next_page_url
				})
				
			} catch (error) {
				console.error('Failed to fetch wishlist:', error)
				this.error_message = 'Failed to load wishlist'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async add_item(product_id) {
			try {
				await add_to_wishlist({ product: product_id })
				await this.fetch_wishlist() // Refresh the list
				return true
			} catch (error) {
				console.error('Failed to add item to wishlist:', error)
				this.error_message = 'Failed to add item to wishlist'
				throw error
			}
		},
		
		async remove_item(item_id) {
			try {
				await remove_wishlist_item(item_id)
				await this.fetch_wishlist() // Refresh the list
				return true
			} catch (error) {
				console.error('Failed to remove item from wishlist:', error)
				this.error_message = 'Failed to remove item from wishlist'
				throw error
			}
		},
		
		async move_to_cart(wishlist_id) {
			try {
				await move_wishlist_to_cart(wishlist_id)
				await this.fetch_wishlist() // Refresh the list
				return true
			} catch (error) {
				console.error('Failed to move item to cart:', error)
				this.error_message = 'Failed to move item to cart'
				throw error
			}
		},
		
		async clear_all() {
			try {
				// Remove all items one by one
				const removePromises = this.items.map(item => 
					remove_wishlist_item(item.id)
				)
				await Promise.all(removePromises)
				this.items = []
				return true
			} catch (error) {
				console.error('Failed to clear wishlist:', error)
				this.error_message = 'Failed to clear wishlist'
				throw error
			}
		},
		
		async load_more() {
			if (!this.next_page_url) return
			
			try {
				this.is_loading = true
				const data = await get_wishlist({ page: this.next_page_url })
				const new_items = data?.results || []
				
				this.items.push(...new_items)
				this.next_page_url = data?.next || ''
				
			} catch (error) {
				console.error('Failed to load more wishlist items:', error)
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		clear_cache() {
			this._cache.clear()
		},
		
		is_in_wishlist(product_id) {
			return this.items.some(item => item.product === product_id || item.product?.id === product_id)
		}
	}
}) 