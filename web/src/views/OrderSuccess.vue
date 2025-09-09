<template>
	<div class="page_container card p-6">
		<h1 class="text-2xl font-bold mb-2">Thank you!</h1>
		<p>Your order <strong>#{{ order_id }}</strong> has been placed successfully.</p>
		<div class="mt-4">
			<RouterLink to="/account" class="btn">View Orders</RouterLink>
			<RouterLink to="/products" class="btn" style="margin-left:8px">Continue Shopping</RouterLink>
		</div>
	</div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { onMounted } from 'vue'
const route = useRoute()
const order_id = route.params.id

onMounted(() => {
	if (window?.gtag) window.gtag('event', 'purchase', { transaction_id: order_id })
})
</script>

<style scoped>
.page_container { padding: 24px; }
</style>
