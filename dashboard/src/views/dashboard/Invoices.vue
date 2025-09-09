<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Invoices</h1>
        <p class="mt-1 text-sm text-gray-500">Manage customer invoices and payment tracking</p>
      </div>
      <div class="mt-4 sm:mt-0">
        <button
          @click="showNewInvoiceModal = true"
          class="btn btn-primary"
        >
          <Plus class="h-4 w-4 mr-2" />
          New Invoice
        </button>
      </div>
    </div>

    <!-- Invoice Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Invoices</p>
            <p class="text-2xl font-bold text-gray-900">{{ invoiceSummary.total }}</p>
          </div>
          <div class="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <FileText class="h-6 w-6 text-primary-600" />
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Draft</p>
            <p class="text-2xl font-bold text-gray-600">{{ invoiceSummary.draft }}</p>
          </div>
          <div class="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
            <FileText class="h-6 w-6 text-gray-600" />
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Sent</p>
            <p class="text-2xl font-bold text-blue-600">{{ invoiceSummary.sent }}</p>
          </div>
          <div class="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <Send class="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Overdue</p>
            <p class="text-2xl font-bold text-red-600">{{ invoiceSummary.overdue }}</p>
          </div>
          <div class="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
            <AlertTriangle class="h-6 w-6 text-red-600" />
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Cancelled</p>
            <p class="text-2xl font-bold text-gray-500">{{ invoiceSummary.cancelled }}</p>
          </div>
          <div class="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
            <XCircle class="h-6 w-6 text-gray-500" />
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Invoice Status Pie Chart -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Invoice Status Distribution</h3>
        <div class="h-80">
          <canvas ref="pieChartRef"></canvas>
        </div>
      </div>

      <!-- Monthly Revenue Line Chart -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Monthly Revenue Trend</h3>
        <div class="h-80">
          <canvas ref="lineChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
        <button 
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="text-sm text-gray-500 hover:text-gray-700 flex items-center"
        >
          <X class="h-4 w-4 mr-1" />
          Clear Filters
        </button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Invoice ID, customer..."
            class="input"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="filters.status" class="input">
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Customer</label>
          <select v-model="filters.customer" class="input">
            <option value="">All Customers</option>
            <option v-for="customer in customers" :key="customer.id" :value="customer.id">
              {{ customer.full_name || customer.name || customer.email }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <div class="flex space-x-2">
            <select 
              v-model="filters.dateRange" 
              :class="[
                'px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                filters.dateRange ? 'border-primary-300 bg-primary-50' : 'border-secondary-200'
              ]"
              class="input flex-1"
            >
            <option value="">All Time</option>
            <option value="today">Today</option>
              <option value="yesterday">Yesterday</option>
              <option value="this_week">This Week (Mon-Sun)</option>
              <option value="week">Last 7 Days</option>
              <option value="this_month">This Month</option>
              <option value="month">Last 30 Days</option>
              <option value="this_year">This Year</option>
              <option value="year">Last 365 Days</option>
          </select>
            <button
              @click="showDateRangeModal = true"
              class="px-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent hover:bg-secondary-50"
              title="Custom Date Range"
            >
              <Calendar class="h-4 w-4" />
            </button>
            <button
              v-if="filters.dateRange || customStartDate || customEndDate"
              @click="clearDateFilters"
              class="px-4 py-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-50"
              title="Clear Date Filters"
            >
              <X class="h-4 w-4" />
            </button>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select v-model="filters.sortBy" class="input">
            <option value="date">Date</option>
            <option value="amount">Amount</option>
            <option value="status">Status</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Invoice Table -->
    <div class="card">
      <div class="p-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Invoice List</h3>
          <div class="mt-4 sm:mt-0">
            <div class="flex space-x-2">
              <button @click="downloadInvoice" class="btn btn-outline">
                <Download class="h-4 w-4 mr-2" /> Export
              </button>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex justify-center items-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span class="ml-2 text-gray-600">Loading invoices...</span>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredInvoices.length === 0" class="text-center py-8">
          <FileText class="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">No invoices found</h3>
          <p class="text-gray-500 mb-4">
            {{ loading ? 'Loading invoices...' : 'Get started by creating your first invoice.' }}
          </p>
          <div v-if="!loading && invoices.length === 0" class="text-sm text-gray-400 mb-4">
            Total invoices in database: {{ invoices.length }}
          </div>
          <button
            v-if="!loading"
            @click="showNewInvoiceModal = true"
            class="btn btn-primary"
          >
            <Plus class="h-4 w-4 mr-2" />
            Create First Invoice
          </button>
        </div>

        <!-- Invoice Table -->
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice Details
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Customer
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Items
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Due Date
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="invoice in filteredInvoices" :key="invoice.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">#{{ invoice.invoice_number }}</div>
                  <div class="text-sm text-gray-500">{{ invoice.id }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
                      <User class="h-4 w-4 text-gray-600" />
                    </div>
                    <div class="ml-3">
                      <div class="text-sm font-medium text-gray-900">{{ invoice.customer_name }}</div>
                      <div class="text-sm text-gray-500">{{ invoice.customer_email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ invoice.order?.items?.length || 0 }} items</div>
                  <div class="text-sm text-gray-500">
                    {{ invoice.order?.items?.map(item => item.product_name).join(', ') || 'No items' }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">UGX {{ formatAmount(invoice.total_amount) }}</div>
                  <div class="text-xs text-secondary-600">Paid: UGX {{ formatAmount(invoice.amount_paid) }}</div>
                  <div class="text-xs text-red-600">Outstanding: UGX {{ formatAmount(calculateInvoiceOutstanding(invoice)) }}</div>
                  <div class="text-xs text-secondary-600">Includes delivery: UGX {{ formatAmount(invoice.delivery_fee) }}</div>
                  <div class="text-xs text-blue-600">Balance: UGX {{ formatAmount(calculateInvoiceOutstanding(invoice)) }} of UGX {{ formatAmount(invoice.total_amount) }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusClass(invoice.status)}`">
                    {{ invoice.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div :class="getDueDateClass(invoice)">{{ new Date(invoice.due_date).toLocaleDateString() || 'N/A' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <div class="flex gap-3">
                    <button @click="viewInvoice(invoice)" class="p-2 rounded hover:bg-gray-100" title="View">
                      <Eye class="h-4 w-4" />
                    </button>
                    <button @click="editInvoice(invoice)" :disabled="invoice.status === 'paid'" :class="['p-2 rounded hover:bg-gray-100', invoice.status === 'paid' ? 'opacity-50 cursor-not-allowed' : '']" title="Edit">
                      <PenSquare class="h-4 w-4" />
                    </button>
                    <button @click="sendInvoiceAction(invoice)" class="p-2 rounded hover:bg-gray-100" title="Send to customer">
                      <Send class="h-4 w-4" />
                    </button>
                    <button @click="markPaid(invoice)" :disabled="invoice.status === 'paid'" :class="['p-2 rounded hover:bg-gray-100', invoice.status === 'paid' ? 'opacity-50 cursor-not-allowed' : '']" title="Mark as paid">
                      <CheckCircle class="h-4 w-4" />
                    </button>
                    <button @click="downloadInvoiceAsPDF(invoice)" class="p-2 rounded hover:bg-gray-100" title="Download PDF">
                      <Download class="h-4 w-4" />
                    </button>
                    <button @click="confirmDeleteInvoice(invoice)" :disabled="invoice.status === 'paid'" :class="['p-2 rounded hover:bg-red-50 text-red-600', invoice.status === 'paid' ? 'opacity-50 cursor-not-allowed' : '']" title="Delete">
                      <Trash2 class="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- New Invoice Modal -->
    <div v-if="showNewInvoiceModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" aria-hidden="true">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Create New Invoice</h3>
                
                <!-- Error Display -->
                <div v-if="invoiceCreationError" class="mb-4 p-4 bg-red-100 border-2 border-red-300 rounded-lg shadow-sm">
                  <div class="flex">
                    <div class="flex-shrink-0">
                      <svg class="h-6 w-6 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                      </svg>
                    </div>
                    <div class="ml-3">
                      <h3 class="text-sm font-semibold text-red-900">
                        ⚠️ Cannot Create Invoice
                      </h3>
                      <div class="mt-2 text-sm text-red-800">
                        <p class="font-medium">{{ invoiceCreationError }}</p>
                        <p class="mt-2 text-xs text-red-700 bg-red-50 p-2 rounded">
                          💡 Tip: Check the invoices list above to see existing invoices for this order.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <form @submit.prevent="createInvoiceAction" class="space-y-4">
                  <!-- Order Selection -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Order</label>
                    <select
                      v-model="invoiceForm.order"
                      required
                      class="input"
                      :disabled="isCheckingBalance"
                    >
                      <option value="">Select an order</option>
                      <option
                        v-for="order in orders"
                        :key="order.id"
                        :value="order.id"
                      >
                        #{{ order.order_number }} - {{ order.customer_name }} (UGX {{ formatAmount(order.total_amount) }})
                      </option>
                    </select>
                    
                    <!-- Payment Balance Information -->
                    <div v-if="isCheckingBalance" class="mt-2 text-sm text-blue-600">
                      <div class="flex items-center">
                        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                        Checking payment balance...
                      </div>
                    </div>
                    
                    <div v-else-if="balanceMessage" class="mt-2 p-3 rounded-lg text-sm" 
                         :class="{
                           'bg-red-50 text-red-700 border border-red-200': !canCreateInvoice,
                           'bg-blue-50 text-blue-700 border border-blue-200': canCreateInvoice && selectedOrderBalance?.is_partially_paid,
                           'bg-gray-50 text-gray-700 border border-gray-200': canCreateInvoice && !selectedOrderBalance?.is_partially_paid
                         }">
                      {{ balanceMessage }}
                    </div>
                    
                    <!-- Existing Invoice Message -->
                    <div v-if="existingInvoiceMessage" class="mt-2 p-3 rounded-lg text-sm font-medium" 
                         :class="{
                           'bg-red-50 text-red-700 border-2 border-red-300': !canCreateInvoiceDueToExisting,
                           'bg-yellow-50 text-yellow-700 border-2 border-yellow-300': canCreateInvoiceDueToExisting
                         }">
                      <div class="flex items-center">
                        <div class="flex-shrink-0 mr-2">
                          <svg v-if="!canCreateInvoiceDueToExisting" class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                          </svg>
                          <svg v-else class="h-5 w-5 text-yellow-500" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                          </svg>
                        </div>
                        <div>
                          <p class="font-semibold">
                            {{ !canCreateInvoiceDueToExisting ? '⚠️ Cannot Create Invoice' : 'ℹ️ Invoice Information' }}
                          </p>
                          <p class="mt-1">{{ existingInvoiceMessage }}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Payment Terms -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Payment Terms</label>
                    <select
                      v-model="invoiceForm.payment_terms"
                      @change="calculateDueDate"
                      class="input"
                    >
                      <option value="immediate">Immediate</option>
                      <option value="net_7">Net 7</option>
                      <option value="net_15">Net 15</option>
                      <option value="net_30">Net 30</option>
                      <option value="net_45">Net 45</option>
                      <option value="net_60">Net 60</option>
                    </select>
                  </div>

                  <!-- Invoice Date -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Invoice Date</label>
                    <input
                      v-model="invoiceForm.invoice_date"
                      type="date"
                      @change="calculateDueDate"
                      class="input"
                    />
                  </div>

                  <!-- Due Date -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                    <div class="flex space-x-2">
                      <input
                        v-model="invoiceForm.due_date"
                        type="date"
                        class="input flex-1"
                        :disabled="invoiceForm.payment_terms === 'immediate'"
                        :min="invoiceForm.invoice_date"
                      />
                      <button
                        v-if="invoiceForm.payment_terms !== 'immediate'"
                        @click="calculateDueDate"
                        type="button"
                        class="px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
                        title="Auto-calculate due date based on payment terms"
                      >
                        Auto
                      </button>
                    </div>
                    <p v-if="invoiceForm.payment_terms === 'immediate'" class="text-xs text-gray-500 mt-1">
                      Due date is automatically set for immediate payment
                    </p>
                    <p v-else class="text-xs text-gray-500 mt-1">
                      Click "Auto" to calculate due date based on payment terms, or manually select a date
                    </p>
                    <div v-if="invoiceForm.due_date && invoiceForm.payment_terms !== 'immediate'" class="text-xs text-green-600 mt-1">
                      Due date: {{ formatDate(invoiceForm.due_date) }}
                    </div>
                  </div>

                  <!-- Tax Rate -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Tax Rate (%)</label>
                    <input
                      v-model.number="invoiceForm.tax_rate"
                      type="number"
                      step="0.01"
                      min="0"
                      max="100"
                      class="input"
                    />
                  </div>

                  <!-- Discount Amount -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Discount Amount ($)</label>
                    <input
                      v-model.number="invoiceForm.discount_amount"
                      type="number"
                      step="0.01"
                      min="0"
                      class="input"
                    />
                  </div>

                  <!-- Notes -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                    <textarea
                      v-model="invoiceForm.notes"
                      rows="3"
                      class="input"
                      placeholder="Additional notes..."
                    ></textarea>
                  </div>

                  <!-- Terms and Conditions -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Terms and Conditions</label>
                    <textarea
                      v-model="invoiceForm.terms_and_conditions"
                      rows="3"
                      class="input"
                      placeholder="Terms and conditions..."
                    ></textarea>
                  </div>
                </form>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">

            
            <button
              type="submit"
              @click="createInvoiceAction"
              :disabled="!canCreateInvoice || !canCreateInvoiceDueToExisting || isCheckingBalance"
              class="btn"
              :class="{
                'btn-primary': canCreateInvoice && canCreateInvoiceDueToExisting,
                'btn-danger opacity-50 cursor-not-allowed': !canCreateInvoice || !canCreateInvoiceDueToExisting,
                'opacity-50 cursor-not-allowed': isCheckingBalance
              }"
              @mouseenter="console.log('Button state:', { canCreateInvoice: canCreateInvoice.value, canCreateInvoiceDueToExisting: canCreateInvoiceDueToExisting.value, isCheckingBalance: isCheckingBalance.value })"
            >
              <span v-if="isCheckingBalance">Checking Balance...</span>
              <span v-else-if="!canCreateInvoice" class="font-semibold">⚠️ Cannot Create Invoice</span>
              <span v-else-if="!canCreateInvoiceDueToExisting" class="font-semibold">⚠️ Cannot Create Invoice</span>
              <span v-else>Create Invoice</span>
            </button>
            <button
              type="button"
              @click="showNewInvoiceModal = false"
              class="btn btn-outline mr-3"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- View Invoice Modal -->
    <div v-if="showViewInvoiceModal && selectedInvoice" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" aria-hidden="true">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <div class="flex justify-between items-center mb-4">
                  <h3 class="text-lg leading-6 font-medium text-gray-900">
                    Invoice #{{ selectedInvoice.invoice_number }}
                  </h3>
                  <span :class="`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusClass(selectedInvoice.status)}`">
                    {{ selectedInvoice.status }}
                  </span>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- Invoice Details -->
                  <div class="space-y-4">
                    <div>
                      <h4 class="text-sm font-medium text-gray-700 mb-2">Invoice Information</h4>
                      <div class="space-y-2 text-sm">
                        <div class="flex justify-between">
                          <span class="text-gray-600">Invoice Number:</span>
                          <span class="font-medium">#{{ selectedInvoice.invoice_number }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-gray-600">Order ID:</span>
                          <span class="font-medium">{{ selectedInvoice.order?.id }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-gray-600">Created:</span>
                          <span class="font-medium">{{ formatDate(selectedInvoice.created_at) }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-gray-600">Due Date:</span>
                          <span class="font-medium" :class="getDueDateClass(selectedInvoice)">
                            {{ formatDate(selectedInvoice.due_date) }}
                          </span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-gray-600">Payment Terms:</span>
                          <span class="font-medium">{{ selectedInvoice.payment_terms }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- Customer Information -->
                    <div>
                      <h4 class="text-sm font-medium text-gray-700 mb-2">Customer Information</h4>
                      <div class="space-y-2 text-sm">
                        <div class="flex justify-between">
                          <span class="text-gray-600">Name:</span>
                          <span class="font-medium">{{ selectedInvoice.customer_name }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-gray-600">Email:</span>
                          <span class="font-medium">{{ selectedInvoice.customer_email }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-gray-600">Phone:</span>
                          <span class="font-medium">{{ selectedInvoice.customer_phone }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Financial Information -->
                  <div class="space-y-4">
                    <div>
                      <h4 class="text-sm font-medium text-gray-700 mb-2">Financial Summary</h4>
                      <div class="space-y-2 text-sm">
                        <div class="flex justify-between">
                          <span class="text-gray-600">Subtotal:</span>
                          <span class="font-medium">UGX {{ formatAmount(selectedInvoice.subtotal) }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-gray-600">Tax ({{ selectedInvoice.tax_rate }}%):</span>
                          <span class="font-medium">UGX {{ formatAmount(selectedInvoice.tax_amount) }}</span>
                        </div>
                        <div v-if="selectedInvoice.delivery_fee > 0" class="flex justify-between">
                          <span class="text-gray-600">Delivery Fee:</span>
                          <span class="font-medium">UGX {{ formatAmount(selectedInvoice.delivery_fee) }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-gray-600">Discount:</span>
                          <span class="font-medium">UGX {{ formatAmount(selectedInvoice.discount_amount) }}</span>
                        </div>
                        <div class="flex justify-between border-t pt-2">
                          <span class="text-gray-800 font-semibold">Total Amount:</span>
                          <span class="font-semibold text-lg">UGX {{ formatAmount(selectedInvoice.total_amount) }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-gray-600">Amount Paid:</span>
                          <span class="font-medium" :class="selectedInvoice.amount_paid > 0 ? 'text-green-600' : 'text-gray-600'">
                            UGX {{ formatAmount(selectedInvoice.amount_paid) }}
                          </span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-gray-600">Outstanding Amount:</span>
                          <span class="font-medium" :class="calculateInvoiceOutstanding(selectedInvoice) > 0 ? 'text-red-600' : 'text-green-600'">
                            UGX {{ formatAmount(calculateInvoiceOutstanding(selectedInvoice)) }}
                          </span>
                        </div>
                        <div v-if="calculateInvoiceOutstanding(selectedInvoice) > 0 && calculateInvoiceOutstanding(selectedInvoice) < selectedInvoice.total_amount" class="flex justify-between border-t pt-2">
                          <span class="text-gray-600 text-sm">Balance Summary:</span>
                          <span class="text-sm text-blue-600">
                            UGX {{ formatAmount(calculateInvoiceOutstanding(selectedInvoice)) }} of UGX {{ formatAmount(selectedInvoice.total_amount) }} remaining
                          </span>
                        </div>
                      </div>
                    </div>

                    <!-- Notes -->
                    <div v-if="selectedInvoice.notes">
                      <h4 class="text-sm font-medium text-gray-700 mb-2">Notes</h4>
                      <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ selectedInvoice.notes }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              @click="downloadInvoiceAsPDF(selectedInvoice)"
              class="btn btn-primary mr-3"
            >
              <Download class="h-4 w-4 mr-2" />
              Download PDF
            </button>
            <button
              type="button"
              @click="showViewInvoiceModal = false"
              class="btn btn-outline"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Invoice Modal -->
    <div v-if="showEditInvoiceModal && selectedInvoice" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" aria-hidden="true">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Edit Invoice #{{ selectedInvoice.invoice_number }}
                </h3>
                
                <div class="space-y-4">
                  <!-- Status -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <select v-model="selectedInvoice.status" class="input">
                      <option value="draft">Draft</option>
                      <option value="sent">Sent</option>
                      <option value="paid">Paid</option>
                      <option value="overdue">Overdue</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>

                  <!-- Payment Terms -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Payment Terms</label>
                    <select v-model="selectedInvoice.payment_terms" class="input">
                      <option value="immediate">Immediate</option>
                      <option value="net_7">Net 7</option>
                      <option value="net_15">Net 15</option>
                      <option value="net_30">Net 30</option>
                      <option value="net_45">Net 45</option>
                      <option value="net_60">Net 60</option>
                    </select>
                  </div>

                  <!-- Due Date -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                    <input
                      v-model="selectedInvoice.due_date"
                      type="date"
                      class="input"
                    />
                  </div>

                  <!-- Notes -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                    <textarea
                      v-model="selectedInvoice.notes"
                      rows="3"
                      class="input"
                      placeholder="Additional notes..."
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              @click="updateInvoiceAction"
              class="btn btn-primary mr-3"
            >
              Update Invoice
            </button>
            <button
              type="button"
              @click="showEditInvoiceModal = false"
              class="btn btn-outline"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirmModal && invoiceToDelete" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" aria-hidden="true">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                <Trash2 class="h-6 w-6 text-red-600" />
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                  Delete Invoice
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    Are you sure you want to delete invoice #{{ invoiceToDelete.invoice_number }}? 
                    This action cannot be undone.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              @click="deleteInvoiceAction"
              class="btn btn-danger mr-3"
            >
              Delete
            </button>
            <button
              type="button"
              @click="showDeleteConfirmModal = false; invoiceToDelete = null"
              class="btn btn-outline"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom Date Range Modal -->
    <div v-if="showDateRangeModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" aria-hidden="true">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Custom Date Range</h3>
                
                <div class="space-y-4">
                  <!-- Active filters indicator -->
                  <div v-if="filters.dateRange || customStartDate || customEndDate" class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p class="text-sm font-medium text-blue-800 mb-1">Active Filters:</p>
                    <div class="text-xs text-blue-600 space-y-1">
                      <p v-if="filters.dateRange">Quick Filter: {{ getFilterDisplayName(filters.dateRange) }}</p>
                      <p v-if="customStartDate && customEndDate">
                        Custom Range: {{ customStartDate }} to {{ customEndDate }}
                      </p>
                    </div>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                    <input 
                      v-model="customStartDate"
                      type="date"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                    <input 
                      v-model="customEndDate"
                      type="date"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div class="flex justify-end space-x-3 pt-4">
                    <button 
                      @click="showDateRangeModal = false"
                      class="px-4 py-2 text-gray-600 hover:text-gray-800"
                    >
                      Cancel
                    </button>
                    <button 
                      @click="applyCustomDateRange"
                      :disabled="!customStartDate || !customEndDate"
                      class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50"
                    >
                      Apply Filter
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { 
  Plus, 
  FileText, 
  Clock, 
  CheckCircle, 
  DollarSign,
  User,
  Eye, 
  PenSquare, 
  Trash2,
  Send,
  Download,
  X,
  Calendar,
  AlertTriangle,
  XCircle
} from 'lucide-vue-next'
import { toast } from 'vue3-toastify'
import { Chart, registerables } from 'chart.js'
import {
  getInvoices,
  getInvoice,
  createInvoice,
  updateInvoice,
  deleteInvoice,
  getMyInvoices,
  sendInvoice,
  applyPayment,
  markInvoicePaid,
  cancelInvoice,
  getInvoiceStats,
  getUsers,
  getProducts,
  getOrders,
  getOrderPaymentBalance,
  getPaymentTransactions,
  getPaymentTransactionsByOrderId,
  downloadInvoicePdf
} from '@/services/api'

Chart.register(...registerables)

// State
const showNewInvoiceModal = ref(false)
const pieChartRef = ref(null)
const lineChartRef = ref(null)
let pieChart = null
let lineChart = null

const customers = ref([])
const products = ref([])
const invoices = ref([])
const orders = ref([])
const loading = ref(false)

// Payment balance tracking
const selectedOrderBalance = ref(null)
const isCheckingBalance = ref(false)
const canCreateInvoice = ref(true)
const balanceMessage = ref('')

const filters = ref({
  search: '',
  status: '',
  customer: '',
  dateRange: '',
  sortBy: 'date'
})

// Custom date range variables
const showDateRangeModal = ref(false)
const customStartDate = ref('')
const customEndDate = ref('')

// Clear all filters
const clearFilters = () => {
  filters.value = {
    search: '',
    status: '',
    customer: '',
    dateRange: '',
    sortBy: 'date'
  }
  customStartDate.value = ''
  customEndDate.value = ''
}

// Check if any filters are active
const hasActiveFilters = computed(() => {
  return filters.value.search || 
         filters.value.status || 
         filters.value.customer || 
         filters.value.dateRange ||
         customStartDate.value ||
         customEndDate.value
})

const invoiceForm = ref({
  order: '',
  payment_terms: 'immediate',
  tax_rate: 10.0,
  discount_amount: 0,
  invoice_date: new Date().toISOString().split('T')[0], // Today's date
  due_date: '', // Will be calculated based on payment terms
  notes: '',
  terms_and_conditions: '',
  company_info: {}
})

// Computed
const invoiceSummary = computed(() => {
  const total = invoices.value.length
  const draft = invoices.value.filter(invoice => invoice.status === 'draft').length
  const sent = invoices.value.filter(invoice => invoice.status === 'sent').length
  const paid = invoices.value.filter(invoice => invoice.status === 'paid').length
  const overdue = invoices.value.filter(invoice => invoice.status === 'overdue').length
  const cancelled = invoices.value.filter(invoice => invoice.status === 'cancelled').length
  
  const totalAmount = invoices.value.reduce((sum, invoice) => sum + parseFloat(invoice.total_amount || 0), 0)
  const totalPaid = invoices.value.reduce((sum, invoice) => sum + parseFloat(invoice.amount_paid || 0), 0)
  const totalOutstanding = invoices.value.reduce((sum, invoice) => sum + parseFloat(invoice.balance_due || 0), 0)
  
  return { 
    total, 
    draft, 
    sent, 
    paid, 
    overdue, 
    cancelled,
    totalAmount,
    totalPaid,
    totalOutstanding
  }
})

const filteredInvoices = computed(() => {
  let filtered = invoices.value

  // Search filter
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(invoice => 
      invoice.invoice_number.toLowerCase().includes(search) ||
      invoice.customer_name.toLowerCase().includes(search) ||
      invoice.customer_email.toLowerCase().includes(search) ||
      (invoice.order?.order_number && invoice.order.order_number.toLowerCase().includes(search))
    )
  }

  // Status filter
  if (filters.value.status) {
    filtered = filtered.filter(invoice => invoice.status === filters.value.status)
  }

  // Customer filter
  if (filters.value.customer) {
    filtered = filtered.filter(invoice => {
      // Check if invoice has an order and the order has a customer
      if (invoice.order && invoice.order.customer) {
        // Convert both to strings for comparison to handle different data types
        return String(invoice.order.customer) === String(filters.value.customer)
      }
      return false
    })
  }

  // Date range filter
  if (filters.value.dateRange || customStartDate.value || customEndDate.value) {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    
    filtered = filtered.filter(invoice => {
      if (!invoice.created_at) return false
      
      const invoiceDate = new Date(invoice.created_at)
      
      // Custom date range filter
      if (customStartDate.value && customEndDate.value) {
        const startDate = new Date(customStartDate.value)
        const endDate = new Date(customEndDate.value)
        endDate.setHours(23, 59, 59, 999) // Include the entire end date
        return invoiceDate >= startDate && invoiceDate <= endDate
      }
      
      // Predefined date range filter
      if (filters.value.dateRange) {
        switch (filters.value.dateRange) {
          case 'today':
            return invoiceDate >= today
          case 'yesterday':
            const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
            return invoiceDate >= yesterday && invoiceDate < today
          case 'this_week':
            // Get start of current week (Monday)
            const daysSinceMonday = now.getDay() === 0 ? 6 : now.getDay() - 1
            const startOfWeek = new Date(today.getTime() - daysSinceMonday * 24 * 60 * 60 * 1000)
            return invoiceDate >= startOfWeek
          case 'week':
            const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
            return invoiceDate >= weekAgo
          case 'this_month':
            // Get start of current month
            const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
            return invoiceDate >= startOfMonth
          case 'month':
            const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
            return invoiceDate >= monthAgo
          case 'this_year':
            // Get start of current year
            const startOfYear = new Date(now.getFullYear(), 0, 1)
            return invoiceDate >= startOfYear
          case 'year':
            const yearAgo = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000)
            return invoiceDate >= yearAgo
          default:
            return true
        }
      }
      
      return true
    })
  }

  // Sort
  switch (filters.value.sortBy) {
    case 'date':
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    case 'amount':
      filtered.sort((a, b) => parseFloat(b.total_amount || 0) - parseFloat(a.total_amount || 0))
      break
    case 'status':
      filtered.sort((a, b) => a.status.localeCompare(b.status))
      break
    default:
      // Default sort by date
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }

  return filtered
})

// Chart data
const pieChartData = computed(() => {
  const statusCounts = {
    draft: invoices.value.filter(invoice => invoice.status === 'draft').length,
    sent: invoices.value.filter(invoice => invoice.status === 'sent').length,
    paid: invoices.value.filter(invoice => invoice.status === 'paid').length,
    overdue: invoices.value.filter(invoice => invoice.status === 'overdue').length,
    cancelled: invoices.value.filter(invoice => invoice.status === 'cancelled').length
  }
  
  return {
    labels: ['Draft', 'Sent', 'Paid', 'Overdue', 'Cancelled'],
    datasets: [{
      data: [
        statusCounts.draft,
        statusCounts.sent,
        statusCounts.paid,
        statusCounts.overdue,
        statusCounts.cancelled
      ],
      backgroundColor: [
        '#6B7280', // Gray for draft
        '#3B82F6', // Blue for sent
        '#10B981', // Green for paid
        '#EF4444', // Red for overdue
        '#F59E0B'  // Yellow for cancelled
      ],
      borderWidth: 2,
      borderColor: '#ffffff'
    }]
  }
})

const lineChartData = computed(() => {
  const currentYear = new Date().getFullYear()
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const values = []
  
  months.forEach((month, index) => {
    const monthStr = `${currentYear}-${String(index + 1).padStart(2, '0')}`
    
    const monthInvoices = invoices.value.filter(invoice => 
      invoice.created_at && invoice.created_at.startsWith(monthStr)
    )
    const monthValue = monthInvoices.reduce((sum, invoice) => sum + (parseFloat(invoice.total_amount) || 0), 0)
    values.push(monthValue)
  })
  
  console.log('Line chart data:', { months, values, invoicesCount: invoices.value.length })
  
  return {
    labels: months,
    datasets: [{
      label: 'Invoice Revenue',
      data: values,
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true
    }]
  }
})

// Methods
const fetchInvoices = async () => {
  try {
    loading.value = true
    console.log('Fetching invoices...')
    const response = await getInvoices()
    console.log('Raw invoice response:', response)
    invoices.value = response.results || response || []
    console.log('Invoices loaded:', invoices.value)
    console.log('Invoices count:', invoices.value.length)
  } catch (error) {
    console.error('Failed to fetch invoices:', error)
    toast.error('Failed to load invoices')
  } finally {
    loading.value = false
  }
}

const fetchCustomers = async () => {
  try {
    const response = await getUsers()
    customers.value = response.results || response || []
  } catch (error) {
    console.error('Failed to fetch customers:', error)
    // Don't show error toast as this is not critical
  }
}

const fetchProducts = async () => {
  try {
    const response = await getProducts()
    products.value = response.results || response || []
  } catch (error) {
    console.error('Failed to fetch products:', error)
    // Don't show error toast as this is not critical
  }
}

const fetchOrders = async () => {
  try {
    const response = await getOrders()
    orders.value = response.results || response || []
  } catch (error) {
    console.error('Failed to fetch orders:', error)
    toast.error('Failed to load orders')
  }
}

// Invoice action states
const showViewInvoiceModal = ref(false)
const showEditInvoiceModal = ref(false)
const showDeleteConfirmModal = ref(false)
const selectedInvoice = ref(null)
const invoiceToDelete = ref(null)

// Error handling
const invoiceCreationError = ref('')
const existingInvoiceMessage = ref('')
const canCreateInvoiceDueToExisting = ref(true)

const viewInvoice = (invoice) => {
  selectedInvoice.value = invoice
  showViewInvoiceModal.value = true
}

const editInvoice = (invoice) => {
  if (invoice.status === 'paid') {
    toast.warning('Paid invoices cannot be edited')
    return
  }
  selectedInvoice.value = invoice
  showEditInvoiceModal.value = true
}

const sendInvoiceAction = async (invoice) => {
  try {
    await sendInvoice(invoice.id)
    invoice.status = 'sent'
    toast.success(`Invoice ${invoice.invoice_number} sent to customer`)
    updateCharts()
  } catch (error) {
    console.error('Failed to send invoice:', error)
    toast.error('Failed to send invoice')
  }
}

const markPaid = async (invoice) => {
  try {
    await markInvoicePaid(invoice.id)
    invoice.status = 'paid'
    invoice.amount_paid = invoice.total_amount
    invoice.balance_due = 0
    toast.success(`Invoice ${invoice.invoice_number} marked as paid`)
    updateCharts()
  } catch (error) {
    console.error('Failed to mark invoice as paid:', error)
    toast.error('Failed to mark invoice as paid')
  }
}

const updateInvoiceAction = async () => {
  try {
    if (!selectedInvoice.value) {
      toast.error('No invoice selected for update')
      return
    }
    if (selectedInvoice.value.status === 'paid') {
      toast.error('Paid invoices cannot be edited')
      return
    }

    const updateData = {
      status: selectedInvoice.value.status,
      payment_terms: selectedInvoice.value.payment_terms,
      due_date: selectedInvoice.value.due_date,
      notes: selectedInvoice.value.notes
    }

    console.log('Updating invoice with data:', updateData)

    const updatedInvoice = await updateInvoice(selectedInvoice.value.id, updateData)
    
    // Refresh all invoice records from the backend
    await fetchInvoices()
    
    // Update the selected invoice with the fresh data
    const refreshedInvoice = invoices.value.find(i => i.id === selectedInvoice.value.id)
    if (refreshedInvoice) {
      selectedInvoice.value = refreshedInvoice
    }

    toast.success(`Invoice ${selectedInvoice.value.invoice_number} updated successfully`)
    showEditInvoiceModal.value = false
    selectedInvoice.value = null
    updateCharts()
  } catch (error) {
    console.error('Failed to update invoice:', error)
    toast.error('Failed to update invoice')
  }
}

const confirmDeleteInvoice = (invoice) => {
  if (invoice.status === 'paid') {
    toast.warning('Paid invoices cannot be deleted')
    return
  }
  invoiceToDelete.value = invoice
  showDeleteConfirmModal.value = true
}

const deleteInvoiceAction = async () => {
  try {
    if (!invoiceToDelete.value) {
      toast.error('No invoice selected for deletion')
      return
    }
    if (invoiceToDelete.value.status === 'paid') {
      toast.error('Paid invoices cannot be deleted')
      return
    }

    const response = await deleteInvoice(invoiceToDelete.value.id)
    
    // Check if the response indicates success
    if (response && response.success) {
      // Refresh all invoice records from the backend
      await fetchInvoices()
      
      toast.success(response.message || `Invoice ${invoiceToDelete.value.invoice_number} deleted successfully`)
      showDeleteConfirmModal.value = false
      invoiceToDelete.value = null
      updateCharts()
    } else {
      // Handle case where response indicates failure
      const errorMessage = response?.error || 'Failed to delete invoice'
      toast.error(errorMessage)
    }
  } catch (error) {
    console.error('Failed to delete invoice:', error)
    // Check if error has a response with error details
    const errorMessage = error.response?.data?.error || error.message || 'Failed to delete invoice'
    toast.error(errorMessage)
  }
}

// Calculate due date based on payment terms
const calculateDueDate = () => {
  const paymentTerms = invoiceForm.value.payment_terms
  const invoiceDate = new Date(invoiceForm.value.invoice_date)
  
  if (paymentTerms === 'immediate') {
    invoiceForm.value.due_date = invoiceForm.value.invoice_date
    toast.info('Due date set to invoice date for immediate payment')
  } else {
    const daysMap = {
      'net_7': 7,
      'net_15': 15,
      'net_30': 30,
      'net_45': 45,
      'net_60': 60
    }
    
    const daysToAdd = daysMap[paymentTerms] || 0
    const dueDate = new Date(invoiceDate)
    dueDate.setDate(dueDate.getDate() + daysToAdd)
    
    invoiceForm.value.due_date = dueDate.toISOString().split('T')[0]
    
    const paymentTermNames = {
      'net_7': 'Net 7',
      'net_15': 'Net 15', 
      'net_30': 'Net 30',
      'net_45': 'Net 45',
      'net_60': 'Net 60'
    }
    
    toast.success(`Due date calculated: ${paymentTermNames[paymentTerms]} (${daysToAdd} days from invoice date)`)
  }
}

const createInvoiceAction = async () => {
  try {
    console.log('createInvoiceAction called with button state:', {
      canCreateInvoice: canCreateInvoice.value,
      canCreateInvoiceDueToExisting: canCreateInvoiceDueToExisting.value,
      isCheckingBalance: isCheckingBalance.value
    })
    
    // Validate required fields
    if (!invoiceForm.value.order) {
      toast.error('Please select an order')
      return
    }
    
    if (!invoiceForm.value.invoice_date) {
      toast.error('Please select an invoice date')
      return
    }
    
    // Validate due date
    if (invoiceForm.value.payment_terms !== 'immediate' && !invoiceForm.value.due_date) {
      toast.error('Please select a due date')
      return
    }
    
    // Validate that due date is not before invoice date
    if (invoiceForm.value.due_date && invoiceForm.value.invoice_date) {
      const invoiceDate = new Date(invoiceForm.value.invoice_date)
      const dueDate = new Date(invoiceForm.value.due_date)
      
      if (dueDate < invoiceDate) {
        toast.error('Due date cannot be before invoice date')
        return
      }
    }
    
    // Check if order is fully paid
    if (!canCreateInvoice.value) {
      toast.error('Cannot create invoice for a fully paid order')
      return
    }
    
    // Check if there's an existing active invoice
    if (!canCreateInvoiceDueToExisting.value) {
      toast.error('Cannot create invoice: Order already has an active invoice with unexpired due date')
      return
    }
    
    // Use balance information if available
    let invoiceAmount = null
    if (selectedOrderBalance.value) {
      if (selectedOrderBalance.value.is_partially_paid) {
        invoiceAmount = selectedOrderBalance.value.balance
        toast.info(`Creating invoice for outstanding amount: ${formatAmount(invoiceAmount)} (${formatAmount(selectedOrderBalance.value.total_paid)} already paid)`)
      } else {
        invoiceAmount = selectedOrderBalance.value.order_total
        toast.info(`Creating invoice for full order amount: ${formatAmount(invoiceAmount)}`)
      }
    }
    
    const invoiceData = {
      order: invoiceForm.value.order,
      payment_terms: invoiceForm.value.payment_terms,
      tax_rate: invoiceForm.value.tax_rate,
      discount_amount: invoiceForm.value.discount_amount,
      invoice_date: invoiceForm.value.invoice_date,
      due_date: invoiceForm.value.due_date,
      notes: invoiceForm.value.notes,
      terms_and_conditions: invoiceForm.value.terms_and_conditions,
      company_info: invoiceForm.value.company_info
    }
    
    // Add balance information to notes if partially paid
    if (selectedOrderBalance.value?.is_partially_paid) {
      const balanceNote = `\n\n--- Payment Information ---\nOrder Total: ${formatAmount(selectedOrderBalance.value.order_total)}\nAmount Paid: ${formatAmount(selectedOrderBalance.value.total_paid)}\nRemaining Balance: ${formatAmount(selectedOrderBalance.value.balance)}\nPayment Transactions: ${selectedOrderBalance.value.payment_transactions_count}`
      invoiceData.notes = (invoiceData.notes || '') + balanceNote
    }
    
    console.log('Creating invoice with data:', invoiceData)
    
    const newInvoice = await createInvoice(invoiceData)
    
    // Refresh all invoice records from the backend
    await fetchInvoices()
    
    toast.success(`Invoice ${newInvoice.invoice_number} created successfully`)
    showNewInvoiceModal.value = false
    
    // Reset form
    initializeInvoiceForm()
    
    updateCharts()
  } catch (error) {
    console.error('Failed to create invoice:', error)
    
        // Handle specific validation errors from backend
    if (error.response?.data?.error) {
      const errorMessage = error.response.data.error
      toast.error(errorMessage)
    } else if (error.response?.data?.non_field_errors) {
      toast.error(error.response.data.non_field_errors[0])
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail)
    } else {
    toast.error('Failed to create invoice')
    }
  }
}

const downloadInvoice = async () => {
  try {
    if (filteredInvoices.value.length === 0) {
      toast.error('No invoices to export')
      return
    }
    
    toast.info(`Generating PDF for ${filteredInvoices.value.length} invoices...`)
    
    // Import jsPDF and html2canvas
    const { jsPDF } = await import('jspdf')
    const html2canvas = await import('html2canvas')
    
    // Create PDF
    const pdf = new jsPDF('p', 'mm', 'a4')
    let totalPages = 0
    
    for (let i = 0; i < filteredInvoices.value.length; i++) {
      const invoice = filteredInvoices.value[i]
      
      // Fetch payment transactions for this invoice's order
      let paymentTransactions = []
      const orderId = invoice.order?.id || invoice.order
      if (orderId) {
        try {
          console.log('Fetching payment transactions for order ID:', orderId, 'invoice:', invoice.invoice_number)
          
          // Use the specific endpoint to get payment transactions by order_id field
          const transactionsResponse = await getPaymentTransactionsByOrderId(orderId)
          console.log('Payment transactions response:', transactionsResponse)
          
          if (transactionsResponse && transactionsResponse.results) {
            paymentTransactions = transactionsResponse.results
            console.log('Found payment transactions:', paymentTransactions.length, 'for order_id:', orderId, 'invoice:', invoice.invoice_number)
          } else {
            console.log('No payment transactions found for order_id:', orderId, 'invoice:', invoice.invoice_number)
            paymentTransactions = []
          }
        } catch (error) {
          console.warn(`Failed to fetch payment transactions for invoice ${invoice.invoice_number}:`, error)
          // Continue without payment transactions
        }
      } else {
        console.warn('No order ID found for invoice:', invoice.invoice_number)
      }
      
              // For multi-page PDF, we'll always generate 2 pages per invoice (invoice + payment history)
      const pagesNeeded = 2
      
      // Generate pages for this invoice
      for (let page = 0; page < pagesNeeded; page++) {
          if (page > 0 || totalPages > 0) {
            pdf.addPage()
          }
          
          // Create a new div for this page
          const pageDiv = document.createElement('div')
          pageDiv.style.position = 'absolute'
          pageDiv.style.left = '-9999px'
          pageDiv.style.top = '0'
          pageDiv.style.width = '210mm'
          pageDiv.style.height = '297mm'
          pageDiv.style.padding = '20mm'
          pageDiv.style.backgroundColor = 'white'
          pageDiv.style.fontFamily = 'Arial, sans-serif'
          pageDiv.style.fontSize = '12px'
          pageDiv.style.lineHeight = '1.4'
          pageDiv.style.overflow = 'hidden'
          
          // Generate page-specific content
          const pageContent = generateInvoicePageContent(invoice, paymentTransactions, page, pagesNeeded)
          pageDiv.innerHTML = pageContent
          document.body.appendChild(pageDiv)
          
          // Convert to canvas
          const canvas = await html2canvas.default(pageDiv, {
            width: 210 * 3.779527559,
            height: 297 * 3.779527559,
            scale: 2,
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff'
          })
          
          // Add to PDF
          const imgData = canvas.toDataURL('image/png')
          pdf.addImage(imgData, 'PNG', 0, 0, 210, 297)
          
          document.body.removeChild(pageDiv)
          totalPages++
        }
    }
    
    // Download PDF
    const fileName = `invoices-${new Date().toISOString().split('T')[0]}.pdf`
    pdf.save(fileName)
    
    toast.success(`PDF generated successfully with ${filteredInvoices.value.length} invoices across ${totalPages} pages!`)
  } catch (error) {
    console.error('Error generating PDF:', error)
    toast.error('Failed to generate PDF')
  }
}

const downloadInvoiceAsPDF = async (invoice) => {
  try {
    toast.info('Generating PDF...')
    
    // Fetch payment transactions for this invoice's order
    let paymentTransactions = []
    const orderId = invoice.order?.id || invoice.order
    if (orderId) {
      try {
        const transactionsResponse = await getPaymentTransactionsByOrderId(orderId)
        paymentTransactions = transactionsResponse?.results || []
      } catch (error) {
        // continue without transactions
      }
    }
    
    // Import jsPDF and html2canvas
    const { jsPDF } = await import('jspdf')
    const html2canvas = await import('html2canvas')
    
    // Two pages: invoice + payment history
    const pagesNeeded = 2
    const pdf = new jsPDF('p', 'mm', 'a4')
    
    for (let page = 0; page < pagesNeeded; page++) {
      if (page > 0) pdf.addPage()
      
      // Off-screen page DOM
      const pageDiv = document.createElement('div')
      pageDiv.style.position = 'absolute'
      pageDiv.style.left = '-9999px'
      pageDiv.style.top = '0'
      pageDiv.style.width = '210mm'
      pageDiv.style.height = '297mm'
      pageDiv.style.padding = '20mm'
      pageDiv.style.backgroundColor = 'white'
      pageDiv.style.fontFamily = 'Arial, sans-serif'
      pageDiv.style.fontSize = '12px'
      pageDiv.style.lineHeight = '1.4'
      pageDiv.style.overflow = 'hidden'
      
      pageDiv.innerHTML = generateInvoicePageContent(
        invoice,
        paymentTransactions,
        page,
        pagesNeeded
      )
      document.body.appendChild(pageDiv)
      
      const canvas = await html2canvas.default(pageDiv, {
        width: 210 * 3.779527559,
        height: 297 * 3.779527559,
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff'
      })
      
      const imgData = canvas.toDataURL('image/png')
      pdf.addImage(imgData, 'PNG', 0, 0, 210, 297)
      document.body.removeChild(pageDiv)
    }
    
    const fileName = `invoice-${invoice.invoice_number}-${new Date().toISOString().split('T')[0]}.pdf`
    pdf.save(fileName)
    toast.success(`PDF generated successfully with ${pagesNeeded} pages!`)
  } catch (error) {
    console.error('Error generating PDF:', error)
    toast.error('Failed to generate PDF')
  }
}

const generateInvoicePageContent = (invoice, paymentTransactions = [], currentPage = 0, totalPages = 1) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0)
  }
  
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }
  
  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // Calculate outstanding amount using payment transactions
  const calculateOutstanding = (invoice, transactions) => {
    // If the invoice has a valid outstanding_amount, use it
    if (invoice.outstanding_amount && invoice.outstanding_amount > 0) {
      return invoice.outstanding_amount
    }
    
    // Calculate based on order total and successful payment transactions
    const orderTotal = parseFloat(invoice.order?.total_amount || invoice.total_amount || 0)
    
    // Sum all successful payment transactions
    const totalPaid = transactions
      .filter(t => t.status === 'successful')
      .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
    
    // Calculate outstanding amount
    const outstanding = Math.max(0, orderTotal - totalPaid)
    
    return outstanding
  }
  
  const outstandingAmount = calculateOutstanding(invoice, paymentTransactions)
  const totalPaid = paymentTransactions
    .filter(t => t.status === 'successful')
    .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
  
  // Shared watermark/header logo source
  const logoSrc = `${import.meta.env.BASE_URL || ''}assets/picture-CzkPMWkL.png`

  // Page-specific content generation
  if (currentPage === 0) {
    // Page 1: Invoice details
    return `
      <div style="font-family: Arial, sans-serif; color: #333; position: relative;">
        <!-- Watermark (image) -->
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-15deg); opacity: 0.08; z-index: 1; pointer-events: none;">
          <img src="${logoSrc}" style="width: 60%; max-width: 420px; filter: grayscale(100%); opacity: 0.5;" />
        </div>
        
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; position: relative; z-index: 2;">
          <div>
            <h1 style="font-size: 28px; font-weight: bold; color: #333; margin: 0 0 10px 0;">INVOICE</h1>
            <div style="font-size: 14px; color: #666;">
              <p style="margin: 5px 0;"><strong>Invoice #:</strong> ${invoice.invoice_number}</p>
              <p style="margin: 5px 0;"><strong>Date:</strong> ${formatDate(invoice.created_at)}</p>
              <p style="margin: 5px 0;"><strong>Due Date:</strong> ${formatDate(invoice.due_date)}</p>
              <p style="margin: 5px 0;"><strong>Status:</strong> <span style="text-transform: uppercase; font-weight: bold;">${invoice.status}</span></p>
            </div>
          </div>
          <div style="text-align: right;">
            <div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 15px;">
              <img src="${logoSrc}" alt="BottlePlug Logo" style="width: 40px; height: 40px; margin-right: 10px;" />
              <h2 style="font-size: 20px; font-weight: bold; color: #333; margin: 0;">BottlePlug</h2>
            </div>
            <div style="font-size: 12px; color: #666; line-height: 1.4;">
              <p style="margin: 3px 0;">123 Business Street</p>
              <p style="margin: 3px 0;">City, State 12345</p>
              <p style="margin: 3px 0;">Phone: (555) 123-4567</p>
              <p style="margin: 3px 0;">Email: info@bottleplug.com</p>
            </div>
          </div>
        </div>
      
              <!-- Customer Information -->
        <div style="margin-bottom: 30px; position: relative; z-index: 2;">
          <h3 style="font-size: 16px; font-weight: bold; color: #333; margin: 0 0 10px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">BILL TO:</h3>
          <div style="font-size: 14px; color: #333;">
            <p style="margin: 5px 0; font-weight: bold;">${invoice.customer_name || 'N/A'}</p>
            <p style="margin: 5px 0;">${invoice.customer_email || 'N/A'}</p>
            <p style="margin: 5px 0;">${invoice.customer_phone || 'N/A'}</p>
            ${invoice.order?.delivery_address ? `<p style="margin: 5px 0;">${invoice.order.delivery_address}</p>` : ''}
          </div>
        </div>
        
        <!-- Order Information -->
        ${invoice.order ? `
          <div style="margin-bottom: 30px; position: relative; z-index: 2;">
            <h3 style="font-size: 16px; font-weight: bold; color: #333; margin: 0 0 10px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">ORDER INFORMATION:</h3>
            <div style="font-size: 14px; color: #333;">
              <p style="margin: 5px 0;"><strong>Order ID:</strong> ${invoice.order.id || 'N/A'}</p>
              <p style="margin: 5px 0;"><strong>Order Date:</strong> ${formatDate(invoice.order.created_at)}</p>
              <p style="margin: 5px 0;"><strong>Delivery Type:</strong> ${invoice.order.is_pickup ? 'Pickup' : 'Delivery'}</p>
              ${invoice.order.is_pickup ? '' : `<p style="margin: 5px 0;"><strong>Delivery Fee:</strong> ${formatCurrency(invoice.delivery_fee || 0)}</p>`}
            </div>
          </div>
        ` : ''}
        
        <!-- Items Table -->
        <div style="margin-bottom: 30px; position: relative; z-index: 2;">
          <h3 style="font-size: 16px; font-weight: bold; color: #333; margin: 0 0 10px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">ITEMS:</h3>
          <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
            <thead>
              <tr style="background-color: #f8f9fa; border-bottom: 2px solid #333;">
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Item</th>
                <th style="padding: 10px; text-align: center; border-bottom: 1px solid #ddd;">Qty</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">Unit Price</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">Total</th>
              </tr>
            </thead>
            <tbody>
              ${invoice.order?.items ? invoice.order.items.map(item => `
                <tr style="border-bottom: 1px solid #eee;">
                  <td style="padding: 10px; text-align: left;">${item.product_name || 'N/A'}</td>
                  <td style="padding: 10px; text-align: center;">${item.quantity || 0}</td>
                  <td style="padding: 10px; text-align: right;">${formatCurrency(item.unit_price || 0)}</td>
                  <td style="padding: 10px; text-align: right;">${formatCurrency(item.total_price || 0)}</td>
                </tr>
              `).join('') : `
                <tr style="border-bottom: 1px solid #eee;">
                  <td style="padding: 10px; text-align: left;" colspan="4">No items available</td>
                </tr>
              `}
            </tbody>
          </table>
        </div>
        
        <!-- Financial Summary -->
        <div style="margin-bottom: 30px; position: relative; z-index: 2;">
          <h3 style="font-size: 16px; font-weight: bold; color: #333; margin: 0 0 10px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">FINANCIAL SUMMARY:</h3>
          <div style="display: flex; justify-content: flex-end;">
            <table style="width: 300px; font-size: 14px;">
              <tr>
                <td style="padding: 5px 10px; text-align: left;">Subtotal:</td>
                <td style="padding: 5px 10px; text-align: right;">${formatCurrency(invoice.subtotal || 0)}</td>
              </tr>
              ${invoice.delivery_fee && invoice.delivery_fee > 0 ? `
                <tr>
                  <td style="padding: 5px 10px; text-align: left;">Delivery Fee:</td>
                  <td style="padding: 5px 10px; text-align: right;">${formatCurrency(invoice.delivery_fee)}</td>
                </tr>
              ` : ''}
              <tr>
                <td style="padding: 5px 10px; text-align: left;">Tax (${invoice.tax_rate || 0}%):</td>
                <td style="padding: 5px 10px; text-align: right;">${formatCurrency(invoice.tax_amount || 0)}</td>
              </tr>
              ${invoice.discount_amount && invoice.discount_amount > 0 ? `
                <tr>
                  <td style="padding: 5px 10px; text-align: left;">Discount:</td>
                  <td style="padding: 5px 10px; text-align: right;">-${formatCurrency(invoice.discount_amount)}</td>
                </tr>
              ` : ''}
              <tr style="border-top: 2px solid #333; font-weight: bold; font-size: 16px;">
                <td style="padding: 10px; text-align: left;">TOTAL:</td>
                <td style="padding: 10px; text-align: right;">${formatCurrency(invoice.total_amount || 0)}</td>
              </tr>
              <tr style="font-weight: bold; border-top: 2px solid #dc3545; background-color: #fff5f5;">
                <td style="padding: 10px; text-align: left; color: #dc3545;">Outstanding Amount:</td>
                <td style="padding: 10px; text-align: right; color: #dc3545; font-size: 16px;">${formatCurrency(outstandingAmount)}</td>
              </tr>
            </table>
          </div>
        </div>
        
        <!-- Payment Terms -->
        <div style="margin-bottom: 30px; position: relative; z-index: 2;">
          <h3 style="font-size: 16px; font-weight: bold; color: #333; margin: 0 0 10px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">PAYMENT TERMS:</h3>
          <div style="font-size: 14px; color: #333;">
            <p style="margin: 5px 0;"><strong>Payment Terms:</strong> ${invoice.payment_terms || 'Immediate'}</p>
            <p style="margin: 5px 0;"><strong>Due Date:</strong> ${formatDate(invoice.due_date)}</p>
            ${invoice.status === 'overdue' ? '<p style="margin: 5px 0; color: #dc3545; font-weight: bold;">⚠️ OVERDUE</p>' : ''}
          </div>
        </div>
        
        <!-- Notes -->
        ${invoice.notes ? `
          <div style="margin-bottom: 30px; position: relative; z-index: 2;">
            <h3 style="font-size: 16px; font-weight: bold; color: #333; margin: 0 0 10px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">NOTES:</h3>
            <div style="font-size: 14px; color: #333; line-height: 1.5;">
              <p style="margin: 0; white-space: pre-wrap;">${invoice.notes}</p>
            </div>
          </div>
        ` : ''}
        
        <!-- Footer -->
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 12px; color: #666; text-align: center; position: relative; z-index: 2;">
          <p style="margin: 5px 0;">Thank you for your business!</p>
          <p style="margin: 5px 0;">For questions, please contact us at info@bottleplug.com</p>
          <p style="margin: 5px 0;">Generated on ${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
        </div>
        
        <!-- Page indicator -->
        ${totalPages > 1 ? `
          <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #666; position: relative; z-index: 2;">
            Page ${currentPage + 1} of ${totalPages}
          </div>
        ` : ''}
      </div>
    `
  } else {
    // Page 2: Payment transactions
    return `
      <div style="font-family: Arial, sans-serif; color: #333; position: relative;">
        <!-- Watermark (image) -->
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-15deg); opacity: 0.08; z-index: 1; pointer-events: none;">
          <img src="${logoSrc}" style="width: 60%; max-width: 420px; filter: grayscale(100%); opacity: 0.5;" />
        </div>
        
        <!-- Header for page 2 -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; position: relative; z-index: 2;">
          <div>
            <h1 style="font-size: 28px; font-weight: bold; color: #333; margin: 0 0 10px 0;">PAYMENT HISTORY</h1>
            <div style="font-size: 14px; color: #666;">
              <p style="margin: 5px 0;"><strong>Invoice #:</strong> ${invoice.invoice_number}</p>
              <p style="margin: 5px 0;"><strong>Date:</strong> ${formatDate(invoice.created_at)}</p>
            </div>
          </div>
          <div style="text-align: right;">
            <div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 15px;">
              <img src="${logoSrc}" alt="BottlePlug Logo" style="width: 40px; height: 40px; margin-right: 10px;" />
              <h2 style="font-size: 20px; font-weight: bold; color: #333; margin: 0;">BottlePlug</h2>
            </div>
          </div>
        </div>
        
        <!-- Payment Transactions -->
        ${paymentTransactions.length > 0 ? `
          <div style="margin-bottom: 30px; position: relative; z-index: 2;">
            <h3 style="font-size: 16px; font-weight: bold; color: #333; margin: 0 0 10px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">PAYMENT HISTORY:</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
              <thead>
                <tr style="background-color: #f8f9fa; border-bottom: 2px solid #333;">
                  <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Date</th>
                  <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Transaction ID</th>
                  <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Order ID</th>
                  <th style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">Amount</th>
                  <th style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd;">Status</th>
                </tr>
              </thead>
              <tbody>
                ${paymentTransactions
                  .filter(t => t.status === 'successful')
                  .map(transaction => `
                    <tr style="border-bottom: 1px solid #eee;">
                      <td style="padding: 8px; text-align: left;">${formatDateTime(transaction.created_at)}</td>
                      <td style="padding: 8px; text-align: left; font-family: monospace; font-size: 11px;">${transaction.transaction_id || transaction.id}</td>
                      <td style="padding: 8px; text-align: left; font-family: monospace; font-size: 11px;">${transaction.order_id || 'N/A'}</td>
                      <td style="padding: 8px; text-align: right; font-weight: bold;">${formatCurrency(transaction.amount)}</td>
                      <td style="padding: 8px; text-align: center;">
                        <span style="background-color: #d4edda; color: #155724; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold;">
                          ${transaction.status}
                        </span>
                      </td>
                    </tr>
                  `).join('')}
              </tbody>
            </table>
          </div>
        ` : `
          <div style="margin-bottom: 30px; position: relative; z-index: 2;">
            <h3 style="font-size: 16px; font-weight: bold; color: #333; margin: 0 0 10px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">PAYMENT HISTORY:</h3>
            <div style="font-size: 14px; color: #666; text-align: center; padding: 40px;">
              <p>No payment transactions found for this invoice.</p>
            </div>
          </div>
        `}
        
        <!-- Footer -->
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 12px; color: #666; text-align: center; position: relative; z-index: 2;">
          <p style="margin: 5px 0;">Thank you for your business!</p>
          <p style="margin: 5px 0;">For questions, please contact us at info@bottleplug.com</p>
          <p style="margin: 5px 0;">Generated on ${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
        </div>
        
        <!-- Page indicator -->
        ${totalPages > 1 ? `
          <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #666; position: relative; z-index: 2;">
            Page ${currentPage + 1} of ${totalPages}
          </div>
        ` : ''}
      </div>
    `
  }
}



const getStatusClass = (status) => {
  switch (status) {
    case 'draft':
      return 'bg-gray-100 text-gray-800'
    case 'sent':
      return 'bg-blue-100 text-blue-800'
    case 'paid':
      return 'bg-green-100 text-green-800'
    case 'overdue':
      return 'bg-red-100 text-red-800'
    case 'cancelled':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatAmount = (amount) => {
  const num = parseFloat(amount) || 0
  return num.toFixed(2)
}

const isInvoiceOverdue = (invoice) => {
  if (!invoice.due_date || invoice.status === 'paid') {
    return false
  }
  const dueDate = new Date(invoice.due_date)
  const today = new Date()
  return dueDate < today
}

const getDueDateClass = (invoice) => {
  if (!invoice.due_date) return 'text-gray-500'
  if (invoice.status === 'paid') return 'text-green-600'
  if (isInvoiceOverdue(invoice)) return 'text-red-600'
  return 'text-gray-900'
}

// Check payment balance for selected order
const checkExistingInvoices = async (orderId) => {
  try {
    console.log('=== CHECKING EXISTING INVOICES ===')
    console.log('OrderId:', orderId, 'type:', typeof orderId)
    console.log('Total invoices available:', invoices.value.length)
    console.log('All invoices with their order IDs:')
    invoices.value.forEach((inv, index) => {
      console.log(`Invoice ${index + 1}:`, {
        id: inv.id,
        order: inv.order,
        order_type: typeof inv.order,
        order_id: inv.order?.id || inv.order,
        invoice_number: inv.invoice_number,
        due_date: inv.due_date
      })
    })
    
    // Filter existing invoices for this order (convert to string for comparison)
    const existingInvoices = invoices.value.filter(invoice => {
      const invoiceOrderId = invoice.order?.id || invoice.order
      const match = String(invoiceOrderId) === String(orderId)
      console.log(`Comparing invoice order ${invoiceOrderId} (${typeof invoiceOrderId}) with selected order ${orderId} (${typeof orderId}): ${match}`)
      return match
    })
    
    console.log('Found existing invoices:', existingInvoices)
    
    if (existingInvoices.length === 0) {
      existingInvoiceMessage.value = ''
      canCreateInvoiceDueToExisting.value = true
      console.log('No existing invoices found, can create invoice')
      return
    }
    
    // Get the most recent invoice for this order
    const mostRecentInvoice = existingInvoices.sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    )[0]
    
    const today = new Date()
    today.setHours(0, 0, 0, 0) // Set to start of day for accurate comparison
    const dueDate = new Date(mostRecentInvoice.due_date)
    dueDate.setHours(0, 0, 0, 0) // Set to start of day for accurate comparison
    
    console.log('Date comparison:', {
      today: today.toISOString(),
      dueDate: dueDate.toISOString(),
      dueDateString: mostRecentInvoice.due_date,
      isExpired: dueDate < today
    })
    
    if (dueDate < today) {
      // Due date has passed, can create new invoice
      const expiredMessage = `Order #${mostRecentInvoice.order?.order_number || orderId} has an expired invoice (#${mostRecentInvoice.invoice_number}) with due date ${formatDate(mostRecentInvoice.due_date)}. You can create a new invoice.`
      existingInvoiceMessage.value = expiredMessage
      canCreateInvoiceDueToExisting.value = true
      console.log('✅ Invoice is expired, can create new invoice')
      console.log('✅ Set existingInvoiceMessage to:', expiredMessage)
      console.log('✅ Set canCreateInvoiceDueToExisting to true')
    } else {
      // Due date is in the future, cannot create new invoice
      const daysUntilDue = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24))
      const message = `Order #${mostRecentInvoice.order?.order_number || orderId} already has an active invoice (#${mostRecentInvoice.invoice_number}) with due date ${formatDate(mostRecentInvoice.due_date)} (${daysUntilDue} days remaining). Cannot create new invoice.`
      existingInvoiceMessage.value = message
      canCreateInvoiceDueToExisting.value = false
      console.log('❌ Invoice is active, cannot create new invoice. Days until due:', daysUntilDue)
      console.log('❌ Set existingInvoiceMessage to:', message)
      console.log('❌ Set canCreateInvoiceDueToExisting to false')
      
      // Show immediate error toast when active invoice is found
      toast.error(`Cannot create invoice: Order #${mostRecentInvoice.order?.order_number || orderId} already has an active invoice (#${mostRecentInvoice.invoice_number}) with due date ${formatDate(mostRecentInvoice.due_date)} (${daysUntilDue} days remaining)`)
    }
    
    console.log('Final canCreateInvoiceDueToExisting value:', canCreateInvoiceDueToExisting.value)
    
  } catch (error) {
    console.error('Failed to check existing invoices:', error)
    existingInvoiceMessage.value = ''
    canCreateInvoiceDueToExisting.value = true
  }
}

const checkOrderPaymentBalance = async (orderId) => {
  try {
    isCheckingBalance.value = true
    balanceMessage.value = ''
    
    console.log('Checking payment balance for orderId:', orderId)
    
    const balanceData = await getOrderPaymentBalance(orderId)
    selectedOrderBalance.value = balanceData
    
    console.log('Payment balance data:', balanceData)
    
    if (balanceData.is_fully_paid) {
      canCreateInvoice.value = false
      balanceMessage.value = `Cannot create invoice: Order #${balanceData.order_number} is fully paid (${formatAmount(balanceData.total_paid)}/${formatAmount(balanceData.order_total)})`
      toast.warning('This order is fully paid. Cannot create invoice.')
    } else if (balanceData.is_partially_paid) {
      canCreateInvoice.value = true
      balanceMessage.value = `Order #${balanceData.order_number} has partial payment. Outstanding amount: ${formatAmount(balanceData.balance)} (${formatAmount(balanceData.total_paid)} already paid of ${formatAmount(balanceData.order_total)})`
      toast.info(`Order has partial payment. Outstanding amount: ${formatAmount(balanceData.balance)}`)
    } else {
      canCreateInvoice.value = true
      balanceMessage.value = `Order #${balanceData.order_number} has no payments. Total amount: ${formatAmount(balanceData.order_total)}`
    }
    
  } catch (error) {
    console.error('Failed to check payment balance:', error)
    selectedOrderBalance.value = null
    canCreateInvoice.value = true
    balanceMessage.value = 'Unable to check payment balance. Proceed with caution.'
    toast.error('Failed to check payment balance')
  } finally {
    isCheckingBalance.value = false
  }
}

// Calculate outstanding amount for an invoice based on order payment transactions
const calculateInvoiceOutstanding = (invoice) => {
  // If the invoice has a valid outstanding_amount, use it
  if (invoice.outstanding_amount && invoice.outstanding_amount > 0) {
    return invoice.outstanding_amount
  }
  
  // Otherwise, calculate based on order total and payment transactions
  // This is a fallback for existing invoices that don't have the correct outstanding_amount
  const orderTotal = parseFloat(invoice.order?.total_amount || invoice.total_amount || 0)
  const amountPaid = parseFloat(invoice.amount_paid || 0)
  
  // Calculate outstanding amount
  const outstanding = Math.max(0, orderTotal - amountPaid)
  
  return outstanding
}

// Chart functions
const initPieChart = () => {
  console.log('Initializing pie chart...')
  console.log('Pie chart data:', pieChartData.value)
  
  if (pieChartRef.value) {
    const ctx = pieChartRef.value.getContext('2d')
    pieChart = new Chart(ctx, {
      type: 'pie',
      data: pieChartData.value,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    })
    console.log('Pie chart initialized successfully')
  }
}

const initLineChart = () => {
  console.log('Initializing line chart...')
  console.log('Line chart data:', lineChartData.value)
  
  if (lineChartRef.value) {
    const ctx = lineChartRef.value.getContext('2d')
    lineChart = new Chart(ctx, {
      type: 'line',
      data: lineChartData.value,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value.toFixed(2)
              }
            }
          }
        }
      }
    })
    console.log('Line chart initialized successfully')
  }
}

const updateCharts = () => {
  console.log('Updating charts...')
  nextTick(() => {
    if (pieChart) {
      console.log('Updating pie chart with data:', pieChartData.value)
      pieChart.data = pieChartData.value
      pieChart.update()
    } else {
      console.warn('Pie chart not initialized')
    }
    if (lineChart) {
      console.log('Updating line chart with data:', lineChartData.value)
      lineChart.data = lineChartData.value
      lineChart.update()
    } else {
      console.warn('Line chart not initialized')
    }
  })
}

// Initialize invoice form
const initializeInvoiceForm = () => {
  invoiceForm.value = {
    order: '',
    payment_terms: 'immediate',
    tax_rate: 10.0,
    discount_amount: 0,
    invoice_date: new Date().toISOString().split('T')[0],
    due_date: new Date().toISOString().split('T')[0], // Same as invoice date for immediate
    notes: '',
    terms_and_conditions: '',
    company_info: {}
  }
  
  // Reset balance tracking
  selectedOrderBalance.value = null
  canCreateInvoice.value = true
  balanceMessage.value = ''
  isCheckingBalance.value = false
  // Clear any previous errors
  existingInvoiceMessage.value = ''
  canCreateInvoiceDueToExisting.value = true
}

// Watch for changes in payment terms or invoice date to recalculate due date
watch([() => invoiceForm.value.payment_terms, () => invoiceForm.value.invoice_date], () => {
  if (invoiceForm.value.invoice_date) {
    calculateDueDate()
  }
})

// Watch for manual due date changes to validate
watch(() => invoiceForm.value.due_date, (newDueDate) => {
  if (newDueDate && invoiceForm.value.invoice_date) {
    const invoiceDate = new Date(invoiceForm.value.invoice_date)
    const dueDate = new Date(newDueDate)
    
    if (dueDate < invoiceDate) {
      toast.warning('Due date cannot be before invoice date')
      // Reset to invoice date if invalid
      invoiceForm.value.due_date = invoiceForm.value.invoice_date
    }
  }
})

// Watch for order selection to check payment balance and existing invoices
watch(() => invoiceForm.value.order, async (newOrderId, oldOrderId) => {
  if (newOrderId) {
    await Promise.all([
      checkOrderPaymentBalance(newOrderId),
      checkExistingInvoices(newOrderId)
    ])
    
    console.log('After both checks - canCreateInvoice:', canCreateInvoice.value, 'canCreateInvoiceDueToExisting:', canCreateInvoiceDueToExisting.value)
  } else {
    // Reset balance info when no order is selected
    selectedOrderBalance.value = null
    canCreateInvoice.value = true
    balanceMessage.value = ''
    existingInvoiceMessage.value = ''
    canCreateInvoiceDueToExisting.value = true
  }
})

// Custom date range functions
const applyCustomDateRange = () => {
  if (customStartDate.value && customEndDate.value) {
    // Clear predefined date filter when using custom range
    filters.value.dateRange = ''
    showDateRangeModal.value = false
    toast.success('Custom date range applied')
  } else {
    toast.error('Please select both start and end dates')
  }
}

const clearDateFilters = () => {
  filters.value.dateRange = ''
  customStartDate.value = ''
  customEndDate.value = ''
  toast.success('Date filters cleared')
}

const getFilterDisplayName = (filterValue) => {
  const filterNames = {
    'today': 'Today',
    'yesterday': 'Yesterday',
    'this_week': 'This Week',
    'week': 'Last 7 Days',
    'this_month': 'This Month',
    'month': 'Last 30 Days',
    'this_year': 'This Year',
    'year': 'Last 365 Days'
  }
  return filterNames[filterValue] || filterValue
}

// Lifecycle
onMounted(async () => {
  console.log('Invoices component mounted')
  try {
    console.log('Starting to fetch data...')
    await Promise.all([
      fetchInvoices(),
      fetchCustomers(),
      fetchProducts(),
      fetchOrders()
    ])
    console.log('All data fetched successfully')
    console.log('Invoices count:', invoices.value.length)
    console.log('Filtered invoices count:', filteredInvoices.value.length)
    nextTick(() => {
      console.log('Initializing charts...')
      initPieChart()
      initLineChart()
      console.log('Charts initialized')
    })
  } catch (error) {
    console.error('Error during component initialization:', error)
  }
})

// Branded backend PDF functionality removed as requested
</script> 