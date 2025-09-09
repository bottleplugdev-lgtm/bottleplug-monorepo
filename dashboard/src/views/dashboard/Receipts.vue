<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Receipts</h1>
        <p class="mt-1 text-sm text-gray-500">Manage payment receipts and transaction records</p>
      </div>
      <div class="mt-4 sm:mt-0">
        <button
          @click="syncMissingReceipts"
          class="btn btn-primary"
        >
          <RefreshCw class="h-4 w-4 mr-2" />
          Automatically Create All Missing Receipts
        </button>
      </div>
    </div>

    <!-- Receipt Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Receipts</p>
            <p class="text-2xl font-bold text-gray-900">{{ receiptSummary.total }}</p>
          </div>
          <div class="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <Receipt class="h-6 w-6 text-primary-600" />
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Today's Receipts</p>
            <p class="text-2xl font-bold text-success-600">{{ receiptSummary.today }}</p>
          </div>
          <div class="h-12 w-12 bg-success-100 rounded-lg flex items-center justify-center">
            <Calendar class="h-6 w-6 text-success-600" />
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Amount</p>
            <p class="text-2xl font-bold text-secondary-600">UGX {{ receiptSummary.totalAmount.toFixed(2) }}</p>
          </div>
          <div class="h-12 w-12 bg-secondary-100 rounded-lg flex items-center justify-center">
            <DollarSign class="h-6 w-6 text-secondary-600" />
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Avg. Receipt</p>
            <p class="text-2xl font-bold text-info-600">UGX {{ receiptSummary.averageAmount.toFixed(2) }}</p>
          </div>
          <div class="h-12 w-12 bg-info-100 rounded-lg flex items-center justify-center">
            <TrendingUp class="h-6 w-6 text-info-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Payment Methods Pie Chart -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Payment Methods Distribution</h3>
        <div class="h-80">
          <canvas ref="pieChartRef"></canvas>
        </div>
      </div>

      <!-- Daily Receipts Line Chart -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Daily Receipts Trend</h3>
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
            placeholder="Receipt ID, customer..."
            class="input"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Payment Method</label>
          <select v-model="filters.paymentMethod" class="input">
            <option value="">All Methods</option>
            <option value="cash">Cash</option>
            <option value="card">Card</option>
            <option value="mobile_money">Mobile Money</option>
            <option value="bank">Bank Transfer</option>
            <option value="check">Check</option>
            <option value="digital_wallet">Digital Wallet</option>
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
            <option value="amount">Amount</option>
            <option value="method">Payment Method</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Receipts Table -->
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Receipt Details
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Invoice
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Payment Method
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
                <div class="text-sm font-medium text-gray-900">#{{ receipt.receiptNumber }}</div>
                <div class="text-sm text-gray-500">{{ receipt.id }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
                    <User class="h-4 w-4 text-gray-600" />
                  </div>
                  <div class="ml-3">
                    <div class="text-sm font-medium text-gray-900">{{ receipt.customer.name }}</div>
                    <div class="text-sm text-gray-500">{{ receipt.customer.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ receipt.invoice.invoiceNumber }}</div>
                <div class="text-sm text-gray-500">UGX {{ receipt.invoice.totalAmount.toFixed(2) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                UGX {{ receipt.amount.toFixed(2) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 py-1 text-xs font-medium rounded-full',
                  getPaymentMethodClass(receipt.paymentMethod)
                ]">
                  {{ getPaymentMethodLabel(receipt.paymentMethod) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(receipt.paymentDate) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <button
                    @click="viewReceipt(receipt)"
                    class="text-primary-600 hover:text-primary-900"
                  >
                    <Eye class="h-4 w-4" />
                  </button>
                  <button
                    @click="printReceipt(receipt)"
                    class="text-secondary-600 hover:text-secondary-900"
                  >
                    <Printer class="h-4 w-4" />
                  </button>
                  <button
                    @click="downloadReceipt(receipt)"
                    class="text-info-600 hover:text-info-900"
                  >
                    <Download class="h-4 w-4" />
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

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Create New Receipt
                </h3>
                
                <form @submit.prevent="createReceipt" class="space-y-4">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Customer</label>
                      <select v-model="receiptForm.customerId" required class="input mt-1">
                        <option value="">Select customer</option>
                        <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                          {{ customer.name }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Invoice</label>
                      <select v-model="receiptForm.invoiceId" required class="input mt-1">
                        <option value="">Select invoice</option>
                        <option v-for="invoice in customerInvoices" :key="invoice.id" :value="invoice.id">
                          {{ invoice.invoiceNumber }} - UGX {{ invoice.amountDue.toFixed(2) }} due
                        </option>
                      </select>
                    </div>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Payment Amount</label>
                      <input
                        v-model="receiptForm.amount"
                        type="number"
                        step="0.01"
                        required
                        class="input mt-1"
                        placeholder="0.00"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Payment Method</label>
                      <select v-model="receiptForm.paymentMethod" required class="input mt-1">
                        <option value="">Select method</option>
                        <option value="cash">Cash</option>
                        <option value="card">Card</option>
                        <option value="bank_transfer">Bank Transfer</option>
                        <option value="check">Check</option>
                        <option value="digital_wallet">Digital Wallet</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700">Reference Number</label>
                    <input
                      v-model="receiptForm.referenceNumber"
                      type="text"
                      class="input mt-1"
                      placeholder="Transaction/Check number..."
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700">Notes</label>
                    <textarea
                      v-model="receiptForm.notes"
                      rows="3"
                      class="input mt-1"
                      placeholder="Payment notes..."
                    ></textarea>
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
  Calendar, 
  DollarSign, 
  TrendingUp,
  User,
  Eye, 
  Printer, 
  Download,
  RefreshCw
} from 'lucide-vue-next'
import { toast } from 'vue3-toastify'
import { Chart, registerables } from 'chart.js'
import { getPaymentReceipts, downloadPaymentReceiptPdf, syncMissingPaymentReceipts } from '@/services/api'

Chart.register(...registerables)

// State
const showNewReceiptModal = ref(false)
const pieChartRef = ref(null)
const lineChartRef = ref(null)
let pieChart = null
let lineChart = null

const customers = ref([
  { id: 1, name: 'John Doe', email: 'john@example.com', phone: '+1-555-0101' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', phone: '+1-555-0102' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', phone: '+1-555-0103' },
  { id: 4, name: 'Alice Brown', email: 'alice@example.com', phone: '+1-555-0104' },
  { id: 5, name: 'Charlie Wilson', email: 'charlie@example.com', phone: '+1-555-0105' }
])

const invoices = ref([
  {
    id: 1,
    invoiceNumber: 'INV-001',
    customer: { id: 1, name: 'John Doe', email: 'john@example.com' },
    totalAmount: 158.32,
    amountDue: 158.32,
    status: 'sent'
  },
  {
    id: 2,
    invoiceNumber: 'INV-002',
    customer: { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
    totalAmount: 73.24,
    amountDue: 0,
    status: 'paid'
  },
  {
    id: 3,
    invoiceNumber: 'INV-003',
    customer: { id: 3, name: 'Bob Johnson', email: 'bob@example.com' },
    totalAmount: 152.84,
    amountDue: 152.84,
    status: 'overdue'
  }
])

const receipts = ref([])

const filters = ref({
  search: '',
  paymentMethod: '',
  customer: '',
  dateRange: '',
  sortBy: 'date'
})

const receiptForm = ref({
  customerId: '',
  invoiceId: '',
  amount: '',
  paymentMethod: '',
  referenceNumber: '',
  notes: ''
})

// Computed
const receiptSummary = computed(() => {
  const total = receipts.value.length
  const today = receipts.value.filter(receipt => {
    const today = new Date().toDateString()
    const receiptDate = new Date(receipt.paymentDate).toDateString()
    return today === receiptDate
  }).length
  const totalAmount = receipts.value.reduce((sum, receipt) => sum + receipt.amount, 0)
  const averageAmount = total > 0 ? totalAmount / total : 0

  return { total, today, totalAmount, averageAmount }
})

const customerInvoices = computed(() => {
  if (!receiptForm.value.customerId) return []
  return invoices.value.filter(invoice => 
    invoice.customer.id === parseInt(receiptForm.value.customerId) && 
    invoice.amountDue > 0
  )
})

const filteredReceipts = computed(() => {
  let filtered = [...receipts.value]

  if (filters.value.search) {
    filtered = filtered.filter(receipt =>
      receipt.receiptNumber.toLowerCase().includes(filters.value.search.toLowerCase()) ||
      receipt.customer.name.toLowerCase().includes(filters.value.search.toLowerCase())
    )
  }

  if (filters.value.paymentMethod) {
    filtered = filtered.filter(receipt => receipt.paymentMethod === filters.value.paymentMethod)
  }

  if (filters.value.customer) {
    filtered = filtered.filter(receipt => receipt.customer.id === parseInt(filters.value.customer))
  }

  // Sort
  filtered.sort((a, b) => {
    switch (filters.value.sortBy) {
      case 'amount':
        return b.amount - a.amount
      case 'method':
        return a.paymentMethod.localeCompare(b.paymentMethod)
      default:
        return new Date(b.paymentDate) - new Date(a.paymentDate)
    }
  })

  return filtered
})

// Chart data computations
const pieChartData = computed(() => {
  const methodCounts = {
    cash: receipts.value.filter(receipt => receipt.paymentMethod === 'cash').length,
    card: receipts.value.filter(receipt => receipt.paymentMethod === 'card').length,
    mobile_money: receipts.value.filter(receipt => receipt.paymentMethod === 'mobile_money').length,
    bank: receipts.value.filter(receipt => receipt.paymentMethod === 'bank').length,
    check: receipts.value.filter(receipt => receipt.paymentMethod === 'check').length,
    digital_wallet: receipts.value.filter(receipt => receipt.paymentMethod === 'digital_wallet').length
  }

  return {
    labels: ['Cash', 'Card', 'Mobile Money', 'Bank Transfer', 'Check', 'Digital Wallet'],
    datasets: [{
      data: [
        methodCounts.cash,
        methodCounts.card,
        methodCounts.mobile_money,
        methodCounts.bank,
        methodCounts.check,
        methodCounts.digital_wallet
      ],
      backgroundColor: [
        '#10B981', // cash
        '#3B82F6', // card
        '#06B6D4', // mobile money (cyan)
        '#8B5CF6', // bank transfer (purple)
        '#F59E0B', // check (yellow)
        '#EF4444'  // digital wallet (red)
      ],
      borderWidth: 2,
      borderColor: '#ffffff'
    }]
  }
})

const lineChartData = computed(() => {
  // Get last 7 days
  const dates = []
  const amounts = []
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().split('T')[0]
    dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))
    
    const dayReceipts = receipts.value.filter(receipt => 
      receipt.paymentDate.startsWith(dateStr)
    )
    const dayAmount = dayReceipts.reduce((sum, receipt) => sum + receipt.amount, 0)
    amounts.push(dayAmount)
  }

  return {
    labels: dates,
    datasets: [{
      label: 'Daily Receipts ($)',
      data: amounts,
      borderColor: '#10B981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      tension: 0.4,
      fill: true
    }]
  }
})

// Methods
const getPaymentMethodClass = (method) => {
  switch (method) {
    case 'cash':
      return 'bg-success-100 text-success-800'
    case 'card':
      return 'bg-secondary-100 text-secondary-800'
    case 'bank':
      return 'bg-purple-100 text-purple-800'
    case 'mobile_money':
      return 'bg-info-100 text-info-800'
    case 'check':
      return 'bg-warning-100 text-warning-800'
    case 'digital_wallet':
      return 'bg-danger-100 text-danger-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getPaymentMethodLabel = (method) => {
  switch (method) {
    case 'cash':
      return 'Cash'
    case 'card':
      return 'Card'
    case 'bank':
      return 'Bank Transfer'
    case 'mobile_money':
      return 'Mobile Money'
    case 'check':
      return 'Check'
    case 'digital_wallet':
      return 'Digital Wallet'
    default:
      return method
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const viewReceipt = (receipt) => {
  toast.info(`Viewing receipt ${receipt.receipt_number || receipt.receiptNumber}`)
}

const printReceipt = (receipt) => {
  toast.success(`Printing receipt ${receipt.receipt_number || receipt.receiptNumber}`)
}

const downloadReceipt = async (receipt) => {
  try {
    const blob = await downloadPaymentReceiptPdf(receipt.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${receipt.receipt_number || receipt.receiptNumber}.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    toast.error('Failed to download receipt PDF')
  }
}

const createReceipt = () => {
  const customer = customers.value.find(c => c.id === parseInt(receiptForm.value.customerId))
  const invoice = invoices.value.find(i => i.id === parseInt(receiptForm.value.invoiceId))
  
  const newReceipt = {
    id: Date.now(),
    receiptNumber: `RCP-${String(receipts.value.length + 1).padStart(3, '0')}`,
    customer,
    invoice: { id: invoice.id, invoiceNumber: invoice.invoiceNumber, totalAmount: invoice.totalAmount },
    amount: parseFloat(receiptForm.value.amount),
    paymentMethod: receiptForm.value.paymentMethod,
    referenceNumber: receiptForm.value.referenceNumber,
    paymentDate: new Date().toISOString(),
    notes: receiptForm.value.notes
  }
  
  // Update invoice amount due
  invoice.amountDue = Math.max(0, invoice.amountDue - newReceipt.amount)
  if (invoice.amountDue === 0) {
    invoice.status = 'paid'
  }
  
  receipts.value.unshift(newReceipt)
  toast.success(`Receipt ${newReceipt.receiptNumber} created successfully`)
  showNewReceiptModal.value = false
  
  // Reset form
  receiptForm.value = {
    customerId: '',
    invoiceId: '',
    amount: '',
    paymentMethod: '',
    referenceNumber: '',
    notes: ''
  }
  
  updateCharts()
}

const syncMissingReceipts = async () => {
  try {
    toast.info('Syncing missing receipts...')
    const res = await syncMissingPaymentReceipts()
    if (res && res.success !== false) {
      toast.success('Sync completed')
      await loadReceipts()
    } else {
      throw new Error(res?.error || 'Sync failed')
    }
  } catch (e) {
    console.error(e)
    toast.error('Failed to sync receipts')
  }
}

// Chart functions
const initPieChart = () => {
  if (pieChart) {
    pieChart.destroy()
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
}

const initLineChart = () => {
  if (lineChart) {
    lineChart.destroy()
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
}

const updateCharts = () => {
  nextTick(() => {
    if (pieChart) {
      pieChart.data = pieChartData.value
      pieChart.update()
    }
    if (lineChart) {
      lineChart.data = lineChartData.value
      lineChart.update()
    }
  })
}

// Initialize charts on mount
onMounted(() => {
  nextTick(() => {
    initPieChart()
    initLineChart()
  })
  loadReceipts()
})

const loadReceipts = async () => {
  try {
    const data = await getPaymentReceipts()
    receipts.value = (Array.isArray(data) ? data : data?.results || []).map((r) => ({
      id: r.id,
      receiptNumber: r.receipt_number,
      customer: { id: null, name: r.customer_name, email: r.customer_email },
      invoice: r.invoice ? { id: r.invoice, invoiceNumber: r.invoice, totalAmount: Number(r.amount) } : { id: null, invoiceNumber: '-', totalAmount: Number(r.amount) },
      amount: Number(r.amount),
      paymentMethod: r.payment_type || r.payment_method_name || 'unknown',
      referenceNumber: r.transaction || '',
      paymentDate: r.paid_at || r.created_at,
      notes: r.notes || ''
    }))
    updateCharts()
  } catch (e) {
    console.error('Failed to load payment receipts', e)
    toast.error('Failed to load payment receipts')
  }
}
</script> 