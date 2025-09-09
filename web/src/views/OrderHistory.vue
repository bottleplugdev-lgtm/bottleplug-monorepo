<template>
	<div class="order_history">
		<!-- Auth Loading State -->
		<AuthLoading v-if="is_auth_loading" />
		
		<!-- Main Content (only show when auth is ready and user is authenticated) -->
		<template v-else-if="should_show_content">
			<!-- Hero Section -->
			<section class="hero_section">
				<div class="hero_content">
					<h1 class="hero_title">Order History</h1>
					<p class="hero_subtitle">Track your purchases and manage your orders</p>
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
								placeholder="Search orders by order number..."
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
								<option value="processing">Processing</option>
								<option value="shipped">Shipped</option>
								<option value="delivered">Delivered</option>
								<option value="cancelled">Cancelled</option>
							</select>

							<select v-model="payment_filter" @change="apply_filters" class="filter_select">
								<option value="">All Payments</option>
								<option value="paid">Fully Paid</option>
								<option value="partial">Partially Paid</option>
								<option value="unpaid">Unpaid</option>
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

			<!-- Orders List -->
			<section class="orders_section">
				<div class="container">
					<div v-if="is_loading && orders.length === 0" class="loading_state">
						<div class="loading_spinner"></div>
						<p>Loading your orders...</p>
					</div>

					<div v-else-if="filtered_orders.length === 0" class="empty_state">
						<div class="empty_illustration">
							<div class="empty_icon">📦</div>
							<div class="empty_icon_secondary">🛍️</div>
						</div>
						<h3 class="empty_title">No Orders Found</h3>
						<div v-if="search_query || status_filter || date_filter" class="empty_content">
							<p class="empty_text">
								We couldn't find any orders matching your current search criteria. 
								Try adjusting your filters or search terms to find what you're looking for.
							</p>
							<div class="empty_actions">
								<button @click="clear_filters" class="clear_filters_btn">
									<span class="btn_icon">🔄</span>
									Clear Filters
								</button>
								<RouterLink to="/products" class="btn_primary">
									<span class="btn_icon">🍷</span>
									Browse Products
								</RouterLink>
							</div>
						</div>
						<div v-else class="empty_content">
							<p class="empty_text">
								You haven't placed any orders yet. Your order history will appear here 
								once you start shopping with us. Discover our premium collection of wines and spirits 
								to begin your journey with BottlePlug.
							</p>
							<div class="empty_features">
								<div class="feature_item">
									<span class="feature_icon">✨</span>
									<span class="feature_text">Premium Quality</span>
								</div>
								<div class="feature_item">
									<span class="feature_icon">🚚</span>
									<span class="feature_text">Fast Delivery</span>
								</div>
								<div class="feature_item">
									<span class="feature_icon">💳</span>
									<span class="feature_text">Secure Payment</span>
								</div>
							</div>
							<div class="empty_actions">
								<RouterLink to="/products" class="btn_primary">
									<span class="btn_icon">🍷</span>
									Start Shopping
								</RouterLink>
								<RouterLink to="/events" class="btn_secondary">
									<span class="btn_icon">🎉</span>
									View Events
								</RouterLink>
							</div>
						</div>
					</div>

					<div v-else class="orders_list">
						<div 
							v-for="order in filtered_orders" 
							:key="order.id" 
							class="order_card"
							@click="view_order_details(order)"
						>
							<div class="order_header">
								<div class="order_info">
									<h3 class="order_number">#{{ order.order_number }}</h3>
									<p class="order_date">{{ format_date(order.created_at) }}</p>
								</div>
								<div class="order_status">
									<span :class="['status_badge', `status_${order.status}`]">
										{{ format_status(order.status) }}
									</span>
								</div>
							</div>

							<div class="order_items">
								<div 
									v-for="item in order.items?.slice(0, 3)" 
									:key="item.id" 
									class="order_item"
								>
									<img 
										:src="image_url(get_product_image(item))" 
										:alt="get_product_name(item)"
										@error="handle_image_error"
										class="item_image"
									>
									<div class="item_details">
										<h4 class="item_name">{{ get_product_name(item) }}</h4>
										<p class="item_quantity">Qty: {{ item.quantity }}</p>
										<p class="item_price">{{ format_price(item.total_price) }}</p>
									</div>
								</div>
								<div v-if="order.items?.length > 3" class="more_items">
									+{{ order.items.length - 3 }} more items
								</div>
							</div>

							<div class="order_footer">
								<div class="order_total">
									<span class="total_label">Total:</span>
									<span class="total_amount">{{ format_price(order.total_amount) }}</span>
								</div>
								<div class="order_tax_info" v-if="order.tax">
									<span class="tax_label">Tax:</span>
									<span class="tax_amount">{{ format_price(order.tax) }}</span>
								</div>
								<div class="order_payment_info">
									<div class="payment_row">
										<span class="payment_label">Paid:</span>
										<span class="payment_amount paid">{{ format_price(order.paid_amount) }}</span>
									</div>
									<div class="payment_row">
										<span class="payment_label">Balance:</span>
										<span :class="['payment_amount', order.payment_status_class]">
											{{ order.balance_display }}
										</span>
									</div>
								</div>
								<div class="order_actions">
									<button 
										@click.stop="view_order_details(order)"
										class="btn_secondary"
									>
										View Details
									</button>
									<button 
										v-if="order.status === 'delivered'"
										@click.stop="write_review(order)"
										class="btn_outline"
									>
										Write Review
									</button>
								</div>
							</div>
						</div>
					</div>

					<!-- Load More -->
					<div v-if="has_more_orders" class="load_more_section">
						<button 
							@click="load_more_orders"
							:disabled="is_loading"
							class="btn_load_more"
						>
							<span v-if="is_loading">Loading...</span>
							<span v-else>Load More Orders</span>
						</button>
					</div>
				</div>
			</section>
		</template>
		
		<!-- Not Authenticated State -->
		<div v-else class="not_authenticated_state">
			<div class="auth_message">
				<h2>Please Sign In</h2>
				<p>You need to be signed in to view your order history.</p>
				<RouterLink to="/login" class="btn_primary">Sign In</RouterLink>
			</div>
		</div>
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
								<span class="detail_value">{{ format_price(selected_order.total_amount) }}</span>
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
										<span class="product_price">{{ format_price(item.unit_price || get_product_price(item)) }}</span>
										<span class="product_quantity">× {{ item.quantity }}</span>
									</div>
									<div class="item_info">
										<div class="item_row">
											<span class="item_label">Product:</span>
											<span class="item_value">{{ get_product_name(item) }}</span>
										</div>
										<div class="item_row">
											<span class="item_label">Unit Price:</span>
											<span class="item_value">{{ format_price(item.unit_price || get_product_price(item)) }}</span>
										</div>
										<div class="item_row">
											<span class="item_label">Quantity:</span>
											<span class="item_value">{{ item.quantity }}</span>
										</div>
										<div class="item_row total_row">
											<span class="item_label">Total Price:</span>
											<span class="item_value total_price">{{ format_price(item.total_price) }}</span>
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
								<span class="summary_value">{{ format_price(selected_order.items?.reduce((sum, item) => sum + (item.total_price || 0), 0)) }}</span>
							</div>
							<div class="summary_row" v-if="selected_order.delivery_fee">
								<span class="summary_label">Delivery Fee:</span>
								<span class="summary_value">{{ format_price(selected_order.delivery_fee) }}</span>
							</div>
							<div class="summary_row" v-if="selected_order.tax">
								<span class="summary_label">Tax:</span>
								<span class="summary_value">{{ format_price(selected_order.tax) }}</span>
							</div>
							<div class="summary_row total_summary_row">
								<span class="summary_label">Grand Total:</span>
								<span class="summary_value total_summary_value">{{ format_price(selected_order.total_amount) }}</span>
							</div>
						</div>
					</div>

					<div class="detail_group">
						<h4>Payment Information</h4>
						<div class="detail_grid">
							<div class="detail_item">
								<span class="detail_label">Paid Amount:</span>
								<span class="detail_value">{{ format_price(selected_order.paid_amount) }}</span>
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { use_orders_store } from '../stores/orders'
import { use_auth_store } from '../stores/auth'
import { get_product } from '../services/api'
import AuthLoading from '../components/AuthLoading.vue'

// Router
const router = useRouter()

// Stores
const orders_store = use_orders_store()
const auth_store = use_auth_store()

// Reactive data
const search_query = ref('')
const status_filter = ref('')
const payment_filter = ref('')
const date_filter = ref('')
const search_timeout = ref(null)
const is_auth_loading = ref(true)
const show_order_modal = ref(false)
const selected_order = ref(null)
const product_details = ref({}) // Cache for product details
const loading_products = ref(false)

// Computed properties
const orders = computed(() => orders_store.orders_with_balance)
const is_loading = computed(() => orders_store.is_loading)
const has_more_orders = computed(() => !!orders_store.next_page_url)
const should_show_content = computed(() => !is_auth_loading.value && auth_store.is_authenticated)

const filtered_orders = computed(() => {
	let filtered = orders.value

	// Search filter
	if (search_query.value) {
		const query = search_query.value.toLowerCase()
		filtered = filtered.filter(order => 
			order.order_number?.toLowerCase().includes(query) ||
			order.items?.some(item => 
				item.product?.name?.toLowerCase().includes(query)
			)
		)
	}

	// Status filter
	if (status_filter.value) {
		filtered = filtered.filter(order => order.status === status_filter.value)
	}

	// Payment filter
	if (payment_filter.value) {
		filtered = filtered.filter(order => {
			if (payment_filter.value === 'paid') {
				return order.is_fully_paid
			} else if (payment_filter.value === 'partial') {
				return order.paid_amount > 0 && !order.is_fully_paid
			} else if (payment_filter.value === 'unpaid') {
				return order.paid_amount === 0
			}
			return true // Should not happen
		})
	}

	// Date filter
	if (date_filter.value) {
		const days = parseInt(date_filter.value)
		const cutoff_date = new Date()
		cutoff_date.setDate(cutoff_date.getDate() - days)
		
		filtered = filtered.filter(order => 
			new Date(order.created_at) >= cutoff_date
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

const format_price = (amount) => {
	if (!amount) return 'UGX 0'
	return new Intl.NumberFormat('en-UG', {
		style: 'currency',
		currency: 'UGX'
	}).format(amount)
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

const clear_filters = () => {
	search_query.value = ''
	status_filter.value = ''
	payment_filter.value = ''
	date_filter.value = ''
}

const load_more_orders = async () => {
	try {
		await orders_store.load_more_orders()
	} catch (error) {
		console.error('Failed to load more orders:', error)
	}
}

const view_order_details = async (order) => {
	selected_order.value = order
	show_order_modal.value = true
	loading_products.value = true
	
	// Debug: Log the order structure (can be removed in production)
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

const write_review = (order) => {
	// Navigate to review page
	router.push({
		name: 'product_detail',
		params: { id: order.items[0]?.product?.id },
		query: { review: 'true', order: order.id }
	})
}

// Lifecycle
onMounted(async () => {
	// Wait for auth to be ready (same pattern as Account.vue)
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
	// If user is not authenticated, the API will return appropriate error
	try {
		// Loading orders...
		await orders_store.fetch_my_orders()
	} catch (error) {
		console.error('Failed to load orders:', error)
		// Don't show error if user is not authenticated - that's expected
		if (auth_store.is_authenticated) {
			console.error('User is authenticated but failed to load orders')
		}
	}
})

// SEO
const set_seo = () => {
	document.title = 'Order History · Bottleplug'
}

onMounted(() => {
	set_seo()
})
</script>

<style scoped>
.order_history {
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

.orders_section {
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

.empty_content {
	max-width: 500px;
	margin: 0 auto;
}

.empty_text {
	color: #64748b;
	font-size: 16px;
	line-height: 1.6;
	margin-bottom: 32px;
}

.empty_features {
	display: flex;
	justify-content: center;
	gap: 32px;
	margin-bottom: 32px;
	flex-wrap: wrap;
}

.feature_item {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 8px;
	padding: 16px;
	background: rgba(218, 165, 32, 0.05);
	border-radius: 12px;
	border: 1px solid rgba(218, 165, 32, 0.1);
	transition: all 0.3s ease;
}

.feature_item:hover {
	background: rgba(218, 165, 32, 0.1);
	transform: translateY(-2px);
}

.feature_icon {
	font-size: 24px;
}

.feature_text {
	font-size: 12px;
	font-weight: 600;
	color: #DAA520;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.empty_actions {
	display: flex;
	gap: 16px;
	justify-content: center;
	flex-wrap: wrap;
}

.clear_filters_btn {
	background: linear-gradient(135deg, #6b7280, #4b5563);
	color: white;
	border: none;
	padding: 12px 24px;
	border-radius: 20px;
	font-weight: 600;
	font-size: 14px;
	transition: all 0.3s ease;
	display: inline-flex;
	align-items: center;
	gap: 6px;
	cursor: pointer;
}

.clear_filters_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
}

.orders_list {
	display: grid;
	gap: 20px;
}

.order_card {
	background: white;
	border-radius: 20px;
	padding: 24px;
	box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
	transition: all 0.3s ease;
	cursor: pointer;
	animation: slideInLeft 0.6s ease-out;
}

.order_card:hover {
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

.order_header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 20px;
}

.order_number {
	font-size: 1.25rem;
	font-weight: 600;
	color: #1e293b;
	margin-bottom: 5px;
}

.order_date {
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

.status_processing {
	background: #dbeafe;
	color: #1d4ed8;
}

.status_shipped {
	background: #dcfce7;
	color: #16a34a;
}

.status_delivered {
	background: #dcfce7;
	color: #16a34a;
}

.status_cancelled {
	background: #fee2e2;
	color: #dc2626;
}

.order_items {
	margin-bottom: 20px;
}

.order_item {
	display: flex;
	align-items: center;
	gap: 15px;
	margin-bottom: 15px;
}

.item_image {
	width: 50px;
	height: 50px;
	border-radius: 8px;
	object-fit: cover;
}


.item_details {
	flex: 1;
}

.item_name {
	font-size: 1rem;
	color: #1e293b;
	margin-bottom: 5px;
	font-weight: 500;
}

.item_quantity, .item_price {
	font-size: 0.9rem;
	color: #64748b;
}

.more_items {
	text-align: center;
	color: #64748b;
	font-size: 0.9rem;
	font-style: italic;
}

.order_footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding-top: 20px;
	border-top: 1px solid #e2e8f0;
}

.total_label {
	color: #64748b;
	font-size: 0.9rem;
}

.total_amount {
	font-size: 1.1rem;
	font-weight: 600;
	color: #DAA520;
}

.order_tax_info {
	display: flex;
	align-items: center;
	gap: 8px;
}

.tax_label {
	color: #64748b;
	font-size: 0.85rem;
}

.tax_amount {
	font-size: 0.9rem;
	font-weight: 500;
	color: #64748b;
}

.order_payment_info {
	display: flex;
	flex-direction: column;
	gap: 5px;
	margin-left: 20px;
}

.payment_row {
	display: flex;
	justify-content: space-between;
}

.payment_label {
	color: #64748b;
	font-size: 0.9rem;
}

.payment_amount {
	font-size: 1rem;
	font-weight: 600;
}

.paid {
	color: #28a745;
}

.payment_amount.payment_status_paid {
	color: #28a745; /* Green for fully paid (0 balance) */
}

.payment_amount.payment_status_partial {
	color: #ffc107; /* Yellow for partially paid */
}

.payment_amount.payment_status_unpaid {
	color: #dc3545; /* Red for unpaid */
}

.order_actions {
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
	
	.order_header {
		flex-direction: column;
		gap: 15px;
	}
	
	.order_footer {
		flex-direction: column;
		gap: 15px;
	}
	
	.empty_title {
		font-size: 24px;
	}
	
	.empty_text {
		font-size: 14px;
		padding: 0 10px;
	}
	
	.empty_features {
		gap: 16px;
		margin-bottom: 24px;
	}
	
	.feature_item {
		padding: 12px;
		min-width: 100px;
	}
	
	.feature_icon {
		font-size: 20px;
	}
	
	.feature_text {
		font-size: 11px;
	}
	
	.empty_actions {
		flex-direction: column;
		align-items: center;
	}
	
	.btn_primary, .btn_secondary, .clear_filters_btn {
		width: 100%;
		max-width: 280px;
		justify-content: center;
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