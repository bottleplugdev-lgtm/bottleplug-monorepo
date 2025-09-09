<template>
	<footer class="footer">
		<div class="footer_container">
			<div class="footer_content">
				<!-- Company Info Column -->
				<div class="footer_column">
					<div class="footer_logo">
						<img src="/bottleplug_logo_new.png" alt="BottlePlug" class="logo_img" />
						<div class="logo_text">
							<div class="logo_title">BottlePlug</div>
							<div class="logo_subtitle">Premium Spirits & Wines</div>
						</div>
					</div>
					<p class="footer_description">
						Discover exceptional wines and spirits from around the world, curated for the discerning connoisseur. Your journey into the world of fine beverages starts here.
					</p>
					<div class="social_icons">
						<div class="social_icon">📱</div>
						<div class="social_icon">📧</div>
						<div class="social_icon">📷</div>
						<div class="social_icon">🐦</div>
					</div>
				</div>

				<!-- Quick Links Column -->
				<div class="footer_column">
					<h3 class="footer_section_title">Quick Links</h3>
					<ul class="footer_links">
						<li><RouterLink to="/products" class="footer_link">All Products</RouterLink></li>
						<li><RouterLink to="/products?category=red-wine" class="footer_link">Red Wines</RouterLink></li>
						<li><RouterLink to="/products?category=champagne" class="footer_link">Champagne</RouterLink></li>
						<li><RouterLink to="/products?category=whisky" class="footer_link">Whisky & Spirits</RouterLink></li>
						<li><RouterLink to="/guide" class="footer_link">Wine Guide</RouterLink></li>
						<li><RouterLink to="/events" class="footer_link">Events & Tastings</RouterLink></li>
					</ul>
				</div>

				<!-- Customer Service Column -->
				<div class="footer_column">
					<h3 class="footer_section_title">Customer Service</h3>
					<ul class="footer_links">
						<li><RouterLink to="/account" class="footer_link">My Account</RouterLink></li>
						<li><RouterLink to="/orders" class="footer_link">Order History</RouterLink></li>
						<li><RouterLink to="/contact" class="footer_link">Contact Us</RouterLink></li>
						<li><RouterLink to="/shipping" class="footer_link">Shipping Info</RouterLink></li>
						<li><RouterLink to="/returns" class="footer_link">Returns & Exchanges</RouterLink></li>
						<li><RouterLink to="/faq" class="footer_link">FAQ</RouterLink></li>
					</ul>
				</div>

				<!-- Newsletter Column -->
				<div class="footer_column">
					<h3 class="footer_section_title">Stay Connected</h3>
					<p class="newsletter_description">
						Subscribe to our newsletter for exclusive offers and wine insights.
					</p>
					<div class="newsletter_form">
						<input 
							v-model="email" 
							type="email" 
							class="newsletter_input" 
							placeholder="Your email" 
						/>
						<button class="newsletter_btn" @click="subscribe">Subscribe</button>
					</div>
					<p v-if="message" class="newsletter_message" :class="{ 'success': success, 'error': !success }">
						{{ message }}
					</p>
					
					<div class="contact_info">
						<div class="contact_item">
							<span class="contact_icon">📞</span>
							<span class="contact_text">+1 (555) 123-4567</span>
						</div>
						<div class="contact_item">
							<span class="contact_icon">✉️</span>
							<span class="contact_text">hello@bottleplug.com</span>
						</div>
						<div class="contact_item">
							<span class="contact_icon">📍</span>
							<span class="contact_text">123 Wine Street, Napa, CA</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Footer Bottom -->
			<div class="footer_bottom">
				<div class="footer_bottom_content">
					<div class="copyright">
						© {{ new Date().getFullYear() }} BottlePlug. All rights reserved.
					</div>
					<div class="legal_links">
						<RouterLink to="/privacy" class="legal_link">Privacy Policy</RouterLink>
						<RouterLink to="/terms" class="legal_link">Terms of Service</RouterLink>
						<RouterLink to="/cookies" class="legal_link">Cookie Policy</RouterLink>
					</div>
				</div>
				<div class="age_verification">
					<span class="wine_icon">🍷</span>
					<span class="age_text">
						You must be 21 or older to purchase alcoholic beverages. By entering this site, you agree to our terms and acknowledge that you are of legal drinking age.
					</span>
				</div>
			</div>
		</div>
	</footer>
</template>

<script setup>
import { ref } from 'vue'
import { create_newsletter_subscription } from '../../services/api'

const email = ref('')
const message = ref('')
const success = ref(false)

async function subscribe() {
	message.value = ''
	success.value = false
	if (!email.value) {
		message.value = 'Please enter your email'
		return
	}
	try {
		await create_newsletter_subscription(email.value)
		success.value = true
		message.value = 'Subscribed successfully!'
		email.value = ''
	} catch (e) {
		message.value = 'Failed to subscribe. Please try again.'
	}
}
</script>

<style scoped>
.footer {
	background: linear-gradient(135deg, #1a0f0f 0%, #2d1b1b 100%);
	color: white;
	padding: 60px 0 20px;
	margin-top: 80px;
}

.footer_container {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
}

.footer_content {
	display: grid;
	grid-template-columns: 2fr 1fr 1fr 1.5fr;
	gap: 40px;
	margin-bottom: 40px;
}

.footer_column {
	display: flex;
	flex-direction: column;
}

.footer_logo {
	display: flex;
	align-items: center;
	gap: 12px;
	margin-bottom: 20px;
}

.logo_img {
	width: 40px;
	height: 40px;
	border-radius: 8px;
	filter: brightness(1.1) contrast(1.1);
}

.logo_title {
	font-size: 24px;
	font-weight: 700;
	color: #DAA520;
	font-family: 'Playfair Display', serif;
}

.logo_subtitle {
	font-size: 14px;
	color: #ccc;
	font-weight: 500;
}

.footer_description {
	color: #ccc;
	line-height: 1.6;
	margin-bottom: 20px;
	font-size: 14px;
}

.social_icons {
	display: flex;
	gap: 12px;
}

.social_icon {
	width: 40px;
	height: 40px;
	background: rgba(218, 165, 32, 0.1);
	border: 1px solid rgba(218, 165, 32, 0.3);
	border-radius: 8px;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 18px;
	cursor: pointer;
	transition: all 0.3s ease;
}

.social_icon:hover {
	background: rgba(218, 165, 32, 0.2);
	border-color: #DAA520;
	transform: translateY(-2px);
}

.footer_section_title {
	font-size: 18px;
	font-weight: 700;
	color: #DAA520;
	margin-bottom: 20px;
	font-family: 'Playfair Display', serif;
}

.footer_links {
	list-style: none;
	padding: 0;
	margin: 0;
}

.footer_links li {
	margin-bottom: 12px;
}

.footer_link {
	color: #ccc;
	text-decoration: none;
	font-size: 14px;
	transition: color 0.3s ease;
}

.footer_link:hover {
	color: #DAA520;
}

.newsletter_description {
	color: #ccc;
	line-height: 1.5;
	margin-bottom: 20px;
	font-size: 14px;
}

.newsletter_form {
	display: flex;
	gap: 8px;
	margin-bottom: 15px;
}

.newsletter_input {
	flex: 1;
	padding: 12px 16px;
	border: 1px solid rgba(218, 165, 32, 0.3);
	border-radius: 25px;
	background: rgba(255, 255, 255, 0.1);
	color: white;
	font-size: 14px;
}

.newsletter_input::placeholder {
	color: #999;
}

.newsletter_input:focus {
	outline: none;
	border-color: #DAA520;
	background: rgba(255, 255, 255, 0.15);
}

.newsletter_btn {
	background: linear-gradient(135deg, #DAA520, #B8860B);
	color: white;
	border: none;
	padding: 12px 24px;
	border-radius: 25px;
	font-weight: 600;
	font-size: 14px;
	cursor: pointer;
	transition: all 0.3s ease;
	white-space: nowrap;
}

.newsletter_btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(218, 165, 32, 0.3);
}

.newsletter_message {
	font-size: 12px;
	margin-top: 8px;
}

.newsletter_message.success {
	color: #4ade80;
}

.newsletter_message.error {
	color: #f87171;
}

.contact_info {
	margin-top: 20px;
}

.contact_item {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 8px;
	font-size: 14px;
	color: #ccc;
}

.contact_icon {
	font-size: 16px;
}

.contact_text {
	font-size: 13px;
}

.footer_bottom {
	border-top: 1px solid rgba(218, 165, 32, 0.2);
	padding-top: 20px;
}

.footer_bottom_content {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 15px;
}

.copyright {
	color: #999;
	font-size: 12px;
}

.legal_links {
	display: flex;
	gap: 20px;
}

.legal_link {
	color: #ccc;
	text-decoration: none;
	font-size: 12px;
	transition: color 0.3s ease;
}

.legal_link:hover {
	color: #DAA520;
}

.age_verification {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 15px 20px;
	background: rgba(139, 69, 19, 0.1);
	border: 1px solid rgba(139, 69, 19, 0.3);
	border-radius: 8px;
}

.wine_icon {
	font-size: 16px;
}

.age_text {
	color: #ccc;
	font-size: 11px;
	line-height: 1.4;
}

/* Responsive Design */
@media (max-width: 1024px) {
	.footer_content {
		grid-template-columns: 1fr 1fr;
		gap: 30px;
	}
}

@media (max-width: 768px) {
	.footer {
		padding: 40px 0 20px;
	}
	
	.footer_content {
		grid-template-columns: 1fr;
		gap: 30px;
	}
	
	.footer_bottom_content {
		flex-direction: column;
		gap: 15px;
		text-align: center;
	}
	
	.legal_links {
		justify-content: center;
	}
	
	.newsletter_form {
		flex-direction: column;
	}
	
	.newsletter_btn {
		width: 100%;
	}
}
</style>
