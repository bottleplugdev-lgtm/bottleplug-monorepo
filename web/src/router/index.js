import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import { use_auth_store } from '../stores/auth'

const routes = [
	{ path: '/', name: 'home', component: Home },
	{ path: '/products', name: 'products', component: () => import('../views/Products.vue') },
	{ path: '/products/:id', name: 'product_detail', component: () => import('../views/ProductDetail.vue') },
	{ path: '/cart', name: 'cart', component: () => import('../views/Cart.vue') },
	{ path: '/checkout', name: 'checkout', component: () => import('../views/Checkout.vue'), meta: { requires_auth: true } },
	{ path: '/events', name: 'events', component: () => import('../views/Events.vue') },
	{ path: '/events/:id', name: 'event_detail', component: () => import('../views/EventDetail.vue') },
	{ path: '/login', name: 'login', component: () => import('../views/Login.vue') },
	{ path: '/register', name: 'register', component: () => import('../views/Register.vue') },
	{ path: '/account', name: 'account', component: () => import('../views/Account.vue'), meta: { requires_auth: true } },
	{ path: '/wishlist', name: 'wishlist', component: () => import('../views/Wishlist.vue'), meta: { requires_auth: true } },
	{ path: '/payment_return', name: 'payment_return', component: () => import('../views/PaymentReturn.vue') },
	{ path: '/order_success/:id', name: 'order_success', component: () => import('../views/OrderSuccess.vue') },
	{ path: '/about', name: 'about', component: () => import('../views/About.vue') },
	{ path: '/delivery-tracking', name: 'delivery_tracking', component: () => import('../views/DeliveryTracking.vue'), meta: { requires_auth: true } },
	{ path: '/order-history', name: 'order_history', component: () => import('../views/OrderHistory.vue'), meta: { requires_auth: true } },
	{ path: '/payments', name: 'payments', component: () => import('../views/PaymentHistory.vue'), meta: { requires_auth: true } }
]

const router = createRouter({
	history: createWebHistory(),
	routes
})

router.beforeEach(async (to, from, next) => {
	const auth_store = use_auth_store()
	
	// If auth is still initializing, wait for it to complete
	if (auth_store.should_show_loading) {
		// Wait for auth to initialize (max 3 seconds)
		let attempts = 0
		const max_attempts = 30 // 30 * 100ms = 3 seconds
		
		while (auth_store.should_show_loading && attempts < max_attempts) {
			await new Promise(resolve => setTimeout(resolve, 100))
			attempts++
		}
		
		// If still initializing after timeout, proceed anyway
		if (auth_store.should_show_loading) {
			console.warn('Auth initialization timeout, proceeding with current state')
		}
	}
	
	// Now check authentication for protected routes
	if (to.meta?.requires_auth && !auth_store.is_authenticated) {
		auth_store.set_intended_destination(to.fullPath)
		return next({ name: 'login' })
	}
	
	next()
})

router.afterEach((to) => {
    const base = 'Bottleplug'
    const title = to.name ? String(to.name).replaceAll('_',' ').replace(/\b\w/g, c => c.toUpperCase()) : ''
    document.title = title ? `${title} · ${base}` : base
})

export default router
