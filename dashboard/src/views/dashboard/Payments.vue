<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Payments</h1>
        <p class="mt-1 text-sm text-gray-500">Mobile Money Payment Integration</p>
      </div>
    </div>

    <!-- Payment Statistics -->
    <PaymentStats />

    <!-- Payment History -->
    <PaymentHistory />
  </div>
</template>

<script setup>
import PaymentHistory from '@/components/PaymentHistory.vue'
import PaymentStats from '@/components/PaymentStats.vue'
</script> 