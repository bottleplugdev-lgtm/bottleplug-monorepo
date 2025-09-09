import { defineStore } from 'pinia'
import { get_products, get_categories, get_featured_products, api_get_url } from '../services/api'

export const use_products_store = defineStore('products_store', {
	state: () => ({
		products: [],
		next_page_url: '',
		categories: [],
		is_loading: false,
		error_message: '',
		_cache: new Map()
	}),
	actions: {
		async fetch_categories() {
			try {
				this.is_loading = true
				const data = await get_categories()
				this.categories = data?.results || data || []
			} catch (e) {
				this.error_message = 'failed to load categories'
			} finally {
				this.is_loading = false
			}
		},
		async fetch_products(params = {}) {
			try {
				this.is_loading = true
				const cache_key = JSON.stringify(params || {})
				if (this._cache.has(cache_key)) {
					const cached = this._cache.get(cache_key)
					this.products = cached.products
					this.next_page_url = cached.next_page_url
					return
				}
				const data = await get_products(params)
				const list = data?.results || data || []
				this.products = list
				this.next_page_url = data?.next || ''
				this._cache.set(cache_key, { products: list, next_page_url: this.next_page_url, ts: Date.now() })
			} catch (e) {
				this.error_message = 'failed to load products'
			} finally {
				this.is_loading = false
			}
		},
		async load_more() {
			if (!this.next_page_url) return
			try {
				this.is_loading = true
				const data = await api_get_url(this.next_page_url)
				const list = data?.results || []
				this.products = [...this.products, ...list]
				this.next_page_url = data?.next || ''
			} finally {
				this.is_loading = false
			}
		},
		async fetch_featured_products() {
			try {
				this.is_loading = true
				const data = await get_featured_products()
				this.products = data?.results || data || []
			} catch (e) {
				this.error_message = 'failed to load featured products'
			} finally {
				this.is_loading = false
			}
		}
	}
})
