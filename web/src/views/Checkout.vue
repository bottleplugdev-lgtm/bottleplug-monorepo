<template>
	<div class="page_container">
		<!-- Auth Loading State -->
		<AuthLoading v-if="is_auth_loading" />
		
		<!-- Main Content (only show when auth is ready and user is authenticated) -->
		<template v-else-if="should_show_content">
			<!-- Progress Header -->
			<div class="card p-3 mb-3">
				<ol class="progress">
					<li class="done">Cart</li>
					<li class="active">Payment</li>
					<li>Complete</li>
				</ol>
			</div>
			<h1 class="title">Checkout</h1>
			<p v-if="user_email" class="text-neutral-600 mb-2">Signed in as {{ user_email }}</p>
			
			<!-- Empty Cart State -->
			<div v-if="!cart.is_loading && !cart.items.length" class="empty_checkout">
				<div class="empty_illustration">
					<div class="empty_icon">🛒</div>
					<div class="empty_icon_secondary">💳</div>
				</div>
				<h2 class="empty_title">Your Cart is Empty</h2>
				<p class="empty_text">
					You need to add items to your cart before proceeding to checkout. 
					Browse our premium collection and add your favorite wines and spirits to continue.
				</p>
				<div class="empty_actions">
					<RouterLink to="/products" class="shop_now_btn">
						<span class="btn_icon">🍷</span>
						Browse Products
					</RouterLink>
					<RouterLink to="/cart" class="view_cart_btn">
						<span class="btn_icon">🛒</span>
						View Cart
					</RouterLink>
				</div>
			</div>
			
			<!-- Checkout Content -->
			<div v-else class="grid">
				<div class="card p-4">
					<h2 class="subtitle">Cart Items ({{ cart.total_quantity }})</h2>
					<div v-if="cart.is_loading">Loading cart...</div>
					<div v-else>
						<div v-for="item in cart.items" :key="item.id || item.product" class="item_row">
							<div class="item_image_container">
								<img 
									:src="image_url(item.product_image || item.product_detail?.image || item.image)" 
									:alt="item.product_name || item.product_detail?.name" 
									class="item_image"
									@error="handle_image_error"
								/>
							</div>
							<div class="item_details">
							<div class="item_name">{{ item.product_name || item.product_detail?.name || 'Item' }}</div>
								<div class="item_qty">Qty: {{ item.quantity }}</div>
							</div>
							<div class="item_price">{{ format_price(cart.get_item_total(item)) }}</div>
						</div>
						<div class="total_row">
							<span>Total</span>
							<strong>{{ format_price(cart.total_amount) }}</strong>
						</div>
					</div>
				</div>
				<div class="card p-4 mobile_money_container">
					<h2 class="subtitle">Mobile Money Payment</h2>
					<div class="payment_info">
						<p class="payment_description">Pay securely with your mobile money account</p>
					</div>
					<div class="mm_form">
						<label>Select Network
							<select v-model="mm_network" class="input w-full" required>
								<option value="">Choose your network</option>
								<option value="mtn">MTN Mobile Money</option>
								<option value="airtel">Airtel Money</option>
							</select>
						</label>
						<label>Phone Number
							<input 
								v-model="mm_phone" 
								class="input phone_input" 
								placeholder="256XXXXXXXXX or 07XXXXXXXX" 
								@input="format_phone_number"
								required
							/>
							<small class="phone_hint">Enter your mobile money registered phone number</small>
						</label>
						<div class="payment_summary">
							<div class="summary_row">
								<span>Amount to Pay:</span>
								<strong class="amount">{{ format_price(estimated_total) }}</strong>
							</div>
							<div class="summary_row" v-if="mm_network">
								<span>Via {{ mm_network.toUpperCase() }} Mobile Money</span>
							</div>
						</div>
					</div>
					<div class="delivery_section">
						<label class="delivery_label">Delivery Address
							<input v-model="address" class="input delivery_input address_input" placeholder="Street, City" />
						</label>
						<label class="delivery_label">Delivery Option
							<select v-model="delivery_option" class="input delivery_input">
								<option value="standard">Standard</option>
								<option value="express">Express</option>
							</select>
						</label>
						<label class="delivery_label">Coupon Code
							<div class="coupon_container">
								<input v-model="coupon" class="input coupon_input" placeholder="Enter code" />
								<button type="button" class="coupon_btn" @click="apply_coupon" :disabled="!coupon">Apply</button>
							</div>
						</label>
						<div class="text-sm text-neutral-700">
							<span v-if="coupon_discount > 0">Coupon Discount: </span>
							<strong v-if="coupon_discount > 0" class="text-green-700">-{{ format_price(coupon_discount) }}</strong>
							<br />
							<span>Delivery Fee: </span><strong>{{ format_price(delivery_fee) }}</strong>
							<span class="ml-3">Estimated Total: </span><strong>{{ format_price(estimated_total) }}</strong>
						</div>
					</div>
					<button class="pay_btn" :disabled="!can_proceed_to_payment" @click="checkout_and_pay">
						{{ is_processing ? 'Processing...' : `Pay ${format_price(estimated_total)} with Mobile Money` }}
					</button>
				</div>
				<div>
					<OrderSummary :subtotal="cart.total_amount" :delivery_fee="delivery_fee" :coupon_discount="coupon_discount">
						<button class="btn" style="width:100%; margin-top:12px" :disabled="!can_proceed_to_payment" @click="checkout_and_pay">
							{{ is_processing ? 'Processing...' : `Pay ${format_price(estimated_total)}` }}
						</button>
					</OrderSummary>
				</div>
			</div>
		</template>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use_auth_store } from '../stores/auth'
import { use_cart_store } from '../stores/cart'
import { complete_mobile_money_payment } from '../services/api'
import { toast_success, toast_error } from '../lib/toast'
import { set_seo } from '../lib/seo'
import OrderSummary from '../components/OrderSummary.vue'
import AuthLoading from '../components/AuthLoading.vue'

const auth_store = use_auth_store()
const user_email = computed(() => auth_store.firebase_user?.email || '')
const cart = use_cart_store()
const mm_network = ref('')
const mm_phone = ref('')
const is_processing = ref(false)
const is_auth_loading = ref(true)
const should_show_content = computed(() => !is_auth_loading.value && auth_store.is_authenticated)
const address = ref('')
const delivery_option = ref('standard')
const coupon = ref('')
const delivery_fee = computed(() => delivery_option.value === 'express' ? 5000 : 0)
const coupon_discount = ref(0)
const estimated_total = computed(() => Math.max(0, (Number(cart.total_amount || 0) + Number(delivery_fee.value || 0) - Number(coupon_discount.value || 0))))

// Mobile money validation
const can_proceed_to_payment = computed(() => {
	return mm_network.value && 
		   mm_phone.value && 
		   address.value && 
		   cart.total_amount > 0 &&
		   !is_processing.value
})

async function apply_coupon() {
	try {
		// optimistic apply: let backend validate during checkout
		coupon_discount.value = Math.round((Number(cart.total_amount || 0)) * 0.05)
		toast_success('Coupon applied')
		if (window?.gtag) window.gtag('event', 'coupon_applied', { coupon: coupon.value })
	} catch (_) {
		coupon_discount.value = 0
		toast_error('Invalid coupon')
	}
}

onMounted(async () => {
	// Wait for auth to be ready
	if (auth_store.should_show_loading) {
		// Wait for auth to initialize (max 3 seconds)
		let attempts = 0
		const max_attempts = 30 // 30 * 100ms = 3 seconds
		
		while (auth_store.should_show_loading && attempts < max_attempts) {
			await new Promise(resolve => setTimeout(resolve, 100))
			attempts++
		}
	}
	
	is_auth_loading.value = false
	await cart.fetch_cart()
	
	// Debug: Log checkout cart data
	console.log('🛒 Checkout cart items loaded:', cart.items.length)
	cart.items.forEach((item, index) => {
		console.log(`🛒 Checkout item ${index}:`, {
			id: item.id,
			product: item.product,
			product_name: item.product_name,
			product_image: item.product_image,
			product_detail: item.product_detail,
			image: item.image,
			quantity: item.quantity
		})
		
		// Debug: Log image paths specifically
		console.log(`🖼️ Checkout item ${index} image paths:`, {
			'item.product_image': item.product_image,
			'item.product_detail?.image': item.product_detail?.image,
			'item.image': item.image,
			'final_image_path': item.product_image || item.product_detail?.image || item.image
		})
	})
	
	set_seo({ title: 'Checkout · Bottleplug', description: 'Secure checkout with mobile money and cards.' })
})

function format_price(value) {
	const amount = Number(value) || 0
	return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', minimumFractionDigits: 0 }).format(amount)
}

function format_phone_number() {
	// Format phone number to Uganda format
	let phone = mm_phone.value.replace(/\D/g, '') // Remove non-digits
	
	if (phone.startsWith('256')) {
		// Already in international format
		mm_phone.value = phone
	} else if (phone.startsWith('0')) {
		// Convert from local format (07XXXXXXXX) to international (256XXXXXXXX)
		mm_phone.value = '256' + phone.substring(1)
	} else if (phone.length === 9) {
		// Add 256 prefix if missing
		mm_phone.value = '256' + phone
	} else {
		mm_phone.value = phone
	}
}

function image_url(image_path) {
	console.log('🖼️ Checkout image_url called with path:', image_path)
	
	if (!image_path) {
		console.log('🖼️ No path provided, using logo fallback')
		return '/bottleplug_logo.png'
	}
	
	if (image_path.startsWith('http')) {
		console.log('🖼️ Full URL detected:', image_path)
		return image_path
	}
	
	const backend_url = import.meta.env.VITE_API_BASE_URL || 'https://api.bottleplugug.com'
	const clean_path = image_path.replace(/^\/?media\//, '')
	const final_url = `${backend_url}/media/${clean_path}`
	console.log('🖼️ Constructed checkout image URL:', final_url)
	return final_url
}

function handle_image_error(event) {
	console.log('❌ Checkout image failed to load:', event.target.src)
	console.log('🔄 Switching to logo fallback')
	event.target.src = '/bottleplug_logo.png'
}

async function checkout_and_pay() {
	try {
		// Validate required fields
		if (!can_proceed_to_payment.value) {
			toast_error('Please fill in all required fields')
			return
		}

		// Debug: Log authentication status
		console.log('🔐 Checkout auth status:', {
			is_authenticated: auth_store.is_authenticated,
			is_anonymous: auth_store.is_anonymous,
			firebase_user: auth_store.firebase_user,
			cart_items: cart.items.length
		})

		is_processing.value = true
		if (window?.gtag) window.gtag('event', 'begin_checkout')

		// Step 1: Create order from cart
		const order_data = {
			payment_method: 'mobile_money',
			is_pickup: false,
			delivery_address: address.value,
			delivery_instructions: delivery_option.value === 'express' ? 'Express delivery requested' : 'Standard delivery',
			delivery_fee: delivery_fee.value,
			notes: coupon.value ? `Coupon applied: ${coupon.value}` : '',
			customer_phone: mm_phone.value.replace(/^\+?256/, '') // Add phone number to order data
		}
		
		const order = await cart.checkout(order_data)
		console.log('🔍 Order response:', order)
		
		const order_id = order?.order?.id || order?.id || order?.order_id || order?.data?.id
		const raw_amount = order?.order?.total_amount || order?.total_amount || order?.total || estimated_total.value
		const amount = Math.round(Number(raw_amount)) // Round off to integer
		
		console.log('🔍 Extracted order_id:', order_id, 'raw_amount:', raw_amount, 'amount (rounded):', amount)
		
		// Step 2: Complete mobile money payment flow
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
				amount: amount,
				currency: 'UGX',
				reference: `payment${Date.now()}${Math.random().toString(36).substr(2, 9)}`
			},
			order_id: order_id
		}
		
		console.log('🔍 Mobile money payment data:', payment_data)
		const payment_response = await complete_mobile_money_payment(payment_data)
		
		// Step 3: Handle payment response
		console.log('🔍 Payment response:', payment_response)
		
		if (payment_response?.success) {
			// Check if payment requires user action
			if (payment_response?.data?.next_action?.type === 'payment_instruction') {
				// Show payment instructions to user
				const instruction = payment_response?.data?.note || payment_response?.data?.instructions?.note || 'Please complete the payment on your mobile device'
				toast_success(`Payment initiated! ${instruction}`)
				
				// Redirect to order success page with payment pending status
				window.location.href = `/order-success?order_id=${order_id}&payment_status=pending`
			} else if (payment_response?.data?.status === 'successful') {
				// Payment successful
				toast_success('Payment successful! Your order is being processed.')
				window.location.href = `/order-success?order_id=${order_id}`
			} else {
				// Payment initiated but status unclear
				const instruction = payment_response?.data?.note || 'Please check your mobile device for payment instructions.'
				toast_success(`Payment initiated! ${instruction}`)
				window.location.href = `/order-success?order_id=${order_id}&payment_status=pending`
			}
		} else {
			// Payment failed
			const error_message = payment_response?.error || 'Payment initiation failed. Please try again.'
			toast_error(error_message)
		}
		
	} catch (error) {
		console.error('Checkout error:', error)
		
		// Handle specific error cases
		if (error.response?.status === 401) {
			toast_error('Please sign in to complete your order.')
			// Redirect to login page
			setTimeout(() => {
				window.location.href = '/login'
			}, 2000)
		} else if (error.response?.data?.error) {
			toast_error(error.response.data.error)
		} else {
			toast_error('Checkout failed. Please try again.')
		}
	} finally {
		is_processing.value = false
	}
}
</script>

<style scoped>
.page_container { 
	padding: 32px 24px; 
	max-width: 1200px; 
	margin: 0 auto; 
	background: #f8fafc;
	min-height: 100vh;
}

.title { 
	font-size: 28px; 
	font-weight: 700; 
	margin-bottom: 20px; 
	color: #1e293b;
}

/* Empty Checkout State */
.empty_checkout {
	text-align: center;
	padding: 80px 20px;
	background: white;
	border-radius: 20px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid #e2e8f0;
	max-width: 600px;
	margin: 0 auto;
}

.empty_illustration {
	position: relative;
	margin-bottom: 32px;
}

.empty_icon {
	font-size: 80px;
	margin-bottom: 16px;
	opacity: 0.8;
}

.empty_icon_secondary {
	font-size: 40px;
	position: absolute;
	top: 20px;
	right: 50%;
	transform: translateX(50%);
	opacity: 0.6;
	animation: float 3s ease-in-out infinite;
}

@keyframes float {
	0%, 100% { transform: translateX(50%) translateY(0px); }
	50% { transform: translateX(50%) translateY(-10px); }
}

.empty_title {
	font-size: 28px;
	font-weight: 700;
	color: #1e293b;
	margin-bottom: 16px;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.empty_text {
	color: #64748b;
	font-size: 16px;
	line-height: 1.6;
	margin-bottom: 32px;
	max-width: 500px;
	margin-left: auto;
	margin-right: auto;
}

.empty_actions {
	display: flex;
	gap: 16px;
	justify-content: center;
	flex-wrap: wrap;
}

.shop_now_btn {
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

.shop_now_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.view_cart_btn {
	background: white;
	color: #DAA520;
	border: 2px solid #DAA520;
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

.view_cart_btn:hover {
	transform: translateY(-2px);
	background: #DAA520;
	color: white;
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.btn_icon {
	font-size: 16px;
}

.grid { 
	display: grid; 
	grid-template-columns: 2fr 1fr; 
	gap: 24px; 
}

.card { 
	border: 1px solid #e2e8f0; 
	border-radius: 20px; 
	padding: 32px; 
	background: #fff; 
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	transition: box-shadow 0.2s ease;
}

.card:hover {
	box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.subtitle { 
	font-size: 20px; 
	font-weight: 600; 
	margin-bottom: 16px; 
	color: #1e293b;
}

.item_row { 
	display: flex; 
	align-items: center; 
	gap: 16px; 
	padding: 20px 0; 
	border-bottom: 1px solid #f1f5f9; 
	transition: background-color 0.2s ease;
}

.item_row:hover {
	background-color: #f8fafc;
	border-radius: 8px;
	margin: 0 -8px;
	padding: 20px 8px;
}

.item_image_container {
	width: 60px;
	height: 60px;
	border-radius: 8px;
	overflow: hidden;
	flex-shrink: 0;
}

.item_image {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.item_details {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.item_name { 
	font-weight: 600; 
	font-size: 16px;
	color: #1e293b;
}

.item_qty { 
	color: #64748b; 
	font-size: 14px;
}

.item_price { 
	font-weight: 700; 
	font-size: 16px;
	color: #059669;
	min-width: 100px;
	text-align: right;
}

.total_row { 
	display: flex; 
	align-items: center; 
	justify-content: space-between; 
	padding: 24px; 
	border-top: 2px solid #e2e8f0;
	margin-top: 24px;
	font-size: 20px;
	font-weight: 700;
	color: #1e293b;
	background: #f8fafc;
	border-radius: 12px;
	margin: 24px -8px 0 -8px;
}
.pay_methods { 
	display: flex; 
	gap: 12px; 
	margin-bottom: 20px; 
}

.mm_form { 
	display: grid; 
	gap: 24px; 
	margin-bottom: 32px; 
	overflow: hidden;
}

.mm_form label {
	display: flex;
	flex-direction: column;
	gap: 12px;
	font-weight: 600;
	color: #374151;
	font-size: 15px;
}

.mm_form .input {
	padding: 14px 16px;
	border: 2px solid #e5e7eb;
	border-radius: 10px;
	font-size: 16px;
	transition: all 0.2s ease;
	background: #fafafa;
	width: 100%;
	box-sizing: border-box;
}

.mm_form .input:focus {
	outline: none;
	border-color: #3b82f6;
	box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	background: #fff;
}

.mm_form .input:hover {
	border-color: #d1d5db;
	background: #fff;
}

.delivery_section {
	margin-top: 32px;
	display: flex;
	flex-direction: column;
	gap: 24px;
	overflow: hidden;
}

.delivery_label {
	display: flex;
	flex-direction: column;
	gap: 12px;
	font-weight: 600;
	color: #374151;
	font-size: 15px;
}

.delivery_input {
	padding: 14px 16px;
	border: 2px solid #e5e7eb;
	border-radius: 10px;
	font-size: 16px;
	transition: all 0.2s ease;
	background: #fafafa;
	width: 100%;
	box-sizing: border-box;
}

.delivery_input:focus {
	outline: none;
	border-color: #3b82f6;
	box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	background: #fff;
}

.delivery_input:hover {
	border-color: #d1d5db;
	background: #fff;
}

.coupon_container {
	display: flex;
	gap: 12px;
	align-items: stretch;
	overflow: hidden;
}

.coupon_input {
	flex: 1;
	padding: 14px 16px;
	border: 2px solid #e5e7eb;
	border-radius: 10px;
	font-size: 16px;
	transition: all 0.2s ease;
	background: #fafafa;
	box-sizing: border-box;
	min-width: 0;
}

.coupon_input:focus {
	outline: none;
	border-color: #3b82f6;
	box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	background: #fff;
}

.coupon_input:hover {
	border-color: #d1d5db;
	background: #fff;
}

.coupon_btn {
	background: #3b82f6;
	color: #fff;
	border: 0;
	padding: 14px 20px;
	border-radius: 10px;
	cursor: pointer;
	font-weight: 600;
	font-size: 16px;
	transition: all 0.2s ease;
	white-space: nowrap;
}

.coupon_btn:hover:not(:disabled) {
	background: #2563eb;
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.coupon_btn:disabled {
	background: #9ca3af;
	cursor: not-allowed;
	transform: none;
	box-shadow: none;
}

.phone_input {
	/* Removed margin-right to prevent overflow */
}

.address_input {
	/* Removed margin-right to prevent overflow */
}

.mobile_money_container {
	padding-right: 24px;
}
.pay_btn { 
	background: linear-gradient(135deg, #16a34a, #15803d); 
	color: #fff; 
	border: 0; 
	padding: 16px 24px; 
	border-radius: 12px; 
	cursor: pointer; 
	width: 100%; 
	font-weight: 700;
	font-size: 18px;
	transition: all 0.2s ease;
	box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
	margin-top: 8px;
}

.pay_btn:hover:not(:disabled) {
	background: linear-gradient(135deg, #15803d, #166534);
	transform: translateY(-2px);
	box-shadow: 0 6px 16px rgba(22, 163, 74, 0.4);
}

.pay_btn:disabled {
	background: #9ca3af;
	cursor: not-allowed;
	transform: none;
	box-shadow: none;
}

.payment_info {
	margin-bottom: 28px;
	padding: 20px;
	background: #f0f9ff;
	border-radius: 12px;
	border-left: 4px solid #0ea5e9;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.payment_description {
	color: #0369a1;
	font-size: 14px;
	margin: 0;
}

.phone_hint {
	color: #6b7280;
	font-size: 12px;
	margin-top: 4px;
	display: block;
}

.payment_summary {
	margin-top: 16px;
	padding: 12px;
	background: #f9fafb;
	border-radius: 8px;
	border: 1px solid #e5e7eb;
}

.payment_summary {
	background: #f8fafc;
	border-radius: 12px;
	padding: 20px;
	margin: 24px 0;
	border: 1px solid #e2e8f0;
}

.payment_summary .summary_row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12px;
	font-size: 16px;
}

.payment_summary .summary_row:last-child {
	margin-bottom: 0;
}

.payment_summary .amount {
	color: #16a34a;
	font-size: 24px;
	font-weight: 700;
}

.progress { 
	display: grid; 
	grid-template-columns: repeat(3, 1fr); 
	gap: 8px; 
}

.progress li { 
	text-align: center; 
	padding: 8px 12px; 
	border-radius: 999px; 
	background: #f3f4f6; 
	color: #374151; 
	font-weight: 600; 
	font-size: 14px;
}

.progress li.active { 
	background: #f7e680; 
	color: #111827; 
}

.progress li.done { 
	background: #16a34a; 
	color: #fff; 
}

/* Responsive Design */
@media (max-width: 768px) {
	.page_container {
		padding: 16px;
	}
	
	.grid {
		grid-template-columns: 1fr;
		gap: 16px;
	}
	
	.card {
		padding: 16px;
	}
	
	.title {
		font-size: 24px;
		margin-bottom: 16px;
	}
	
	.subtitle {
		font-size: 18px;
		margin-bottom: 12px;
	}
	
	.item_row {
		gap: 12px;
		padding: 12px 0;
	}
	
	.item_image_container {
		width: 50px;
		height: 50px;
	}
	
	.item_name {
		font-size: 14px;
	}
	
	.item_qty {
		font-size: 12px;
	}
	
	.item_price {
		font-size: 14px;
		min-width: 80px;
	}
	
	.mm_form {
		gap: 12px;
	}
	
	.mm_form .input {
		padding: 10px 12px;
		font-size: 14px;
	}
	
	.pay_btn {
		padding: 14px 16px;
		font-size: 16px;
	}
	
	.empty_title {
		font-size: 24px;
	}
	
	.empty_text {
		font-size: 14px;
		padding: 0 10px;
	}
	
	.empty_actions {
		flex-direction: column;
		align-items: center;
	}
	
	.shop_now_btn, .view_cart_btn {
		width: 100%;
		max-width: 280px;
		justify-content: center;
	}
}
</style>
