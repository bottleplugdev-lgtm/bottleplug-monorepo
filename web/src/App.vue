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
import { onMounted } from 'vue'

const router = useRouter()

function go_to_login() {
	router.push({ name: 'login' })
}

// Ensure page scrolls to top on mount (handles page reload)
onMounted(() => {
	// Immediate scroll to top for page reloads
	window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
	
	// Also handle any delayed scroll issues
	setTimeout(() => {
		window.scrollTo({ top: 0, left: 0, behavior: 'smooth' })
	}, 100)
})
</script>

<style>
body { 
	font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
	/* Ensure page starts at top on reload */
	scroll-behavior: smooth;
}

/* Ensure html and body start at top */
html, body {
	scroll-behavior: smooth;
}

/* Reset scroll position on page load */
html {
	scroll-behavior: auto;
}
</style>
