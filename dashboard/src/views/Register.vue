<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center p-4">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo and Title -->
      <div class="text-center">
        <div class="mx-auto h-16 w-16 bg-primary-600 rounded-full flex items-center justify-center">
          <Wine class="h-8 w-8 text-white" />
        </div>
        <h2 class="mt-6 text-3xl font-bold text-gray-900">BottlePlug</h2>
        <p class="mt-2 text-sm text-gray-600">Create your account</p>
      </div>

      <!-- Registration Form -->
      <div class="card p-8">
        <form @submit.prevent="handleRegister" class="space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="firstName" class="block text-sm font-medium text-gray-700">First Name</label>
              <input
                id="firstName"
                v-model="form.firstName"
                type="text"
                required
                class="input mt-1"
                placeholder="John"
              />
            </div>
            <div>
              <label for="lastName" class="block text-sm font-medium text-gray-700">Last Name</label>
              <input
                id="lastName"
                v-model="form.lastName"
                type="text"
                required
                class="input mt-1"
                placeholder="Doe"
              />
            </div>
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email address</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="input mt-1"
              placeholder="john@example.com"
            />
          </div>

          <div>
            <label for="phone" class="block text-sm font-medium text-gray-700">Phone Number</label>
            <input
              id="phone"
              v-model="form.phone"
              type="tel"
              class="input mt-1"
              placeholder="+1234567890"
            />
          </div>

          <div>
            <label for="businessName" class="block text-sm font-medium text-gray-700">Business Name</label>
            <input
              id="businessName"
              v-model="form.businessName"
              type="text"
              class="input mt-1"
              placeholder="Your Business Name"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="input mt-1"
              placeholder="Create a strong password"
            />
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700">Confirm Password</label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              required
              class="input mt-1"
              placeholder="Confirm your password"
            />
          </div>

          <div class="flex items-center">
            <input
              id="terms"
              v-model="form.agreeToTerms"
              type="checkbox"
              required
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label for="terms" class="ml-2 block text-sm text-gray-900">
              I agree to the
              <a href="#" class="text-primary-600 hover:text-primary-500">Terms of Service</a>
              and
              <a href="#" class="text-primary-600 hover:text-primary-500">Privacy Policy</a>
            </label>
          </div>

          <div>
            <button
              type="submit"
              :disabled="authStore.loading || !isFormValid"
              class="btn btn-primary w-full"
            >
              <Loader2 v-if="authStore.loading" class="mr-2 h-4 w-4 animate-spin" />
              {{ authStore.loading ? 'Creating account...' : 'Create account' }}
            </button>
          </div>
        </form>

        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300" />
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500">Or continue with</span>
            </div>
          </div>

          <div class="mt-6">
            <button
              @click="handleGoogleRegister"
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

        <p class="mt-6 text-center text-sm text-gray-600">
          Already have an account?
          <router-link to="/" class="font-medium text-primary-600 hover:text-primary-500">
            Sign in
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { Wine, Loader2 } from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  businessName: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false
})

const isFormValid = computed(() => {
  return form.value.firstName &&
         form.value.lastName &&
         form.value.email &&
         form.value.password &&
         form.value.confirmPassword &&
         form.value.password === form.value.confirmPassword &&
         form.value.agreeToTerms
})

const handleRegister = async () => {
  if (!isFormValid.value) return
  
  try {
    const userData = {
      displayName: `${form.value.firstName} ${form.value.lastName}`,
      firstName: form.value.firstName,
      lastName: form.value.lastName,
      phone: form.value.phone,
      businessName: form.value.businessName
    }
    
    await authStore.signUpWithEmail(form.value.email, form.value.password, userData)
    // Redirect to dashboard after successful registration
    router.push('/dashboard')
  } catch (error) {
    console.error('Registration error:', error)
  }
}

const handleGoogleRegister = async () => {
  try {
    await authStore.signInWithGoogle()
    // Redirect to dashboard after successful Google registration
    router.push('/dashboard')
  } catch (error) {
    console.error('Google registration error:', error)
  }
}
</script> 