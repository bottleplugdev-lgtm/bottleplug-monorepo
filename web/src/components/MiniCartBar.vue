<template>
	<div v-if="total_items > 0" class="bar">
		<div class="inner">
			<div class="summary">
				<strong>{{ total_items }}</strong>
				<span>items</span>
				<span class="sep">|</span>
				<strong>{{ format_amount(total_amount) }}</strong>
			</div>
			<div class="actions">
				<RouterLink to="/cart" class="btn">View Cart</RouterLink>
				<RouterLink to="/checkout" class="btn" style="background:#16a34a">Checkout</RouterLink>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { use_cart_store } from '../stores/cart'

const cart = use_cart_store()
const total_items = computed(() => cart.total_quantity)
const total_amount = computed(() => cart.total_amount)

function format_amount(value) {
	const amount = Number(value) || 0
	return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', minimumFractionDigits: 0 }).format(amount)
}
</script>

<style scoped>
.bar { position: fixed; left: 0; right: 0; bottom: 0; z-index: 40; padding: 8px; }
.inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 8px; background: #111827; color: #fff; border-radius: 12px; padding: 10px 12px; }
.summary { display: flex; align-items: center; gap: 8px; }
.sep { opacity: .6; }
.actions { display: flex; align-items: center; gap: 8px; }
</style>
