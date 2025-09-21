<template>
	<div class="profile_page">
		<div class="profile_container">
			<div class="profile_header">
				<h1 class="profile_title">Profile Information</h1>
				<p class="profile_subtitle">Manage your personal information and profile settings</p>
			</div>

			<div class="profile_content">
				<!-- Profile Picture Section -->
				<div class="profile_section">
					<h2 class="section_title">Profile Picture</h2>
					<div class="profile_picture_section">
						<div class="profile_picture_container">
							<img 
								:src="profile.profile_image || default_avatar" 
								:alt="profile.first_name + ' ' + profile.last_name"
								class="profile_picture"
							/>
							<div class="profile_picture_overlay">
								<input 
									ref="fileInput"
									type="file" 
									accept="image/*"
									@change="handle_image_upload"
									class="file_input"
								/>
								<button @click="trigger_file_input" class="upload_btn">
									<span class="upload_icon">📷</span>
									<span class="upload_text">Upload Image</span>
								</button>
							</div>
						</div>
						<div class="profile_picture_info">
							<p class="file_status">{{ file_status }}</p>
							<p class="file_help">Click to upload a new profile picture. Max size: 5MB</p>
						</div>
					</div>
				</div>

				<!-- Personal Information Form -->
				<form @submit.prevent="update_profile" class="profile_form">
					<div class="profile_section">
						<h2 class="section_title">Personal Information</h2>
						<div class="form_row">
							<div class="form_group">
								<label class="form_label">First Name *</label>
								<input 
									v-model="profile.first_name" 
									type="text" 
									class="form_input"
									placeholder="Enter your first name"
									required
								/>
							</div>
							<div class="form_group">
								<label class="form_label">Last Name *</label>
								<input 
									v-model="profile.last_name" 
									type="text" 
									class="form_input"
									placeholder="Enter your last name"
									required
								/>
							</div>
						</div>
						<div class="form_group">
							<label class="form_label">Email Address</label>
							<input 
								v-model="profile.email" 
								type="email" 
								class="form_input"
								disabled
							/>
							<p class="form_help">Email cannot be changed</p>
						</div>
						<div class="form_group">
							<label class="form_label">Phone Number</label>
							<input 
								v-model="profile.phone" 
								type="tel" 
								class="form_input"
								placeholder="Enter your phone number"
							/>
						</div>
					</div>

					<div class="profile_section">
						<h2 class="section_title">Address Information</h2>
						<div class="form_group">
							<label class="form_label">Address</label>
							<textarea 
								v-model="profile.address" 
								class="form_textarea"
								placeholder="Enter your full address"
								rows="3"
							></textarea>
						</div>
					</div>

					<div class="profile_section">
						<h2 class="section_title">About You</h2>
						<div class="form_group">
							<label class="form_label">Bio</label>
							<textarea 
								v-model="profile.bio" 
								class="form_textarea"
								placeholder="Tell us about yourself..."
								rows="4"
							></textarea>
							<p class="form_help">Share a bit about yourself (optional)</p>
						</div>
					</div>

					<div class="profile_actions">
						<button 
							type="submit" 
							:disabled="updating"
							class="btn_primary"
						>
							{{ updating ? 'Updating...' : 'Update Profile' }}
						</button>
						<button 
							type="button"
							@click="reset_form" 
							class="btn_secondary"
						>
							Reset
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { use_auth_store } from '../stores/auth'
import { toast_success, toast_error } from '../lib/toast'
import { set_seo } from '../lib/seo'
import { getUserProfile, updateUserProfile, uploadProfileImage } from '../services/api'
import { useScrollToTop } from '../composables/useScrollToTop'

const auth_store = use_auth_store()
const updating = ref(false)
const fileInput = ref(null)
const file_status = ref('No file chosen')

// Default avatar image
const default_avatar = 'https://via.placeholder.com/150x150/3b82f6/ffffff?text=U'

const profile = ref({
	first_name: '',
	last_name: '',
	email: '',
	phone: '',
	address: '',
	bio: '',
	profile_image: null
})

// Computed properties
const full_name = computed(() => {
	return `${profile.value.first_name} ${profile.value.last_name}`.trim()
})

// Set SEO
set_seo({ 
	title: 'Profile Information · BottlePlug', 
	description: 'Manage your personal information, profile picture, and account settings on BottlePlug.' 
})

// Use scroll to top composable
useScrollToTop()

onMounted(async () => {
	await load_user_profile()
})

const load_user_profile = async () => {
	try {
		// Load user data from Firebase auth first
		if (auth_store.firebase_user) {
			const user = auth_store.firebase_user
			profile.value.email = user.email || ''
			
			// Parse display name if available
			if (user.displayName) {
				const nameParts = user.displayName.split(' ')
				profile.value.first_name = nameParts[0] || ''
				profile.value.last_name = nameParts.slice(1).join(' ') || ''
			}
			
			// Load profile image if available
			if (user.photoURL) {
				profile.value.profile_image = user.photoURL
			}
		}
		
		// Load additional profile data from backend API
		try {
			const response = await getUserProfile()
			if (response) {
				// Update profile with backend data
				profile.value.first_name = response.first_name || profile.value.first_name
				profile.value.last_name = response.last_name || profile.value.last_name
				profile.value.phone = response.phone_number || ''
				profile.value.address = response.address || ''
				profile.value.bio = response.bio || ''
				profile.value.profile_image = response.profile_image_url || profile.value.profile_image
			}
		} catch (apiError) {
			console.warn('Could not load profile from backend:', apiError)
			// Continue with Firebase data only
		}
	} catch (error) {
		console.error('Error loading user profile:', error)
		toast_error('Failed to load profile data')
	}
}

const trigger_file_input = () => {
	fileInput.value?.click()
}

const handle_image_upload = (event) => {
	const file = event.target.files[0]
	if (!file) return
	
	// Validate file type
	if (!file.type.startsWith('image/')) {
		toast_error('Please select an image file')
		return
	}
	
	// Validate file size (5MB max)
	if (file.size > 5 * 1024 * 1024) {
		toast_error('File size must be less than 5MB')
		return
	}
	
	// Update file status
	file_status.value = file.name
	
	// Create preview URL
	const reader = new FileReader()
	reader.onload = (e) => {
		profile.value.profile_image = e.target.result
	}
	reader.readAsDataURL(file)
}

const update_profile = async () => {
	updating.value = true
	try {
		// Validate required fields
		if (!profile.value.first_name || !profile.value.last_name) {
			toast_error('First name and last name are required')
			return
		}
		
		// Prepare profile data for API
		const profileData = {
			first_name: profile.value.first_name,
			last_name: profile.value.last_name,
			phone_number: profile.value.phone,
			address: profile.value.address,
			bio: profile.value.bio
		}
		
		// Update profile via backend API
		const response = await updateUserProfile(profileData)
		if (response) {
			toast_success('Profile updated successfully!')
			await load_user_profile()
		} else {
			throw new Error('Failed to update profile')
		}
		
	} catch (error) {
		console.error('Error updating profile:', error)
		toast_error('Failed to update profile. Please try again.')
	} finally {
		updating.value = false
	}
}

const reset_form = () => {
	load_user_profile()
	file_status.value = 'No file chosen'
}
</script>

<style scoped>
.profile_page {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
	padding: 2rem 0;
}

.profile_container {
	max-width: 800px;
	margin: 0 auto;
	padding: 0 1rem;
}

.profile_header {
	text-align: center;
	margin-bottom: 3rem;
}

.profile_title {
	font-size: 2.5rem;
	font-weight: 700;
	color: #1e293b;
	margin-bottom: 0.5rem;
}

.profile_subtitle {
	font-size: 1.125rem;
	color: #64748b;
}

.profile_content {
	background: white;
	border-radius: 1rem;
	box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
	padding: 2rem;
}

.profile_section {
	margin-bottom: 2.5rem;
}

.section_title {
	font-size: 1.5rem;
	font-weight: 600;
	color: #1e293b;
	margin-bottom: 1.5rem;
	border-bottom: 2px solid #e2e8f0;
	padding-bottom: 0.5rem;
}

/* Profile Picture Styles */
.profile_picture_section {
	display: flex;
	align-items: center;
	gap: 2rem;
}

.profile_picture_container {
	position: relative;
	width: 150px;
	height: 150px;
	border-radius: 50%;
	overflow: hidden;
	border: 4px solid #e2e8f0;
	transition: all 0.3s;
}

.profile_picture_container:hover {
	border-color: #3b82f6;
	transform: scale(1.05);
}

.profile_picture {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.profile_picture_overlay {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.7);
	display: flex;
	align-items: center;
	justify-content: center;
	opacity: 0;
	transition: opacity 0.3s;
}

.profile_picture_container:hover .profile_picture_overlay {
	opacity: 1;
}

.file_input {
	display: none;
}

.upload_btn {
	background: none;
	border: none;
	color: white;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.5rem;
	cursor: pointer;
	font-size: 0.875rem;
}

.upload_icon {
	font-size: 1.5rem;
}

.profile_picture_info {
	flex: 1;
}

.file_status {
	font-weight: 500;
	color: #374151;
	margin-bottom: 0.5rem;
}

.file_help {
	font-size: 0.875rem;
	color: #6b7280;
}

/* Form Styles */
.profile_form {
	display: flex;
	flex-direction: column;
	gap: 2.5rem;
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
.form_textarea {
	padding: 0.75rem 1rem;
	border: 2px solid #e5e7eb;
	border-radius: 0.5rem;
	font-size: 1rem;
	transition: border-color 0.2s;
	font-family: inherit;
}

.form_input:focus,
.form_textarea:focus {
	outline: none;
	border-color: #3b82f6;
	box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form_input:disabled {
	background-color: #f9fafb;
	color: #6b7280;
}

.form_textarea {
	resize: vertical;
	min-height: 100px;
}

.form_help {
	font-size: 0.875rem;
	color: #6b7280;
	margin-top: 0.25rem;
}

.profile_actions {
	display: flex;
	gap: 1rem;
	justify-content: center;
	margin-top: 2rem;
	padding-top: 2rem;
	border-top: 2px solid #e2e8f0;
}

.btn_primary,
.btn_secondary {
	padding: 0.75rem 2rem;
	border-radius: 0.5rem;
	font-weight: 600;
	font-size: 1rem;
	cursor: pointer;
	transition: all 0.2s;
	border: none;
}

.btn_primary {
	background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
	color: white;
}

.btn_primary:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
}

.btn_primary:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}

.btn_secondary {
	background: white;
	color: #374151;
	border: 2px solid #e5e7eb;
}

.btn_secondary:hover {
	background: #f9fafb;
	border-color: #d1d5db;
}

@media (max-width: 768px) {
	.profile_container {
		padding: 0 0.5rem;
	}
	
	.profile_content {
		padding: 1.5rem;
	}
	
	.profile_title {
		font-size: 2rem;
	}
	
	.profile_picture_section {
		flex-direction: column;
		text-align: center;
	}
	
	.form_row {
		grid-template-columns: 1fr;
	}
	
	.profile_actions {
		flex-direction: column;
	}
}
</style>