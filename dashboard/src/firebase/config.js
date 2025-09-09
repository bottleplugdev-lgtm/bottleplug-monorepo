import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider, setPersistence, browserLocalPersistence } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'
import { getStorage } from 'firebase/storage'
import { getAnalytics } from 'firebase/analytics'

const firebaseConfig = {
  apiKey: "AIzaSyCWanxavLgje_xaM5n3g6yCEK4QZvNbF_c",
  authDomain: "booze-nation-94e3f.firebaseapp.com",
  projectId: "booze-nation-94e3f",
  storageBucket: "booze-nation-94e3f.appspot.com",
  messagingSenderId: "286573090537",
  appId: "1:286573090537:web:915bdb23b99a18eb6c8278",
  measurementId: "G-1NS3W2CWQ9"
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)

// Initialize Firebase services
export const auth = getAuth(app)
// Ensure session persists across tabs/reloads
setPersistence(auth, browserLocalPersistence).catch(() => {})

export const db = getFirestore(app)
export const storage = getStorage(app)
export const analytics = getAnalytics(app)
export const googleProvider = new GoogleAuthProvider()

export default app 