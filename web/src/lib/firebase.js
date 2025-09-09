import { initializeApp, getApps } from 'firebase/app'
import { getAuth, setPersistence, browserLocalPersistence, onIdTokenChanged, signInAnonymously } from 'firebase/auth'

let firebaseApp = null
let auth = null

export function init_firebase() {
	if (!getApps().length) {
		firebaseApp = initializeApp({
			apiKey: import.meta.env.VITE_FIREBASE_API_KEY || 'AIzaSyCWanxavLgje_xaM5n3g6yCEK4QZvNbF_c',
			authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'booze-nation-94e3f.firebaseapp.com',
			projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || 'booze-nation-94e3f',
			appId: import.meta.env.VITE_FIREBASE_APP_ID || '1:286573090537:web:915bdb23b99a18eb6c8278'
		})
	}
	auth = getAuth()
	
	// Set persistence to LOCAL to maintain session across browser restarts
	setPersistence(auth, browserLocalPersistence)
	
	return auth
}

export async function ensure_anonymous_auth() {
	const authInstance = auth || init_firebase()
	if (!authInstance.currentUser) {
		await signInAnonymously(authInstance)
	}
}

export function setup_token_persistence() {
	const authInstance = auth || init_firebase()
	onIdTokenChanged(authInstance, async (user) => {
		if (!user) {
			localStorage.removeItem('firebase_id_token')
			localStorage.removeItem('firebase_id_token_exp')
			return
		}
		
		try {
			const token = await user.getIdToken()
			const tokenResult = await user.getIdTokenResult()
			
			localStorage.setItem('firebase_id_token', token)
			localStorage.setItem('firebase_id_token_exp', String(new Date(tokenResult.expirationTime).getTime()))
			
			// For non-anonymous users, ensure session is maintained
			if (!user.isAnonymous) {
				const session_start = localStorage.getItem('user_session_start')
				if (!session_start) {
					// Session not started yet, this will be handled by auth store
					console.log('Token updated for authenticated user')
				}
			}
		} catch (error) {
			console.error('Error updating token:', error)
		}
	})
}

export function get_auth() {
	return auth || init_firebase()
}
