<template>
	<header class="site_header">
		<div class="header_container">
			<div class="brand_section">
				<RouterLink to="/" class="brand_link" aria-label="BottlePlug Home">
					<div class="logo_container">
						<img src="/bottleplug_logo_new.png" alt="BottlePlug" class="brand_logo" />
					</div>
					<div class="brand_text">
						<div class="brand_name">BottlePlug</div>
						<div class="brand_tagline">Premium Spirits & Wines</div>
					</div>
				</RouterLink>
			</div>
			<div class="nav_section">
				<RouterLink to="/" class="nav_link" @mouseover="prefetch('home')">Home</RouterLink>
                <RouterLink to="/products" class="nav_link" @mouseover="prefetch('products')">Discover</RouterLink>
                <RouterLink to="/events" class="nav_link" @mouseover="prefetch('events')">Events</RouterLink>
                <RouterLink to="/about" class="nav_link">About</RouterLink>
				<RouterLink to="/wishlist" class="util_btn hidden sm:inline-flex" aria-label="Wishlist">♡</RouterLink>
				<RouterLink to="/delivery-tracking" class="util_btn hidden sm:inline-flex" aria-label="Delivery Tracking">📦</RouterLink>
				<RouterLink to="/cart" class="util_btn" aria-label="Cart">🛒<span v-if="cart_count" class="cart_badge">{{ cart_count }}</span></RouterLink>
				<button v-if="!is_authenticated" class="auth_btn" @click="$emit('sign_in')" @mouseover="prefetch('login')">Sign In</button>
				<RouterLink v-if="is_authenticated" to="/account" class="auth_btn" @mouseover="prefetch('account')">Account</RouterLink>
				<button v-if="is_authenticated" class="auth_btn sign_out_btn" @click="sign_out">Sign Out</button>
			</div>
		</div>
	</header>
</template>

<script setup>
import { computed } from 'vue'
import { use_cart_store } from '../../stores/cart'
import { use_auth_store } from '../../stores/auth'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const cart = use_cart_store()
const auth = use_auth_store()
const router = useRouter()

const cart_count = computed(() => cart.total_quantity)
const is_authenticated = computed(() => auth.is_authenticated)
const search_term = ref('')
const open_menu = ref('')

async function sign_out() {
	await auth.sign_out_and_go_anonymous()
}

function open_group(name) { open_menu.value = name }
function close_group(name) { if (open_menu.value === name) open_menu.value = '' }
function go_products(term) { router.push({ name: 'products', query: { search: term } }) }

function go_search() {
	const q = (search_term.value || '').trim()
	router.push({ name: 'products', query: q ? { search: q } : {} })
}

function prefetch(name) {
	// trigger dynamic imports for lazy routes
	try {
		switch (name) {
			case 'products': import('../../views/Products.vue'); break
			case 'product_detail': import('../../views/ProductDetail.vue'); break
			case 'cart': import('../../views/Cart.vue'); break
			case 'checkout': import('../../views/Checkout.vue'); break
			case 'events': import('../../views/Events.vue'); break
			case 'login': import('../../views/Login.vue'); break
			case 'account': import('../../views/Account.vue'); break
			case 'wishlist': import('../../views/Wishlist.vue'); break
			default: break
		}
	} catch (_) {}
}
</script>

<style scoped>
.site_header { 
	position: sticky; 
	top: 0; 
	z-index: 30; 
	backdrop-filter: saturate(180%) blur(6px); 
	background: rgba(255,255,255,.95); 
	border-bottom: 1px solid rgba(218, 165, 32, 0.2); 
	padding: 16px 0; 
	box-shadow: 0 2px 20px rgba(0,0,0,0.08);
}

.header_container {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 20px;
}

.brand_section {
	display: flex;
	align-items: center;
}

.brand_link { 
	display: inline-flex; 
	align-items: center; 
	gap: 12px; 
	text-decoration: none; 
	transition: transform 0.3s ease;
}

.brand_link:hover {
	transform: translateY(-1px);
}

.logo_container {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: center;
	width: 48px;
	height: 48px;
	background: transparent;
	border-radius: 12px;
	padding: 4px;
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.brand_logo { 
	width: 40px; 
	height: 40px; 
	transition: transform 0.3s ease;
}

.brand_link:hover .brand_logo {
	transform: scale(1.05);
}

.brand_text {
	display: flex;
	flex-direction: column;
	gap: 2px;
}

.brand_name { 
	font-family: 'Playfair Display', serif; 
	font-weight: 700; 
	font-size: 24px; 
	background: linear-gradient(135deg, #8B4513, #DAA520); 
	-webkit-background-clip: text; 
	background-clip: text; 
	color: transparent; 
	letter-spacing: 0.5px;
	line-height: 1;
}

.brand_tagline {
	font-size: 11px;
	font-weight: 500;
	color: #666;
	letter-spacing: 0.8px;
	text-transform: uppercase;
	line-height: 1;
}

.nav_section {
	display: flex;
	align-items: center;
	gap: 8px;
}

.nav_link { 
	text-decoration: none; 
	color: #374151; 
	font-weight: 600; 
	padding: 10px 16px; 
	border-radius: 8px; 
	font-size: 14px;
	transition: all 0.3s ease;
	position: relative;
}

.nav_link:hover { 
	background: rgba(218, 165, 32, 0.1); 
	color: #8B4513; 
	transform: translateY(-1px);
}

.nav_link::after {
	content: '';
	position: absolute;
	bottom: 0;
	left: 50%;
	width: 0;
	height: 2px;
	background: linear-gradient(135deg, #DAA520, #B8860B);
	transition: all 0.3s ease;
	transform: translateX(-50%);
}

.nav_link:hover::after {
	width: 80%;
}

.util_btn { 
	display: inline-flex; 
	align-items: center; 
	justify-content: center; 
	width: 40px; 
	height: 40px; 
	border: 1px solid rgba(218, 165, 32, 0.2); 
	border-radius: 10px; 
	background: rgba(255, 255, 255, 0.8); 
	margin-right: 8px; 
	transition: all 0.3s ease;
	font-size: 16px;
}

.util_btn:hover {
	background: rgba(218, 165, 32, 0.1);
	border-color: #DAA520;
	transform: translateY(-2px);
	box-shadow: 0 4px 12px rgba(218, 165, 32, 0.2);
}

.cart_badge { 
	margin-left: 4px; 
	font-size: 11px; 
	background: linear-gradient(135deg, #8B4513, #DAA520); 
	color: #fff; 
	border-radius: 10px; 
	padding: 2px 6px; 
	font-weight: 600;
	min-width: 18px;
	text-align: center;
}

.auth_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 10px 20px;
	border-radius: 25px;
	font-weight: 600;
	font-size: 14px;
	cursor: pointer;
	transition: all 0.3s ease;
	text-decoration: none;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 4px 15px rgba(218, 165, 32, 0.3);
}

.auth_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.4);
}

.sign_out_btn {
	background: linear-gradient(135deg, #8B4513, #A0522D);
	box-shadow: 0 4px 15px rgba(139, 69, 19, 0.3);
}

.sign_out_btn:hover {
	box-shadow: 0 6px 20px rgba(139, 69, 19, 0.4);
}

/* Responsive Design */
@media (max-width: 768px) {
	.header_container {
		padding: 0 15px;
	}
	
	.brand_name {
		font-size: 20px;
	}
	
	.brand_tagline {
		font-size: 10px;
	}
	
	.nav_link {
		padding: 8px 12px;
		font-size: 13px;
	}
	
	.auth_btn {
		padding: 8px 16px;
		font-size: 13px;
	}
}

@media (max-width: 640px) {
	.brand_tagline {
		display: none;
	}
	
	.nav_section {
		gap: 4px;
	}
	
	.util_btn {
		width: 36px;
		height: 36px;
		font-size: 14px;
	}
}
</style>
