<template>
  <div class="min-h-screen bg-gradient-to-br from-secondary-50 to-secondary-100">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 w-64 bg-gradient-to-b from-secondary-500 to-secondary-900 shadow-2xl transform transition-transform duration-300 ease-in-out border-r border-secondary-600',
        sidebarOpen ? 'translate-x-0' : 'lg:translate-x-0 -translate-x-full'
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center justify-between h-20 px-6 border-b border-secondary-600 bg-secondary-600/50">
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-primary-500 rounded-xl shadow-lg">
            <img src="@/assets/images/logos/picture.png" alt="BottlePlug Logo" class="h-8 w-8 object-contain rounded-lg" />
          </div>
          <div>
            <span class="text-xl font-bold text-cream-500">BottlePlug</span>
            <p class="text-xs text-secondary-200"></p>
          </div>
        </div>
        <button
          @click="sidebarOpen = false"
          class="lg:hidden p-2 rounded-lg text-secondary-200 hover:text-cream-500 hover:bg-secondary-600 transition-colors"
        >
          <X class="h-5 w-5" />
        </button>
      </div>

      <!-- Navigation -->
      <nav class="mt-8 px-4">
        <div class="space-y-2">
          <router-link
            v-for="item in navigationItems"
            :key="item.name"
            :to="item.path"
            :class="[
              'flex items-center gap-3 px-4 py-3 rounded-xl text-secondary-200 transition-all duration-200 hover:bg-secondary-600/50 hover:text-cream-500 group',
              $route.path === item.path ? 'bg-primary-500 text-cream-500 shadow-lg' : ''
            ]"
          >
            <div :class="[
              'p-2 rounded-lg transition-colors',
              $route.path === item.path ? 'bg-cream-500/20' : 'group-hover:bg-secondary-600'
            ]">
              <component :is="item.icon" class="h-5 w-5" />
            </div>
            <span class="font-medium">{{ item.name }}</span>
          </router-link>
        </div>
      </nav>

      <!-- User Profile -->
      <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-secondary-600 bg-secondary-600/30">
        <div class="flex items-center space-x-3">
          <div class="h-12 w-12 bg-primary-500 rounded-full flex items-center justify-center shadow-lg">
            <User class="h-6 w-6 text-cream-500" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-cream-500 truncate">
              {{ authStore.userProfile?.displayName || authStore.backendUser?.first_name || 'User' }}
            </p>
            <p class="text-xs text-secondary-200 truncate">
              {{ authStore.userProfile?.email || authStore.backendUser?.email || authStore.user?.email }}
            </p>
            <p v-if="authStore.backendUser?.user_type" class="text-xs text-secondary-300 truncate">
              {{ authStore.backendUser.user_type }}
            </p>
          </div>
          <button
            @click="handleLogout"
            class="p-2 rounded-lg text-secondary-200 hover:text-cream-500 hover:bg-secondary-600 transition-colors"
            title="Sign out"
          >
            <LogOut class="h-5 w-5" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="lg:pl-64">
      <!-- Header -->
      <header class="bg-white shadow-sm border-b border-secondary-200">
        <div class="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
          <div class="flex items-center">
            <button
              @click="sidebarOpen = true"
              class="lg:hidden p-3 rounded-xl text-secondary-600 hover:text-secondary-800 hover:bg-secondary-100 transition-colors"
            >
              <Menu class="h-6 w-6" />
            </button>
            <h1 class="ml-4 lg:ml-0 text-xl font-bold text-secondary-800">
              {{ currentPageTitle }}
            </h1>
          </div>

          <!-- Header Actions -->
          <div class="flex items-center space-x-4">
            <!-- Notifications -->
            <button class="p-2 rounded-md text-secondary-400 hover:text-secondary-600 relative">
              <Bell class="h-5 w-5" />
              <span class="absolute top-1 right-1 h-2 w-2 bg-accent-500 rounded-full"></span>
            </button>

            <!-- Search -->
            <div class="relative">
              <input
                type="text"
                placeholder="Search..."
                class="w-64 pl-10 pr-4 py-2 text-sm border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white"
              />
              <Search class="absolute left-3 top-2.5 h-4 w-4 text-secondary-400" />
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="p-4 sm:p-6 lg:p-8">
        <router-view />
      </main>
    </div>

    <!-- Mobile Overlay -->
    <div
      v-if="sidebarOpen"
      @click="sidebarOpen = false"
      class="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
    ></div>
    
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  X,
  User,
  LogOut,
  Menu,
  Bell,
  Search,
  Home,
  Package,
  ShoppingCart,
  Users,
  Minus,
  Settings,
  Calendar,
  CreditCard,
  Wallet,
  Smartphone
} from 'lucide-vue-next'

const route = useRoute()
const authStore = useAuthStore()
const sidebarOpen = ref(false)

const navigationItems = [
  { name: 'Overview', path: '/dashboard', icon: Home },
  { name: 'Products', path: '/dashboard/products', icon: Package },
  { name: 'Orders', path: '/dashboard/orders', icon: ShoppingCart },
  { name: 'Customers', path: '/dashboard/customers', icon: Users },
  { name: 'Events', path: '/dashboard/events', icon: Calendar },
  { name: 'Expenses', path: '/dashboard/expenses', icon: Minus },
  { name: 'Payments', path: '/dashboard/payments', icon: CreditCard },
  { name: 'Settings', path: '/dashboard/settings', icon: Settings }
]

const currentPageTitle = computed(() => {
  const currentItem = navigationItems.find(item => item.path === route.path)
  return currentItem ? currentItem.name : 'Dashboard'
})

const handleLogout = async () => {
  try {
    console.log('Attempting logout...')
    await authStore.logout()
    console.log('Logout successful, redirecting to login...')
    // Redirect to login page after logout
    window.location.href = '/'
  } catch (error) {
    console.error('Logout error:', error)
    // Even if logout fails, clear session and redirect
    localStorage.removeItem('bottleplug_session')
    console.log('Forced redirect to login...')
    window.location.href = '/'
  }
}
</script>
