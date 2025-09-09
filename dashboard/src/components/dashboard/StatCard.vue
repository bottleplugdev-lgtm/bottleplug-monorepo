<template>
  <div class="bg-white rounded-lg shadow-sm p-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600">{{ title }}</p>
        <p class="text-2xl font-bold text-gray-900">{{ value }}</p>
        <div v-if="change !== null" class="flex items-center mt-1">
          <component 
            :is="changeIcon" 
            :class="[
              'h-4 w-4 mr-1',
              changeType === 'positive' ? 'text-green-600' : 'text-red-600'
            ]" 
          />
          <span :class="[
            'text-sm',
            changeType === 'positive' ? 'text-green-600' : 'text-red-600'
          ]">
            {{ change > 0 ? '+' : '' }}{{ change }}%
          </span>
        </div>
      </div>
      <div :class="[
        'h-12 w-12 rounded-lg flex items-center justify-center',
        iconBgClass
      ]">
        <component :is="iconComponent" :class="[iconClass, 'h-6 w-6']" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  ShoppingCart, 
  Package, 
  Users 
} from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  change: {
    type: [String, Number],
    default: null
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'blue'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const changeIcon = computed(() => {
  return props.change >= 0 ? TrendingUp : TrendingDown
})

const changeType = computed(() => {
  return props.change >= 0 ? 'positive' : 'negative'
})

const iconComponent = computed(() => {
  const iconMap = {
    DollarSign,
    ShoppingCart,
    Package,
    Users
  }
  return iconMap[props.icon] || DollarSign
})

const iconBgClass = computed(() => {
  const colorMap = {
    green: 'bg-green-100',
    blue: 'bg-blue-100',
    purple: 'bg-purple-100',
    orange: 'bg-orange-100',
    red: 'bg-red-100',
    gray: 'bg-gray-100'
  }
  return colorMap[props.color] || 'bg-blue-100'
})

const iconClass = computed(() => {
  const colorMap = {
    green: 'text-green-600',
    blue: 'text-blue-600',
    purple: 'text-purple-600',
    orange: 'text-orange-600',
    red: 'text-red-600',
    gray: 'text-gray-600'
  }
  return colorMap[props.color] || 'text-blue-600'
})
</script> 