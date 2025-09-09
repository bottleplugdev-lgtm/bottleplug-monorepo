<template>
	<div class="page_container card p-6">
		<h1 class="text-2xl font-bold mb-2">Processing Payment...</h1>
		<p v-if="message">{{ message }}</p>
		<div class="mt-3" v-if="status === 'failed'">
			<button class="retry_btn" @click="retry">Try Again</button>
		</div>
	</div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { verify_payment } from '../services/api'
import { set_seo } from '../lib/seo'

const router = useRouter()
const route = useRoute()
const message = ref('')
const status = ref('verifying') // verifying | waiting | failed | success
let current_timeout = null

onMounted(async () => {
	const tx = route.query.transaction_id || route.query.tx_id || ''
	if (!tx) {
		message.value = 'Missing transaction information.'
		return
	}
	let attempts = 0
	async function poll() {
		attempts += 1
		try {
			const res = await verify_payment(tx)
			if (res?.success && res?.verified) {
				message.value = 'Payment verified successfully.'
				const order_id = res?.order_id || ''
				setTimeout(() => router.replace(order_id ? { name: 'order_success', params: { id: order_id } } : { name: 'account' }), 900)
				status.value = 'success'
				return
			}
		} catch (_) {}
		if (attempts < 6) {
			message.value = 'Waiting for payment confirmation...'
			status.value = 'waiting'
			current_timeout = setTimeout(poll, 1500)
		} else {
			message.value = 'Payment not confirmed yet.'
			status.value = 'failed'
		}
	}
	poll()
	set_seo({ title: 'Payment Status · Bottleplug', description: 'Verifying your payment. This may take a moment.' })
})

function retry() {
	if (current_timeout) clearTimeout(current_timeout)
	message.value = 'Retrying verification...'
	status.value = 'verifying'
	// restart flow by reloading route to trigger onMounted
	window.location.reload()
}
</script>

<style scoped>
.page_container { padding: 24px; }
.retry_btn { background: #111827; color: #fff; border: 0; padding: 8px 12px; border-radius: 8px; cursor: pointer; }
</style>
