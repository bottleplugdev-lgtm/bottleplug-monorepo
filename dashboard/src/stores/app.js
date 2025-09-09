import { defineStore } from 'pinia'
import apiService from '@/services/api'

export const useAppStore = defineStore('app', {
  state: () => ({
    // Products
    products: [],
    categories: [],
    selectedProduct: null,
    
    // Orders
    orders: [],
    selectedOrder: null,
    
    // Users
    users: [],
    selectedUser: null,
    
    // Deliveries
    deliveries: [],
    selectedDelivery: null,
    
    // Analytics
    dashboardStats: {},
    revenueMetrics: {},
    userMetrics: {},
    productMetrics: {},
    orderMetrics: {},
    deliveryMetrics: {},
    
    // Notifications
    notifications: [],
    unreadCount: 0,
    
    // UI State
    loading: false,
    error: null
  }),

  getters: {
    pendingOrders: (state) => state.orders.filter(order => order.status === 'pending'),
    activeDeliveries: (state) => state.deliveries.filter(delivery => delivery.status === 'in_transit'),
    totalRevenue: (state) => state.dashboardStats.total_revenue || 0,
    totalOrders: (state) => state.dashboardStats.total_orders || 0,
    totalUsers: (state) => state.dashboardStats.total_users || 0
  },

  actions: {
    // Products
    async fetchProducts(params = {}) {
      this.loading = true
      try {
        const response = await apiService.getProducts(params)
        this.products = response.results || response
        this.error = null
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async fetchCategories() {
      try {
        this.categories = await apiService.getCategories()
      } catch (error) {
        this.error = error.message
      }
    },

    async createProduct(productData) {
      try {
        const newProduct = await apiService.createProduct(productData)
        this.products.unshift(newProduct)
        return newProduct
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async updateProduct(id, productData) {
      try {
        const updatedProduct = await apiService.updateProduct(id, productData)
        const index = this.products.findIndex(p => p.id === id)
        if (index !== -1) {
          this.products[index] = updatedProduct
        }
        return updatedProduct
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async deleteProduct(id) {
      try {
        await apiService.deleteProduct(id)
        this.products = this.products.filter(p => p.id !== id)
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // Orders
    async fetchOrders(params = {}) {
      this.loading = true
      try {
        const response = await apiService.getOrders(params)
        this.orders = response.results || response
        this.error = null
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async updateOrderStatus(id, status) {
      try {
        const updatedOrder = await apiService.updateOrderStatus(id, status)
        const index = this.orders.findIndex(o => o.id === id)
        if (index !== -1) {
          this.orders[index] = updatedOrder
        }
        return updatedOrder
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // Users
    async fetchUsers(params = {}) {
      this.loading = true
      try {
        const response = await apiService.getUsers(params)
        this.users = response.results || response
        this.error = null
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    // Deliveries
    async fetchDeliveries(params = {}) {
      this.loading = true
      try {
        const response = await apiService.getDeliveries(params)
        this.deliveries = response.results || response
        this.error = null
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async updateDeliveryStatus(id, status) {
      try {
        const updatedDelivery = await apiService.updateDeliveryStatus(id, status)
        const index = this.deliveries.findIndex(d => d.id === id)
        if (index !== -1) {
          this.deliveries[index] = updatedDelivery
        }
        return updatedDelivery
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    // Analytics
    async fetchDashboardStats() {
      try {
        this.dashboardStats = await apiService.getDashboardStats()
      } catch (error) {
        this.error = error.message
      }
    },

    async fetchAnalytics(period = 'month') {
      try {
        const [revenue, users, products, orders, deliveries] = await Promise.all([
          apiService.getRevenueMetrics(period),
          apiService.getUserMetrics(period),
          apiService.getProductMetrics(period),
          apiService.getOrderMetrics(period),
          apiService.getDeliveryMetrics(period)
        ])
        
        this.revenueMetrics = revenue
        this.userMetrics = users
        this.productMetrics = products
        this.orderMetrics = orders
        this.deliveryMetrics = deliveries
      } catch (error) {
        this.error = error.message
      }
    },

    // Notifications
    async fetchNotifications() {
      try {
        const response = await apiService.getNotifications()
        this.notifications = response.results || response
        this.unreadCount = this.notifications.filter(n => !n.is_read).length
      } catch (error) {
        this.error = error.message
      }
    },

    async markNotificationRead(id) {
      try {
        await apiService.markNotificationRead(id)
        const notification = this.notifications.find(n => n.id === id)
        if (notification) {
          notification.is_read = true
          this.unreadCount = Math.max(0, this.unreadCount - 1)
        }
      } catch (error) {
        this.error = error.message
      }
    },

    async markAllNotificationsRead() {
      try {
        await apiService.markAllNotificationsRead()
        this.notifications.forEach(n => n.is_read = true)
        this.unreadCount = 0
      } catch (error) {
        this.error = error.message
      }
    },

    // Real-time updates
    handleWebSocketMessage(data) {
      if (data.type === 'notification') {
        this.notifications.unshift(data.data)
        this.unreadCount++
      } else if (data.type === 'order_update') {
        const index = this.orders.findIndex(o => o.id === data.data.order_id)
        if (index !== -1) {
          this.orders[index].status = data.data.status
        }
      } else if (data.type === 'delivery_update') {
        const index = this.deliveries.findIndex(d => d.id === data.data.delivery_id)
        if (index !== -1) {
          this.deliveries[index].status = data.data.status
        }
      }
    },

    // Initialize app data
    async initializeApp() {
      await Promise.all([
        this.fetchDashboardStats(),
        this.fetchNotifications(),
        this.fetchCategories()
      ])
    }
  }
})