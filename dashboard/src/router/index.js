import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AnalyticsService from '@/services/analytics'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Overview',
        component: () => import('@/views/dashboard/Overview.vue')
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/dashboard/Products.vue')
      },

      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/dashboard/Orders.vue')
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/dashboard/Customers.vue')
      },
      {
        path: 'events',
        name: 'Events',
        component: () => import('@/views/dashboard/Events.vue')
      },
      {
        path: 'expenses',
        name: 'Expenses',
        component: () => import('@/views/dashboard/Expenses.vue')
      },
      {
        path: 'finance',
        name: 'FinanceLegacy',
        component: () => import('@/views/dashboard/Expenses.vue')
      },
      
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/dashboard/Settings.vue')
      },
      {
        path: 'payments',
        name: 'Payments',
        component: () => import('@/views/dashboard/Payments.vue')
      },
      {
        path: 'order-receipts',
        name: 'OrderReceipts',
        component: () => import('@/views/dashboard/OrderReceipts.vue')
      },
      {
        path: 'invoices',
        name: 'Invoices',
        component: () => import('@/views/dashboard/Invoices.vue')
      },
      {
        path: 'receipts',
        name: 'Receipts',
        component: () => import('@/views/dashboard/Receipts.vue')
      },
      {
        path: 'delivery-request',
        name: 'DeliveryRequest',
        component: () => import('@/views/dashboard/DeliveryRequest.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  try {
    // Initialize auth once
    if (!authStore.authInitialized) {
      await authStore.initAuth()
    }

    // Wait briefly for auth to finish; if timeout, do not hard-redirect
    if (authStore.loading) {
      await new Promise(resolve => {
        const unwatch = authStore.$subscribe(() => {
          if (!authStore.loading) {
            unwatch()
            resolve()
          }
        })
        setTimeout(() => {
          unwatch()
          resolve()
        }, 8000)
      })
    }

    // Require active Firebase user OR restored session, and valid backend token
    const hasToken = !!localStorage.getItem('access_token')
    const hasSession = !!localStorage.getItem('bottleplug_session')
    const isAuth = (authStore.isAuthenticated || hasSession) && hasToken

    // Track page view
    AnalyticsService.trackPageView(to.name || to.path)

    // If still loading, allow navigation to continue; guards will re-evaluate once loading flips
    if (authStore.loading) {
      return next()
    }

    if (to.meta.requiresAuth && !isAuth) {
      // Store intended destination for after login
      if (to.path !== '/' && to.path !== '/login') {
        sessionStorage.setItem('intendedDestination', to.fullPath)
      }
      return next('/')
    }

    if (to.meta.requiresGuest && isAuth) {
      const intendedDestination = sessionStorage.getItem('intendedDestination')
      if (intendedDestination && intendedDestination !== '/' && intendedDestination !== '/login') {
        sessionStorage.removeItem('intendedDestination')
        return next(intendedDestination)
      }
      return next('/dashboard')
    }

    return next()
  } catch (error) {
    // On guard errors, force sign-in for protected routes
    if (to.meta.requiresAuth) {
      sessionStorage.setItem('intendedDestination', to.fullPath)
      return next('/')
    }
    return next()
  }
})

export default router 