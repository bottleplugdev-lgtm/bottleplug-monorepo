<template>
	<div class="event_detail_page">
		<!-- Loading State -->
		<div v-if="is_loading" class="loading_state">
			<div class="loading_spinner"></div>
			<p class="loading_text">Loading event details...</p>
		</div>

		<!-- Event Not Found -->
		<div v-else-if="!event" class="not_found">
			<div class="not_found_icon">🎉</div>
			<h2 class="not_found_title">Event Not Found</h2>
			<p class="not_found_text">The event you're looking for doesn't exist or has been removed.</p>
			<RouterLink to="/events" class="back_to_events_btn">
				<span class="btn_icon">🎪</span>
				Back to Events
			</RouterLink>
		</div>

		<!-- Event Details -->
		<div v-else class="event_detail_content">
			<!-- Breadcrumb -->
			<nav class="breadcrumb">
				<RouterLink to="/" class="breadcrumb_link">Home</RouterLink>
				<span class="breadcrumb_separator">/</span>
				<RouterLink to="/events" class="breadcrumb_link">Events</RouterLink>
				<span class="breadcrumb_separator">/</span>
				<span class="breadcrumb_current">{{ event.title }}</span>
			</nav>

			<!-- Event Main Section -->
			<div class="event_main">
				<!-- Event Image -->
				<div class="event_image_section">
					<div class="event_image_container">
						<img 
							:src="image_url(event.image)" 
							:alt="event.title" 
							class="event_image" 
							loading="lazy" 
							@error="handle_image_error"
						/>
						<div class="event_badge" :class="get_event_status_class(event.status)">
							{{ event.status || 'Upcoming' }}
						</div>
						<div class="event_type_badge">
							{{ event.event_type || 'Event' }}
						</div>
					</div>
				</div>

				<!-- Event Info -->
				<div class="event_info">
					<div class="event_header">
						<h1 class="event_title">{{ event.title }}</h1>
						<div class="event_meta">
							<div class="event_date_time">
								<span class="date_icon">📅</span>
								<span class="date_text">{{ format_date(event.start_date) }}</span>
							</div>
							<div class="event_time" v-if="event.start_date">
								<span class="time_icon">🕐</span>
								<span class="time_text">{{ format_time(event.start_date) }}</span>
							</div>
						</div>
					</div>

					<div class="event_location" v-if="event.location_name">
						<div class="location_icon">📍</div>
						<div class="location_details">
							<h3 class="location_name">{{ event.location_name }}</h3>
							<p v-if="event.address" class="location_address">{{ event.address }}</p>
							<p v-if="event.city" class="location_city">{{ event.city }}{{ event.state ? ', ' + event.state : '' }}</p>
						</div>
					</div>

					<div class="event_pricing" v-if="event.price !== undefined">
						<div class="price_display">
							<span v-if="event.price === 0" class="free_price">Free Event</span>
							<span v-else class="ticket_price">{{ format_price(event.price) }}</span>
							<span v-if="event.member_price && event.member_price < event.price" class="member_price">Member Price: {{ format_price(event.member_price) }}</span>
						</div>
					</div>

					<div class="event_capacity" v-if="event.max_capacity">
						<div class="capacity_info">
							<span class="capacity_icon">👥</span>
							<span class="capacity_text">{{ event.current_attendees || 0 }} / {{ event.max_capacity }} attendees</span>
						</div>
						<div class="capacity_bar">
							<div class="capacity_fill" :style="{ width: capacity_percentage + '%' }"></div>
						</div>
					</div>

					<div class="event_description" v-if="event.description">
						<h3 class="description_title">About This Event</h3>
						<p class="description_text">{{ event.description }}</p>
					</div>

					<!-- RSVP Section -->
					<div class="rsvp_section">
						<div class="rsvp_header">
							<h3 class="rsvp_title">
								<span class="title_icon">🎫</span>
								RSVP for This Event
							</h3>
						</div>

						<div class="rsvp_form">
							<div class="guest_count_selector">
								<label class="guest_label">Number of Guests</label>
								<div class="guest_controls">
									<button 
										class="guest_btn" 
										@click="guest_count = Math.max(1, guest_count - 1)"
										:disabled="guest_count <= 1"
									>-</button>
									<input 
										type="number" 
										min="1" 
										:max="event.max_capacity - (event.current_attendees || 0)"
										v-model.number="guest_count" 
										class="guest_input" 
									/>
									<button 
										class="guest_btn" 
										@click="guest_count++"
										:disabled="guest_count >= (event.max_capacity - (event.current_attendees || 0))"
									>+</button>
								</div>
							</div>

							<div class="rsvp_actions">
								<button 
									class="rsvp_btn" 
									:class="{ 'paid_btn': has_paid, 'confirmed_btn': has_rsvped && !has_paid }"
									@click="rsvp_event()" 
									:disabled="is_rsvping || !can_rsvp || has_paid"
								>
									<span v-if="is_rsvping" class="btn_spinner"></span>
									<span v-else class="btn_icon">{{ rsvp_button_icon }}</span>
									{{ rsvp_button_text }}
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Event Payment Modal -->
	<div v-if="show_payment_modal" class="modal_overlay" @click="close_payment_modal">
		<div class="modal_content" @click.stop>
			<div class="modal_header">
				<h3>Pay for Event: {{ event?.title }}</h3>
				<button @click="close_payment_modal" class="modal_close">×</button>
			</div>
			
			<div v-if="event" class="modal_body">
				<div class="event_payment_summary">
					<div class="summary_item">
						<span class="summary_label">Event:</span>
						<span class="summary_value">{{ event.title }}</span>
					</div>
					<div class="summary_item">
						<span class="summary_label">Guests:</span>
						<span class="summary_value">{{ guest_count }}</span>
					</div>
					<div class="summary_item">
						<span class="summary_label">Price per ticket:</span>
						<span class="summary_value">{{ format_price(event.price) }}</span>
					</div>
					<div class="summary_item total_item">
						<span class="summary_label">Total Amount:</span>
						<span class="summary_value">{{ format_price(event.price * guest_count) }}</span>
					</div>
				</div>

				<div class="payment_form">
					<h4 class="form_title">Mobile Money Payment</h4>
					
					<div class="form_group">
						<label class="form_label">Network</label>
						<select v-model="mm_network" class="form_select">
							<option value="MTN">MTN Mobile Money</option>
							<option value="AIRTEL">Airtel Money</option>
						</select>
					</div>

					<div class="form_group">
						<label class="form_label">Phone Number</label>
						<input 
							v-model="mm_phone" 
							type="tel" 
							placeholder="e.g., 0701234567 or +256701234567"
							class="form_input"
						/>
						<small class="form_help">Enter your mobile money phone number</small>
					</div>

					<div class="payment_actions">
						<button 
							@click="close_payment_modal" 
							class="btn_cancel"
							:disabled="is_processing_payment"
						>
							Cancel
						</button>
						<button 
							@click="process_event_payment" 
							class="btn_pay"
							:disabled="is_processing_payment || !mm_phone"
						>
							<span v-if="is_processing_payment" class="btn_spinner"></span>
							<span v-else class="btn_icon">💳</span>
							{{ is_processing_payment ? 'Processing...' : 'Pay Now' }}
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { get_event, create_rsvp, complete_mobile_money_payment } from '../services/api'
import { use_auth_store } from '../stores/auth'
import { image_url as utils_image_url, get_fallback_image_url } from '../utils/image_utils'
import { use_events_store } from '../stores/events'
import { set_seo } from '../lib/seo'
import { toast_success, toast_error } from '../lib/toast'

const route = useRoute()
const router = useRouter()
const auth_store = use_auth_store()
const events_store = use_events_store()
const event = ref(null)
const is_loading = ref(true)
const guest_count = ref(1)
const is_rsvping = ref(false)
const has_paid_for_current_event = ref(false)

// Payment modal state
const show_payment_modal = ref(false)
const mm_network = ref('MTN')
const mm_phone = ref('')
const is_processing_payment = ref(false)

// Computed properties
const capacity_percentage = computed(() => {
	if (!event.value?.max_capacity) return 0
	return Math.round(((event.value.current_attendees || 0) / event.value.max_capacity) * 100)
})

const can_rsvp = computed(() => {
	if (!event.value) return false
	const available = (event.value.max_capacity || 0) - (event.value.current_attendees || 0)
	return available > 0 && event.value.status !== 'cancelled'
})

// Check if user has already RSVPed for this event
const has_rsvped = computed(() => {
	if (!event.value || !auth_store.is_ready || !auth_store.is_authenticated) return false
	return events_store.has_rsvp_for_event(event.value.id)
})

// Get the current RSVP for this event
const current_rsvp = computed(() => {
	if (!event.value || !auth_store.is_ready || !auth_store.is_authenticated) return null
	return events_store.get_rsvp_by_event_id(event.value.id)
})

// Check if user has paid for this event
const has_paid = computed(() => {
	// For free events, consider RSVP as "paid"
	if (!event.value.price || event.value.price === 0) {
		console.log(`🔍 Free event ${event.value?.id}: has_rsvped = ${has_rsvped.value}`)
		return has_rsvped.value
	}
	// For paid events, check actual payment status
	console.log(`🔍 Paid event ${event.value?.id}: has_paid_for_current_event = ${has_paid_for_current_event.value}`)
	return has_paid_for_current_event.value
})

// Get appropriate button text and icon
const rsvp_button_text = computed(() => {
	if (is_rsvping.value) return 'Processing...'
	
	if (has_rsvped.value) {
		if (has_paid.value) {
			return '✅ Payment Confirmed'
		} else if (event.value.price > 0) {
			return 'Complete Payment'
		} else {
			return '✅ RSVP Confirmed'
		}
	}
	
	// Not RSVPed yet
	if (event.value.price > 0) {
		return 'RSVP & Pay'
	} else {
		return 'RSVP Now'
	}
})

const rsvp_button_icon = computed(() => {
	if (is_rsvping.value) return '⏳'
	
	if (has_rsvped.value) {
		if (has_paid.value) {
			return '✅'
		} else if (event.value.price > 0) {
			return '💳'
		} else {
			return '✅'
		}
	}
	
	// Not RSVPed yet
	return '🎫'
})

onMounted(async () => {
	try {
		const id = route.params.id
		if (id) {
			// Load event details
			event.value = await get_event(id)
			
			// Load user's RSVPs if authenticated and auth is ready
			if (auth_store.is_ready && auth_store.is_authenticated) {
				try {
					await events_store.fetch_my_rsvps()
					
					// Check if user has paid for this event
					if (event.value.price > 0) {
						console.log(`🔍 Checking payment for event ${event.value.id} with price ${event.value.price}`)
						has_paid_for_current_event.value = await events_store.has_paid_for_event(event.value.id)
						console.log(`🔍 Payment status result for event ${event.value.id}: ${has_paid_for_current_event.value}`)
					}
				} catch (error) {
					console.warn('Could not fetch RSVPs:', error)
					// Continue without RSVPs - the UI will show default states
				}
			}
			
			set_seo({ 
				title: `${event.value.title} · BottlePlug Events`, 
				description: event.value.description || '', 
				image: image_url(event.value.image) 
			})
		}
	} finally {
		is_loading.value = false
	}
})

function image_url(path) {
	return utils_image_url(path)
}

function handle_image_error(event) {
	event.target.src = get_fallback_image_url()
}

function format_price(value) {
	const amount = Number(value) || 0
	return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', minimumFractionDigits: 0 }).format(amount)
}

function format_date(date_string) {
	if (!date_string) return 'TBD'
	const date = new Date(date_string)
	return date.toLocaleDateString('en-US', { 
		weekday: 'long',
		year: 'numeric', 
		month: 'long', 
		day: 'numeric' 
	})
}

function format_time(date_string) {
	if (!date_string) return ''
	const date = new Date(date_string)
	return date.toLocaleTimeString('en-US', { 
		hour: 'numeric',
		minute: '2-digit',
		hour12: true
	})
}

function get_event_status_class(status) {
	switch (status?.toLowerCase()) {
		case 'upcoming': return 'status_upcoming'
		case 'ongoing': return 'status_ongoing'
		case 'completed': return 'status_completed'
		case 'cancelled': return 'status_cancelled'
		default: return 'status_upcoming'
	}
}

async function rsvp_event() {
	if (!event.value || !auth_store.is_authenticated) {
		auth_store.set_intended_destination(route.fullPath)
		return router.push({ name: 'login' })
	}
	
	// If it's a free event, just RSVP
	if (!event.value.price || event.value.price === 0) {
		try {
			is_rsvping.value = true
			await create_rsvp({ 
				event: event.value.id,
				guest_count: guest_count.value
			})
			
			// Refresh RSVPs to update the UI
			try {
				await events_store.fetch_my_rsvps()
			} catch (error) {
				console.warn('Could not refresh RSVPs:', error)
			}
			
			toast_success('RSVP confirmed! We\'ll see you there.')
			
			// Track analytics
			if (window?.gtag) {
				window.gtag('event', 'rsvp', { 
					event_id: event.value.id, 
					event_title: event.value.title,
					guest_count: guest_count.value
				})
			}
		} catch (error) {
			console.error('RSVP error:', error)
			toast_error('Failed to RSVP for event')
		} finally {
			is_rsvping.value = false
		}
	} else {
		// If it's a paid event, open payment modal
		show_payment_modal.value = true
	}
}

async function process_event_payment() {
	if (!event.value || !mm_phone.value) {
		toast_error('Please enter your mobile money phone number')
		return
	}
	
	const total_amount = event.value.price * guest_count.value
	
	try {
		is_processing_payment.value = true
		
		// Prepare payment data similar to checkout
		const payment_data = {
			customer_data: {
				email: auth_store.firebase_user?.email || '',
				name: {
					first: auth_store.firebase_user?.displayName?.split(' ')[0] || 'Customer',
					last: auth_store.firebase_user?.displayName?.split(' ').slice(1).join(' ') || ''
				}
			},
			mobile_money_data: {
				country_code: '256', // Uganda
				network: mm_network.value,
				phone_number: mm_phone.value.replace(/^\+?256/, '') // Remove country code prefix
			},
			charge_data: {
				amount: Math.round(Number(total_amount)), // Round off to integer
				currency: 'UGX',
				reference: `event${event.value.id}${Date.now()}${Math.random().toString(36).substr(2, 9)}`
			},
			event_id: event.value.id,
			event_data: {
				title: event.value.title,
				quantity: guest_count.value,
				unit_price: event.value.price
			}
		}
		
		console.log('🔍 Event payment data:', payment_data)
		const payment_response = await complete_mobile_money_payment(payment_data)
		
		console.log('🔍 Event payment response:', payment_response)
		
		if (payment_response?.success) {
			toast_success('Payment initiated successfully! Check your phone for payment instructions.')
			close_payment_modal()
			
			// Refresh RSVPs and payment status to update the UI
			try {
				await events_store.fetch_my_rsvps()
				
				// Check payment status for this event
				if (event.value.price > 0) {
					has_paid_for_current_event.value = await events_store.has_paid_for_event(event.value.id)
				}
			} catch (error) {
				console.warn('Could not refresh RSVPs:', error)
			}
			
			// Track analytics
			if (window?.gtag) {
				window.gtag('event', 'purchase', {
					transaction_id: payment_response.transaction_id,
					value: total_amount,
					currency: 'UGX',
					items: [{
						item_id: event.value.id,
						item_name: event.value.title,
						item_category: 'Event',
						quantity: guest_count.value,
						price: event.value.price
					}]
				})
			}
		} else {
			toast_error(payment_response?.message || 'Payment failed. Please try again.')
		}
	} catch (error) {
		console.error('Event payment error:', error)
		toast_error('Payment failed. Please try again.')
	} finally {
		is_processing_payment.value = false
	}
}

function close_payment_modal() {
	show_payment_modal.value = false
	mm_phone.value = ''
	mm_network.value = 'MTN'
}
</script>

<style scoped>
.event_detail_page {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
	padding: 40px 0;
}

.loading_state {
	text-align: center;
	padding: 80px 20px;
}

.loading_spinner {
	width: 40px;
	height: 40px;
	border: 3px solid rgba(218, 165, 32, 0.3);
	border-top: 3px solid #DAA520;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin: 0 auto 20px;
}

@keyframes spin {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}

.loading_text {
	color: #666;
	font-size: 16px;
}

.not_found {
	text-align: center;
	padding: 80px 20px;
	background: white;
	border-radius: 16px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
	max-width: 500px;
	margin: 0 auto;
}

.not_found_icon {
	font-size: 64px;
	margin-bottom: 20px;
}

.not_found_title {
	font-size: 24px;
	font-weight: 600;
	color: #1a0f0f;
	margin-bottom: 12px;
}

.not_found_text {
	color: #666;
	font-size: 16px;
	margin-bottom: 30px;
}

.back_to_events_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 16px 32px;
	border-radius: 25px;
	font-weight: 600;
	font-size: 16px;
	text-decoration: none;
	transition: all 0.3s ease;
	display: inline-flex;
	align-items: center;
	gap: 8px;
}

.back_to_events_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.event_detail_content {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

.breadcrumb {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 30px;
	font-size: 14px;
}

.breadcrumb_link {
	color: #DAA520;
	text-decoration: none;
	transition: color 0.3s ease;
}

.breadcrumb_link:hover {
	color: #B8860B;
}

.breadcrumb_separator {
	color: #666;
}

.breadcrumb_current {
	color: #1a0f0f;
	font-weight: 600;
}

.event_main {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 60px;
	margin-bottom: 60px;
}

.event_image_section {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.event_image_container {
	position: relative;
	border-radius: 16px;
	overflow: hidden;
	background: white;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.event_image {
	width: 100%;
	height: 400px;
	object-fit: cover;
	display: block;
}

.event_badge {
	position: absolute;
	top: 16px;
	left: 16px;
	padding: 6px 12px;
	border-radius: 20px;
	font-size: 12px;
	font-weight: 600;
	color: white;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.status_upcoming {
	background: linear-gradient(135deg, #16a34a, #15803d);
}

.status_ongoing {
	background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.status_completed {
	background: linear-gradient(135deg, #6b7280, #4b5563);
}

.status_cancelled {
	background: linear-gradient(135deg, #dc2626, #b91c1c);
}

.event_type_badge {
	position: absolute;
	top: 16px;
	right: 16px;
	padding: 6px 12px;
	border-radius: 20px;
	font-size: 12px;
	font-weight: 600;
	color: #1a0f0f;
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(10px);
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.event_info {
	display: flex;
	flex-direction: column;
	gap: 30px;
}

.event_header {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.event_title {
	font-size: 36px;
	font-weight: 700;
	color: #1a0f0f;
	line-height: 1.2;
	font-family: 'Playfair Display', serif;
}

.event_meta {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.event_date_time, .event_time {
	display: flex;
	align-items: center;
	gap: 8px;
}

.date_icon, .time_icon {
	font-size: 16px;
	color: #DAA520;
}

.date_text, .time_text {
	font-size: 16px;
	color: #666;
	font-weight: 500;
}

.event_location {
	display: flex;
	gap: 16px;
	padding: 20px;
	background: rgba(218, 165, 32, 0.05);
	border-radius: 12px;
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.location_icon {
	font-size: 24px;
	color: #DAA520;
	flex-shrink: 0;
}

.location_details {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.location_name {
	font-size: 18px;
	font-weight: 600;
	color: #1a0f0f;
}

.location_address, .location_city {
	font-size: 14px;
	color: #666;
}

.event_pricing {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.price_display {
	display: flex;
	align-items: center;
	gap: 16px;
}

.free_price {
	font-size: 24px;
	font-weight: 700;
	color: #16a34a;
}

.ticket_price {
	font-size: 24px;
	font-weight: 700;
	color: #1a0f0f;
}

.member_price {
	font-size: 16px;
	color: #DAA520;
	font-weight: 600;
}

.event_capacity {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.capacity_info {
	display: flex;
	align-items: center;
	gap: 8px;
}

.capacity_icon {
	font-size: 16px;
	color: #DAA520;
}

.capacity_text {
	font-size: 14px;
	color: #666;
	font-weight: 500;
}

.capacity_bar {
	width: 100%;
	height: 8px;
	background: rgba(218, 165, 32, 0.2);
	border-radius: 4px;
	overflow: hidden;
}

.capacity_fill {
	height: 100%;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	transition: width 0.3s ease;
}

.event_description {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.description_title {
	font-size: 20px;
	font-weight: 600;
	color: #1a0f0f;
}

.description_text {
	font-size: 16px;
	color: #666;
	line-height: 1.6;
}

.rsvp_section {
	padding: 24px;
	background: white;
	border-radius: 16px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.rsvp_header {
	margin-bottom: 20px;
}

.rsvp_title {
	font-size: 20px;
	font-weight: 600;
	color: #1a0f0f;
	display: flex;
	align-items: center;
	gap: 8px;
}

.title_icon {
	font-size: 20px;
}

.rsvp_form {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.guest_count_selector {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.guest_label {
	font-size: 14px;
	font-weight: 600;
	color: #1a0f0f;
}

.guest_controls {
	display: flex;
	align-items: center;
	gap: 8px;
}

.guest_btn {
	width: 40px;
	height: 40px;
	border: 2px solid rgba(218, 165, 32, 0.3);
	border-radius: 50%;
	background: white;
	color: #666;
	font-size: 18px;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
}

.guest_btn:hover:not(:disabled) {
	border-color: #DAA520;
	color: #DAA520;
	background: rgba(218, 165, 32, 0.1);
}

.guest_btn:disabled {
	opacity: 0.5;
	cursor: not-allowed;
}

.guest_input {
	width: 80px;
	height: 40px;
	border: 2px solid rgba(218, 165, 32, 0.3);
	border-radius: 20px;
	text-align: center;
	font-size: 16px;
	font-weight: 600;
}

.guest_input:focus {
	outline: none;
	border-color: #DAA520;
}

.rsvp_actions {
	display: flex;
	gap: 12px;
}

.rsvp_btn {
	border: none;
	padding: 16px 24px;
	border-radius: 12px;
	font-weight: 600;
	font-size: 16px;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	flex: 1;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
}

.rsvp_btn:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.rsvp_btn:disabled {
	opacity: 0.7;
	cursor: not-allowed;
	transform: none;
	box-shadow: none;
}

.rsvp_btn.paid_btn {
	background: linear-gradient(135deg, #16a34a, #15803d);
	color: white;
	cursor: default;
}

.rsvp_btn.paid_btn:hover {
	transform: none;
	box-shadow: none;
}

.rsvp_btn.confirmed_btn {
	background: linear-gradient(135deg, #059669, #047857);
	color: white;
}

.btn_spinner {
	width: 20px;
	height: 20px;
	border: 2px solid rgba(255, 255, 255, 0.3);
	border-top: 2px solid white;
	border-radius: 50%;
	animation: spin 1s linear infinite;
}

.btn_icon {
	font-size: 16px;
}

@media (max-width: 768px) {
	.event_main {
		grid-template-columns: 1fr;
		gap: 30px;
	}
	
	.event_title {
		font-size: 28px;
	}
	
	.rsvp_actions {
		flex-direction: column;
	}
}

/* Event Payment Modal */
.modal_overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
	animation: fadeIn 0.3s ease-out;
}

.modal_content {
	background: white;
	border-radius: 20px;
	width: 90%;
	max-width: 500px;
	max-height: 90vh;
	overflow-y: auto;
	animation: slideInUp 0.3s ease-out;
}

.modal_header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 25px 30px;
	border-bottom: 1px solid #e2e8f0;
}

.modal_header h3 {
	font-size: 1.3rem;
	font-weight: 600;
	color: #1e293b;
	margin: 0;
}

.modal_close {
	background: none;
	border: none;
	font-size: 1.5rem;
	color: #64748b;
	cursor: pointer;
	padding: 5px;
	border-radius: 50%;
	transition: all 0.3s ease;
}

.modal_close:hover {
	background: #f1f5f9;
	color: #1e293b;
}

.modal_body {
	padding: 30px;
}

.event_payment_summary {
	background: #f8fafc;
	border-radius: 12px;
	padding: 20px;
	margin-bottom: 30px;
	border: 1px solid #e2e8f0;
}

.summary_item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 8px 0;
}

.summary_label {
	font-size: 0.95rem;
	color: #64748b;
	font-weight: 500;
}

.summary_value {
	font-size: 0.95rem;
	color: #1e293b;
	font-weight: 500;
}

.total_item {
	border-top: 2px solid #e2e8f0;
	padding-top: 12px;
	margin-top: 8px;
}

.total_item .summary_value {
	font-weight: 700;
	color: #DAA520;
	font-size: 1.1rem;
}

.payment_form {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.form_title {
	font-size: 1.1rem;
	font-weight: 600;
	color: #1e293b;
	margin-bottom: 10px;
}

.form_group {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.form_label {
	font-size: 0.9rem;
	font-weight: 600;
	color: #1e293b;
}

.form_select, .form_input {
	padding: 12px 16px;
	border: 2px solid #e2e8f0;
	border-radius: 8px;
	font-size: 1rem;
	transition: all 0.3s ease;
}

.form_select:focus, .form_input:focus {
	outline: none;
	border-color: #DAA520;
	box-shadow: 0 0 0 3px rgba(218, 165, 32, 0.1);
}

.form_help {
	font-size: 0.8rem;
	color: #64748b;
}

.payment_actions {
	display: flex;
	gap: 12px;
	margin-top: 20px;
}

.btn_cancel, .btn_pay {
	padding: 12px 24px;
	border-radius: 8px;
	font-size: 1rem;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	flex: 1;
}

.btn_cancel {
	background: white;
	color: #64748b;
	border: 2px solid #e2e8f0;
}

.btn_cancel:hover:not(:disabled) {
	border-color: #64748b;
	color: #1e293b;
}

.btn_pay {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
}

.btn_pay:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.btn_cancel:disabled, .btn_pay:disabled {
	opacity: 0.7;
	cursor: not-allowed;
	transform: none;
	box-shadow: none;
}

.btn_spinner {
	width: 20px;
	height: 20px;
	border: 2px solid rgba(255, 255, 255, 0.3);
	border-top: 2px solid white;
	border-radius: 50%;
	animation: spin 1s linear infinite;
}

@keyframes fadeIn {
	from { opacity: 0; }
	to { opacity: 1; }
}

@keyframes slideInUp {
	from {
		opacity: 0;
		transform: translateY(30px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

@media (max-width: 768px) {
	.modal_content {
		width: 95%;
		margin: 20px;
	}
	
	.modal_header, .modal_body {
		padding: 20px;
	}
	
	.payment_actions {
		flex-direction: column;
	}
}
</style> 