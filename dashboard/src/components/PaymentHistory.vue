<template>
  <div class="payment-history">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">Payment Transactions</h3>
      <div class="flex space-x-2">
        <select v-model="statusFilter" class="form-select text-sm">
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="successful">Successful</option>
          <option value="paid">Paid</option>
          <option value="failed">Failed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select v-model="paymentMethodFilter" class="form-select text-sm">
          <option value="">All Methods</option>
          <option value="cash">Cash</option>
          <option value="mobile_money">Mobile Money</option>
          <option value="card">Card</option>
        </select>
        <select v-model="typeFilter" class="form-select text-sm">
          <option value="">All Types</option>
          <option value="order">Orders</option>
          <option value="invoice">Invoices</option>
          <option value="event">Events</option>
          <option value="receipt">Receipts</option>
        </select>
        <button
          @click="refreshTransactions"
          :disabled="loading"
          class="btn btn-sm btn-outline"
        >
          <RefreshCw v-if="!loading" class="h-4 w-4" />
          <div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredTransactions.length === 0" class="text-center py-8">
      <CreditCard class="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Payment Transactions</h3>
      <p class="text-gray-500">No payment transactions found.</p>
    </div>

    <!-- Payment Transactions -->
    <div v-else class="space-y-4">
      <div
        v-for="transaction in filteredTransactions"
        :key="transaction.id"
        class="card p-4 hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div
                  :class="getStatusColor(transaction.status)"
                  class="w-3 h-3 rounded-full"
                ></div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-900">
                      {{ transaction.description || `Payment for ${transaction.transaction_type}` }}
                    </p>
                    <p class="text-xs text-gray-500">
                      {{ formatDate(transaction.created_at) }} • {{ transaction.transaction_id }}
                    </p>
                  </div>
                  <div class="text-right">
                    <p class="text-sm font-semibold text-gray-900">
                      UGX {{ formatAmount(transaction.amount) }}
                    </p>
                    <p class="text-xs text-gray-500 capitalize">
                      {{ transaction.status }}
                    </p>
                  </div>
                </div>
                
                <!-- Transaction Details -->
                <div class="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-600">
                  <div>
                    <span class="font-medium">Type:</span> {{ transaction.transaction_type }}
                  </div>
                  <div>
                    <span class="font-medium">Method:</span> {{ formatPaymentMethod(transaction.payment_method) }}
                  </div>
                  <div v-if="transaction.customer_name">
                    <span class="font-medium">Customer:</span> {{ transaction.customer_name }}
                  </div>
                  <div v-if="transaction.order_id">
                    <span class="font-medium">Order ID:</span> {{ transaction.order_id }}
                  </div>
                  <div v-if="transaction.flutterwave_charge_id">
                    <span class="font-medium">Flutterwave ID:</span> {{ transaction.flutterwave_charge_id }}
                  </div>
                  <div v-if="transaction.currency">
                    <span class="font-medium">Currency:</span> {{ transaction.currency }}
                  </div>
                </div>

                <!-- Payment URL -->
                <div v-if="transaction.payment_url" class="mt-2">
                  <a
                    :href="transaction.payment_url"
                    target="_blank"
                    class="text-xs text-blue-600 hover:text-blue-800 underline"
                  >
                    View Payment Link
                  </a>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center space-x-2 ml-4">
            <button
              v-if="transaction.status === 'pending'"
              @click="verifyPayment(transaction.id)"
              :disabled="verifying === transaction.id"
              class="text-xs text-blue-600 hover:text-blue-800 disabled:opacity-50"
            >
              {{ verifying === transaction.id ? 'Verifying...' : 'Verify' }}
            </button>
            <button
              v-if="transaction.status === 'successful'"
              @click="viewTransaction(transaction)"
              class="text-xs text-gray-600 hover:text-gray-800"
            >
              View Details
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center mt-6">
      <nav class="flex space-x-2">
        <button
          @click="changePage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="px-3 py-2 text-sm border rounded disabled:opacity-50"
        >
          Previous
        </button>
        <span class="px-3 py-2 text-sm">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button
          @click="changePage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="px-3 py-2 text-sm border rounded disabled:opacity-50"
        >
          Next
        </button>
      </nav>
    </div>

    <!-- Transaction Summary -->
    <div v-if="filteredTransactions.length > 0" class="mt-6 p-4 bg-gray-50 rounded-lg">
      <h4 class="text-sm font-medium text-gray-900 mb-2">Transaction Summary</h4>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <span class="text-gray-600">Total Transactions:</span>
          <span class="font-medium ml-1">{{ filteredTransactions.length }}</span>
        </div>
        <div>
          <span class="text-gray-600">Total Amount:</span>
          <span class="font-medium ml-1">UGX {{ formatAmount(totalAmount) }}</span>
        </div>
        <div>
          <span class="text-gray-600">Successful:</span>
          <span class="font-medium ml-1">{{ successfulCount }}</span>
        </div>
        <div>
          <span class="text-gray-600">Pending:</span>
          <span class="font-medium ml-1">{{ pendingCount }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { CreditCard, RefreshCw } from 'lucide-vue-next'
import { toast } from 'vue3-toastify'
import { getPaymentTransactions, verifyPayment as verifyPaymentApi } from '@/services/api'

const props = defineProps({
  limit: {
    type: Number,
    default: 50
  }
})

const transactions = ref([])
const loading = ref(false)
const verifying = ref(null)
const statusFilter = ref('')
const paymentMethodFilter = ref('')
const typeFilter = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

const filteredTransactions = computed(() => {
  let filtered = transactions.value

  if (statusFilter.value) {
    filtered = filtered.filter(t => t.status === statusFilter.value)
  }

  if (paymentMethodFilter.value) {
    filtered = filtered.filter(t => t.payment_method === paymentMethodFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(t => t.transaction_type === typeFilter.value)
  }

  return filtered
})

const totalAmount = computed(() => {
  return filteredTransactions.value.reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
})

const successfulCount = computed(() => {
  return filteredTransactions.value.filter(t => t.status === 'successful' || t.status === 'paid').length
})

const pendingCount = computed(() => {
  return filteredTransactions.value.filter(t => t.status === 'pending').length
})

const getStatusColor = (status) => {
  const colors = {
    pending: 'bg-yellow-400',
    successful: 'bg-green-400',
    paid: 'bg-green-400',        // Support for legacy 'paid' status
    failed: 'bg-red-400',
    cancelled: 'bg-gray-400'
  }
  return colors[status] || 'bg-gray-400'
}

const formatAmount = (amount) => {
  return new Intl.NumberFormat('en-UG').format(amount)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-UG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPaymentMethod = (method) => {
  const methods = {
    cash: 'Cash',
    mobile_money: 'Mobile Money',
    card: 'Card'
  }
  return methods[method] || method
}

const fetchTransactions = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: props.limit
    }
    
    const response = await getPaymentTransactions(params)
    transactions.value = response.results || response || []
    totalCount.value = response.count || transactions.value.length
    totalPages.value = Math.ceil(totalCount.value / props.limit)
  } catch (error) {
    console.error('Failed to fetch transactions:', error)
    toast.error('Failed to load payment transactions')
  } finally {
    loading.value = false
  }
}

const refreshTransactions = async () => {
  await fetchTransactions()
  toast.success('Payment transactions refreshed')
}

const verifyPayment = async (transactionId) => {
  try {
    verifying.value = transactionId
    const response = await verifyPaymentApi(transactionId)
    
    if (response.success) {
      toast.success('Payment verified successfully')
      await fetchTransactions() // Refresh the list
    } else {
      toast.error(response.error || 'Failed to verify payment')
    }
  } catch (error) {
    console.error('Payment verification error:', error)
    toast.error('Failed to verify payment')
  } finally {
    verifying.value = null
  }
}

const viewTransaction = (transaction) => {
  // Open transaction details in new window or modal
  if (transaction.payment_url) {
    window.open(transaction.payment_url, '_blank')
  }
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchTransactions()
  }
}

// Watch for filter changes to reset pagination
watch([statusFilter, paymentMethodFilter, typeFilter], () => {
  currentPage.value = 1
  fetchTransactions()
})

onMounted(() => {
  fetchTransactions()
})
</script> 