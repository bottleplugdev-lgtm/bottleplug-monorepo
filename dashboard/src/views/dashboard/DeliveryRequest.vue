<template>
  <div class="delivery-request">
    <div class="header">
      <h1 class="text-2xl font-bold text-gray-900">New Delivery Request</h1>
      <p class="text-gray-600">Create a new delivery request for customers</p>
    </div>

    <div class="content">
      <form @submit.prevent="createDelivery" class="space-y-6">
        <!-- Customer Selection -->
        <div class="form-group">
          <label for="customer" class="form-label">Customer</label>
          <select
            id="customer"
            v-model="form.customerId"
            class="form-select"
            required
          >
            <option value="">Select a customer</option>
            <option
              v-for="customer in customers"
              :key="customer.id"
              :value="customer.id"
            >
              {{ customer.fullName }} - {{ customer.email }}
            </option>
          </select>
        </div>

        <!-- Pickup Location -->
        <div class="form-group">
          <label for="pickupAddress" class="form-label">Pickup Address</label>
          <textarea
            id="pickupAddress"
            v-model="form.pickupAddress"
            class="form-textarea"
            rows="3"
            placeholder="Enter pickup address"
            required
          ></textarea>
        </div>

        <!-- Pickup Coordinates -->
        <div class="grid grid-cols-2 gap-4">
          <div class="form-group">
            <label for="pickupLatitude" class="form-label">Pickup Latitude</label>
            <input
              id="pickupLatitude"
              v-model.number="form.pickupLatitude"
              type="number"
              step="any"
              class="form-input"
              placeholder="0.000000"
              required
            />
          </div>
          <div class="form-group">
            <label for="pickupLongitude" class="form-label">Pickup Longitude</label>
            <input
              id="pickupLongitude"
              v-model.number="form.pickupLongitude"
              type="number"
              step="any"
              class="form-input"
              placeholder="0.000000"
              required
            />
          </div>
        </div>

        <!-- Delivery Location -->
        <div class="form-group">
          <label for="deliveryAddress" class="form-label">Delivery Address</label>
          <textarea
            id="deliveryAddress"
            v-model="form.deliveryAddress"
            class="form-textarea"
            rows="3"
            placeholder="Enter delivery address"
            required
          ></textarea>
        </div>

        <!-- Delivery Coordinates -->
        <div class="grid grid-cols-2 gap-4">
          <div class="form-group">
            <label for="deliveryLatitude" class="form-label">Delivery Latitude</label>
            <input
              id="deliveryLatitude"
              v-model.number="form.deliveryLatitude"
              type="number"
              step="any"
              class="form-input"
              placeholder="0.000000"
              required
            />
          </div>
          <div class="form-group">
            <label for="deliveryLongitude" class="form-label">Delivery Longitude</label>
            <input
              id="deliveryLongitude"
              v-model.number="form.deliveryLongitude"
              type="number"
              step="any"
              class="form-input"
              placeholder="0.000000"
              required
            />
          </div>
        </div>

        <!-- Package Details -->
        <div class="form-group">
          <label for="amount" class="form-label">Package Value ($)</label>
          <input
            id="amount"
            v-model.number="form.amount"
            type="number"
            step="0.01"
            min="0"
            class="form-input"
            placeholder="0.00"
            required
          />
        </div>

        <!-- Payment Method -->
        <div class="form-group">
          <label class="form-label">Payment Method</label>
          <div class="grid grid-cols-3 gap-4">
            <label class="payment-option">
              <input
                type="radio"
                v-model="form.paymentMethod"
                value="cash"
                class="sr-only"
              />
              <div class="payment-card">
                <div class="payment-icon">💵</div>
                <div class="payment-text">
                  <div class="payment-title">Cash</div>
                  <div class="payment-subtitle">Pay on delivery</div>
                </div>
              </div>
            </label>
            <label class="payment-option">
              <input
                type="radio"
                v-model="form.paymentMethod"
                value="card"
                class="sr-only"
              />
              <div class="payment-card">
                <div class="payment-icon">💳</div>
                <div class="payment-text">
                  <div class="payment-title">Card</div>
                  <div class="payment-subtitle">Credit/Debit card</div>
                </div>
              </div>
            </label>
            <label class="payment-option">
              <input
                type="radio"
                v-model="form.paymentMethod"
                value="mobile_money"
                class="sr-only"
              />
              <div class="payment-card">
                <div class="payment-icon">📱</div>
                <div class="payment-text">
                  <div class="payment-title">Mobile Money</div>
                  <div class="payment-subtitle">Mobile payment</div>
                </div>
              </div>
            </label>
          </div>
        </div>

        <!-- Notes -->
        <div class="form-group">
          <label for="notes" class="form-label">Notes (Optional)</label>
          <textarea
            id="notes"
            v-model="form.notes"
            class="form-textarea"
            rows="3"
            placeholder="Add any special instructions"
          ></textarea>
        </div>

        <!-- Package Items -->
        <div class="form-group">
          <label class="form-label">Package Items</label>
          <div class="space-y-2">
            <div
              v-for="(item, index) in form.items"
              :key="index"
              class="flex gap-2"
            >
              <input
                v-model="item.name"
                type="text"
                class="form-input flex-1"
                placeholder="Item name"
              />
              <input
                v-model.number="item.quantity"
                type="number"
                min="1"
                class="form-input w-20"
                placeholder="Qty"
              />
              <input
                v-model.number="item.value"
                type="number"
                step="0.01"
                min="0"
                class="form-input w-24"
                placeholder="Value"
              />
              <button
                type="button"
                @click="removeItem(index)"
                class="btn btn-danger"
              >
                Remove
              </button>
            </div>
            <button
              type="button"
              @click="addItem"
              class="btn btn-secondary"
            >
              Add Item
            </button>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="form-actions">
          <button
            type="submit"
            :disabled="loading"
            class="btn btn-primary"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? 'Creating Delivery...' : 'Create Delivery Request' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { collection, getDocs, addDoc, serverTimestamp } from 'firebase/firestore'
import { db } from '@/firebase/config'

export default {
  name: 'DeliveryRequest',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const customers = ref([])

    const form = reactive({
      customerId: '',
      pickupAddress: '',
      pickupLatitude: null,
      pickupLongitude: null,
      deliveryAddress: '',
      deliveryLatitude: null,
      deliveryLongitude: null,
      amount: 0,
      paymentMethod: 'cash',
      notes: '',
      items: []
    })

    // Load customers
    const loadCustomers = async () => {
      try {
        const customersRef = collection(db, 'users')
        const snapshot = await getDocs(customersRef)
        customers.value = snapshot.docs
          .map(doc => ({ id: doc.id, ...doc.data() }))
          .filter(user => user.userType === 'customer')
      } catch (error) {
        console.error('Error loading customers:', error)
      }
    }

    // Add item to package
    const addItem = () => {
      form.items.push({
        name: '',
        quantity: 1,
        value: 0
      })
    }

    // Remove item from package
    const removeItem = (index) => {
      form.items.splice(index, 1)
    }

    // Create delivery
    const createDelivery = async () => {
      if (!form.customerId) {
        alert('Please select a customer')
        return
      }

      loading.value = true

      try {
        const deliveryData = {
          customerId: form.customerId,
          pickupAddress: form.pickupAddress,
          pickupLatitude: form.pickupLatitude,
          pickupLongitude: form.pickupLongitude,
          deliveryAddress: form.deliveryAddress,
          deliveryLatitude: form.deliveryLatitude,
          deliveryLongitude: form.deliveryLongitude,
          amount: form.amount,
          paymentMethod: form.paymentMethod,
          paymentStatus: 'pending',
          notes: form.notes,
          items: form.items.filter(item => item.name && item.quantity > 0),
          status: 'pending',
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp()
        }

        const deliveriesRef = collection(db, 'deliveries')
        await addDoc(deliveriesRef, deliveryData)

        alert('Delivery request created successfully!')
        router.push('/dashboard/orders')
      } catch (error) {
        console.error('Error creating delivery:', error)
        alert('Error creating delivery request: ' + error.message)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadCustomers()
      addItem() // Add one initial item
    })

    return {
      form,
      loading,
      customers,
      addItem,
      removeItem,
      createDelivery
    }
  }
}
</script>

<style scoped>
.delivery-request {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.15s ease-in-out;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.payment-option {
  cursor: pointer;
}

.payment-card {
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  text-align: center;
  transition: all 0.15s ease-in-out;
}

.payment-option input:checked + .payment-card {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.payment-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.payment-title {
  font-weight: 600;
  color: #374151;
}

.payment-subtitle {
  font-size: 0.75rem;
  color: #6b7280;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #4b5563;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-danger:hover:not(:disabled) {
  background-color: #dc2626;
}

.form-actions {
  text-align: center;
  margin-top: 2rem;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style> 