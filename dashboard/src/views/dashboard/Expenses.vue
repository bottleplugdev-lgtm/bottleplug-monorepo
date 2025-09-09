<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-800">Expenses</h1>
        <p class="text-secondary-600">Track expenses and financial outflows</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="refreshExpenses"
          class="btn btn-outline"
          :disabled="loading"
        >
          <RefreshCw v-if="loading" class="h-4 w-4 animate-spin" />
          <RefreshCw v-else class="h-4 w-4" />
          Refresh
        </button>
        <button @click="showAddExpenseModal = true" class="btn btn-warning">
          <Minus class="h-4 w-4" />
          Add Expense
        </button>
      </div>
    </div>

    <!-- Expenses Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Minus class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Total Expenses</p>
            <p class="text-2xl font-bold text-red-600">UGX {{ formatUGX(financialSummary.totalExpenses) }}</p>
            <p class="text-sm text-red-600 flex items-center mt-1">
              <TrendingDown class="h-4 w-4 mr-1" />
              +{{ financialSummary.expenseGrowth }}%
            </p>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <BarChart3 class="h-8 w-8 text-primary-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Monthly Spend</p>
            <p class="text-2xl font-bold text-primary-600">UGX {{ formatUGX(financialSummary.monthlySpend) }}</p>
            <p class="text-sm text-primary-600 flex items-center mt-1">
              <TrendingUp class="h-4 w-4 mr-1" />
              +{{ financialSummary.expenseGrowth }}%
            </p>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Percent class="h-8 w-8 text-secondary-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Avg Expense</p>
            <p class="text-2xl font-bold text-secondary-800">UGX {{ formatUGX(financialSummary.avgExpense) }}</p>
            <p class="text-sm text-green-600 flex items-center mt-1">
              <TrendingUp class="h-4 w-4 mr-1" />
              +{{ financialSummary.marginGrowth }}%
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts removed for expenses-only view -->

    <!-- Recent Transactions -->
    <div class="card p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-secondary-800">Recent Expenses</h3>
        <div class="flex space-x-2">
          <button
            @click="transactionTypeFilter = 'expense'"
            :class="[
              'px-3 py-1 text-sm rounded-md',
              transactionTypeFilter === 'expense' ? 'bg-red-100 text-red-700' : 'bg-secondary-100 text-secondary-700'
            ]"
          >
            Expenses Only
          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-secondary-200">
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Date</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Description</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Category</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Amount</th>
              <th class="text-right py-3 px-4 font-semibold text-secondary-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading" class="border-b border-secondary-100">
              <td colspan="5" class="py-8 px-4 text-center">
                <div class="flex items-center justify-center">
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                  <span class="ml-2 text-secondary-600">Loading transactions...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="filteredTransactions.length === 0" class="border-b border-secondary-100">
              <td colspan="5" class="py-8 px-4 text-center text-secondary-600">
                No expenses found
              </td>
            </tr>
            <tr
              v-for="transaction in filteredTransactions"
              :key="transaction.id"
              class="border-b border-secondary-100 hover:bg-secondary-50"
            >
              <td class="py-4 px-4 text-sm text-secondary-800">
                {{ formatDate(transaction.date || transaction.created_at) }}
              </td>
              <td class="py-4 px-4">
                <div class="text-sm font-medium text-secondary-800">{{ transaction.description || transaction.name }}</div>
                <div class="text-sm text-secondary-600">{{ transaction.reference || transaction.id }}</div>
              </td>
              <td class="py-4 px-4">
                <span class="px-2 py-1 text-xs font-medium bg-secondary-100 text-secondary-700 rounded-full">
                  {{ transaction.category || 'General' }}
                </span>
              </td>
              <td class="py-4 px-4 text-sm font-medium text-red-600">
                -UGX {{ Number(transaction.amount || 0).toFixed(2) }}
              </td>
              <td class="py-4 px-4 text-right space-x-2">
                <button class="btn btn-xs btn-outline" @click="openEditExpense(transaction)">
                  <Edit class="h-3 w-3" />
                  Edit
                </button>
                <button class="btn btn-xs btn-danger" @click="deleteExpenseAction(transaction)">
                  <Trash2 class="h-3 w-3" />
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && filteredTransactions.length > 0" class="flex items-center justify-between">
      <p class="text-sm text-secondary-600">
        Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalTransactions) }} of {{ totalTransactions }} expenses
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

    <!-- Add Expense Modal -->
    <div v-if="showAddExpenseModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="addExpense">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Add Expense</h3>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Description</label>
                  <input
                    v-model="expenseForm.description"
                    type="text"
                    required
                    class="input mt-1"
                    placeholder="Expense description"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Amount</label>
                  <input
                    v-model="expenseForm.amount"
                    type="number"
                    step="0.01"
                    required
                    class="input mt-1"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Category</label>
                  <select v-model="expenseForm.category" required class="input mt-1">
                    <option value="">Select category</option>
                    <option value="inventory">Inventory</option>
                    <option value="utilities">Utilities</option>
                    <option value="rent">Rent</option>
                    <option value="wages">Wages</option>
                    <option value="marketing">Marketing</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Date</label>
                  <input
                    v-model="expenseForm.date"
                    type="date"
                    required
                    class="input mt-1"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Reference</label>
                  <input
                    v-model="expenseForm.reference"
                    type="text"
                    class="input mt-1"
                    placeholder="Receipt number, invoice, etc."
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Notes</label>
                  <textarea
                    v-model="expenseForm.notes"
                    rows="3"
                    class="input mt-1"
                    placeholder="Additional notes..."
                  ></textarea>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button type="submit" class="btn btn-warning sm:ml-3 sm:w-auto">
                Add Expense
              </button>
              <button
                type="button"
                @click="showAddExpenseModal = false"
                class="btn btn-outline sm:w-auto"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit Expense Modal -->
    <div v-if="showEditExpenseModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="updateExpenseAction">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Edit Expense</h3>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Description</label>
                  <input
                    v-model="editExpenseForm.description"
                    type="text"
                    required
                    class="input mt-1"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Amount</label>
                  <input
                    v-model="editExpenseForm.amount"
                    type="number"
                    step="0.01"
                    required
                    class="input mt-1"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Category</label>
                  <select v-model="editExpenseForm.category" required class="input mt-1">
                    <option value="inventory">Inventory</option>
                    <option value="utilities">Utilities</option>
                    <option value="rent">Rent</option>
                    <option value="wages">Wages</option>
                    <option value="marketing">Marketing</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Date</label>
                  <input
                    v-model="editExpenseForm.date"
                    type="date"
                    required
                    class="input mt-1"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Reference</label>
                  <input
                    v-model="editExpenseForm.reference"
                    type="text"
                    class="input mt-1"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Notes</label>
                  <textarea
                    v-model="editExpenseForm.notes"
                    rows="3"
                    class="input mt-1"
                  ></textarea>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button type="submit" class="btn btn-primary sm:ml-3 sm:w-auto">
                Save Changes
              </button>
              <button
                type="button"
                @click="showEditExpenseModal = false"
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import { 
  Plus, 
  Minus, 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Percent,
  RefreshCw,
  Edit,
  Trash2
} from 'lucide-vue-next'
import {
  getExpenses,
  createExpense,
  getExpenseSummary,
  getExpenseCategories,
  getExpenseStats,
  updateExpense,
  deleteExpense
} from '@/services/api'

// State
const loading = ref(false)
const transactions = ref([])
const summary = ref({ total_expenses: 0, count: 0 })
const transactionTypeFilter = ref('expense')
const showAddExpenseModal = ref(false)
const showEditExpenseModal = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalTransactions = ref(0)

const expenseForm = ref({
  description: '',
  amount: '',
  category: '',
  date: new Date().toISOString().split('T')[0],
  reference: '',
  notes: ''
})

const editingExpenseId = ref(null)
const editExpenseForm = ref({
  description: '',
  amount: '',
  category: '',
  date: new Date().toISOString().split('T')[0],
  reference: '',
  notes: ''
})

// Computed
const filteredTransactions = computed(() => {
  const filtered = transactions.value
  return filtered.sort((a, b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at))
})

const totalPages = computed(() => Math.ceil(totalTransactions.value / pageSize.value))

const financialSummary = computed(() => {
  const totalExpenses = Number(summary.value.total_expenses || 0)
  const monthlySpend = totalExpenses
  const avgExpense = transactions.value.length ? Math.round(totalExpenses / transactions.value.length) : 0
  const expenseGrowth = 0
  const marginGrowth = 0
  return { totalExpenses, monthlySpend, avgExpense, expenseGrowth, marginGrowth }
})

// Methods
const fetchTransactions = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    const response = await getExpenses(params)
    transactions.value = response.results || response
    totalTransactions.value = response.count || response.length || 0
    const sum = await getExpenseSummary()
    summary.value = sum
    
    console.log('Transactions loaded:', transactions.value)
  } catch (error) {
    console.error('Failed to fetch transactions:', error)
    toast.error('Failed to load expenses')
  } finally {
    loading.value = false
  }
}

const refreshExpenses = async () => {
  await fetchTransactions()
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatUGX = (value) => {
  const n = Number(value || 0)
  try {
    return n.toLocaleString('en-UG')
  } catch (e) {
    return String(n)
  }
}

const addExpense = async () => {
  try {
    const payload = { ...expenseForm.value }
    payload.amount = Number(payload.amount)
    if (!payload.category) payload.category = 'other'
    await createExpense(payload)
    toast.success('Expense added')
    showAddExpenseModal.value = false
    await fetchTransactions()
    // Reset form
    expenseForm.value = {
      description: '',
      amount: '',
      category: '',
      date: new Date().toISOString().split('T')[0],
      reference: '',
      notes: ''
    }
  } catch (e) {
    console.error('Failed to create expense:', e)
    toast.error('Failed to add expense')
  }
}

const openEditExpense = (expense) => {
  editingExpenseId.value = expense.id
  editExpenseForm.value = {
    description: expense.description || '',
    amount: String(expense.amount ?? ''),
    category: expense.category || 'other',
    date: (expense.date || new Date().toISOString().split('T')[0]).slice(0, 10),
    reference: expense.reference || '',
    notes: expense.notes || ''
  }
  showEditExpenseModal.value = true
}

const updateExpenseAction = async () => {
  try {
    const payload = { ...editExpenseForm.value, amount: Number(editExpenseForm.value.amount) }
    await updateExpense(editingExpenseId.value, payload)
    toast.success('Expense updated')
    showEditExpenseModal.value = false
    await fetchTransactions()
  } catch (e) {
    console.error('Failed to update expense:', e)
    toast.error('Failed to update expense')
  }
}

const deleteExpenseAction = async (expense) => {
  try {
    if (!confirm('Delete this expense?')) return
    await deleteExpense(expense.id)
    toast.success('Expense deleted')
    await fetchTransactions()
  } catch (e) {
    console.error('Failed to delete expense:', e)
    toast.error('Failed to delete expense')
  }
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchTransactions()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchTransactions()
  }
}

// Lifecycle
onMounted(async () => {
  await fetchTransactions()
})
</script>

