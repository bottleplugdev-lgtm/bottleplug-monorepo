<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-800">Customers</h1>
        <p class="text-secondary-600">Manage customer relationships and track purchase history</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="refreshCustomers"
          class="btn btn-outline"
          :disabled="loading"
        >
          <RefreshCw v-if="loading" class="h-4 w-4 animate-spin" />
          <RefreshCw v-else class="h-4 w-4" />
          Refresh
        </button>
        <button
          @click="showAddCustomerModal = true"
          class="btn btn-primary"
        >
          <Plus class="h-4 w-4" />
          Add Customer
        </button>
      </div>
    </div>

    <!-- Customer Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Users class="h-8 w-8 text-primary-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Total Customers</p>
            <p class="text-2xl font-bold text-secondary-800">{{ customerSummary.total }}</p>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <UserCheck class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Active Customers</p>
            <p class="text-2xl font-bold text-green-600">{{ customerSummary.active }}</p>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <UserPlus class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">New This Month</p>
            <p class="text-2xl font-bold text-blue-600">{{ customerSummary.newThisMonth }}</p>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <DollarSign class="h-8 w-8 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Avg. Order Value</p>
            <p class="text-2xl font-bold text-secondary-800">UGX {{ customerSummary.avgOrderValue }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search customers..."
            class="w-full px-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @input="handleSearch"
          />
        </div>
        <div class="flex gap-2">
          <select
            v-model="statusFilter"
            class="px-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @change="handleFilter"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="vip">VIP</option>
          </select>
          <select
            v-model="typeFilter"
            class="px-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @change="handleFilter"
          >
            <option value="">All Types</option>
            <option value="customer">Customer</option>
            <option value="wholesale">Wholesale</option>
            <option value="restaurant">Restaurant</option>
            <option value="bar">Bar</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Customers Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-secondary-200">
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Customer</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Contact</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Type</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Status</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Orders</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Total Spent</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading" class="border-b border-secondary-100">
              <td colspan="7" class="py-8 px-4 text-center">
                <div class="flex items-center justify-center">
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                  <span class="ml-2 text-secondary-600">Loading customers...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="filteredCustomers.length === 0" class="border-b border-secondary-100">
              <td colspan="7" class="py-8 px-4 text-center text-secondary-600">
                No customers found
              </td>
            </tr>
            <tr
              v-for="customer in filteredCustomers"
              :key="customer.id"
              class="border-b border-secondary-100 hover:bg-secondary-50"
            >
              <td class="py-4 px-4">
                <div class="flex items-center space-x-3">
                  <div class="h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <User class="h-5 w-5 text-primary-600" />
                  </div>
                  <div>
                    <div class="font-medium text-secondary-800">
                      {{ customer.first_name }} {{ customer.last_name }}
                    </div>
                    <div class="text-sm text-secondary-600">{{ customer.user_type || 'Customer' }}</div>
                  </div>
                </div>
              </td>
              <td class="py-4 px-4">
                <div class="space-y-1">
                  <div class="text-sm text-secondary-800">{{ customer.email }}</div>
                  <div class="text-sm text-secondary-600">{{ customer.phone_number || 'N/A' }}</div>
                </div>
              </td>
              <td class="py-4 px-4">
                <span class="px-2 py-1 bg-secondary-100 text-secondary-700 rounded-full text-sm">
                  {{ customer.user_type || 'Customer' }}
                </span>
              </td>
              <td class="py-4 px-4">
                <span :class="[
                  'px-2 py-1 rounded-full text-sm font-medium',
                  getStatusClass(customer.is_verified, customer.is_available)
                ]">
                  {{ getStatusText(customer.is_verified, customer.is_available) }}
                </span>
              </td>
              <td class="py-4 px-4">
                <span class="font-medium text-secondary-800">{{ customer.total_deliveries || 0 }}</span>
              </td>
              <td class="py-4 px-4">
                <span class="font-medium text-secondary-800">UGX {{ customer.wallet_balance || '0.00' }}</span>
              </td>
              <td class="py-4 px-4">
                <div class="flex items-center space-x-2">
                  <button
                    @click="viewCustomer(customer)"
                    class="p-2 text-secondary-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="View Details"
                  >
                    <Eye class="h-4 w-4" />
                  </button>
                  <button
                    @click="editCustomer(customer)"
                    class="p-2 text-secondary-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Edit Customer"
                  >
                    <Edit class="h-4 w-4" />
                  </button>
                  <button
                    @click="viewHistory(customer)"
                    class="p-2 text-secondary-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                    title="View History"
                  >
                    <History class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && filteredCustomers.length > 0" class="flex items-center justify-between">
      <p class="text-sm text-secondary-600">
        Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalCustomers) }} of {{ totalCustomers }} customers
      </p>
      <div class="flex items-center space-x-2">
        <button
          @click="previousPage"
          :disabled="currentPage === 1"
          class="btn btn-sm btn-outline"
        >
          Previous
        </button>
        <span class="px-3 py-1 text-sm text-secondary-600">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="btn btn-sm btn-outline"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Add/Edit Customer Modal -->
    <div
      v-if="showAddCustomerModal || editingCustomer"
      class="fixed inset-0 z-50 overflow-y-auto"
    >
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="saveCustomer">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                {{ editingCustomer ? 'Edit Customer' : 'Add New Customer' }}
              </h3>
              
              <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">First Name</label>
                    <input
                      v-model="customerForm.firstName"
                      type="text"
                      required
                      class="input mt-1"
                      placeholder="John"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Last Name</label>
                    <input
                      v-model="customerForm.lastName"
                      type="text"
                      required
                      class="input mt-1"
                      placeholder="Doe"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    v-model="customerForm.email"
                    type="email"
                    required
                    class="input mt-1"
                    placeholder="john@example.com"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Phone</label>
                  <input
                    v-model="customerForm.phone"
                    type="tel"
                    class="input mt-1"
                    placeholder="+1234567890"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Customer Type</label>
                  <select v-model="customerForm.type" required class="input mt-1">
                    <option value="">Select type</option>
                    <option value="customer">Customer</option>
                    <option value="wholesale">Wholesale</option>
                    <option value="restaurant">Restaurant</option>
                    <option value="bar">Bar</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Address</label>
                  <input
                    v-model="customerForm.address"
                    type="text"
                    class="input mt-1"
                    placeholder="123 Main St"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Status</label>
                  <select v-model="customerForm.status" required class="input mt-1">
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="vip">VIP</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Notes</label>
                  <textarea
                    v-model="customerForm.notes"
                    rows="3"
                    class="input mt-1"
                    placeholder="Customer notes..."
                  ></textarea>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button type="submit" class="btn btn-primary sm:ml-3 sm:w-auto">
                {{ editingCustomer ? 'Update Customer' : 'Add Customer' }}
              </button>
              <button
                type="button"
                @click="closeModal"
                class="btn btn-outline sm:w-auto"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- View Customer Modal -->
  <div v-if="showViewModal" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Customer Details</h3>
          <div v-if="selectedCustomer" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-secondary-600">Name</p>
                <p class="font-medium text-secondary-800">{{ selectedCustomer.first_name }} {{ selectedCustomer.last_name }}</p>
              </div>
              <div>
                <p class="text-sm text-secondary-600">Email</p>
                <p class="font-medium text-secondary-800">{{ selectedCustomer.email }}</p>
              </div>
              <div>
                <p class="text-sm text-secondary-600">Phone</p>
                <p class="font-medium text-secondary-800">{{ selectedCustomer.phone_number || 'N/A' }}</p>
              </div>
              <div>
                <p class="text-sm text-secondary-600">Type</p>
                <p class="font-medium text-secondary-800">{{ selectedCustomer.user_type || 'Customer' }}</p>
              </div>
            </div>
            <div>
              <p class="text-sm font-semibold text-secondary-700 mb-2">Recent Orders</p>
              <div class="divide-y divide-secondary-100 border border-secondary-100 rounded">
                <div v-for="o in recentOrders" :key="o.id" class="px-3 py-2 flex items-center justify-between">
                  <div class="text-secondary-700">#{{ o.id }} · {{ new Date(o.created_at).toLocaleDateString() }}</div>
                  <div class="font-medium">UGX {{ (o.total_amount || 0).toLocaleString() }}</div>
                </div>
                <div v-if="!recentOrders || recentOrders.length === 0" class="px-3 py-4 text-center text-secondary-500">No recent orders</div>
              </div>
            </div>
            <div>
              <p class="text-sm font-semibold text-secondary-700 mb-2">Recent Payments</p>
              <div class="divide-y divide-secondary-100 border border-secondary-100 rounded">
                <div v-for="r in recentReceipts" :key="r.id" class="px-3 py-2 flex items-center justify-between">
                  <div class="text-secondary-700">{{ r.payment_method || 'Payment' }} · {{ new Date(r.created_at).toLocaleDateString() }}</div>
                  <div class="font-medium">UGX {{ (r.amount || 0).toLocaleString() }}</div>
                </div>
                <div v-if="!recentReceipts || recentReceipts.length === 0" class="px-3 py-4 text-center text-secondary-500">No recent payments</div>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button type="button" class="btn btn-primary sm:ml-3 sm:w-auto" @click="closeViewModal">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- History Modal -->
  <div v-if="showHistoryModal" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Customer History</h3>
          <div v-if="selectedCustomer" class="space-y-4">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="card p-3"><p class="text-xs text-secondary-600">Orders</p><p class="text-xl font-bold text-secondary-800">{{ historyOrders.length }}</p></div>
              <div class="card p-3"><p class="text-xs text-secondary-600">Payments</p><p class="text-xl font-bold text-secondary-800">{{ historyReceipts.length }}</p></div>
              <div class="card p-3"><p class="text-xs text-secondary-600">Total Spent</p><p class="text-xl font-bold text-secondary-800">UGX {{ totalSpent.toLocaleString() }}</p></div>
              <div class="card p-3"><p class="text-xs text-secondary-600">Total Paid</p><p class="text-xl font-bold text-secondary-800">UGX {{ totalPaid.toLocaleString() }}</p></div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="card p-3">
                <p class="text-sm font-semibold text-secondary-700 mb-2">Orders</p>
                <div class="max-h-64 overflow-auto divide-y divide-secondary-100">
                  <div v-for="o in historyOrders" :key="o.id" class="py-2 flex items-center justify-between">
                    <div class="text-secondary-700">#{{ o.id }} · {{ new Date(o.created_at).toLocaleDateString() }}</div>
                    <div class="font-medium">UGX {{ (o.total_amount || 0).toLocaleString() }}</div>
                  </div>
                  <div v-if="!historyOrders || historyOrders.length === 0" class="py-4 text-center text-secondary-500">No orders</div>
                </div>
              </div>
              <div class="card p-3">
                <p class="text-sm font-semibold text-secondary-700 mb-2">Payments</p>
                <div class="max-h-64 overflow-auto divide-y divide-secondary-100">
                  <div v-for="r in historyReceipts" :key="r.id" class="py-2 flex items-center justify-between">
                    <div class="text-secondary-700">{{ r.payment_method || 'Payment' }} · {{ new Date(r.created_at).toLocaleDateString() }}</div>
                    <div class="font-medium">UGX {{ (r.amount || 0).toLocaleString() }}</div>
                  </div>
                  <div v-if="!historyReceipts || historyReceipts.length === 0" class="py-4 text-center text-secondary-500">No payments</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button type="button" class="btn btn-primary sm:ml-3 sm:w-auto" @click="closeHistoryModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import { 
  Plus, 
  Users, 
  UserCheck, 
  UserPlus, 
  DollarSign, 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Eye, 
  Edit, 
  History,
  RefreshCw
} from 'lucide-vue-next'
import {
  getUsers,
  getOrders,
  getPaymentReceipts,
  updateMyBusiness // placeholder for future customer update endpoint
} from '@/services/api'

// State
const loading = ref(false)
const customers = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const showAddCustomerModal = ref(false)
const editingCustomer = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const totalCustomers = ref(0)

// Dialog state
const showViewModal = ref(false)
const showHistoryModal = ref(false)
const selectedCustomer = ref(null)
const recentOrders = ref([])
const recentReceipts = ref([])
const historyOrders = ref([])
const historyReceipts = ref([])

const totalSpent = computed(() => historyOrders.value.reduce((s, o) => s + parseFloat(o.total_amount || 0), 0))
const totalPaid = computed(() => historyReceipts.value.reduce((s, r) => s + parseFloat(r.amount || 0), 0))

const customerForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  type: '',
  address: '',
  status: 'active',
  notes: ''
})

// Computed
const filteredCustomers = computed(() => {
  let filtered = customers.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(customer =>
      `${customer.first_name} ${customer.last_name}`.toLowerCase().includes(query) ||
      customer.email?.toLowerCase().includes(query) ||
      customer.phone_number?.includes(query)
    )
  }

  // Status filter
  if (statusFilter.value) {
    filtered = filtered.filter(customer => {
      const status = getStatusText(customer.is_verified, customer.is_available)
      return status.toLowerCase() === statusFilter.value
    })
  }

  // Type filter
  if (typeFilter.value) {
    filtered = filtered.filter(customer => customer.user_type === typeFilter.value)
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(totalCustomers.value / pageSize.value))

const customerSummary = computed(() => {
  const total = customers.value.length
  const active = customers.value.filter(c => c.is_verified && c.is_available).length
  const newThisMonth = customers.value.filter(c => {
    const createdAt = new Date(c.created_at)
    const now = new Date()
    return createdAt.getMonth() === now.getMonth() && createdAt.getFullYear() === now.getFullYear()
  }).length
  const avgOrderValue = customers.value.length > 0 
    ? (customers.value.reduce((sum, c) => sum + parseFloat(c.wallet_balance || 0), 0) / customers.value.length).toFixed(2)
    : '0.00'

  return { total, active, newThisMonth, avgOrderValue }
})

// Methods
const fetchCustomers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await getUsers(params)
    customers.value = response.results || response
    totalCustomers.value = response.count || response.length
    
    console.log('Customers loaded:', customers.value)
  } catch (error) {
    console.error('Failed to fetch customers:', error)
    toast.error('Failed to load customers')
  } finally {
    loading.value = false
  }
}

const refreshCustomers = async () => {
  await fetchCustomers()
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const getStatusClass = (isVerified, isAvailable) => {
  if (isVerified && isAvailable) return 'bg-green-100 text-green-800'
  if (isVerified && !isAvailable) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

const getStatusText = (isVerified, isAvailable) => {
  if (isVerified && isAvailable) return 'Active'
  if (isVerified && !isAvailable) return 'Inactive'
  return 'Pending'
}

const viewCustomer = async (customer) => {
  try {
    loading.value = true
    selectedCustomer.value = customer
    const orders = await getOrders({ customer_id: customer.id, page_size: 5 })
    const receipts = await getPaymentReceipts({ customer_id: customer.id, page_size: 5 })
    const allOrders = orders.results || orders || []
    const allReceipts = receipts.results || receipts || []
    // Strictly attach to this user
    recentOrders.value = allOrders.filter(o => ((o.customer && (o.customer.id || o.customer)) === customer.id) || (o.customer_email && o.customer_email === customer.email))
    recentReceipts.value = allReceipts.filter(r => ((r.customer && (r.customer.id || r.customer)) === customer.id) || (r.customer_email && r.customer_email === customer.email))
    showViewModal.value = true
  } catch (e) {
    console.error('Failed to load customer details:', e)
    toast.error('Failed to load customer details')
  } finally {
    loading.value = false
  }
}

const editCustomer = (customer) => {
  editingCustomer.value = customer
  customerForm.value = {
    firstName: customer.first_name || '',
    lastName: customer.last_name || '',
    email: customer.email || '',
    phone: customer.phone_number || '',
    type: customer.user_type || '',
    address: customer.address || '',
    status: customer.is_verified ? 'active' : 'inactive',
    notes: ''
  }
}

const viewHistory = async (customer) => {
  try {
    loading.value = true
    selectedCustomer.value = customer
    const orders = await getOrders({ customer_id: customer.id, page_size: 50 })
    const receipts = await getPaymentReceipts({ customer_id: customer.id, page_size: 50 })
    const allOrders = orders.results || orders || []
    const allReceipts = receipts.results || receipts || []
    // Strictly attach to this user
    historyOrders.value = allOrders.filter(o => ((o.customer && (o.customer.id || o.customer)) === customer.id) || (o.customer_email && o.customer_email === customer.email))
    historyReceipts.value = allReceipts.filter(r => ((r.customer && (r.customer.id || r.customer)) === customer.id) || (r.customer_email && r.customer_email === customer.email))
    showHistoryModal.value = true
  } catch (e) {
    console.error('Failed to load history:', e)
    toast.error('Failed to load history')
  } finally {
    loading.value = false
  }
}

const closeViewModal = () => {
  showViewModal.value = false
  selectedCustomer.value = null
  recentOrders.value = []
  recentReceipts.value = []
}

const closeHistoryModal = () => {
  showHistoryModal.value = false
  selectedCustomer.value = null
  historyOrders.value = []
  historyReceipts.value = []
}

const saveCustomer = async () => {
  // Placeholder: we currently lack a customer create/update endpoint
  // For now, just close the modal and show a toast
  try {
    toast.info('Customer save will be connected to backend in a later step')
  } finally {
    closeModal()
  }
}

const closeModal = () => {
  showAddCustomerModal.value = false
  editingCustomer.value = null
  customerForm.value = {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    type: '',
    address: '',
    status: 'active',
    notes: ''
  }
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchCustomers()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchCustomers()
  }
}

// Lifecycle
onMounted(async () => {
  await fetchCustomers()
})
</script> 