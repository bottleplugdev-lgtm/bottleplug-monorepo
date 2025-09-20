/**
 * Utility functions for handling image URLs
 */

/**
 * Get the backend base URL for media files
 */
function getBackendUrl() {
	const envUrl = import.meta.env.VITE_API_BASE_URL
	if (envUrl) {
		// Remove /api/v1 suffix if present to get base URL
		return envUrl.replace(/\/api\/v1\/?$/, '')
	}
	// Default to live API endpoint
	return 'https://api.bottleplugug.com'
}

/**
 * Build a complete image URL from a path
 * @param {string} path - The image path (can be relative or absolute)
 * @returns {string} - Complete image URL
 */
export function image_url(path) {
	if (!path) {
		return `${getBackendUrl()}/media/bottleplug_logo.png`
	}
	
	// If it's already a full URL, return as is
	if (path.startsWith('http://') || path.startsWith('https://')) {
		return path
	}
	
	// Handle localhost references (legacy) - convert to production URL
	if (path.includes('localhost')) {
		path = path.replace('localhost:8000', 'api.bottleplugug.com')
		path = path.replace('localhost', 'api.bottleplugug.com')
	}
	
	const backend_url = getBackendUrl()
	const clean_path = path.replace(/^\/?media\//, '')
	return `${backend_url}/media/${clean_path}`
}

/**
 * Build a category image URL
 * @param {object} category - Category object with image property
 * @returns {string} - Complete image URL
 */
export function category_image_url(category) {
	if (!category || !category.image) {
		return image_url('bottleplug_logo.png')
	}
	
	// Handle legacy localhost references - convert to production URL
	if (category.image.includes('localhost')) {
		return image_url(category.image.replace('localhost:8000', 'api.bottleplugug.com').replace('localhost', 'api.bottleplugug.com'))
	}
	
	return image_url(category.image)
}

/**
 * Get fallback image URL
 * @returns {string} - Fallback image URL
 */
export function get_fallback_image_url() {
	return image_url('bottleplug_logo.png')
}
