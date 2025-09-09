<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center">
      <div class="mb-6">
        <div class="mx-auto h-16 w-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
          <svg class="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">Access Denied</h3>
        <p class="text-gray-600 mb-6">
          You do not have staff permissions to access this dashboard. 
          Please contact your administrator for access.
        </p>
      </div>
      
      <div class="space-y-3">
        <button
          @click="handleLogout"
          class="w-full btn btn-primary"
        >
          Sign Out
        </button>
        <button
          @click="handleContact"
          class="w-full btn btn-outline"
        >
          Contact Administrator
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { toast } from 'vue3-toastify'

const authStore = useAuthStore()

const handleLogout = async () => {
  try {
    await authStore.logout()
    toast.success('Successfully signed out')
  } catch (error) {
    console.error('Logout error:', error)
    toast.error('Error signing out')
  }
}

const handleContact = () => {
  toast.info('Please contact your system administrator for staff access')
}
</script> 