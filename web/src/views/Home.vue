<template>
	<div class="homepage">
		<!-- Premium Hero Section -->
		<section class="hero_section">
			<div class="hero_background">
				<div class="hero_overlay"></div>
			</div>
			<div class="hero_content">
				<div class="hero_left">
					<div class="hero_badge">🏆 #1 Premium Wine & Spirits Retailer</div>
					<h1 class="hero_title">Premium Wines & <span class="hero_accent">Spirits</span></h1>
					<p class="hero_subtitle">Curated collection of the world's finest wines and spirits, delivered to your door</p>
					
					<div class="hero_benefits">
						<div class="benefit_item">
							<div class="benefit_icon">💰</div>
							<div class="benefit_content">
								<div class="benefit_title">Best Prices</div>
								<div class="benefit_desc">Competitive pricing on premium selections</div>
							</div>
						</div>
						<div class="benefit_item">
							<div class="benefit_icon">🚚</div>
							<div class="benefit_content">
								<div class="benefit_title">Free Shipping</div>
								                                        <div class="benefit_desc">On orders over Shs 1,000,000</div>
							</div>
						</div>
						<div class="benefit_item">
							<div class="benefit_icon">➕</div>
							<div class="benefit_content">
								<div class="benefit_title">Expert Curation</div>
								<div class="benefit_desc">Handpicked by certified sommeliers</div>
							</div>
						</div>
						<div class="benefit_item">
							<div class="benefit_icon">🏆</div>
							<div class="benefit_content">
								<div class="benefit_title">{{ products.length }}+ Products</div>
								<div class="benefit_desc">Curated collection from around the world</div>
							</div>
						</div>
					</div>
					
					<div class="hero_actions">
						<RouterLink to="/products" class="hero_btn_primary">Shop Now</RouterLink>
						<RouterLink to="/about" class="hero_btn_secondary">Learn More</RouterLink>
					</div>
					
					<div class="hero_features">
						<span class="feature_tag">✓ Free Shipping</span>
						<span class="feature_tag">✓ Expert Curation</span>
						<span class="feature_tag">✓ Secure Payment</span>
					</div>
				</div>
				
				<div class="hero_right">
					<div class="featured_product_card">
						<div class="product_highlight">
							<div class="highlight_icon">🍷</div>
							<div class="highlight_title">Featured Selection</div>
							<div class="highlight_name">{{ hero_product?.name || 'Château Margaux 2015' }}</div>
							<div class="highlight_price">
								<span class="current_price">{{ format_price(hero_price) }}</span>
								<span v-if="old_price > hero_price" class="original_price">{{ format_price(old_price) }}</span>
								<span v-if="save_amount > 0" class="save_badge">Save {{ format_price(save_amount) }}</span>
							</div>
							<button 
								class="highlight_btn" 
								:disabled="!hero_product" 
								@click="hero_product && add_product_to_cart(hero_product)"
							>
								Add to Cart
							</button>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Search Section -->
		<section class="search_section">
			<div class="search_container">
				<div class="search_content">
					<h2 class="search_title">Find Your Perfect Bottle</h2>
					<p class="search_subtitle">Discover rare vintages and premium spirits from around the world</p>
					<div class="search_form">
						<input 
							v-model="search_term" 
							class="search_input" 
							placeholder="Search wines, spirits, regions, vintages..." 
							@keyup.enter="go_search" 
						/>
						<button class="search_btn" @click="go_search">
							<svg class="search_icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
							</svg>
						</button>
					</div>
				</div>
			</div>
		</section>

		<!-- Stats Section -->
		<section class="stats_section">
			<div class="stats_container">
				<div class="stat_item">
					<div class="stat_number">{{ products.length }}+</div>
					<div class="stat_label">Premium Products</div>
				</div>
				<div class="stat_item">
					<div class="stat_number">{{ categories.length }}+</div>
					<div class="stat_label">Categories</div>
				</div>
				                                <div class="stat_item">
                                        <div class="stat_number">{{ featured_total_count }}+</div>
                                        <div class="stat_label">Featured Items</div>
                                </div>
                                <div class="stat_item">
                                        <div class="stat_number">{{ new_arrivals_total_count }}+</div>
                                        <div class="stat_label">New Arrivals</div>
                                </div>
                                <div class="stat_item">
                                        <div class="stat_number">{{ on_sale_total_count }}+</div>
                                        <div class="stat_label">On Sale</div>
                                </div>
				<div class="stat_item">
					<div class="stat_number">24/7</div>
					<div class="stat_label">Expert Support</div>
				</div>
			</div>
		</section>

		<!-- Categories Section -->
		<section class="categories_section">
			<div class="section_header">
				<h2 class="section_title">Explore by Category</h2>
				<p class="section_subtitle">Discover our carefully curated collections</p>
			</div>
			<div class="categories_grid">
				<RouterLink 
					v-for="category in categories" 
					:key="category.id" 
					:to="{ name: 'products', query: { category: category.id } }" 
					class="category_card"
				>
					<div class="category_image">
						                                                <img 
                                                        :src="category_image_url(category)" 
                                                        :alt="category.name" 
                                                        loading="lazy"
                                                        class="category_img"
                                                        @error="$event.target.src = get_fallback_image_url()"
                                                />
						<!-- <div class="category_overlay">
							<div class="category_icon">🍷</div>
						</div> -->
					</div>
					<div class="category_content">
						<div class="category_name">{{ category.name }}</div>
						<div class="category_desc">{{ category.description || `Explore the finest ${category.name.toLowerCase()}` }}</div>
						<div class="category_count">{{ category.product_count || 0 }} products</div>
					</div>
				</RouterLink>
			</div>
		</section>

		<!-- Featured Products Section -->
		<section v-if="paginated_featured.length" class="featured_section">
			<div class="section_header">
				<h2 class="section_title">Featured Selections</h2>
				<p class="section_subtitle">Handpicked by our expert sommeliers</p>
			</div>
			<div class="products_grid">
				<div v-for="product in paginated_featured" :key="product.id" class="product_card">
					<div class="product_image">
						<img 
							:src="image_url(product.image)" 
							:alt="product.name" 
							loading="lazy" 
							:srcset="image_srcset(product.image)" 
							sizes="(max-width: 640px) 50vw, (max-width: 1024px) 25vw, 280px" 
						/>
						<div class="product_badge featured_badge">Featured</div>
						<div class="product_overlay">
							<RouterLink :to="{ name: 'product_detail', params: { id: product.id } }" class="overlay_btn">View Details</RouterLink>
						</div>
					</div>
					<div class="product_info">
						<div class="product_category">{{ product.category_name || 'Premium Selection' }}</div>
						<h3 class="product_name">{{ product.name }}</h3>
						<div class="product_details">
							<span v-if="product.region" class="product_region">{{ product.region }}</span>
							<span v-if="product.vintage" class="product_vintage">{{ product.vintage }}</span>
						</div>
						<div class="product_price">
							<span class="current_price">{{ format_price(product.price) }}</span>
							<span v-if="product.original_price && product.original_price > product.price" class="original_price">{{ format_price(product.original_price) }}</span>
						</div>
						<div class="product_rating" v-if="product.average_rating">
							<div class="stars">
								<span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.round(product.average_rating) }">★</span>
							</div>
							<span class="rating_text">({{ product.review_count || 0 }})</span>
						</div>
						<button class="product_btn" @click="add_product_to_cart(product)">Add to Cart</button>
					</div>
				</div>
			</div>
			
			<!-- Featured Pagination -->
			<div v-if="featured_total_pages > 1" class="pagination_controls">
				<button 
					@click="prev_featured_page" 
					:disabled="featured_page === 1"
					class="pagination_btn prev_btn"
				>
					← Previous
				</button>
				<div class="pagination_info">
					Page {{ featured_page }} of {{ featured_total_pages }}
				</div>
				<button 
					@click="next_featured_page" 
					:disabled="featured_page >= featured_total_pages"
					class="pagination_btn next_btn"
				>
					Next →
				</button>
			</div>
		</section>

		                <!-- New Arrivals Section -->
                <section v-if="paginated_new_arrivals.length" class="new_arrivals_section">
			<div class="section_header">
				<h2 class="section_title">New Arrivals</h2>
				<p class="section_subtitle">Fresh additions to our premium collection</p>
			</div>
			<div class="products_grid">
				<div v-for="product in paginated_new_arrivals" :key="product.id" class="product_card">
					<div class="product_image">
						<img 
							:src="image_url(product.image)" 
							:alt="product.name" 
							loading="lazy" 
							:srcset="image_srcset(product.image)" 
							sizes="(max-width: 640px) 50vw, (max-width: 1024px) 25vw, 280px" 
						/>
						<div class="product_badge new_badge">New</div>
						<div class="product_overlay">
							<RouterLink :to="{ name: 'product_detail', params: { id: product.id } }" class="overlay_btn">View Details</RouterLink>
						</div>
					</div>
					<div class="product_info">
						<div class="product_category">{{ product.category_name || 'New Arrival' }}</div>
						<h3 class="product_name">{{ product.name }}</h3>
						<div class="product_details">
							<span v-if="product.region" class="product_region">{{ product.region }}</span>
							<span v-if="product.vintage" class="product_vintage">{{ product.vintage }}</span>
						</div>
						<div class="product_price">
							<span class="current_price">{{ format_price(product.price) }}</span>
							<span v-if="product.original_price && product.original_price > product.price" class="original_price">{{ format_price(product.original_price) }}</span>
						</div>
						<div class="product_rating" v-if="product.average_rating">
							<div class="stars">
								<span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.round(product.average_rating) }">★</span>
							</div>
							<span class="rating_text">({{ product.review_count || 0 }})</span>
						</div>
						<button class="product_btn" @click="add_product_to_cart(product)">Add to Cart</button>
					</div>
				</div>
			</div>
			
			<!-- New Arrivals Pagination -->
			<div v-if="new_arrivals_total_pages > 1" class="pagination_controls">
				<button 
					@click="prev_new_arrivals_page" 
					:disabled="new_arrivals_page === 1"
					class="pagination_btn prev_btn"
				>
					← Previous
				</button>
				<div class="pagination_info">
					Page {{ new_arrivals_page }} of {{ new_arrivals_total_pages }}
				</div>
				<button 
					@click="next_new_arrivals_page" 
					:disabled="new_arrivals_page >= new_arrivals_total_pages"
					class="pagination_btn next_btn"
				>
					Next →
				</button>
			</div>
		</section>

		                <!-- On Sale Section -->
                <section v-if="paginated_on_sale.length" class="sale_section">
			<div class="section_header">
				<h2 class="section_title">Special Offers</h2>
				<p class="section_subtitle">Premium selections at exceptional prices</p>
			</div>
			<div class="products_grid">
				<div v-for="product in paginated_on_sale" :key="product.id" class="product_card sale_card">
					<div class="product_image">
						<img 
							:src="image_url(product.image)" 
							:alt="product.name" 
							loading="lazy" 
							:srcset="image_srcset(product.image)" 
							sizes="(max-width: 640px) 50vw, (max-width: 1024px) 25vw, 280px" 
						/>
						<div class="product_badge sale_badge">
							<span v-if="product.sale_percentage">{{ product.sale_percentage }}% OFF</span>
							<span v-else>Sale</span>
						</div>
						<div class="product_overlay">
							<RouterLink :to="{ name: 'product_detail', params: { id: product.id } }" class="overlay_btn">View Details</RouterLink>
						</div>
					</div>
					<div class="product_info">
						<div class="product_category">{{ product.category_name || 'Special Offer' }}</div>
						<h3 class="product_name">{{ product.name }}</h3>
						<div class="product_details">
							<span v-if="product.region" class="product_region">{{ product.region }}</span>
							<span v-if="product.vintage" class="product_vintage">{{ product.vintage }}</span>
						</div>
						<div class="product_price">
							<span class="current_price">{{ format_price(product.price) }}</span>
							<span v-if="product.original_price && product.original_price > product.price" class="original_price">{{ format_price(product.original_price) }}</span>
						</div>
						<div class="product_rating" v-if="product.average_rating">
							<div class="stars">
								<span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.round(product.average_rating) }">★</span>
							</div>
							<span class="rating_text">({{ product.review_count || 0 }})</span>
						</div>
						<button class="product_btn sale_btn" @click="add_product_to_cart(product)">Add to Cart</button>
					</div>
				</div>
			</div>
			
			<!-- On Sale Pagination -->
			<div v-if="on_sale_total_pages > 1" class="pagination_controls">
				<button 
					@click="prev_on_sale_page" 
					:disabled="on_sale_page === 1"
					class="pagination_btn prev_btn"
				>
					← Previous
				</button>
				<div class="pagination_info">
					Page {{ on_sale_page }} of {{ on_sale_total_pages }}
				</div>
				<button 
					@click="next_on_sale_page" 
					:disabled="on_sale_page >= on_sale_total_pages"
					class="pagination_btn next_btn"
				>
					Next →
				</button>
			</div>
		</section>

		<!-- CTA Section -->
		<section class="cta_section">
			<div class="cta_container">
				<div class="cta_content">
					<h2 class="cta_title">Ready to Experience Premium?</h2>
					<p class="cta_subtitle">Join thousands of connoisseurs who trust BottlePlug for their finest selections</p>
					<div class="cta_actions">
						<RouterLink to="/products" class="cta_btn_primary">Shop Premium Collection</RouterLink>
						<RouterLink to="/events" class="cta_btn_secondary">View Events</RouterLink>
					</div>
				</div>
			</div>
		</section>

		<!-- Debug Section (only show in development) -->
		<section v-if="is_dev" class="debug_section">
			<div class="container">
				<h3>Debug Information</h3>
				<div class="debug_info">
					<p><strong>Authentication State:</strong> {{ auth_store.is_authenticated ? 'Authenticated' : 'Not Authenticated' }}</p>
					<p><strong>Firebase User:</strong> {{ auth_store.firebase_user ? 'Exists' : 'None' }}</p>
					<p><strong>User Anonymous:</strong> {{ auth_store.firebase_user?.isAnonymous ? 'Yes' : 'No' }}</p>
					<p><strong>Session Valid:</strong> {{ auth_store.is_session_valid() ? 'Yes' : 'No' }}</p>
					<p><strong>Cart Items:</strong> {{ cart.items.length }}</p>
				</div>
				<div class="debug_actions">
					<button @click="test_cart_functionality" class="debug_btn">Test Cart Functionality</button>
					<button @click="test_auth_state" class="debug_btn">Test Auth State</button>
				</div>
			</div>
		</section>
	</div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue'
import { use_products_store } from '../stores/products'
import { use_cart_store } from '../stores/cart'
import { useRouter } from 'vue-router'
import { get_new_arrivals, get_on_sale, get_featured_products } from '../services/api'
import { set_seo } from '../lib/seo'
import { analytics } from '../services/analytics'
import { require_auth_for_action } from '../utils/auth_guard'
import { toast_success, toast_error } from '../lib/toast'
import { use_auth_store } from '../stores/auth'
import { image_url, category_image_url, get_fallback_image_url } from '../utils/image_utils'

const store = use_products_store()
const cart = use_cart_store()
const router = useRouter()
const new_arrivals = ref([])
const on_sale = ref([])
const featured = ref([])
const search_term = ref('')
const auth_store = use_auth_store()
const is_dev = computed(() => import.meta.env.DEV)

// Pagination state
const featured_page = ref(1)
const new_arrivals_page = ref(1)
const on_sale_page = ref(1)
const items_per_page = 6

onMounted(async () => {
	console.log('Loading homepage data...')
	
	// Load categories and products (using web token)
	await Promise.all([
		store.fetch_categories(),
		store.fetch_products({})
	])
	
	console.log('Categories loaded:', store.categories.length)
	console.log('Category data:', store.categories.map(c => ({ id: c.id, name: c.name, image: c.image })))
	console.log('Products loaded:', store.products.length)
	
	// Load initial paginated data for each section
	await Promise.all([
		load_featured_products(),
		load_new_arrivals(),
		load_on_sale_products()
	])
	
	set_seo({ 
		title: 'BottlePlug · Premium Wines & Fine Spirits', 
		description: 'Discover curated wines and premium spirits from around the world. Expert curation, competitive pricing, and secure delivery.',
		                image: get_fallback_image_url() 
	})
	
	// Track page view
	analytics.track_page_view({
		page_type: 'homepage',
		products_count: store.products.length,
		categories_count: store.categories.length
	})
})

const products = computed(() => {
	console.log('Products computed:', store.products.length, store.products.slice(0, 2))
	return store.products
})

const categories = computed(() => {
	console.log('Categories computed:', store.categories.length, store.categories.slice(0, 2))
	return store.categories
})

// Paginated product sections - now using server-side pagination
const paginated_featured = ref([])
const paginated_new_arrivals = ref([])
const paginated_on_sale = ref([])

// Pagination info
const featured_total_pages = ref(1)
const new_arrivals_total_pages = ref(1)
const on_sale_total_pages = ref(1)
const featured_total_count = ref(0)
const new_arrivals_total_count = ref(0)
const on_sale_total_count = ref(0)

// Pagination functions
async function load_featured_products() {
	try {
		const params = {
			page: featured_page.value,
			page_size: items_per_page
		}
		const data = await get_featured_products(params)
		paginated_featured.value = data.results || []
		featured_total_pages.value = data.total_pages || 1
		featured_total_count.value = data.count || 0
		console.log('Featured products loaded:', paginated_featured.value.length)
	} catch (error) {
		console.error('Failed to load featured products:', error)
		paginated_featured.value = []
	}
}

async function load_new_arrivals() {
	try {
		const params = {
			page: new_arrivals_page.value,
			page_size: items_per_page
		}
		const data = await get_new_arrivals(params)
		paginated_new_arrivals.value = data.results || []
		new_arrivals_total_pages.value = data.total_pages || 1
		new_arrivals_total_count.value = data.count || 0
		console.log('New arrivals loaded:', paginated_new_arrivals.value.length)
	} catch (error) {
		console.error('Failed to load new arrivals:', error)
		paginated_new_arrivals.value = []
	}
}

async function load_on_sale_products() {
	try {
		const params = {
			page: on_sale_page.value,
			page_size: items_per_page
		}
		const data = await get_on_sale(params)
		paginated_on_sale.value = data.results || []
		on_sale_total_pages.value = data.total_pages || 1
		on_sale_total_count.value = data.count || 0
		console.log('On-sale products loaded:', paginated_on_sale.value.length)
	} catch (error) {
		console.error('Failed to load on-sale products:', error)
		paginated_on_sale.value = []
	}
}



const hero_product = computed(() => 
	(paginated_featured.value && paginated_featured.value.length ? paginated_featured.value[0] : 
	(products.value && products.value.length ? products.value[0] : null))
)
const hero_price = computed(() => Number(hero_product.value?.price || 1299))
const old_price = computed(() => Number(hero_product.value?.original_price || hero_product.value?.compare_at_price || 1599))
const save_amount = computed(() => Math.max(0, Number(old_price.value || 0) - Number(hero_price.value || 0)))

// Image URL functions are now imported from utils/image_utils.js

function format_price(value) {
	const amount = Number(value) || 0
	return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', minimumFractionDigits: 0 }).format(amount)
}



async function add_product_to_cart(product) {
	console.log('add_product_to_cart called with:', product)
	console.log('Current auth state:', auth_store.is_authenticated)
	
	return require_auth_for_action('Add to Cart', async () => {
		try {
			console.log('Adding product to cart:', product.id, product.name)
			console.log('User is authenticated, proceeding with cart operation')
			
			await cart.add_item({ product: product.id, quantity: 1 })
			analytics.track_add_to_cart(product.id, product.name, 1, product.price)
			// Show success message
			toast_success(`${product.name} added to cart!`)
		} catch (error) {
			console.error('Failed to add to cart:', error)
			console.error('Error details:', error.response?.data || error.message)
			toast_error('Failed to add item to cart. Please try again.')
			throw error
		}
	}, router.currentRoute.value.fullPath)
}


function go_search() {
	const q = (search_term.value || '').trim()
	if (!q) return
	
	analytics.track_product_search(q)
	router.push({ name: 'products', query: { search: q } })
}

// Update pagination functions to include analytics and data loading
function next_featured_page() {
	if (featured_page.value < featured_total_pages.value) {
		featured_page.value++
		load_featured_products()
		analytics.track_event('pagination', { section: 'featured', page: featured_page.value })
	}
}

function prev_featured_page() {
	if (featured_page.value > 1) {
		featured_page.value--
		load_featured_products()
		analytics.track_event('pagination', { section: 'featured', page: featured_page.value })
	}
}

function next_new_arrivals_page() {
	if (new_arrivals_page.value < new_arrivals_total_pages.value) {
		new_arrivals_page.value++
		load_new_arrivals()
		analytics.track_event('pagination', { section: 'new_arrivals', page: new_arrivals_page.value })
	}
}

function prev_new_arrivals_page() {
	if (new_arrivals_page.value > 1) {
		new_arrivals_page.value--
		load_new_arrivals()
		analytics.track_event('pagination', { section: 'new_arrivals', page: new_arrivals_page.value })
	}
}

function next_on_sale_page() {
	if (on_sale_page.value < on_sale_total_pages.value) {
		on_sale_page.value++
		load_on_sale_products()
		analytics.track_event('pagination', { section: 'on_sale', page: on_sale_page.value })
	}
}

function prev_on_sale_page() {
	if (on_sale_page.value > 1) {
		on_sale_page.value--
		load_on_sale_products()
		analytics.track_event('pagination', { section: 'on_sale', page: on_sale_page.value })
	}
}

function image_srcset(path) {
	const base = image_url(path)
	return `${base} 1x`
}

// Debug functions
async function test_cart_functionality() {
	console.log('=== Testing Cart Functionality ===')
	console.log('Auth state:', auth_store.is_authenticated)
	console.log('Firebase user:', auth_store.firebase_user)
	
	if (featured.value.length > 0) {
		const test_product = featured.value[0]
		console.log('Testing with product:', test_product)
		await add_product_to_cart(test_product)
	} else {
		console.log('No products available for testing')
	}
}

async function test_auth_state() {
	console.log('=== Testing Auth State ===')
	console.log('Auth store:', auth_store)
	console.log('Firebase user:', auth_store.firebase_user)
	console.log('Is fully authenticated:', auth_store.is_authenticated)
	console.log('Is anonymous:', auth_store.is_anonymous())
	console.log('Session valid:', auth_store.is_session_valid())
	
	// Test API call
	try {
		console.log('Testing API call to get cart...')
		await cart.fetch_cart()
		console.log('Cart fetch successful:', cart.items)
	} catch (error) {
		console.error('Cart fetch failed:', error)
	}
}
</script>

<style scoped>
.homepage {
	min-height: 100vh;
}

/* Hero Section */
.hero_section {
	position: relative;
	height: 100vh;
	min-height: 700px;
	display: flex;
	align-items: center;
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

.hero_overlay {
	position: absolute;
	inset: 0;
	background: linear-gradient(135deg, rgba(26, 15, 15, 0.8) 0%, rgba(45, 27, 27, 0.6) 50%, rgba(26, 15, 15, 0.8) 100%);
}

.hero_content {
	position: relative;
	z-index: 2;
	max-width: 1400px;
	margin: 0 auto;
	padding: 0 24px;
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 60px;
	align-items: center;
	color: white;
}

.hero_left {
	max-width: 600px;
}

.hero_badge {
	display: inline-block;
	background: linear-gradient(135deg, #8a0f2e, #4a0a1e);
	color: white;
	padding: 8px 16px;
	border-radius: 50px;
	font-weight: 700;
	font-size: 14px;
	box-shadow: 0 4px 20px rgba(138, 15, 46, 0.3);
	margin-bottom: 24px;
}

.hero_title {
	font-size: clamp(48px, 8vw, 72px);
	line-height: 1.1;
	font-weight: 900;
	margin-bottom: 20px;
	text-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.hero_accent {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.hero_subtitle {
	font-size: 20px;
	line-height: 1.6;
	opacity: 0.9;
	margin-bottom: 32px;
	max-width: 500px;
}

.hero_benefits {
	display: flex;
	flex-direction: column;
	gap: 16px;
	margin-bottom: 32px;
}

.benefit_item {
	display: flex;
	align-items: center;
	gap: 16px;
	background: rgba(255, 255, 255, 0.1);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(255, 255, 255, 0.2);
	border-radius: 16px;
	padding: 16px 20px;
	transition: all 0.3s ease;
}

.benefit_item:hover {
	background: rgba(255, 255, 255, 0.15);
	transform: translateX(8px);
}

.benefit_icon {
	width: 40px;
	height: 40px;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 18px;
	font-weight: 700;
	color: white;
	flex-shrink: 0;
}

.benefit_content {
	flex: 1;
}

.benefit_title {
	font-weight: 700;
	font-size: 16px;
	margin-bottom: 4px;
}

.benefit_desc {
	font-size: 14px;
	opacity: 0.8;
}

.hero_actions {
	display: flex;
	gap: 16px;
	margin-bottom: 24px;
}

.hero_btn_primary {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	padding: 16px 32px;
	border-radius: 50px;
	text-decoration: none;
	font-weight: 700;
	font-size: 16px;
	transition: all 0.3s ease;
	box-shadow: 0 4px 20px rgba(218, 165, 32, 0.3);
}

.hero_btn_primary:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 30px rgba(218, 165, 32, 0.4);
}

.hero_btn_secondary {
	background: transparent;
	color: white;
	padding: 16px 32px;
	border: 2px solid rgba(255, 255, 255, 0.3);
	border-radius: 50px;
	text-decoration: none;
	font-weight: 600;
	font-size: 16px;
	transition: all 0.3s ease;
}

.hero_btn_secondary:hover {
	background: rgba(255, 255, 255, 0.1);
	border-color: rgba(255, 255, 255, 0.5);
}

.hero_features {
	display: flex;
	gap: 20px;
	flex-wrap: wrap;
}

.feature_tag {
	font-size: 14px;
	opacity: 0.8;
	font-weight: 500;
}

/* Hero Right - Featured Product */
.hero_right {
	display: flex;
	justify-content: center;
	align-items: center;
}

.featured_product_card {
	background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
	backdrop-filter: blur(20px);
	border: 1px solid rgba(255, 255, 255, 0.2);
	border-radius: 24px;
	padding: 32px;
	box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
	max-width: 400px;
	width: 100%;
}

.product_highlight {
	text-align: center;
}

.highlight_icon {
	width: 80px;
	height: 80px;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32px;
	margin: 0 auto 20px;
}

.highlight_title {
	font-size: 18px;
	font-weight: 700;
	color: #DAA520;
	margin-bottom: 8px;
}

.highlight_name {
	font-size: 16px;
	font-weight: 600;
	margin-bottom: 16px;
	color: white;
}

.highlight_price {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 12px;
	margin-bottom: 24px;
	flex-wrap: wrap;
}

.current_price {
	font-size: 24px;
	font-weight: 900;
	color: #DAA520;
}

.original_price {
	font-size: 16px;
	color: rgba(255, 255, 255, 0.6);
	text-decoration: line-through;
}

.save_badge {
	background: linear-gradient(135deg, #8a0f2e, #4a0a1e);
	color: white;
	padding: 4px 12px;
	border-radius: 20px;
	font-size: 12px;
	font-weight: 700;
}

.highlight_btn {
	width: 100%;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 16px;
	border-radius: 16px;
	font-weight: 700;
	font-size: 16px;
	cursor: pointer;
	transition: all 0.3s ease;
}

.highlight_btn:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 8px 25px rgba(218, 165, 32, 0.4);
}

.highlight_btn:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}

/* Search Section */
.search_section {
	padding: 80px 24px;
	background: linear-gradient(135deg, #f8f4f0 0%, #f5f1eb 100%);
}

.search_container {
	max-width: 800px;
	margin: 0 auto;
	text-align: center;
}

.search_title {
	font-size: 36px;
	font-weight: 800;
	color: #1a0f0f;
	margin-bottom: 16px;
}

.search_subtitle {
	font-size: 18px;
	color: #666;
	margin-bottom: 40px;
}

.search_form {
	display: flex;
	max-width: 600px;
	margin: 0 auto;
	background: white;
	border-radius: 50px;
	box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
	overflow: hidden;
}

.search_input {
	flex: 1;
	border: none;
	padding: 20px 24px;
	font-size: 16px;
	outline: none;
}

.search_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 20px 24px;
	cursor: pointer;
	transition: all 0.3s ease;
}

.search_btn:hover {
	background: linear-gradient(135deg, #B8860B, #DAA520);
}

.search_icon {
	width: 20px;
	height: 20px;
}

/* Stats Section */
.stats_section {
	padding: 60px 24px;
	background: white;
}

.stats_container {
	max-width: 1200px;
	margin: 0 auto;
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
	gap: 30px;
}

.stat_item {
	text-align: center;
}

.stat_number {
	font-size: 48px;
	font-weight: 900;
	color: #DAA520;
	margin-bottom: 8px;
}

.stat_label {
	font-size: 16px;
	color: #666;
	font-weight: 600;
}

/* Categories Section */
.categories_section {
	padding: 80px 24px;
	background: linear-gradient(135deg, #f8f4f0 0%, #f5f1eb 100%);
}

.section_header {
	text-align: center;
	max-width: 600px;
	margin: 0 auto 60px;
}

.section_title {
	font-size: 36px;
	font-weight: 800;
	color: #1a0f0f;
	margin-bottom: 16px;
}

.section_subtitle {
	font-size: 18px;
	color: #666;
}

.categories_grid {
	max-width: 1200px;
	margin: 0 auto;
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
	gap: 24px;
}

.category_card {
	background: white;
	border-radius: 20px;
	overflow: hidden;
	text-decoration: none;
	color: inherit;
	transition: all 0.3s ease;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.category_card:hover {
	transform: translateY(-8px);
	box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.category_image {
	position: relative;
	height: 200px;
	overflow: hidden;
}

.category_img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	transition: transform 0.3s ease;
}

.category_card:hover .category_img {
	transform: scale(1.05);
}

.category_overlay {
	position: absolute;
	inset: 0;
	background: linear-gradient(135deg, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.1));
	display: flex;
	align-items: center;
	justify-content: center;
}

.category_icon {
	font-size: 48px;
	color: white;
	text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

.category_content {
	padding: 24px;
}

.category_name {
	font-size: 20px;
	font-weight: 700;
	color: #1a0f0f;
	margin-bottom: 8px;
}

.category_desc {
	font-size: 14px;
	color: #666;
	margin-bottom: 8px;
	line-height: 1.4;
}

.category_count {
	font-size: 12px;
	color: #DAA520;
	font-weight: 600;
}

/* Products Sections */
.featured_section,
.new_arrivals_section,
.sale_section {
	padding: 80px 24px;
}

.featured_section {
	background: white;
}

.new_arrivals_section {
	background: linear-gradient(135deg, #f8f4f0 0%, #f5f1eb 100%);
}

.sale_section {
	background: white;
}

.products_grid {
	max-width: 1200px;
	margin: 0 auto;
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
	gap: 32px;
}

.product_card {
	background: white;
	border-radius: 20px;
	overflow: hidden;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
	transition: all 0.3s ease;
	position: relative;
}

.product_card:hover {
	transform: translateY(-8px);
	box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.product_image {
	position: relative;
	height: 280px;
	overflow: hidden;
}

.product_image img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	transition: transform 0.3s ease;
}

.product_card:hover .product_image img {
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

.overlay_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	padding: 12px 24px;
	border-radius: 25px;
	text-decoration: none;
	font-weight: 600;
	transition: all 0.3s ease;
}

.overlay_btn:hover {
	transform: scale(1.05);
}

.product_badge {
	position: absolute;
	top: 16px;
	left: 16px;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	padding: 6px 12px;
	border-radius: 20px;
	font-size: 12px;
	font-weight: 700;
}

.featured_badge {
	background: linear-gradient(135deg, #DAA520, #B8860B);
}

.new_badge {
	background: linear-gradient(135deg, #4CAF50, #45a049);
}

.sale_badge {
	background: linear-gradient(135deg, #8a0f2e, #4a0a1e);
}

.product_info {
	padding: 24px;
}

.product_category {
	font-size: 12px;
	color: #DAA520;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
	margin-bottom: 8px;
}

.product_name {
	font-size: 18px;
	font-weight: 700;
	color: #1a0f0f;
	margin-bottom: 8px;
	line-height: 1.4;
}

.product_details {
	display: flex;
	gap: 12px;
	margin-bottom: 12px;
	flex-wrap: wrap;
}

.product_region,
.product_vintage {
	font-size: 12px;
	color: #666;
	background: #f5f5f5;
	padding: 4px 8px;
	border-radius: 12px;
}

.product_price {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 12px;
}

.current_price {
	font-size: 20px;
	font-weight: 800;
	color: #DAA520;
}

.original_price {
	font-size: 16px;
	color: #999;
	text-decoration: line-through;
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

.rating_text {
	font-size: 12px;
	color: #666;
}

.product_btn {
	width: 100%;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 12px;
	border-radius: 12px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
}

.product_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 25px rgba(218, 165, 32, 0.3);
}

.sale_btn {
	background: linear-gradient(135deg, #8a0f2e, #4a0a1e);
}

.sale_btn:hover {
	box-shadow: 0 8px 25px rgba(138, 15, 46, 0.3);
}

/* CTA Section */
.cta_section {
	padding: 100px 24px;
	background: linear-gradient(135deg, #1a0f0f 0%, #2d1b1b 100%);
	color: white;
	text-align: center;
}

.cta_container {
	max-width: 800px;
	margin: 0 auto;
}

.cta_title {
	font-size: 48px;
	font-weight: 900;
	margin-bottom: 20px;
}

.cta_subtitle {
	font-size: 20px;
	opacity: 0.9;
	margin-bottom: 40px;
}

.cta_actions {
	display: flex;
	gap: 20px;
	justify-content: center;
	flex-wrap: wrap;
}

.cta_btn_primary {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	padding: 16px 32px;
	border-radius: 50px;
	text-decoration: none;
	font-weight: 700;
	font-size: 16px;
	transition: all 0.3s ease;
}

.cta_btn_primary:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 30px rgba(218, 165, 32, 0.4);
}

.cta_btn_secondary {
	background: transparent;
	color: white;
	padding: 16px 32px;
	border: 2px solid rgba(255, 255, 255, 0.3);
	border-radius: 50px;
	text-decoration: none;
	font-weight: 600;
	font-size: 16px;
	transition: all 0.3s ease;
}

.cta_btn_secondary:hover {
	background: rgba(255, 255, 255, 0.1);
	border-color: rgba(255, 255, 255, 0.5);
}

/* Responsive Design */
@media (max-width: 1024px) {
	.hero_content {
		grid-template-columns: 1fr;
		gap: 40px;
		text-align: center;
	}
	
	.hero_benefits {
		align-items: center;
	}
	
	.hero_features {
		justify-content: center;
	}
	
	.categories_grid {
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
	}
	
	.products_grid {
		grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
	}
}

@media (max-width: 768px) {
	.hero_section {
		height: auto;
		min-height: 100vh;
		padding: 60px 0;
	}
	
	.hero_title {
		font-size: 48px;
	}
	
	.hero_actions {
		flex-direction: column;
		align-items: center;
	}
	
	.search_form {
		flex-direction: column;
		border-radius: 20px;
	}
	
	.search_input,
	.search_btn {
		border-radius: 0;
	}
	
	.stats_container {
		grid-template-columns: repeat(2, 1fr);
	}
}

/* Pagination Controls */
.pagination_controls {
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 20px;
	margin-top: 40px;
	padding: 20px 0;
}

.pagination_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 12px 24px;
	border-radius: 25px;
	font-weight: 600;
	font-size: 14px;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	gap: 8px;
}

.pagination_btn:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.pagination_btn:disabled {
	background: #666;
	cursor: not-allowed;
	opacity: 0.5;
}

.pagination_info {
	color: #DAA520;
	font-weight: 600;
	font-size: 14px;
	background: rgba(218, 165, 32, 0.1);
	padding: 8px 16px;
	border-radius: 20px;
	border: 1px solid rgba(218, 165, 32, 0.2);
}

.prev_btn {
	background: linear-gradient(135deg, #8B4513, #A0522D);
}

/* Debug Section */
.debug_section {
	background: #f8f9fa;
	padding: 40px 20px;
	border-top: 2px solid #e9ecef;
}

.debug_info {
	background: white;
	padding: 20px;
	border-radius: 8px;
	margin-bottom: 20px;
	border: 1px solid #dee2e6;
}

.debug_info p {
	margin: 8px 0;
	font-family: monospace;
	font-size: 14px;
}

.debug_actions {
	display: flex;
	gap: 15px;
}

.debug_btn {
	background: #007bff;
	color: white;
	border: none;
	padding: 10px 20px;
	border-radius: 5px;
	cursor: pointer;
	font-size: 14px;
}

.debug_btn:hover {
	background: #0056b3;
}

@media (max-width: 768px) {
	.debug_actions {
		flex-direction: column;
	}
}

.prev_btn:hover:not(:disabled) {
	box-shadow: 0 6px 20px rgba(139, 69, 19, 0.3);
}

.next_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
}

@media (max-width: 768px) {
	.pagination_controls {
		flex-direction: column;
		gap: 15px;
	}
	
	.pagination_btn {
		width: 100%;
		justify-content: center;
	}
}
</style>
