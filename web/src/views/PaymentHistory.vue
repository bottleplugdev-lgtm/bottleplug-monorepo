<template>
	<div class="payment_history">
		<!-- Auth Loading State -->
		<AuthLoading v-if="is_auth_loading" />
		
		<!-- Main Content (only show when auth is ready and user is authenticated) -->
		<template v-else-if="should_show_content">
			<!-- Hero Section -->
			<section class="hero_section">
				<div class="hero_content">
					<h1 class="hero_title">Payment History</h1>
					<p class="hero_subtitle">Track your payment transactions and manage your billing</p>
				</div>
			</section>

			<!-- Filters and Search -->
			<section class="filters_section">
				<div class="container">
					<div class="filters_container">
						<div class="search_box">
							<input 
								v-model="search_query" 
								type="text" 
								placeholder="Search payments by ID or amount..."
								@input="debounce_search"
								class="search_input"
							>
							<svg class="search_icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
							</svg>
						</div>

						<div class="filter_controls">
							<select v-model="status_filter" @change="apply_filters" class="filter_select">
								<option value="">All Status</option>
								<option value="pending">Pending</option>
								<option value="completed">Completed</option>
								<option value="failed">Failed</option>
								<option value="refunded">Refunded</option>
								<option value="cancelled">Cancelled</option>
							</select>

							<select v-model="method_filter" @change="apply_filters" class="filter_select">
								<option value="">All Methods</option>
								<option value="card">Card</option>
								<option value="mobile_money">Mobile Money</option>
								<option value="bank_transfer">Bank Transfer</option>
							</select>

							<select v-model="date_filter" @change="apply_filters" class="filter_select">
								<option value="">All Time</option>
								<option value="7">Last 7 days</option>
								<option value="30">Last 30 days</option>
								<option value="90">Last 3 months</option>
								<option value="365">Last year</option>
							</select>
						</div>
					</div>
				</div>
			</section>

			<!-- Payments List -->
			<section class="payments_section">
				<div class="container">
					<div v-if="is_loading && payments.length === 0" class="loading_state">
						<div class="loading_spinner"></div>
						<p>Loading your payments...</p>
					</div>

					<div v-else-if="filtered_payments.length === 0" class="empty_state">
						<div class="empty_icon">💳</div>
						<h3>No Payments Found</h3>
						<p v-if="search_query || status_filter || date_filter">
							No payments match your current filters. Try adjusting your search criteria.
						</p>
						<p v-else>
							You haven't made any payments yet. Your payment history will appear here.
						</p>
						<RouterLink to="/products" class="btn_primary">Start Shopping</RouterLink>
					</div>

					<div v-else class="payments_list">
						<div 
							v-for="payment in filtered_payments" 
							:key="payment.id" 
							class="payment_card"
							@click="view_payment_details(payment)"
						>
							<div class="payment_header">
								<div class="payment_info">
									<h3 class="payment_number">Payment #{{ payment.id }}</h3>
									<p class="payment_date">{{ format_date(payment.created_at) }}</p>
								</div>
								<div class="payment_status">
									<span :class="['status_badge', `status_${payment.status}`]">
										{{ format_payment_status(payment.status) }}
									</span>
								</div>
							</div>

							<div class="payment_details">
								<div class="payment_method">
									<span class="method_icon">{{ get_payment_method_icon(payment.payment_method) }}</span>
									<span class="method_text">{{ format_payment_method(payment.payment_method) }}</span>
								</div>
								<div class="payment_amount">
									<span class="amount_text">{{ format_amount(payment.amount) }}</span>
								</div>
								<div class="payment_reference" v-if="payment.reference">
									<span class="reference_text">Ref: {{ payment.reference }}</span>
								</div>
							</div>

							<div class="payment_footer">
								<div class="payment_actions">
									<button 
										@click.stop="view_payment_details(payment)"
										class="btn_secondary"
									>
										View Details
									</button>
									<button 
										v-if="payment.status === 'completed' && payment.order"
										@click.stop="view_related_order(payment.order)"
										class="btn_outline"
									>
										View Order
									</button>
								</div>
							</div>
						</div>
					</div>

					<!-- Load More -->
					<div v-if="has_more_payments" class="load_more_section">
						<button 
							@click="load_more_payments"
							:disabled="is_loading"
							class="btn_load_more"
						>
							<span v-if="is_loading">Loading...</span>
							<span v-else>Load More Payments</span>
						</button>
					</div>
				</div>
			</section>
		</template>
		
		<!-- Not Authenticated State -->
		<div v-else class="not_authenticated_state">
			<div class="auth_message">
				<h2>Please Sign In</h2>
				<p>You need to be signed in to view your payment history.</p>
				<RouterLink to="/login" class="btn_primary">Sign In</RouterLink>
			</div>
		</div>
	</div>

	<!-- Payment Details Modal -->
	<div v-if="show_payment_modal" class="modal_overlay" @click="close_payment_modal">
		<div class="modal_content" @click.stop>
			<div class="modal_header">
				<h3>Payment Details: #{{ selected_payment?.id }}</h3>
				<button @click="close_payment_modal" class="modal_close">×</button>
			</div>
			
			<div v-if="selected_payment" class="modal_body">
				<div class="payment_details">
					<div class="detail_group">
						<h4>Payment Information</h4>
						<div class="detail_grid">
							<div class="detail_item">
								<span class="detail_label">Payment ID:</span>
								<span class="detail_value">#{{ selected_payment.id }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Payment Date:</span>
								<span class="detail_value">{{ format_date(selected_payment.created_at) }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Status:</span>
								<span class="detail_value">{{ format_payment_status(selected_payment.status) }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Amount:</span>
								<span class="detail_value">{{ format_amount(selected_payment.amount) }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Payment Method:</span>
								<span class="detail_value">{{ format_payment_method(selected_payment.payment_method) }}</span>
							</div>
							<div class="detail_item" v-if="selected_payment.transaction_id">
								<span class="detail_label">Transaction ID:</span>
								<span class="detail_value">{{ selected_payment.transaction_id }}</span>
							</div>
							<div class="detail_item" v-if="selected_payment.reference">
								<span class="detail_label">Reference:</span>
								<span class="detail_value">{{ selected_payment.reference }}</span>
							</div>
						</div>
					</div>

					<div class="detail_group" v-if="selected_payment.order">
						<h4>Related Order</h4>
						<div class="detail_grid">
							<div class="detail_item">
								<span class="detail_label">Order Number:</span>
								<span class="detail_value">#{{ selected_payment.order.order_number || selected_payment.order.id }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Order Date:</span>
								<span class="detail_value">{{ format_date(selected_payment.order.created_at) }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Order Status:</span>
								<span class="detail_value">{{ format_status(selected_payment.order.status) }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Order Total:</span>
								<span class="detail_value">{{ format_amount(selected_payment.order.total_amount) }}</span>
							</div>
						</div>
					</div>

					<div class="detail_group" v-if="selected_payment.description || selected_payment.notes">
						<h4>Additional Information</h4>
						<div class="detail_grid">
							<div class="detail_item" v-if="selected_payment.description">
								<span class="detail_label">Description:</span>
								<span class="detail_value">{{ selected_payment.description }}</span>
							</div>
							<div class="detail_item" v-if="selected_payment.notes">
								<span class="detail_label">Notes:</span>
								<span class="detail_value">{{ selected_payment.notes }}</span>
							</div>
						</div>
					</div>

					<div class="detail_group" v-if="selected_payment.failure_reason">
						<h4>Payment Failure Details</h4>
						<div class="detail_grid">
							<div class="detail_item">
								<span class="detail_label">Failure Reason:</span>
								<span class="detail_value error_text">{{ selected_payment.failure_reason }}</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { use_auth_store } from '../stores/auth'
import { get_my_transactions } from '../services/api'
import AuthLoading from '../components/AuthLoading.vue'

// Router
const router = useRouter()

// Stores
const auth_store = use_auth_store()

// Reactive data
const search_query = ref('')
const status_filter = ref('')
const method_filter = ref('')
const date_filter = ref('')
const search_timeout = ref(null)
const is_auth_loading = ref(true)
const show_payment_modal = ref(false)
const selected_payment = ref(null)
const payments = ref([])
const is_loading = ref(true)
const next_page_url = ref(null)

// Computed properties
const should_show_content = computed(() => !is_auth_loading.value && auth_store.is_authenticated)
const has_more_payments = computed(() => !!next_page_url.value)

const filtered_payments = computed(() => {
	let filtered = payments.value

	// Search filter
	if (search_query.value) {
		const query = search_query.value.toLowerCase()
		filtered = filtered.filter(payment => 
			payment.id?.toString().includes(query) ||
			payment.amount?.toString().includes(query) ||
			payment.reference?.toLowerCase().includes(query)
		)
	}

	// Status filter
	if (status_filter.value) {
		filtered = filtered.filter(payment => payment.status === status_filter.value)
	}

	// Method filter
	if (method_filter.value) {
		filtered = filtered.filter(payment => payment.payment_method === method_filter.value)
	}

	// Date filter
	if (date_filter.value) {
		const days = parseInt(date_filter.value)
		const cutoff_date = new Date()
		cutoff_date.setDate(cutoff_date.getDate() - days)
		
		filtered = filtered.filter(payment => 
			new Date(payment.created_at) >= cutoff_date
		)
	}

	return filtered
})

// Methods
const format_date = (date_string) => {
	if (!date_string) return 'N/A'
	return new Date(date_string).toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	})
}

const format_payment_status = (status) => {
	const status_map = {
		'pending': 'Pending',
		'completed': 'Completed',
		'failed': 'Failed',
		'refunded': 'Refunded',
		'cancelled': 'Cancelled',
		'processing': 'Processing'
	}
	return status_map[status] || status
}

const format_payment_method = (method) => {
	const method_map = {
		'card': 'Credit/Debit Card',
		'mobile_money': 'Mobile Money',
		'bank_transfer': 'Bank Transfer',
		'cash': 'Cash'
	}
	return method_map[method] || method || 'Card'
}

const get_payment_method_icon = (method) => {
	const icon_map = {
		'card': '💳',
		'mobile_money': '📱',
		'bank_transfer': '🏦',
		'cash': '💵'
	}
	return icon_map[method] || '💳'
}

const format_amount = (amount) => {
	if (!amount) return 'UGX 0'
	return new Intl.NumberFormat('en-UG', {
		style: 'currency',
		currency: 'UGX'
	}).format(amount)
}

const format_status = (status) => {
	const status_map = {
		'pending': 'Pending',
		'processing': 'Processing',
		'shipped': 'Shipped',
		'delivered': 'Delivered',
		'cancelled': 'Cancelled'
	}
	return status_map[status] || status
}

const debounce_search = () => {
	if (search_timeout.value) {
		clearTimeout(search_timeout.value)
	}
	search_timeout.value = setTimeout(() => {
		apply_filters()
	}, 300)
}

const apply_filters = () => {
	// Filters are applied automatically through computed properties
}

const load_more_payments = async () => {
	if (!next_page_url.value || is_loading.value) return
	
	try {
		is_loading.value = true
		const response = await fetch(next_page_url.value, {
			headers: {
				'Authorization': `Bearer ${await auth_store.get_firebase_token()}`
			}
		})
		
		if (response.ok) {
			const data = await response.json()
			payments.value = [...payments.value, ...(data.results || data)]
			next_page_url.value = data.next
		}
	} catch (error) {
		console.error('Failed to load more payments:', error)
	} finally {
		is_loading.value = false
	}
}

const view_payment_details = (payment) => {
	selected_payment.value = payment
	show_payment_modal.value = true
	
	// Debug: Log the payment structure
	console.log('=== PAYMENT DETAILS DEBUG ===')
	console.log('Full payment:', payment)
	console.log('Payment keys:', Object.keys(payment))
}

const close_payment_modal = () => {
	show_payment_modal.value = false
	selected_payment.value = null
}

const view_related_order = (order) => {
	// Navigate to order history with the specific order highlighted
	router.push({
		name: 'order_history',
		query: { highlight: order.id }
	})
}

// Lifecycle
onMounted(async () => {
	// Wait for auth to be ready
	if (auth_store.should_show_loading) {
		let attempts = 0
		const max_attempts = 30 // 30 * 100ms = 3 seconds
		
		while (auth_store.should_show_loading && attempts < max_attempts) {
			await new Promise(resolve => setTimeout(resolve, 100))
			attempts++
		}
	}
	
	is_auth_loading.value = false
	
	// Try to load data - the API will handle authentication
	try {
		const data = await get_my_transactions()
		payments.value = data?.results || data || []
		next_page_url.value = data?.next
	} catch (error) {
		console.error('Failed to load payments:', error)
		// Don't show error if user is not authenticated - that's expected
		if (auth_store.is_authenticated) {
			console.error('User is authenticated but failed to load payments')
		}
	} finally {
		is_loading.value = false
	}
})

// SEO
const set_seo = () => {
	document.title = 'Payment History · Bottleplug'
}

onMounted(() => {
	set_seo()
})
</script>

<style scoped>
.payment_history {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8f4f0 0%, #f5f1eb 25%, #f2ede6 50%, #efe9e1 75%, #ece5dc 100%);
}

.hero_section {
	background: linear-gradient(135deg, #DAA520 0%, #c6951a 50%, #b8860b 100%);
	padding: 80px 0 60px;
	text-align: center;
	position: relative;
	overflow: hidden;
}

.hero_title {
	font-size: 3.5rem;
	font-weight: 700;
	color: #ffffff;
	margin-bottom: 1rem;
}

.hero_subtitle {
	font-size: 1.25rem;
	color: rgba(255, 255, 255, 0.9);
	max-width: 600px;
	margin: 0 auto;
}

.container {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

.filters_section {
	padding: 30px 0;
	background: rgba(255, 255, 255, 0.5);
}

.filters_container {
	display: flex;
	flex-wrap: wrap;
	gap: 20px;
	align-items: center;
	justify-content: space-between;
}

.search_box {
	position: relative;
	flex: 1;
	max-width: 400px;
}

.search_input {
	width: 100%;
	padding: 12px 20px 12px 50px;
	border: 2px solid #e2e8f0;
	border-radius: 12px;
	background: white;
	color: #1e293b;
	font-size: 1rem;
	transition: all 0.3s ease;
}

.search_input:focus {
	outline: none;
	border-color: #DAA520;
	box-shadow: 0 0 0 3px rgba(218, 165, 32, 0.1);
}

.search_input::placeholder {
	color: #64748b;
}

.search_icon {
	position: absolute;
	left: 15px;
	top: 50%;
	transform: translateY(-50%);
	width: 20px;
	height: 20px;
	color: #64748b;
}

.filter_controls {
	display: flex;
	gap: 15px;
}

.filter_select {
	padding: 12px 20px;
	border: 2px solid #e2e8f0;
	border-radius: 12px;
	background: white;
	color: #1e293b;
	font-size: 1rem;
	cursor: pointer;
	transition: all 0.3s ease;
}

.filter_select:focus {
	outline: none;
	border-color: #DAA520;
	box-shadow: 0 0 0 3px rgba(218, 165, 32, 0.1);
}

.filter_select option {
	background: white;
	color: #1e293b;
}

.payments_section {
	padding: 40px 0 80px;
}

.loading_state, .empty_state {
	text-align: center;
	padding: 80px 20px;
}

.loading_spinner {
	width: 40px;
	height: 40px;
	border: 4px solid rgba(218, 165, 32, 0.1);
	border-top: 4px solid #DAA520;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin: 0 auto 20px;
}

@keyframes spin {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}

.empty_icon {
	font-size: 4rem;
	margin-bottom: 20px;
}

.empty_state h3 {
	font-size: 1.5rem;
	color: #1e293b;
	margin-bottom: 10px;
}

.empty_state p {
	color: #64748b;
	margin-bottom: 30px;
}

.payments_list {
	display: grid;
	gap: 20px;
}

.payment_card {
	background: white;
	border-radius: 20px;
	padding: 24px;
	box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
	transition: all 0.3s ease;
	cursor: pointer;
	animation: slideInLeft 0.6s ease-out;
}

.payment_card:hover {
	transform: translateY(-3px);
	box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

@keyframes slideInLeft {
	from {
		opacity: 0;
		transform: translateX(-30px);
	}
	to {
		opacity: 1;
		transform: translateX(0);
	}
}

.payment_header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 20px;
}

.payment_number {
	font-size: 1.25rem;
	font-weight: 600;
	color: #1e293b;
	margin-bottom: 5px;
}

.payment_date {
	color: #64748b;
	font-size: 0.9rem;
}

.status_badge {
	padding: 6px 12px;
	border-radius: 20px;
	font-size: 0.8rem;
	font-weight: 500;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.status_pending {
	background: #fef3c7;
	color: #d97706;
}

.status_completed {
	background: #dcfce7;
	color: #16a34a;
}

.status_failed {
	background: #fee2e2;
	color: #dc2626;
}

.status_refunded {
	background: #e0e7ff;
	color: #3730a3;
}

.status_cancelled {
	background: #f3f4f6;
	color: #6b7280;
}

.payment_details {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20px;
}

.payment_method {
	display: flex;
	align-items: center;
	gap: 8px;
}

.method_icon {
	font-size: 1.2rem;
}

.method_text {
	font-size: 0.9rem;
	color: #64748b;
}

.payment_amount {
	font-size: 1.5rem;
	font-weight: 700;
	color: #DAA520;
}

.payment_reference {
	font-size: 0.8rem;
	color: #64748b;
	font-style: italic;
}

.payment_footer {
	display: flex;
	justify-content: flex-end;
	padding-top: 20px;
	border-top: 1px solid #e2e8f0;
}

.payment_actions {
	display: flex;
	gap: 10px;
}

.btn_primary, .btn_secondary, .btn_outline, .btn_load_more {
	padding: 10px 20px;
	border-radius: 8px;
	font-size: 0.9rem;
	font-weight: 500;
	text-decoration: none;
	border: none;
	cursor: pointer;
	transition: all 0.3s ease;
}

.btn_primary {
	background: linear-gradient(135deg, #DAA520 0%, #c6951a 100%);
	color: white;
}

.btn_primary:hover {
	background: linear-gradient(135deg, #c6951a 0%, #b8860b 100%);
	transform: translateY(-2px);
	box-shadow: 0 10px 20px rgba(218, 165, 32, 0.3);
}

.btn_secondary {
	background: white;
	color: #1e293b;
	border: 2px solid #e2e8f0;
}

.btn_secondary:hover {
	border-color: #DAA520;
	color: #DAA520;
	transform: translateY(-2px);
	box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.btn_outline {
	background: transparent;
	color: #DAA520;
	border: 2px solid #DAA520;
}

.btn_outline:hover {
	background: #DAA520;
	color: white;
	transform: translateY(-2px);
	box-shadow: 0 5px 15px rgba(218, 165, 32, 0.3);
}

.btn_load_more {
	background: white;
	color: #1e293b;
	border: 2px solid #e2e8f0;
	padding: 15px 30px;
	font-size: 1rem;
}

.btn_load_more:hover {
	border-color: #DAA520;
	color: #DAA520;
	transform: translateY(-2px);
	box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.load_more_section {
	text-align: center;
	margin-top: 40px;
}

@media (max-width: 768px) {
	.hero_title {
		font-size: 2.5rem;
	}
	
	.filters_container {
		flex-direction: column;
		align-items: stretch;
	}
	
	.search_box {
		max-width: none;
	}
	
	.payment_header {
		flex-direction: column;
		gap: 15px;
	}
	
	.payment_details {
		flex-direction: column;
		gap: 10px;
		align-items: flex-start;
	}
}

/* Not Authenticated State */
.not_authenticated_state {
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 60vh;
	padding: 40px 20px;
}

.auth_message {
	text-align: center;
	background: white;
	border-radius: 20px;
	padding: 60px 40px;
	box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
	max-width: 500px;
	width: 100%;
}

.auth_message h2 {
	font-size: 2rem;
	font-weight: 600;
	color: #1e293b;
	margin-bottom: 15px;
}

.auth_message p {
	font-size: 1.1rem;
	color: #64748b;
	margin-bottom: 30px;
	line-height: 1.6;
}

/* Payment Details Modal */
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
	max-width: 800px;
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

.detail_group {
	margin-bottom: 30px;
}

.detail_group h4 {
	font-size: 1.1rem;
	font-weight: 600;
	color: #1e293b;
	margin-bottom: 15px;
	padding-bottom: 8px;
	border-bottom: 2px solid #e2e8f0;
}

.detail_grid {
	display: grid;
	gap: 15px;
}

.detail_item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 12px 0;
}

.detail_label {
	font-weight: 500;
	color: #64748b;
}

.detail_value {
	font-weight: 600;
	color: #1e293b;
}

.error_text {
	color: #dc2626;
	font-weight: 600;
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
}
</style>
