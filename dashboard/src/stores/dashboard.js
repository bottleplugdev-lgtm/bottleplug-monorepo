import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { toast } from 'vue3-toastify'
import {
  getDashboardStats,
  getDashboardCharts,
  getSalesData,
  getOrderStatusData,
  getRevenueData,
  getTopProducts,
  getRecentOrders
} from '@/services/api'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const loading = ref(false)
  const stats = ref({
    users: { total: 0, new: 0 },
    products: { total: 0, low_stock: 0 },
    orders: { total: 0, revenue: 0, avg_value: 0 },
    deliveries: { total: 0, completed: 0, completion_rate: 0 }
  })
  // Chart.js safe defaults
  const salesData = ref({ labels: [], datasets: [] })
  const orderStatusData = ref({ labels: [], datasets: [] })
  const recentOrders = ref([])
  const topProducts = ref([])
  const chartsData = ref({})

  // Computed
  const totalRevenue = computed(() => stats.value.orders.revenue)
  const totalOrders = computed(() => stats.value.orders.total)
  const avgOrderValue = computed(() => stats.value.orders.avg_value)
  const totalUsers = computed(() => stats.value.users.total)
  const newUsers = computed(() => stats.value.users.new)
  const totalProducts = computed(() => stats.value.products.total)
  const lowStockProducts = computed(() => stats.value.products.low_stock)
  const totalDeliveries = computed(() => stats.value.deliveries.total)
  const completedDeliveries = computed(() => stats.value.deliveries.completed)
  const deliveryCompletionRate = computed(() => stats.value.deliveries.completion_rate)

  // Helpers to build Chart.js datasets
  const buildSalesChartData = (response) => {
    const itemsRaw = (response && response.results) ? response.results : (Array.isArray(response) ? response : [])
    // Normalize and sort by date ascending
    const items = itemsRaw
      .map(i => ({
        date: String(i.date || i.day || i.label || (i.created_at ? String(i.created_at).slice(0, 10) : '')),
        amount: Number(i.amount ?? i.total ?? i.value ?? i.revenue ?? 0),
        count: Number(i.count ?? 0)
      }))
      .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0))

    const labels = items.map(i => i.date)
    const amounts = items.map(i => i.amount)
    const counts = items.map(i => i.count)

    return {
      labels,
      datasets: [
        {
          type: 'line',
          label: 'Revenue',
          yAxisID: 'y',
          data: amounts,
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34,197,94,0.25)',
          tension: 0.3,
          fill: true,
        },
        {
          type: 'bar',
          label: 'Orders',
          yAxisID: 'y1',
          data: counts,
          backgroundColor: 'rgba(59,130,246,0.35)',
          borderColor: '#3b82f6',
          borderWidth: 1,
          maxBarThickness: 16,
        }
      ]
    }
  }

  const buildOrderStatusChartData = (response) => {
    const items = (response && response.results) ? response.results : Array.isArray(response) ? response : []
    const labels = items.map(i => i.status)
    const counts = items.map(i => Number(i.count || 0))
    const palette = ['#3b82f6', '#22c55e', '#eab308', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316']
    return {
      labels,
      datasets: [
        {
          label: 'Orders',
          data: counts,
          backgroundColor: labels.map((_, idx) => palette[idx % palette.length])
        }
      ]
    }
  }

  // Helpers to map lists for Overview components
  const mapTopProducts = (response) => {
    const items = (response && response.results) ? response.results : (response || [])
    return items.map(item => ({
      id: item.product_id ?? item.id ?? null,
      name: item.product_name ?? item.name ?? 'Unknown',
      category: item.category ?? '',
      sales: Number(item.total_quantity ?? item.sales ?? 0),
      revenue: Number(item.total_sales ?? item.revenue ?? 0)
    }))
  }

  const mapRecentOrders = (response) => {
    const items = (response && response.results) ? response.results : (response || [])
    return items.map(item => ({
      id: item.id,
      orderNumber: item.order_number ?? item.orderNumber ?? `#${item.id}`,
      customer: item.customer_name ?? item.customer ?? 'Customer',
      amount: Number(item.total_amount ?? item.amount ?? 0),
      date: item.created_at ?? item.date ?? new Date().toISOString(),
      status: item.status ?? 'pending'
    }))
  }

  // Actions
  const fetchDashboardData = async (days = 30) => {
    loading.value = true
    try {
      // Fetch all dashboard data in parallel
      const [
        statsResponse,
        chartsResponse,
        salesResponse,
        orderStatusResponse,
        revenueResponse,
        topProductsResponse,
        recentOrdersResponse
      ] = await Promise.all([
        getDashboardStats(days),
        getDashboardCharts(days),
        getSalesData(days),
        getOrderStatusData(days),
        getRevenueData(days),
        getTopProducts(days),
        getRecentOrders(days)
      ])

      // Update state with real backend data
      stats.value = statsResponse
      chartsData.value = chartsResponse || {}
      salesData.value = buildSalesChartData(salesResponse)
      orderStatusData.value = buildOrderStatusChartData(orderStatusResponse)
      topProducts.value = mapTopProducts(topProductsResponse)
      recentOrders.value = mapRecentOrders(recentOrdersResponse)

      toast.success('Dashboard data updated successfully!')
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      toast.error('Failed to load dashboard data. Please try again.')
      
      // Fallback to empty data
      stats.value = {
        users: { total: 0, new: 0 },
        products: { total: 0, low_stock: 0 },
        orders: { total: 0, revenue: 0, avg_value: 0 },
        deliveries: { total: 0, completed: 0, completion_rate: 0 }
      }
      salesData.value = { labels: [], datasets: [] }
      orderStatusData.value = { labels: [], datasets: [] }
      recentOrders.value = []
      topProducts.value = []
      chartsData.value = {}
    } finally {
      loading.value = false
    }
  }

  const updateStats = (newStats) => {
    stats.value = { ...stats.value, ...newStats }
  }

  const addRecentOrder = (order) => {
    recentOrders.value.unshift(order)
    if (recentOrders.value.length > 10) {
      recentOrders.value.pop()
    }
  }

  const updateTopProducts = (products) => {
    topProducts.value = products
  }

  const refreshData = async (days = 30) => {
    await fetchDashboardData(days)
  }

  return {
    // State
    loading,
    stats,
    salesData,
    orderStatusData,
    recentOrders,
    topProducts,
    chartsData,
    
    // Computed
    totalRevenue,
    totalOrders,
    avgOrderValue,
    totalUsers,
    newUsers,
    totalProducts,
    lowStockProducts,
    totalDeliveries,
    completedDeliveries,
    deliveryCompletionRate,
    
    // Actions
    fetchDashboardData,
    updateStats,
    addRecentOrder,
    updateTopProducts,
    refreshData
  }
}) 