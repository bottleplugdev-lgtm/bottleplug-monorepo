import { 
	get_notifications, 
	mark_notification_read, 
	mark_all_notifications_read, 
	register_push_token 
} from './api'
import { analytics } from './analytics'

// Notification types
export const NOTIFICATION_TYPES = {
	ORDER_UPDATE: 'order_update',
	DELIVERY_UPDATE: 'delivery_update',
	PAYMENT_UPDATE: 'payment_update',
	PROMOTION: 'promotion',
	NEWS: 'news',
	EVENT: 'event',
	SYSTEM: 'system',
	SECURITY: 'security'
}

// Notification priority levels
export const NOTIFICATION_PRIORITY = {
	LOW: 'low',
	NORMAL: 'normal',
	HIGH: 'high',
	URGENT: 'urgent'
}

class NotificationService {
	constructor() {
		this.notifications = []
		this.unread_count = 0
		this.push_token = null
		this.is_initialized = false
		this.notification_sound = null
		this.permission_status = 'default'
		this.websocket = null
		this.reconnect_attempts = 0
		this.max_reconnect_attempts = 5
	}

	// Initialize notification service
	async init() {
		if (this.is_initialized) return
		
		try {
			// Check notification permissions
			await this.check_notification_permission()
			
			// Load existing notifications
			await this.load_notifications()
			
			// Initialize push notifications
			await this.init_push_notifications()
			
			// Initialize WebSocket for real-time notifications
			await this.init_websocket()
			
			this.is_initialized = true
			console.log('Notification service initialized')
		} catch (error) {
			console.error('Failed to initialize notification service:', error)
		}
	}

	// Check notification permission
	async check_notification_permission() {
		if (!('Notification' in window)) {
			console.log('This browser does not support notifications')
			return false
		}

		this.permission_status = Notification.permission

		if (this.permission_status === 'default') {
			const permission = await Notification.requestPermission()
			this.permission_status = permission
			return permission === 'granted'
		}

		return this.permission_status === 'granted'
	}

	// Request notification permission
	async request_permission() {
		if (!('Notification' in window)) {
			throw new Error('This browser does not support notifications')
		}

		const permission = await Notification.requestPermission()
		this.permission_status = permission
		
		// Track analytics
		await analytics.track_user_action('notification_permission_requested', {
			permission_granted: permission === 'granted'
		})
		
		return permission === 'granted'
	}

	// Load notifications from API
	async load_notifications(params = {}) {
		try {
			this.notifications = await get_notifications(params)
			this.update_unread_count()
			return this.notifications
		} catch (error) {
			console.error('Failed to load notifications:', error)
			return []
		}
	}

	// Update unread count
	update_unread_count() {
		this.unread_count = this.notifications.filter(n => !n.is_read).length
	}

	// Mark notification as read
	async mark_as_read(notification_id) {
		try {
			await mark_notification_read(notification_id)
			
			// Update local state
			const notification = this.notifications.find(n => n.id === notification_id)
			if (notification) {
				notification.is_read = true
				this.update_unread_count()
			}
			
			// Track analytics
			await analytics.track_user_action('notification_read', {
				notification_id,
				notification_type: notification?.type
			})
			
			return true
		} catch (error) {
			console.error('Failed to mark notification as read:', error)
			return false
		}
	}

	// Mark all notifications as read
	async mark_all_as_read() {
		try {
			await mark_all_notifications_read()
			
			// Update local state
			this.notifications.forEach(n => n.is_read = true)
			this.update_unread_count()
			
			// Track analytics
			await analytics.track_user_action('all_notifications_read', {
				count: this.notifications.length
			})
			
			return true
		} catch (error) {
			console.error('Failed to mark all notifications as read:', error)
			return false
		}
	}

	// Initialize push notifications
	async init_push_notifications() {
		if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
			console.log('Push notifications not supported')
			return false
		}

		try {
			// Register service worker
			const registration = await navigator.serviceWorker.register('/sw.js')
			
			// Get push subscription
			const subscription = await registration.pushManager.getSubscription()
			
			if (subscription) {
				this.push_token = subscription
				await this.register_push_token(subscription)
			} else if (this.permission_status === 'granted') {
				await this.subscribe_to_push_notifications(registration)
			}
			
			return true
		} catch (error) {
			console.error('Failed to initialize push notifications:', error)
			return false
		}
	}

	// Subscribe to push notifications
	async subscribe_to_push_notifications(registration) {
		try {
			const subscription = await registration.pushManager.subscribe({
				userVisibleOnly: true,
				applicationServerKey: this.url_base64_to_uint8_array(process.env.VITE_VAPID_PUBLIC_KEY)
			})
			
			this.push_token = subscription
			await this.register_push_token(subscription)
			
			return subscription
		} catch (error) {
			console.error('Failed to subscribe to push notifications:', error)
			throw error
		}
	}

	// Register push token with backend
	async register_push_token(subscription) {
		try {
			const token = subscription.toJSON()
			await register_push_token(token, 'web')
			
			// Track analytics
			await analytics.track_user_action('push_token_registered', {
				platform: 'web'
			})
			
			return true
		} catch (error) {
			console.error('Failed to register push token:', error)
			return false
		}
	}

	// Convert VAPID key to Uint8Array
	url_base64_to_uint8_array(base64_string) {
		const padding = '='.repeat((4 - base64_string.length % 4) % 4)
		const base64 = (base64_string + padding)
			.replace(/-/g, '+')
			.replace(/_/g, '/')

		const raw_data = window.atob(base64)
		const output_array = new Uint8Array(raw_data.length)

		for (let i = 0; i < raw_data.length; ++i) {
			output_array[i] = raw_data.charCodeAt(i)
		}
		return output_array
	}

	// Initialize WebSocket for real-time notifications
	async init_websocket() {
		try {
			const ws_url = process.env.VITE_WS_URL || 'ws://localhost:8000/ws/notifications/'
			this.websocket = new WebSocket(ws_url)
			
			this.websocket.onopen = () => {
				console.log('WebSocket connected for notifications')
				this.reconnect_attempts = 0
			}
			
			this.websocket.onmessage = (event) => {
				this.handle_websocket_message(event.data)
			}
			
			this.websocket.onclose = () => {
				console.log('WebSocket disconnected')
				this.handle_websocket_reconnect()
			}
			
			this.websocket.onerror = (error) => {
				console.error('WebSocket error:', error)
			}
			
		} catch (error) {
			console.error('Failed to initialize WebSocket:', error)
		}
	}

	// Handle WebSocket message
	handle_websocket_message(data) {
		try {
			const message = JSON.parse(data)
			
			switch (message.type) {
				case 'notification':
					this.handle_new_notification(message.data)
					break
				case 'notification_update':
					this.handle_notification_update(message.data)
					break
				default:
					console.log('Unknown WebSocket message type:', message.type)
			}
		} catch (error) {
			console.error('Failed to parse WebSocket message:', error)
		}
	}

	// Handle new notification from WebSocket
	handle_new_notification(notification_data) {
		// Add to notifications list
		this.notifications.unshift(notification_data)
		this.update_unread_count()
		
		// Show browser notification if permission granted
		if (this.permission_status === 'granted') {
			this.show_browser_notification(notification_data)
		}
		
		// Play notification sound
		this.play_notification_sound()
		
		// Track analytics
		analytics.track_user_action('notification_received', {
			notification_id: notification_data.id,
			notification_type: notification_data.type
		})
	}

	// Handle notification update from WebSocket
	handle_notification_update(notification_data) {
		const index = this.notifications.findIndex(n => n.id === notification_data.id)
		if (index !== -1) {
			this.notifications[index] = { ...this.notifications[index], ...notification_data }
			this.update_unread_count()
		}
	}

	// Handle WebSocket reconnection
	handle_websocket_reconnect() {
		if (this.reconnect_attempts < this.max_reconnect_attempts) {
			this.reconnect_attempts++
			const delay = Math.min(1000 * Math.pow(2, this.reconnect_attempts), 30000)
			
			setTimeout(() => {
				console.log(`Attempting WebSocket reconnection ${this.reconnect_attempts}/${this.max_reconnect_attempts}`)
				this.init_websocket()
			}, delay)
		}
	}

	// Show browser notification
	show_browser_notification(notification_data) {
		const notification = new Notification(notification_data.title, {
			body: notification_data.message,
			icon: '/bottleplug_logo.png',
			badge: '/bottleplug_logo.png',
			tag: `notification_${notification_data.id}`,
			requireInteraction: notification_data.priority === NOTIFICATION_PRIORITY.URGENT,
			actions: this.get_notification_actions(notification_data)
		})
		
		notification.onclick = () => {
			this.handle_notification_click(notification_data)
			notification.close()
		}
		
		// Auto-close after 5 seconds (except for urgent notifications)
		if (notification_data.priority !== NOTIFICATION_PRIORITY.URGENT) {
			setTimeout(() => notification.close(), 5000)
		}
	}

	// Get notification actions
	get_notification_actions(notification_data) {
		const actions = []
		
		switch (notification_data.type) {
			case NOTIFICATION_TYPES.ORDER_UPDATE:
				actions.push({ action: 'view_order', title: 'View Order' })
				break
			case NOTIFICATION_TYPES.DELIVERY_UPDATE:
				actions.push({ action: 'track_delivery', title: 'Track Delivery' })
				break
			case NOTIFICATION_TYPES.PAYMENT_UPDATE:
				actions.push({ action: 'view_payment', title: 'View Payment' })
				break
			case NOTIFICATION_TYPES.EVENT:
				actions.push({ action: 'view_event', title: 'View Event' })
				break
		}
		
		return actions
	}

	// Handle notification click
	handle_notification_click(notification_data) {
		// Mark as read
		this.mark_as_read(notification_data.id)
		
		// Navigate based on notification type
		switch (notification_data.type) {
			case NOTIFICATION_TYPES.ORDER_UPDATE:
				window.location.href = `/account?tab=orders&order=${notification_data.related_id}`
				break
			case NOTIFICATION_TYPES.DELIVERY_UPDATE:
				window.location.href = `/account?tab=deliveries&delivery=${notification_data.related_id}`
				break
			case NOTIFICATION_TYPES.PAYMENT_UPDATE:
				window.location.href = `/account?tab=payments&payment=${notification_data.related_id}`
				break
			case NOTIFICATION_TYPES.EVENT:
				window.location.href = `/events/${notification_data.related_id}`
				break
			default:
				window.location.href = '/account?tab=notifications'
		}
	}

	// Play notification sound
	play_notification_sound() {
		try {
			if (!this.notification_sound) {
				this.notification_sound = new Audio('/notification.mp3')
			}
			this.notification_sound.play()
		} catch (error) {
			console.error('Failed to play notification sound:', error)
		}
	}

	// Get notifications by type
	get_notifications_by_type(type) {
		return this.notifications.filter(n => n.type === type)
	}

	// Get unread notifications
	get_unread_notifications() {
		return this.notifications.filter(n => !n.is_read)
	}

	// Get notifications by priority
	get_notifications_by_priority(priority) {
		return this.notifications.filter(n => n.priority === priority)
	}

	// Get urgent notifications
	get_urgent_notifications() {
		return this.get_notifications_by_priority(NOTIFICATION_PRIORITY.URGENT)
	}

	// Get notification statistics
	get_notification_stats() {
		const stats = {
			total: this.notifications.length,
			unread: this.unread_count,
			read: this.notifications.length - this.unread_count
		}
		
		// Count by type
		Object.values(NOTIFICATION_TYPES).forEach(type => {
			stats[type] = this.get_notifications_by_type(type).length
		})
		
		// Count by priority
		Object.values(NOTIFICATION_PRIORITY).forEach(priority => {
			stats[priority] = this.get_notifications_by_priority(priority).length
		})
		
		return stats
	}

	// Clear old notifications
	async clear_old_notifications(days_old = 30) {
		const cutoff_date = new Date()
		cutoff_date.setDate(cutoff_date.getDate() - days_old)
		
		const old_notifications = this.notifications.filter(n => {
			const notification_date = new Date(n.created_at)
			return notification_date < cutoff_date && n.is_read
		})
		
		// Remove from local state
		this.notifications = this.notifications.filter(n => {
			const notification_date = new Date(n.created_at)
			return notification_date >= cutoff_date || !n.is_read
		})
		
		this.update_unread_count()
		
		// Track analytics
		await analytics.track_user_action('old_notifications_cleared', {
			count: old_notifications.length,
			days_old
		})
		
		return old_notifications.length
	}

	// Export notification data
	export_notification_data() {
		return {
			notifications: this.notifications,
			unread_count: this.unread_count,
			stats: this.get_notification_stats(),
			permission_status: this.permission_status,
			push_enabled: !!this.push_token
		}
	}

	// Cleanup
	cleanup() {
		if (this.websocket) {
			this.websocket.close()
		}
		if (this.notification_sound) {
			this.notification_sound.pause()
			this.notification_sound = null
		}
	}
}

// Create singleton instance
export const notification_service = new NotificationService()

// Auto-initialize when module is imported (commented out to prevent errors)
// notification_service.init()

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
	notification_service.cleanup()
})

// Export for manual initialization if needed
export default notification_service 