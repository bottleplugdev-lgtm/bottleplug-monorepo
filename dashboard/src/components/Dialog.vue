<template>
  <Transition name="dialog">
    <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop -->
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div
          class="fixed inset-0 transition-opacity bg-gray-900 bg-opacity-50"
          @click="handleBackdropClick"
        ></div>

        <!-- Dialog Panel -->
        <div class="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-2xl rounded-lg sm:my-16 sm:p-0">
          <div class="relative">
            <!-- Header -->
            <div class="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 class="text-xl font-semibold text-gray-900">
                {{ title }}
              </h3>
              <button
                @click="$emit('close')"
                class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"
              >
                <X class="h-6 w-6" />
              </button>
            </div>

            <!-- Content -->
            <div class="p-6">
              <slot />
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer" class="flex items-center justify-end px-6 py-4 border-t border-gray-200 bg-gray-50 space-x-3">
              <slot name="footer" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { X } from 'lucide-vue-next'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  },
  maxWidth: {
    type: String,
    default: 'max-w-2xl'
  }
})

const emit = defineEmits(['close'])

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    emit('close')
  }
}
</script>

<style scoped>
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-active .bg-white,
.dialog-leave-active .bg-white {
  transition: all 0.3s ease;
}

.dialog-enter-from .bg-white,
.dialog-leave-to .bg-white {
  transform: scale(0.95) translateY(-10px);
  opacity: 0;
}
</style> 