<template>
	<div class="card p-4">
		<div class="text-lg font-semibold mb-2">Order Summary</div>
		<div class="row" style="justify-content:space-between"><span>Subtotal</span><strong>{{ format_price(subtotal) }}</strong></div>
		<div class="row" style="justify-content:space-between"><span>Delivery</span><strong>{{ format_price(delivery_fee) }}</strong></div>
		<div class="row" style="justify-content:space-between" v-if="coupon_discount > 0"><span>Coupon</span><strong class="text-green-700">-{{ format_price(coupon_discount) }}</strong></div>
		<hr class="my-2" />
		<div class="row" style="justify-content:space-between"><span>Total</span><strong>{{ format_price(total) }}</strong></div>
		<slot />
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	subtotal: { type: Number, default: 0 },
	delivery_fee: { type: Number, default: 0 },
	coupon_discount: { type: Number, default: 0 }
})

const total = computed(() => Math.max(0, Number(props.subtotal || 0) + Number(props.delivery_fee || 0) - Number(props.coupon_discount || 0)))

function format_price(value) {
	const amount = Number(value) || 0
	return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', minimumFractionDigits: 0 }).format(amount)
}
</script>

<style scoped>
.row { display: flex; align-items: center; }
</style>

