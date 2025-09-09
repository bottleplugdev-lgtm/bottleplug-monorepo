<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-800">Events</h1>
        <p class="text-secondary-600">Manage and track events</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="openCreateModal"
          class="btn btn-primary"
        >
          <Plus class="h-4 w-4" />
          New Event
        </button>
      </div>
    </div>

    <!-- Event Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Calendar class="h-8 w-8 text-primary-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Total Events</p>
            <p class="text-2xl font-bold text-secondary-800">{{ eventSummary.total }}</p>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Clock class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Upcoming (published)</p>
            <p class="text-2xl font-bold text-blue-600">{{ eventSummary.upcoming }}</p>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <Play class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Ongoing</p>
            <p class="text-2xl font-bold text-green-600">{{ eventSummary.ongoing }}</p>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CheckCircle class="h-8 w-8 text-gray-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-secondary-600">Completed</p>
            <p class="text-2xl font-bold text-gray-600">{{ eventSummary.completed }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Event Status Pie Chart -->
      <div class="card p-4">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">Event Status Distribution</h3>
        <div class="h-80">
          <canvas ref="pieChartRef"></canvas>
        </div>
      </div>

      <!-- Monthly Events Line Chart -->
      <div class="card p-4">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">Monthly Events</h3>
        <div class="h-80">
          <canvas ref="lineChartRef"></canvas>
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
            placeholder="Search events..."
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
            <option value="draft">Draft</option>
            <option value="published">Published</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <select
            v-model="typeFilter"
            class="px-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @change="handleFilter"
          >
            <option value="">All Types</option>
            <option value="tasting">Wine Tasting</option>
            <option value="dinner">Wine Dinner</option>
            <option value="class">Wine Class</option>
            <option value="tour">Vineyard Tour</option>
            <option value="party">Wine Party</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Events Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-secondary-200">
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Event</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Type</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Date & Time</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Location</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Attendees</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Status</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading" class="border-b border-secondary-100">
              <td colspan="7" class="py-8 px-4 text-center">
                <div class="flex items-center justify-center">
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                  <span class="ml-2 text-secondary-600">Loading events...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="filteredEvents.length === 0" class="border-b border-secondary-100">
              <td colspan="7" class="py-8 px-4 text-center text-secondary-600">
                No events found
              </td>
            </tr>
            <tr
              v-for="event in filteredEvents"
              :key="event.id"
              class="border-b border-secondary-100 hover:bg-secondary-50"
            >
              <td class="py-4 px-4">
                <div class="flex items-center gap-3">
                  <img v-if="event.image" :src="buildMediaUrl(event.image)" alt="event image" class="h-10 w-10 rounded object-cover" />
                  <div>
                    <h4 class="font-medium text-secondary-800">{{ event.title }}</h4>
                    <p class="text-sm text-secondary-600">{{ event.description }}</p>
                  </div>
                </div>
              </td>
              <td class="py-4 px-4">
                <span class="px-2 py-1 bg-secondary-100 text-secondary-700 rounded-full text-sm">
                  {{ event.event_type }}
                </span>
              </td>
              <td class="py-4 px-4">
                <div>
                  <p class="font-medium text-secondary-800">{{ formatDate(event.start_date) }}</p>
                  <p class="text-sm text-secondary-600">{{ formatTimeFromDateTime(event.start_date) }} - {{ formatTimeFromDateTime(event.end_date) }}</p>
                </div>
              </td>
              <td class="py-4 px-4">
                <span class="text-secondary-700">{{ event.location_name }}</span>
              </td>
              <td class="py-4 px-4">
                <span class="text-secondary-700">{{ event.current_attendees || 0 }} / {{ event.max_capacity }}</span>
              </td>
              <td class="py-4 px-4">
                <span :class="[
                  'px-2 py-1 rounded-full text-sm font-medium',
                  getStatusClass(event.status)
                ]">
                  {{ event.status }}
                </span>
              </td>
              <td class="py-4 px-4">
                <div class="flex items-center space-x-2">
                  <button
                    @click="viewEvent(event.id)"
                    class="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="View"
                  >
                    <Eye class="h-4 w-4" />
                  </button>
                  <button
                    @click="openEditModal(event.id)"
                    class="p-2 text-secondary-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Edit"
                  >
                    <Edit class="h-4 w-4" />
                  </button>
                  <button
                    @click="deleteEvent(event.id)"
                    class="p-2 text-secondary-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && filteredEvents.length > 0" class="flex items-center justify-between">
      <p class="text-sm text-secondary-600">
        Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalEvents) }} of {{ totalEvents }} events
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

    <!-- Create/Edit Event Modal -->
    <div v-if="showAddModal" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black bg-opacity-50" @click="closeEventModal"></div>
      <div class="relative bg-white rounded-lg shadow-xl w-full max-w-4xl p-6 max-h-[85vh] overflow-y-auto">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">{{ isEditMode ? 'Edit Event' : 'Create Event' }}</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm text-secondary-700 mb-1">Title</label>
            <input v-model="eventForm.title" type="text" class="form-input w-full" placeholder="Event title" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm text-secondary-700 mb-1">Description</label>
            <textarea v-model="eventForm.description" class="form-input w-full" rows="3" placeholder="Description"></textarea>
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Type</label>
            <select v-model="eventForm.event_type" class="form-input w-full">
              <option disabled value="">Select type</option>
              <option value="tasting">Wine Tasting</option>
              <option value="dinner">Wine Dinner</option>
              <option value="class">Wine Class</option>
              <option value="tour">Vineyard Tour</option>
              <option value="party">Wine Party</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Status</label>
            <select v-model="eventForm.status" class="form-input w-full">
              <option disabled value="">Select status</option>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Start Date</label>
            <input v-model="eventForm.start_date" type="date" class="form-input w-full" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Start Time</label>
            <input v-model="eventForm.start_time" type="time" class="form-input w-full" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">End Date</label>
            <input v-model="eventForm.end_date" type="date" class="form-input w-full" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">End Time</label>
            <input v-model="eventForm.end_time" type="time" class="form-input w-full" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Location Name</label>
            <input v-model="eventForm.location_name" type="text" class="form-input w-full" placeholder="Location name" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">City</label>
            <input v-model="eventForm.city" type="text" class="form-input w-full" placeholder="City" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">State</label>
            <input v-model="eventForm.state" type="text" class="form-input w-full" placeholder="State" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">ZIP Code</label>
            <input v-model="eventForm.zip_code" type="text" class="form-input w-full" placeholder="ZIP Code" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm text-secondary-700 mb-1">Address</label>
            <input v-model="eventForm.address" type="text" class="form-input w-full" placeholder="Street address" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Max Capacity</label>
            <input v-model.number="eventForm.max_capacity" type="number" min="0" class="form-input w-full" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Price</label>
            <input v-model.number="eventForm.price" type="number" min="0" step="0.01" class="form-input w-full" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Member Price (optional)</label>
            <input v-model.number="eventForm.member_price" type="number" min="0" step="0.01" class="form-input w-full" />
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Age Requirement</label>
            <input v-model.number="eventForm.age_requirement" type="number" min="0" class="form-input w-full" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm text-secondary-700 mb-1">Featured Wines</label>
            <textarea v-model="eventForm.featured_wines" class="form-input w-full" rows="2" placeholder="Comma-separated list or description"></textarea>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm text-secondary-700 mb-1">Food Pairings</label>
            <textarea v-model="eventForm.food_pairings" class="form-input w-full" rows="2" placeholder="Comma-separated list or description"></textarea>
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Dress Code</label>
            <input v-model="eventForm.dress_code" type="text" class="form-input w-full" placeholder="e.g. Smart Casual" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm text-secondary-700 mb-1">Meta Description</label>
            <textarea v-model="eventForm.meta_description" class="form-input w-full" rows="2" placeholder="SEO description"></textarea>
          </div>
          <div>
            <label class="block text-sm text-secondary-700 mb-1">Main Image</label>
            <input type="file" accept="image/*" class="form-input w-full" @change="onImageChange" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm text-secondary-700 mb-1">Gallery Images</label>
            <input type="file" accept="image/*" multiple class="form-input w-full" @change="onGalleryChange" />
            <p class="text-xs text-secondary-500 mt-1">You can select multiple images</p>
          </div>
        </div>
        <div v-if="formError" class="mt-3 text-sm text-red-600">{{ formError }}</div>
        <div class="mt-6 flex justify-end gap-2">
          <button @click="closeEventModal" class="btn btn-outline">Cancel</button>
          <button @click="submitEvent" class="btn btn-primary" :disabled="submitting">
            <span v-if="submitting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2 inline-block"></span>
            {{ isEditMode ? 'Save Changes' : 'Create Event' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Event Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black bg-opacity-50" @click="closeDetailsModal"></div>
      <div class="relative bg-white rounded-lg shadow-xl w-full max-w-2xl p-6 max-h-[85vh] overflow-y-auto">
        <h3 class="text-lg font-semibold text-secondary-800 mb-4">Event Details</h3>
        <div v-if="selectedEvent" class="space-y-4">
          <div class="flex justify-between"><span class="text-secondary-600">Title</span><span class="font-medium">{{ selectedEvent.title }}</span></div>
          <div class="flex justify-between"><span class="text-secondary-600">Type</span><span class="font-medium">{{ selectedEvent.event_type }}</span></div>
          <div class="flex justify-between"><span class="text-secondary-600">Status</span><span class="font-medium">{{ selectedEvent.status }}</span></div>
          <div class="flex justify-between"><span class="text-secondary-600">Date</span><span class="font-medium">{{ formatDate(selectedEvent.start_date) }} - {{ formatDate(selectedEvent.end_date) }}</span></div>
          <div class="flex justify-between"><span class="text-secondary-600">Time</span><span class="font-medium">{{ formatTimeFromDateTime(selectedEvent.start_date) }} - {{ formatTimeFromDateTime(selectedEvent.end_date) }}</span></div>
          <div class="flex justify-between"><span class="text-secondary-600">Location</span><span class="font-medium">{{ selectedEvent.location_name }}, {{ selectedEvent.city }}, {{ selectedEvent.state }}</span></div>
          <div><span class="text-secondary-600 block">Description</span><p class="mt-1">{{ selectedEvent.description }}</p></div>
          <div class="flex justify-between"><span class="text-secondary-600">Capacity</span><span class="font-medium">{{ selectedEvent.current_attendees || 0 }} / {{ selectedEvent.max_capacity }}</span></div>
          <div class="flex justify-between"><span class="text-secondary-600">Price</span><span class="font-medium">{{ selectedEvent.price }}</span></div>
          <div v-if="selectedEvent.featured_wines"><span class="text-secondary-600 block">Featured Wines</span><p class="mt-1">{{ selectedEvent.featured_wines }}</p></div>
          <div v-if="selectedEvent.food_pairings"><span class="text-secondary-600 block">Food Pairings</span><p class="mt-1">{{ selectedEvent.food_pairings }}</p></div>
          <div v-if="selectedEvent.dress_code" class="flex justify-between"><span class="text-secondary-600">Dress Code</span><span class="font-medium">{{ selectedEvent.dress_code }}</span></div>
          <div v-if="selectedEvent.meta_description"><span class="text-secondary-600 block">Meta Description</span><p class="mt-1">{{ selectedEvent.meta_description }}</p></div>
          <div v-if="selectedEvent.image" class="mt-2"><img :src="buildMediaUrl(selectedEvent.image)" class="w-full max-h-64 object-cover rounded" /></div>

          <!-- Gallery -->
          <div v-if="selectedEvent.gallery && selectedEvent.gallery.length" class="mt-4">
            <div class="text-secondary-600 mb-2">Gallery ({{ selectedEvent.gallery.length }})</div>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
              <div v-for="(g, idx) in selectedEvent.gallery" :key="idx" class="rounded overflow-hidden border border-secondary-100">
                <img :src="buildMediaUrl(g)" class="w-full h-28 object-cover" />
              </div>
            </div>
          </div>

          <!-- RSVPs -->
          <div v-if="selectedEvent.rsvp_count !== undefined" class="mt-4">
            <div class="flex items-center justify-between">
              <div class="text-secondary-600">RSVPs</div>
              <div class="flex items-center gap-2">
                <div class="text-sm text-secondary-700">Total: <span class="font-medium">{{ selectedEvent.rsvp_count }}</span></div>
                <button @click="addRSVP" class="btn btn-sm btn-primary">Add RSVP</button>
              </div>
            </div>
            <div v-if="selectedEvent.rsvps && selectedEvent.rsvps.length" class="mt-2 border border-secondary-100 rounded">
              <div class="grid grid-cols-3 text-xs font-medium text-secondary-600 px-3 py-2 border-b border-secondary-100">
                <div>User</div>
                <div>Status</div>
                <div class="text-right">Guests</div>
              </div>
              <div v-for="r in selectedEvent.rsvps" :key="r.id" class="grid grid-cols-3 text-sm px-3 py-2 border-b last:border-b-0 border-secondary-100 items-center">
                <div class="truncate" :title="r.user">{{ r.user }}</div>
                <div>
                  <div v-if="!r._editing" class="flex items-center gap-2">
                    <span class="capitalize">{{ r.status }}</span>
                    <button class="btn btn-xs btn-outline" @click="startEditRSVP(r)">Edit</button>
                  </div>
                  <div v-else class="flex items-center gap-2">
                    <select v-model="r._editing_status" class="form-input form-input-sm">
                      <option value="pending">pending</option>
                      <option value="confirmed">confirmed</option>
                      <option value="attended">attended</option>
                      <option value="no_show">no_show</option>
                      <option value="cancelled">cancelled</option>
                    </select>
                    <button class="btn btn-xs btn-primary" @click="saveRSVPStatus(r)">Save</button>
                    <button class="btn btn-xs btn-outline" @click="cancelRSVPEdit(r)">Cancel</button>
                  </div>
                </div>
                <div class="text-right">{{ r.guest_count }}</div>
              </div>
            </div>
            <div v-else class="text-sm text-secondary-500 mt-1">No RSVPs yet</div>
          </div>
        </div>
        <div class="mt-6 flex justify-end">
          <button @click="closeDetailsModal" class="btn btn-outline">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { toast } from 'vue3-toastify'
import { 
  Plus, 
  Edit, 
  Eye, 
  Trash2,
  Calendar,
  Clock,
  Play,
  CheckCircle
} from 'lucide-vue-next'
import { Chart, registerables } from 'chart.js'
import {
  getEvents,
  getEvent as getEventAPI,
  createEvent as createEventAPI,
  updateEvent as updateEventAPI,
  deleteEvent as deleteEventAPI,
  createRSVP as createRSVPAPI,
  updateRSVP as updateRSVPAPI
} from '@/services/api'

Chart.register(...registerables)

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const BACKEND_ORIGIN = API_BASE_URL.replace(/\/api\/v1\/?$/, '')
const buildMediaUrl = (path) => {
  if (!path) return ''
  if (typeof path !== 'string') return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (path.startsWith('/')) return `${BACKEND_ORIGIN}${path}`
  return `${BACKEND_ORIGIN}/${path}`
}

// Simple slugify util (ASCII, lower_case, underscored)
const slugify = (text) =>
  String(text || '')
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9_\s]/g, '')
    .replace(/\s+/g, '_')
    .replace(/_+/g, '_')

// State
const loading = ref(false)
const events = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const showAddModal = ref(false)
const isEditMode = ref(false)
const submitting = ref(false)
const formError = ref('')
const imageFile = ref(null)
const galleryFiles = ref([])

const eventForm = ref({
  id: null,
  title: '',
  description: '',
  event_type: '',
  status: 'draft',
  start_date: '', // yyyy_mm_dd
  start_time: '', // HH:mm
  end_date: '',   // yyyy_mm_dd
  end_time: '',   // HH:mm
  location_name: '',
  address: '',
  city: '',
  state: '',
  zip_code: '',
  max_capacity: null,
  price: 0,
  member_price: null,
  age_requirement: 21,
  featured_wines: '',
  food_pairings: '',
  dress_code: '',
  meta_description: '',
  slug: ''
})
const showDetailsModal = ref(false)
const selectedEvent = ref(null)

const currentPage = ref(1)
const pageSize = ref(10)
const totalEvents = ref(0)
const pieChartRef = ref(null)
const lineChartRef = ref(null)
let pieChart = null
let lineChart = null

// Computed
const filteredEvents = computed(() => {
  let filtered = events.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(event =>
      (event.title || '').toLowerCase().includes(query) ||
      (event.description || '').toLowerCase().includes(query) ||
      (event.location_name || '').toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(event => event.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(event => event.event_type === typeFilter.value)
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(totalEvents.value / pageSize.value || 1))

const eventSummary = computed(() => {
  const total = events.value.length
  const now = new Date()
  const upcoming = events.value.filter(e => e.is_upcoming === true).length
  const ongoing = events.value.filter(e => {
    const sd = e.start_date ? new Date(e.start_date) : null
    const ed = e.end_date ? new Date(e.end_date) : null
    return e.status === 'published' && sd && ed && sd <= now && now <= ed
  }).length
  const completed = events.value.filter(e => e.status === 'completed').length
  return { total, upcoming, ongoing, completed }
})

// Chart data computations
const pieChartData = computed(() => {
  const statusCounts = {
    draft: events.value.filter(event => event.status === 'draft').length,
    published: events.value.filter(event => event.status === 'published').length,
    completed: events.value.filter(event => event.status === 'completed').length,
    cancelled: events.value.filter(event => event.status === 'cancelled').length
  }

  return {
    labels: ['Draft', 'Published', 'Completed', 'Cancelled'],
    datasets: [{
      data: [
        statusCounts.draft,
        statusCounts.published,
        statusCounts.completed,
        statusCounts.cancelled
      ],
      backgroundColor: [
        '#A78BFA',
        '#3B82F6',
        '#6B7280',
        '#EF4444'
      ],
      borderWidth: 2,
      borderColor: '#ffffff'
    }]
  }
})

const lineChartData = computed(() => {
  const months = []
  const eventCounts = []
  for (let i = 5; i >= 0; i--) {
    const date = new Date()
    date.setMonth(date.getMonth() - i)
    const monthStr = date.toISOString().slice(0, 7)
    months.push(date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }))
    const monthEvents = events.value.filter(event => (event.start_date || '').startsWith(monthStr))
    eventCounts.push(monthEvents.length)
  }
  return {
    labels: months,
    datasets: [
      {
        label: 'Events',
        data: eventCounts,
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  }
})

// Helpers
const buildDateTime = (datePart, timePart) => {
  if (!datePart) return ''
  const time = timePart && timePart.length > 0 ? timePart : '00:00'
  const dt = new Date(`${datePart}T${time}`)
  return isNaN(dt.getTime()) ? '' : dt.toISOString()
}

const splitToDateAndTime = (isoString) => {
  if (!isoString) return { date: '', time: '' }
  const d = new Date(isoString)
  if (isNaN(d.getTime())) return { date: '', time: '' }
  const pad = (n) => (n < 10 ? `0${n}` : `${n}`)
  return {
    date: `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`,
    time: `${pad(d.getHours())}:${pad(d.getMinutes())}`
  }
}

const parseGalleryUrls = (text) => {
  if (!text) return []
  return text
    .split(/\n|,/)
    .map(s => s.trim())
    .filter(s => s.length > 0)
}

// Methods
const fetchEvents = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (statusFilter.value) params.status = statusFilter.value
    if (typeFilter.value) params.event_type = typeFilter.value
    if (searchQuery.value) params.search = searchQuery.value

    const response = await getEvents(params)
    events.value = response.results || response
    totalEvents.value = response.count || response.length || 0
    updateCharts()
  } catch (error) {
    console.error('Failed to fetch events:', error)
    toast.error('Failed to load events')
  } finally {
    loading.value = false
  }
}

const refreshEvents = async () => {
  await fetchEvents()
}

const handleSearch = () => {
  currentPage.value = 1
  fetchEvents()
}

const handleFilter = () => {
  currentPage.value = 1
  fetchEvents()
}

const getStatusClass = (status) => {
  switch ((status || '').toLowerCase()) {
    case 'draft':
      return 'bg-violet-100 text-violet-800'
    case 'published':
      return 'bg-blue-100 text-blue-800'
    case 'completed':
      return 'bg-gray-100 text-gray-800'
    case 'cancelled':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-secondary-100 text-secondary-800'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  if (isNaN(d.getTime())) return 'N/A'
  return d.toLocaleDateString()
}

const formatTimeFromDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  if (isNaN(d.getTime())) return 'N/A'
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const onImageChange = (e) => {
  const files = e.target.files
  imageFile.value = files && files[0] ? files[0] : null
}

const onGalleryChange = (e) => {
  const files = Array.from(e.target.files || [])
  galleryFiles.value = files
}

const openCreateModal = () => {
  isEditMode.value = false
  formError.value = ''
  imageFile.value = null
  galleryFiles.value = []
  eventForm.value = {
    id: null,
    title: '',
    description: '',
    event_type: '',
    status: 'draft',
    start_date: '',
    start_time: '',
    end_date: '',
    end_time: '',
    location_name: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    max_capacity: null,
    price: 0,
    member_price: null,
    age_requirement: 21,
    featured_wines: '',
    food_pairings: '',
    dress_code: '',
    meta_description: '',
    slug: ''
  }
  showAddModal.value = true
}

const openEditModal = async (eventId) => {
  try {
    const data = await getEventAPI(eventId)
    isEditMode.value = true
    formError.value = ''
    imageFile.value = null
    galleryFiles.value = []
    const sd = splitToDateAndTime(data.start_date)
    const ed = splitToDateAndTime(data.end_date)
    eventForm.value = {
      id: data.id,
      title: data.title || '',
      description: data.description || '',
      event_type: data.event_type || '',
      status: data.status || 'draft',
      start_date: sd.date,
      start_time: sd.time,
      end_date: ed.date,
      end_time: ed.time,
      location_name: data.location_name || '',
      address: data.address || '',
      city: data.city || '',
      state: data.state || '',
      zip_code: data.zip_code || '',
      max_capacity: data.max_capacity ?? null,
      price: Number(data.price ?? 0),
      member_price: data.member_price != null ? Number(data.member_price) : null,
      age_requirement: data.age_requirement ?? 21,
      featured_wines: data.featured_wines || '',
      food_pairings: data.food_pairings || '',
      dress_code: data.dress_code || '',
      meta_description: data.meta_description || '',
      slug: data.slug || ''
    }
    showAddModal.value = true
  } catch (e) {
    toast.error('Failed to load event for editing')
  }
}

const closeEventModal = () => {
  showAddModal.value = false
}

const validateEventForm = () => {
  if (!eventForm.value.title) return 'Title is required'
  if (!eventForm.value.description) return 'Description is required'
  if (!eventForm.value.event_type) return 'Type is required'
  if (!eventForm.value.start_date) return 'Start date is required'
  if (!eventForm.value.end_date) return 'End date is required'
  if (!eventForm.value.location_name) return 'Location name is required'
  if (!eventForm.value.address) return 'Address is required'
  if (!eventForm.value.city) return 'City is required'
  if (!eventForm.value.state) return 'State is required'
  if (!eventForm.value.zip_code) return 'ZIP code is required'
  if (eventForm.value.max_capacity == null) return 'Max capacity is required'
  // end must be after start if both provided
  const startIso = buildDateTime(eventForm.value.start_date, eventForm.value.start_time)
  const endIso = buildDateTime(eventForm.value.end_date, eventForm.value.end_time)
  if (startIso && endIso && new Date(endIso) < new Date(startIso)) return 'End date/time must be after start date/time'
  return ''
}

const submitEvent = async () => {
  formError.value = validateEventForm()
  if (formError.value) return
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('title', eventForm.value.title)
    fd.append('description', eventForm.value.description)
    fd.append('event_type', eventForm.value.event_type)
    fd.append('status', eventForm.value.status)
    fd.append('start_date', buildDateTime(eventForm.value.start_date, eventForm.value.start_time))
    fd.append('end_date', buildDateTime(eventForm.value.end_date, eventForm.value.end_time))
    fd.append('location_name', eventForm.value.location_name)
    fd.append('address', eventForm.value.address)
    fd.append('city', eventForm.value.city)
    fd.append('state', eventForm.value.state)
    fd.append('zip_code', eventForm.value.zip_code)
    fd.append('max_capacity', String(eventForm.value.max_capacity ?? '0'))
    fd.append('price', String(eventForm.value.price ?? '0'))
    if (eventForm.value.member_price != null) fd.append('member_price', String(eventForm.value.member_price))
    fd.append('age_requirement', String(eventForm.value.age_requirement ?? '21'))
    if (eventForm.value.featured_wines) fd.append('featured_wines', eventForm.value.featured_wines)
    if (eventForm.value.food_pairings) fd.append('food_pairings', eventForm.value.food_pairings)
    if (eventForm.value.dress_code) fd.append('dress_code', eventForm.value.dress_code)
    if (eventForm.value.meta_description) fd.append('meta_description', eventForm.value.meta_description)

    // Slug: on create, generate unique-ish with underscore suffix; on edit, keep existing slug
    if (!isEditMode.value) {
      const base = slugify(eventForm.value.title)
      fd.append('slug', `${base}_${Date.now()}`)
    }

    if (galleryFiles.value && galleryFiles.value.length > 0) {
      galleryFiles.value.forEach((file) => fd.append('gallery', file))
    }

    if (imageFile.value) {
      fd.append('image', imageFile.value)
    }

    if (isEditMode.value && eventForm.value.id) {
      await updateEventAPI(eventForm.value.id, fd)
      toast.success('Event updated successfully')
    } else {
      await createEventAPI(fd)
      toast.success('Event created successfully')
    }
    showAddModal.value = false
    await fetchEvents()
  } catch (e) {
    console.error('Failed to submit event:', e)
    const detail = (e && e.response) ? JSON.stringify(e.response) : (e?.message || 'Failed to save event')
    formError.value = detail
    toast.error('Failed to save event')
  } finally {
    submitting.value = false
  }
}

const viewEvent = async (eventId) => {
  try {
    const data = await getEventAPI(eventId)
    // initialize inline editor values
    if (data && Array.isArray(data.rsvps)) {
      data.rsvps = data.rsvps.map(x => ({ ...x, _editing_status: x.status, _editing: false }))
    }
    selectedEvent.value = data
    showDetailsModal.value = true
  } catch (e) {
    console.error('Failed to load event details:', e)
    toast.error('Failed to load event details')
  }
}

const addRSVP = async () => {
  try {
    if (!selectedEvent.value?.id) return
    await createRSVPAPI({ event: selectedEvent.value.id, guest_count: 1 })
    toast.success('RSVP added')
    // Refresh details
    const data = await getEventAPI(selectedEvent.value.id)
    if (data && Array.isArray(data.rsvps)) {
      data.rsvps = data.rsvps.map(x => ({ ...x, _editing_status: x.status, _editing: false }))
    }
    selectedEvent.value = data
  } catch (e) {
    console.error('Failed to create RSVP:', e)
    toast.error('Failed to add RSVP')
  }
}

const startEditRSVP = (rsvp) => {
  rsvp._editing = true
  if (!rsvp._editing_status) rsvp._editing_status = rsvp.status
}

const cancelRSVPEdit = (rsvp) => {
  rsvp._editing = false
  rsvp._editing_status = rsvp.status
}

const saveRSVPStatus = async (rsvp) => {
  try {
    if (!rsvp?.id) return
    await updateRSVPAPI(rsvp.id, { status: rsvp._editing_status })
    toast.success('RSVP updated')
    const data = await getEventAPI(selectedEvent.value.id)
    if (data && Array.isArray(data.rsvps)) {
      data.rsvps = data.rsvps.map(x => ({ ...x, _editing_status: x.status, _editing: false }))
    }
    selectedEvent.value = data
  } catch (e) {
    console.error('Failed to update RSVP:', e)
    toast.error('Failed to update RSVP')
  }
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedEvent.value = null
}

const deleteEvent = async (eventId) => {
  if (!confirm('Are you sure you want to delete this event?')) return
  try {
    await deleteEventAPI(eventId)
    toast.success('Event deleted successfully')
    await fetchEvents()
  } catch (error) {
    console.error('Failed to delete event:', error)
    toast.error('Failed to delete event')
  }
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchEvents()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchEvents()
  }
}

// Chart functions
const initPieChart = () => {
  if (pieChart) {
    pieChart.destroy()
  }
  const ctx = pieChartRef.value.getContext('2d')
  pieChart = new Chart(ctx, {
    type: 'pie',
    data: pieChartData.value,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { padding: 20, usePointStyle: true, font: { size: 12 } }
        }
      }
    }
  })
}

const initLineChart = () => {
  if (lineChart) {
    lineChart.destroy()
  }
  const ctx = lineChartRef.value.getContext('2d')
  lineChart = new Chart(ctx, {
    type: 'line',
    data: lineChartData.value,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { usePointStyle: true, font: { size: 12 } } }
      },
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
      interaction: { mode: 'nearest', axis: 'x', intersect: false }
    }
  })
}

const updateCharts = () => {
  nextTick(() => {
    if (pieChart) { pieChart.data = pieChartData.value; pieChart.update() }
    if (lineChart) { lineChart.data = lineChartData.value; lineChart.update() }
  })
}

// Lifecycle
onMounted(async () => {
  await fetchEvents()
  nextTick(() => { initPieChart(); initLineChart() })
})
</script> 