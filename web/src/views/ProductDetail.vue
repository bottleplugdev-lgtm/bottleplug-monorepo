<template>
	<div class="product_detail_page">
		<!-- Loading State -->
		<div v-if="is_loading" class="loading_state">
			<div class="loading_spinner"></div>
			<p class="loading_text">Loading product details...</p>
		</div>

		<!-- Product Not Found -->
		<div v-else-if="!product" class="not_found">
			<div class="not_found_icon">🍷</div>
			<h2 class="not_found_title">Product Not Found</h2>
			<p class="not_found_text">The product you're looking for doesn't exist or has been removed.</p>
			<RouterLink to="/products" class="back_to_products_btn">
				<span class="btn_icon">🛍️</span>
				Back to Products
			</RouterLink>
		</div>

		<!-- Product Details -->
		<div v-else class="product_detail_content">
			<!-- Breadcrumb -->
			<nav class="breadcrumb">
				<RouterLink to="/" class="breadcrumb_link">Home</RouterLink>
				<span class="breadcrumb_separator">/</span>
				<RouterLink to="/products" class="breadcrumb_link">Products</RouterLink>
				<span class="breadcrumb_separator">/</span>
				<span class="breadcrumb_current">{{ product.name }}</span>
			</nav>

			<!-- Product Main Section -->
			<div class="product_main">
				<!-- Product Images -->
				<div class="product_images">
					<div class="main_image_container">
						<img 
							:src="image_url(product.image)" 
							:alt="product.name" 
							class="main_image" 
							loading="lazy" 
							:srcset="image_srcset(product.image)" 
							sizes="(max-width: 640px) 100vw, 500px"
							@error="handle_image_error"
						/>
						<div class="image_overlay">
							<button class="zoom_btn" @click="zoom_image">
								<span class="btn_icon">🔍</span>
								Zoom
							</button>
						</div>
					</div>
				</div>

				<!-- Product Info -->
				<div class="product_info">
					<div class="product_header">
						<div class="product_meta">
							<span v-if="product.category_name" class="product_category">{{ product.category_name }}</span>
							<span v-if="product.region" class="product_region">{{ product.region }}</span>
							<span v-if="product.vintage" class="product_vintage">{{ product.vintage }}</span>
						</div>
						<h1 class="product_title">{{ product.name }}</h1>
						<div class="product_rating" v-if="product.rating">
							<div class="stars">{{ render_stars(product.rating) }}</div>
							<span class="rating_text">{{ product.rating }}/5</span>
							<span class="rating_count">({{ product.review_count || 0 }} reviews)</span>
						</div>
					</div>

					<div class="product_pricing">
						<div class="price_display">
							<span class="current_price">{{ format_price(product.price) }}</span>
							<span v-if="product.original_price && product.original_price > product.price" class="original_price">{{ format_price(product.original_price) }}</span>
						</div>
						<div v-if="product.original_price && product.original_price > product.price" class="savings">
							<span class="save_badge">Save {{ format_price(product.original_price - product.price) }}</span>
						</div>
					</div>

					<div class="product_description" v-if="product.description">
						<h3 class="description_title">Description</h3>
						<p class="description_text">{{ product.description }}</p>
					</div>

					<div class="product_details" v-if="product.details">
						<h3 class="details_title">Product Details</h3>
						<div class="details_grid">
							<div v-if="product.alcohol_content" class="detail_item">
								<span class="detail_label">Alcohol Content:</span>
								<span class="detail_value">{{ product.alcohol_content }}%</span>
							</div>
							<div v-if="product.volume" class="detail_item">
								<span class="detail_label">Volume:</span>
								<span class="detail_value">{{ product.volume }}ml</span>
							</div>
							<div v-if="product.producer" class="detail_item">
								<span class="detail_label">Producer:</span>
								<span class="detail_value">{{ product.producer }}</span>
							</div>
							<div v-if="product.country" class="detail_item">
								<span class="detail_label">Country:</span>
								<span class="detail_value">{{ product.country }}</span>
							</div>
						</div>
					</div>

					<!-- Add to Cart Section -->
					<div class="add_to_cart_section">
						<div class="quantity_selector">
							<label class="quantity_label">Quantity</label>
							<div class="quantity_controls">
								<button 
									class="quantity_btn" 
									@click="qty = Math.max(1, qty - 1)"
									:disabled="qty <= 1"
								>-</button>
								<input 
									type="number" 
									min="1" 
									v-model.number="qty" 
									class="quantity_input" 
								/>
								<button 
									class="quantity_btn" 
									@click="qty++"
								>+</button>
							</div>
						</div>

						<div class="action_buttons">
							<button class="add_to_cart_btn" @click="add_to_cart()" :disabled="is_adding">
								<span v-if="is_adding" class="btn_spinner"></span>
								<span v-else class="btn_icon">🛒</span>
								{{ is_adding ? 'Adding...' : 'Add to Cart' }}
							</button>
							<button class="buy_now_btn" @click="buy_now()" :disabled="is_adding">
								<span class="btn_icon">💳</span>
								Buy Now
							</button>
							<button 
								class="wishlist_btn" 
								:class="{ 'in_wishlist': is_in_wishlist }"
								@click="toggle_wishlist" 
								:disabled="is_toggling_wishlist"
								:title="is_in_wishlist ? 'Remove from wishlist' : 'Add to wishlist'"
							>
								<span v-if="is_toggling_wishlist" class="btn_spinner"></span>
								<span v-else class="btn_icon">{{ is_in_wishlist ? '❤️' : '🤍' }}</span>
							</button>
						</div>
					</div>

					<!-- Product Features -->
					<div class="product_features">
						<div class="feature_item">
							<span class="feature_icon">🚚</span>
							                                <span class="feature_text">Free Delivery on orders over Shs 1,000,000</span>
						</div>
						<div class="feature_item">
							<span class="feature_icon">🛡️</span>
							<span class="feature_text">Secure Payment</span>
						</div>
						<div class="feature_item">
							<span class="feature_icon">↩️</span>
							<span class="feature_text">Easy Returns</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Reviews Section -->
			<div class="reviews_section">
				<div class="reviews_header">
					<h2 class="reviews_title">
						<span class="title_icon">⭐</span>
						Customer Reviews
					</h2>
					<div class="reviews_summary" v-if="reviews.length">
						<div class="average_rating">
							<span class="rating_stars">{{ render_stars(average_rating) }}</span>
							<span class="rating_average">{{ average_rating.toFixed(1) }}/5</span>
						</div>
						<span class="total_reviews">{{ reviews.length }} reviews</span>
					</div>
				</div>

				<!-- Reviews List -->
				<div class="reviews_content">
					<div v-if="reviews_loading" class="loading_reviews">
						<div class="loading_spinner"></div>
						<p>Loading reviews...</p>
					</div>
					
					<div v-else-if="!reviews.length" class="no_reviews">
						<div class="no_reviews_icon">⭐</div>
						<h3 class="no_reviews_title">No reviews yet</h3>
						<p class="no_reviews_text">Be the first to review this product!</p>
					</div>
					
					<div v-else class="reviews_list">
						<div v-for="review in reviews" :key="review.id" class="review_item">
							<div class="review_header">
								<div class="reviewer_info">
									<div class="reviewer_avatar">
										<span class="avatar_letter">{{ (review.user_name || 'C')[0].toUpperCase() }}</span>
									</div>
									<div class="reviewer_details">
										<h4 class="reviewer_name">{{ review.user_name || 'Anonymous Customer' }}</h4>
										<div class="review_rating">
											<span class="review_stars">{{ render_stars(review.rating || 0) }}</span>
											<span class="review_date">{{ format_date(review.created_at) }}</span>
										</div>
									</div>
								</div>
							</div>
							<div class="review_content">
								<p class="review_comment">{{ review.comment }}</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Write Review Form -->
				<div class="write_review_section">
					<h3 class="write_review_title">Write a Review</h3>
					<form @submit.prevent="submit_review" class="review_form">
						<div class="form_group">
							<label class="form_label">Rating</label>
							<div class="rating_selector">
								<button 
									v-for="star in 5" 
									:key="star"
									type="button"
									class="star_btn"
									:class="{ 'selected': new_rating >= star }"
									@click="new_rating = star"
								>
									⭐
								</button>
							</div>
						</div>
						
						<div class="form_group">
							<label class="form_label">Your Review</label>
							<textarea 
								v-model="new_comment" 
								class="review_textarea" 
								rows="4" 
								placeholder="Share your thoughts about this product..."
								required
							></textarea>
						</div>
						
						<div class="form_actions">
							<button type="submit" class="submit_review_btn" :disabled="is_submitting_review">
								<span v-if="is_submitting_review" class="btn_spinner"></span>
								<span v-else class="btn_icon">📝</span>
								{{ is_submitting_review ? 'Submitting...' : 'Submit Review' }}
							</button>
						</div>
						
						<div v-if="review_message" class="review_message" :class="{ 'success': review_success, 'error': !review_success }">
							<span class="message_icon">{{ review_success ? '✅' : '❌' }}</span>
							{{ review_message }}
						</div>
					</form>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { get_product, get_reviews, create_review, get_wishlist, add_to_wishlist, remove_wishlist_item } from '../services/api'
import { require_auth_for_action } from '../utils/auth_guard'
import { use_cart_store } from '../stores/cart'
import { set_seo } from '../lib/seo'
import { toast_success, toast_error } from '../lib/toast'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const is_loading = ref(true)
const cart = use_cart_store()
const qty = ref(1)
const reviews = ref([])
const reviews_loading = ref(true)
const new_rating = ref(5)
const new_comment = ref('')
const review_message = ref('')
const review_success = ref(false)
const is_in_wishlist = ref(false)
const is_adding = ref(false)
const is_toggling_wishlist = ref(false)
const is_submitting_review = ref(false)

// Computed properties
const average_rating = computed(() => {
	if (!reviews.value.length) return 0
	const total = reviews.value.reduce((sum, review) => sum + (review.rating || 0), 0)
	return total / reviews.value.length
})

onMounted(async () => {
	try {
		const id = route.params.id
		if (id) {
			product.value = await get_product(id)
			try {
				const wl = await get_wishlist()
				const list = wl?.results || wl || []
				is_in_wishlist.value = !!list.find(i => i.product === product.value.id)
			} catch (_) {}
			set_seo({ 
				title: `${product.value.name} · BottlePlug`, 
				description: product.value.description || '', 
				image: image_url(product.value.image) 
			})
		}
	} finally {
		is_loading.value = false
	}
})

onMounted(async () => {
	try {
		const id = route.params.id
		if (id) {
			const data = await get_reviews({ product: id })
			reviews.value = data?.results || data || []
		}
	} finally {
		reviews_loading.value = false
	}
})

function image_url(path) {
	if (!path) return 'http://localhost:8000/media/bottleplug_logo.png'
	if (/^https?:/.test(path)) {
		path = path.replace('localhost', 'localhost:8000')
		return path
	}
	
	const backend_url = 'http://localhost:8000'
	const clean_path = path.replace(/^\/?media\//, '')
	return `${backend_url}/media/${clean_path}`
}

function image_srcset(path) {
	const base = image_url(path)
	return `${base} 1x`
}

function handle_image_error(event) {
	event.target.src = 'http://localhost:8000/media/bottleplug_logo.png'
}

function format_price(value) {
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

async function add_to_cart() {
	if (!product.value) return
	
	return require_auth_for_action('Add to Cart', async () => {
		try {
			is_adding.value = true
			console.log('Adding product to cart:', product.value.id, product.value.name)
			await cart.add_item({ product: product.value.id, quantity: qty.value || 1 })
			toast_success(`${product.value.name} added to cart!`)
			if (window?.gtag) window.gtag('event', 'add_to_cart', { items: [{ id: product.value.id, name: product.value.name, price: product.value.price }] })
		} catch (error) {
			console.error('Failed to add to cart:', error)
			toast_error('Failed to add item to cart. Please try again.')
			throw error
		} finally {
			is_adding.value = false
		}
	}, router.currentRoute.value.fullPath)
}

async function buy_now() {
	await add_to_cart()
	if (window?.gtag) window.gtag('event', 'begin_checkout')
	router.push({ name: 'checkout' })
}

function render_stars(rating) {
	const max = 5
	const full = '★'.repeat(Math.max(0, Math.min(max, Math.floor(rating))))
	const empty = '☆'.repeat(Math.max(0, max - full.length))
	return full + empty
}

function zoom_image() {
	// Implement image zoom functionality
	console.log('Zoom image')
}

async function submit_review() {
	if (!product.value || !new_comment.value.trim()) return
	
	try {
		is_submitting_review.value = true
		review_message.value = ''
		review_success.value = false
		
		await create_review({ 
			product: product.value.id, 
			rating: new_rating.value, 
			comment: new_comment.value 
		})
		
		review_success.value = true
		review_message.value = 'Review submitted successfully!'
		new_comment.value = ''
		new_rating.value = 5
		
		// Refresh reviews
		const data = await get_reviews({ product: product.value.id })
		reviews.value = data?.results || data || []
		
		toast_success('Review submitted successfully!')
	} catch (error) {
		review_success.value = false
		review_message.value = 'Failed to submit review. Please try again.'
		toast_error('Failed to submit review')
	} finally {
		is_submitting_review.value = false
	}
}

async function toggle_wishlist() {
	if (!product.value) return

	return require_auth_for_action('Add to Wishlist', async () => {
		try {
			is_toggling_wishlist.value = true
			
			if (is_in_wishlist.value) {
				const wl = await get_wishlist()
				const list = wl?.results || wl || []
				const item = list.find(i => i.product === product.value.id)
				if (item) await remove_wishlist_item(item.id)
				is_in_wishlist.value = false
				toast_success('Removed from wishlist')
				if (window?.gtag) window.gtag('event', 'remove_from_wishlist', { items: [{ id: product.value.id, name: product.value.name, price: product.value.price }] })
			} else {
				await add_to_wishlist({ product: product.value.id })
				is_in_wishlist.value = true
				toast_success('Added to wishlist')
				if (window?.gtag) window.gtag('event', 'add_to_wishlist', { items: [{ id: product.value.id, name: product.value.name, price: product.value.price }] })
			}
		} catch (error) {
			toast_error('Failed to update wishlist')
		} finally {
			is_toggling_wishlist.value = false
		}
	})
}
</script>

<style scoped>
.product_detail_page {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
	padding: 40px 0;
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

/* Not Found State */
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

.back_to_products_btn {
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

.back_to_products_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

/* Product Detail Content */
.product_detail_content {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

/* Breadcrumb */
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

/* Product Main Section */
.product_main {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 60px;
	margin-bottom: 60px;
}

/* Product Images */
.product_images {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.main_image_container {
	position: relative;
	border-radius: 16px;
	overflow: hidden;
	background: white;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.main_image {
	width: 100%;
	height: auto;
	display: block;
	transition: transform 0.3s ease;
}

.image_overlay {
	position: absolute;
	inset: 0;
	background: rgba(0, 0, 0, 0.7);
	display: flex;
	align-items: center;
	justify-content: center;
	opacity: 0;
	transition: opacity 0.3s ease;
}

.main_image_container:hover .image_overlay {
	opacity: 1;
}

.main_image_container:hover .main_image {
	transform: scale(1.05);
}

.zoom_btn {
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

.zoom_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(218, 165, 32, 0.3);
}

/* Product Info */
.product_info {
	display: flex;
	flex-direction: column;
	gap: 30px;
}

.product_header {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.product_meta {
	display: flex;
	gap: 12px;
	flex-wrap: wrap;
}

.product_category, .product_region, .product_vintage {
	font-size: 12px;
	color: #DAA520;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
	padding: 4px 8px;
	background: rgba(218, 165, 32, 0.1);
	border-radius: 12px;
}

.product_title {
	font-size: 36px;
	font-weight: 700;
	color: #1a0f0f;
	line-height: 1.2;
	font-family: 'Playfair Display', serif;
}

.product_rating {
	display: flex;
	align-items: center;
	gap: 12px;
}

.stars {
	color: #DAA520;
	font-size: 18px;
}

.rating_text {
	font-size: 16px;
	font-weight: 600;
	color: #1a0f0f;
}

.rating_count {
	font-size: 14px;
	color: #666;
}

/* Product Pricing */
.product_pricing {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.price_display {
	display: flex;
	align-items: center;
	gap: 16px;
}

.current_price {
	font-size: 32px;
	font-weight: 700;
	color: #1a0f0f;
}

.original_price {
	font-size: 20px;
	color: #666;
	text-decoration: line-through;
}

.savings {
	display: flex;
	align-items: center;
}

.save_badge {
	background: linear-gradient(135deg, #16a34a, #15803d);
	color: white;
	padding: 6px 12px;
	border-radius: 16px;
	font-size: 12px;
	font-weight: 600;
}

/* Product Description */
.product_description {
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

/* Product Details */
.product_details {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.details_title {
	font-size: 20px;
	font-weight: 600;
	color: #1a0f0f;
}

.details_grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
	gap: 12px;
}

.detail_item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 12px 16px;
	background: rgba(218, 165, 32, 0.05);
	border-radius: 8px;
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.detail_label {
	font-size: 14px;
	color: #666;
	font-weight: 500;
}

.detail_value {
	font-size: 14px;
	color: #1a0f0f;
	font-weight: 600;
}

/* Add to Cart Section */
.add_to_cart_section {
	display: flex;
	flex-direction: column;
	gap: 20px;
	padding: 24px;
	background: white;
	border-radius: 16px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.quantity_selector {
	display: flex;
	flex-direction: column;
	gap: 8px;
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
	width: 80px;
	height: 40px;
	border: 2px solid rgba(218, 165, 32, 0.3);
	border-radius: 20px;
	text-align: center;
	font-size: 16px;
	font-weight: 600;
}

.quantity_input:focus {
	outline: none;
	border-color: #DAA520;
}

.action_buttons {
	display: flex;
	gap: 12px;
}

.add_to_cart_btn, .buy_now_btn, .wishlist_btn {
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
}

.add_to_cart_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
}

.add_to_cart_btn:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.buy_now_btn {
	background: linear-gradient(135deg, #1a0f0f, #2d1b1b);
	color: white;
}

.buy_now_btn:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(26, 15, 15, 0.3);
}

.wishlist_btn {
	background: white;
	color: #666;
	border: 2px solid rgba(218, 165, 32, 0.3);
	flex: 0 0 auto;
	width: 56px;
	padding: 16px;
}

.wishlist_btn:hover:not(:disabled) {
	border-color: #DAA520;
	color: #DAA520;
	background: rgba(218, 165, 32, 0.1);
}

.wishlist_btn.in_wishlist {
	background: linear-gradient(135deg, #dc2626, #b91c1c);
	color: white;
	border-color: transparent;
}

.wishlist_btn.in_wishlist:hover {
	background: linear-gradient(135deg, #b91c1c, #991b1b);
}

.add_to_cart_btn:disabled, .buy_now_btn:disabled, .wishlist_btn:disabled {
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

/* Product Features */
.product_features {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.feature_item {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 12px 16px;
	background: rgba(218, 165, 32, 0.05);
	border-radius: 8px;
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.feature_icon {
	font-size: 20px;
}

.feature_text {
	font-size: 14px;
	color: #666;
	font-weight: 500;
}

/* Reviews Section */
.reviews_section {
	background: white;
	border-radius: 16px;
	padding: 40px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.reviews_header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30px;
	padding-bottom: 20px;
	border-bottom: 2px solid rgba(218, 165, 32, 0.1);
}

.reviews_title {
	font-size: 24px;
	font-weight: 600;
	color: #1a0f0f;
	display: flex;
	align-items: center;
	gap: 8px;
}

.title_icon {
	font-size: 24px;
}

.reviews_summary {
	display: flex;
	align-items: center;
	gap: 16px;
}

.average_rating {
	display: flex;
	align-items: center;
	gap: 8px;
}

.rating_stars {
	color: #DAA520;
	font-size: 18px;
}

.rating_average {
	font-size: 18px;
	font-weight: 700;
	color: #1a0f0f;
}

.total_reviews {
	font-size: 14px;
	color: #666;
}

/* Reviews Content */
.reviews_content {
	margin-bottom: 40px;
}

.loading_reviews {
	text-align: center;
	padding: 40px 20px;
}

.no_reviews {
	text-align: center;
	padding: 40px 20px;
}

.no_reviews_icon {
	font-size: 48px;
	margin-bottom: 16px;
}

.no_reviews_title {
	font-size: 18px;
	font-weight: 600;
	color: #1a0f0f;
	margin-bottom: 8px;
}

.no_reviews_text {
	color: #666;
	font-size: 14px;
}

.reviews_list {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.review_item {
	border: 1px solid rgba(218, 165, 32, 0.1);
	border-radius: 12px;
	padding: 20px;
	background: #fafafa;
	transition: all 0.3s ease;
}

.review_item:hover {
	background: white;
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.review_header {
	margin-bottom: 12px;
}

.reviewer_info {
	display: flex;
	align-items: center;
	gap: 12px;
}

.reviewer_avatar {
	width: 40px;
	height: 40px;
	border-radius: 50%;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}

.avatar_letter {
	font-size: 16px;
	font-weight: 700;
	color: white;
}

.reviewer_details {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.reviewer_name {
	font-size: 16px;
	font-weight: 600;
	color: #1a0f0f;
}

.review_rating {
	display: flex;
	align-items: center;
	gap: 8px;
}

.review_stars {
	color: #DAA520;
	font-size: 14px;
}

.review_date {
	font-size: 12px;
	color: #666;
}

.review_content {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.review_comment {
	font-size: 14px;
	color: #666;
	line-height: 1.5;
}

/* Write Review Section */
.write_review_section {
	border-top: 2px solid rgba(218, 165, 32, 0.1);
	padding-top: 30px;
}

.write_review_title {
	font-size: 20px;
	font-weight: 600;
	color: #1a0f0f;
	margin-bottom: 20px;
}

.review_form {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.form_group {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.form_label {
	font-size: 14px;
	font-weight: 600;
	color: #1a0f0f;
}

.rating_selector {
	display: flex;
	gap: 8px;
}

.star_btn {
	background: none;
	border: none;
	font-size: 24px;
	cursor: pointer;
	transition: all 0.3s ease;
	opacity: 0.3;
}

.star_btn.selected {
	opacity: 1;
	color: #DAA520;
}

.star_btn:hover {
	transform: scale(1.1);
}

.review_textarea {
	padding: 12px 16px;
	border: 2px solid rgba(218, 165, 32, 0.3);
	border-radius: 8px;
	font-size: 16px;
	background: white;
	transition: all 0.3s ease;
	resize: vertical;
}

.review_textarea:focus {
	outline: none;
	border-color: #DAA520;
	box-shadow: 0 0 0 3px rgba(218, 165, 32, 0.1);
}

.review_textarea::placeholder {
	color: #999;
}

.form_actions {
	display: flex;
	justify-content: flex-end;
}

.submit_review_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 12px 24px;
	border-radius: 20px;
	font-weight: 600;
	font-size: 14px;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	gap: 6px;
}

.submit_review_btn:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(218, 165, 32, 0.3);
}

.submit_review_btn:disabled {
	opacity: 0.7;
	cursor: not-allowed;
	transform: none;
	box-shadow: none;
}

.review_message {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 12px 16px;
	border-radius: 8px;
	font-size: 14px;
	font-weight: 500;
}

.review_message.success {
	background: rgba(34, 197, 94, 0.1);
	color: #16a34a;
	border: 1px solid rgba(34, 197, 94, 0.2);
}

.review_message.error {
	background: rgba(239, 68, 68, 0.1);
	color: #dc2626;
	border: 1px solid rgba(239, 68, 68, 0.2);
}

.message_icon {
	font-size: 16px;
}

.btn_icon {
	font-size: 16px;
}

/* Responsive Design */
@media (max-width: 768px) {
	.product_main {
		grid-template-columns: 1fr;
		gap: 30px;
	}
	
	.product_title {
		font-size: 28px;
	}
	
	.current_price {
		font-size: 28px;
	}
	
	.action_buttons {
		flex-direction: column;
	}
	
	.reviews_header {
		flex-direction: column;
		gap: 16px;
		align-items: stretch;
	}
	
	.reviews_section {
		padding: 20px;
	}
}
</style>

