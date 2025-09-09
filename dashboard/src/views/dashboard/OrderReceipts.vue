<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Order Receipts</h1>
        <p class="mt-1 text-sm text-gray-500">Manage customer order receipts and confirmations</p>
      </div>
      <div class="mt-4 sm:mt-0">
        <button
          @click="$router.push('/dashboard/orders')"
          class="btn btn-primary"
        >
          <Plus class="h-4 w-4 mr-2" />
          Back to Orders
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-blue-100 text-blue-600">
            <Receipt class="h-6 w-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Order Receipts</p>
            <p class="text-2xl font-semibold text-gray-900">{{ receiptSummary.total }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-yellow-100 text-yellow-600">
            <Clock class="h-6 w-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Pending</p>
            <p class="text-2xl font-semibold text-gray-900">{{ receiptSummary.pending }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-green-100 text-green-600">
            <CheckCircle class="h-6 w-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Signed</p>
            <p class="text-2xl font-semibold text-gray-900">{{ receiptSummary.signed }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-purple-100 text-purple-600">
            <DollarSign class="h-6 w-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Delivered</p>
            <p class="text-2xl font-semibold text-gray-900">{{ receiptSummary.delivered }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Receipt Status Pie Chart -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Order Receipt Status Distribution</h3>
        <div class="h-80">
          <canvas ref="pieChartRef"></canvas>
        </div>
      </div>

      <!-- Monthly Receipt Value Line Chart -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Monthly Order Receipt Value Trend</h3>
        <div class="h-80">
          <canvas ref="lineChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Order receipt ID, customer..."
            class="input"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="filters.status" class="input">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="sent">Sent</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Customer</label>
          <select v-model="filters.customer" class="input">
            <option value="">All Customers</option>
            <option v-for="customer in customers" :key="customer.id" :value="customer.id">
              {{ customer.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <select v-model="filters.dateRange" class="input">
            <option value="">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select v-model="filters.sortBy" class="input">
            <option value="date">Date</option>
            <option value="value">Value</option>
            <option value="status">Status</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Receipts Table -->
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <!-- Loading State -->
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-4 text-gray-600">Loading order receipts...</p>
          </div>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="filteredReceipts.length === 0" class="flex items-center justify-center py-12">
          <div class="text-center">
            <Receipt class="h-12 w-12 text-gray-400 mx-auto" />
            <h3 class="mt-4 text-lg font-medium text-gray-900">No order receipts found</h3>
            <p class="mt-2 text-gray-600">
              {{ receipts.length === 0 ? 'No order receipts have been created yet.' : 'No order receipts match your current filters.' }}
            </p>
            <button
              v-if="receipts.length === 0"
              @click="$router.push('/dashboard/orders')"
              class="mt-4 btn btn-primary"
            >
              <Plus class="h-4 w-4 mr-2" />
              Back to Orders
            </button>
          </div>
        </div>
        
        <!-- Receipts Table -->
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Order Receipt Details
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Order Items
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total Value
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="receipt in filteredReceipts" :key="receipt.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">#{{ receipt.receipt_number }}</div>
                <div class="text-sm text-gray-500">{{ receipt.id }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
                    <User class="h-4 w-4 text-gray-600" />
                  </div>
                  <div class="ml-3">
                    <div class="text-sm font-medium text-gray-900">{{ receipt.customer_name }}</div>
                    <div class="text-sm text-gray-500">{{ receipt.customer_email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ receipt.order?.order_number || 'N/A' }}</div>
                <div class="text-sm text-gray-500">{{ receipt.order?.items?.length || 0 }} items</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                UGX {{ formatAmount(receipt.total_amount) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 py-1 text-xs font-medium rounded-full',
                  getStatusClass(receipt.status)
                ]">
                  {{ receipt.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(receipt.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center space-x-2">
                  <button
                    @click="viewReceipt(receipt)"
                    class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="View"
                  >
                    <Eye class="h-4 w-4" />
                  </button>
                  
                  <button
                    v-if="receipt.status === 'pending'"
                    @click="sendReceipt(receipt)"
                    class="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Send to Customer"
                  >
                    <Send class="h-4 w-4" />
                  </button>
                  
                  <button
                    v-if="receipt.status === 'sent'"
                    @click="signReceipt(receipt)"
                    class="p-2 text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                    title="Sign Receipt"
                  >
                    <CheckCircle class="h-4 w-4" />
                  </button>
                  
                  <button
                    v-if="receipt.status === 'signed'"
                    @click="markDelivered(receipt)"
                    class="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Mark Delivered"
                  >
                    <CheckCircle class="h-4 w-4" />
                  </button>
                  
                  <button
                    @click="editReceipt(receipt)"
                    class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Edit"
                  >
                    <Edit class="h-4 w-4" />
                  </button>
                  
                  <button
                    @click="downloadReceipt(receipt)"
                    class="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Download"
                  >
                    <Receipt class="h-4 w-4" />
                  </button>
                  
                  <button
                    @click="deleteReceiptAction(receipt)"
                    class="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- New Receipt Modal -->
    <div
      v-if="showNewReceiptModal"
      class="fixed inset-0 z-50 overflow-y-auto"
    >
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Create New Order Receipt
                </h3>
                
                <form @submit.prevent="createReceiptAction" class="space-y-4">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Order</label>
                      <select v-model="receiptForm.order" required class="input mt-1">
                        <option value="">Select order</option>
                        <option v-for="order in orders" :key="order.id" :value="order.id">
                          {{ order.order_number }} - {{ order.customer_name }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Notes</label>
                      <textarea
                        v-model="receiptForm.notes"
                        rows="3"
                        class="input mt-1"
                        placeholder="Additional notes..."
                      ></textarea>
                    </div>
                  </div>

                  <div class="flex justify-end space-x-3 pt-4">
                    <button
                      type="submit"
                      class="btn btn-primary"
                    >
                      Create Receipt
                    </button>
                    <button
                      type="button"
                      @click="showNewReceiptModal = false"
                      class="btn btn-outline"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { 
  Plus, 
  Receipt, 
  Clock, 
  CheckCircle, 
  DollarSign,
  User,
  Eye, 
  Edit, 
  Trash2,
  Send
} from 'lucide-vue-next'
import { toast } from 'vue3-toastify'
import { Chart, registerables } from 'chart.js'
import {
  getReceipts,
  getReceipt,
  createReceipt,
  updateReceipt,
  deleteReceipt,
  getMyReceipts,
  sendReceiptToCustomer,
  signReceiptByCustomer,
  markReceiptDelivered,
  getUsers,
  getProducts,
  getOrders
} from '@/services/api'

Chart.register(...registerables)

// State
const showNewReceiptModal = ref(false)
const pieChartRef = ref(null)
const lineChartRef = ref(null)
let pieChart = null
let lineChart = null

const customers = ref([])
const products = ref([])
const receipts = ref([])
const loading = ref(false)
const orders = ref([])

const filters = ref({
  search: '',
  status: '',
  customer: '',
  dateRange: '',
  sortBy: 'date'
})

const receiptForm = ref({
  order: '',
  notes: ''
})

// Computed
const receiptSummary = computed(() => {
  const total = receipts.value.length
  const pending = receipts.value.filter(r => r.status === 'pending').length
  const sent = receipts.value.filter(r => r.status === 'sent').length
  const signed = receipts.value.filter(r => r.status === 'signed').length
  const delivered = receipts.value.filter(r => r.status === 'delivered').length
  
  return { total, pending, sent, signed, delivered }
})

const filteredReceipts = computed(() => {
  let filtered = receipts.value

  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(receipt => 
      receipt.receipt_number.toLowerCase().includes(search) ||
      receipt.customer_name.toLowerCase().includes(search) ||
      receipt.customer_email.toLowerCase().includes(search)
    )
  }

  if (filters.value.status) {
    filtered = filtered.filter(receipt => receipt.status === filters.value.status)
  }

  if (filters.value.customer) {
    filtered = filtered.filter(receipt => receipt.customer_name === filters.value.customer)
  }

  // Sort
  switch (filters.value.sortBy) {
    case 'date':
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    case 'amount':
      filtered.sort((a, b) => b.total_amount - a.total_amount)
      break
    case 'status':
      filtered.sort((a, b) => a.status.localeCompare(b.status))
      break
  }

  return filtered
})

// Methods
const fetchReceipts = async () => {
  try {
    console.log('Fetching order receipts...')
    loading.value = true
    const response = await getReceipts()
    console.log('Order receipts API response:', response)
    receipts.value = response.results || response || []
    console.log('Order receipts loaded:', receipts.value)
    console.log('Order receipts count after loading:', receipts.value.length)
  } catch (error) {
    console.error('Failed to fetch order receipts:', error)
    console.error('Error details:', {
      message: error.message,
      status: error.status,
      response: error.response
    })
    toast.error('Failed to load order receipts')
  } finally {
    loading.value = false
    console.log('Loading finished, order receipts count:', receipts.value.length)
  }
}

const fetchCustomers = async () => {
  try {
    const response = await getUsers()
    customers.value = response.results || response || []
  } catch (error) {
    console.error('Failed to fetch customers:', error)
    // Don't show error toast as this is not critical
  }
}

const fetchProducts = async () => {
  try {
    const response = await getProducts()
    products.value = response.results || response || []
  } catch (error) {
    console.error('Failed to fetch products:', error)
    // Don't show error toast as this is not critical
  }
}

const fetchOrders = async () => {
  try {
    const response = await getOrders()
    orders.value = response.results || response || []
  } catch (error) {
    console.error('Failed to fetch orders:', error)
    toast.error('Failed to load orders')
  }
}

const viewReceipt = (receipt) => {
  toast.info(`Viewing receipt ${receipt.receipt_number}`)
}

const editReceipt = (receipt) => {
  toast.info(`Editing receipt ${receipt.receipt_number}`)
}

const sendReceipt = async (receipt) => {
  try {
    await sendReceiptToCustomer(receipt.id)
    receipt.status = 'sent'
    toast.success(`Order receipt ${receipt.receipt_number} sent to customer`)
    updateCharts()
  } catch (error) {
    console.error('Failed to send order receipt:', error)
    toast.error('Failed to send order receipt')
  }
}

const signReceipt = async (receipt) => {
  try {
    // In a real implementation, you would capture the signature
    const signatureData = 'customer_signature_data_here'
    await signReceiptByCustomer(receipt.id, signatureData)
    receipt.status = 'signed'
    toast.success(`Order receipt ${receipt.receipt_number} signed by customer`)
    updateCharts()
  } catch (error) {
    console.error('Failed to sign order receipt:', error)
    toast.error('Failed to sign order receipt')
  }
}

const markDelivered = async (receipt) => {
  try {
    await markReceiptDelivered(receipt.id)
    receipt.status = 'delivered'
    toast.success(`Order receipt ${receipt.receipt_number} marked as delivered`)
    updateCharts()
  } catch (error) {
    console.error('Failed to mark order receipt as delivered:', error)
    toast.error('Failed to mark order receipt as delivered')
  }
}

const deleteReceiptAction = async (receipt) => {
  try {
    await deleteReceipt(receipt.id)
    const index = receipts.value.findIndex(r => r.id === receipt.id)
    if (index !== -1) {
      receipts.value.splice(index, 1)
    }
    toast.success(`Order receipt ${receipt.receipt_number} deleted`)
    updateCharts()
  } catch (error) {
    console.error('Failed to delete order receipt:', error)
    toast.error('Failed to delete order receipt')
  }
}

const createReceiptAction = async () => {
  try {
    const receiptData = {
      order: receiptForm.value.order,
      notes: receiptForm.value.notes
    }
    
    const newReceipt = await createReceipt(receiptData)
    receipts.value.unshift(newReceipt)
    toast.success(`Order receipt ${newReceipt.receipt_number} created successfully`)
    showNewReceiptModal.value = false
    
    // Reset form
    receiptForm.value = {
      order: '',
      notes: ''
    }
    
    updateCharts()
  } catch (error) {
    console.error('Failed to create order receipt:', error)
    toast.error('Failed to create order receipt')
  }
}

const downloadReceipt = (receipt) => {
  toast.success(`Downloading order receipt ${receipt.receipt_number}`)
}

const getStatusClass = (status) => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'sent':
      return 'bg-blue-100 text-blue-800'
    case 'signed':
      return 'bg-green-100 text-green-800'
    case 'delivered':
      return 'bg-purple-100 text-purple-800'
    case 'cancelled':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatAmount = (amount) => {
  const num = parseFloat(amount) || 0
  return num.toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

// Chart data
const pieChartData = computed(() => ({
  labels: ['Pending', 'Sent', 'Signed', 'Delivered'],
  datasets: [{
    data: [
      receiptSummary.value.pending,
      receiptSummary.value.sent,
      receiptSummary.value.signed,
      receiptSummary.value.delivered
    ],
    backgroundColor: [
      '#FCD34D', // yellow
      '#3B82F6', // blue
      '#10B981', // green
      '#8B5CF6'  // purple
    ],
    borderWidth: 0
  }]
}))

const lineChartData = computed(() => {
  const currentYear = new Date().getFullYear()
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const values = []
  
  months.forEach((month, index) => {
    const monthStr = `${currentYear}-${String(index + 1).padStart(2, '0')}`
    
    const monthReceipts = receipts.value.filter(receipt => 
      receipt.created_at && receipt.created_at.startsWith(monthStr)
    )
    const monthValue = monthReceipts.reduce((sum, receipt) => sum + (parseFloat(receipt.total_amount) || 0), 0)
    values.push(monthValue)
  })
  
  console.log('Line chart data:', { months, values, receiptsCount: receipts.value.length })
  
  return {
    labels: months,
    datasets: [{
      label: 'Order Receipt Value',
      data: values,
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true
    }]
  }
})

// Chart functions
const initPieChart = () => {
  console.log('Initializing pie chart...')
  console.log('Pie chart data:', pieChartData.value)
  
  if (pieChart) {
    pieChart.destroy()
  }
  
  if (!pieChartRef.value) {
    console.error('Pie chart ref is null')
    return
  }
  
  const ctx = pieChartRef.value.getContext('2d')
  pieChart = new Chart(ctx, {
    type: 'pie',
    data: pieChartData.value,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 20,
            usePointStyle: true,
            font: { size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || ''
              const value = context.parsed
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = ((value / total) * 100).toFixed(1)
              return `${label}: ${value} (${percentage}%)`
            }
          }
        }
      }
    }
  })
  console.log('Pie chart initialized successfully')
}

const initLineChart = () => {
  console.log('Initializing line chart...')
  console.log('Line chart data:', lineChartData.value)
  
  if (lineChart) {
    lineChart.destroy()
  }
  
  if (!lineChartRef.value) {
    console.error('Line chart ref is null')
    return
  }
  
  const ctx = lineChartRef.value.getContext('2d')
  lineChart = new Chart(ctx, {
    type: 'line',
    data: lineChartData.value,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            font: { size: 12 }
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: $${context.parsed.y.toFixed(2)}`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '$' + value.toFixed(0)
            }
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  })
  console.log('Line chart initialized successfully')
}

const updateCharts = () => {
  console.log('Updating charts...')
  nextTick(() => {
    if (pieChart) {
      console.log('Updating pie chart with data:', pieChartData.value)
      pieChart.data = pieChartData.value
      pieChart.update()
    } else {
      console.warn('Pie chart not initialized')
    }
    if (lineChart) {
      console.log('Updating line chart with data:', lineChartData.value)
      lineChart.data = lineChartData.value
      lineChart.update()
    } else {
      console.warn('Line chart not initialized')
    }
  })
}

// Lifecycle
onMounted(async () => {
  console.log('OrderReceipts component mounted')
  
  try {
    console.log('Starting to fetch data...')
    await Promise.all([
      fetchReceipts(),
      fetchCustomers(),
      fetchProducts(),
      fetchOrders()
    ])
    console.log('All data fetched successfully')
    console.log('Order receipts count:', receipts.value.length)
    console.log('Filtered order receipts count:', filteredReceipts.value.length)
    
    nextTick(() => {
      console.log('Initializing charts...')
      initPieChart()
      initLineChart()
      console.log('Charts initialized')
    })
  } catch (error) {
    console.error('Error during component initialization:', error)
  }
})
</script>