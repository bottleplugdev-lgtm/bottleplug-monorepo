import { use_auth_store } from '../stores/auth'
import { useRouter } from 'vue-router'
import { toast_error } from '../lib/toast'

/**
 * Utility function to handle actions that require authentication
 * @param {string} action_name - Human-readable name of the action (e.g., "Add to Cart", "RSVP to Event")
 * @param {Function} action_function - The function to execute if user is authenticated
 * @param {string} current_path - Current page path for redirect after login
 */
export function require_auth_for_action(action_name, action_function, current_path = null) {
    const auth_store = use_auth_store()
    const router = useRouter()
    
    // Check if user is authenticated
    if (!auth_store.is_authenticated) {
        // Show user-friendly message
        toast_error(`Please sign in to ${action_name.toLowerCase()}`)
        
        // Set intended destination for redirect after login
        if (current_path) {
            auth_store.set_intended_destination(current_path)
        } else {
            // Use current route if no specific path provided
            auth_store.set_intended_destination(router.currentRoute.value.fullPath)
        }
        
        // Navigate to login page
        router.push({ name: 'login' })
        return false
    }
    
    // User is authenticated, execute the action
    return action_function()
}

/**
 * Utility function to check if user is authenticated without redirecting
 * @param {string} action_name - Human-readable name of the action
 * @returns {boolean} - True if authenticated, false otherwise
 */
export function check_auth_for_action(action_name) {
    const auth_store = use_auth_store()
    
    if (!auth_store.is_authenticated) {
        toast_error(`Please sign in to ${action_name.toLowerCase()}`)
        return false
    }
    
    return true
} 