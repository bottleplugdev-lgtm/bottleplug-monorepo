<template>
	<div class="min-h-screen bg-cream-50 text-neutral-900">
		<AppHeader @sign_in="go_to_login" @sign_up="go_to_login" />
		<main class="max-w-screen-xl mx-auto px-4 py-6">
			<router-view />
		</main>
		<MiniCartBar />
		<AppFooter />
	</div>
</template>

<script setup>
import AppHeader from './components/layout/Header.vue'
import AppFooter from './components/layout/Footer.vue'
import { useRouter } from 'vue-router'
import MiniCartBar from './components/MiniCartBar.vue'

const router = useRouter()

function go_to_login() {
	router.push({ name: 'login' })
}
</script>

<style>
body { font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
</style>
