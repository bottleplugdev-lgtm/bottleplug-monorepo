import { defineStore } from 'pinia'
import { get_payment_methods, get_my_transactions, initiate_payment, verify_payment } from '../services/api'

export const use_payments_store = defineStore('payments_store', {
	state: () => ({
		payment_methods: [],
		transactions: [],
		current_transaction: null,
		is_loading: false,
		error_message: '',
		next_page_url: null,
		_cache: new Map()
	}),
	
	getters: {
		total_transactions: (state) => state.transactions.length,
		successful_transactions: (state) => state.transactions.filter(t => t.status === 'successful'),
		pending_transactions: (state) => state.transactions.filter(t => t.status === 'pending'),
		failed_transactions: (state) => state.transactions.filter(t => t.status === 'failed'),
		saved_payment_methods: (state) => state.payment_methods.filter(m => m.is_saved)
	},
	
	actions: {
		async fetch_payment_methods(params = {}) {
			try {
				this.is_loading = true
				const data = await get_payment_methods(params)
				this.payment_methods = data?.results || data || []
			} catch (error) {
				console.error('Failed to fetch payment methods:', error)
				this.error_message = 'Failed to load payment methods'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async fetch_transactions(params = {}) {
			try {
				this.is_loading = true
				const cache_key = JSON.stringify(params || {})
				
				if (this._cache.has(cache_key)) {
					const cached = this._cache.get(cache_key)
					this.transactions = cached.transactions
					this.next_page_url = cached.next_page_url
					return
				}
				
				const data = await get_my_transactions(params)
				const list = data?.results || data || []
				
				this.transactions = list
				this.next_page_url = data?.next || ''
				
				// Cache the result
				this._cache.set(cache_key, {
					transactions: list,
					next_page_url: this.next_page_url
				})
				
			} catch (error) {
				console.error('Failed to fetch transactions:', error)
				this.error_message = 'Failed to load transactions'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async initiate_payment(payment_data) {
			try {
				this.is_loading = true
				const transaction = await initiate_payment(payment_data)
				this.current_transaction = transaction
				return transaction
			} catch (error) {
				console.error('Failed to initiate payment:', error)
				this.error_message = 'Failed to initiate payment'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async verify_payment(transaction_id) {
			try {
				this.is_loading = true
				const result = await verify_payment(transaction_id)
				
				// Update the current transaction if it matches
				if (this.current_transaction && this.current_transaction.id === transaction_id) {
					this.current_transaction = result
				}
				
				// Refresh transactions list
				await this.fetch_transactions()
				
				return result
			} catch (error) {
				console.error('Failed to verify payment:', error)
				this.error_message = 'Failed to verify payment'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async load_more_transactions() {
			if (!this.next_page_url) return
			
			try {
				this.is_loading = true
				const data = await get_my_transactions({ page: this.next_page_url })
				const new_transactions = data?.results || []
				
				this.transactions.push(...new_transactions)
				this.next_page_url = data?.next || ''
				
			} catch (error) {
				console.error('Failed to load more transactions:', error)
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		clear_cache() {
			this._cache.clear()
		},
		
		clear_current_transaction() {
			this.current_transaction = null
		},
		
		get_transaction_by_id(transaction_id) {
			return this.transactions.find(t => t.id === transaction_id)
		},
		
		get_payment_method_by_id(method_id) {
			return this.payment_methods.find(m => m.id === method_id)
		}
	}
}) 