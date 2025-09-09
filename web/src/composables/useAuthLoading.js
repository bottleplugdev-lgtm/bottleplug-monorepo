import { computed } from 'vue'
import { use_auth_store } from '../stores/auth'

/**
 * Composable to handle authentication loading states
 * Use this in components that require authentication
 */
export function use_auth_loading() {
	const auth_store = use_auth_store()
	
	const is_loading = computed(() => auth_store.should_show_loading)
	const is_ready = computed(() => auth_store.is_ready)
	const is_authenticated = computed(() => auth_store.is_authenticated)
	const should_show_content = computed(() => auth_store.is_ready && auth_store.is_authenticated)
	
	return {
		is_loading,
		is_ready,
		is_authenticated,
		should_show_content,
		auth_store
	}
}
