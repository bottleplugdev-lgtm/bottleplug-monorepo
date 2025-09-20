<template>
	<div class="products_page">
		<!-- Hero Section -->
		<section class="hero_section">
			<div class="hero_background"></div>
			<div class="hero_content">
				<h1 class="hero_title">Discover Premium Spirits</h1>
				<p class="hero_subtitle">Curated collection of the world's finest wines and spirits, delivered to your door</p>
			</div>
		</section>

		<!-- Filters Section -->
		<section class="filters_section">
			<div class="filters_container">
				<div class="search_section">
					<div class="search_input_wrapper">
						<span class="search_icon">🔍</span>
						<input 
							v-model="search" 
							class="search_input" 
							placeholder="Search wines, spirits, regions..." 
						/>
					</div>
				</div>
				<div class="filters_row">
					<select v-model="selected_category" class="filter_select">
						<option value="">All Categories</option>
						<option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
					</select>
					<select v-model="sort" class="filter_select">
						<option value="">Sort: Featured</option>
						<option value="price">Price: Low to High</option>
						<option value="-price">Price: High to Low</option>
						<option value="-created_at">Newest First</option>
						<option value="name">Name: A-Z</option>
					</select>
					<button class="filter_btn" @click="apply_filters">
						<span class="btn_icon">✨</span>
						Apply Filters
					</button>
				</div>
			</div>
		</section>

		<!-- Products Grid -->
		<section class="products_section">
			<div class="products_container">
				<!-- Loading State -->
				<div v-if="is_loading" class="loading_state">
					<div class="loading_spinner"></div>
					<p class="loading_text">Discovering exceptional spirits...</p>
				</div>

				<!-- Error State -->
				<div v-else-if="error_message" class="error_state">
					<div class="error_icon">⚠️</div>
					<p class="error_text">{{ error_message }}</p>
					<button class="retry_btn" @click="apply_filters">Try Again</button>
				</div>

				<!-- Products Grid -->
				<div v-else class="products_grid">
					<div v-for="p in products" :key="p.id" class="product_card">
						<div class="product_image_container">
							<img 
								:src="image_url(p.image)" 
								:alt="p.name" 
								class="product_image" 
								loading="lazy" 
								:srcset="image_srcset(p.image)" 
								sizes="(max-width: 640px) 50vw, (max-width: 1024px) 25vw, 280px"
								@error="handle_image_error"
							/>
							<div class="product_overlay">
								<RouterLink :to="{ name: 'product_detail', params: { id: p.id } }" class="view_details_btn">
									View Details
								</RouterLink>
							</div>
							<div class="product_badges">
								<span v-if="p.is_featured" class="badge featured_badge">Featured</span>
								<span v-if="p.sale_percentage" class="badge sale_badge">{{ p.sale_percentage }}% OFF</span>
							</div>
						</div>
						
						<div class="product_info">
							<div class="product_meta">
								<span v-if="p.category_name" class="product_category">{{ p.category_name }}</span>
								<span v-if="p.region" class="product_region">{{ p.region }}</span>
							</div>
							
							<h3 class="product_name">
								<RouterLink :to="{ name: 'product_detail', params: { id: p.id } }">
									{{ p.name }}
								</RouterLink>
							</h3>
							
							<div class="product_details">
								<span v-if="p.vintage" class="product_vintage">{{ p.vintage }}</span>
								<span v-if="p.volume" class="product_volume">{{ p.volume }}</span>
							</div>
							
							<div v-if="product_rating(p) > 0" class="product_rating">
								<div class="stars">
									<span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.round(product_rating(p)) }">★</span>
								</div>
								<span class="rating_count">({{ p.review_count || 0 }})</span>
							</div>
							
							<div class="product_price_section">
								<div class="price_info">
									<span class="current_price">{{ format_price(p.price) }}</span>
									<span v-if="p.original_price && p.original_price > p.price" class="original_price">{{ format_price(p.original_price) }}</span>
								</div>
								
								<div class="product_actions">
									<button class="add_to_cart_btn" @click="add_product_to_cart(p)">
										<span class="btn_icon">🛒</span>
										Add to Cart
									</button>
									<button 
										class="wishlist_btn" 
										:class="{ 'in_wishlist': is_in_wishlist(p) }"
										@click="toggle_wishlist(p)" 
										:title="is_in_wishlist(p) ? 'Remove from wishlist' : 'Add to wishlist'"
									>
										{{ is_in_wishlist(p) ? '♥' : '♡' }}
									</button>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Load More -->
				<div v-if="has_more && !is_loading" class="load_more_section">
					<button class="load_more_btn" @click="store.load_more()">
						<span class="btn_icon">🍷</span>
						Discover More
					</button>
				</div>

				<!-- Empty State -->
				<div v-if="!is_loading && !error_message && products.length === 0" class="empty_state">
					<div class="empty_icon">🍷</div>
					<h3 class="empty_title">No products found</h3>
					<p class="empty_text">Try adjusting your search or filters to discover our premium collection</p>
					<button class="reset_btn" @click="reset_filters">Reset Filters</button>
				</div>
			</div>
		</section>
	</div>
</template>

<script setup>
import { onMounted, computed, ref, watch } from 'vue'
import { use_products_store } from '../stores/products'
import { use_cart_store } from '../stores/cart'
import { useRoute, useRouter } from 'vue-router'
import { get_wishlist, add_to_wishlist, remove_wishlist_item } from '../services/api'
import { require_auth_for_action } from '../utils/auth_guard'
import { set_seo } from '../lib/seo'
import { toast_success, toast_error } from '../lib/toast'
import { use_auth_store } from '../stores/auth'
import { image_url as utils_image_url, get_fallback_image_url } from '../utils/image_utils'

const store = use_products_store()
const cart = use_cart_store()
const auth_store = use_auth_store()
const route = useRoute()
const router = useRouter()
const search = ref('')
const selected_category = ref('')
const sort = ref('')
const wishlist_ids = ref(new Set())

onMounted(async () => {
	await store.fetch_categories()
	await load_from_query()
	
	// Load wishlist if user is authenticated
	if (auth_store.is_authenticated) {
		try {
			const wl = await get_wishlist()
			const list = wl?.results || wl || []
			wishlist_ids.value = new Set(list.map(i => i.product))
		} catch (_) {}
	}
	
	set_seo({ 
		title: 'Discover Premium Spirits · BottlePlug', 
		description: 'Explore our curated collection of the world\'s finest wines and spirits. Expert curation, competitive pricing, and secure delivery.' 
	})
})

watch(() => route.query, () => { load_from_query() })

const products = computed(() => store.products)
const categories = computed(() => store.categories)
const is_loading = computed(() => store.is_loading)
const error_message = computed(() => store.error_message)
const has_more = computed(() => !!store.next_page_url)

function format_price(value) {
	const amount = Number(value) || 0
	return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', minimumFractionDigits: 0 }).format(amount)
}

function image_url(path) {
	return utils_image_url(path)
}

function handle_image_error(event) {
	// Fallback to logo if image fails to load
	event.target.src = get_fallback_image_url()
}

function image_srcset(path) {
	const base = image_url(path)
	// For now, return single resolution. In production, you might want to generate multiple sizes
	return `${base} 1x`
}

function product_rating(p) {
	return p.average_rating || 0
}

function render_stars(rating) {
	const full = Math.floor(rating)
	const has_half = rating % 1 >= 0.5
	return '★'.repeat(full) + (has_half ? '☆' : '') + '☆'.repeat(5 - full - (has_half ? 1 : 0))
}

function is_in_wishlist(p) {
	return wishlist_ids.value.has(p.id)
}

async function toggle_wishlist(p) {
        return require_auth_for_action('Add to Wishlist', async () => {
                try {
                        if (is_in_wishlist(p)) {
                                // Get the wishlist item ID first
                                const wl = await get_wishlist()
                                const list = wl?.results || wl || []
                                const item = list.find(i => i.product === p.id)
                                if (item) {
                                        await remove_wishlist_item(item.id)
                                        wishlist_ids.value.delete(p.id)
                                        toast_success('Removed from wishlist')
                                }
                        } else {
                                await add_to_wishlist({ product: p.id })
                                wishlist_ids.value.add(p.id)
                                toast_success('Added to wishlist')
                        }
                } catch (err) {
                        console.error('Wishlist error:', err)
                        toast_error('Failed to update wishlist')
                }
        })
}

async function add_product_to_cart(p) {
	console.log('add_product_to_cart called with:', p)
	console.log('Current auth state:', auth_store.is_authenticated)
	
	return require_auth_for_action('Add to Cart', async () => {
		try {
			console.log('Adding product to cart:', p.id, p.name)
			console.log('User is authenticated, proceeding with cart operation')
			
			await cart.add_item({ product: p.id, quantity: 1 })
			toast_success(`${p.name} added to cart!`)
		} catch (err) {
			console.error('Failed to add to cart:', err)
			console.error('Error details:', err.response?.data || err.message)
			toast_error('Failed to add item to cart. Please try again.')
			throw err
		}
	}, router.currentRoute.value.fullPath)
}

async function load_from_query() {
	const q = route.query.search || ''
	const cat = route.query.category || ''
	const s = route.query.sort || ''
	
	search.value = q
	selected_category.value = cat
	sort.value = s
	
	await apply_filters()
}

async function apply_filters() {
	const filters = {}
	if (search.value) filters.search = search.value
	if (selected_category.value) filters.category = selected_category.value
	if (sort.value) filters.sort = sort.value
	
	await store.fetch_products(filters)
	
	// Update URL
	const query = {}
	if (search.value) query.search = search.value
	if (selected_category.value) query.category = selected_category.value
	if (sort.value) query.sort = sort.value
	
	router.replace({ query })
}

function reset_filters() {
	search.value = ''
	selected_category.value = ''
	sort.value = ''
	apply_filters()
}
</script>

<style scoped>
.products_page {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

/* Hero Section */
.hero_section {
	position: relative;
	height: 300px;
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
}

/* Filters Section */
.filters_section {
	background: white;
	border-bottom: 1px solid rgba(218, 165, 32, 0.2);
	padding: 30px 0;
}

.filters_container {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

.search_section {
	margin-bottom: 20px;
}

.search_input_wrapper {
	position: relative;
	max-width: 500px;
}

.search_icon {
	position: absolute;
	left: 16px;
	top: 50%;
	transform: translateY(-50%);
	font-size: 18px;
	color: #666;
}

.search_input {
	width: 100%;
	padding: 16px 16px 16px 50px;
	border: 2px solid rgba(218, 165, 32, 0.3);
	border-radius: 25px;
	font-size: 16px;
	background: white;
	transition: all 0.3s ease;
}

.search_input:focus {
	outline: none;
	border-color: #DAA520;
	box-shadow: 0 0 0 3px rgba(218, 165, 32, 0.1);
}

.filters_row {
	display: flex;
	gap: 15px;
	align-items: center;
	flex-wrap: wrap;
}

.filter_select {
	padding: 12px 16px;
	border: 2px solid rgba(218, 165, 32, 0.3);
	border-radius: 20px;
	background: white;
	font-size: 14px;
	min-width: 180px;
	transition: all 0.3s ease;
}

.filter_select:focus {
	outline: none;
	border-color: #DAA520;
}

.filter_btn {
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
	gap: 8px;
}

.filter_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.btn_icon {
	font-size: 16px;
}

/* Products Section */
.products_section {
	padding: 40px 0;
}

.products_container {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

.loading_state, .error_state, .empty_state {
	text-align: center;
	padding: 60px 20px;
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

.loading_text, .error_text, .empty_text {
	color: #666;
	font-size: 16px;
	margin-bottom: 20px;
}

.error_icon, .empty_icon {
	font-size: 48px;
	margin-bottom: 20px;
}

.retry_btn, .reset_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 12px 24px;
	border-radius: 20px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
}

.retry_btn:hover, .reset_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

/* Products Grid */
.products_grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
	gap: 30px;
}

.product_card {
	background: white;
	border-radius: 16px;
	overflow: hidden;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	transition: all 0.3s ease;
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.product_card:hover {
	transform: translateY(-8px);
	box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.product_image_container {
	position: relative;
	height: 250px;
	overflow: hidden;
}

.product_image {
	width: 100%;
	height: 100%;
	object-fit: cover;
	transition: transform 0.3s ease;
	background-color: #f8f9fa;
}

.product_card:hover .product_image {
	transform: scale(1.05);
}

.product_overlay {
	position: absolute;
	inset: 0;
	background: rgba(0, 0, 0, 0.7);
	display: flex;
	align-items: center;
	justify-content: center;
	opacity: 0;
	transition: opacity 0.3s ease;
}

.product_card:hover .product_overlay {
	opacity: 1;
}

.view_details_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	padding: 12px 24px;
	border-radius: 25px;
	text-decoration: none;
	font-weight: 600;
	transition: all 0.3s ease;
}

.view_details_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.4);
}

.product_badges {
	position: absolute;
	top: 12px;
	left: 12px;
	display: flex;
	gap: 8px;
}

.badge {
	padding: 4px 8px;
	border-radius: 12px;
	font-size: 11px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.featured_badge {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
}

.sale_badge {
	background: linear-gradient(135deg, #dc2626, #b91c1c);
	color: white;
}

.product_info {
	padding: 20px;
}

.product_meta {
	display: flex;
	gap: 8px;
	margin-bottom: 8px;
}

.product_category, .product_region {
	font-size: 11px;
	color: #DAA520;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.product_name {
	margin-bottom: 8px;
}

.product_name a {
	color: #1a0f0f;
	text-decoration: none;
	font-weight: 600;
	font-size: 16px;
	line-height: 1.4;
	transition: color 0.3s ease;
}

.product_name a:hover {
	color: #DAA520;
}

.product_details {
	display: flex;
	gap: 12px;
	margin-bottom: 12px;
}

.product_vintage, .product_volume {
	font-size: 12px;
	color: #666;
}

.product_rating {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 16px;
}

.stars {
	display: flex;
	gap: 2px;
}

.star {
	color: #ddd;
	font-size: 14px;
}

.star.filled {
	color: #DAA520;
}

.rating_count {
	font-size: 12px;
	color: #666;
}

.product_price_section {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.price_info {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.current_price {
	font-size: 18px;
	font-weight: 700;
	color: #1a0f0f;
}

.original_price {
	font-size: 14px;
	color: #666;
	text-decoration: line-through;
}

.product_actions {
	display: flex;
	gap: 8px;
	align-items: center;
}

.add_to_cart_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
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
	gap: 4px;
}

.add_to_cart_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(218, 165, 32, 0.3);
}

.wishlist_btn {
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

.wishlist_btn:hover, .wishlist_btn.in_wishlist {
	border-color: #DAA520;
	color: #DAA520;
	background: rgba(218, 165, 32, 0.1);
}

.load_more_section {
	text-align: center;
	margin-top: 40px;
}

.load_more_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 16px 32px;
	border-radius: 25px;
	font-weight: 600;
	font-size: 16px;
	cursor: pointer;
	transition: all 0.3s ease;
	display: inline-flex;
	align-items: center;
	gap: 8px;
}

.load_more_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 25px rgba(218, 165, 32, 0.4);
}

/* Responsive Design */
@media (max-width: 768px) {
	.hero_title {
		font-size: 36px;
	}
	
	.hero_subtitle {
		font-size: 16px;
	}
	
	.filters_row {
		flex-direction: column;
		align-items: stretch;
	}
	
	.filter_select {
		min-width: auto;
	}
	
	.products_grid {
		grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
		gap: 20px;
	}
	
	.product_image_container {
		height: 200px;
	}
}
</style>

