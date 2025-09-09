<template>
	<div class="auth_loading">
		<div class="loading_container">
			<div class="loading_spinner"></div>
			<p class="loading_text">Loading your account...</p>
		</div>
	</div>
</template>

<script setup>
// This component is used to show loading state while auth is being determined
</script>

<style scoped>
.auth_loading {
	display: flex;
	justify-content: center;
	align-items: center;
	min-height: 60vh;
	background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.loading_container {
	text-align: center;
	padding: 2rem;
	background: white;
	border-radius: 12px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.loading_spinner {
	width: 40px;
	height: 40px;
	border: 4px solid #f3f3f3;
	border-top: 4px solid #8b5cf6;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin: 0 auto 1rem;
}

.loading_text {
	color: #6b7280;
	font-size: 1.1rem;
	font-weight: 500;
	margin: 0;
}

@keyframes spin {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}
</style>
