// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth, GoogleAuthProvider, setPersistence, browserLocalPersistence } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'
import { getStorage } from 'firebase/storage'
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

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Initialize Firebase services
export const auth = getAuth(app)
// Ensure session persists across tabs/reloads
setPersistence(auth, browserLocalPersistence).catch(() => {})

export const db = getFirestore(app)
export const storage = getStorage(app)
export { analytics }
export const googleProvider = new GoogleAuthProvider()
googleProvider.setCustomParameters({
  prompt: 'select_account'
})

export default app