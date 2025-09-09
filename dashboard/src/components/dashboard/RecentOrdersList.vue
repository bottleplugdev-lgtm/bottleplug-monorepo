<template>
  <div class="space-y-3">
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="animate-pulse">
        <div class="h-12 bg-gray-200 rounded"></div>
      </div>
    </div>
    
    <div v-else-if="orders.length === 0" class="text-center py-8">
      <p class="text-gray-500">No recent orders</p>
    </div>
    
    <div v-else class="space-y-3">
      <div 
        v-for="order in orders" 
        :key="order.id"
        class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <div class="flex-1">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <ShoppingCart class="w-4 h-4 text-blue-600" />
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ order.orderNumber }}
              </p>
              <p class="text-sm text-gray-500 truncate">
                {{ order.customer }}
              </p>
            </div>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <div class="text-right">
            <p class="text-sm font-medium text-gray-900">
              UGX {{ order.amount.toFixed(2) }}
            </p>
            <p class="text-xs text-gray-500">
              {{ formatDate(order.date) }}
            </p>
          </div>
          <span :class="[
            'px-2 py-1 text-xs font-medium rounded-full',
            getStatusClass(order.status)
          ]">
            {{ order.status }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ShoppingCart } from 'lucide-vue-next'

const props = defineProps({
  orders: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric' 
  })
}

const getStatusClass = (status) => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'processing':
      return 'bg-blue-100 text-blue-800'
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'cancelled':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}
</script> 