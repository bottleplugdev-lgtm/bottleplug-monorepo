<template>
  <div class="space-y-8 md:space-y-10">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        title="Total Revenue"
        :value="`$${dashboardStore.totalRevenue.toLocaleString()}`"
        :change="12.5"
        icon="DollarSign"
        color="green"
        :loading="dashboardStore.loading"
      />
      <StatCard
        title="Total Orders"
        :value="dashboardStore.totalOrders.toLocaleString()"
        :change="8.2"
        icon="ShoppingCart"
        color="blue"
        :loading="dashboardStore.loading"
      />
      <StatCard
        title="Total Products"
        :value="dashboardStore.totalProducts.toLocaleString()"
        :change="15.3"
        icon="Package"
        color="purple"
        :loading="dashboardStore.loading"
      />
      <StatCard
        title="Total Users"
        :value="dashboardStore.totalUsers.toLocaleString()"
        :change="5.7"
        icon="Users"
        color="orange"
        :loading="dashboardStore.loading"
      />
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-10">
      <!-- Sales Chart -->
      <div class="card p-6 md:p-8">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-secondary-800">Sales Overview</h3>
          <div class="flex items-center gap-2">
            <select
              v-model="timePeriod"
              @change="refreshCharts"
              class="px-2 py-1 border border-secondary-200 rounded text-sm"
              :disabled="dashboardStore.loading"
            >
              <option :value="7">7d</option>
              <option :value="30">30d</option>
              <option :value="90">90d</option>
            </select>
            <button
              @click="refreshCharts"
              class="btn btn-sm btn-outline"
              :disabled="dashboardStore.loading"
            >
              <RefreshCw v-if="dashboardStore.loading" class="h-4 w-4 animate-spin" />
              <RefreshCw v-else class="h-4 w-4" />
              Refresh
            </button>
          </div>
        </div>
        <SalesChart
          :data="dashboardStore.salesData" 
          :loading="dashboardStore.loading"
        />
      </div>

      <!-- Order Status Chart -->
      <div class="card p-6 md:p-8">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-secondary-800">Order Status</h3>
          <div class="flex items-center gap-2">
            <select
              v-model="timePeriod"
              @change="refreshCharts"
              class="px-2 py-1 border border-secondary-200 rounded text-sm"
              :disabled="dashboardStore.loading"
            >
              <option :value="7">7d</option>
              <option :value="30">30d</option>
              <option :value="90">90d</option>
            </select>
          </div>
        </div>
        <OrderStatusChart
          :data="dashboardStore.orderStatusData" 
          :loading="dashboardStore.loading"
        />
      </div>
    </div>

    <!-- Recent Activity Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-10">
      <!-- Recent Orders -->
      <div class="card p-6 md:p-8">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-secondary-800">Recent Orders</h3>
          <router-link to="/dashboard/orders" class="btn btn-sm btn-outline">
            View All
          </router-link>
        </div>
        <RecentOrdersList
          :orders="dashboardStore.recentOrders" 
          :loading="dashboardStore.loading"
        />
      </div>

      <!-- Top Products -->
      <div class="card p-6 md:p-8">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-secondary-800">Top Products</h3>
          <router-link to="/dashboard/products" class="btn btn-sm btn-outline">
            View All
          </router-link>
        </div>
        <TopProductsList
          :products="dashboardStore.topProducts" 
          :loading="dashboardStore.loading"
        />
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card p-6 md:p-8">
      <h3 class="text-lg font-semibold text-secondary-800 mb-4">Quick Actions</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
        <QuickActionCard
          title="Add Product"
          description="Create new product"
          icon="Plus"
          color="green"
          @click="$router.push('/dashboard/products')"
        />
        <QuickActionCard
          title="New Order"
          description="Create order"
          icon="ShoppingCart"
          color="blue"
          @click="$router.push('/dashboard/orders')"
        />
        <QuickActionCard
          title="Add Event"
          description="Create event"
          icon="Calendar"
          color="purple"
          @click="$router.push('/dashboard/events')"
        />
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import StatCard from '@/components/StatCard.vue'
import SalesChart from '@/components/charts/SalesChart.vue'
import OrderStatusChart from '@/components/charts/OrderStatusChart.vue'
import RecentOrdersList from '@/components/dashboard/RecentOrdersList.vue'
import TopProductsList from '@/components/dashboard/TopProductsList.vue'
import QuickActionCard from '@/components/dashboard/QuickActionCard.vue'
import { RefreshCw } from 'lucide-vue-next'

const dashboardStore = useDashboardStore()
const timePeriod = ref(30)

const refreshCharts = async () => {
  await dashboardStore.fetchDashboardData(timePeriod.value)
}

onMounted(async () => {
  // Load dashboard data when component mounts
  await dashboardStore.fetchDashboardData(timePeriod.value)
})
</script> 