<template>
  <div class="payment-stats">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Total Transactions -->
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CreditCard class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Transactions</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.total_transactions || 0 }}</p>
          </div>
        </div>
      </div>

      <!-- Total Amount -->
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <DollarSign class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Amount</p>
            <p class="text-2xl font-bold text-gray-900">
              UGX {{ formatAmount(stats.total_amount || 0) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Successful Payments -->
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CheckCircle class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Successful</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.successful_transactions || 0 }}</p>
          </div>
        </div>
      </div>

      <!-- Failed Payments -->
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <XCircle class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Failed</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.failed_transactions || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Stats Row -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
      <!-- Pending Payments -->
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Clock class="h-6 w-6 text-yellow-600" />
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">Pending</p>
            <p class="text-xl font-bold text-gray-900">{{ stats.pending_transactions || 0 }}</p>
          </div>
        </div>
      </div>

      <!-- Average Transaction -->
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <TrendingUp class="h-6 w-6 text-purple-600" />
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">Avg Transaction</p>
            <p class="text-xl font-bold text-gray-900">
              UGX {{ formatAmount(averageTransaction) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Today's Transactions -->
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Calendar class="h-6 w-6 text-indigo-600" />
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">Today</p>
            <p class="text-xl font-bold text-gray-900">{{ todayTransactions }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Rate -->
    <div class="mt-6">
      <div class="card p-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Payment Success Rate</h3>
        <div class="flex items-center">
          <div class="flex-1">
            <div class="flex justify-between text-sm text-gray-600 mb-2">
              <span>Success Rate</span>
              <span>{{ successRate }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-green-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${successRate}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Methods Breakdown -->
    <div class="mt-6">
      <div class="card p-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Payment Methods Breakdown</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Cash Payments -->
          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="flex items-center justify-center mb-2">
              <Wallet class="h-8 w-8 text-green-600" />
            </div>
            <h4 class="font-medium text-green-900">Cash</h4>
            <p class="text-2xl font-bold text-green-700">{{ cashTransactions }}</p>
            <p class="text-sm text-green-600">UGX {{ formatAmount(cashAmount) }}</p>
          </div>

          <!-- Mobile Money -->
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="flex items-center justify-center mb-2">
              <Smartphone class="h-8 w-8 text-blue-600" />
            </div>
            <h4 class="font-medium text-blue-900">Mobile Money</h4>
            <p class="text-2xl font-bold text-blue-700">{{ mobileMoneyTransactions }}</p>
            <p class="text-sm text-blue-600">UGX {{ formatAmount(mobileMoneyAmount) }}</p>
          </div>

          <!-- Card Payments -->
          <div class="text-center p-4 bg-purple-50 rounded-lg">
            <div class="flex items-center justify-center mb-2">
              <CreditCard class="h-8 w-8 text-purple-600" />
            </div>
            <h4 class="font-medium text-purple-900">Card</h4>
            <p class="text-2xl font-bold text-purple-700">{{ cardTransactions }}</p>
            <p class="text-sm text-purple-600">UGX {{ formatAmount(cardAmount) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="mt-6">
      <div class="card p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Recent Payment Activity</h3>
          <button
            @click="refreshStats"
            :disabled="loading"
            class="btn btn-sm btn-outline"
          >
            <RefreshCw v-if="!loading" class="h-4 w-4" />
            <div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          </button>
        </div>
        
        <div v-if="recentTransactions.length === 0" class="text-center py-4 text-gray-500">
          No recent transactions
        </div>
        
        <div v-else class="space-y-2">
          <div
            v-for="transaction in recentTransactions"
            :key="transaction.id"
            class="flex items-center justify-between p-2 bg-gray-50 rounded"
          >
            <div class="flex items-center space-x-3">
              <div
                :class="getStatusColor(transaction.status)"
                class="w-2 h-2 rounded-full"
              ></div>
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ transaction.description || `Payment for ${transaction.transaction_type}` }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ formatDate(transaction.created_at) }}
                </p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-semibold text-gray-900">
                UGX {{ formatAmount(transaction.amount) }}
              </p>
              <p class="text-xs text-gray-500 capitalize">
                {{ transaction.payment_method }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  CreditCard, 
  DollarSign, 
  CheckCircle, 
  XCircle, 
  Clock, 
  TrendingUp, 
  Calendar,
  Wallet,
  Smartphone,
  RefreshCw
} from 'lucide-vue-next'
import { toast } from 'vue3-toastify'
import { getPaymentStats, getPaymentTransactions } from '@/services/api'

const stats = ref({
  total_transactions: 0,
  total_amount: 0,
  successful_transactions: 0,
  failed_transactions: 0,
  pending_transactions: 0,
  total_fees: 0,
  net_amount: 0,
  refunds_count: 0,
  refunds_amount: 0,
  // Additional computed fields
  average_transaction: 0,
  today_transactions: 0,
  cash_transactions: 0,
  cash_amount: 0,
  mobile_money_transactions: 0,
  mobile_money_amount: 0,
  card_transactions: 0,
  card_amount: 0,
  currency: 'UGX'
})

const recentTransactions = ref([])
const loading = ref(false)

const successRate = computed(() => {
  const total = stats.value.total_transactions
  const successful = stats.value.successful_transactions
  
  if (total === 0) return 0
  return Math.round((successful / total) * 100)
})

// Computed properties to match frontend expectations
const successfulPayments = computed(() => stats.value.successful_transactions)
const failedPayments = computed(() => stats.value.failed_transactions)
const pendingPayments = computed(() => stats.value.pending_transactions)

// Computed properties for additional fields not provided by backend
const averageTransaction = computed(() => {
  if (stats.value.total_transactions === 0) return 0
  return stats.value.total_amount / stats.value.total_transactions
})

const todayTransactions = computed(() => {
  // This would need to be calculated from recent transactions
  return recentTransactions.value.filter(t => {
    const today = new Date()
    const transactionDate = new Date(t.created_at)
    return transactionDate.toDateString() === today.toDateString()
  }).length
})

const cashTransactions = computed(() => {
  return recentTransactions.value.filter(t => t.payment_method === 'cash').length
})

const cashAmount = computed(() => {
  return recentTransactions.value
    .filter(t => t.payment_method === 'cash')
    .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
})

const mobileMoneyTransactions = computed(() => {
  return recentTransactions.value.filter(t => t.payment_method === 'mobile_money').length
})

const mobileMoneyAmount = computed(() => {
  return recentTransactions.value
    .filter(t => t.payment_method === 'mobile_money')
    .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
})

const cardTransactions = computed(() => {
  return recentTransactions.value.filter(t => t.payment_method === 'card').length
})

const cardAmount = computed(() => {
  return recentTransactions.value
    .filter(t => t.payment_method === 'card')
    .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
})

const formatAmount = (amount) => {
  return new Intl.NumberFormat('en-UG').format(amount)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-UG', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusColor = (status) => {
  const colors = {
    pending: 'bg-yellow-400',
    successful: 'bg-green-400',
    failed: 'bg-red-400',
    cancelled: 'bg-gray-400'
  }
  return colors[status] || 'bg-gray-400'
}

const fetchStats = async () => {
  try {
    loading.value = true
    const response = await getPaymentStats()
    stats.value = response || {
      total_transactions: 0,
      total_amount: 0,
      successful_transactions: 0,
      failed_transactions: 0,
      pending_transactions: 0,
      total_fees: 0,
      net_amount: 0,
      refunds_count: 0,
      refunds_amount: 0,
      // Additional computed fields
      average_transaction: 0,
      today_transactions: 0,
      cash_transactions: 0,
      cash_amount: 0,
      mobile_money_transactions: 0,
      mobile_money_amount: 0,
      card_transactions: 0,
      card_amount: 0,
      currency: 'UGX'
    }
  } catch (error) {
    console.error('Failed to fetch payment stats:', error)
    toast.error('Failed to load payment statistics')
  } finally {
    loading.value = false
  }
}

const fetchRecentTransactions = async () => {
  try {
    const response = await getPaymentTransactions({ page_size: 5 })
    recentTransactions.value = response.results || response || []
  } catch (error) {
    console.error('Failed to fetch recent transactions:', error)
  }
}

const refreshStats = async () => {
  await Promise.all([fetchStats(), fetchRecentTransactions()])
  toast.success('Payment statistics refreshed')
}

onMounted(() => {
  fetchStats()
  fetchRecentTransactions()
})
</script> 