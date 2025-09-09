import { get_deliveries, get_my_deliveries, track_delivery, get_delivery_instructions, save_delivery_instructions, get_delivery_stats } from './api'

export const DELIVERY_STATUS = {
	PENDING: 'confirmed',
	CONFIRMED: 'confirmed',
	PROCESSING: 'processing',
	READY_FOR_DELIVERY: 'ready_for_delivery',
	OUT_FOR_DELIVERY: 'out_for_delivery',
	DELIVERED: 'delivered',
	CANCELLED: 'cancelled',
	FAILED: 'failed'
}

export const DELIVERY_EVENTS = {
	DELIVERY_CREATED: 'delivery_created',
	DELIVERY_CONFIRMED: 'delivery_confirmed',
	DELIVERY_PICKED_UP: 'delivery_picked_up',
	DELIVERY_OUT_FOR_DELIVERY: 'delivery_out_for_delivery',
	DELIVERY_DELIVERED: 'delivery_delivered',
	DELIVERY_FAILED: 'delivery_failed',
	DELIVERY_CANCELLED: 'delivery_cancelled'
}

class DeliveryService {
	constructor() {
		this.deliveries = []
		this.my_deliveries = []
		this.delivery_instructions = null
		this.delivery_stats = null
		this.tracking_updates = new Map()
		this.is_initialized = false
	}

	async init() {
		if (this.is_initialized) return
		await this.refresh_deliveries()
		await this.load_delivery_stats()
		this.delivery_instructions = await this.load_delivery_instructions()
		this.is_initialized = true
	}

	async load_delivery_instructions() {
		try {
			return await get_delivery_instructions()
		} catch (_) {
			return null
		}
	}

	async save_delivery_instructions(instructions) {
		const saved = await save_delivery_instructions(instructions)
		this.delivery_instructions = saved
		return saved
	}

	async load_deliveries(params = {}) {
		const data = await get_deliveries(params)
		this.deliveries = data?.results || data || []
		return this.deliveries
	}

	async load_my_deliveries() {
		const data = await get_my_deliveries()
		this.my_deliveries = data?.results || data || []
		return this.my_deliveries
	}

	async load_delivery_stats() {
		try {
			this.delivery_stats = await get_delivery_stats()
			return this.delivery_stats
		} catch (_) {
			return null
		}
	}

	async track_delivery_by_code(order_number) {
		const data = await track_delivery(order_number)
		return data
	}

	async refresh_deliveries() {
		await this.load_deliveries()
		await this.load_my_deliveries()
	}

	get_delivery_by_id(delivery_id) {
		return this.deliveries.find(d => d.id === delivery_id) || null
	}

	get_deliveries_by_status(status) {
		return this.deliveries.filter(d => d.status === status)
	}

	get_active_deliveries() {
		return this.my_deliveries
	}

	get_completed_deliveries() {
		return this.deliveries.filter(d => d.status === DELIVERY_STATUS.DELIVERED)
	}

	get_tracking_updates(delivery_id) { return [] }

	get_delivery_stats() {
		return this.delivery_stats || {
			total: 0,
			pending: 0,
			processing: 0,
			out_for_delivery: 0,
			delivered: 0,
			cancelled: 0
		}
	}

	is_delivery_overdue(delivery) { return false }
	get_delivery_priority(delivery) { return 'low' }
	
	calculate_delivery_progress(delivery) {
		const status_progress = {
			'confirmed': 20,
			'processing': 40,
			'ready_for_delivery': 60,
			'out_for_delivery': 80,
			'delivered': 100,
			'cancelled': 0
		}
		return status_progress[delivery.status] || 0
	}
	
	format_delivery_date(date_string) {
		return date_string ? new Date(date_string).toLocaleDateString() : 'Not specified'
	}
	
	calculate_time_until_delivery(delivery) {
		if (!delivery.estimated_delivery_time) return 'Not specified'
		const now = new Date()
		const estimated = new Date(delivery.estimated_delivery_time)
		const diff = estimated - now
		
		if (diff < 0) return 'Overdue'
		
		const days = Math.floor(diff / (1000 * 60 * 60 * 24))
		const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
		
		if (days > 0) return `${days} day(s) ${hours} hour(s)`
		if (hours > 0) return `${hours} hour(s)`
		return 'Less than 1 hour'
	}
	
	get_status_display_text(status) {
		const status_map = {
			'confirmed': 'Confirmed',
			'processing': 'Processing',
			'ready_for_delivery': 'Ready for Delivery',
			'out_for_delivery': 'Out for Delivery',
			'delivered': 'Delivered',
			'cancelled': 'Cancelled'
		}
		return status_map[status] || 'Unknown'
	}
	
	get_status_icon(status) {
		const icon_map = {
			'confirmed': '✅',
			'processing': '🔄',
			'ready_for_delivery': '📦',
			'out_for_delivery': '🚚',
			'delivered': '🎉',
			'cancelled': '❌'
		}
		return icon_map[status] || '❓'
	}
	
	get_progress_class(progress) {
		if (progress >= 80) return 'progress_high'
		if (progress >= 50) return 'progress_medium'
		return 'progress_low'
	}
	
	get_delivery_instructions_template() {
		return {
			preferred_delivery_time: '',
			delivery_notes: '',
			contact_preference: 'phone',
			leave_at_door: false,
			require_signature: true,
			special_instructions: '',
			access_instructions: '',
			security_code: '',
			landmark: ''
		}
	}
	
	validate_delivery_instructions(instructions) {
		const errors = []
		if (!instructions.preferred_delivery_time) errors.push('Preferred delivery time is required')
		if (!instructions.contact_preference) errors.push('Contact preference is required')
		return { is_valid: errors.length === 0, errors }
	}
	
	export_delivery_data(delivery_id) { return null }
}

export const delivery_service = new DeliveryService()
export default delivery_service 