<template>
  <button
    @click="$emit('click')"
    class="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow border border-gray-200 hover:border-gray-300"
  >
    <div class="flex flex-col items-center space-y-2">
      <div :class="[
        'w-12 h-12 rounded-lg flex items-center justify-center',
        iconBgClass
      ]">
        <component :is="iconComponent" :class="[iconClass, 'w-6 h-6']" />
      </div>
      <p class="text-sm font-medium text-gray-900 text-center">
        {{ title }}
      </p>
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { 
  Plus, 
  ShoppingCart, 
  Users, 
  BarChart3, 
  Settings, 
  FileText 
} from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'blue'
  }
})

const iconComponent = computed(() => {
  const iconMap = {
    Plus,
    ShoppingCart,
    Users,
    BarChart3,
    Settings,
    FileText
  }
  return iconMap[props.icon] || Plus
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