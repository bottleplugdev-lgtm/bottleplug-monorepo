import { defineStore } from 'pinia'
import { get_events, get_event, get_event_rsvps, get_my_rsvps, get_payments_by_event, create_rsvp, update_rsvp, delete_rsvp } from '../services/api'

export const use_events_store = defineStore('events_store', {
	state: () => ({
		events: [],
		current_event: null,
		my_rsvps: [],
		is_loading: false,
		error_message: '',
		next_page_url: null,
		_cache: new Map()
	}),
	
	getters: {
		total_events: (state) => state.events.length,
		upcoming_events: (state) => state.events.filter(event => event.status === 'upcoming'),
		ongoing_events: (state) => state.events.filter(event => event.status === 'ongoing'),
		completed_events: (state) => state.events.filter(event => event.status === 'completed'),
		cancelled_events: (state) => state.events.filter(event => event.status === 'cancelled'),
		my_upcoming_rsvps: (state) => state.my_rsvps.filter(rsvp => rsvp.event?.status === 'upcoming'),
		my_ongoing_rsvps: (state) => state.my_rsvps.filter(rsvp => rsvp.event?.status === 'ongoing')
	},
	
	actions: {
		async fetch_events(params = {}) {
			try {
				this.is_loading = true
				const cache_key = JSON.stringify(params || {})
				
				if (this._cache.has(cache_key)) {
					const cached = this._cache.get(cache_key)
					this.events = cached.events
					this.next_page_url = cached.next_page_url
					return
				}
				
				const data = await get_events(params)
				const list = data?.results || data || []
				
				this.events = list
				this.next_page_url = data?.next || ''
				
				// Cache the result
				this._cache.set(cache_key, {
					events: list,
					next_page_url: this.next_page_url
				})
				
			} catch (error) {
				console.error('Failed to fetch events:', error)
				this.error_message = 'Failed to load events'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async fetch_event(event_id) {
			try {
				this.is_loading = true
				const event = await get_event(event_id)
				this.current_event = event
				return event
			} catch (error) {
				console.error('Failed to fetch event:', error)
				this.error_message = 'Failed to load event details'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async fetch_my_rsvps(params = {}) {
			try {
				this.is_loading = true
				const data = await get_my_rsvps(params)
				this.my_rsvps = data?.results || data || []
			} catch (error) {
				console.error('Failed to fetch my RSVPs:', error)
				this.error_message = 'Failed to load RSVPs'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async create_rsvp(rsvp_data) {
			try {
				this.is_loading = true
				const rsvp = await create_rsvp(rsvp_data)
				
				// Add to my RSVPs list
				this.my_rsvps.push(rsvp)
				
				// Update event capacity if it's the current event
				if (this.current_event && this.current_event.id === rsvp_data.event) {
					this.current_event.current_capacity = (this.current_event.current_capacity || 0) + 1
				}
				
				return rsvp
			} catch (error) {
				console.error('Failed to create RSVP:', error)
				this.error_message = 'Failed to create RSVP'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async update_rsvp(rsvp_id, rsvp_data) {
			try {
				this.is_loading = true
				const updated_rsvp = await update_rsvp(rsvp_id, rsvp_data)
				
				// Update in my RSVPs list
				const index = this.my_rsvps.findIndex(r => r.id === rsvp_id)
				if (index !== -1) {
					this.my_rsvps[index] = updated_rsvp
				}
				
				return updated_rsvp
			} catch (error) {
				console.error('Failed to update RSVP:', error)
				this.error_message = 'Failed to update RSVP'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async delete_rsvp(rsvp_id) {
			try {
				this.is_loading = true
				await delete_rsvp(rsvp_id)
				
				// Remove from my RSVPs list
				this.my_rsvps = this.my_rsvps.filter(r => r.id !== rsvp_id)
				
				// Update event capacity if it's the current event
				const removed_rsvp = this.my_rsvps.find(r => r.id === rsvp_id)
				if (removed_rsvp && this.current_event && this.current_event.id === removed_rsvp.event) {
					this.current_event.current_capacity = Math.max(0, (this.current_event.current_capacity || 0) - 1)
				}
				
				return true
			} catch (error) {
				console.error('Failed to delete RSVP:', error)
				this.error_message = 'Failed to delete RSVP'
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		async load_more_events() {
			if (!this.next_page_url) return
			
			try {
				this.is_loading = true
				const data = await get_events({ page: this.next_page_url })
				const new_events = data?.results || []
				
				this.events.push(...new_events)
				this.next_page_url = data?.next || ''
				
			} catch (error) {
				console.error('Failed to load more events:', error)
				throw error
			} finally {
				this.is_loading = false
			}
		},
		
		clear_cache() {
			this._cache.clear()
		},
		
		clear_current_event() {
			this.current_event = null
		},
		
		get_event_by_id(event_id) {
			return this.events.find(e => e.id === event_id)
		},
		
		get_rsvp_by_event_id(event_id) {
			return this.my_rsvps.find(r => r.event === event_id || r.event?.id === event_id)
		},
		
		has_rsvp_for_event(event_id) {
			return this.my_rsvps.some(r => r.event === event_id || r.event?.id === event_id)
		},
		
		async has_paid_for_event(event_id) {
			try {
				console.log(`🔍 Checking payment status for event ${event_id}`)
				const response = await get_payments_by_event(event_id)
				console.log(`🔍 Payment response for event ${event_id}:`, response)
				
				// The new endpoint returns { success: true, has_paid: boolean, ... }
				const hasPaid = response?.success && response?.has_paid === true
				console.log(`🔍 Event ${event_id} has paid:`, hasPaid)
				return hasPaid
			} catch (error) {
				console.warn('Could not check payment status for event:', error)
				return false
			}
		}
	}
}) 