<template>
	<div class="support_page">
		<div class="support_container">
			<div class="support_header">
				<h1 class="support_title">Customer Support</h1>
				<p class="support_subtitle">We're here to help! Get in touch with our support team</p>
			</div>

			<div class="support_content">
				<!-- Contact Information -->
				<div class="support_section">
					<h2 class="section_title">Contact Information</h2>
					<div class="contact_grid">
						<div class="contact_card">
							<div class="contact_icon">📞</div>
							<h3 class="contact_title">Phone Support</h3>
							<a href="tel:+256700000000" class="contact_info">+256 700 000 000</a>
							<p class="contact_hours">Mon-Fri: 8AM-6PM</p>
							<button @click="call_support" class="contact_btn">Call Now</button>
						</div>
						<div class="contact_card">
							<div class="contact_icon">📧</div>
							<h3 class="contact_title">Email Support</h3>
							<a href="mailto:support@bottleplugug.com" class="contact_info">support@bottleplugug.com</a>
							<p class="contact_hours">24/7 Response</p>
							<button @click="email_support" class="contact_btn">Send Email</button>
						</div>
						<div class="contact_card">
							<div class="contact_icon">💬</div>
							<h3 class="contact_title">WhatsApp</h3>
							<a href="https://wa.me/256700000000" target="_blank" class="contact_info">+256 700 000 000</a>
							<p class="contact_hours">24/7 Available</p>
							<button @click="whatsapp_support" class="contact_btn">Chat on WhatsApp</button>
						</div>
						<div class="contact_card">
							<div class="contact_icon">📍</div>
							<h3 class="contact_title">Visit Us</h3>
							<p class="contact_info">Kampala, Uganda</p>
							<p class="contact_hours">Mon-Fri: 9AM-5PM</p>
							<button @click="get_directions" class="contact_btn">Get Directions</button>
						</div>
					</div>
				</div>

				<!-- Support Form -->
				<div class="support_section">
					<h2 class="section_title">Send us a Message</h2>
					<form @submit.prevent="submit_support_request" class="support_form">
						<div class="form_row">
							<div class="form_group">
								<label class="form_label">Name *</label>
								<input 
									v-model="support_form.name" 
									type="text" 
									class="form_input"
									placeholder="Your full name"
									required
								/>
							</div>
							<div class="form_group">
								<label class="form_label">Email *</label>
								<input 
									v-model="support_form.email" 
									type="email" 
									class="form_input"
									placeholder="your.email@example.com"
									required
								/>
							</div>
						</div>
						<div class="form_group">
							<label class="form_label">Phone Number</label>
							<input 
								v-model="support_form.phone" 
								type="tel" 
								class="form_input"
								placeholder="+256 700 000 000"
							/>
						</div>
						<div class="form_group">
							<label class="form_label">Subject *</label>
							<select v-model="support_form.subject" class="form_select" required>
								<option value="">Select a subject</option>
								<option value="order_issue">Order Issue</option>
								<option value="delivery_problem">Delivery Problem</option>
								<option value="payment_issue">Payment Issue</option>
								<option value="product_question">Product Question</option>
								<option value="account_help">Account Help</option>
								<option value="technical_issue">Technical Issue</option>
								<option value="feedback">Feedback</option>
								<option value="other">Other</option>
							</select>
						</div>
						<div class="form_group">
							<label class="form_label">Order Number (if applicable)</label>
							<input 
								v-model="support_form.order_number" 
								type="text" 
								class="form_input"
								placeholder="e.g., ORD-20250920-R8C1K"
							/>
						</div>
						<div class="form_group">
							<label class="form_label">Message *</label>
							<textarea 
								v-model="support_form.message" 
								class="form_textarea"
								placeholder="Please describe your issue or question in detail..."
								rows="6"
								required
							></textarea>
						</div>
						<div class="form_actions">
							<button 
								type="submit" 
								:disabled="submitting"
								class="btn_primary"
							>
								{{ submitting ? 'Sending...' : 'Send Message' }}
							</button>
						</div>
					</form>
				</div>

				<!-- FAQ Section -->
				<div class="support_section">
					<h2 class="section_title">Frequently Asked Questions</h2>
					<div class="faq_list">
						<div class="faq_item" v-for="(faq, index) in faqs" :key="index">
							<button 
								@click="toggle_faq(index)"
								class="faq_question"
								:class="{ active: faq.open }"
							>
								<span>{{ faq.question }}</span>
								<span class="faq_icon">{{ faq.open ? '−' : '+' }}</span>
							</button>
							<div v-if="faq.open" class="faq_answer">
								<p>{{ faq.answer }}</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { use_auth_store } from '../stores/auth'
import { toast_success, toast_error } from '../lib/toast'
import { set_seo } from '../lib/seo'
import { useScrollToTop } from '../composables/useScrollToTop'

const auth_store = use_auth_store()
const submitting = ref(false)

const support_form = ref({
	name: '',
	email: '',
	phone: '',
	subject: '',
	order_number: '',
	message: ''
})

const faqs = ref([
	{
		question: 'How do I track my order?',
		answer: 'You can track your order by going to the "Delivery Tracking" page in your account or by using the order number we sent to your email.',
		open: false
	},
	{
		question: 'What payment methods do you accept?',
		answer: 'We accept mobile money (MTN, Airtel), credit/debit cards, and cash on delivery.',
		open: false
	},
	{
		question: 'How long does delivery take?',
		answer: 'Standard delivery takes 2-3 business days within Kampala and 3-5 business days for other areas. Express delivery is available for same-day delivery in Kampala.',
		open: false
	},
	{
		question: 'Can I cancel my order?',
		answer: 'Yes, you can cancel your order if it hasn\'t been processed yet. Please contact our support team as soon as possible.',
		open: false
	},
	{
		question: 'Do you offer refunds?',
		answer: 'Yes, we offer refunds for damaged or incorrect items. Please contact our support team within 48 hours of delivery.',
		open: false
	},
	{
		question: 'How do I create an account?',
		answer: 'Click on "Sign Up" in the top right corner, enter your email and password, and follow the verification steps.',
		open: false
	}
])

// Set SEO
set_seo({ 
	title: 'Customer Support · BottlePlug', 
	description: 'Get help with your BottlePlug orders, delivery, payments, and account. Contact our support team or browse our FAQ.' 
})

// Use scroll to top composable
useScrollToTop()

onMounted(() => {
	// Pre-fill form with user data if available
	if (auth_store.firebase_user) {
		support_form.value.name = auth_store.firebase_user.displayName || ''
		support_form.value.email = auth_store.firebase_user.email || ''
	}
})

const submit_support_request = async () => {
	submitting.value = true
	try {
		// TODO: Implement support request API call
		await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API call
		
		toast_success('Your message has been sent! We\'ll get back to you within 24 hours.')
		
		// Reset form
		support_form.value = {
			name: auth_store.firebase_user?.displayName || '',
			email: auth_store.firebase_user?.email || '',
			phone: '',
			subject: '',
			order_number: '',
			message: ''
		}
	} catch (error) {
		console.error('Error submitting support request:', error)
		toast_error('Failed to send message. Please try again or contact us directly.')
	} finally {
		submitting.value = false
	}
}

const toggle_faq = (index) => {
	faqs.value[index].open = !faqs.value[index].open
}

// Contact method functions
const call_support = () => {
	window.location.href = 'tel:+256700000000'
}

const email_support = () => {
	window.location.href = 'mailto:support@bottleplugug.com?subject=Support Request'
}

const whatsapp_support = () => {
	const message = encodeURIComponent('Hello! I need support with my BottlePlug order.')
	window.open(`https://wa.me/256700000000?text=${message}`, '_blank')
}

const get_directions = () => {
	// Open Google Maps with Kampala location
	window.open('https://maps.google.com/?q=Kampala,Uganda', '_blank')
}
</script>

<style scoped>
.support_page {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
	padding: 2rem 0;
}

.support_container {
	max-width: 1000px;
	margin: 0 auto;
	padding: 0 1rem;
}

.support_header {
	text-align: center;
	margin-bottom: 3rem;
}

.support_title {
	font-size: 2.5rem;
	font-weight: 700;
	color: #1e293b;
	margin-bottom: 0.5rem;
}

.support_subtitle {
	font-size: 1.125rem;
	color: #64748b;
}

.support_content {
	display: flex;
	flex-direction: column;
	gap: 3rem;
}

.support_section {
	background: white;
	border-radius: 1rem;
	box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
	padding: 2rem;
}

.section_title {
	font-size: 1.5rem;
	font-weight: 600;
	color: #1e293b;
	margin-bottom: 1.5rem;
	border-bottom: 2px solid #e2e8f0;
	padding-bottom: 0.5rem;
}

.contact_grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
	gap: 1.5rem;
}

.contact_card {
	text-align: center;
	padding: 1.5rem;
	border: 2px solid #e5e7eb;
	border-radius: 0.75rem;
	transition: all 0.2s;
}

.contact_card:hover {
	border-color: #3b82f6;
	transform: translateY(-2px);
	box-shadow: 0 10px 25px rgba(59, 130, 246, 0.1);
}

.contact_icon {
	font-size: 2rem;
	margin-bottom: 1rem;
}

.contact_title {
	font-size: 1.25rem;
	font-weight: 600;
	color: #1e293b;
	margin-bottom: 0.5rem;
}

.contact_info {
	font-size: 1rem;
	color: #3b82f6;
	font-weight: 500;
	margin-bottom: 0.25rem;
}

.contact_hours {
	font-size: 0.875rem;
	color: #6b7280;
	margin-bottom: 1rem;
}

.contact_btn {
	padding: 0.5rem 1rem;
	background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
	color: white;
	border: none;
	border-radius: 0.5rem;
	font-size: 0.875rem;
	font-weight: 500;
	cursor: pointer;
	transition: all 0.2s;
}

.contact_btn:hover {
	transform: translateY(-1px);
	box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
}

.support_form {
	display: flex;
	flex-direction: column;
	gap: 1.5rem;
}

.form_row {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 1.5rem;
}

.form_group {
	display: flex;
	flex-direction: column;
}

.form_label {
	font-weight: 500;
	color: #374151;
	margin-bottom: 0.5rem;
}

.form_input,
.form_select,
.form_textarea {
	padding: 0.75rem 1rem;
	border: 2px solid #e5e7eb;
	border-radius: 0.5rem;
	font-size: 1rem;
	transition: border-color 0.2s;
	font-family: inherit;
}

.form_input:focus,
.form_select:focus,
.form_textarea:focus {
	outline: none;
	border-color: #3b82f6;
	box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form_textarea {
	resize: vertical;
	min-height: 120px;
}

.form_actions {
	display: flex;
	justify-content: center;
	margin-top: 1rem;
}

.btn_primary {
	padding: 0.75rem 2rem;
	background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
	color: white;
	border: none;
	border-radius: 0.5rem;
	font-weight: 600;
	font-size: 1rem;
	cursor: pointer;
	transition: all 0.2s;
}

.btn_primary:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
}

.btn_primary:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}

.faq_list {
	display: flex;
	flex-direction: column;
	gap: 1rem;
}

.faq_item {
	border: 2px solid #e5e7eb;
	border-radius: 0.5rem;
	overflow: hidden;
}

.faq_question {
	width: 100%;
	padding: 1rem 1.5rem;
	background: white;
	border: none;
	text-align: left;
	font-size: 1rem;
	font-weight: 500;
	color: #374151;
	cursor: pointer;
	display: flex;
	justify-content: space-between;
	align-items: center;
	transition: background-color 0.2s;
}

.faq_question:hover {
	background: #f9fafb;
}

.faq_question.active {
	background: #eff6ff;
	color: #1d4ed8;
}

.faq_icon {
	font-size: 1.25rem;
	font-weight: 600;
}

.faq_answer {
	padding: 0 1.5rem 1rem 1.5rem;
	background: #f9fafb;
	color: #4b5563;
	line-height: 1.6;
}

@media (max-width: 768px) {
	.support_container {
		padding: 0 0.5rem;
	}
	
	.support_section {
		padding: 1.5rem;
	}
	
	.support_title {
		font-size: 2rem;
	}
	
	.form_row {
		grid-template-columns: 1fr;
	}
	
	.contact_grid {
		grid-template-columns: 1fr;
	}
}
</style>
