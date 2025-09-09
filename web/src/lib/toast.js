let container = null

function ensure_container() {
	if (container) return container
	container = document.createElement('div')
	container.setAttribute('id', 'toast-container')
	container.style.position = 'fixed'
	container.style.top = '16px'
	container.style.right = '16px'
	container.style.zIndex = '9999'
	document.body.appendChild(container)
	return container
}

export function toast(message, { type = 'info', duration = 3000 } = {}) {
	const root = ensure_container()
	const el = document.createElement('div')
	el.textContent = message
	el.setAttribute('role', 'status')
	el.style.marginTop = '8px'
	el.style.padding = '10px 12px'
	el.style.borderRadius = '8px'
	el.style.color = '#fff'
	el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'
	if (type === 'error') el.style.background = '#b91c1c'
	else if (type === 'success') el.style.background = '#16a34a'
	else el.style.background = '#111827'
	root.appendChild(el)
	setTimeout(() => { root.removeChild(el) }, duration)
}

export function toast_error(message, opts = {}) { toast(message, { type: 'error', ...opts }) }
export function toast_success(message, opts = {}) { toast(message, { type: 'success', ...opts }) }

