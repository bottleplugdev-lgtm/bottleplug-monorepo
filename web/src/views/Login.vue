<template>
	<div class="auth_page">
		<!-- Hero Section -->
		<section class="hero_section">
			<div class="hero_background"></div>
			<div class="hero_content">
				<h1 class="hero_title">Welcome Back</h1>
				<p class="hero_subtitle">Sign in to access your premium wine and spirit collection</p>
			</div>
		</section>

		<!-- Auth Section -->
		<section class="auth_section">
			<div class="auth_container">
				<div class="auth_card">
					<div class="auth_header">
						<div class="auth_logo">
							<img src="/bottleplug_logo_new.png" alt="BottlePlug" class="logo_img" />
						</div>
						<h2 class="auth_title">Sign In</h2>
						<p class="auth_subtitle">Access your account to continue shopping</p>
					</div>

					<!-- Loading State -->
					<div v-if="is_initializing" class="loading_state">
						<div class="loading_spinner"></div>
						<p class="loading_text">Initializing authentication...</p>
					</div>

					<!-- Auth Forms -->
					<div v-else class="auth_content">
						<!-- Email/Password Form -->
						<form class="auth_form" @submit.prevent="handle_email_login">
							<div class="form_group">
								<label class="form_label">Email Address</label>
								<div class="input_wrapper">
									<span class="input_icon">📧</span>
									<input 
										class="form_input" 
										v-model="email" 
										type="email" 
										required 
										autocomplete="email"
										placeholder="Enter your email"
									/>
								</div>
							</div>

							<div class="form_group">
								<label class="form_label">Password</label>
								<div class="input_wrapper">
									<span class="input_icon">🔒</span>
									<input 
										class="form_input" 
										v-model="password" 
										type="password" 
										required 
										autocomplete="current-password"
										placeholder="Enter your password"
									/>
								</div>
							</div>

							<button type="submit" class="primary_btn" :disabled="is_submitting">
								<span v-if="is_submitting" class="btn_spinner"></span>
								<span v-else class="btn_icon">🚀</span>
								{{ is_submitting ? 'Signing In...' : 'Sign In' }}
							</button>
						</form>

						<!-- Divider -->
						<div class="divider">
							<span class="divider_text">or</span>
						</div>

						<!-- Social Login -->
						<div class="social_auth">
							<button class="google_btn" @click="sign_in_with_google" :disabled="is_submitting">
								<span class="btn_icon">🔍</span>
								Sign in with Google
							</button>
						</div>

						<!-- Guest Option -->
						<div class="guest_option">
							<button class="guest_btn" @click="go_home" :disabled="is_submitting">
								<span class="btn_icon">👤</span>
								Continue as Guest
							</button>
						</div>

						<!-- Error Message -->
						<div v-if="error_message" class="error_message">
							<span class="error_icon">⚠️</span>
							{{ error_message }}
						</div>

						<!-- Sign Up Link -->
						<div class="auth_footer">
							<p class="auth_footer_text">
								Don't have an account? 
								<RouterLink to="/register" class="auth_link">Sign up here</RouterLink>
							</p>
						</div>
					</div>
				</div>
			</div>
		</section>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth'
import { use_auth_store, get_auth_instance } from '../stores/auth'
import { set_seo } from '../lib/seo'
import { toast_success, toast_error } from '../lib/toast'

const router = useRouter()
const auth_store = use_auth_store()
const is_initializing = computed(() => auth_store.is_initializing)
const error_message = ref('')
const email = ref('')
const password = ref('')
const is_submitting = ref(false)

// Set SEO
set_seo({ 
	title: 'Sign In · BottlePlug', 
	description: 'Sign in to your BottlePlug account to access your premium wine and spirit collection, order history, and exclusive offers.' 
})

async function sign_in_with_google() {
	if (is_submitting.value) return
	
	try {
		is_submitting.value = true
		error_message.value = ''
		
		const provider = new GoogleAuthProvider()
		const auth_instance = get_auth_instance()
		await signInWithPopup(auth_instance, provider)
		
		toast_success('Successfully signed in!')
		const destination = auth_store.intended_destination || '/'
		auth_store.set_intended_destination(null)
		router.replace(destination)
	} catch (e) {
		console.error('Google sign in error:', e)
		error_message.value = 'Failed to sign in with Google. Please try again.'
		toast_error('Failed to sign in with Google')
	} finally {
		is_submitting.value = false
	}
}

function go_home() {
	if (is_submitting.value) return
	
	const destination = auth_store.intended_destination || '/'
	auth_store.set_intended_destination(null)
	router.replace(destination)
}

async function handle_email_login() {
	if (is_submitting.value) return
	
	try {
		is_submitting.value = true
		error_message.value = ''
		
		await auth_store.sign_in_with_email_password(email.value, password.value)
		
		toast_success('Successfully signed in!')
		const destination = auth_store.intended_destination || '/'
		auth_store.set_intended_destination(null)
		router.replace(destination)
	} catch (e) {
		console.error('Email sign in error:', e)
		error_message.value = 'Invalid email or password. Please check your credentials and try again.'
		toast_error('Invalid email or password')
	} finally {
		is_submitting.value = false
	}
}
</script>

<style scoped>
.auth_page {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

/* Hero Section */
.hero_section {
	position: relative;
	height: 300px;
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
}

.hero_background {
	position: absolute;
	inset: 0;
	background: linear-gradient(135deg, #1a0f0f 0%, #2d1b1b 50%, #1a0f0f 100%);
}

.hero_background::before {
	content: '';
	position: absolute;
	inset: 0;
	background-image: url('/toss.jpg');
	background-size: cover;
	background-position: center;
	opacity: 0.3;
	filter: blur(1px);
}

.hero_content {
	position: relative;
	z-index: 2;
	text-align: center;
	color: white;
	max-width: 600px;
	padding: 0 20px;
}

.hero_title {
	font-size: 48px;
	font-weight: 700;
	font-family: 'Playfair Display', serif;
	margin-bottom: 16px;
	background: linear-gradient(135deg, #DAA520, #FFD700);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.hero_subtitle {
	font-size: 18px;
	opacity: 0.9;
	line-height: 1.6;
}

/* Auth Section */
.auth_section {
	padding: 40px 0;
}

.auth_container {
	max-width: 500px;
	margin: 0 auto;
	padding: 0 20px;
}

.auth_card {
	background: white;
	border-radius: 20px;
	padding: 40px;
	box-shadow: 0 8px 40px rgba(0, 0, 0, 0.12);
	border: 1px solid rgba(218, 165, 32, 0.1);
}

.auth_header {
	text-align: center;
	margin-bottom: 40px;
}

.auth_logo {
	margin-bottom: 20px;
}

.logo_img {
	width: 60px;
	height: 60px;
	border-radius: 12px;
}

.auth_title {
	font-size: 32px;
	font-weight: 700;
	color: #1a0f0f;
	margin-bottom: 8px;
	font-family: 'Playfair Display', serif;
}

.auth_subtitle {
	font-size: 16px;
	color: #666;
	line-height: 1.5;
}

/* Loading State */
.loading_state {
	text-align: center;
	padding: 40px 20px;
}

.loading_spinner {
	width: 40px;
	height: 40px;
	border: 3px solid rgba(218, 165, 32, 0.3);
	border-top: 3px solid #DAA520;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin: 0 auto 20px;
}

@keyframes spin {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}

.loading_text {
	color: #666;
	font-size: 16px;
}

/* Auth Content */
.auth_content {
	display: flex;
	flex-direction: column;
	gap: 24px;
}

.auth_form {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.form_group {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.form_label {
	font-size: 14px;
	font-weight: 600;
	color: #1a0f0f;
}

.input_wrapper {
	position: relative;
	display: flex;
	align-items: center;
}

.input_icon {
	position: absolute;
	left: 16px;
	font-size: 16px;
	color: #666;
	z-index: 2;
}

.form_input {
	width: 100%;
	padding: 16px 16px 16px 48px;
	border: 2px solid rgba(218, 165, 32, 0.3);
	border-radius: 12px;
	font-size: 16px;
	background: white;
	transition: all 0.3s ease;
}

.form_input:focus {
	outline: none;
	border-color: #DAA520;
	box-shadow: 0 0 0 3px rgba(218, 165, 32, 0.1);
}

.form_input::placeholder {
	color: #999;
}

/* Buttons */
.primary_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 16px 24px;
	border-radius: 12px;
	font-weight: 600;
	font-size: 16px;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	position: relative;
}

.primary_btn:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.primary_btn:disabled {
	opacity: 0.7;
	cursor: not-allowed;
}

.btn_spinner {
	width: 20px;
	height: 20px;
	border: 2px solid rgba(255, 255, 255, 0.3);
	border-top: 2px solid white;
	border-radius: 50%;
	animation: spin 1s linear infinite;
}

.google_btn {
	background: white;
	color: #1a0f0f;
	border: 2px solid rgba(218, 165, 32, 0.3);
	padding: 16px 24px;
	border-radius: 12px;
	font-weight: 600;
	font-size: 16px;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	width: 100%;
}

.google_btn:hover:not(:disabled) {
	border-color: #DAA520;
	background: rgba(218, 165, 32, 0.05);
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.google_btn:disabled {
	opacity: 0.7;
	cursor: not-allowed;
}

.guest_btn {
	background: linear-gradient(135deg, #6b7280, #4b5563);
	color: white;
	border: none;
	padding: 12px 24px;
	border-radius: 12px;
	font-weight: 600;
	font-size: 14px;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	width: 100%;
}

.guest_btn:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
}

.guest_btn:disabled {
	opacity: 0.7;
	cursor: not-allowed;
}

.btn_icon {
	font-size: 16px;
}

/* Divider */
.divider {
	position: relative;
	text-align: center;
	margin: 20px 0;
}

.divider::before {
	content: '';
	position: absolute;
	top: 50%;
	left: 0;
	right: 0;
	height: 1px;
	background: rgba(218, 165, 32, 0.3);
}

.divider_text {
	background: white;
	padding: 0 16px;
	color: #666;
	font-size: 14px;
	font-weight: 500;
}

/* Social Auth */
.social_auth {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.guest_option {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

/* Error Message */
.error_message {
	background: linear-gradient(135deg, #fef2f2, #fee2e2);
	border: 1px solid #fecaca;
	color: #dc2626;
	padding: 12px 16px;
	border-radius: 8px;
	font-size: 14px;
	display: flex;
	align-items: center;
	gap: 8px;
}

.error_icon {
	font-size: 16px;
}

/* Auth Footer */
.auth_footer {
	text-align: center;
	padding-top: 20px;
	border-top: 1px solid rgba(218, 165, 32, 0.1);
}

.auth_footer_text {
	color: #666;
	font-size: 14px;
}

.auth_link {
	color: #DAA520;
	text-decoration: none;
	font-weight: 600;
	transition: color 0.3s ease;
}

.auth_link:hover {
	color: #B8860B;
}

/* Responsive Design */
@media (max-width: 768px) {
	.hero_title {
		font-size: 36px;
	}
	
	.hero_subtitle {
		font-size: 16px;
	}
	
	.auth_card {
		padding: 30px 20px;
	}
	
	.auth_title {
		font-size: 28px;
	}
}
</style>
