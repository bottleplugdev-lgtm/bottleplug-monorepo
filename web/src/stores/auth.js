import { defineStore } from 'pinia'
import { init_firebase, ensure_anonymous_auth, setup_token_persistence, get_auth } from '../lib/firebase'
import { GoogleAuthProvider, signInWithPopup, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from 'firebase/auth'
import { use_cart_store } from './cart'

export const use_auth_store = defineStore('auth_store', {
	state: () => ({
		firebase_user: null,
		is_initializing: true,
		intended_destination: null,
		session_start_time: null,
		session_duration: 24 * 60 * 60 * 1000 // 24 hours in milliseconds
	}),
	getters: {
		is_ready: (state) => !state.is_initializing,
		should_show_loading: (state) => state.is_initializing,
		is_authenticated: (state) => !!(state.firebase_user && state.firebase_user.uid && !state.firebase_user.isAnonymous),
		is_anonymous: (state) => !!(state.firebase_user && state.firebase_user.isAnonymous),
		is_fully_authenticated: (state) => !!(state.firebase_user && state.firebase_user.uid && !state.firebase_user.isAnonymous)
	},
	actions: {
		async init_auth() {
			const auth = init_firebase()
			setup_token_persistence()
			
			// Check for existing session
			await this.check_existing_session()
			
			auth.onAuthStateChanged(async (user) => {
				this.firebase_user = user
				this.is_initializing = false
				
				if (user && !user.isAnonymous) {
					// User is signed in - start session timer
					this.start_user_session()
					try { 
						await this.sync_backend_user() 
						await this.load_user_cart()
					} catch (error) {
						console.error('Failed to sync backend user:', error)
					}
				} else if (user && user.isAnonymous) {
					// Anonymous user - ensure session is valid
					await this.ensure_anonymous_session()
				}
			})
		},
		async check_existing_session() {
			const session_start = localStorage.getItem('user_session_start')
			const now = Date.now()
			
			if (session_start) {
				const session_age = now - Number(session_start)
				if (session_age < this.session_duration) {
					// Session is still valid
					this.session_start_time = Number(session_start)
					console.log(`Valid session found, ${Math.round((this.session_duration - session_age) / (1000 * 60 * 60))} hours remaining`)
					return true
				} else {
					// Session expired
					console.log('Session expired, clearing...')
					this.clear_session()
				}
			}
			return false
		},
		
		start_user_session() {
			const now = Date.now()
			this.session_start_time = now
			localStorage.setItem('user_session_start', String(now))
			localStorage.setItem('user_session_duration', String(this.session_duration))
			console.log('User session started, will expire in 24 hours')
		},
		
		clear_session() {
			this.session_start_time = null
			localStorage.removeItem('user_session_start')
			localStorage.removeItem('user_session_duration')
			localStorage.removeItem('firebase_id_token')
			localStorage.removeItem('firebase_id_token_exp')
		},
		
		is_session_valid() {
			if (!this.session_start_time) return false
			const now = Date.now()
			return (now - this.session_start_time) < this.session_duration
		},
		
		get_session_remaining_time() {
			if (!this.session_start_time) return 0
			const now = Date.now()
			const remaining = this.session_duration - (now - this.session_start_time)
			return Math.max(0, remaining)
		},
		
		async ensure_anonymous_session() {
			const start_key = 'anon_session_start'
			const now = Date.now()
			const existing = Number(localStorage.getItem(start_key) || '0')
			if (!existing) {
				await ensure_anonymous_auth()
				localStorage.setItem(start_key, String(now))
				return
			}
			// 24 hours for anonymous sessions
			const twenty_four_hours_ms = 24 * 60 * 60 * 1000
			if (now - existing > twenty_four_hours_ms) {
				await ensure_anonymous_auth()
				localStorage.setItem(start_key, String(now))
			}
		},
		async sign_out_anonymous_if_needed() {
			const auth = get_auth()
			if (auth.currentUser && auth.currentUser.isAnonymous) {
				try { await signOut(auth) } catch (_) {}
			}
		},
		set_intended_destination(path) {
			this.intended_destination = path
		},
		async sync_backend_user() {
			// Firebase authentication is handled automatically by the backend
			// when the Firebase token is included in the Authorization header
			// No need for a separate verification endpoint
			console.log('User authenticated via Firebase - backend will validate token automatically')
			return true
		},
		
		async load_user_cart() {
			try {
				const cart = use_cart_store()
				await cart.fetch_cart()
				console.log('User cart loaded after sign-in:', cart.items.length, 'items')
			} catch (error) {
				console.error('Failed to load user cart after sign-in:', error)
				// Don't throw - cart loading failure shouldn't break sign-in
			}
		},
		async sign_in_with_google() {
			try {
				await this.sign_out_anonymous_if_needed()
				const auth = get_auth()
				const provider = new GoogleAuthProvider()
				await signInWithPopup(auth, provider)
				
				// Start user session after successful sign-in
				this.start_user_session()
				await this.sync_backend_user()
				await this.load_user_cart()
			} catch (e) {
				// fallback to anonymous
				try { await ensure_anonymous_auth() } catch (_) {}
				throw e
			}
		},
		async sign_in_with_email_password(email, password) {
			try {
				await this.sign_out_anonymous_if_needed()
				const auth = get_auth()
				await signInWithEmailAndPassword(auth, email, password)
				
				// Start user session after successful sign-in
				this.start_user_session()
				await this.sync_backend_user()
				await this.load_user_cart()
			} catch (e) {
				try { await ensure_anonymous_auth() } catch (_) {}
				throw e
			}
		},
		async sign_up_with_email_password(email, password) {
			try {
				await this.sign_out_anonymous_if_needed()
				const auth = get_auth()
				await createUserWithEmailAndPassword(auth, email, password)
				
				// Start user session after successful sign-up
				this.start_user_session()
				await this.sync_backend_user()
				await this.load_user_cart()
			} catch (e) {
				try { await ensure_anonymous_auth() } catch (_) {}
				throw e
			}
		},
		async sign_out_and_go_anonymous() {
			const auth = get_auth()
			try { await signOut(auth) } catch (_) {}
			
			// Clear user session
			this.clear_session()
			
			// Clear cart when user signs out
			try {
				const cart = use_cart_store()
				cart.clear_cart_state()
			} catch (error) {
				console.error('Failed to clear cart after sign out:', error)
			}
			
			// Go back to anonymous auth
			await ensure_anonymous_auth()
		}
	}
})

export function get_firebase_id_token_sync() {
	return localStorage.getItem('firebase_id_token') || ''
}

export function get_auth_instance() {
	return get_auth()
}
