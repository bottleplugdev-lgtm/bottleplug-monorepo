<template>
	<div class="events_page">
		<!-- Hero Section -->
		<section class="hero_section">
			<div class="hero_background"></div>
			<div class="hero_content">
				<h1 class="hero_title">Exclusive Events & Tastings</h1>
				<p class="hero_subtitle">Join us for curated wine tastings, spirit masterclasses, and unforgettable experiences</p>
				<div class="hero_stats">
					<div class="stat_item">
						<span class="stat_number">{{ events.length }}</span>
						<span class="stat_label">Upcoming Events</span>
					</div>
					<div class="stat_item">
						<span class="stat_number">🍷</span>
						<span class="stat_label">Premium Tastings</span>
					</div>
					<div class="stat_item">
						<span class="stat_number">⭐</span>
						<span class="stat_label">Expert Curation</span>
					</div>
				</div>
			</div>
		</section>

		<!-- Events Section -->
		<section class="events_section">
			<div class="events_container">
				<!-- Loading State -->
				<div v-if="is_loading" class="loading_state">
					<div class="loading_spinner"></div>
					<p class="loading_text">Discovering exclusive events...</p>
				</div>

				<!-- Events Grid -->
				<div v-else class="events_grid">
					<div v-for="e in events" :key="e.id" class="event_card">
						<RouterLink :to="`/events/${e.id}`" class="event_link">
						<div class="event_image_container">
							<img 
								:src="image_url(e.cover || e.image)" 
								:alt="e.title" 
								class="event_image" 
								loading="lazy"
							/>
							<div class="event_overlay">
								<div class="event_actions">
									<button class="rsvp_btn" @click.stop="rsvp(e)">
										<span class="btn_icon">📅</span>
										RSVP Now
									</button>
									<button v-if="e.price" class="pay_btn" @click.stop="pay_for_event(e)">
										<span class="btn_icon">💳</span>
										Buy Tickets
									</button>
								</div>
							</div>
							<div class="event_badges">
								<span v-if="e.price" class="badge paid_badge">Paid Event</span>
								<span v-else class="badge free_badge">Free Event</span>
							</div>
						</div>
						
						<div class="event_info">
							<div class="event_meta">
								<span v-if="e.venue" class="event_venue">{{ e.venue }}</span>
								<span v-if="e.city" class="event_city">{{ e.city }}</span>
							</div>
							
							<h3 class="event_title">{{ e.title }}</h3>
							
							<div class="event_details">
								<div v-if="e.date" class="event_date">
									<span class="date_icon">📅</span>
									<span class="date_text">{{ format_date(e.date) }}</span>
								</div>
								<div v-if="e.time" class="event_time">
									<span class="time_icon">🕒</span>
									<span class="time_text">{{ e.time }}</span>
								</div>
								<div v-if="e.price" class="event_price">
									<span class="price_icon">💰</span>
									<span class="price_text">{{ format_price(e.price) }}</span>
								</div>
							</div>
							
							<p v-if="e.description" class="event_description">{{ e.description }}</p>
							
							<div class="event_booking">
								<div v-if="e.price" class="quantity_section">
									<label class="quantity_label">Tickets:</label>
									<div class="quantity_controls">
										<button 
											class="quantity_btn" 
											@click="e._qty = Math.max(1, (e._qty || 1) - 1)"
										>-</button>
										<input 
											type="number" 
											min="1" 
											v-model.number="e._qty" 
											class="quantity_input" 
										/>
										<button 
											class="quantity_btn" 
											@click="e._qty = (e._qty || 1) + 1"
										>+</button>
									</div>
								</div>
								
								<div class="event_buttons">
									<button 
										v-if="!e.price || !has_rsvped_for_event(e.id)"
										class="rsvp_action_btn" 
										:class="{ 'paid_btn': has_paid_for_event(e.id), 'confirmed_btn': has_rsvped_for_event(e.id) && !has_paid_for_event(e.id) }"
										@click.stop="rsvp(e)"
										:disabled="has_paid_for_event(e.id)"
									>
										<span class="btn_icon">{{ get_event_button_icon(e) }}</span>
										{{ get_event_button_text(e) }}
									</button>
									<button 
										v-if="e.price && !has_rsvped_for_event(e.id)" 
										class="pay_action_btn" 
										@click.stop="pay_for_event(e)"
									>
										<span class="btn_icon">💳</span>
										Buy Tickets
									</button>
								</div>
							</div>
						</div>
						</RouterLink>
					</div>
				</div>

				<!-- Empty State -->
				<div v-if="!is_loading && events.length === 0" class="empty_state">
					<div class="empty_icon">🍷</div>
					<h3 class="empty_title">No events scheduled</h3>
					<p class="empty_text">Check back soon for upcoming tastings and exclusive experiences</p>
				</div>
			</div>
		</section>
	</div>

	<!-- Event Payment Modal -->
	<div v-if="show_payment_modal" class="modal_overlay" @click="close_payment_modal">
		<div class="modal_content" @click.stop>
			<div class="modal_header">
				<h3>Pay for Event: {{ selected_event?.title }}</h3>
				<button @click="close_payment_modal" class="modal_close">×</button>
			</div>
			
			<div v-if="selected_event" class="modal_body">
				<div class="event_payment_summary">
					<div class="summary_item">
						<span class="summary_label">Event:</span>
						<span class="summary_value">{{ selected_event.title }}</span>
					</div>
					<div class="summary_item">
						<span class="summary_label">Tickets:</span>
						<span class="summary_value">{{ selected_event.quantity }}</span>
					</div>
					<div class="summary_item">
						<span class="summary_label">Price per ticket:</span>
						<span class="summary_value">{{ format_price(selected_event.price) }}</span>
					</div>
					<div class="summary_item total_item">
						<span class="summary_label">Total Amount:</span>
						<span class="summary_value">{{ format_price(selected_event.total_amount) }}</span>
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
import { useRouter } from 'vue-router'
import { get_events, create_rsvp, complete_mobile_money_payment } from '../services/api'
import { use_auth_store } from '../stores/auth'
import { use_events_store } from '../stores/events'
import { set_seo } from '../lib/seo'
import { toast_success, toast_error } from '../lib/toast'

const events = ref([])
const is_loading = ref(true)
const router = useRouter()
const auth_store = use_auth_store()
const events_store = use_events_store()

// Payment modal state
const show_payment_modal = ref(false)
const selected_event = ref(null)
const mm_network = ref('MTN')
const mm_phone = ref('')
const is_processing_payment = ref(false)
const event_payment_status = ref(new Map()) // Track payment status for each event

// Helper functions to check RSVP status
function has_rsvped_for_event(event_id) {
	if (!auth_store.is_ready || !auth_store.is_authenticated) return false
	return events_store.has_rsvp_for_event(event_id)
}

function get_rsvp_for_event(event_id) {
	if (!auth_store.is_ready || !auth_store.is_authenticated) return null
	return events_store.get_rsvp_by_event_id(event_id)
}

async function has_paid_for_event(event_id) {
	const event = events.value.find(e => e.id === event_id)
	
	// For free events, consider RSVP as "paid"
	if (!event?.price || event.price === 0) {
		return has_rsvped_for_event(event_id)
	}
	
	// For paid events, check actual payment status
	try {
		return await events_store.has_paid_for_event(event_id)
	} catch (error) {
		console.warn('Could not check payment status for event:', error)
		return false
	}
}

function get_event_button_text(event) {
	if (has_rsvped_for_event(event.id)) {
		if (event_payment_status.value.get(event.id)) {
			return '✅ Paid'
		} else if (event.price > 0) {
			return 'Complete Payment'
		} else {
			return '✅ RSVPed'
		}
	}
	
	// Not RSVPed yet
	if (event.price > 0) {
		return 'Buy Tickets'
	} else {
		return 'RSVP'
	}
}

function get_event_button_icon(event) {
	if (has_rsvped_for_event(event.id)) {
		if (event_payment_status.value.get(event.id)) {
			return '✅'
		} else if (event.price > 0) {
			return '💳'
		} else {
			return '✅'
		}
	}
	
	// Not RSVPed yet
	if (event.price > 0) {
		return '💳'
	} else {
		return '📅'
	}
}

onMounted(async () => {
	try {
		events.value = (await get_events())?.results || []
		
		// Load user's RSVPs if authenticated and auth is ready
		if (auth_store.is_ready && auth_store.is_authenticated) {
			try {
				await events_store.fetch_my_rsvps()
				
				// Check payment status for all paid events
				for (const event of events.value) {
					if (event.price > 0) {
						const hasPaid = await events_store.has_paid_for_event(event.id)
						event_payment_status.value.set(event.id, hasPaid)
					}
				}
			} catch (error) {
				console.warn('Could not fetch RSVPs:', error)
				// Continue without RSVPs - the UI will show default states
			}
		}
	} finally {
		is_loading.value = false
	}
	set_seo({ 
		title: 'Exclusive Events & Tastings · BottlePlug', 
		description: 'Join us for curated wine tastings, spirit masterclasses, and unforgettable experiences. RSVP or buy tickets for exclusive events.' 
	})
})

function image_url(path) {
        if (!path) return 'http://localhost:8000/media/bottleplug_logo.png'
	if (/^https?:/.test(path)) {
		path = path.replace('localhost', 'localhost:8000')
		return path
	}
	
	        // Build full URL from relative path
        // The backend returns relative paths like 'products/image.jpg' or 'media/products/image.jpg'
        // We need to construct the full URL using the backend URL directly
        const backend_url = 'http://localhost:8000'

        // Remove any leading 'media/' from the path to avoid duplication
        const clean_path = path.replace(/^\/?media\//, '')
        return `${backend_url}/media/${clean_path}`
}

function format_price(value) {
	const amount = Number(value) || 0
	return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', minimumFractionDigits: 0 }).format(amount)
}

function format_date(date_string) {
	const date = new Date(date_string)
	return date.toLocaleDateString('en-US', { 
		weekday: 'long', 
		year: 'numeric', 
		month: 'long', 
		day: 'numeric' 
	})
}

function require_auth_or_redirect() {
			if (!auth_store.is_authenticated) {
		auth_store.set_intended_destination('/events')
		router.push({ name: 'login' })
		return false
	}
	return true
}

async function rsvp(e) {
	if (!require_auth_or_redirect()) return
	try {
		await create_rsvp({ event: e.id })
		
		// Refresh RSVPs to update the UI
		try {
			await events_store.fetch_my_rsvps()
		} catch (error) {
			console.warn('Could not refresh RSVPs:', error)
		}
		
		toast_success('RSVP confirmed! We\'ll see you there.')
		if (window?.gtag) window.gtag('event', 'rsvp', { event_id: e.id, event_title: e.title })
	} catch (err) {
		toast_error('Failed to RSVP. Please try again.')
	}
}

async function pay_for_event(e) {
	if (!require_auth_or_redirect()) return
	
	const qty = Number(e._qty || 1)
	const amount = Number(e.price || 0) * (qty > 0 ? qty : 1)
	if (!amount) {
		toast_error('Invalid event price')
		return
	}
	
	// Store event data for payment modal
	selected_event.value = {
		...e,
		quantity: qty,
		total_amount: amount
	}
	show_payment_modal.value = true
}

async function process_event_payment() {
	if (!selected_event.value || !mm_phone.value) {
		toast_error('Please enter your mobile money phone number')
		return
	}
	
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
				amount: Math.round(Number(selected_event.value.total_amount)), // Round off to integer
				currency: 'UGX',
				reference: `event${selected_event.value.id}${Date.now()}${Math.random().toString(36).substr(2, 9)}`
			},
			event_id: selected_event.value.id,
			event_data: {
				title: selected_event.value.title,
				quantity: selected_event.value.quantity,
				unit_price: selected_event.value.price
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
				
				// Update payment status for the selected event
				if (selected_event.value?.id) {
					const hasPaid = await events_store.has_paid_for_event(selected_event.value.id)
					event_payment_status.value.set(selected_event.value.id, hasPaid)
				}
			} catch (error) {
				console.warn('Could not refresh RSVPs:', error)
			}
			
			// Track analytics
			if (window?.gtag) {
				window.gtag('event', 'purchase', {
					transaction_id: payment_response.transaction_id,
					value: selected_event.value.total_amount,
					currency: 'UGX',
					items: [{
						item_id: selected_event.value.id,
						item_name: selected_event.value.title,
						item_category: 'Event',
						quantity: selected_event.value.quantity,
						price: selected_event.value.price
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
	selected_event.value = null
	mm_phone.value = ''
	mm_network.value = 'MTN'
}
</script>

<style scoped>
.events_page {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

/* Hero Section */
.hero_section {
	position: relative;
	height: 400px;
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
}

.hero_background {
	position: absolute;
	inset: 0;
	background: linear-gradient(135deg, #1a0f0f 0%, #2d1b1b 50%, #1a0f0f 100%);
}

.hero_background::before {
	content: '';
	position: absolute;
	inset: 0;
	background-image: url('/toss.jpg');
	background-size: cover;
	background-position: center;
	opacity: 0.3;
	filter: blur(1px);
}

.hero_content {
	position: relative;
	z-index: 2;
	text-align: center;
	color: white;
	max-width: 800px;
	padding: 0 20px;
}

.hero_title {
	font-size: 48px;
	font-weight: 700;
	font-family: 'Playfair Display', serif;
	margin-bottom: 16px;
	background: linear-gradient(135deg, #DAA520, #FFD700);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.hero_subtitle {
	font-size: 18px;
	opacity: 0.9;
	line-height: 1.6;
	margin-bottom: 40px;
}

.hero_stats {
	display: flex;
	justify-content: center;
	gap: 40px;
	flex-wrap: wrap;
}

.stat_item {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 8px;
}

.stat_number {
	font-size: 32px;
	font-weight: 700;
	color: #DAA520;
}

.stat_label {
	font-size: 14px;
	opacity: 0.8;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

/* Events Section */
.events_section {
	padding: 60px 0;
}

.events_container {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

.loading_state, .empty_state {
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

.loading_text, .empty_text {
	color: #666;
	font-size: 16px;
	margin-bottom: 20px;
}

.empty_icon {
	font-size: 48px;
	margin-bottom: 20px;
}

.empty_title {
	font-size: 24px;
	font-weight: 600;
	color: #1a0f0f;
	margin-bottom: 12px;
}

/* Events Grid */
.events_grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
	gap: 30px;
}

.event_link {
	text-decoration: none;
	color: inherit;
	display: block;
}

.event_card {
	background: white;
	border-radius: 16px;
	overflow: hidden;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	transition: all 0.3s ease;
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.event_card:hover {
	transform: translateY(-8px);
	box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.event_image_container {
	position: relative;
	height: 250px;
	overflow: hidden;
}

.event_image {
	width: 100%;
	height: 100%;
	object-fit: cover;
	transition: transform 0.3s ease;
}

.event_card:hover .event_image {
	transform: scale(1.05);
}

.event_overlay {
	position: absolute;
	inset: 0;
	background: rgba(0, 0, 0, 0.7);
	display: flex;
	align-items: center;
	justify-content: center;
	opacity: 0;
	transition: opacity 0.3s ease;
}

.event_card:hover .event_overlay {
	opacity: 1;
}

.event_actions {
	display: flex;
	gap: 12px;
}

.rsvp_btn, .pay_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	padding: 12px 20px;
	border-radius: 25px;
	text-decoration: none;
	font-weight: 600;
	font-size: 14px;
	transition: all 0.3s ease;
	border: none;
	cursor: pointer;
	display: flex;
	align-items: center;
	gap: 6px;
}

.pay_btn {
	background: linear-gradient(135deg, #8B4513, #A0522D);
}

.rsvp_btn:hover, .pay_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.4);
}

.event_badges {
	position: absolute;
	top: 12px;
	right: 12px;
	display: flex;
	gap: 8px;
}

.badge {
	padding: 6px 12px;
	border-radius: 12px;
	font-size: 11px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.paid_badge {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
}

.free_badge {
	background: linear-gradient(135deg, #059669, #047857);
	color: white;
}

.event_info {
	padding: 24px;
}

.event_meta {
	display: flex;
	gap: 12px;
	margin-bottom: 12px;
}

.event_venue, .event_city {
	font-size: 12px;
	color: #DAA520;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.event_title {
	font-size: 20px;
	font-weight: 600;
	color: #1a0f0f;
	margin-bottom: 16px;
	line-height: 1.3;
}

.event_details {
	display: flex;
	flex-direction: column;
	gap: 8px;
	margin-bottom: 16px;
}

.event_date, .event_time, .event_price {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 14px;
	color: #666;
}

.date_icon, .time_icon, .price_icon {
	font-size: 16px;
}

.event_description {
	color: #666;
	line-height: 1.6;
	margin-bottom: 20px;
	font-size: 14px;
}

.event_booking {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 16px;
}

.quantity_section {
	display: flex;
	align-items: center;
	gap: 12px;
}

.quantity_label {
	font-size: 14px;
	font-weight: 600;
	color: #1a0f0f;
}

.quantity_controls {
	display: flex;
	align-items: center;
	gap: 8px;
}

.quantity_btn {
	width: 32px;
	height: 32px;
	border: 2px solid rgba(218, 165, 32, 0.3);
	border-radius: 50%;
	background: white;
	color: #666;
	font-size: 16px;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
}

.quantity_btn:hover {
	border-color: #DAA520;
	color: #DAA520;
	background: rgba(218, 165, 32, 0.1);
}

.quantity_input {
	width: 50px;
	height: 32px;
	border: 2px solid rgba(218, 165, 32, 0.3);
	border-radius: 16px;
	text-align: center;
	font-size: 14px;
	font-weight: 600;
}

.quantity_input:focus {
	outline: none;
	border-color: #DAA520;
}

.event_buttons {
	display: flex;
	gap: 8px;
}

.rsvp_action_btn, .pay_action_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 10px 20px;
	border-radius: 20px;
	font-size: 12px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	gap: 6px;
}

.pay_action_btn {
	background: linear-gradient(135deg, #8B4513, #A0522D);
}

.rsvp_action_btn:hover, .pay_action_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(218, 165, 32, 0.3);
}

.rsvp_action_btn.paid_btn {
	background: linear-gradient(135deg, #16a34a, #15803d);
	color: white;
	cursor: default;
}

.rsvp_action_btn.paid_btn:hover {
	transform: none;
	box-shadow: none;
}

.rsvp_action_btn.confirmed_btn {
	background: linear-gradient(135deg, #059669, #047857);
	color: white;
}

.btn_icon {
	font-size: 14px;
}

/* Responsive Design */
@media (max-width: 768px) {
	.hero_title {
		font-size: 36px;
	}
	
	.hero_subtitle {
		font-size: 16px;
	}
	
	.hero_stats {
		gap: 20px;
	}
	
	.stat_number {
		font-size: 24px;
	}
	
	.events_grid {
		grid-template-columns: 1fr;
		gap: 20px;
	}
	
	.event_booking {
		flex-direction: column;
		align-items: stretch;
		gap: 16px;
	}
	
	.quantity_section {
		justify-content: center;
	}
	
	.event_buttons {
		justify-content: center;
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
