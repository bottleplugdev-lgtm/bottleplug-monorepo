import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import 'vue3-toastify/dist/index.css'
import { toast } from 'vue3-toastify'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(toast, {
  autoClose: 3000,
  position: 'top-right',
})

app.mount('#app') 