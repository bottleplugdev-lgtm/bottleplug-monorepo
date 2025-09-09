<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-secondary-800">Settings</h1>
      <p class="text-secondary-600">Manage your account and business preferences</p>
    </div>

    <!-- Settings Navigation -->
    <div class="flex space-x-1 bg-secondary-100 p-1 rounded-lg">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors',
          activeTab === tab.id
            ? 'bg-white text-primary-700 shadow-sm'
            : 'text-secondary-600 hover:text-secondary-900'
        ]"
      >
        <component :is="tab.icon" class="h-4 w-4 mr-2 inline" />
        {{ tab.name }}
      </button>
    </div>

    <!-- Profile Settings -->
    <div v-if="activeTab === 'profile'" class="space-y-6">
      <div class="card p-4">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">Profile Information</h3>
        <div class="flex items-center gap-4 mb-4">
          <img
            :src="profileImagePreview || buildMediaUrl(authStore.backendUser?.profile_image)"
            alt="Profile"
            class="h-16 w-16 rounded-full object-cover bg-secondary-100"
          />
          <div class="flex items-center gap-2">
            <input type="file" accept="image/*" @change="onProfileImageSelected" />
            <button type="button" class="btn btn-outline" @click="uploadProfileImageAction" :disabled="loading || !profileImageFile">
              Upload Image
            </button>
          </div>
        </div>
        <form @submit.prevent="updateProfile" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-secondary-700">First Name</label>
              <input
                v-model="profileForm.firstName"
                type="text"
                required
                class="input mt-1"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-secondary-700">Last Name</label>
              <input
                v-model="profileForm.lastName"
                type="text"
                required
                class="input mt-1"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700">Email</label>
            <input
              v-model="profileForm.email"
              type="email"
              required
              class="input mt-1"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700">Phone</label>
            <input
              v-model="profileForm.phone"
              type="tel"
              class="input mt-1"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700">Address</label>
            <textarea
              v-model="profileForm.address"
              rows="3"
              class="input mt-1"
              placeholder="Your address..."
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700">Bio</label>
            <textarea
              v-model="profileForm.bio"
              rows="3"
              class="input mt-1"
              placeholder="Tell us about yourself..."
            ></textarea>
          </div>

          <div class="flex justify-end">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <RefreshCw v-if="loading" class="h-4 w-4 animate-spin mr-2" />
              Update Profile
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Business Settings -->
    <div v-if="activeTab === 'business'" class="space-y-6">
      <div class="card p-4">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">Business Information</h3>
        <form @submit.prevent="updateBusiness" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-secondary-700">Business Name</label>
            <input
              v-model="businessForm.name"
              type="text"
              required
              class="input mt-1"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700">Business Type</label>
            <select v-model="businessForm.type" required class="input mt-1">
              <option value="">Select business type</option>
              <option value="retail">Retail Store</option>
              <option value="wholesale">Wholesale</option>
              <option value="online">Online Store</option>
              <option value="restaurant">Restaurant</option>
              <option value="bar">Bar</option>
              <option value="distributor">Distributor</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700">Address</label>
            <textarea
              v-model="businessForm.address"
              rows="3"
              class="input mt-1"
              placeholder="Business address..."
            ></textarea>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-secondary-700">City</label>
              <input
                v-model="businessForm.city"
                type="text"
                class="input mt-1"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-secondary-700">State</label>
              <input
                v-model="businessForm.state"
                type="text"
                class="input mt-1"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-secondary-700">ZIP Code</label>
              <input
                v-model="businessForm.zipCode"
                type="text"
                class="input mt-1"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700">Tax ID</label>
            <input
              v-model="businessForm.taxId"
              type="text"
              class="input mt-1"
              placeholder="EIN or Tax ID"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700">Business License</label>
            <input
              v-model="businessForm.license"
              type="text"
              class="input mt-1"
              placeholder="Business license number"
            />
          </div>

          <div class="flex justify-end">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <RefreshCw v-if="loading" class="h-4 w-4 animate-spin mr-2" />
              Update Business
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Preferences -->
    <div v-if="activeTab === 'preferences'" class="space-y-6">
      <div class="card p-4">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">Display Preferences</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-secondary-800">Email Notifications</p>
              <p class="text-sm text-secondary-600">Receive email alerts for orders and updates</p>
            </div>
            <button
              @click="preferences.emailNotifications = !preferences.emailNotifications"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                preferences.emailNotifications ? 'bg-primary-600' : 'bg-secondary-200'
              ]"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  preferences.emailNotifications ? 'translate-x-6' : 'translate-x-1'
                ]"
              ></span>
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-secondary-800">SMS Notifications</p>
              <p class="text-sm text-secondary-600">Receive SMS alerts for urgent updates</p>
            </div>
            <button
              @click="preferences.smsNotifications = !preferences.smsNotifications"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                preferences.smsNotifications ? 'bg-primary-600' : 'bg-secondary-200'
              ]"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  preferences.smsNotifications ? 'translate-x-6' : 'translate-x-1'
                ]"
              ></span>
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-secondary-800">Low Stock Alerts</p>
              <p class="text-sm text-secondary-600">Get notified when products are running low</p>
            </div>
            <button
              @click="preferences.lowStockAlerts = !preferences.lowStockAlerts"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                preferences.lowStockAlerts ? 'bg-primary-600' : 'bg-secondary-200'
              ]"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  preferences.lowStockAlerts ? 'translate-x-6' : 'translate-x-1'
                ]"
              ></span>
            </button>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">Currency & Units</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-secondary-700">Currency</label>
            <select v-model="preferences.currency" class="input mt-1">
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
              <option value="CAD">CAD (C$)</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-secondary-700">Date Format</label>
            <select v-model="preferences.dateFormat" class="input mt-1">
              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-secondary-700">Time Zone</label>
            <select v-model="preferences.timezone" class="input mt-1">
              <option value="UTC-8">Pacific Time (UTC-8)</option>
              <option value="UTC-7">Mountain Time (UTC-7)</option>
              <option value="UTC-6">Central Time (UTC-6)</option>
              <option value="UTC-5">Eastern Time (UTC-5)</option>
              <option value="UTC+0">UTC</option>
              <option value="UTC+1">Central European Time (UTC+1)</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-secondary-700">Language</label>
            <select v-model="preferences.language" class="input mt-1">
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Security -->
    <div v-if="activeTab === 'security'" class="space-y-6">
      <div class="card p-4">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">Change Password</h3>
        <form @submit.prevent="changePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-secondary-700">Current Password</label>
            <input
              v-model="passwordForm.currentPassword"
              type="password"
              required
              class="input mt-1"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700">New Password</label>
            <input
              v-model="passwordForm.newPassword"
              type="password"
              required
              class="input mt-1"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700">Confirm New Password</label>
            <input
              v-model="passwordForm.confirmPassword"
              type="password"
              required
              class="input mt-1"
            />
          </div>

          <div class="flex justify-end">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <RefreshCw v-if="loading" class="h-4 w-4 animate-spin mr-2" />
              Change Password
            </button>
          </div>
        </form>
      </div>

      

      <div class="card p-4">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">Active Sessions</h3>
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 3" :key="i" class="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
            <div class="flex items-center space-x-3">
              <div class="h-8 w-8 bg-secondary-200 rounded-lg animate-pulse"></div>
              <div>
                <div class="h-4 bg-secondary-200 rounded w-32 animate-pulse"></div>
                <div class="h-3 bg-secondary-200 rounded w-24 mt-1 animate-pulse"></div>
              </div>
            </div>
            <div class="h-6 bg-secondary-200 rounded w-16 animate-pulse"></div>
          </div>
        </div>
        <div v-else class="space-y-3">
          <div v-for="session in pagedSessions" :key="session.id" class="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
            <div class="flex items-center space-x-3">
              <div class="h-8 w-8 bg-primary-100 rounded-lg flex items-center justify-center">
                <Monitor class="h-4 w-4 text-primary-600" />
              </div>
              <div>
                <p class="text-sm font-medium text-secondary-800">{{ session.device }}</p>
                <p class="text-xs text-secondary-600">{{ session.location }} • {{ session.lastActive }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <span v-if="session.current" class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                Current
              </span>
              <button
                v-if="!session.current"
                @click="revokeSession(session.id)"
                class="text-red-600 hover:text-red-800 text-sm"
              >
                Revoke
              </button>
            </div>
          </div>
          <div class="flex items-center justify-between pt-2">
            <button class="btn btn-sm btn-outline" :disabled="sessionsPage===1" @click="sessionsPage--">Previous</button>
            <span class="text-sm text-secondary-600">Page {{ sessionsPage }} of {{ sessionsTotalPages }}</span>
            <button class="btn btn-sm btn-outline" :disabled="sessionsPage===sessionsTotalPages" @click="sessionsPage++">Next</button>
          </div>
          <div class="flex items-center justify-end gap-2 pt-2">
            <button class="btn btn-sm btn-danger" @click="revokeAllSessions">Revoke All Sessions</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Billing -->
    <div v-if="activeTab === 'billing'" class="space-y-6">
      <div class="card p-4">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">Billing History</h3>
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 3" :key="i" class="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
            <div>
              <div class="h-4 bg-secondary-200 rounded w-32 animate-pulse"></div>
              <div class="h-3 bg-secondary-200 rounded w-20 mt-1 animate-pulse"></div>
            </div>
            <div class="flex items-center space-x-3">
              <div class="h-4 bg-secondary-200 rounded w-16 animate-pulse"></div>
              <div class="h-4 bg-secondary-200 rounded w-20 animate-pulse"></div>
            </div>
          </div>
        </div>
        <div v-else class="space-y-3">
          <div v-for="invoice in billingHistory" :key="invoice.id" class="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
            <div>
              <p class="text-sm font-medium text-secondary-800">{{ invoice.description }}</p>
              <p class="text-xs text-secondary-600">{{ invoice.date }}</p>
            </div>
            <div class="flex items-center space-x-3">
              <span class="text-sm font-medium text-secondary-800">UGX {{ invoice.amount }}</span>
              <button class="text-primary-600 hover:text-primary-800 text-sm">
                Download
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { toast } from 'vue3-toastify'
import { 
  User, 
  Building, 
  Settings, 
  Shield, 
  CreditCard, 
  Plus, 
  Monitor,
  RefreshCw
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import {
  getMyProfile,
  patchMyProfile,
  getMyPreferences,
  updateMyPreferences,
  getMyBusiness,
  updateMyBusiness,
  changeMyPassword,
  listMySessions,
  revokeMySession,
  revokeAllMySessions,
  getMyBilling,
  uploadProfileImage
} from '@/services/api'

// State
const loading = ref(false)
const activeTab = ref('profile')
const authStore = useAuthStore()
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const BACKEND_ORIGIN = API_BASE_URL.replace(/\/api\/v1\/?$/, '')
const buildMediaUrl = (path) => {
  if (!path) return ''
  if (typeof path !== 'string') return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (path.startsWith('/')) return `${BACKEND_ORIGIN}${path}`
  return `${BACKEND_ORIGIN}/${path}`
}

const tabs = [
  { id: 'profile', name: 'Profile', icon: User },
  { id: 'business', name: 'Business', icon: Building },
  { id: 'preferences', name: 'Preferences', icon: Settings },
  { id: 'security', name: 'Security', icon: Shield },
  { id: 'billing', name: 'Billing', icon: CreditCard }
]

const profileForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  address: '',
  bio: ''
})

const profileImageFile = ref(null)
const profileImagePreview = ref('')

const businessForm = ref({
  name: '',
  type: '',
  address: '',
  city: '',
  state: '',
  zipCode: '',
  taxId: '',
  license: ''
})

const preferences = ref({
  darkMode: false,
  emailNotifications: true,
  smsNotifications: false,
  lowStockAlerts: true,
  currency: 'USD',
  dateFormat: 'MM/DD/YYYY',
  timezone: 'UTC-5',
  language: 'en',
  twoFactorAuth: false
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const activeSessions = ref([])
const billingHistory = ref([])
const billingInfo = ref({})
const sessionsPage = ref(1)
const sessionsPageSize = ref(5)
const pagedSessions = computed(() => {
  const start = (sessionsPage.value - 1) * sessionsPageSize.value
  return activeSessions.value.slice(start, start + sessionsPageSize.value)
})
const sessionsTotalPages = computed(() => Math.max(1, Math.ceil(activeSessions.value.length / sessionsPageSize.value)))

// Methods
const loadUserData = async () => {
  try {
    const me = await getMyProfile()
    profileForm.value = {
      firstName: me.first_name || '',
      lastName: me.last_name || '',
      email: me.email || '',
      phone: me.phone_number || '',
      address: me.address || '',
      bio: ''
    }
    // ensure backend_user on store has latest image/url
    authStore.backendUser = { ...authStore.backendUser, ...me }
  } catch (_) {}
  try {
    const businessResp = await getMyBusiness()
    const b = businessResp.business || {}
    businessForm.value = {
      name: b.name || '',
      type: b.type || '',
      address: b.address || '',
      city: b.city || '',
      state: b.state || '',
      zipCode: b.zip_code || '',
      taxId: b.tax_id || '',
      license: b.license || ''
    }
  } catch (_) {}
  try {
    const prefsResp = await getMyPreferences()
    const p = prefsResp.preferences || {}
    preferences.value = {
      darkMode: !!p.darkMode,
      emailNotifications: p.emailNotifications !== false,
      smsNotifications: !!p.smsNotifications,
      lowStockAlerts: p.lowStockAlerts !== false,
      currency: p.currency || 'USD',
      dateFormat: p.dateFormat || 'MM/DD/YYYY',
      timezone: p.timezone || 'UTC-5',
      language: p.language || 'en',
      twoFactorAuth: !!p.twoFactorAuth
    }
  } catch (_) {}
  try {
    const billing = await getMyBilling()
    billingInfo.value = {
      planName: billing.current_plan?.plan_name,
      planDescription: billing.current_plan?.plan_description
    }
    billingHistory.value = billing.billing_history || []
  } catch (_) {}
  try {
    const sessions = await listMySessions()
    activeSessions.value = (sessions.results || []).map(s => ({
      id: s.id,
      device: s.device_info?.platform || 'web',
      location: s.ip_address || 'Unknown',
      lastActive: new Date(s.last_activity).toLocaleString(),
      current: s.is_active
    }))
  } catch (_) {}
}

const updateProfile = async () => {
  loading.value = true
  try {
    const payload = {
      first_name: profileForm.value.firstName,
      last_name: profileForm.value.lastName,
      phone_number: profileForm.value.phone,
      address: profileForm.value.address
    }
    await patchMyProfile(payload)
    toast.success('Profile updated')
  } catch (error) {
    console.error('Failed to update profile:', error)
    toast.error('Failed to update profile')
  } finally {
    loading.value = false
  }
}

const updateBusiness = async () => {
  loading.value = true
  try {
    const payload = {
      name: businessForm.value.name,
      type: businessForm.value.type,
      address: businessForm.value.address,
      city: businessForm.value.city,
      state: businessForm.value.state,
      zip_code: businessForm.value.zipCode,
      tax_id: businessForm.value.taxId,
      license: businessForm.value.license,
      phone: profileForm.value.phone
    }
    await updateMyBusiness(payload)
    toast.success('Business information updated')
  } catch (error) {
    console.error('Failed to update business:', error)
    toast.error('Failed to update business information')
  } finally {
    loading.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    toast.error('New passwords do not match')
    return
  }
  
  loading.value = true
  try {
    await changeMyPassword({
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword
    })
    toast.success('Password changed successfully')
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    console.error('Failed to change password:', error)
    toast.error('Failed to change password')
  } finally {
    loading.value = false
  }
}

const revokeSession = async (sessionId) => {
  try {
    await revokeMySession(sessionId)
    activeSessions.value = activeSessions.value.filter(s => s.id !== sessionId)
    toast.success('Session revoked successfully')
  } catch (error) {
    console.error('Failed to revoke session:', error)
    toast.error('Failed to revoke session')
  }
}

const revokeAllSessions = async () => {
  try {
    await revokeAllMySessions()
    activeSessions.value = []
    sessionsPage.value = 1
    toast.success('All sessions revoked')
  } catch (error) {
    console.error('Failed to revoke all sessions:', error)
    toast.error('Failed to revoke all sessions')
  }
}

const onProfileImageSelected = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  profileImageFile.value = file
  const reader = new FileReader()
  reader.onload = () => { profileImagePreview.value = reader.result }
  reader.readAsDataURL(file)
}

const uploadProfileImageAction = async () => {
  if (!profileImageFile.value) return
  loading.value = true
  try {
    const updated = await uploadProfileImage(profileImageFile.value)
    toast.success('Profile image updated')
    // reflect new image if backend returns url
    if (updated?.profile_image) {
      authStore.backendUser = { ...authStore.backendUser, profile_image: updated.profile_image }
    }
  } catch (error) {
    console.error('Profile image upload failed:', error)
    toast.error('Failed to upload profile image')
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadUserData()
})
</script> 