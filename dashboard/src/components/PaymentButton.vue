<template>
  <div class="payment-button">
    <button
      @click="openPaymentDialog"
      :disabled="loading || isFullyPaid"
      class="btn btn-primary"
      :class="{ 'opacity-50 cursor-not-allowed': isFullyPaid }"
    >
      <Wallet v-if="!loading && !isFullyPaid" class="h-4 w-4 mr-2" />
      <Check v-if="isFullyPaid" class="h-4 w-4 mr-2" />
      <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
      {{ computedButtonText }}
    </button>
    
    <!-- Payment Method Selection Dialog -->
    <div v-if="showPaymentDialog" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" aria-hidden="true">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <!-- Step 1: Payment Method Selection -->
          <div v-if="currentStep === 1" class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Select Payment Method</h3>
                
                <div class="space-y-3">
                  <!-- Cash Payment Option -->
                  <div
                    @click="selectPaymentMethod(cashMethod)"
                    class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-green-50 transition-colors"
                    :class="selectedPaymentMethod?.payment_type === 'cash' ? 'border-green-500 bg-green-50' : 'border-gray-200'"
                  >
                    <div class="flex-shrink-0">
                      <Wallet class="h-6 w-6 text-green-600" />
                    </div>
                    <div class="ml-3 flex-1">
                      <p class="text-sm font-medium text-gray-900">Cash Payment</p>
                      <p class="text-xs text-gray-500">Pay with cash on delivery</p>
                      <p class="text-xs text-green-600 font-medium">Unlimited amount</p>
                    </div>
                    <div class="flex-shrink-0">
                      <div v-if="selectedPaymentMethod?.payment_type === 'cash'" class="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                        <Check class="h-3 w-3 text-white" />
                      </div>
                    </div>
                  </div>

                  <!-- Mobile Money Option -->
                  <div
                    @click="selectPaymentMethod(mobileMoneyMethod)"
                    class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-blue-50 transition-colors"
                    :class="selectedPaymentMethod?.payment_type === 'mobile_money' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
                  >
                    <div class="flex-shrink-0">
                      <Smartphone class="h-6 w-6 text-blue-600" />
                    </div>
                    <div class="ml-3 flex-1">
                      <p class="text-sm font-medium text-gray-900">Mobile Money</p>
                      <p class="text-xs text-gray-500">MTN Mobile Money & Airtel Money</p>
                      <p class="text-xs text-blue-600 font-medium">Up to UGX 7,000,000</p>
                    </div>
                    <div class="flex-shrink-0">
                      <div v-if="selectedPaymentMethod?.payment_type === 'mobile_money'" class="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                        <Check class="h-3 w-3 text-white" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 2: Payment Details -->
          <div v-if="currentStep === 2" class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Payment Details</h3>
                
                <!-- Payment Status Summary -->
                <div v-if="paymentStatus && paymentStatus.success" class="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-sm font-medium text-gray-700">Payment Progress</span>
                    <span class="text-sm text-gray-600">{{ Math.round(paymentProgress) }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div 
                      class="bg-green-600 h-2 rounded-full transition-all duration-300" 
                      :style="{ width: `${paymentProgress}%` }"
                    ></div>
                  </div>
                  <div class="flex justify-between text-xs text-gray-500">
                    <span>Paid: {{ formatAmount(paymentStatus.total_paid) }}</span>
                    <span>Total: {{ formatAmount(paymentStatus.order_total) }}</span>
                  </div>
                </div>
                
                <!-- Fully Paid Notice -->
                <div v-if="isFullyPaid" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div class="flex items-center">
                    <Check class="h-5 w-5 text-green-600 mr-2" />
                    <div>
                      <h4 class="text-sm font-medium text-green-800">Order Fully Paid</h4>
                      <p class="text-sm text-green-600 mt-1">
                        This order has been completely paid. No additional payment is required.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div class="space-y-4">
                  <div class="flex justify-between">
                    <span class="text-sm text-gray-600">Amount to Pay:</span>
                    <div class="flex items-center space-x-2">
                      <span class="text-sm font-semibold text-gray-900">{{ formatAmount(editableAmount) }}</span>
                      <button 
                        v-if="!isFullyPaid"
                        @click="showAmountEditor = !showAmountEditor"
                        class="text-xs text-blue-600 hover:text-blue-800 underline"
                      >
                        Edit
                      </button>
                    </div>
                  </div>
                  
                  <!-- Amount Limits Info -->
                  <div v-if="selectedPaymentMethod" class="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                    <div class="flex justify-between">
                      <span>Min: {{ formatAmount(selectedPaymentMethod.min_amount || 0) }}</span>
                      <span v-if="selectedPaymentMethod.max_amount">Max: {{ formatAmount(selectedPaymentMethod.max_amount) }}</span>
                      <span v-else>Max: Unlimited</span>
                    </div>
                  </div>
                  
                  <!-- Amount Editor -->
                  <div v-if="showAmountEditor" class="p-3 bg-gray-50 rounded-lg">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Payment Amount</label>
                    <div class="flex items-center space-x-2">
                      <span class="text-sm text-gray-600">{{ currency }}</span>
                      <input
                        v-model.number="editableAmount"
                        type="number"
                        :min="selectedPaymentMethod?.min_amount || 0"
                        :max="selectedPaymentMethod?.max_amount || undefined"
                        step="0.01"
                        class="form-input flex-1"
                        placeholder="Enter amount"
                      />
                    </div>
                    <div class="mt-2 text-xs text-gray-500">
                      Original amount: {{ formatAmount(amount) }}
                    </div>
                    <div v-if="selectedPaymentMethod" class="mt-1 text-xs text-blue-600">
                      {{ selectedPaymentMethod.max_amount ? `Max: ${formatAmount(selectedPaymentMethod.max_amount)}` : 'Unlimited amount' }}
                    </div>
                  </div>

                  <!-- Cash Payment Details -->
                  <div v-if="selectedPaymentMethod?.payment_type === 'cash'" class="space-y-3">
                    <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div class="flex items-center">
                        <Wallet class="h-5 w-5 text-green-600 mr-2" />
                        <div>
                          <h4 class="text-sm font-medium text-green-800">Cash on Delivery</h4>
                          <p class="text-sm text-green-600 mt-1">
                            Pay with cash when your order is delivered. No additional details required.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Mobile Money Details -->
                  <div v-if="selectedPaymentMethod?.payment_type === 'mobile_money'" class="space-y-3">
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div class="flex items-center mb-3">
                        <Smartphone class="h-5 w-5 text-blue-600 mr-2" />
                        <div>
                          <h4 class="text-sm font-medium text-blue-800">Mobile Money Payment</h4>
                          <p class="text-sm text-blue-600">Enter your mobile money details</p>
                        </div>
                      </div>
                      
                      <!-- Network Selection -->
                      <div class="mb-3">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Mobile Network</label>
                        <select 
                          v-model="paymentDetails.network" 
                          class="form-select w-full"
                          required
                        >
                          <option value="">Select network</option>
                          <option value="mtn">MTN Mobile Money</option>
                          <option value="airtel">Airtel Money</option>
                        </select>
                      </div>
                      
                      <!-- Phone Number -->
                      <div class="mb-3">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                        <div class="flex">
                          <span class="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm">
                            +256
                          </span>
                          <input
                            v-model="paymentDetails.phone_number"
                            type="tel"
                            class="form-input rounded-none rounded-r-md flex-1"
                            placeholder="7XXXXXXXX"
                            required
                          />
                        </div>
                        <p class="text-xs text-gray-500 mt-1">Enter your mobile money registered phone number</p>
                      </div>
                      
                      <!-- Payment Instructions -->
                      <div class="bg-yellow-50 border border-yellow-200 rounded p-3">
                        <div class="flex">
                          <div class="flex-shrink-0">
                            <AlertCircle class="h-4 w-4 text-yellow-400" />
                          </div>
                          <div class="ml-3">
                            <p class="text-xs text-yellow-800">
                              You will receive a push notification on your phone to authorize this payment.
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 3: Payment Confirmation -->
          <div v-if="currentStep === 3" class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Confirm Payment</h3>
                
                <div class="space-y-4">
                  <div class="text-center">
                    <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                      <component :is="selectedPaymentMethod?.payment_type === 'cash' ? Wallet : Smartphone" class="h-6 w-6 text-blue-600" />
                    </div>
                    <h3 class="mt-2 text-sm font-medium text-gray-900">Ready to Pay</h3>
                    <p class="mt-1 text-sm text-gray-500" v-if="selectedPaymentMethod?.payment_type !== 'cash'">
                      You will be redirected to {{ selectedPaymentMethod?.name }} to complete your payment.
                    </p>
                    <p class="mt-1 text-sm text-gray-500" v-else>
                      Your order will be processed for cash on delivery payment.
                    </p>
                  </div>
                  
                  <div class="bg-gray-50 p-3 rounded-lg">
                    <div class="flex justify-between text-sm">
                      <span class="text-gray-600">Total Amount:</span>
                      <span class="font-semibold text-gray-900">{{ formatAmount(editableAmount) }}</span>
                    </div>
                    <div class="flex justify-between text-sm mt-1">
                      <span class="text-gray-600">Payment Method:</span>
                      <span class="font-semibold text-gray-900">{{ selectedPaymentMethod?.name }}</span>
                    </div>
                    <div v-if="selectedPaymentMethod?.payment_type === 'mobile_money'" class="flex justify-between text-sm mt-1">
                      <span class="text-gray-600">Network:</span>
                      <span class="font-semibold text-gray-900">{{ paymentDetails.network?.toUpperCase() }}</span>
                    </div>
                    <div v-if="selectedPaymentMethod?.payment_type === 'mobile_money'" class="flex justify-between text-sm mt-1">
                      <span class="text-gray-600">Phone:</span>
                      <span class="font-semibold text-gray-900">+256{{ paymentDetails.phone_number }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Dialog Footer -->
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
              v-if="currentStep === 1"
                @click="nextStep"
                :disabled="!selectedPaymentMethod"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue
              </button>
              <button
              v-if="currentStep === 2"
                @click="nextStep"
              :disabled="!validatePaymentDetails"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
              Continue
              </button>
              <button
              v-if="currentStep === 3"
                @click="initiatePaymentAction"
                :disabled="loading"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
              <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              {{ loading ? 'Processing...' : 'Confirm Payment' }}
              </button>
              <button
                @click="previousStep"
              v-if="currentStep > 1"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                Back
              </button>
            <button
              @click="closePaymentDialog"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Wallet, Smartphone, Check, AlertCircle } from 'lucide-vue-next'
import { toast } from 'vue3-toastify'
import { initiatePayment, completeMobileMoneyPayment, getPaymentMethods, checkOrderPaymentStatus } from '@/services/api'

const props = defineProps({
  amount: {
    type: Number,
    required: true
  },
  currency: {
    type: String,
    default: 'UGX'
  },
  description: {
    type: String,
    default: 'Payment'
  },
  transactionType: {
    type: String,
    required: true
  },
  entityId: {
    type: Number,
    required: true
  },
  buttonText: {
    type: String,
    default: 'Pay Now'
  }
})

const emit = defineEmits(['payment_done'])
const loading = ref(false)
const showPaymentDialog = ref(false)
const currentStep = ref(1)
const selectedPaymentMethod = ref(null)
const paymentUrl = ref('')
const editableAmount = ref(0)
const showAmountEditor = ref(false)
const paymentMethods = ref([])
const loadingPaymentMethods = ref(false)

// Payment status tracking
const paymentStatus = ref(null)
const loadingPaymentStatus = ref(false)

// Payment details
const paymentDetails = ref({
  phone_number: '',
  network: ''
})

// Load payment methods from backend
const loadPaymentMethods = async () => {
  try {
    loadingPaymentMethods.value = true
    const methods = await getPaymentMethods()
    paymentMethods.value = methods.results || methods
    console.log('Loaded payment methods:', paymentMethods.value)
  } catch (error) {
    console.error('Failed to load payment methods:', error)
    // Fallback to hardcoded methods if API fails
    paymentMethods.value = [
      {
        id: 3,
        name: 'Cash Payment',
        payment_type: 'cash',
        description: 'Pay with cash on delivery',
        max_amount: null,
        min_amount: 0
      },
      {
        id: 2,
        name: 'Mobile Money',
        payment_type: 'mobile_money',
        description: 'MTN Mobile Money & Airtel Money',
        max_amount: 7000000,
        min_amount: 100
      }
    ]
  } finally {
    loadingPaymentMethods.value = false
  }
}

// Load payment status for the order
const loadPaymentStatus = async () => {
  if (props.transactionType !== 'order') return
  
  try {
    loadingPaymentStatus.value = true
    const status = await checkOrderPaymentStatus(props.entityId)
    paymentStatus.value = status
    console.log('Payment status loaded:', status)
    
    // Update editable amount based on remaining amount
    if (status.success) {
      const remainingAmount = status.order_total - status.total_paid
      editableAmount.value = Math.max(0, remainingAmount)
    }
  } catch (error) {
    console.error('Failed to load payment status:', error)
    // Set default amount if status loading fails
    editableAmount.value = props.amount
  } finally {
    loadingPaymentStatus.value = false
  }
}

// Get payment method by type
const getPaymentMethodByType = (type) => {
  return paymentMethods.value.find(method => method.payment_type === type)
}

// Cash and mobile money methods for UI
const cashMethod = computed(() => getPaymentMethodByType('cash'))
const mobileMoneyMethod = computed(() => getPaymentMethodByType('mobile_money'))

// Computed properties for payment status display
const remainingAmount = computed(() => {
  if (!paymentStatus.value || !paymentStatus.value.success) {
    return props.amount
  }
  return Math.max(0, paymentStatus.value.order_total - paymentStatus.value.total_paid)
})

const isFullyPaid = computed(() => {
  return paymentStatus.value?.success && paymentStatus.value.is_paid
})

const paymentProgress = computed(() => {
  if (!paymentStatus.value || !paymentStatus.value.success) {
    return 0
  }
  return Math.min(100, (paymentStatus.value.total_paid / paymentStatus.value.order_total) * 100)
})

// Computed button text based on payment status
const computedButtonText = computed(() => {
  if (loading.value) return 'Processing...'
  
  // If order is fully paid, show different text
  if (isFullyPaid.value) {
    return 'Order Fully Paid'
  }
  
  // If there's partial payment, show remaining amount
  if (paymentStatus.value?.success && paymentStatus.value.total_paid > 0) {
    const remaining = remainingAmount.value
    if (remaining > 0) {
      return `Pay Remaining ${formatAmount(remaining)}`
    }
  }
  
  // Default button text
  return props.buttonText
})

// Load payment methods and status on component mount
onMounted(() => {
  loadPaymentMethods()
  loadPaymentStatus()
})

const formatAmount = (amount) => {
  return new Intl.NumberFormat('en-UG', {
    style: 'currency',
    currency: 'UGX',
    minimumFractionDigits: 0
  }).format(amount)
}

const validatePaymentDetails = computed(() => {
  const method = selectedPaymentMethod.value
  
  // Validate amount
  if (!editableAmount.value || editableAmount.value <= 0) {
    return false
  }
  
  // Check minimum amount
  if (method?.min_amount && editableAmount.value < method.min_amount) {
    return false
  }
  
  // Check maximum amount (except for cash which is unlimited)
  if (method?.max_amount && editableAmount.value > method.max_amount) {
      return false
    }
  
  // Validate mobile money details
  if (method?.payment_type === 'mobile_money') {
    if (!paymentDetails.value.network || !paymentDetails.value.phone_number) {
      return false
    }
    
    // Validate phone number format (Uganda format)
    const phoneRegex = /^[7-9]\d{8}$/
    if (!phoneRegex.test(paymentDetails.value.phone_number)) {
      return false
    }
  }
  
  return true
})

const resetPaymentDetails = () => {
  paymentDetails.value = {
    phone_number: '',
    network: ''
  }
}

const openPaymentDialog = () => {
  showPaymentDialog.value = true
  currentStep.value = 1
  selectedPaymentMethod.value = null
  if (editableAmount.value === 0) {
    editableAmount.value = props.amount
  }
  showAmountEditor.value = false
  resetPaymentDetails()
}

const closePaymentDialog = () => {
  showPaymentDialog.value = false
  currentStep.value = 1
  selectedPaymentMethod.value = null
  showAmountEditor.value = false
  resetPaymentDetails()
}

const selectPaymentMethod = async (method) => {
  selectedPaymentMethod.value = method
  
  // Load payment status when a payment method is selected for order transactions
  if (props.transactionType === 'order') {
    await loadPaymentStatus()
  }
}

const nextStep = () => {
  // Prevent proceeding if order is fully paid
  if (isFullyPaid.value) {
    toast.info('Order is already fully paid. No additional payment is required.')
    return
  }
  
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const initiatePaymentAction = async () => {
  try {
    // Prevent payment if order is fully paid
    if (isFullyPaid.value) {
      toast.info('Order is already fully paid. No additional payment is required.')
      return
    }
    
    console.log('Payment button clicked')
    console.log('Payment data:', {
      transaction_type: props.transactionType,
      amount: props.amount,
      currency: props.currency,
      description: props.description,
      entityId: props.entityId,
      payment_method: selectedPaymentMethod.value,
      payment_details: paymentDetails.value
    })
    
    loading.value = true
    
    // Handle mobile money payments with complete flow
    if (selectedPaymentMethod.value?.payment_type === 'mobile_money') {
      try {
        // Generate unique email for testing
        const timestamp = Date.now()
        const randomId = Math.random().toString(36).substr(2, 9)
        
        // Prepare data for complete mobile money flow
        const completePaymentData = {
          customer_data: {
            email: `customer_${timestamp}_${randomId}@example.com`, // Unique email for each payment
            name: {
              first: 'Customer',
              last: 'User'
            },
            phone: {
              country_code: '256',
              number: paymentDetails.value.phone_number
            }
          },
          mobile_money_data: {
            country_code: '256',
            network: paymentDetails.value.network,
            phone_number: paymentDetails.value.phone_number
          },
          charge_data: {
            amount: editableAmount.value,
            currency: props.currency,
            reference: `payment_${timestamp}_${randomId}`
          }
        }
        
        // Add entity ID based on transaction type
        switch (props.transactionType) {
          case 'order':
            completePaymentData.order_id = props.entityId
            break
          case 'invoice':
            completePaymentData.invoice_id = props.entityId
            break
          case 'event':
            completePaymentData.event_id = props.entityId
            break
          case 'receipt':
            completePaymentData.receipt_id = props.entityId
            break
        }
        
        console.log('Complete mobile money payment data:', completePaymentData)
        
        const response = await completeMobileMoneyPayment(completePaymentData)
        console.log('Complete mobile money payment response:', response)
        
        if (response && response.success) {
          const data = response.data
          
          if (data.next_action?.type === 'payment_instruction') {
            // Show payment instructions to user
            toast.success('Payment instructions received')
            alert(`Payment Instructions: ${data.note}`)
            closePaymentDialog()
          } else if (data.next_action?.type === 'redirect_url') {
            // Redirect to payment page
            toast.success('Redirecting to payment page')
            if (data.redirect_url) {
              window.open(data.redirect_url, '_blank')
            }
            closePaymentDialog()
          } else {
            // Payment completed successfully
            toast.success('Mobile money payment completed successfully!')
            closePaymentDialog()
            emit('payment_done', { order_id: props.entityId, transaction_type: props.transactionType, payment_method: selectedPaymentMethod.value?.payment_type })
          }
        } else {
          const errorMessage = response?.error || 'Failed to complete mobile money payment'
          console.error('Mobile money payment failed:', errorMessage)
          toast.error(errorMessage)
        }
      } catch (apiError) {
        console.error('Complete mobile money API call failed:', apiError)
        if (apiError.message?.includes('401') || apiError.message?.includes('403')) {
          toast.error('Authentication required. Please log in again.')
        } else {
          toast.error(`Mobile money payment failed: ${apiError.message || 'Unknown error'}`)
        }
      }
      return
    }
    
    // Handle cash payments with existing flow
    const paymentData = {
      transaction_type: props.transactionType,
      amount: editableAmount.value,
      currency: props.currency,
      description: props.description,
      payment_details: paymentDetails.value,
      payment_method_id: selectedPaymentMethod.value?.id
    }
    
    // Add entity ID based on transaction type
    switch (props.transactionType) {
      case 'order':
        paymentData.order_id = props.entityId
        break
      case 'invoice':
        paymentData.invoice_id = props.entityId
        break
      case 'event':
        paymentData.event_id = props.entityId
        break
      case 'receipt':
        paymentData.receipt_id = props.entityId
        break
    }
    
    console.log('Sending payment data:', paymentData)
    
    try {
      const response = await initiatePayment(paymentData)
      console.log('Payment response:', response)
      
      if (response && response.success) {
        if (selectedPaymentMethod.value?.payment_type === 'cash') {
          // Handle cash payment success
          toast.success(response.message || 'Cash payment confirmed!')
          closePaymentDialog()
          emit('payment_done', { order_id: props.entityId, transaction_type: props.transactionType, payment_method: selectedPaymentMethod.value?.payment_type })
        } else {
          // Handle mobile money payment success
          paymentUrl.value = response.payment_url
          toast.success('Payment initiated successfully')
          
          // Open payment URL in new window
          if (paymentUrl.value) {
            window.open(paymentUrl.value, '_blank')
          }
          
          closePaymentDialog()
        }
      } else {
        const errorMessage = response?.error || 'Failed to initiate payment'
        console.error('Payment failed:', errorMessage)
        toast.error(errorMessage)
      }
    } catch (apiError) {
      console.error('API call failed:', apiError)
      if (apiError.message?.includes('401') || apiError.message?.includes('403')) {
        toast.error('Authentication required. Please log in again.')
      } else {
        toast.error(`Payment failed: ${apiError.message || 'Unknown error'}`)
      }
    }
  } catch (error) {
    console.error('Payment initiation error:', error)
    toast.error('Failed to initiate payment')
  } finally {
    loading.value = false
  }
}
</script> 