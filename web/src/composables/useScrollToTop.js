import { onMounted } from 'vue'

/**
 * Composable for handling scroll-to-top behavior
 * Use this in components that need to scroll to top on mount
 */
export function useScrollToTop() {
	const scrollToTop = () => {
		window.scrollTo({ 
			top: 0, 
			left: 0, 
			behavior: 'smooth' 
		})
	}

	// Automatically scroll to top when component mounts
	onMounted(() => {
		scrollToTop()
	})

	return {
		scrollToTop
	}
}
