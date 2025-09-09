<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-800">Orders</h1>
        <p class="text-secondary-600">Manage customer orders and deliveries</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="refreshOrders"
          class="btn btn-outline"
          :disabled="loading"
        >
          <RefreshCw v-if="loading" class="h-4 w-4 animate-spin" />
          <RefreshCw v-else class="h-4 w-4" />
          Refresh
        </button>
        <button @click="showAddModal = true" class="btn btn-primary">
          <Plus class="h-4 w-4" />
          New Order
        </button>
      </div>
    </div>

    <!-- Order Statistics -->
    <div v-if="orderStats" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Package class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Total Orders</p>
            <p class="text-2xl font-bold text-secondary-800">{{ orderStats.total_orders || 0 }}</p>
          </div>
        </div>
      </div>
      
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Clock class="h-8 w-8 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Pending</p>
            <p class="text-2xl font-bold text-secondary-800">{{ orderStats.pending_orders || 0 }}</p>
          </div>
        </div>
      </div>
      
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Check class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Delivered</p>
            <p class="text-2xl font-bold text-secondary-800">{{ orderStats.delivered_orders || 0 }}</p>
          </div>
        </div>
      </div>
      
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <DollarSign class="h-8 w-8 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Revenue</p>
            <p class="text-2xl font-bold text-secondary-800">UGX {{ formatPrice(orderStats.total_revenue) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-wrap gap-3">
      <button
        @click="navigateToOrderReceipts"
        class="btn btn-outline"
      >
        <FileText class="h-4 w-4" />
        Order Receipts
      </button>
      <button
        @click="navigateToInvoices"
        class="btn btn-outline"
      >
        <Receipt class="h-4 w-4" />
        Invoices
      </button>
      <button
        @click="navigateToReceipts"
        class="btn btn-outline"
      >
        <CreditCard class="h-4 w-4" />
        Receipts
      </button>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search orders..."
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
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="processing">Processing</option>
            <option value="ready_for_delivery">Ready for Delivery</option>
            <option value="out_for_delivery">Out for Delivery</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
            <option value="refunded">Refunded</option>
          </select>
          <div class="relative">
            <select
              v-model="dateFilter"
              :class="[
                'px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent pr-8',
                dateFilter ? 'border-primary-300 bg-primary-50' : 'border-secondary-200'
              ]"
              @change="handleFilter"
            >
              <option value="">All Dates</option>
              <option value="today">Today</option>
              <option value="yesterday">Yesterday</option>
              <option value="this_week">This Week (Mon-Sun)</option>
              <option value="week">Last 7 Days</option>
              <option value="this_month">This Month</option>
              <option value="month">Last 30 Days</option>
              <option value="this_year">This Year</option>
              <option value="year">Last 365 Days</option>
            </select>
            <div v-if="dateFilter" class="absolute right-2 top-1/2 transform -translate-y-1/2">
              <div class="w-2 h-2 bg-primary-500 rounded-full"></div>
            </div>
          </div>
          <button
            @click="showDateRangeModal = true"
            class="px-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent hover:bg-secondary-50"
            title="Custom Date Range"
          >
            <Calendar class="h-4 w-4" />
          </button>
          <button
            v-if="dateFilter || customStartDate || customEndDate"
            @click="clearDateFilters"
            class="px-4 py-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-50"
            title="Clear Date Filters"
          >
            <X class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Orders Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-secondary-200">
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Order ID</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Customer</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Type</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Items</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Total</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Status</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Date</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading" class="border-b border-secondary-100">
              <td colspan="8" class="py-8 px-4 text-center">
                <div class="flex items-center justify-center">
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                  <span class="ml-2 text-secondary-600">Loading orders...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="filteredOrders.length === 0" class="border-b border-secondary-100">
              <td colspan="8" class="py-8 px-4 text-center text-secondary-600">
                No orders found
              </td>
            </tr>
            <tr
              v-for="order in filteredOrders"
              :key="order.id"
              class="border-b border-secondary-100 hover:bg-secondary-50"
            >
              <td class="py-4 px-4">
                <span class="font-medium text-secondary-800">#{{ order.order_number || order.id }}</span>
              </td>
              <td class="py-4 px-4">
                <div>
                  <p class="font-medium text-secondary-800">{{ order.customer?.name || order.customer_name }}</p>
                  <p class="text-sm text-secondary-600">{{ order.customer?.email || order.customer_email }}</p>
                </div>
              </td>
              <td class="py-4 px-4">
                <span :class="[
                  'px-2 py-1 rounded-full text-xs font-medium',
                  order.is_pickup ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                ]">
                  {{ order.is_pickup ? 'Pickup' : 'Delivery' }}
                </span>
              </td>
              <td class="py-4 px-4">
                <span class="text-secondary-700">{{ (order.items && Array.isArray(order.items) ? order.items.length : 0) }} items</span>
              </td>
              <td class="py-4 px-4">
                <div class="text-right">
                  <div class="font-medium text-secondary-800">UGX {{ formatPrice(order.total_amount) }}</div>
                  <div class="text-xs text-secondary-500">
                    Subtotal: UGX {{ formatPrice(order.subtotal || 0) }}
                    <span v-if="order.delivery_fee > 0" class="ml-1">+ UGX {{ formatPrice(order.delivery_fee) }} delivery</span>
                  </div>
                </div>
              </td>
              <td class="py-4 px-4">
                <div class="flex items-center gap-2">
                  <component 
                    :is="getStatusIcon(order.status)" 
                    class="w-4 h-4"
                    :class="order.status_changing ? 'animate-spin' : ''"
                  />
                  <span :class="[
                    'px-2 py-1 rounded-full text-sm font-medium transition-all duration-200',
                    getStatusClass(order.status),
                    order.status_changing ? 'opacity-75' : '',
                    order.status_success ? 'animate-pulse bg-green-100 text-green-800' : ''
                  ]">
                    {{ order.status }}
                  </span>
                  <span v-if="order.status_changing" class="text-xs text-secondary-500">
                    Updating...
                  </span>
                  <span v-if="order.status_success" class="text-xs text-green-600 flex items-center gap-1">
                    <Check class="w-3 h-3" />
                    Updated!
                  </span>
                </div>
              </td>
              <td class="py-4 px-4">
                <span class="text-secondary-700">{{ formatDate(order.created_at) }}</span>
              </td>
              <td class="py-4 px-4">
                <div class="flex items-center space-x-2">
                  <button
                    @click="viewOrder(order)"
                    class="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="View"
                  >
                    <Eye class="h-4 w-4" />
                  </button>
                  <button
                    @click="editOrder(order)"
                    :disabled="!isOrderEditable(order.status)"
                    :class="[
                      'p-2 rounded-lg transition-colors',
                      isOrderEditable(order.status)
                        ? 'text-secondary-600 hover:text-blue-600 hover:bg-blue-50 cursor-pointer'
                        : 'text-gray-400 cursor-not-allowed'
                    ]"
                    :title="isOrderEditable(order.status) ? 'Edit' : `Cannot edit order with status: ${order.status}`"
                  >
                    <Edit class="h-4 w-4" />
                  </button>
                  <button
                    v-if="order.status === 'pending'"
                    @click="confirmOrderAction(order.id)"
                    class="p-2 text-secondary-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Confirm"
                  >
                    <Check class="h-4 w-4" />
                  </button>
                  <button
                    v-if="order.status === 'confirmed'"
                    @click="updateOrderStatus(order.id, 'processing')"
                    class="p-2 text-secondary-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Process"
                  >
                    <Play class="h-4 w-4" />
                  </button>
                  <button
                    v-if="order.status === 'processing'"
                    @click="updateOrderStatus(order.id, 'ready_for_delivery')"
                    class="p-2 text-secondary-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                    title="Ready for Delivery"
                  >
                    <Package class="h-4 w-4" />
                  </button>
                  <button
                    v-if="!order.is_pickup && order.status === 'ready_for_delivery'"
                    @click="openAssignDriverModal(order)"
                    class="p-2 text-secondary-600 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                    title="Assign Driver"
                  >
                    <User class="h-4 w-4" />
                  </button>
                  <button
                    v-if="!order.is_pickup && ['pending', 'confirmed', 'processing'].includes(order.status)"
                    @click="showOrderNotReadyMessage(order.status)"
                    class="p-2 text-secondary-600 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                    title="Order not ready for driver assignment"
                  >
                    <User class="h-4 w-4" />
                  </button>
                  <button
                    v-if="!order.is_pickup && ['out_for_delivery', 'delivered', 'cancelled', 'refunded'].includes(order.status)"
                    @click="showOrderStatusMessage(order.status)"
                    class="p-2 text-secondary-600 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                    title="Driver already assigned or order completed"
                  >
                    <User class="h-4 w-4" />
                  </button>
                  <button
                    v-if="order.status === 'out_for_delivery'"
                    @click="updateOrderStatus(order.id, 'delivered')"
                    class="p-2 text-secondary-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Mark Delivered"
                  >
                    <Check class="h-4 w-4" />
                  </button>
                  <button
                    v-if="['pending', 'confirmed', 'processing'].includes(order.status)"
                    @click="cancelOrderAction(order.id)"
                    class="p-2 text-secondary-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Cancel"
                  >
                    <X class="h-4 w-4" />
                  </button>
                  
                  <!-- Status Change Button -->
                  <button
                    @click="openStatusDialog(order)"
                    class="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="Change Status"
                  >
                    <RefreshCw class="h-4 w-4" />
                  </button>
                  <!-- Payment Button or Status Badges -->
                  <div v-if="order.status === 'cancelled'" class="inline-flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                    <X class="h-4 w-4 mr-1" />
                    Cancelled
                  </div>
                  <div v-else-if="isOrderPaid(order.id) || order.payment_status === 'paid'" class="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                    <Check class="h-4 w-4 mr-1" />
                    Cleared
                  </div>
                  <div v-else class="inline-block">
                    <PaymentButton
                      :amount="parseFloat(order.total_amount)"
                      :currency="'UGX'"
                      :description="`Payment for order #${order.order_number}`"
                      :transaction-type="'order'"
                      :entity-id="order.id"
                      :button-text="'Pay'"
                      @payment_done="handlePaymentDone"
                      class="inline-block"
                    />
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && filteredOrders.length > 0" class="flex items-center justify-between">
      <p class="text-sm text-secondary-600">
        Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalOrders) }} of {{ totalOrders }} orders
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
  </div>

  <!-- Order Details Dialog -->
  <Dialog :show="showOrderDetailsModal" title="Order Details" @close="showOrderDetailsModal = false">
    <div v-if="selectedOrder" class="space-y-6">
      <!-- Order Header -->
      <div class="bg-secondary-50 p-4 rounded-lg">
        <div class="flex justify-between items-start">
          <div>
            <h4 class="text-xl font-bold text-secondary-800">{{ selectedOrder.order_number }}</h4>
            <p class="text-sm text-secondary-600">Created: {{ formatDate(selectedOrder.created_at) }}</p>
          </div>
          <span :class="[
            'px-3 py-1 rounded-full text-sm font-medium',
            getStatusClass(selectedOrder.status)
          ]">
            {{ selectedOrder.status }}
          </span>
        </div>
      </div>

      <!-- Customer Information -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <div>
            <h5 class="text-lg font-semibold text-secondary-800 mb-3">Customer Information</h5>
            <div class="space-y-3">
              <div class="flex items-center space-x-3">
                <User class="h-5 w-5 text-secondary-500" />
                <div>
                  <p class="font-medium">{{ selectedOrder.customer_name }}</p>
                  <p class="text-sm text-secondary-600">{{ selectedOrder.customer_email }}</p>
                </div>
              </div>
              <div v-if="selectedOrder.customer_phone" class="flex items-center space-x-3">
                <Phone class="h-5 w-5 text-secondary-500" />
                <p class="text-sm text-secondary-600">{{ selectedOrder.customer_phone }}</p>
              </div>
            </div>
          </div>

          <!-- Payment Status -->
          <div>
            <h5 class="text-lg font-semibold text-secondary-800 mb-3">Payment Status</h5>
            <div class="flex items-center space-x-3">
              <CreditCard class="h-5 w-5 text-secondary-500" />
              <div class="flex items-center space-x-2">
                <span v-if="isOrderPaid(selectedOrder.id)" class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  <Check class="h-4 w-4 inline mr-1" />
                  Paid
                </span>
                <span v-else class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                  Pending
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="space-y-4">
          <div>
            <h5 class="text-lg font-semibold text-secondary-800 mb-3">Order Summary</h5>
                         <div class="space-y-2">
               <div class="flex justify-between">
                 <span class="text-secondary-600">Subtotal:</span>
                 <span class="font-medium">UGX {{ (parseFloat(selectedOrder.subtotal) || 0).toFixed(2) }}</span>
               </div>
               <div class="flex justify-between">
                 <span class="text-secondary-600">Delivery Fee:</span>
                 <span class="font-medium">UGX {{ (parseFloat(selectedOrder.delivery_fee) || 0).toFixed(2) }}</span>
               </div>
               <div class="flex justify-between">
                 <span class="text-secondary-600">Tax:</span>
                 <span class="font-medium">UGX {{ (parseFloat(selectedOrder.tax) || 0).toFixed(2) }}</span>
               </div>
               <div class="flex justify-between">
                 <span class="text-secondary-600">Discount:</span>
                 <span class="font-medium">UGX {{ (parseFloat(selectedOrder.discount) || 0).toFixed(2) }}</span>
               </div>
               <div class="border-t pt-2">
                 <div class="flex justify-between">
                   <span class="font-semibold text-lg">Total:</span>
                   <span class="font-bold text-lg text-primary-600">UGX {{ (parseFloat(selectedOrder.total_amount) || 0).toFixed(2) }}</span>
                 </div>
               </div>
             </div>
          </div>

          <!-- Delivery Information -->
          <div v-if="!selectedOrder.is_pickup">
            <h5 class="text-lg font-semibold text-secondary-800 mb-3">Delivery Information</h5>
            <div class="space-y-2">
              <div class="flex items-center space-x-3">
                <MapPin class="h-5 w-5 text-secondary-500" />
                <div>
                  <p class="font-medium">{{ selectedOrder.delivery_address || 'Address not specified' }}</p>
                  <p v-if="selectedOrder.address_line1" class="text-sm text-secondary-600">{{ selectedOrder.address_line1 }}</p>
                  <p v-if="selectedOrder.address_line2" class="text-sm text-secondary-600">{{ selectedOrder.address_line2 }}</p>
                  <p v-if="selectedOrder.city || selectedOrder.state" class="text-sm text-secondary-600">
                    {{ [selectedOrder.city, selectedOrder.state, selectedOrder.postal_code].filter(Boolean).join(', ') }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div v-else>
            <h5 class="text-lg font-semibold text-secondary-800 mb-3">Pickup Information</h5>
            <div class="flex items-center space-x-3">
              <Package class="h-5 w-5 text-secondary-500" />
              <span class="text-sm text-secondary-600">Customer will pick up the order</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Order Items -->
      <div v-if="selectedOrder.items && selectedOrder.items.length > 0">
        <h5 class="text-lg font-semibold text-secondary-800 mb-3">Order Items</h5>
        <div class="space-y-3">
          <div v-for="item in selectedOrder.items" :key="item.id" class="flex justify-between items-center p-3 bg-secondary-50 rounded-lg">
            <div class="flex-1">
              <p class="font-medium">{{ item.product_name }}</p>
              <p class="text-sm text-secondary-600">SKU: {{ item.product_sku || 'N/A' }}</p>
            </div>
                         <div class="text-right">
               <p class="font-medium">UGX {{ (parseFloat(item.unit_price) || 0).toFixed(2) }} × {{ item.quantity }}</p>
               <p class="font-semibold text-primary-600">UGX {{ (parseFloat(item.total_price) || 0).toFixed(2) }}</p>
             </div>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="selectedOrder.notes">
        <h5 class="text-lg font-semibold text-secondary-800 mb-3">Notes</h5>
        <div class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p class="text-sm text-secondary-700">{{ selectedOrder.notes }}</p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-end space-x-3 pt-4 border-t">
        <button 
          @click="showOrderDetailsModal = false"
          class="px-4 py-2 text-secondary-600 hover:text-secondary-800"
        >
          Close
        </button>
        <button 
          v-if="isOrderEditable(selectedOrder.status)"
          @click="editOrder(selectedOrder)"
          class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600"
        >
          Edit Order
        </button>
      </div>
    </div>
  </Dialog>

  <!-- Assign Driver Dialog -->
  <Dialog :show="showAssignDriverModal" title="Assign Driver" @close="showAssignDriverModal = false">
    <div v-if="selectedOrder" class="space-y-4">
      <div>
        <p class="text-sm font-medium text-secondary-600 mb-2">Order: {{ selectedOrder.order_number }}</p>
        <p class="text-sm text-secondary-600">Customer: {{ selectedOrder.customer_name }}</p>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-secondary-700 mb-2">Select Driver</label>
        <select 
          v-model="selectedDriverId" 
          class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="">Select a driver...</option>
          <option v-for="driver in drivers" :key="driver.id" :value="driver.id">
            {{ driver.first_name }} {{ driver.last_name }} - {{ driver.phone }}
          </option>
        </select>
      </div>
      
      <div class="flex justify-end space-x-3 pt-4">
        <button 
          @click="showAssignDriverModal = false" 
          class="px-4 py-2 text-secondary-600 hover:text-secondary-800"
        >
          Cancel
        </button>
        <button 
          @click="assignDriver(selectedOrder.id, selectedDriverId)"
          :disabled="!selectedDriverId"
          class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50"
        >
          Assign Driver
        </button>
      </div>
    </div>
  </Dialog>

  <!-- Date Range Modal -->
  <Dialog :show="showDateRangeModal" title="Custom Date Range" @close="showDateRangeModal = false">
    <div class="space-y-4">
      <!-- Active filters indicator -->
      <div v-if="dateFilter || customStartDate || customEndDate" class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p class="text-sm font-medium text-blue-800 mb-1">Active Filters:</p>
        <div class="text-xs text-blue-600 space-y-1">
          <p v-if="dateFilter">Quick Filter: {{ getFilterDisplayName(dateFilter) }}</p>
          <p v-if="customStartDate && customEndDate">
            Custom Range: {{ customStartDate }} to {{ customEndDate }}
          </p>
        </div>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-secondary-700 mb-2">Start Date</label>
        <input 
          v-model="customStartDate"
          type="date"
          class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-secondary-700 mb-2">End Date</label>
        <input 
          v-model="customEndDate"
          type="date"
          class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>
      
      <div class="flex justify-end space-x-3 pt-4">
        <button 
          @click="showDateRangeModal = false"
          class="px-4 py-2 text-secondary-600 hover:text-secondary-800"
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
  </Dialog>

  <!-- Create Order Dialog -->
  <Dialog :show="showAddModal" title="Create New Order" @close="showAddModal = false">
          <form id="create-order-form" @submit.prevent="createOrderAction" class="space-y-6">
        <!-- Customer Selection -->
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">Customer</label>
          <select 
            v-model="newOrder.customer_id" 
            @change="updateCustomerDetails"
            required
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Select a customer</option>
            <option v-for="customer in customers" :key="customer.id" :value="customer.id">
              {{ customer.name }} ({{ customer.email }})
            </option>
          </select>
        </div>

        <!-- Customer Details -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-secondary-700 mb-2">Customer Name</label>
            <input 
              v-model="newOrder.customer_name"
              type="text"
              required
              placeholder="Customer name"
              class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-secondary-700 mb-2">Customer Email</label>
            <input 
              v-model="newOrder.customer_email"
              type="email"
              required
              placeholder="Customer email"
              class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">Customer Phone</label>
          <input 
            v-model="newOrder.customer_phone"
            type="tel"
            placeholder="Customer phone number"
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <!-- Product Selection -->
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">Products</label>
          <div class="space-y-3">
            <div v-for="(item, index) in newOrder.items" :key="index" class="flex gap-3">
              <select 
                v-model="item.product_id" 
                required
                class="flex-1 px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select a product</option>
                <option v-for="product in products" :key="product.id" :value="product.id">
                  {{ product.name }} - UGX {{ product.price }}
                </option>
              </select>
              <input 
                v-model.number="item.quantity" 
                type="number" 
                min="1"
                placeholder="Qty"
                class="w-20 px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button 
                type="button"
                @click="removeOrderItem(index)"
                class="px-3 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md"
              >
                <X class="h-4 w-4" />
              </button>
            </div>
            <button 
              type="button"
              @click="addOrderItem"
              class="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              + Add Product
            </button>
          </div>
        </div>

        <!-- Pickup/Delivery Option -->
        <div>
          <label class="flex items-center space-x-2">
            <input 
              v-model="newOrder.is_pickup"
              type="checkbox"
              class="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-secondary-700">Pickup Order</span>
          </label>
        </div>

        <!-- Delivery Address (only show if not pickup) -->
        <div v-if="!newOrder.is_pickup">
          <label class="block text-sm font-medium text-secondary-700 mb-2">Delivery Address</label>
          <textarea 
            v-model="newOrder.delivery_address"
            rows="3"
            placeholder="Enter delivery address"
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          ></textarea>
        </div>

        <!-- Detailed Address Fields (only show if not pickup) -->
        <div v-if="!newOrder.is_pickup" class="space-y-4">
          <h4 class="text-sm font-medium text-secondary-700">Detailed Address</h4>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-secondary-700 mb-2">Address Line 1</label>
              <input 
                v-model="newOrder.address_line1"
                type="text"
                placeholder="House number, street name"
                class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-secondary-700 mb-2">Address Line 2</label>
              <input 
                v-model="newOrder.address_line2"
                type="text"
                placeholder="Apartment, building, etc."
                class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-secondary-700 mb-2">City</label>
              <input 
                v-model="newOrder.city"
                type="text"
                placeholder="City or town"
                class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-secondary-700 mb-2">District/County</label>
              <input 
                v-model="newOrder.district"
                type="text"
                placeholder="District or county"
                class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-secondary-700 mb-2">State/Region</label>
              <input 
                v-model="newOrder.state"
                type="text"
                placeholder="State, province, or region"
                class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-secondary-700 mb-2">Postal Code</label>
              <input 
                v-model="newOrder.postal_code"
                type="text"
                placeholder="ZIP or postal code"
                class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary-700 mb-2">Country</label>
            <input 
              v-model="newOrder.country"
              type="text"
              placeholder="Country"
              class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <!-- Order Notes -->
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">Order Notes</label>
          <textarea 
            v-model="newOrder.notes"
            rows="2"
            placeholder="Optional notes about the order"
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          ></textarea>
        </div>

        <!-- Cost Breakdown -->
        <div class="bg-secondary-50 p-4 rounded-lg">
          <h4 class="font-medium text-secondary-800 mb-3">Cost Breakdown</h4>
          <div class="space-y-3">
            <!-- Items -->
            <div v-for="item in newOrder.items.filter(i => i.product_id)" :key="item.product_id" class="flex justify-between text-sm">
              <span>{{ getProductName(item.product_id) }} x{{ item.quantity }}</span>
              <span class="font-medium">UGX {{ formatPrice(getProductPrice(item.product_id) * item.quantity) }}</span>
            </div>
            
            <div class="border-t pt-2 space-y-2">
              <!-- Subtotal -->
              <div class="flex justify-between text-sm">
                <span>Subtotal:</span>
                <span>UGX {{ formatPrice(calculateOrderTotal()) }}</span>
              </div>
              
              <!-- Tax -->
              <div class="flex justify-between text-sm">
                <span>Tax (0%):</span>
                <span>UGX 0</span>
              </div>
              
              <!-- Delivery Fee (Transportation) -->
              <div class="flex justify-between text-sm">
                <span>Transportation:</span>
                <div class="flex items-center space-x-2">
                  <span v-if="newOrder.is_pickup">UGX 0</span>
                  <div v-else class="flex items-center space-x-1">
                    <span>UGX</span>
                    <input 
                      v-model.number="newOrder.delivery_fee"
                      type="number"
                      min="0"
                      step="1"
                      class="w-20 px-2 py-0.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
                    />
                  </div>
                </div>
              </div>
              
              <!-- Discount -->
              <div class="flex justify-between text-sm">
                <span>Discount:</span>
                <span>UGX 0</span>
              </div>
              
              <!-- Total -->
              <div class="border-t pt-2 flex justify-between font-semibold text-base">
                <span>Total:</span>
                <span>UGX {{ formatPrice(calculateOrderTotalWithFees()) }}</span>
              </div>
            </div>
          </div>
        </div>

      </form>

      <template #footer>
        <button 
          type="button"
          @click="showAddModal = false"
          class="px-4 py-2 text-secondary-600 hover:text-secondary-700 border border-secondary-300 rounded-md"
        >
          Cancel
        </button>
        <button 
          type="submit"
          form="create-order-form"
          :disabled="creatingOrder"
          class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 flex items-center gap-2"
        >
          <span v-if="creatingOrder" class="animate-spin">⏳</span>
          {{ creatingOrder ? 'Creating...' : 'Create Order' }}
        </button>
      </template>
  </Dialog>

  <!-- Edit Order Dialog -->
  <Dialog :show="showEditModal" title="Edit Order" @close="showEditModal = false">
    <!-- Loading State -->
    <div v-if="loadingOrderDetails" class="flex items-center justify-center py-8">
      <div class="flex items-center space-x-2">
        <RefreshCw class="h-5 w-5 animate-spin text-primary-600" />
        <span class="text-secondary-600">Loading order details...</span>
      </div>
    </div>
    
    <!-- Edit Form -->
    <form v-else id="edit-order-form" @submit.prevent="updateOrderDetails" class="space-y-6">
      <!-- Customer Selection -->
      <div>
        <label class="block text-sm font-medium text-secondary-700 mb-2">Customer</label>
        <select 
          v-model="editingOrder.customer_id" 
          @change="updateEditingCustomerDetails"
          class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">Select a customer</option>
          <option v-for="customer in customers" :key="customer.id" :value="customer.id">
            {{ customer.name }} ({{ customer.email }})
          </option>
        </select>
      </div>

      <!-- Customer Details -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">Customer Name</label>
                      <input 
              v-model="editingOrder.customer_name"
              type="text"
              placeholder="Customer name"
              class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
        </div>
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">Customer Email</label>
                      <input 
              v-model="editingOrder.customer_email"
              type="email"
              placeholder="Customer email"
              class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-secondary-700 mb-2">Customer Phone</label>
        <input 
          v-model="editingOrder.customer_phone"
          type="tel"
          placeholder="Customer phone number"
          class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <!-- Product Selection -->
      <div>
        <label class="block text-sm font-medium text-secondary-700 mb-2">Products</label>
        <div class="space-y-3">
          <div v-for="(item, index) in editingOrder.items" :key="index" class="flex gap-3">
            <select 
              v-model="item.product_id" 
              class="flex-1 px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Select a product</option>
              <option v-for="product in products" :key="product.id" :value="product.id">
                {{ product.name }} - UGX {{ product.price }}
              </option>
            </select>
            <input 
              v-model.number="item.quantity" 
              type="number" 
              min="1"
              required
              placeholder="Qty"
              class="w-20 px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button 
              type="button"
              @click="removeEditingOrderItem(index)"
              class="px-3 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md"
            >
              <X class="h-4 w-4" />
            </button>
          </div>
          <button 
            type="button"
            @click="addEditingOrderItem"
            class="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            + Add Product
          </button>
        </div>
      </div>

      <!-- Delivery Options -->
      <div>
        <label class="flex items-center">
          <input 
            v-model="editingOrder.is_pickup"
            type="checkbox"
            class="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
          />
          <span class="ml-2 text-sm text-secondary-700">Pickup (no delivery)</span>
        </label>
      </div>

      <!-- Delivery Address -->
      <div v-if="!editingOrder.is_pickup">
        <label class="block text-sm font-medium text-secondary-700 mb-2">Delivery Address</label>
        <textarea 
          v-model="editingOrder.delivery_address"
          rows="3"
          placeholder="Full delivery address"
          class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        ></textarea>
      </div>

      <!-- Address Details -->
      <div v-if="!editingOrder.is_pickup" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">Address Line 1</label>
          <input 
            v-model="editingOrder.address_line1"
            type="text"
            placeholder="Street address"
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">Address Line 2</label>
          <input 
            v-model="editingOrder.address_line2"
            type="text"
            placeholder="Apartment, suite, etc."
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      <div v-if="!editingOrder.is_pickup" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">City</label>
          <input 
            v-model="editingOrder.city"
            type="text"
            placeholder="City"
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">District</label>
          <input 
            v-model="editingOrder.district"
            type="text"
            placeholder="District"
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">State</label>
          <input 
            v-model="editingOrder.state"
            type="text"
            placeholder="State"
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      <div v-if="!editingOrder.is_pickup" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">Postal Code</label>
          <input 
            v-model="editingOrder.postal_code"
            type="text"
            placeholder="Postal code"
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-secondary-700 mb-2">Country</label>
          <input 
            v-model="editingOrder.country"
            type="text"
            placeholder="Country"
            class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      <!-- Notes -->
      <div>
        <label class="block text-sm font-medium text-secondary-700 mb-2">Notes</label>
        <textarea 
          v-model="editingOrder.notes"
          rows="3"
          placeholder="Additional notes for this order"
          class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        ></textarea>
      </div>

      <!-- Cost Breakdown -->
      <div class="bg-secondary-50 p-4 rounded-lg">
        <h4 class="font-medium text-secondary-800 mb-3">Cost Breakdown</h4>
        <div class="space-y-3">
          <!-- Items -->
          <div v-for="item in editingOrder.items.filter(i => i.product_id)" :key="item.product_id" class="flex justify-between text-sm">
            <span>{{ getProductName(item.product_id) }} x{{ item.quantity }}</span>
            <span class="font-medium">UGX {{ formatPrice(getProductPrice(item.product_id) * item.quantity) }}</span>
          </div>
          
          <div class="border-t pt-2 space-y-2">
            <!-- Subtotal -->
            <div class="flex justify-between text-sm">
              <span>Subtotal:</span>
              <span>UGX {{ formatPrice(calculateEditingOrderTotal()) }}</span>
            </div>
            
            <!-- Tax -->
            <div class="flex justify-between text-sm">
              <span>Tax (0%):</span>
              <span>UGX 0</span>
            </div>
            
            <!-- Delivery Fee (Transportation) -->
            <div class="flex justify-between text-sm">
              <span>Transportation:</span>
              <div class="flex items-center space-x-2">
                <span v-if="editingOrder.is_pickup">UGX 0</span>
                <div v-else class="flex items-center space-x-1">
                  <span>UGX</span>
                  <input 
                    v-model.number="editingOrder.delivery_fee"
                    type="number"
                    min="0"
                    step="1"
                    class="w-20 px-2 py-0.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>
            
            <!-- Discount -->
            <div class="flex justify-between text-sm">
              <span>Discount:</span>
              <span>UGX 0</span>
            </div>
            
            <!-- Total -->
            <div class="border-t pt-2 flex justify-between font-semibold text-base">
              <span>Total:</span>
              <span>UGX {{ formatPrice(calculateEditingOrderTotalWithFees()) }}</span>
            </div>
          </div>
        </div>
      </div>

    </form>

    <template #footer>
      <button 
        type="button"
        @click="showEditModal = false"
        class="px-4 py-2 text-secondary-600 hover:text-secondary-700 border border-secondary-300 rounded-md"
      >
        Cancel
      </button>
      <button 
        type="submit"
        form="edit-order-form"
        :disabled="updatingOrder"
        class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 flex items-center gap-2"
      >
        <span v-if="updatingOrder" class="animate-spin">⏳</span>
        {{ updatingOrder ? 'Updating...' : 'Update Order' }}
      </button>
    </template>
  </Dialog>

  <!-- Status Change Dialog -->
  <Dialog :show="showStatusDialog" title="Change Order Status" @close="closeStatusDialog">
    <div v-if="selectedOrderForStatus" class="space-y-4">
      <div class="mb-4">
        <p class="text-sm text-secondary-600">Order #{{ selectedOrderForStatus.order_number }}</p>
        <p class="text-sm text-secondary-600">Current Status: 
          <span :class="[
            'px-2 py-1 rounded-full text-xs font-medium',
            getStatusClass(selectedOrderForStatus.status)
          ]">
            {{ selectedOrderForStatus.status }}
          </span>
        </p>
      </div>

      <div v-if="selectedOrderForStatus.status_changing" class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div class="flex items-center gap-2 text-blue-700">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-700"></div>
          <span class="text-sm font-medium">Updating order status...</span>
        </div>
      </div>
      
      <div v-if="selectedOrderForStatus.status_success" class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
        <div class="flex items-center gap-2 text-green-700">
          <Check class="w-4 h-4" />
          <span class="text-sm font-medium">Status updated successfully!</span>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <button
          v-for="status in getAllStatuses()"
          :key="status.value"
          @click="updateOrderStatus(selectedOrderForStatus.id, status.value)"
          :disabled="selectedOrderForStatus.status_changing"
          :class="[
            'p-4 rounded-lg border-2 transition-all duration-200 flex items-center gap-3',
            status.value === selectedOrderForStatus.status
              ? 'border-primary-500 bg-primary-50 text-primary-700'
              : 'border-secondary-200 hover:border-primary-300 hover:bg-primary-50',
            selectedOrderForStatus.status_changing ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'
          ]"
        >
          <component :is="getStatusIcon(status.value)" class="w-5 h-5" />
          <div class="text-left">
            <div class="font-medium">{{ status.label }}</div>
            <div class="text-xs text-secondary-600">{{ status.description }}</div>
          </div>
        </button>
      </div>
    </div>

    <template #footer>
      <button 
        @click="closeStatusDialog"
        class="px-4 py-2 text-secondary-600 hover:text-secondary-700 border border-secondary-300 rounded-md"
      >
        Cancel
      </button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, h } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import Dialog from '@/components/Dialog.vue'
import Modal from '@/components/Modal.vue'
import PaymentButton from '@/components/PaymentButton.vue'
import { 
  Plus, 
  RefreshCw, 
  Edit, 
  Eye, 
  Play, 
  Truck, 
  Check, 
  X,
  FileText,
  Receipt,
  CreditCard,
  Package,
  User,
  Clock,
  DollarSign,
  RotateCcw,
  Search,
  Filter,
  MoreVertical,
  Phone,
  Mail,
  MapPin,
  Calendar,
  ShoppingCart,
  Send,
  Download,
  Trash2
} from 'lucide-vue-next'
import {
  getOrders, 
  getOrder, 
  createOrder, 
  updateOrder,
  updateOrderStatus as updateOrderStatusAPI, 
  cancelOrder, 
  confirmOrder, 
  assignDriverToOrder,
  getOrderStats,
  getDrivers,
  getProducts,
  getUsers,
  checkOrderPaymentStatus
} from '@/services/api'


const router = useRouter()

// State
const loading = ref(false)
const orders = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const dateFilter = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showOrderDetailsModal = ref(false)
const showAssignDriverModal = ref(false)
const showDateRangeModal = ref(false)
const selectedOrder = ref(null)
const selectedDriverId = ref('')
const customStartDate = ref('')
const customEndDate = ref('')
const drivers = ref([])
const orderStats = ref({})
const currentPage = ref(1)
const pageSize = ref(10)
const totalOrders = ref(0)
const showStatusMenu = ref(null)
const showStatusDialog = ref(false)
const selectedOrderForStatus = ref(null)
const products = ref([])
const customers = ref([])
const creatingOrder = ref(false)
const updatingOrder = ref(false)
const loadingOrderDetails = ref(false)
const orderPaymentStatus = ref({}) // Track payment status for each order
const newOrder = ref({
  customer_id: '',
  customer_name: '',
  customer_email: '',
  customer_phone: '',
  is_pickup: false,
  delivery_fee: 15000, // Default transportation fee (UGX)
  items: [{ product_id: '', quantity: 1 }],
  delivery_address: '',
  address_line1: '',
  address_line2: '',
  city: '',
  district: '',
  state: '',
  postal_code: '',
  country: '',
  notes: ''
})

const editingOrder = ref({
  id: null,
  customer_id: '',
  customer_name: '',
  customer_email: '',
  customer_phone: '',
  is_pickup: false,
  delivery_fee: 15000, // Default transportation fee (UGX)
  items: [{ product_id: '', quantity: 1 }],
  delivery_address: '',
  address_line1: '',
  address_line2: '',
  city: '',
  district: '',
  state: '',
  postal_code: '',
  country: '',
  notes: ''
})

// Computed
const filteredOrders = computed(() => {
  let filtered = orders.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(order =>
      order.order_number?.toLowerCase().includes(query) ||
      order.customer?.name?.toLowerCase().includes(query) ||
      order.customer?.email?.toLowerCase().includes(query) ||
      order.customer_name?.toLowerCase().includes(query) ||
      order.customer_email?.toLowerCase().includes(query)
    )
  }

  // Status filter
  if (statusFilter.value) {
    filtered = filtered.filter(order => order.status === statusFilter.value)
  }

  // Date filter
  if (dateFilter.value) {
    const now = new Date()
    const orderDate = new Date(order.created_at)
    
    switch (dateFilter.value) {
      case 'today':
        filtered = filtered.filter(order => {
          const orderDate = new Date(order.created_at)
          return orderDate.toDateString() === now.toDateString()
        })
        break
      case 'week':
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        filtered = filtered.filter(order => {
          const orderDate = new Date(order.created_at)
          return orderDate >= weekAgo
        })
        break
      case 'month':
        const monthAgo = new Date(now.getFullYear(), now.getMonth(), 1)
        filtered = filtered.filter(order => {
          const orderDate = new Date(order.created_at)
          return orderDate >= monthAgo
        })
        break
      case 'year':
        const yearAgo = new Date(now.getFullYear(), 0, 1)
        filtered = filtered.filter(order => {
          const orderDate = new Date(order.created_at)
          return orderDate >= yearAgo
        })
        break
    }
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(totalOrders.value / pageSize.value))

// Methods
const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // Add status filter
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    // Add date filter
    if (dateFilter.value) {
      params.dateFilter = dateFilter.value
    }
    
    // Add custom date range
    if (customStartDate.value && customEndDate.value) {
      params.startDate = customStartDate.value
      params.endDate = customEndDate.value
    }
    
    console.log('Fetching orders with params:', params)
    console.log('Current filters:', {
      statusFilter: statusFilter.value,
      dateFilter: dateFilter.value,
      customStartDate: customStartDate.value,
      customEndDate: customEndDate.value
    })
    
    const response = await getOrders(params)
    orders.value = response.results || response
    totalOrders.value = response.count || response.length
    
    console.log('Orders loaded:', orders.value)
    
    // Check payment status for each order
    for (const order of orders.value) {
      await checkPaymentStatus(order.id)
    }
  } catch (error) {
    console.error('Failed to fetch orders:', error)
    toast.error('Failed to load orders')
  } finally {
    loading.value = false
  }
}

const fetchDrivers = async () => {
  try {
    const response = await getDrivers()
    drivers.value = response.results || response || []
  } catch (error) {
    console.error('Failed to fetch drivers:', error)
    // Don't show error toast for drivers as it's not critical
    drivers.value = []
  }
}

const fetchOrderStats = async () => {
  try {
    const response = await getOrderStats()
    orderStats.value = response || {}
  } catch (error) {
    console.error('Failed to fetch order stats:', error)
    // Don't show error toast for stats as it's not critical
    orderStats.value = {}
  }
}

const refreshOrders = async () => {
  await fetchOrders()
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  console.log('Filter changed:', { 
    statusFilter: statusFilter.value, 
    dateFilter: dateFilter.value,
    customStartDate: customStartDate.value,
    customEndDate: customEndDate.value
  })
  currentPage.value = 1
  fetchOrders()
}

const getStatusClass = (status) => {
  switch (status?.toLowerCase()) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'confirmed':
      return 'bg-blue-100 text-blue-800'
    case 'processing':
      return 'bg-indigo-100 text-indigo-800'
    case 'ready_for_delivery':
      return 'bg-purple-100 text-purple-800'
    case 'out_for_delivery':
      return 'bg-orange-100 text-orange-800'
    case 'delivered':
      return 'bg-green-100 text-green-800'
    case 'cancelled':
      return 'bg-red-100 text-red-800'
    case 'refunded':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-secondary-100 text-secondary-800'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatPrice = (price) => {
  if (!price && price !== 0) return '0.00'
  const numPrice = parseFloat(price)
  if (isNaN(numPrice)) return '0.00'
  return numPrice.toFixed(2)
}

const viewOrder = (order) => {
  selectedOrder.value = order
  showOrderDetailsModal.value = true
}

// Check if order can be edited based on status
const isOrderEditable = (status) => {
  const nonEditableStatuses = ['out_for_delivery', 'delivered', 'cancelled', 'refunded']
  return !nonEditableStatuses.includes(status)
}

// Check payment status for an order
const checkPaymentStatus = async (orderId) => {
  try {
    const response = await checkOrderPaymentStatus(orderId)
    if (response.success) {
      orderPaymentStatus.value[orderId] = response
    }
  } catch (error) {
    console.error('Failed to check payment status for order:', orderId, error)
  }
}

// Check if order is paid
const isOrderPaid = (orderId) => {
  const status = orderPaymentStatus.value[orderId]
  return status && status.is_paid
}

// Show message when order is not ready for driver assignment
const showOrderNotReadyMessage = (status) => {
  const statusMessages = {
    'pending': 'Order is still pending and not ready for driver assignment.',
    'confirmed': 'Order is confirmed but not yet processed. Driver assignment will be available when order is ready for delivery.',
    'processing': 'Order is being processed. Driver assignment will be available when order is ready for delivery.'
  }
  toast.info(statusMessages[status] || 'Order is not ready for driver assignment.')
}

// Show message for completed or cancelled orders
const showOrderStatusMessage = (status) => {
  const statusMessages = {
    'out_for_delivery': 'Order is already out for delivery with a driver assigned.',
    'delivered': 'Order has been successfully delivered.',
    'cancelled': 'Order has been cancelled and cannot be assigned to a driver.',
    'refunded': 'Order has been refunded and cannot be assigned to a driver.'
  }
  toast.info(statusMessages[status] || 'Order status does not allow driver assignment.')
}

// Open driver assignment modal
const openAssignDriverModal = (order) => {
  console.log('Opening assign driver modal for order:', order)
  console.log('Order status:', order.status)
  console.log('Order is_pickup:', order.is_pickup)
  selectedOrder.value = order
  selectedDriverId.value = '' // Reset driver selection
  showAssignDriverModal.value = true
  console.log('Modal should be open:', showAssignDriverModal.value)
}

// Apply custom date range filter
const applyCustomDateRange = () => {
  if (customStartDate.value && customEndDate.value) {
    // Clear other date filters
    dateFilter.value = ''
    
    // Set custom date range
    currentPage.value = 1
    console.log('Applying custom date range:', {
      startDate: customStartDate.value,
      endDate: customEndDate.value,
      dateFilter: dateFilter.value
    })
    fetchOrders()
    showDateRangeModal.value = false
    toast.success('Custom date range applied')
  } else {
    toast.error('Please select both start and end dates')
  }
}

// Get human-readable filter name
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

// Clear all date filters
const clearDateFilters = () => {
  console.log('Clearing date filters')
  dateFilter.value = ''
  customStartDate.value = ''
  customEndDate.value = ''
  currentPage.value = 1
  fetchOrders()
  toast.success('Date filters cleared')
}

const editOrder = async (order) => {
  // Check if order can be edited
  if (!isOrderEditable(order.status)) {
    toast.error(`Cannot edit order with status: ${order.status}`)
    return
  }
  
  try {
    // Show loading state
    loadingOrderDetails.value = true
    showEditModal.value = true
    
    // Fetch detailed order data
    console.log('Fetching order details for ID:', order.id)
    const orderDetails = await getOrder(order.id)
    console.log('Order details fetched:', orderDetails)
    
    // Populate the edit form with fetched order data
    editingOrder.value = {
      id: orderDetails.id,
      customer_id: orderDetails.customer_id || '',
      customer_name: orderDetails.customer_name || '',
      customer_email: orderDetails.customer_email || '',
      customer_phone: orderDetails.customer_phone || '',
      is_pickup: orderDetails.is_pickup || false,
      delivery_fee: orderDetails.delivery_fee || 15000, // Include transportation fee
      items: orderDetails.items && Array.isArray(orderDetails.items) ? orderDetails.items.map(item => ({
        product_id: item.product?.toString() || item.product_id?.toString() || '',
        quantity: item.quantity || 1,
        product_name: item.product_name || '',
        unit_price: item.unit_price || 0
      })) : [{ product_id: '', quantity: 1 }],
      delivery_address: orderDetails.delivery_address || '',
      address_line1: orderDetails.address_line1 || '',
      address_line2: orderDetails.address_line2 || '',
      city: orderDetails.city || '',
      district: orderDetails.district || '',
      state: orderDetails.state || '',
      postal_code: orderDetails.postal_code || '',
      country: orderDetails.country || '',
      notes: orderDetails.notes || ''
    }
    
    console.log('Populated editingOrder:', editingOrder.value)
  } catch (error) {
    console.error('Failed to fetch order details:', error)
    toast.error('Failed to load order details')
    showEditModal.value = false
  } finally {
    loadingOrderDetails.value = false
  }
}

const updateOrderStatus = async (orderId, newStatus) => {
  try {
    console.log('Updating order status:', orderId, newStatus)
    
    // Show loading state
    const order = orders.value.find(o => o.id === orderId)
    if (order) {
      order.status = newStatus
      order.status_changing = true
      order.status_success = false
    }
    
    console.log('Calling API with orderId:', orderId, 'newStatus:', newStatus)
    const result = await updateOrderStatusAPI(orderId, newStatus)
    console.log('API response:', result)
    
    // Show success state briefly
    if (order) {
      order.status_success = true
      setTimeout(() => {
        order.status_success = false
      }, 2000)
    }
    
    // Show success with status icon
    const statusInfo = getAllStatuses().find(s => s.value === newStatus)
    const statusIcon = getStatusIcon(newStatus)
    
    toast.success(
      `Order status updated to ${statusInfo?.label || newStatus}`,
      {
        icon: statusIcon ? h(statusIcon, { class: 'w-5 h-5' }) : undefined,
        position: 'top-right',
        autoClose: 3000
      }
    )
    
    closeStatusDialog()
    await fetchOrders()
  } catch (error) {
    console.error('Failed to update order status:', error)
    console.error('Error details:', {
      message: error.message,
      status: error.status,
      response: error.response
    })
    toast.error(`Failed to update order status: ${error.message}`)
    
    // Revert the status change on error
    const order = orders.value.find(o => o.id === orderId)
    if (order) {
      await fetchOrders() // Refresh to get correct status
    }
  } finally {
    // Clear loading state
    const order = orders.value.find(o => o.id === orderId)
    if (order) {
      order.status_changing = false
    }
  }
}

const openStatusDialog = (order) => {
  selectedOrderForStatus.value = order
  showStatusDialog.value = true
}

const closeStatusDialog = () => {
  showStatusDialog.value = false
  selectedOrderForStatus.value = null
}

const getAllStatuses = () => {
  return [
    { 
      value: 'pending', 
      label: 'Pending', 
      description: 'Order is waiting to be confirmed',
      icon: 'clock'
    },
    { 
      value: 'confirmed', 
      label: 'Confirmed', 
      description: 'Order has been confirmed and is ready for processing',
      icon: 'check'
    },
    { 
      value: 'processing', 
      label: 'Processing', 
      description: 'Order is being prepared for delivery',
      icon: 'play'
    },
    { 
      value: 'ready_for_delivery', 
      label: 'Ready for Delivery', 
      description: 'Order is ready to be picked up by driver',
      icon: 'package'
    },
    { 
      value: 'out_for_delivery', 
      label: 'Out for Delivery', 
      description: 'Order is being delivered to customer',
      icon: 'truck'
    },
    { 
      value: 'delivered', 
      label: 'Delivered', 
      description: 'Order has been successfully delivered',
      icon: 'check'
    },
    { 
      value: 'cancelled', 
      label: 'Cancelled', 
      description: 'Order has been cancelled',
      icon: 'x'
    },
    { 
      value: 'refunded', 
      label: 'Refunded', 
      description: 'Order has been refunded',
      icon: 'refresh'
    }
  ]
}

const getAvailableStatuses = (currentStatus) => {
  const statusFlow = {
    'pending': [
      { value: 'confirmed', label: 'Confirm Order', icon: 'check' },
      { value: 'cancelled', label: 'Cancel Order', icon: 'x' }
    ],
    'confirmed': [
      { value: 'processing', label: 'Start Processing', icon: 'play' },
      { value: 'cancelled', label: 'Cancel Order', icon: 'x' }
    ],
    'processing': [
      { value: 'ready_for_delivery', label: 'Ready for Delivery', icon: 'package' },
      { value: 'cancelled', label: 'Cancel Order', icon: 'x' }
    ],
    'ready_for_delivery': [
      { value: 'out_for_delivery', label: 'Out for Delivery', icon: 'truck' },
      { value: 'cancelled', label: 'Cancel Order', icon: 'x' }
    ],
    'out_for_delivery': [
      { value: 'delivered', label: 'Mark Delivered', icon: 'check' },
      { value: 'cancelled', label: 'Cancel Order', icon: 'x' }
    ],
    'delivered': [
      { value: 'refunded', label: 'Mark Refunded', icon: 'refresh' }
    ],
    'cancelled': [
      { value: 'pending', label: 'Reactivate Order', icon: 'refresh' }
    ],
    'refunded': []
  }
  
  return statusFlow[currentStatus] || []
}

const getStatusIcon = (status) => {
  const iconMap = {
    'pending': Clock,
    'confirmed': Check,
    'processing': Play,
    'ready_for_delivery': Package,
    'out_for_delivery': Truck,
    'delivered': Check,
    'cancelled': X,
    'refunded': RotateCcw
  }
  return iconMap[status] || Edit
}

const confirmOrderAction = async (orderId) => {
  try {
    await confirmOrder(orderId)
    toast.success('Order confirmed successfully')
    await fetchOrders()
  } catch (error) {
    console.error('Failed to confirm order:', error)
    toast.error('Failed to confirm order')
  }
}

const cancelOrderAction = async (orderId) => {
  try {
    const reason = prompt('Please provide a reason for cancellation:')
    if (reason !== null) {
      await cancelOrder(orderId, reason)
      toast.success('Order cancelled successfully')
      await fetchOrders()
    }
  } catch (error) {
    console.error('Failed to cancel order:', error)
    toast.error('Failed to cancel order')
  }
}

const assignDriver = async (orderId, driverId) => {
  try {
    await assignDriverToOrder(orderId, driverId)
    toast.success('Driver assigned successfully')
    showAssignDriverModal.value = false
    selectedOrder.value = null
    await fetchOrders()
  } catch (error) {
    console.error('Failed to assign driver:', error)
    toast.error('Failed to assign driver')
  }
}

const navigateToOrderReceipts = () => {
  router.push('/dashboard/order-receipts')
}

const navigateToInvoices = () => {
  router.push('/dashboard/invoices')
}

const navigateToReceipts = () => {
  router.push('/dashboard/receipts')
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchOrders()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchOrders()
  }
}

// Create Order Functions
const fetchProducts = async () => {
  try {
    const response = await getProducts()
    products.value = response.results || response
  } catch (error) {
    console.error('Failed to fetch products:', error)
    toast.error('Failed to load products')
  }
}

const fetchCustomers = async () => {
  try {
    const response = await getUsers()
    customers.value = response.results || response
  } catch (error) {
    console.error('Failed to fetch customers:', error)
    toast.error('Failed to load customers')
  }
}

const addOrderItem = () => {
  newOrder.value.items.push({ product_id: '', quantity: 1 })
}

const removeOrderItem = (index) => {
  if (newOrder.value.items.length > 1) {
    newOrder.value.items.splice(index, 1)
  }
}

const getProductName = (productId) => {
  const product = products.value.find(p => p.id === productId)
  return product ? product.name : 'Unknown Product'
}

const getProductPrice = (productId) => {
  const product = products.value.find(p => p.id == productId)
  if (!product || !product.price) return 0
  
  const price = parseFloat(product.price)
  return isNaN(price) ? 0 : price
}

const addEditingOrderItem = () => {
  editingOrder.value.items.push({ product_id: '', quantity: 1 })
}

const removeEditingOrderItem = (index) => {
  if (editingOrder.value.items.length > 1) {
    editingOrder.value.items.splice(index, 1)
  }
}

const calculateOrderTotal = () => {
  return newOrder.value.items.reduce((total, item) => {
    const price = getProductPrice(item.product_id)
    const quantity = parseInt(item.quantity) || 0
    return total + (price * quantity)
  }, 0)
}

const calculateOrderTotalWithFees = () => {
  const subtotal = calculateOrderTotal()
  const tax = 0 // 0% tax for now
  const deliveryFee = newOrder.value.is_pickup ? 0 : (newOrder.value.delivery_fee || 15000)
  const discount = 0 // No discount for now
  
  return subtotal + tax + deliveryFee - discount
}

const createOrderAction = async () => {
  creatingOrder.value = true
  try {
    // Filter out empty items
    const validItems = newOrder.value.items.filter(item => item.product_id && item.quantity > 0)
    
    if (validItems.length === 0) {
      toast.error('Please add at least one product to the order')
      return
    }

    // Validate required fields
    if (!newOrder.value.customer_name || !newOrder.value.customer_email) {
      toast.error('Please fill in customer name and email')
      return
    }

    // Calculate costs
    const subtotal = calculateOrderTotal()
    const tax = 0 // 0% tax for now
    const deliveryFee = newOrder.value.is_pickup ? 0 : (newOrder.value.delivery_fee || 15000)
    const discount = 0 // No discount for now
    const totalAmount = subtotal + tax + deliveryFee - discount

    const orderData = {
      customer_name: newOrder.value.customer_name,
      customer_email: newOrder.value.customer_email,
      customer_phone: newOrder.value.customer_phone || '',
      is_pickup: newOrder.value.is_pickup,
      items: validItems.map(item => ({
        product_id: parseInt(item.product_id),
        quantity: parseInt(item.quantity)
      })),
      delivery_address: newOrder.value.delivery_address || '',
      address_line1: newOrder.value.address_line1 || '',
      address_line2: newOrder.value.address_line2 || '',
      city: newOrder.value.city || '',
      district: newOrder.value.district || '',
      state: newOrder.value.state || '',
      postal_code: newOrder.value.postal_code || '',
      country: newOrder.value.country || '',
      notes: newOrder.value.notes || '',
      // Include calculated costs
      subtotal: subtotal,
      tax: tax,
      delivery_fee: deliveryFee,
      discount: discount,
      total_amount: totalAmount
    }

    console.log('Sending order data:', orderData)
    
    const response = await createOrder(orderData)
    console.log('Order created successfully:', response)
    
    toast.success('Order created successfully')
    showAddModal.value = false
    resetNewOrder()
    await fetchOrders()
  } catch (error) {
    console.error('Failed to create order:', error)
    console.error('Error details:', {
      message: error.message,
      response: error.response,
      status: error.status
    })
    
    let errorMessage = 'Failed to create order'
    
    // Check for specific error types
    if (error.response?.detail) {
      errorMessage = error.response.detail
    } else if (error.response?.message) {
      errorMessage = error.response.message
    } else if (error.message) {
      errorMessage = error.message
    }
    
    // Add more context for common errors
    if (error.status === 500) {
      errorMessage = 'Server error. Please check the backend logs.'
    } else if (error.status === 403) {
      errorMessage = 'Permission denied. Please check your authentication.'
    } else if (error.status === 400) {
      errorMessage = `Validation error: ${errorMessage}`
    }
    
    toast.error(errorMessage)
  } finally {
    creatingOrder.value = false
  }
}

const updateOrderDetails = async () => {
  try {
    updatingOrder.value = true
    
    // Only include items that have both product_id and quantity
    const validItems = editingOrder.value.items.filter(item => 
      item.product_id && item.quantity > 0
    )
    
    // Build complete order data for PUT request
    const orderData = {
      customer_name: editingOrder.value.customer_name || '',
      customer_email: editingOrder.value.customer_email || '',
      customer_phone: editingOrder.value.customer_phone || '',
      is_pickup: editingOrder.value.is_pickup,
      delivery_address: editingOrder.value.delivery_address || '',
      address_line1: editingOrder.value.address_line1 || '',
      address_line2: editingOrder.value.address_line2 || '',
      city: editingOrder.value.city || '',
      district: editingOrder.value.district || '',
      state: editingOrder.value.state || '',
      postal_code: editingOrder.value.postal_code || '',
      country: editingOrder.value.country || '',
      notes: editingOrder.value.notes || ''
    }
    
    // Include items if there are valid ones
    if (validItems.length > 0) {
      orderData.items = validItems.map(item => ({
        product_id: parseInt(item.product_id),
        quantity: parseInt(item.quantity)
      }))
    } else {
      orderData.items = []
    }

    // Calculate costs
    const subtotal = calculateEditingOrderTotal()
    const tax = 0 // 0% tax for now
    const deliveryFee = editingOrder.value.is_pickup ? 0 : (editingOrder.value.delivery_fee || 15000)
    const discount = 0 // No discount for now
    const totalAmount = subtotal + tax + deliveryFee - discount
    
    // Include calculated costs
    orderData.subtotal = subtotal
    orderData.tax = tax
    orderData.delivery_fee = deliveryFee
    orderData.discount = discount
    orderData.total_amount = totalAmount

    console.log('Sending updated order data:', orderData)
    
    const response = await updateOrder(editingOrder.value.id, orderData)
    console.log('Order updated successfully:', response)
    
    toast.success('Order updated successfully')
    showEditModal.value = false
    resetEditingOrder()
    await fetchOrders()
  } catch (error) {
    console.error('Failed to update order:', error)
    console.error('Error details:', {
      message: error.message,
      response: error.response,
      status: error.status
    })
    
    let errorMessage = 'Failed to update order'
    
    // Check for specific error types
    if (error.response?.detail) {
      errorMessage = error.response.detail
    } else if (error.response?.message) {
      errorMessage = error.response.message
    } else if (error.message) {
      errorMessage = error.message
    }
    
    // Add more context for common errors
    if (error.status === 500) {
      errorMessage = 'Server error. Please check the backend logs.'
    } else if (error.status === 403) {
      errorMessage = 'Permission denied. Please check your authentication.'
    } else if (error.status === 400) {
      errorMessage = `Validation error: ${errorMessage}`
    }
    
    toast.error(errorMessage)
  } finally {
    updatingOrder.value = false
  }
}

const updateCustomerDetails = () => {
  if (newOrder.value.customer_id) {
    const selectedCustomer = customers.value.find(c => c.id === newOrder.value.customer_id)
    if (selectedCustomer) {
      newOrder.value.customer_name = selectedCustomer.name || selectedCustomer.full_name || ''
      newOrder.value.customer_email = selectedCustomer.email || ''
      newOrder.value.customer_phone = selectedCustomer.phone_number || ''
    }
  }
}

const updateEditingCustomerDetails = () => {
  if (editingOrder.value.customer_id) {
    const selectedCustomer = customers.value.find(c => c.id === editingOrder.value.customer_id)
    if (selectedCustomer) {
      editingOrder.value.customer_name = selectedCustomer.name || selectedCustomer.full_name || ''
      editingOrder.value.customer_email = selectedCustomer.email || ''
      editingOrder.value.customer_phone = selectedCustomer.phone_number || ''
    }
  }
}

const resetNewOrder = () => {
  newOrder.value = {
    customer_id: '',
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    is_pickup: false,
    delivery_fee: 15000, // Default transportation fee (UGX)
    items: [{ product_id: '', quantity: 1 }],
    delivery_address: '',
    address_line1: '',
    address_line2: '',
    city: '',
    district: '',
    state: '',
    postal_code: '',
    country: '',
    notes: ''
  }
}

const resetEditingOrder = () => {
  editingOrder.value = {
    id: null,
    customer_id: '',
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    is_pickup: false,
    delivery_fee: 15000, // Default transportation fee (UGX)
    items: [{ product_id: '', quantity: 1 }],
    delivery_address: '',
    address_line1: '',
    address_line2: '',
    city: '',
    district: '',
    state: '',
    postal_code: '',
    country: '',
    notes: ''
  }
}

const calculateEditingOrderTotal = () => {
  return editingOrder.value.items.reduce((total, item) => {
    const price = getProductPrice(item.product_id)
    const quantity = parseInt(item.quantity) || 0
    return total + (price * quantity)
  }, 0)
}

const calculateEditingOrderTotalWithFees = () => {
  const subtotal = calculateEditingOrderTotal()
  const tax = 0 // 0% tax for now
  const deliveryFee = editingOrder.value.is_pickup ? 0 : (editingOrder.value.delivery_fee || 15000)
  const discount = 0 // No discount for now
  
  return subtotal + tax + deliveryFee - discount
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    fetchOrders(),
    fetchDrivers(),
    fetchOrderStats(),
    fetchProducts(),
    fetchCustomers()
  ])
  

})

const handlePaymentDone = async () => {
  await fetchOrders()
  await fetchOrderStats()
}
</script> 