<template>
  <div class="card overflow-hidden">
    <!-- Table Header -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
        <div v-if="$slots.actions" class="flex items-center space-x-2">
          <slot name="actions" />
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              :class="[
                'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                column.class || ''
              ]"
            >
              {{ column.label }}
            </th>
            <th v-if="showActions" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="(item, index) in data"
            :key="item.id || index"
            class="hover:bg-gray-50"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              :class="[
                'px-6 py-4 whitespace-nowrap text-sm text-gray-900',
                column.class || ''
              ]"
            >
              <slot :name="column.key" :item="item" :value="item[column.key]">
                {{ formatValue(item[column.key], column.type) }}
              </slot>
            </td>
            <td v-if="showActions" class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <slot name="actions" :item="item" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="data.length === 0" class="text-center py-12">
      <slot name="empty">
        <div class="text-gray-500">
          <Package class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">No data available</h3>
          <p class="mt-1 text-sm text-gray-500">Get started by adding some data.</p>
        </div>
      </slot>
    </div>

    <!-- Pagination -->
    <div v-if="showPagination && totalPages > 1" class="px-6 py-4 border-t border-gray-200">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-700">
          Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ totalItems }} results
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="prevPage"
            :disabled="currentPage === 1"
            class="btn btn-outline btn-sm"
          >
            Previous
          </button>
          <span class="text-sm text-gray-700">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
          <button
            @click="nextPage"
            :disabled="currentPage === totalPages"
            class="btn btn-outline btn-sm"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Package } from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  columns: {
    type: Array,
    required: true
  },
  data: {
    type: Array,
    required: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showPagination: {
    type: Boolean,
    default: false
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  totalItems: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['page-change'])

const totalPages = computed(() => Math.ceil(props.totalItems / props.pageSize))
const startIndex = computed(() => (props.currentPage - 1) * props.pageSize)
const endIndex = computed(() => Math.min(startIndex.value + props.pageSize, props.totalItems))

const formatValue = (value, type) => {
  if (value === null || value === undefined) return '-'
  
  switch (type) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value)
    case 'date':
      return new Date(value).toLocaleDateString()
    case 'datetime':
      return new Date(value).toLocaleString()
    case 'number':
      return new Intl.NumberFormat('en-US').format(value)
    case 'percentage':
      return `${value}%`
    default:
      return value
  }
}

const prevPage = () => {
  if (props.currentPage > 1) {
    emit('page-change', props.currentPage - 1)
  }
}

const nextPage = () => {
  if (props.currentPage < totalPages.value) {
    emit('page-change', props.currentPage + 1)
  }
}
</script> 