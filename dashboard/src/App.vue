<template>
  <div id="app">
    <LoadingSpinner v-if="authStore.loading" />
    <router-view v-else />
    <AccessDenied v-if="authStore.showAccessDenied" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import AccessDenied from '@/components/AccessDenied.vue'

const authStore = useAuthStore()

onMounted(() => {
  // Clear any demo sessions that might exist
  const session = localStorage.getItem('bottleplug_session')
  if (session) {
    try {
      const sessionData = JSON.parse(session)
      if (sessionData.uid === 'demo-user') {
        localStorage.removeItem('bottleplug_session')
        authStore.clearTokens()
      }
    } catch (error) {
      // Clear invalid session data
      localStorage.removeItem('bottleplug_session')
      authStore.clearTokens()
    }
  }
  
  // Auth initialization is now handled by router guards
  // This ensures better timing and avoids race conditions
  console.log('App mounted, auth will be initialized by router guards')
})
</script>

<style>
#app {
  min-height: 100vh;
}
</style> 