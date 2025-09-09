<template>
	<div class="wishlist_page">
		<!-- Hero Section -->
		<section class="hero_section">
			<div class="hero_background"></div>
			<div class="hero_content">
				<h1 class="hero_title">My Wishlist</h1>
				<p class="hero_subtitle">Your curated collection of premium wines and spirits</p>
			</div>
		</section>

		<!-- Wishlist Section -->
		<section class="wishlist_section">
			<div class="wishlist_container">
				<!-- Loading State -->
				<div v-if="loading" class="loading_state">
					<div class="loading_spinner"></div>
					<p class="loading_text">Loading your wishlist...</p>
				</div>

				<!-- Empty State -->
				<div v-else-if="!items.length" class="empty_wishlist">
					<div class="empty_illustration">
						<div class="empty_icon">💝</div>
						<div class="empty_icon_secondary">🍷</div>
					</div>
					<h2 class="empty_title">Your Wishlist is Empty</h2>
					<div v-if="!auth_store.is_authenticated" class="auth_notice">
						<p class="empty_text">
							Sign in to save your favorite wines and spirits to your personal wishlist. 
							Create your curated collection and never lose track of the bottles you love.
						</p>
						<div class="empty_actions">
							<RouterLink to="/login" class="sign_in_btn">
								<span class="btn_icon">🔐</span>
								Sign In to Save Favorites
							</RouterLink>
							<RouterLink to="/products" class="browse_btn">
								<span class="btn_icon">👀</span>
								Browse Products
							</RouterLink>
						</div>
					</div>
					<div v-else class="authenticated_empty">
						<p class="empty_text">
							Your wishlist is waiting to be filled with amazing wines and spirits! 
							Browse our premium collection and save your favorites for later. 
							Build your personal collection of the finest beverages.
						</p>
						<div class="empty_features">
							<div class="feature_item">
								<span class="feature_icon">✨</span>
								<span class="feature_text">Save Favorites</span>
							</div>
							<div class="feature_item">
								<span class="feature_icon">🛒</span>
								<span class="feature_text">Quick Add to Cart</span>
							</div>
							<div class="feature_item">
								<span class="feature_icon">📱</span>
								<span class="feature_text">Access Anywhere</span>
							</div>
						</div>
						<div class="empty_actions">
							<RouterLink to="/products" class="shop_now_btn">
								<span class="btn_icon">🍷</span>
								Discover Premium Collection
							</RouterLink>
							<RouterLink to="/events" class="view_events_btn">
								<span class="btn_icon">🎉</span>
								Explore Events
							</RouterLink>
						</div>
					</div>
				</div>


				

				
				<!-- Wishlist Items -->
				<div v-if="!loading && items.length > 0" class="wishlist_content">
					<div class="wishlist_header">
						<h2 class="wishlist_title">Wishlist Items ({{ items.length }})</h2>
						<div class="wishlist_actions">
							<button class="clear_wishlist_btn" @click="clear_wishlist" v-if="items.length > 1">
								<span class="btn_icon">🗑️</span>
								Clear All
							</button>
						</div>
					</div>

					<div class="wishlist_grid">
						<div v-for="item in items" :key="item.id" class="wishlist_item">
							<div class="item_image_container">
								<img 
									:src="image_url(item.product_image)" 
									:alt="item.product_name" 
									class="item_image"
									@error="handle_image_error"
								/>
								<div class="item_overlay">
									<button class="add_to_cart_btn" @click="add_to_cart(item)">
										<span class="btn_icon">🛒</span>
										Add to Cart
									</button>
								</div>
							</div>
							
							<div class="item_details">
								<div class="item_info">
									<h3 class="item_name">{{ item.product_name }}</h3>
									<div class="item_meta">
										<span v-if="item.product" class="item_category">Product ID: {{ item.product }}</span>
									</div>
									<div class="item_rating" v-if="item.product_price">
										<span class="price_text">{{ format_price(item.product_price) }}</span>
									</div>
								</div>
								
								<div class="item_actions">
									<div class="item_price">
										<span class="price_amount">{{ format_price(item.product_price) }}</span>
									</div>
									
									<div class="action_buttons">
										<button class="remove_btn" @click="remove_item(item)">
											<span class="btn_icon">💔</span>
											Remove
										</button>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get_wishlist, remove_wishlist_item, add_to_cart as api_add_to_cart } from '../services/api'
import { set_seo } from '../lib/seo'
import { toast_success, toast_error } from '../lib/toast'
import { require_auth_for_action } from '../utils/auth_guard'
import { use_auth_store } from '../stores/auth'

const items = ref([])
const loading = ref(true)
const auth_store = use_auth_store()

// Set SEO
set_seo({ 
	title: 'My Wishlist · BottlePlug', 
	description: 'Your curated collection of premium wines and spirits. Save your favorites and add them to cart when ready.' 
})

onMounted(async () => {
        try {
                const data = await get_wishlist()
                
                // Handle different response formats
                if (data && data.results) {
                        items.value = data.results
                } else if (Array.isArray(data)) {
                        items.value = data
                } else {
                        items.value = []
                }
        } catch (error) {
                console.error('Failed to load wishlist:', error)
                toast_error('Failed to load wishlist')
        } finally { 
                loading.value = false 
        }
})

function image_url(path) {
	if (!path) return 'http://localhost:8000/media/bottleplug_logo.png'
	if (/^https?:/.test(path)) return path
	
	const backend_url = 'http://localhost:8000'
	const clean_path = path.replace(/^\/?media\//, '')
	return `${backend_url}/media/${clean_path}`
}

function handle_image_error(event) {
	event.target.src = 'http://localhost:8000/media/bottleplug_logo.png'
}

function format_price(value) {
	const amount = Number(value) || 0
	return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', minimumFractionDigits: 0 }).format(amount)
}

async function remove_item(item) {
        return require_auth_for_action('Remove from Wishlist', async () => {
                try {
                        await remove_wishlist_item(item.id)
                        items.value = items.value.filter(i => i.id !== item.id)
                        toast_success('Item removed from wishlist')
                } catch (error) {
                        console.error('Failed to remove item:', error)
                        toast_error('Failed to remove item from wishlist')
                }
        })
}

async function add_to_cart(item) {
        return require_auth_for_action('Add to Cart', async () => {
                try {
                        await api_add_to_cart({ product: item.product, quantity: 1 })
                        toast_success('Added to cart!')
                } catch (error) {
                        console.error('Failed to add to cart:', error)
                        toast_error('Failed to add item to cart')
                }
        })
}

async function clear_wishlist() {
        return require_auth_for_action('Clear Wishlist', async () => {
                if (confirm('Are you sure you want to clear your entire wishlist?')) {
                        try {
                                // Remove all items one by one
                                for (const item of items.value) {
                                        await remove_wishlist_item(item.id)
                                }
                                items.value = []
                                toast_success('Wishlist cleared')
                        } catch (error) {
                                console.error('Failed to clear wishlist:', error)
                                toast_error('Failed to clear wishlist')
                        }
                }
        })
}
</script>

<style scoped>
.wishlist_page {
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

/* Wishlist Section */
.wishlist_section {
	padding: 40px 0;
}

.wishlist_container {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

/* Loading State */
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

/* Empty State */
.empty_wishlist {
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

.sign_in_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.browse_btn {
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

.browse_btn:hover {
	transform: translateY(-2px);
	background: #DAA520;
	color: white;
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.view_events_btn {
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

.view_events_btn:hover {
	transform: translateY(-2px);
	background: #DAA520;
	color: white;
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

/* Wishlist Content */
.wishlist_content {
	background: white;
	border-radius: 16px;
	padding: 30px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.wishlist_header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 24px;
	padding-bottom: 16px;
	border-bottom: 2px solid rgba(218, 165, 32, 0.1);
}

.wishlist_title {
	font-size: 24px;
	font-weight: 600;
	color: #1a0f0f;
}

.clear_wishlist_btn {
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

.clear_wishlist_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
}

.wishlist_grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
	gap: 24px;
}

.wishlist_item {
	border: 1px solid rgba(218, 165, 32, 0.1);
	border-radius: 12px;
	background: #fafafa;
	transition: all 0.3s ease;
	overflow: hidden;
}

.wishlist_item:hover {
	background: white;
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
	transform: translateY(-2px);
}

.item_image_container {
	position: relative;
	height: 200px;
	overflow: hidden;
}

.item_image {
	width: 100%;
	height: 100%;
	object-fit: cover;
	background-color: #f8f9fa;
	transition: transform 0.3s ease;
}

.item_overlay {
	position: absolute;
	inset: 0;
	background: rgba(0, 0, 0, 0.7);
	display: flex;
	align-items: center;
	justify-content: center;
	opacity: 0;
	transition: opacity 0.3s ease;
}

.wishlist_item:hover .item_overlay {
	opacity: 1;
}

.wishlist_item:hover .item_image {
	transform: scale(1.05);
}

.add_to_cart_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 12px 20px;
	border-radius: 20px;
	font-weight: 600;
	font-size: 14px;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	gap: 6px;
}

.add_to_cart_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(218, 165, 32, 0.3);
}

.item_details {
	padding: 20px;
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
	gap: 8px;
	flex-wrap: wrap;
}

.item_category, .item_region, .item_vintage {
	font-size: 11px;
	color: #DAA520;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.item_rating {
	display: flex;
	align-items: center;
	gap: 6px;
}

.stars {
	color: #DAA520;
	font-size: 14px;
}

.rating_text {
	font-size: 12px;
	color: #666;
	font-weight: 600;
}

.item_actions {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 12px;
}

.item_price {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.price_amount {
	font-size: 20px;
	font-weight: 700;
	color: #1a0f0f;
}

.action_buttons {
	display: flex;
	gap: 8px;
}

.remove_btn {
	background: linear-gradient(135deg, #dc2626, #b91c1c);
	color: white;
	border: none;
	padding: 8px 12px;
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

.btn_icon {
	font-size: 14px;
}

/* Responsive Design */
@media (max-width: 768px) {
	.hero_title {
		font-size: 28px;
	}
	
	.wishlist_grid {
		grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
		gap: 16px;
	}
	
	.wishlist_content {
		padding: 20px;
	}
	
	.wishlist_header {
		flex-direction: column;
		gap: 12px;
		align-items: stretch;
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
	
	.shop_now_btn, .sign_in_btn, .browse_btn, .view_events_btn {
		width: 100%;
		max-width: 280px;
		justify-content: center;
	}
}
</style>