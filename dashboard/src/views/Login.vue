<template>
  <div class="min-h-screen bg-gradient-to-br from-secondary-50 to-secondary-100 flex items-center justify-center p-4">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo and Title -->
      <div class="text-center">
        <div class="mx-auto h-24 w-24 flex items-center justify-center">
          <img src="@/assets/images/logos/picture.png" alt="BottlePlug Logo" class="h-20 w-20 object-contain rounded-xl" />
        </div>
        <h2 class="mt-6 text-3xl font-bold text-secondary-800">BottlePlug</h2>
        <p class="mt-2 text-sm text-secondary-600">Sign in to your account</p>
      </div>

      <!-- Login Form -->
      <div class="card p-8">
        <form @submit.prevent="handleLogin" class="space-y-6" autocomplete="on">
          <div>
            <label for="email" class="block text-sm font-medium text-secondary-700">Email address</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="input mt-1"
              placeholder="Enter your email"
              autocomplete="email"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-secondary-700">Password</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="input mt-1"
              placeholder="Enter your password"
              autocomplete="current-password"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                v-model="form.rememberMe"
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label for="remember-me" class="ml-2 block text-sm text-secondary-900">
                Remember me
              </label>
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="authStore.loading"
              class="btn btn-primary w-full"
            >
              <Loader2 v-if="authStore.loading" class="mr-2 h-4 w-4 animate-spin" />
              {{ authStore.loading ? 'Signing in...' : 'Sign in' }}
            </button>
          </div>
        </form>

        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300" />
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-secondary-500">Or continue with</span>
            </div>
          </div>

          <div class="mt-6">
            <button
              @click="handleGoogleLogin"
              :disabled="authStore.loading"
              class="btn btn-outline w-full"
            >
              <svg class="mr-2 h-4 w-4" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Google
            </button>
          </div>
        </div>

        <p class="mt-6 text-center text-sm text-secondary-600">
          Don't have an account?
          <router-link to="/register" class="font-medium text-primary-600 hover:text-primary-500">
            Sign up
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { Loader2 } from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()

const form = ref({
  email: '',
  password: '',
  rememberMe: false
})

const handleLogin = async () => {
  try {
    console.log('Attempting login...')
    const result = await authStore.signInWithEmail(form.value.email, form.value.password)
    
    if (result.success) {
      console.log('Login successful, redirecting to dashboard...')
      
      // Check for intended destination or redirect to dashboard
      const intendedDestination = sessionStorage.getItem('intendedDestination')
      if (intendedDestination) {
        sessionStorage.removeItem('intendedDestination')
        console.log('Redirecting to intended destination:', intendedDestination)
        router.push(intendedDestination)
      } else {
        console.log('Redirecting to dashboard')
        router.push('/dashboard')
      }
    }
  } catch (error) {
    console.error('Login error:', error)
  }
}

const handleGoogleLogin = async () => {
  try {
    const result = await authStore.signInWithGoogle()
    
    if (result.success) {
      console.log('Google login successful, redirecting to dashboard...')
      
      // Check for intended destination or redirect to dashboard
      const intendedDestination = sessionStorage.getItem('intendedDestination')
      if (intendedDestination) {
        sessionStorage.removeItem('intendedDestination')
        router.push(intendedDestination)
      } else {
        router.push('/dashboard')
      }
    }
  } catch (error) {
    console.error('Google login error:', error)
  }
}
</script>
