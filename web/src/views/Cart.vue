<template>
	<div class="cart_page">
		<!-- Hero Section -->
		<section class="hero_section">
			<div class="hero_background"></div>
			<div class="hero_content">
				<h1 class="hero_title">Your Cart</h1>
				<p class="hero_subtitle">Review your premium selections before checkout</p>
			</div>
		</section>

		<!-- Cart Section -->
		<section class="cart_section">
			<div class="cart_container">
				<!-- Loading State -->
				<div v-if="cart.is_loading" class="loading_cart">
					<div class="loading_spinner">🔄</div>
					<h2 class="loading_title">Loading your cart...</h2>
					<p class="loading_text">Please wait while we fetch your items</p>
				</div>

				<!-- Empty Cart State -->
				<div v-else-if="!items.length" class="empty_cart">
					<div class="empty_illustration">
						<div class="empty_icon">🛒</div>
						<div class="empty_icon_secondary">🍷</div>
					</div>
					<h2 class="empty_title">Your Shopping Cart is Empty</h2>
					<p class="empty_text">
						It looks like you haven't added any items to your cart yet. 
						Browse our carefully curated collection of premium wines and spirits 
						to find the perfect selection for your next celebration.
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
						<RouterLink to="/products" class="shop_now_btn">
							<span class="btn_icon">🍷</span>
							Explore Our Collection
						</RouterLink>
						<RouterLink to="/login" class="sign_in_btn">
							<span class="btn_icon">🔐</span>
							Sign In to Save Items
						</RouterLink>
					</div>
				</div>

				<!-- Cart Items -->
				<div v-else class="cart_content">
					<div class="cart_items_section">
						<div class="section_header">
							<h2 class="section_title">Cart Items ({{ items.length }})</h2>
							<button class="clear_cart_btn" @click="clear_cart" v-if="items.length > 1">
								<span class="btn_icon">🗑️</span>
								Clear Cart
							</button>
						</div>

						<div class="cart_items">
							<div v-for="item in items" :key="item.id || item.product" class="cart_item">
								<div class="item_image_container">
									<img 
										:src="image_url(item.product_image || item.product_detail?.image || item.image)" 
										:alt="item.product_name || item.product_detail?.name" 
										class="item_image"
										@error="handle_image_error"
									/>
								</div>
								
								<div class="item_details">
									<div class="item_info">
										<h3 class="item_name">{{ item.product_name || item.product_detail?.name || 'Item' }}</h3>
										<div class="item_meta">
											<span v-if="item.product_detail?.category_name" class="item_category">{{ item.product_detail.category_name }}</span>
											<span v-if="item.product_detail?.region" class="item_region">{{ item.product_detail.region }}</span>
											<span v-if="item.product_detail?.vintage" class="item_vintage">{{ item.product_detail.vintage }}</span>
										</div>
									</div>
									
									<div class="item_actions">
										<div class="quantity_controls">
											<button 
												class="quantity_btn" 
												@click="update(item, Math.max(1, (item.quantity || 1) - 1))"
												:disabled="item.quantity <= 1"
											>-</button>
											<input 
												type="number" 
												min="1" 
												:value="item.quantity" 
												@change="(e) => update(item, e.target.value)" 
												class="quantity_input" 
											/>
											<button 
												class="quantity_btn" 
												@click="update(item, (item.quantity || 1) + 1)"
											>+</button>
										</div>
										
										<div class="item_price_section">
											<div class="price_info">
												<span class="unit_price">{{ format_amount(item.unit_price || item.price || 0) }} each</span>
												<span class="total_price">{{ format_amount(cart.get_item_total(item)) }}</span>
											</div>
											
											<button class="remove_btn" @click="remove(item)">
												<span class="btn_icon">🗑️</span>
												Remove
											</button>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Order Summary -->
					<div class="order_summary_section">
						<OrderSummary :subtotal="total" :delivery_fee="0" :coupon_discount="0">
							<template #actions>
								<div class="checkout_actions">
									<RouterLink to="/products" class="continue_shopping_btn">
										<span class="btn_icon">🛍️</span>
										Continue Shopping
									</RouterLink>
									<RouterLink to="/checkout" class="checkout_btn">
										<span class="btn_icon">💳</span>
										Proceed to Checkout
									</RouterLink>
								</div>
							</template>
						</OrderSummary>
					</div>
				</div>
			</div>
		</section>
	</div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { use_cart_store } from '../stores/cart'
import OrderSummary from '../components/OrderSummary.vue'
import { set_seo } from '../lib/seo'
import { toast_success, toast_error } from '../lib/toast'
import { image_url, get_fallback_image_url } from '../utils/image_utils'

const cart = use_cart_store()
const items = computed(() => cart.items)
const total = computed(() => cart.total_amount)

// Set SEO
set_seo({ 
	title: 'Shopping Cart · BottlePlug', 
	description: 'Review your premium wine and spirit selections. Secure checkout with expert curation and fast delivery.' 
})

// Auto-load cart items when page loads
onMounted(async () => {
	try {
		console.log('🛒 Loading cart items...')
		await cart.fetch_cart()
		console.log('🛒 Cart items loaded:', cart.items.length)
		
		// Debug: Log each cart item structure
		cart.items.forEach((item, index) => {
			console.log(`🛒 Cart item ${index}:`, {
				id: item.id,
				product: item.product,
				product_name: item.product_name,
				product_image: item.product_image,
				product_detail: item.product_detail,
				image: item.image,
				quantity: item.quantity,
				unit_price: item.unit_price
			})
			
			// Debug: Log image paths specifically
			console.log(`🖼️ Item ${index} image paths:`, {
				'item.product_image': item.product_image,
				'item.product_detail?.image': item.product_detail?.image,
				'item.image': item.image,
				'final_image_path': item.product_image || item.product_detail?.image || item.image
			})
		})
	} catch (error) {
		console.error('Failed to load cart items:', error)
		// Don't show error toast for initial load - user might not be signed in
	}
})

function format_amount(value) {
	const amount = Number(value) || 0
	return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', minimumFractionDigits: 0 }).format(amount)
}

// Image URL function is now imported from utils/image_utils.js

function handle_image_error(event) {
	console.log('❌ Cart image failed to load:', event.target.src)
	console.log('🔄 Switching to logo fallback')
	event.target.src = get_fallback_image_url()
}

async function update(item, qty) {
	try {
		await cart.update_item(item.id, { quantity: Number(qty) || 1 })
		toast_success('Cart updated')
	} catch (err) {
		toast_error('Failed to update cart')
	}
}

async function remove(item) {
	try {
		await cart.remove_item(item.id)
		toast_success('Item removed from cart')
	} catch (err) {
		toast_error('Failed to remove item')
	}
}

async function clear_cart() {
	if (confirm('Are you sure you want to clear your cart?')) {
		try {
			await cart.clear_cart()
			toast_success('Cart cleared')
		} catch (err) {
			toast_error('Failed to clear cart')
		}
	}
}
</script>

<style scoped>
.cart_page {
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

/* Cart Section */
.cart_section {
	padding: 40px 0;
}

.cart_container {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

/* Empty Cart */
.empty_cart {
	text-align: center;
	padding: 80px 20px;
	background: white;
	border-radius: 16px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
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
	color: #1a0f0f;
	margin-bottom: 16px;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.empty_text {
	color: #666;
	font-size: 16px;
	line-height: 1.6;
	margin-bottom: 32px;
	max-width: 500px;
	margin-left: auto;
	margin-right: auto;
}

.empty_features {
	display: flex;
	justify-content: center;
	gap: 32px;
	margin-bottom: 40px;
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

/* Loading Cart */
.loading_cart {
	text-align: center;
	padding: 80px 20px;
	background: white;
	border-radius: 16px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.loading_spinner {
	font-size: 48px;
	margin-bottom: 20px;
	animation: spin 2s linear infinite;
}

@keyframes spin {
	from { transform: rotate(0deg); }
	to { transform: rotate(360deg); }
}

.loading_title {
	font-size: 24px;
	font-weight: 600;
	color: #1a0f0f;
	margin-bottom: 12px;
}

.loading_text {
	color: #666;
	font-size: 16px;
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

.sign_in_btn {
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

.sign_in_btn:hover {
	transform: translateY(-2px);
	background: #DAA520;
	color: white;
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

/* Cart Content */
.cart_content {
	display: grid;
	grid-template-columns: 2fr 1fr;
	gap: 30px;
}

.cart_items_section {
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
	font-size: 24px;
	font-weight: 600;
	color: #1a0f0f;
}

.clear_cart_btn {
	background: linear-gradient(135deg, #dc2626, #b91c1c);
	color: white;
	border: none;
	padding: 8px 16px;
	border-radius: 20px;
	font-size: 12px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	gap: 6px;
}

.clear_cart_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
}

.cart_items {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.cart_item {
	display: flex;
	gap: 20px;
	padding: 20px;
	border: 1px solid rgba(218, 165, 32, 0.1);
	border-radius: 12px;
	background: #fafafa;
	transition: all 0.3s ease;
}

.cart_item:hover {
	background: white;
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.item_image_container {
	width: 80px;
	height: 80px;
	border-radius: 8px;
	overflow: hidden;
	flex-shrink: 0;
}

.item_image {
	width: 100%;
	height: 100%;
	object-fit: cover;
	background-color: #f8f9fa;
}

.item_details {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.item_info {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.item_name {
	font-size: 18px;
	font-weight: 600;
	color: #1a0f0f;
	line-height: 1.3;
}

.item_meta {
	display: flex;
	gap: 12px;
	flex-wrap: wrap;
}

.item_category, .item_region, .item_vintage {
	font-size: 12px;
	color: #DAA520;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.item_actions {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 20px;
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

.quantity_btn:hover:not(:disabled) {
	border-color: #DAA520;
	color: #DAA520;
	background: rgba(218, 165, 32, 0.1);
}

.quantity_btn:disabled {
	opacity: 0.5;
	cursor: not-allowed;
}

.quantity_input {
	width: 60px;
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

.item_price_section {
	display: flex;
	flex-direction: column;
	gap: 8px;
	align-items: flex-end;
}

.price_info {
	display: flex;
	flex-direction: column;
	gap: 4px;
	align-items: flex-end;
}

.unit_price {
	font-size: 12px;
	color: #666;
}

.total_price {
	font-size: 18px;
	font-weight: 700;
	color: #1a0f0f;
}

.remove_btn {
	background: linear-gradient(135deg, #dc2626, #b91c1c);
	color: white;
	border: none;
	padding: 6px 12px;
	border-radius: 16px;
	font-size: 11px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	gap: 4px;
}

.remove_btn:hover {
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

/* Order Summary Section */
.order_summary_section {
	background: white;
	border-radius: 16px;
	padding: 30px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
	height: fit-content;
}

.checkout_actions {
	display: flex;
	flex-direction: column;
	gap: 12px;
	margin-top: 20px;
}

.continue_shopping_btn {
	background: linear-gradient(135deg, #6b7280, #4b5563);
	color: white;
	border: none;
	padding: 12px 24px;
	border-radius: 20px;
	font-weight: 600;
	font-size: 14px;
	text-decoration: none;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
}

.continue_shopping_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
}

.checkout_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 16px 24px;
	border-radius: 20px;
	font-weight: 600;
	font-size: 16px;
	text-decoration: none;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
}

.checkout_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.btn_icon {
	font-size: 16px;
}

/* Responsive Design */
@media (max-width: 768px) {
	.hero_title {
		font-size: 28px;
	}
	
	.cart_content {
		grid-template-columns: 1fr;
		gap: 20px;
	}
	
	.cart_item {
		flex-direction: column;
		gap: 16px;
	}
	
	.item_actions {
		flex-direction: column;
		align-items: stretch;
		gap: 16px;
	}
	
	.item_price_section {
		align-items: stretch;
	}
	
	.price_info {
		align-items: center;
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
		margin-bottom: 32px;
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
	
	.shop_now_btn, .sign_in_btn {
		width: 100%;
		max-width: 280px;
		justify-content: center;
	}
}
</style>
