<template>
  <div class="delivery-tracking-page">
    <!-- Auth Loading State -->
    <div v-if="is_auth_loading" class="auth-loading">
      <div class="loading-spinner"></div>
      <p class="loading-text">Initializing...</p>
    </div>

    <!-- Main Content -->
    <div v-else-if="should_show_content" class="main-content">
      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">
            <span class="title-icon">🚚</span>
            Delivery Tracking
          </h1>
          <p class="hero-subtitle">Track your orders and manage deliveries in real-time</p>
        </div>
      </section>

      <!-- Stats Cards -->
      <section class="stats-section">
        <div class="container">
          <div class="stats-grid">
            <div class="stat-card" v-for="stat in delivery_stats" :key="stat.key">
              <div class="stat-icon">{{ stat.icon }}</div>
              <div class="stat-content">
                <div class="stat-number">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Track by Order Number -->
      <section class="tracking-section">
        <div class="container">
          <div class="tracking-card">
            <h2 class="section-title">Track Your Delivery</h2>
            <div class="tracking-form">
              <input
                v-model="tracking_order_number"
                type="text"
                placeholder="Enter order number (e.g., ORD-2024-001)"
                class="tracking-input"
                @keyup.enter="trackDelivery"
              />
              <button
                @click="trackDelivery"
                :disabled="!tracking_order_number || is_tracking"
                class="track-button"
              >
                <span v-if="is_tracking" class="tracking-spinner"></span>
                {{ is_tracking ? 'Tracking...' : 'Track Order' }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Active Deliveries -->
      <section class="deliveries-section">
        <div class="container">
          <h2 class="section-title">Active Deliveries</h2>
          <div v-if="is_loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading your deliveries...</p>
          </div>
          <div v-else-if="active_deliveries.length === 0" class="empty-state">
            <div class="empty-icon">📦</div>
            <h3>No Active Deliveries</h3>
            <p>You don't have any active deliveries at the moment.</p>
          </div>
          <div v-else class="deliveries-grid">
            <div
              v-for="delivery in active_deliveries"
              :key="delivery.id"
              class="delivery-card"
              @click="viewDeliveryDetails(delivery)"
            >
              <div class="delivery-header">
                <div class="delivery-status">
                  <span class="status-icon">{{ getStatusIcon(delivery.status) }}</span>
                  <span class="status-text">{{ getStatusText(delivery.status) }}</span>
                </div>
                <div class="delivery-number">#{{ delivery.order_number }}</div>
              </div>
              
              <div class="delivery-progress">
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: getDeliveryProgress(delivery) + '%' }"
                  ></div>
                </div>
                <span class="progress-text">{{ getDeliveryProgress(delivery) }}% Complete</span>
              </div>

              <div class="delivery-details">
                <div class="detail-row">
                  <span class="detail-label">Amount:</span>
                  <span class="detail-value">USh {{ formatPrice(delivery.total_amount) }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Estimated Delivery:</span>
                  <span class="detail-value">{{ formatDate(delivery.estimated_delivery_time) }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Time Remaining:</span>
                  <span class="detail-value">{{ getTimeRemaining(delivery) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Deliverable Orders -->
      <section class="orders-section">
        <div class="container">
          <h2 class="section-title">Deliverable Orders</h2>
          <div v-if="is_loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading your orders...</p>
          </div>
          <div v-else-if="deliverable_orders.length === 0" class="empty-state">
            <div class="empty-icon">📋</div>
            <h3>No Deliverable Orders</h3>
            <p>All your orders are either delivered or not yet ready for delivery.</p>
          </div>
          <div v-else class="orders-grid">
            <div
              v-for="order in deliverable_orders"
              :key="order.id"
              class="order-card"
            >
              <div class="order-header">
                <div class="order-info">
                  <h3 class="order-number">#{{ order.order_number }}</h3>
                  <p class="order-date">{{ formatDate(order.created_at) }}</p>
                </div>
                <div class="order-status">
                  <span class="status-badge" :class="getStatusClass(order.status)">
                    {{ getStatusText(order.status) }}</span>
                </div>
              </div>

              <div class="order-items">
                <div class="items-summary">
                  <span class="items-count">{{ order.items?.length || 0 }} items</span>
                </div>
              </div>

              <div class="order-footer">
                <div class="order-total">
                  <span class="total-label">Total:</span>
                  <span class="total-amount">USh {{ formatPrice(order.total_amount) }}</span>
                </div>
                <div class="delivery-fee">
                  <span class="fee-label">+ Delivery:</span>
                  <span class="fee-amount">USh {{ formatPrice(order.delivery_fee) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Tracking Result Modal -->
    <div v-if="show_tracking_modal" class="modal-overlay" @click="closeTrackingModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Delivery Details: {{ tracking_result?.order_number }}</h3>
          <button @click="closeTrackingModal" class="modal-close">×</button>
        </div>
        
        <div v-if="tracking_result" class="modal-body">
          <div class="tracking-details">
            <div class="detail-group">
              <h4>Order Information</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="detail-label">Status:</span>
                  <span class="detail-value">{{ getStatusText(tracking_result.status) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Order Date:</span>
                  <span class="detail-value">{{ formatDate(tracking_result.created_at) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Total Amount:</span>
                  <span class="detail-value">USh {{ formatPrice(tracking_result.total_amount) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Delivery Fee:</span>
                  <span class="detail-value">USh {{ formatPrice(tracking_result.delivery_fee) }}</span>
                </div>
              </div>
            </div>

            <div class="detail-group">
              <h4>Delivery Information</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="detail-label">Address:</span>
                  <span class="detail-value">{{ tracking_result.delivery_address || 'Not specified' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Instructions:</span>
                  <span class="detail-value">{{ tracking_result.delivery_instructions || 'No special instructions' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Estimated Delivery:</span>
                  <span class="detail-value">{{ formatDate(tracking_result.estimated_delivery_time) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use_auth_store } from '../stores/auth'
import { get_deliveries, get_my_deliveries, track_delivery, get_delivery_stats } from '../services/api'

// Reactive data
const is_auth_loading = ref(true)
const is_loading = ref(false)
const active_deliveries = ref([])
const deliverable_orders = ref([])
const delivery_stats_raw = ref({})
const tracking_order_number = ref('')
const is_tracking = ref(false)
const tracking_result = ref(null)
const show_tracking_modal = ref(false)

// Auth store
const auth_store = use_auth_store()

// Computed properties
const should_show_content = computed(() => !is_auth_loading.value && auth_store.is_authenticated)

const delivery_stats = computed(() => [
  {
    key: 'total',
    icon: '📦',
    label: 'Total Orders',
    value: delivery_stats_raw.value.total_deliveries || 0
  },
  {
    key: 'active',
    icon: '🚚',
    label: 'Active Deliveries',
    value: delivery_stats_raw.value.out_for_delivery || 0
  },
  {
    key: 'completed',
    icon: '✅',
    label: 'Completed',
    value: delivery_stats_raw.value.delivered || 0
  },
  {
    key: 'pending',
    icon: '⏳',
    label: 'Pending',
    value: delivery_stats_raw.value.pending || 0
  }
])

// Methods
const loadData = async () => {
  try {
    is_loading.value = true
    
    // Load all data in parallel
    const [deliveriesData, activeData, statsData] = await Promise.all([
      get_deliveries(),
      get_my_deliveries(),
      get_delivery_stats()
    ])
    
    deliverable_orders.value = deliveriesData?.results || deliveriesData || []
    active_deliveries.value = activeData?.results || activeData || []
    delivery_stats_raw.value = statsData || {}
    
  } catch (error) {
    console.error('Error loading delivery data:', error)
  } finally {
    is_loading.value = false
  }
}

const trackDelivery = async () => {
  if (!tracking_order_number.value) return
  
  is_tracking.value = true
  try {
    const result = await track_delivery(tracking_order_number.value)
    tracking_result.value = result
    show_tracking_modal.value = true
  } catch (error) {
    console.error('Error tracking delivery:', error)
    alert('Error tracking delivery. Please check the order number and try again.')
  } finally {
    is_tracking.value = false
  }
}

const closeTrackingModal = () => {
  show_tracking_modal.value = false
  tracking_result.value = null
  tracking_order_number.value = ''
}

const viewDeliveryDetails = (delivery) => {
  tracking_result.value = delivery
  show_tracking_modal.value = true
}

// Utility functions
const formatPrice = (value) => {
  if (!value && value !== 0) return '0'
  const num = parseFloat(value)
  if (isNaN(num)) return '0'
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  })
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not specified'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusIcon = (status) => {
  const iconMap = {
    'confirmed': '✅',
    'processing': '🔄',
    'ready_for_delivery': '📦',
    'out_for_delivery': '🚚',
    'delivered': '🎉',
    'cancelled': '❌'
  }
  return iconMap[status] || '❓'
}

const getStatusText = (status) => {
  const textMap = {
    'confirmed': 'Confirmed',
    'processing': 'Processing',
    'ready_for_delivery': 'Ready for Delivery',
    'out_for_delivery': 'Out for Delivery',
    'delivered': 'Delivered',
    'cancelled': 'Cancelled'
  }
  return textMap[status] || 'Unknown'
}

const getStatusClass = (status) => {
  const classMap = {
    'confirmed': 'status-confirmed',
    'processing': 'status-processing',
    'ready_for_delivery': 'status-ready',
    'out_for_delivery': 'status-out',
    'delivered': 'status-delivered',
    'cancelled': 'status-cancelled'
  }
  return classMap[status] || 'status-default'
}

const getDeliveryProgress = (delivery) => {
  const progressMap = {
    'confirmed': 20,
    'processing': 40,
    'ready_for_delivery': 60,
    'out_for_delivery': 80,
    'delivered': 100,
    'cancelled': 0
  }
  return progressMap[delivery.status] || 0
}

const getTimeRemaining = (delivery) => {
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

// Lifecycle
onMounted(async () => {
  // Wait for auth to be ready (same pattern as OrderHistory)
  if (auth_store.should_show_loading) {
    let attempts = 0
    const max_attempts = 30 // 30 * 100ms = 3 seconds
    
    while (auth_store.should_show_loading && attempts < max_attempts) {
      await new Promise(resolve => setTimeout(resolve, 100))
      attempts++
    }
  }
  
  is_auth_loading.value = false
  
  // Load data if user is authenticated
  if (auth_store.is_authenticated) {
    await loadData()
  }
})
</script>

<style scoped>
.delivery-tracking-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

/* Auth Loading */
.auth-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.loading-text {
  font-size: 1.2rem;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Main Content */
.main-content {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 0 60px;
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.title-icon {
  font-size: 4rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

.hero-subtitle {
  font-size: 1.25rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
}

/* Container */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Stats Section */

/* Stats Section */
.stats-section {
  padding: 40px 0;
  margin-top: -40px;
  position: relative;
  z-index: 2;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 30px 20px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  animation: slideInUp 0.6s ease-out;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
.stat-card:nth-child(4) { animation-delay: 0.4s; }

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-icon {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 1rem;
  color: #64748b;
  font-weight: 500;
}

/* Tracking Section */
.tracking-section {
  padding: 40px 0;
}

.tracking-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 30px;
}

.tracking-form {
  display: flex;
  gap: 15px;
  max-width: 600px;
  margin: 0 auto;
}

.tracking-input {
  flex: 1;
  padding: 15px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.tracking-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.track-button {
  padding: 15px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.track-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.track-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tracking-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Deliveries Section */
.deliveries-section {
  padding: 40px 0;
}

.deliveries-grid {
  display: grid;
  gap: 20px;
}

.delivery-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  animation: slideInLeft 0.6s ease-out;
}

.delivery-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.delivery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.delivery-status {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-icon {
  font-size: 1.5rem;
}

.status-text {
  font-weight: 600;
  color: #64748b;
}

.delivery-number {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
}

.delivery-progress {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.8s ease;
}

.progress-text {
  font-size: 0.9rem;
  color: #64748b;
  text-align: center;
  display: block;
}

.delivery-details {
  display: grid;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 0.9rem;
  color: #64748b;
}

.detail-value {
  font-weight: 600;
  color: #1e293b;
}

/* Orders Section */
.orders-section {
  padding: 40px 0 80px;
}

.orders-grid {
  display: grid;
  gap: 20px;
}

.order-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  animation: slideInRight 0.6s ease-out;
}

.order-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.order-info h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 5px;
}

.order-date {
  font-size: 0.9rem;
  color: #64748b;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-confirmed { background: #dbeafe; color: #1d4ed8; }
.status-processing { background: #fef3c7; color: #d97706; }
.status-ready { background: #dcfce7; color: #16a34a; }
.status-out { background: #fce7f3; color: #be185d; }
.status-delivered { background: #dcfce7; color: #16a34a; }
.status-cancelled { background: #fee2e2; color: #dc2626; }
.status-default { background: #f1f5f9; color: #475569; }

.order-items {
  margin-bottom: 20px;
}

.items-summary {
  text-align: center;
}

.items-count {
  font-size: 0.9rem;
  color: #64748b;
  background: #f8fafc;
  padding: 8px 16px;
  border-radius: 20px;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.order-total, .delivery-fee {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.total-label, .fee-label {
  font-size: 0.8rem;
  color: #64748b;
}

.total-amount {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
}

.fee-amount {
  font-size: 0.9rem;
  color: #64748b;
}

/* Loading and Empty States */
.loading-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #64748b;
  margin-bottom: 10px;
}

.empty-state p {
  color: #94a3b8;
  margin-bottom: 0;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideInUp 0.3s ease-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.modal-body {
  padding: 30px;
}

.detail-group {
  margin-bottom: 30px;
}

.detail-group h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

.detail-grid {
  display: grid;
  gap: 15px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.detail-label {
  font-weight: 500;
  color: #64748b;
}

.detail-value {
  font-weight: 600;
  color: #1e293b;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .title-icon {
    font-size: 3rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .tracking-form {
    flex-direction: column;
  }
  
  .delivery-header, .order-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .order-footer {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .modal-header, .modal-body {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 60px 0 40px;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .tracking-card {
    padding: 25px 20px;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
}
</style>
