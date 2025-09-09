<template>
	<div class="ribbon card p-4 overflow-x-auto">
		<div class="inner">
			<button v-for="c in categories" :key="c.id" class="chip" @click="$emit('select', c)">{{ c.name }}</button>
		</div>
	</div>
</template>

<script setup>
defineProps({ categories: { type: Array, default: () => [] } })
defineEmits(['select'])
</script>

<style scoped>
.inner { display: flex; gap: 8px; }
.chip { background: #f7e680; color: #111827; border: 0; padding: 8px 12px; border-radius: 999px; white-space: nowrap; }
.chip:hover { background: #f4dc4d; }
</style>
