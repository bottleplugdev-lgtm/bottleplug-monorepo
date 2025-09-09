export function set_seo({ title = '', description = '', image = '', url = '' } = {}) {
	if (title) {
		document.title = title
	}
	set_meta('description', description)
	set_meta_property('og:title', title)
	set_meta_property('og:description', description)
	set_meta_property('og:image', image)
	set_meta_property('og:url', url || window.location.href)
}

function set_meta(name, content) {
	let tag = document.querySelector(`meta[name="${name}"]`)
	if (!tag) {
		tag = document.createElement('meta')
		tag.setAttribute('name', name)
		document.head.appendChild(tag)
	}
	if (content) tag.setAttribute('content', content)
}

function set_meta_property(property, content) {
	let tag = document.querySelector(`meta[property="${property}"]`)
	if (!tag) {
		tag = document.createElement('meta')
		tag.setAttribute('property', property)
		document.head.appendChild(tag)
	}
	if (content) tag.setAttribute('content', content)
}

