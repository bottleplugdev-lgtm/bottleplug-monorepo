<template>
  <div class="space-y-3">
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="animate-pulse">
        <div class="h-12 bg-gray-200 rounded"></div>
      </div>
    </div>
    
    <div v-else-if="products.length === 0" class="text-center py-8">
      <p class="text-gray-500">No products available</p>
    </div>
    
    <div v-else class="space-y-3">
      <div 
        v-for="(product, index) in products" 
        :key="product.id"
        class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <div class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <span class="text-sm font-medium text-purple-600">{{ index + 1 }}</span>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">
              {{ product.name }}
            </p>
            <p class="text-sm text-gray-500 truncate">
              {{ product.category }}
            </p>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <div class="text-right">
            <p class="text-sm font-medium text-gray-900">
              {{ product.sales }} sold
            </p>
            <p class="text-xs text-gray-500">
              UGX {{ product.revenue.toFixed(2) }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  products: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})
</script> 