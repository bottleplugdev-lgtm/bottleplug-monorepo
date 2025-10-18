// Import the functions you need from the SDKs you need
import { initializeApp, getApps } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth, setPersistence, browserLocalPersistence, onIdTokenChanged, signInAnonymously, GoogleAuthProvider } from 'firebase/auth'
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCWanxavLgje_xaM5n3g6yCEK4QZvNbF_c",
  authDomain: "booze-nation-94e3f.firebaseapp.com",
  projectId: "booze-nation-94e3f",
  storageBucket: "booze-nation-94e3f.appspot.com",
  messagingSenderId: "286573090537",
  appId: "1:286573090537:web:915bdb23b99a18eb6c8278",
  measurementId: "G-1NS3W2CWQ9"
};

let firebaseApp = null
let auth = null
let analytics = null

export function init_firebase() {
	if (!getApps().length) {
		// Initialize Firebase
		firebaseApp = initializeApp(firebaseConfig);
		analytics = getAnalytics(firebaseApp);
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

export function get_analytics() {
	return analytics
}

// Google Auth Provider with account selection
export const googleProvider = new GoogleAuthProvider()
googleProvider.setCustomParameters({
	prompt: 'select_account'
})
