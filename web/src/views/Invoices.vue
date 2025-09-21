<template>
	<div class="invoices_page">
		<div class="page_header">
			<div class="header_content">
				<h1 class="page_title">My Invoices</h1>
				<p class="page_subtitle">View and manage your invoices</p>
			</div>
		</div>

		<div class="page_content">
			<div class="invoices_container">
				<!-- Loading State -->
				<div v-if="loading" class="loading_state">
					<div class="loading_spinner"></div>
					<p>Loading your invoices...</p>
				</div>

				<!-- Error State -->
				<div v-else-if="error" class="error_state">
					<div class="error_icon">⚠️</div>
					<h3>Unable to load invoices</h3>
					<p>{{ error }}</p>
					<button @click="load_invoices" class="retry_btn">Try Again</button>
				</div>

				<!-- Empty State -->
				<div v-else-if="invoices.length === 0" class="empty_state">
					<div class="empty_icon">🧾</div>
					<h3>No invoices found</h3>
					<p>You don't have any invoices yet. Invoices will appear here when you place orders.</p>
					<RouterLink to="/products" class="browse_btn">Browse Products</RouterLink>
				</div>

				<!-- Invoices List -->
				<div v-else class="invoices_list">
					<div class="invoices_header">
						<h2>Your Invoices ({{ invoices.length }})</h2>
						<div class="filter_controls">
							<select v-model="status_filter" @change="filter_invoices" class="filter_select">
								<option value="">All Status</option>
								<option value="sent">Sent</option>
								<option value="paid">Paid</option>
								<option value="overdue">Overdue</option>
								<option value="draft">Draft</option>
							</select>
						</div>
					</div>

					<div class="invoices_grid">
						<div 
							v-for="invoice in filtered_invoices" 
							:key="invoice.id" 
							class="invoice_card"
							:class="{ 'overdue': invoice.status === 'overdue' }"
						>
							<div class="invoice_header">
								<div class="invoice_info">
									<h3 class="invoice_number">{{ invoice.invoice_number }}</h3>
									<p class="invoice_date">{{ format_date(invoice.created_at) }}</p>
								</div>
								<div class="invoice_status">
									<span class="status_badge" :class="get_status_class(invoice.status)">
										{{ get_status_text(invoice.status) }}
									</span>
								</div>
							</div>

							<div class="invoice_details">
								<div class="detail_row">
									<span class="detail_label">Order:</span>
									<span class="detail_value">#{{ invoice.order?.order_number || 'N/A' }}</span>
								</div>
								<div class="detail_row">
									<span class="detail_label">Total Amount:</span>
									<span class="detail_value amount">UGX {{ format_currency(invoice.total_amount) }}</span>
								</div>
								<div class="detail_row">
									<span class="detail_label">Amount Paid:</span>
									<span class="detail_value amount paid">UGX {{ format_currency(invoice.amount_paid) }}</span>
								</div>
								<div class="detail_row" v-if="invoice.balance_due > 0">
									<span class="detail_label">Balance Due:</span>
									<span class="detail_value amount due">UGX {{ format_currency(invoice.balance_due) }}</span>
								</div>
							</div>

							<div class="invoice_actions">
								<button @click="view_invoice(invoice)" class="action_btn view_btn">
									<span class="btn_icon">👁️</span>
									View Details
								</button>
								<button 
									v-if="invoice.balance_due > 0" 
									@click="pay_invoice(invoice)" 
									class="action_btn pay_btn"
								>
									<span class="btn_icon">💳</span>
									Pay Now
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Invoice Details Modal -->
		<div v-if="show_invoice_modal" class="modal_overlay" @click="close_invoice_modal">
			<div class="modal_content" @click.stop>
				<div class="modal_header">
					<h2>Invoice Details</h2>
					<button @click="close_invoice_modal" class="close_btn">×</button>
				</div>
				<div v-if="selected_invoice" class="modal_body">
					<div class="invoice_summary">
						<div class="summary_row">
							<span class="summary_label">Invoice Number:</span>
							<span class="summary_value">{{ selected_invoice.invoice_number }}</span>
						</div>
						<div class="summary_row">
							<span class="summary_label">Order Number:</span>
							<span class="summary_value">#{{ selected_invoice.order?.order_number || 'N/A' }}</span>
						</div>
						<div class="summary_row">
							<span class="summary_label">Date:</span>
							<span class="summary_value">{{ format_date(selected_invoice.created_at) }}</span>
						</div>
						<div class="summary_row">
							<span class="summary_label">Status:</span>
							<span class="summary_value">
								<span class="status_badge" :class="get_status_class(selected_invoice.status)">
									{{ get_status_text(selected_invoice.status) }}
								</span>
							</span>
						</div>
					</div>

					<div class="invoice_amounts">
						<div class="amount_row">
							<span class="amount_label">Total Amount:</span>
							<span class="amount_value">UGX {{ format_currency(selected_invoice.total_amount) }}</span>
						</div>
						<div class="amount_row">
							<span class="amount_label">Amount Paid:</span>
							<span class="amount_value paid">UGX {{ format_currency(selected_invoice.amount_paid) }}</span>
						</div>
						<div class="amount_row" v-if="selected_invoice.balance_due > 0">
							<span class="amount_label">Balance Due:</span>
							<span class="amount_value due">UGX {{ format_currency(selected_invoice.balance_due) }}</span>
						</div>
					</div>

					<div class="modal_actions">
						<button @click="close_invoice_modal" class="action_btn secondary_btn">Close</button>
						<button 
							v-if="selected_invoice.balance_due > 0" 
							@click="pay_invoice(selected_invoice)" 
							class="action_btn pay_btn"
						>
							Pay Now
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- Payment Modal -->
		<div v-if="show_payment_modal" class="modal_overlay" @click="close_payment_modal">
			<div class="modal_content payment_modal" @click.stop>
				<div class="modal_header">
					<h2>Pay Invoice</h2>
					<button @click="close_payment_modal" class="close_btn">×</button>
				</div>
				<div v-if="selected_invoice" class="modal_body">
					<div class="payment_summary">
						<div class="payment_info">
							<h3>Pay for Order #{{ selected_invoice.order?.order_number || 'N/A' }}</h3>
							<p class="payment_subtitle">Invoice: {{ selected_invoice.invoice_number }}</p>
							<p class="payment_amount">Amount to Pay: <strong>UGX {{ format_currency(selected_invoice.balance_due) }}</strong></p>
						</div>
					</div>

					<div class="payment_form">
						<div class="form_group">
							<label for="mm_network">Mobile Money Network</label>
							<select id="mm_network" v-model="mm_network" class="form_input" required>
								<option value="">Select Network</option>
								<option value="MTN">MTN Mobile Money</option>
								<option value="AIRTEL">Airtel Money</option>
							</select>
						</div>

						<div class="form_group">
							<label for="mm_phone">Phone Number</label>
							<input 
								id="mm_phone"
								v-model="mm_phone" 
								type="tel" 
								placeholder="e.g., 0701234567 or +256701234567"
								class="form_input"
								required
							/>
							<small class="form_help">Enter your mobile money phone number</small>
						</div>
					</div>

					<div class="payment_instructions">
						<div class="instruction_icon">📱</div>
						<div class="instruction_text">
							<h4>Payment Instructions</h4>
							<p>After clicking "Pay Now", you will receive a payment request on your phone. Follow the prompts to complete the payment.</p>
						</div>
					</div>

					<div class="modal_actions">
						<button @click="close_payment_modal" class="action_btn secondary_btn" :disabled="is_processing_payment">
							Cancel
						</button>
						<button 
							@click="process_invoice_payment" 
							class="action_btn pay_btn"
							:disabled="!mm_network || !mm_phone || is_processing_payment"
						>
							<span v-if="is_processing_payment" class="loading_spinner_small"></span>
							{{ is_processing_payment ? 'Processing...' : 'Pay Now' }}
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use_auth_store } from '../stores/auth'
import { toast_success, toast_error } from '../lib/toast'
import { set_seo } from '../lib/seo'
import { get_invoices, complete_mobile_money_payment } from '../services/api'
import { useScrollToTop } from '../composables/useScrollToTop'

// Use scroll to top composable
useScrollToTop()

// SEO
set_seo({
	title: 'My Invoices - BottlePlug',
	description: 'View and manage your invoices on BottlePlug'
})

// State
const auth_store = use_auth_store()
const loading = ref(true)
const error = ref('')
const invoices = ref([])
const status_filter = ref('')
const show_invoice_modal = ref(false)
const selected_invoice = ref(null)
const show_payment_modal = ref(false)
const mm_network = ref('')
const mm_phone = ref('')
const is_processing_payment = ref(false)

// Computed
const filtered_invoices = computed(() => {
	if (!status_filter.value) return invoices.value
	return invoices.value.filter(invoice => invoice.status === status_filter.value)
})

// Methods
const load_invoices = async () => {
	try {
		loading.value = true
		error.value = ''
		
		const response = await get_invoices()
		invoices.value = response.results || response || []
		
		console.log('Invoices loaded:', invoices.value)
	} catch (err) {
		console.error('Failed to load invoices:', err)
		error.value = 'Failed to load invoices. Please try again.'
		toast_error('Failed to load invoices')
	} finally {
		loading.value = false
	}
}

const filter_invoices = () => {
	// Filter is handled by computed property
}

const view_invoice = (invoice) => {
	selected_invoice.value = invoice
	show_invoice_modal.value = true
}

const close_invoice_modal = () => {
	show_invoice_modal.value = false
	selected_invoice.value = null
}

const pay_invoice = (invoice) => {
	// Close invoice modal if open
	close_invoice_modal()
	
	// Set selected invoice for payment
	selected_invoice.value = invoice
	
	// Show payment modal
	show_payment_modal.value = true
}

const close_payment_modal = () => {
	show_payment_modal.value = false
	selected_invoice.value = null
	mm_network.value = ''
	mm_phone.value = ''
	is_processing_payment.value = false
}

const process_invoice_payment = async () => {
	if (!selected_invoice.value || !mm_network.value || !mm_phone.value) {
		toast_error('Please fill in all payment details')
		return
	}
	
	try {
		is_processing_payment.value = true
		
		// Prepare payment data for Flutterwave v4 - Payment is for the order
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
				amount: Math.round(Number(selected_invoice.value.balance_due)), // Round off to integer
				currency: 'UGX',
				reference: `order${selected_invoice.value.order?.id || selected_invoice.value.id}${Date.now()}${Math.random().toString(36).substr(2, 9)}`
			},
			order_id: selected_invoice.value.order?.id, // Payment is for the order
			invoice_id: selected_invoice.value.id, // Keep invoice reference for tracking
			order_data: {
				order_number: selected_invoice.value.order?.order_number || 'N/A',
				invoice_number: selected_invoice.value.invoice_number,
				balance_due: selected_invoice.value.balance_due,
				payment_type: 'invoice_payment'
			}
		}
		
		console.log('🔍 Invoice payment data:', payment_data)
		const payment_response = await complete_mobile_money_payment(payment_data)
		
		console.log('🔍 Invoice payment response:', payment_response)
		
		if (payment_response?.success) {
			// Check if payment requires user action
			if (payment_response?.data?.next_action?.type === 'payment_instruction') {
				// Show payment instructions to user
				const instruction = payment_response?.data?.note || payment_response?.data?.instructions?.note || 'Please complete the payment on your mobile device'
				toast_success(`Payment initiated! ${instruction}`)
				
				// Close payment modal and refresh invoices
				close_payment_modal()
				await load_invoices()
			} else if (payment_response?.data?.status === 'successful') {
				// Payment successful
				toast_success('Payment successful! Your invoice has been updated.')
				close_payment_modal()
				await load_invoices()
			} else {
				// Payment initiated but status unclear
				const instruction = payment_response?.data?.note || 'Please check your mobile device for payment instructions.'
				toast_success(`Payment initiated! ${instruction}`)
				close_payment_modal()
				await load_invoices()
			}
		} else {
			// Payment failed
			const error_message = payment_response?.error || 'Payment initiation failed. Please try again.'
			toast_error(error_message)
		}
	} catch (error) {
		console.error('Invoice payment error:', error)
		toast_error('Payment failed. Please try again.')
	} finally {
		is_processing_payment.value = false
	}
}

const format_date = (date_string) => {
	if (!date_string) return 'N/A'
	const date = new Date(date_string)
	return date.toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	})
}

const format_currency = (amount) => {
	if (!amount) return '0'
	return new Intl.NumberFormat('en-US').format(amount)
}

const get_status_class = (status) => {
	switch (status) {
		case 'paid': return 'status_paid'
		case 'sent': return 'status_sent'
		case 'overdue': return 'status_overdue'
		case 'draft': return 'status_draft'
		default: return 'status_default'
	}
}

const get_status_text = (status) => {
	switch (status) {
		case 'paid': return 'Paid'
		case 'sent': return 'Sent'
		case 'overdue': return 'Overdue'
		case 'draft': return 'Draft'
		default: return 'Unknown'
	}
}

// Lifecycle
onMounted(async () => {
	await load_invoices()
})
</script>

<style scoped>
.invoices_page {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.page_header {
	background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%);
	color: white;
	padding: 60px 0;
	text-align: center;
}

.header_content {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

.page_title {
	font-size: 2.5rem;
	font-weight: 700;
	margin-bottom: 10px;
}

.page_subtitle {
	font-size: 1.1rem;
	opacity: 0.9;
}

.page_content {
	max-width: 1200px;
	margin: 0 auto;
	padding: 40px 20px;
}

.invoices_container {
	background: white;
	border-radius: 16px;
	padding: 30px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* Loading State */
.loading_state {
	text-align: center;
	padding: 60px 20px;
}

.loading_spinner {
	width: 40px;
	height: 40px;
	border: 4px solid #f3f3f3;
	border-top: 4px solid #DAA520;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin: 0 auto 20px;
}

@keyframes spin {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}

/* Error State */
.error_state {
	text-align: center;
	padding: 60px 20px;
}

.error_icon {
	font-size: 3rem;
	margin-bottom: 20px;
}

.error_state h3 {
	color: #dc2626;
	margin-bottom: 10px;
}

.retry_btn {
	background: #DAA520;
	color: white;
	border: none;
	padding: 12px 24px;
	border-radius: 8px;
	font-weight: 600;
	cursor: pointer;
	margin-top: 20px;
}

/* Empty State */
.empty_state {
	text-align: center;
	padding: 60px 20px;
}

.empty_icon {
	font-size: 4rem;
	margin-bottom: 20px;
}

.empty_state h3 {
	color: #6b7280;
	margin-bottom: 10px;
}

.browse_btn {
	background: #DAA520;
	color: white;
	text-decoration: none;
	padding: 12px 24px;
	border-radius: 8px;
	font-weight: 600;
	display: inline-block;
	margin-top: 20px;
}

/* Invoices List */
.invoices_header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30px;
}

.invoices_header h2 {
	color: #1a0f0f;
	font-size: 1.5rem;
	font-weight: 600;
}

.filter_controls {
	display: flex;
	gap: 10px;
}

.filter_select {
	padding: 8px 12px;
	border: 1px solid #d1d5db;
	border-radius: 8px;
	background: white;
	font-size: 14px;
}

.invoices_grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
	gap: 20px;
}

.invoice_card {
	background: white;
	border: 1px solid #e5e7eb;
	border-radius: 12px;
	padding: 20px;
	transition: all 0.3s ease;
}

.invoice_card:hover {
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
	transform: translateY(-2px);
}

.invoice_card.overdue {
	border-left: 4px solid #dc2626;
}

.invoice_header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 15px;
}

.invoice_info h3 {
	color: #1a0f0f;
	font-size: 1.1rem;
	font-weight: 600;
	margin-bottom: 5px;
}

.invoice_date {
	color: #6b7280;
	font-size: 0.9rem;
}

.status_badge {
	padding: 4px 8px;
	border-radius: 6px;
	font-size: 0.8rem;
	font-weight: 600;
	text-transform: uppercase;
}

.status_paid {
	background: #dcfce7;
	color: #166534;
}

.status_sent {
	background: #dbeafe;
	color: #1e40af;
}

.status_overdue {
	background: #fecaca;
	color: #dc2626;
}

.status_draft {
	background: #f3f4f6;
	color: #6b7280;
}

.invoice_details {
	margin-bottom: 20px;
}

.detail_row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 8px;
}

.detail_label {
	color: #6b7280;
	font-size: 0.9rem;
}

.detail_value {
	font-weight: 600;
	color: #1a0f0f;
}

.detail_value.amount {
	font-size: 1rem;
}

.detail_value.paid {
	color: #16a34a;
}

.detail_value.due {
	color: #dc2626;
}

.invoice_actions {
	display: flex;
	gap: 10px;
}

.action_btn {
	display: flex;
	align-items: center;
	gap: 6px;
	padding: 8px 16px;
	border: none;
	border-radius: 8px;
	font-size: 0.9rem;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
}

.view_btn {
	background: #f3f4f6;
	color: #374151;
}

.view_btn:hover {
	background: #e5e7eb;
}

.pay_btn {
	background: #DAA520;
	color: white;
}

.pay_btn:hover {
	background: #B8860B;
}

.btn_icon {
	font-size: 0.8rem;
}

/* Modal */
.modal_overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
	padding: 20px;
}

.modal_content {
	background: white;
	border-radius: 12px;
	max-width: 500px;
	width: 100%;
	max-height: 90vh;
	overflow-y: auto;
}

.modal_header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20px;
	border-bottom: 1px solid #e5e7eb;
}

.modal_header h2 {
	color: #1a0f0f;
	font-size: 1.3rem;
	font-weight: 600;
}

.close_btn {
	background: none;
	border: none;
	font-size: 1.5rem;
	color: #6b7280;
	cursor: pointer;
	padding: 0;
	width: 30px;
	height: 30px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.modal_body {
	padding: 20px;
}

.invoice_summary {
	margin-bottom: 20px;
}

.summary_row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 10px;
}

.summary_label {
	color: #6b7280;
	font-size: 0.9rem;
}

.summary_value {
	font-weight: 600;
	color: #1a0f0f;
}

.invoice_amounts {
	background: #f9fafb;
	border-radius: 8px;
	padding: 15px;
	margin-bottom: 20px;
}

.amount_row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 8px;
}

.amount_row:last-child {
	margin-bottom: 0;
}

.amount_label {
	color: #6b7280;
	font-size: 0.9rem;
}

.amount_value {
	font-weight: 600;
	font-size: 1rem;
	color: #1a0f0f;
}

.amount_value.paid {
	color: #16a34a;
}

.amount_value.due {
	color: #dc2626;
}

.modal_actions {
	display: flex;
	gap: 10px;
	justify-content: flex-end;
}

.secondary_btn {
	background: #f3f4f6;
	color: #374151;
}

.secondary_btn:hover {
	background: #e5e7eb;
}

/* Payment Modal Styles */
.payment_modal {
	max-width: 500px;
}

.payment_summary {
	background: #f9fafb;
	border-radius: 8px;
	padding: 20px;
	margin-bottom: 20px;
	text-align: center;
}

.payment_info h3 {
	color: #1a0f0f;
	font-size: 1.2rem;
	font-weight: 600;
	margin-bottom: 8px;
}

.payment_subtitle {
	color: #6b7280;
	font-size: 0.9rem;
	margin-bottom: 10px;
}

.payment_amount {
	color: #6b7280;
	font-size: 1rem;
}

.payment_amount strong {
	color: #DAA520;
	font-size: 1.1rem;
}

.payment_form {
	margin-bottom: 20px;
}

.form_group {
	margin-bottom: 20px;
}

.form_group label {
	display: block;
	margin-bottom: 6px;
	color: #374151;
	font-weight: 600;
	font-size: 0.9rem;
}

.form_input {
	width: 100%;
	padding: 12px;
	border: 1px solid #d1d5db;
	border-radius: 8px;
	font-size: 1rem;
	transition: border-color 0.3s ease;
}

.form_input:focus {
	outline: none;
	border-color: #DAA520;
	box-shadow: 0 0 0 3px rgba(218, 165, 32, 0.1);
}

.form_help {
	display: block;
	margin-top: 4px;
	color: #6b7280;
	font-size: 0.8rem;
}

.payment_instructions {
	background: #fef3c7;
	border: 1px solid #f59e0b;
	border-radius: 8px;
	padding: 15px;
	margin-bottom: 20px;
	display: flex;
	align-items: flex-start;
	gap: 12px;
}

.instruction_icon {
	font-size: 1.5rem;
	flex-shrink: 0;
}

.instruction_text h4 {
	color: #92400e;
	font-size: 0.9rem;
	font-weight: 600;
	margin-bottom: 5px;
}

.instruction_text p {
	color: #92400e;
	font-size: 0.85rem;
	line-height: 1.4;
	margin: 0;
}

.loading_spinner_small {
	width: 16px;
	height: 16px;
	border: 2px solid transparent;
	border-top: 2px solid currentColor;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	display: inline-block;
	margin-right: 8px;
}

.action_btn:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}

.action_btn:disabled:hover {
	transform: none;
	box-shadow: none;
}

/* Responsive */
@media (max-width: 768px) {
	.invoices_grid {
		grid-template-columns: 1fr;
	}
	
	.invoices_header {
		flex-direction: column;
		align-items: flex-start;
		gap: 15px;
	}
	
	.invoice_actions {
		flex-direction: column;
	}
	
	.modal_actions {
		flex-direction: column;
	}
	
	.payment_modal {
		margin: 10px;
		max-width: calc(100vw - 20px);
	}
}
</style>
