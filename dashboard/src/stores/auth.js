import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signInWithPopup,
  signInWithRedirect,
  getRedirectResult,
  signOut,
  onAuthStateChanged
} from 'firebase/auth'
import { auth, googleProvider } from '@/firebase/config'
import { toast } from 'vue3-toastify'
import AnalyticsService from '@/services/analytics'
import ApiService from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(true)
  const userProfile = ref(null)
  const authInitialized = ref(false)
  const backendUser = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const sessionId = ref(localStorage.getItem('session_id') || null)
  const showAccessDenied = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => userProfile.value?.is_admin || userProfile.value?.is_staff)

  // Persist tokens to localStorage
  const persistTokens = () => {
    if (accessToken.value) localStorage.setItem('access_token', accessToken.value)
    if (refreshToken.value) localStorage.setItem('refresh_token', refreshToken.value)
    if (sessionId.value) localStorage.setItem('session_id', sessionId.value)
  }

  // Navigate to intended destination or dashboard after successful auth
  const redirect_after_auth = async () => {
    try {
      const { default: router } = await import('@/router')
      const intended = sessionStorage.getItem('intendedDestination')
      if (intended && intended !== '/' && intended !== '/login') {
        sessionStorage.removeItem('intendedDestination')
        await router.push(intended)
      } else {
        await router.push('/dashboard')
      }
    } catch (_) {
      // no op if router not available
    }
  }

  // Clear tokens from localStorage
  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    sessionId.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('session_id')
    localStorage.removeItem('bottleplug_session')
  }

  // Initialize auth state listener
  const initAuth = async () => {
    if (authInitialized.value) return
    
    console.log('Initializing auth...')
    authInitialized.value = true
    loading.value = true
    
    // First, try to restore session from localStorage
    const existingSession = checkExistingSession()
    if (existingSession && accessToken.value) {
      console.log('Found existing session, attempting to restore...')
      try {
        const isValid = await checkTokenValidity()
        if (isValid) {
          console.log('Session tokens are valid, restoring user state...')
          // Create a minimal user object for immediate auth state
          user.value = {
            uid: existingSession.uid,
            email: existingSession.email,
            displayName: existingSession.email
          }
          
          try {
            await refreshProfile()
            console.log('Profile refreshed successfully')
          } catch (profileError) {
            console.warn('Could not refresh profile on restore:', profileError)
          }
          
          loading.value = false
          console.log('Session restored successfully for:', existingSession.email)
        } else {
          console.log('Session tokens are invalid, clearing...')
          clearUserData()
        }
      } catch (error) {
        console.warn('Session restoration failed:', error)
        clearUserData()
      }
    }
    
    try {
      // Set up Firebase auth state listener
      onAuthStateChanged(auth, async (firebaseUser) => {
        console.log('Firebase auth state changed:', firebaseUser ? firebaseUser.email : 'signed out')
        
        if (firebaseUser) {
          // Only update user state if it's different from what we have
          if (!user.value || user.value.uid !== firebaseUser.uid) {
            user.value = firebaseUser
            
            try {
              await verifyWithBackend(firebaseUser)
              console.log('Backend verification successful for:', firebaseUser.email)
              // Store session in localStorage for persistence
              localStorage.setItem('bottleplug_session', JSON.stringify({
                uid: firebaseUser.uid,
                email: firebaseUser.email,
                timestamp: Date.now()
              }))
              // If we arrived here from redirect flow, ensure we navigate now
              await redirect_after_auth()
            } catch (error) {
              console.error('Backend verification failed:', error)
              
              // Retry once after a short delay
              console.log('Retrying backend verification in 2 seconds...')
              setTimeout(async () => {
                try {
                  await verifyWithBackend(firebaseUser)
                  console.log('Backend verification successful on retry')
                  localStorage.setItem('bottleplug_session', JSON.stringify({
                    uid: firebaseUser.uid,
                    email: firebaseUser.email,
                    timestamp: Date.now()
                  }))
                } catch (retryError) {
                  console.error('Backend verification failed after retry:', retryError)
                  // Do not force logout here; keep Firebase session to avoid unintended sign-out on navigation
                  // Show a gentle warning to the user
                  try { toast.warn('Connected, but failed to sync with server. Some features may be limited.') } catch (_) {}
                }
              }, 2000)
            }
          }
        } else {
          // Only clear if we don't have a valid restored session
          if (!user.value || !existingSession) {
            clearUserData()
            console.log('User signed out')
          }
        }
        loading.value = false
      })
    } catch (error) {
      console.error('Firebase authentication error:', error)
      loading.value = false
    }
  }

  // Clear user data
  const clearUserData = () => {
    user.value = null
    userProfile.value = null
    backendUser.value = null
    clearTokens()
    showAccessDenied.value = false
  }

  // Verify Firebase token with backend
  const verifyWithBackend = async (firebaseUser) => {
    try {
      const idToken = await firebaseUser.getIdToken()
      
      const response = await fetch(`${ApiService.baseUrl}/auth/users/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_token: idToken,
          platform: 'web',
          device_id: navigator.userAgent,
          app_version: '1.0.0'
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      // Allow any authenticated user to access dashboard (development mode)
      // if (!data.user.is_staff && !data.user.is_admin) {
      //   console.error('User does not have dashboard access permissions')
      //   toast.error('Access denied. Staff permissions required.')
      //   showAccessDenied.value = true
      //   throw new Error('Access denied')
      // }
      
      // Store backend session data
      backendUser.value = data.user
      accessToken.value = data.access_token
      refreshToken.value = data.refresh_token
      sessionId.value = data.session_id
      persistTokens()
      
      // Update user profile with backend data
      userProfile.value = {
        id: data.user.id,
        uid: firebaseUser.uid,
        email: data.user.email,
        displayName: `${data.user.first_name} ${data.user.last_name}`.trim(),
        first_name: data.user.first_name,
        last_name: data.user.last_name,
        phone_number: data.user.phone_number,
        profile_image: data.user.profile_image,
        address: data.user.address,
        latitude: data.user.latitude,
        longitude: data.user.longitude,
        is_verified: data.user.is_verified,
        user_type: data.user.user_type,
        wallet_balance: data.user.wallet_balance,
        is_staff: data.user.is_staff,
        is_admin: data.user.is_admin,
        is_worker: data.user.is_worker,
        current_status: data.user.current_status,
        total_deliveries: data.user.total_deliveries,
        is_available: data.user.is_available,
        rating: data.user.rating,
        saved_addresses: data.user.saved_addresses,
        default_payment_method: data.user.default_payment_method,
        created_at: data.user.created_at,
        updated_at: data.user.updated_at
      }
      
      console.log('Backend user profile loaded:', userProfile.value)
      
      if (data.is_new_user) {
        toast.success('Welcome! Your account has been created.')
      } else {
        toast.success('Successfully authenticated')
      }
      
    } catch (error) {
      console.error('Backend verification error:', error)
      throw error
    }
  }

  // Email/Password Sign In (Firebase-first approach)
  const signInWithEmail = async (email, password) => {
    loading.value = true
    try {
      // Always use Firebase authentication
      const result = await signInWithEmailAndPassword(auth, email, password)
      AnalyticsService.trackLogin('email')
      
      // Immediately verify with backend to acquire access/refresh tokens
      await verifyWithBackend(result.user)
      // Set user immediately so router guard passes without waiting for onAuthStateChanged
      user.value = result.user
      // Persist minimal session snapshot
      localStorage.setItem('bottleplug_session', JSON.stringify({
        uid: result.user.uid,
        email: result.user.email,
        timestamp: Date.now()
      }))
      await redirect_after_auth()
      return { user: result.user, success: true }
    } catch (error) {
      console.error('Firebase sign in error:', error)
      
      // If user doesn't exist in Firebase, help them create an account
      if (error.code === 'auth/user-not-found') {
        try {
          console.log('User not found in Firebase, checking backend...')
          // Check if user exists in backend
          const backendUser = await checkUserExistsInBackend(email)
          if (backendUser) {
            toast.error('Account found but not set up for dashboard access. Please contact administrator to enable Firebase authentication.')
            throw new Error('Firebase account setup required')
          } else {
            toast.error('No account found with this email address. Please check your email or sign up for a new account.')
            throw error
          }
        } catch (checkError) {
          console.error('Error checking backend user:', checkError)
          throw error
        }
      }
      
      // Fallback: allow backend-only test login if Firebase sign-in fails for common credential errors
      if (['auth/invalid-credential', 'auth/wrong-password', 'auth/user-not-found'].includes(error.code)) {
        try {
          const res = await fetch(`${ApiService.baseUrl}/auth/users/test-login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
          })
          if (res.ok) {
            const data = await res.json()
            backendUser.value = data.user
            accessToken.value = data.access_token
            refreshToken.value = data.refresh_token
            persistTokens()
            user.value = { uid: 'backend-only', email }
            localStorage.setItem('bottleplug_session', JSON.stringify({ uid: 'backend-only', email, backend_only: true, timestamp: Date.now() }))
            try { toast.success('Signed in') } catch (_) {}
            await redirect_after_auth()
            return { user: user.value, success: true }
          }
        } catch (fallbackErr) {
          console.warn('Backend test-login fallback failed:', fallbackErr)
        }
      }
      let errorMessage = 'Sign in failed. Please try again.'
      try { toast.error(errorMessage) } catch (_) {}
      throw error
    } finally {
      loading.value = false
    }
  }

  // Check if user exists in backend
  const checkUserExistsInBackend = async (email) => {
    try {
      const response = await fetch(`${ApiService.baseUrl}/auth/users/check_exists/?email=${encodeURIComponent(email)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        return data.exists ? data : null
      }
      return null
    } catch (error) {
      console.error('Error checking user existence:', error)
      return null
    }
  }


  // Google Sign In
  const signInWithGoogle = async () => {
    loading.value = true
    try {
      let result = null
      try {
        result = await signInWithPopup(auth, googleProvider)
      } catch (popupErr) {
        console.warn('Google popup failed, falling back to redirect:', popupErr)
        // Start redirect flow and let onAuthStateChanged handle post-redirect
        await signInWithRedirect(auth, googleProvider)
        return { user: null, success: true }
      }
      AnalyticsService.trackLogin('google')

      // Immediately verify with backend to ensure tokens/session are set before router guard runs
      await verifyWithBackend(result.user)
      // Set user immediately so router guard passes without waiting for onAuthStateChanged
      user.value = result.user

      // Persist minimal session snapshot
      localStorage.setItem('bottleplug_session', JSON.stringify({
        uid: result.user.uid,
        email: result.user.email,
        timestamp: Date.now()
      }))
      await redirect_after_auth()

      return { user: result.user, success: true }
    } catch (error) {
      console.error('Google sign in error:', error)
      // If Firebase user exists, treat as success and let router guard proceed
      if (auth.currentUser) {
        return { user: auth.currentUser, success: true }
      }
      // Only toast for known auth errors
      const code = error && error.code
      if (code === 'auth/popup-closed-by-user' || code === 'auth/popup-blocked' || code === 'auth/cancelled-popup-request' || code === 'auth/network-request-failed' || code === 'auth/too-many-requests') {
        let errorMessage = 'Google sign in failed. Please try again.'
        switch (code) {
          case 'auth/popup-closed-by-user':
            errorMessage = 'Sign in was cancelled. Please try again.'
            break
          case 'auth/popup-blocked':
            errorMessage = 'Pop-up was blocked. Please allow pop-ups for this site.'
            break
          case 'auth/cancelled-popup-request':
            errorMessage = 'Sign in was cancelled. Please try again.'
            break
          case 'auth/network-request-failed':
            errorMessage = 'Network error. Please check your connection and try again.'
            break
          case 'auth/too-many-requests':
            errorMessage = 'Too many attempts. Please wait a moment and try again.'
            break
        }
        try { toast.error(errorMessage) } catch (_) {}
      }
      // Do not rethrow to avoid noisy errors on UI
      return { user: null, success: false }
    } finally {
      loading.value = false
    }
  }

  // Sign Up (for creating admin/staff accounts)
  const signUpWithEmail = async (email, password, userData) => {
    loading.value = true
    try {
      const result = await createUserWithEmailAndPassword(auth, email, password)
      
      // The backend will create the user profile when we call verifyWithBackend
      AnalyticsService.trackSignup('email')
      toast.success('Account created successfully!')
      
      return { user: result.user, success: true }
    } catch (error) {
      console.error('Sign up error:', error)
      
      let errorMessage = 'Account creation failed. Please try again.'
      
      switch (error.code) {
        case 'auth/email-already-in-use':
          errorMessage = 'An account with this email already exists.'
          break
        case 'auth/invalid-email':
          errorMessage = 'Please enter a valid email address.'
          break
        case 'auth/weak-password':
          errorMessage = 'Password should be at least 6 characters long.'
          break
      }
      
      toast.error(errorMessage)
      throw error
    } finally {
      loading.value = false
    }
  }

  // Sign Out
  const logout = async () => {
    loading.value = true
    try {
      // Sign out from backend
      if (accessToken.value) {
        try {
          await fetch(`${ApiService.baseUrl}/auth/users/logout/`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${accessToken.value}`,
              'Content-Type': 'application/json',
            },
          })
        } catch (error) {
          console.warn('Backend logout failed:', error)
        }
      }
      
      // Sign out from Firebase
      await signOut(auth)
      
      // Clear all data
      clearUserData()
      
      AnalyticsService.trackLogout()
      toast.success('Signed out successfully')
    } catch (error) {
      console.error('Sign out error:', error)
      // Even if logout fails, clear local data
      clearUserData()
      toast.error('Sign out completed with errors')
    } finally {
      loading.value = false
    }
  }

  // Update user profile
  const updateProfile = async (profileData) => {
    try {
      if (!accessToken.value) {
        throw new Error('No access token available')
      }

      const response = await fetch(`${ApiService.baseUrl}/auth/users/update_profile/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${accessToken.value}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const updatedUser = await response.json()
      
      // Update local user profile
      userProfile.value = { ...userProfile.value, ...updatedUser }
      backendUser.value = { ...backendUser.value, ...updatedUser }
      
      toast.success('Profile updated successfully')
      return updatedUser
    } catch (error) {
      console.error('Profile update error:', error)
      toast.error('Failed to update profile')
      throw error
    }
  }

  // Get fresh user profile from backend
  const refreshProfile = async () => {
    try {
      if (!accessToken.value) {
        throw new Error('No access token available')
      }

      const response = await fetch(`${ApiService.baseUrl}/auth/users/profile/`, {
        headers: {
          'Authorization': `Bearer ${accessToken.value}`,
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const userData = await response.json()
      
      // Update user profile
      userProfile.value = { ...userProfile.value, ...userData }
      backendUser.value = { ...backendUser.value, ...userData }
      
      return userData
    } catch (error) {
      console.error('Profile refresh error:', error)
      throw error
    }
  }

  // Check if tokens are valid and refresh if needed
  const checkTokenValidity = async () => {
    if (!accessToken.value) return false

    try {
      const response = await fetch(`${ApiService.baseUrl}/auth/users/profile/`, {
        headers: {
          'Authorization': `Bearer ${accessToken.value}`,
        },
      })

      return response.ok
    } catch (error) {
      console.error('Token validation error:', error)
      return false
    }
  }

  // Check for existing session in localStorage and restore user state
  const checkExistingSession = () => {
    const session = localStorage.getItem('bottleplug_session')
    if (!session) return false

    try {
      const sessionData = JSON.parse(session)
      const now = Date.now()
      const sessionAge = now - sessionData.timestamp
      
      // Session expires after 24 hours
      if (sessionAge > 24 * 60 * 60 * 1000) {
        localStorage.removeItem('bottleplug_session')
        clearTokens()
        return false
      }
      
      return sessionData
    } catch (error) {
      localStorage.removeItem('bottleplug_session')
      clearTokens()
      return false
    }
  }

  // Restore user session from stored tokens and session data
  const restoreUserSession = async () => {
    const existingSession = checkExistingSession()
    if (!existingSession) return false

    // Check if we have valid tokens
    if (!accessToken.value) return false

    try {
      // Validate token with backend
      const isValid = await checkTokenValidity()
      if (!isValid) {
        clearUserData()
        return false
      }

      // Restore user state from session
      if (existingSession.backend_only) {
        // Backend-only session
        user.value = {
          uid: existingSession.uid,
          email: existingSession.email,
          displayName: existingSession.displayName || existingSession.email
        }
      } else {
        // Firebase session
        user.value = {
          uid: existingSession.uid,
          email: existingSession.email
        }
      }

      // Try to refresh user profile from backend
      try {
        await refreshProfile()
      } catch (error) {
        console.warn('Could not refresh profile:', error)
      }

      console.log('Session restored for:', existingSession.email)
      return true
    } catch (error) {
      console.error('Session restoration failed:', error)
      clearUserData()
      return false
    }
  }

  return {
    // State
    user,
    loading,
    userProfile,
    backendUser,
    accessToken,
    refreshToken,
    sessionId,
    showAccessDenied,

    // Computed
    isAuthenticated,
    isAdmin,

    // Actions
    initAuth,
    signInWithEmail,
    signInWithGoogle,
    signUpWithEmail,
    logout,
    updateProfile,
    refreshProfile,
    checkTokenValidity,
    checkExistingSession,
    restoreUserSession,
    clearUserData,
    persistTokens,
    clearTokens
  }
})
