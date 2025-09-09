import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router/index.js'
import App from './App.vue'
import { use_auth_store } from './stores/auth'
import { analytics } from './services/analytics'
import { delivery_service } from './services/delivery'
import { notification_service } from './services/notifications'
import { test_connection } from './services/api'
import './index.css'

// Initialize the Vue app
const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

// Initialize auth store
const auth_store = use_auth_store(pinia)
auth_store.init_auth()

// Set up session monitoring
function setup_session_monitoring() {
	// Check session validity every 5 minutes
	setInterval(() => {
		if (auth_store.is_authenticated && !auth_store.is_session_valid()) {
			console.log('Session expired, signing out user...')
			auth_store.sign_out_and_go_anonymous()
		}
	}, 5 * 60 * 1000) // 5 minutes
	
	// Check session remaining time every hour and log it
	setInterval(() => {
		if (auth_store.is_authenticated) {
			const remaining = auth_store.get_session_remaining_time()
			const hours = Math.round(remaining / (1000 * 60 * 60))
			if (hours > 0) {
				console.log(`Session active: ${hours} hours remaining`)
			}
		}
	}, 60 * 60 * 1000) // 1 hour
}

setup_session_monitoring()

// Initialize services
async function initialize_services() {
	try {
		console.log('Initializing BottlePlug services...')
		
		// Test backend connection
		const is_connected = await test_connection()
		if (!is_connected) {
			console.warn('Backend connection failed - some features may not work')
		}
		
		// Initialize analytics (commented out to prevent errors)
		// await analytics.init()
		
		// Initialize delivery service (commented out - endpoints not available)
		// await delivery_service.init()
		
		// Initialize notification service (commented out - endpoints not available)
		// await notification_service.init()
		
		// Track app initialization
		await analytics.track_user_action('app_initialized', {
			backend_connected: is_connected,
			services_loaded: true
		})
		
		console.log('All services initialized successfully')
	} catch (error) {
		console.error('Failed to initialize services:', error)
		analytics.track_error('service_initialization_failed', {
			error_message: error.message,
			error_stack: error.stack
		})
	}
}

// Set up global error handling
app.config.errorHandler = (error, instance, info) => {
	console.error('Vue error:', error)
	console.error('Component:', instance)
	console.error('Info:', info)
	
	analytics.track_error('vue_error', {
		error_message: error.message,
		error_stack: error.stack,
		component: instance?.$options?.name || 'unknown',
		info
	})
}

// Set up performance monitoring
if ('performance' in window) {
	window.addEventListener('load', () => {
		setTimeout(() => {
			const perf_data = performance.getEntriesByType('navigation')[0]
			if (perf_data) {
				analytics.track_performance('page_load_time', perf_data.loadEventEnd - perf_data.loadEventStart, {
					dom_content_loaded: perf_data.domContentLoadedEventEnd - perf_data.domContentLoadedEventStart,
					first_paint: perf_data.responseEnd - perf_data.fetchStart,
					time_to_interactive: perf_data.domInteractive - perf_data.fetchStart
				})
			}
		}, 0)
	})
}

// Set up router navigation tracking
router.afterEach((to, from) => {
	analytics.track_page_view({
		from_path: from?.path,
		to_path: to.path,
		route_name: to.name
	})
})

// Use router
app.use(router)

// Mount the app
app.mount('#app')

// Initialize services after app is mounted
initialize_services()

// Export for debugging
window.bottleplug_services = {
	analytics,
	delivery_service,
	notification_service,
	auth_store
}
