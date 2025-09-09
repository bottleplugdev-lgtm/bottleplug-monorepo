<template>
	<div class="account_page">
		<!-- Auth Loading State -->
		<AuthLoading v-if="is_loading" />
		
		<!-- Main Content (only show when auth is ready and user is authenticated) -->
		<template v-else-if="should_show_content">
			<!-- Hero Section -->
			<section class="hero_section">
				<div class="hero_background"></div>
				<div class="hero_content">
					<h1 class="hero_title">My Account</h1>
					<p class="hero_subtitle">Manage your orders, payments, and preferences</p>
				</div>
			</section>

			<!-- Account Section -->
			<section class="account_section">
				<div class="account_container">
					<!-- Account Overview -->
					<div class="account_overview">
						<div class="user_info_card">
							<div class="user_avatar">
								<span class="avatar_icon">👤</span>
							</div>
							<div class="user_details">
								<h2 class="user_name">{{ user_name || 'Guest User' }}</h2>
								<p class="user_email">{{ user_email || 'guest@bottleplug.com' }}</p>
								<div class="user_stats">
									<div class="stat_item">
										<span class="stat_number">{{ orders.length }}</span>
										<span class="stat_label">Orders</span>
									</div>
									<div class="stat_item">
										<span class="stat_number">{{ transactions.length }}</span>
										<span class="stat_label">Payments</span>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Account Content -->
					<div class="account_content">
						<!-- Orders Section -->
						<div class="content_section">
							<div class="section_header">
								<h3 class="section_title">
									<span class="title_icon">📦</span>
									Recent Orders
								</h3>
								<RouterLink to="/order-history" class="view_all_btn">View All</RouterLink>
							</div>

							<div class="section_content">
								<div v-if="orders_loading" class="loading_state">
									<div class="loading_spinner"></div>
									<p class="loading_text">Loading orders...</p>
								</div>
								
								<div v-else-if="!orders.length" class="empty_state">
									<div class="empty_illustration">
										<div class="empty_icon">📦</div>
										<div class="empty_icon_secondary">🛍️</div>
									</div>
									<h4 class="empty_title">No Orders Yet</h4>
									<p class="empty_text">
										Your order history will appear here once you start shopping with us. 
										Discover our premium collection of wines and spirits to begin your journey.
									</p>
									<div class="empty_actions">
										<RouterLink to="/products" class="shop_now_btn">
											<span class="btn_icon">🍷</span>
											Start Shopping
										</RouterLink>
										<RouterLink to="/events" class="view_events_btn">
											<span class="btn_icon">🎉</span>
											View Events
										</RouterLink>
									</div>
								</div>
								
								<div v-else class="orders_list">
									<div v-for="order in orders.slice(0, 5)" :key="order.id" class="order_item">
										<div class="order_header">
											<div class="order_info">
												<h4 class="order_number">Order #{{ order.id }}</h4>
												<p class="order_date">{{ format_date(order.created_at) }}</p>
											</div>
											<div class="order_status">
												<span class="status_badge" :class="get_status_class(order.status)">
													{{ order.status || 'Processing' }}
												</span>
											</div>
										</div>
										
										<div class="order_details">
											<div class="order_items">
												<span class="items_count">{{ order.items_count || 0 }} items</span>
											</div>
											<div class="order_total">
												<span class="total_amount">{{ format_amount(order.total || 0) }}</span>
											</div>
											<div class="order_payment_info" v-if="order.balance_display">
												<div class="payment_row">
													<span class="payment_label">Paid:</span>
													<span class="payment_amount paid">{{ format_amount(order.paid_amount || 0) }}</span>
												</div>
												<div class="payment_row">
													<span class="payment_label">Balance:</span>
													<span :class="['payment_amount', order.payment_status_class]">
														{{ order.balance_display }}
													</span>
												</div>
											</div>
										</div>
										
										<div class="order_actions">
											<button @click="view_order_details(order)" class="view_order_btn">
												<span class="btn_icon">👁️</span>
												View Details
											</button>
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- Payments Section -->
						<div class="content_section">
							<div class="section_header">
								<h3 class="section_title">
									<span class="title_icon">💳</span>
									Payment History
								</h3>
								<RouterLink to="/payments" class="view_all_btn">View All</RouterLink>
							</div>

							<div class="section_content">
								<div v-if="tx_loading" class="loading_state">
									<div class="loading_spinner"></div>
									<p class="loading_text">Loading payments...</p>
								</div>
								
								<div v-else-if="!transactions.length" class="empty_state">
									<div class="empty_illustration">
										<div class="empty_icon">💳</div>
										<div class="empty_icon_secondary">💰</div>
									</div>
									<h4 class="empty_title">No Payment History Yet</h4>
									<p class="empty_text">
										Your payment transactions will appear here once you make your first purchase. 
										All your payment history will be securely stored and easily accessible.
									</p>
									<div class="empty_actions">
										<RouterLink to="/products" class="shop_now_btn">
											<span class="btn_icon">🍷</span>
											Make Your First Purchase
										</RouterLink>
									</div>
								</div>
								
								<div v-else class="transactions_list">
									<div v-for="transaction in transactions.slice(0, 5)" :key="transaction.id" class="transaction_item">
										<div class="transaction_header">
											<div class="transaction_info">
												<h4 class="transaction_number">Payment #{{ transaction.id }}</h4>
												<p class="transaction_date">{{ format_date(transaction.created_at) }}</p>
											</div>
											<div class="transaction_status">
												<span class="status_badge" :class="get_payment_status_class(transaction.status)">
													{{ transaction.status || 'Pending' }}
												</span>
											</div>
										</div>
										
										<div class="transaction_details">
											<div class="transaction_method">
												<span class="method_text">{{ transaction.payment_method || 'Card' }}</span>
											</div>
											<div class="transaction_amount">
												<span class="amount_text">{{ format_amount(transaction.amount || 0) }}</span>
											</div>
										</div>
										
										<div class="transaction_actions">
											<button @click="view_payment_details(transaction)" class="view_payment_btn">
												<span class="btn_icon">👁️</span>
												View Details
											</button>
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- Quick Actions -->
						<div class="quick_actions">
							<h3 class="actions_title">Quick Actions</h3>
							<div class="actions_grid">
								<RouterLink to="/wishlist" class="action_card">
									<span class="action_icon">💝</span>
									<span class="action_text">My Wishlist</span>
								</RouterLink>
								<RouterLink to="/order-history" class="action_card">
									<span class="action_icon">📋</span>
									<span class="action_text">Order History</span>
								</RouterLink>
								<RouterLink to="/delivery-tracking" class="action_card">
									<span class="action_icon">🚚</span>
									<span class="action_text">Track Deliveries</span>
								</RouterLink>
								<RouterLink to="/events" class="action_card">
									<span class="action_icon">🎉</span>
									<span class="action_text">My Events</span>
								</RouterLink>
								<RouterLink to="/profile" class="action_card">
									<span class="action_icon">⚙️</span>
									<span class="action_text">Profile Settings</span>
								</RouterLink>
								<RouterLink to="/support" class="action_card">
									<span class="action_icon">🆘</span>
									<span class="action_text">Customer Support</span>
								</RouterLink>
							</div>
						</div>
					</div>
				</div>
			</section>
		</template>
	</div>

	<!-- Order Details Modal -->
	<div v-if="show_order_modal" class="modal_overlay" @click="close_order_modal">
		<div class="modal_content" @click.stop>
			<div class="modal_header">
				<h3>Order Details: {{ selected_order?.order_number }}</h3>
				<button @click="close_order_modal" class="modal_close">×</button>
			</div>
			
			<div v-if="selected_order" class="modal_body">
				<div v-if="loading_products" class="loading_products">
					<div class="loading_spinner"></div>
					<p>Loading product details...</p>
				</div>
				<div v-else class="order_details">
					<div class="detail_group">
						<h4>Order Information</h4>
						<div class="detail_grid">
							<div class="detail_item">
								<span class="detail_label">Order Number:</span>
								<span class="detail_value">#{{ selected_order.order_number }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Order Date:</span>
								<span class="detail_value">{{ format_date(selected_order.created_at) }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Status:</span>
								<span class="detail_value">{{ format_status(selected_order.status) }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Total Amount:</span>
								<span class="detail_value">{{ format_amount(selected_order.total_amount) }}</span>
							</div>
						</div>
					</div>

					<div class="detail_group">
						<h4>Products</h4>
						<div class="order_items_list">
							<div 
								v-for="item in selected_order.items" 
								:key="item.id" 
								class="order_item_detail"
							>
								<img 
									:src="image_url(get_product_image(item))" 
									:alt="get_product_name(item)"
									@error="handle_image_error"
									class="item_image"
								>
								<div class="item_details">
									<div class="product_header">
										<h5 class="item_name">{{ get_product_name(item) }}</h5>
										<p class="product_description">{{ get_product_description(item) }}</p>
									</div>
									<div class="product_price_display">
										<span class="product_price">{{ format_amount(item.unit_price || get_product_price(item)) }}</span>
										<span class="product_quantity">× {{ item.quantity }}</span>
									</div>
									<div class="item_info">
										<div class="item_row">
											<span class="item_label">Product:</span>
											<span class="item_value">{{ get_product_name(item) }}</span>
										</div>
										<div class="item_row">
											<span class="item_label">Unit Price:</span>
											<span class="item_value">{{ format_amount(item.unit_price || get_product_price(item)) }}</span>
										</div>
										<div class="item_row">
											<span class="item_label">Quantity:</span>
											<span class="item_value">{{ item.quantity }}</span>
										</div>
										<div class="item_row total_row">
											<span class="item_label">Total Price:</span>
											<span class="item_value total_price">{{ format_amount(item.total_price) }}</span>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>

					<div class="detail_group">
						<h4>Order Summary</h4>
						<div class="order_summary">
							<div class="summary_row">
								<span class="summary_label">Items Total:</span>
								<span class="summary_value">{{ format_amount(selected_order.items?.reduce((sum, item) => sum + (item.total_price || 0), 0)) }}</span>
							</div>
							<div class="summary_row" v-if="selected_order.delivery_fee">
								<span class="summary_label">Delivery Fee:</span>
								<span class="summary_value">{{ format_amount(selected_order.delivery_fee) }}</span>
							</div>
							<div class="summary_row" v-if="selected_order.tax">
								<span class="summary_label">Tax:</span>
								<span class="summary_value">{{ format_amount(selected_order.tax) }}</span>
							</div>
							<div class="summary_row total_summary_row">
								<span class="summary_label">Grand Total:</span>
								<span class="summary_value total_summary_value">{{ format_amount(selected_order.total_amount) }}</span>
							</div>
						</div>
					</div>

					<div class="detail_group">
						<h4>Payment Information</h4>
						<div class="detail_grid">
							<div class="detail_item">
								<span class="detail_label">Paid Amount:</span>
								<span class="detail_value">{{ format_amount(selected_order.paid_amount) }}</span>
							</div>
							<div class="detail_item">
								<span class="detail_label">Balance:</span>
								<span class="detail_value">{{ selected_order.balance_display }}</span>
							</div>
						</div>
					</div>
				</div>
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
								<span class="detail_value">{{ selected_payment.payment_method || 'Card' }}</span>
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
import { use_auth_store } from '../stores/auth'
import { use_orders_store } from '../stores/orders'
import { get_my_transactions, get_product } from '../services/api'
import { toast_error } from '../lib/toast'
import { set_seo } from '../lib/seo'
import AuthLoading from '../components/AuthLoading.vue'

const orders = ref([])
const orders_loading = ref(true)
const transactions = ref([])
const tx_loading = ref(true)
const is_loading = ref(true)
const show_order_modal = ref(false)
const selected_order = ref(null)
const product_details = ref({}) // Cache for product details
const loading_products = ref(false)
const show_payment_modal = ref(false)
const selected_payment = ref(null)

const auth_store = use_auth_store()
const orders_store = use_orders_store()
const user_name = computed(() => auth_store.firebase_user?.displayName || 'Guest User')
const user_email = computed(() => auth_store.firebase_user?.email || 'guest@bottleplug.com')
const should_show_content = computed(() => !is_loading.value && auth_store.is_authenticated)

// Set SEO
set_seo({ 
	title: 'My Account · BottlePlug', 
	description: 'Manage your BottlePlug account, view order history, payment transactions, and account preferences.' 
})

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
	
	is_loading.value = false
	
	try {
		await orders_store.fetch_my_orders()
		orders.value = orders_store.orders_with_balance.slice(0, 5)
	} catch (error) {
		console.error('Failed to load orders:', error)
		toast_error('Failed to load orders')
	} finally {
		orders_loading.value = false
	}
	
	try {
		const data2 = await get_my_transactions()
		transactions.value = data2?.results || data2 || []
	} catch (error) {
		console.error('Failed to load transactions:', error)
		toast_error('Failed to load payment history')
	} finally {
		tx_loading.value = false
	}
})

function format_amount(value) {
	const amount = Number(value) || 0
	return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', minimumFractionDigits: 0 }).format(amount)
}

function format_date(date_string) {
	if (!date_string) return 'N/A'
	const date = new Date(date_string)
	return date.toLocaleDateString('en-US', { 
		year: 'numeric', 
		month: 'short', 
		day: 'numeric' 
	})
}

function get_status_class(status) {
	const status_map = {
		'pending': 'status_pending',
		'processing': 'status_processing',
		'shipped': 'status_shipped',
		'delivered': 'status_delivered',
		'cancelled': 'status_cancelled'
	}
	return status_map[status?.toLowerCase()] || 'status_processing'
}

function get_payment_status_class(status) {
	const status_map = {
		'pending': 'status_pending',
		'completed': 'status_completed',
		'failed': 'status_failed',
		'refunded': 'status_refunded'
	}
	return status_map[status?.toLowerCase()] || 'status_pending'
}

// Modal functions
const view_order_details = async (order) => {
	selected_order.value = order
	show_order_modal.value = true
	loading_products.value = true
	
	// Debug: Log the order structure
	console.log('=== ORDER DETAILS DEBUG ===')
	console.log('Full order:', order)
	console.log('Order items:', order.items)
	if (order.items && order.items.length > 0) {
		console.log('First item:', order.items[0])
		console.log('First item keys:', Object.keys(order.items[0]))
		console.log('First item product:', order.items[0].product)
		if (order.items[0].product) {
			console.log('First item product keys:', Object.keys(order.items[0].product))
		}
	}
	
	// Always fetch product details to ensure we have complete information including images
	const items_to_fetch = order.items?.filter(item => {
		const product_id = item.product_id || item.product?.id
		const has_complete_data = product_details.value[product_id]?.image
		console.log('Checking item for fetch:', item, 'product_id:', product_id, 'has_complete_data:', has_complete_data)
		return product_id && !has_complete_data
	}) || []
	
	console.log('Items to fetch for complete data:', items_to_fetch.length, items_to_fetch)
	
	if (items_to_fetch.length > 0) {
		try {
			const product_promises = order.items.map(async (item) => {
				const product_id = item.product_id || item.product?.id
				if (product_id && !product_details.value[product_id]) {
					try {
						console.log(`Fetching product ${product_id} for complete data (image)`)
						const product = await get_product(product_id)
						product_details.value[product_id] = product
						console.log(`Fetched product ${product_id}:`, product)
						console.log(`Product image:`, product?.image)
					} catch (error) {
						console.error(`Failed to fetch product ${product_id}:`, error)
						product_details.value[product_id] = null
					}
				}
			})
			
			await Promise.all(product_promises)
		} catch (error) {
			console.error('Error fetching product details:', error)
		}
	}
	
	loading_products.value = false
}

const close_order_modal = () => {
	show_order_modal.value = false
	selected_order.value = null
}

// Helper functions to get product information
const get_product_name = (item) => {
	const product_id = item.product_id || item.product?.id
	const cached_product = product_details.value[product_id]
	
	// Try different possible field names and structures
	const product_name = item.product?.name || 
						cached_product?.name ||
						item.product_name || 
						item.name || 
						item.title ||
						`Product #${product_id || item.id || 'Unknown'}`
	
	return product_name || 'Product Name Not Available'
}

const get_product_description = (item) => {
	const product_id = item.product_id || item.product?.id
	const cached_product = product_details.value[product_id]
	
	return item.product?.description || 
		   cached_product?.description ||
		   item.description || 
		   'Product description not available'
}

const get_product_price = (item) => {
	const product_id = item.product_id || item.product?.id
	const cached_product = product_details.value[product_id]
	
	return item.product?.price || 
		   cached_product?.price ||
		   item.unit_price || 
		   item.price || 
		   0
}

const get_product_image = (item) => {
	const product_id = item.product_id || item.product?.id
	const cached_product = product_details.value[product_id]
	
	// Debug: Log image data
	console.log('Getting image for item:', item)
	console.log('Product image:', item.product_image)
	console.log('Product image (direct):', item.product_image)
	console.log('Cached product image:', cached_product?.image)
	console.log('Item image:', item.image)
	
	// Try multiple sources for the image - prioritize product_image field
	let image = item.product_image || 
		   item.product?.image || 
		   cached_product?.image ||
		   item.image
	
	// If we have a product ID but no image, try to get it from cached product
	if (!image && product_id && cached_product) {
		image = cached_product.image
	}
	
	// Fallback to logo if no image found
	if (!image) {
		image = '/bottleplug_logo.png'
	}
	
	console.log('Final image path:', image)
	return image
}

const image_url = (path) => {
	console.log('Image URL:', path)

	if (!path) return '/bottleplug_logo.png'
	if (path.startsWith('http')) return path
	if (path.startsWith('/bottleplug_logo.png')) return '/bottleplug_logo.png'
	return `http://localhost:8000/media/${path.replace(/^\/?media\//, '')}`
}

const handle_image_error = (event) => {
	event.target.src = '/bottleplug_logo.png'
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

// Payment modal functions
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
</script>

<style scoped>
.account_page {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

/* Hero Section */
.hero_section {
	position: relative;
	height: 200px;
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
	max-width: 600px;
	padding: 0 20px;
}

.hero_title {
	font-size: 36px;
	font-weight: 700;
	font-family: 'Playfair Display', serif;
	margin-bottom: 8px;
	background: linear-gradient(135deg, #DAA520, #FFD700);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.hero_subtitle {
	font-size: 16px;
	opacity: 0.9;
	line-height: 1.6;
}

/* Account Section */
.account_section {
	padding: 40px 0;
}

.account_container {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

/* Account Overview */
.account_overview {
	margin-bottom: 40px;
}

.user_info_card {
	background: white;
	border-radius: 16px;
	padding: 30px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
	display: flex;
	align-items: center;
	gap: 24px;
}

.user_avatar {
	width: 80px;
	height: 80px;
	border-radius: 50%;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}

.avatar_icon {
	font-size: 32px;
	color: white;
}

.user_details {
	flex: 1;
}

.user_name {
	font-size: 24px;
	font-weight: 700;
	color: #1a0f0f;
	margin-bottom: 4px;
}

.user_email {
	font-size: 16px;
	color: #666;
	margin-bottom: 16px;
}

.user_stats {
	display: flex;
	gap: 24px;
}

.stat_item {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 4px;
}

.stat_number {
	font-size: 24px;
	font-weight: 700;
	color: #DAA520;
}

.stat_label {
	font-size: 12px;
	color: #666;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

/* Account Content */
.account_content {
	display: grid;
	grid-template-columns: 2fr 1fr;
	gap: 30px;
}

.content_section {
	background: white;
	border-radius: 16px;
	padding: 30px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.section_header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 24px;
	padding-bottom: 16px;
	border-bottom: 2px solid rgba(218, 165, 32, 0.1);
}

.section_title {
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

.view_all_btn {
	color: #DAA520;
	text-decoration: none;
	font-weight: 600;
	font-size: 14px;
	transition: color 0.3s ease;
}

.view_all_btn:hover {
	color: #B8860B;
}

/* Loading State */
.loading_state {
	text-align: center;
	padding: 40px 20px;
}

.loading_spinner {
	width: 32px;
	height: 32px;
	border: 3px solid rgba(218, 165, 32, 0.3);
	border-top: 3px solid #DAA520;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin: 0 auto 12px;
}

@keyframes spin {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}

.loading_text {
	color: #666;
	font-size: 14px;
}

/* Empty State */
.empty_state {
	text-align: center;
	padding: 40px 20px;
}

.empty_illustration {
	position: relative;
	margin-bottom: 24px;
}

.empty_icon {
	font-size: 64px;
	margin-bottom: 12px;
	opacity: 0.8;
}

.empty_icon_secondary {
	font-size: 32px;
	position: absolute;
	top: 16px;
	right: 50%;
	transform: translateX(50%);
	opacity: 0.6;
	animation: float 3s ease-in-out infinite;
}

@keyframes float {
	0%, 100% { transform: translateX(50%) translateY(0px); }
	50% { transform: translateX(50%) translateY(-8px); }
}

.empty_title {
	font-size: 20px;
	font-weight: 700;
	color: #1a0f0f;
	margin-bottom: 12px;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.empty_text {
	color: #666;
	font-size: 14px;
	line-height: 1.5;
	margin-bottom: 24px;
	max-width: 400px;
	margin-left: auto;
	margin-right: auto;
}

.empty_actions {
	display: flex;
	gap: 12px;
	justify-content: center;
	flex-wrap: wrap;
}

.shop_now_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 12px 24px;
	border-radius: 20px;
	font-weight: 600;
	font-size: 14px;
	text-decoration: none;
	transition: all 0.3s ease;
	display: inline-flex;
	align-items: center;
	gap: 6px;
}

.shop_now_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(218, 165, 32, 0.3);
}

.view_events_btn {
	background: white;
	color: #DAA520;
	border: 2px solid #DAA520;
	padding: 12px 24px;
	border-radius: 20px;
	font-weight: 600;
	font-size: 14px;
	text-decoration: none;
	transition: all 0.3s ease;
	display: inline-flex;
	align-items: center;
	gap: 6px;
}

.view_events_btn:hover {
	transform: translateY(-2px);
	background: #DAA520;
	color: white;
	box-shadow: 0 4px 15px rgba(218, 165, 32, 0.3);
}

/* Orders List */
.orders_list, .transactions_list {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.order_item, .transaction_item {
	border: 1px solid rgba(218, 165, 32, 0.1);
	border-radius: 12px;
	padding: 20px;
	background: #fafafa;
	transition: all 0.3s ease;
}

.order_item:hover, .transaction_item:hover {
	background: white;
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.order_header, .transaction_header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 12px;
}

.order_info, .transaction_info {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.order_number, .transaction_number {
	font-size: 16px;
	font-weight: 600;
	color: #1a0f0f;
}

.order_date, .transaction_date {
	font-size: 12px;
	color: #666;
}

.status_badge {
	padding: 4px 8px;
	border-radius: 12px;
	font-size: 11px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.status_pending {
	background: rgba(251, 191, 36, 0.1);
	color: #d97706;
}

.status_processing {
	background: rgba(59, 130, 246, 0.1);
	color: #2563eb;
}

.status_shipped {
	background: rgba(34, 197, 94, 0.1);
	color: #16a34a;
}

.status_delivered {
	background: rgba(34, 197, 94, 0.1);
	color: #16a34a;
}

.status_cancelled {
	background: rgba(239, 68, 68, 0.1);
	color: #dc2626;
}

.status_completed {
	background: rgba(34, 197, 94, 0.1);
	color: #16a34a;
}

.status_failed {
	background: rgba(239, 68, 68, 0.1);
	color: #dc2626;
}

.status_refunded {
	background: rgba(168, 85, 247, 0.1);
	color: #9333ea;
}

.order_details, .transaction_details {
	display: flex;
	flex-direction: column;
	gap: 8px;
	margin-bottom: 12px;
}

.items_count, .method_text {
	font-size: 14px;
	color: #666;
	margin-bottom: 4px;
}

.total_amount, .amount_text {
	font-size: 18px;
	font-weight: 700;
	color: #1a0f0f;
	margin-bottom: 4px;
}

.order_payment_info {
	display: flex;
	flex-direction: column;
	gap: 4px;
	margin-top: 8px;
}

.payment_row {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.payment_label {
	font-size: 12px;
	color: #666;
}

.payment_amount {
	font-size: 14px;
	font-weight: 600;
}

.payment_amount.paid {
	color: #16a34a;
}

.payment_amount.payment_status_paid {
	color: #16a34a; /* Green for fully paid (0 balance) */
}

.payment_amount.payment_status_partial {
	color: #d97706; /* Yellow for partially paid */
}

.payment_amount.payment_status_unpaid {
	color: #dc2626; /* Red for unpaid */
}

.order_actions, .transaction_actions {
	display: flex;
	justify-content: flex-end;
}

.view_order_btn, .view_payment_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 8px 16px;
	border-radius: 16px;
	font-weight: 600;
	font-size: 12px;
	text-decoration: none;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	gap: 4px;
}

.view_order_btn:hover, .view_payment_btn:hover {
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(218, 165, 32, 0.3);
}

/* Quick Actions */
.quick_actions {
	background: white;
	border-radius: 16px;
	padding: 30px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
	height: fit-content;
}

.actions_title {
	font-size: 20px;
	font-weight: 600;
	color: #1a0f0f;
	margin-bottom: 20px;
}

.actions_grid {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.action_card {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 16px;
	border: 1px solid rgba(218, 165, 32, 0.1);
	border-radius: 12px;
	background: #fafafa;
	text-decoration: none;
	transition: all 0.3s ease;
}

.action_card:hover {
	background: white;
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
	transform: translateY(-2px);
}

.action_icon {
	font-size: 20px;
}

.action_text {
	font-size: 14px;
	font-weight: 600;
	color: #1a0f0f;
}

.btn_icon {
	font-size: 12px;
}

/* Responsive Design */
@media (max-width: 768px) {
	.hero_title {
		font-size: 28px;
	}
	
	.account_content {
		grid-template-columns: 1fr;
		gap: 20px;
	}
	
	.user_info_card {
		flex-direction: column;
		text-align: center;
		gap: 16px;
	}
	
	.user_stats {
		justify-content: center;
	}
	
	.content_section {
		padding: 20px;
	}
	
	.section_header {
		flex-direction: column;
		gap: 12px;
		align-items: stretch;
	}
	
	.empty_title {
		font-size: 18px;
	}
	
	.empty_text {
		font-size: 13px;
		padding: 0 10px;
	}
	
	.empty_actions {
		flex-direction: column;
		align-items: center;
	}
	
	.shop_now_btn, .view_events_btn {
		width: 100%;
		max-width: 240px;
		justify-content: center;
	}
}

/* Order Details Modal */
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

.loading_products {
	text-align: center;
	padding: 40px 20px;
}

.loading_products .loading_spinner {
	width: 40px;
	height: 40px;
	border: 4px solid rgba(218, 165, 32, 0.1);
	border-top: 4px solid #DAA520;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin: 0 auto 20px;
}

.loading_products p {
	color: #64748b;
	font-size: 1rem;
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

.order_items_list {
	display: grid;
	gap: 15px;
}

.order_item_detail {
	display: flex;
	align-items: center;
	gap: 15px;
	padding: 15px;
	background: #f8fafc;
	border-radius: 12px;
}

.order_item_detail .item_image {
	width: 60px;
	height: 60px;
	border-radius: 8px;
	object-fit: cover;
}

.order_item_detail .item_details {
	flex: 1;
}

.product_header {
	margin-bottom: 15px;
}

.order_item_detail .item_name {
	font-size: 1.2rem;
	color: #1e293b;
	margin-bottom: 8px;
	font-weight: 600;
	line-height: 1.3;
}

.product_description {
	font-size: 0.9rem;
	color: #64748b;
	margin-bottom: 0;
	line-height: 1.4;
}

.product_price_display {
	display: flex;
	align-items: center;
	gap: 10px;
	margin-bottom: 15px;
	padding: 10px 15px;
	background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
	border-radius: 8px;
	border-left: 4px solid #DAA520;
}

.product_price {
	font-size: 1.1rem;
	font-weight: 700;
	color: #DAA520;
}

.product_quantity {
	font-size: 1rem;
	font-weight: 600;
	color: #1e293b;
	background: #DAA520;
	color: white;
	padding: 4px 8px;
	border-radius: 6px;
}

.item_info {
	display: grid;
	gap: 8px;
}

.item_row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 4px 0;
}

.item_label {
	font-size: 0.9rem;
	color: #64748b;
	font-weight: 500;
}

.item_value {
	font-size: 0.9rem;
	color: #1e293b;
	font-weight: 500;
}

.total_row {
	border-top: 1px solid #e2e8f0;
	padding-top: 8px;
	margin-top: 8px;
}

.total_price {
	font-weight: 600;
	color: #DAA520;
	font-size: 1rem;
}

/* Order Summary */
.order_summary {
	background: #f8fafc;
	border-radius: 12px;
	padding: 20px;
	border: 1px solid #e2e8f0;
}

.summary_row {
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

.total_summary_row {
	border-top: 2px solid #e2e8f0;
	padding-top: 12px;
	margin-top: 8px;
}

.total_summary_value {
	font-weight: 700;
	color: #DAA520;
	font-size: 1.1rem;
}

/* Payment Details Modal Specific Styles */
.payment_details {
	/* Inherits all modal styles from order details */
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
	
	.order_item_detail {
		flex-direction: column;
		text-align: center;
	}
}
</style>
