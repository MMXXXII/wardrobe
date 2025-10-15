import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle'
import 'bootstrap-icons/font/bootstrap-icons.css'


import axios from 'axios'
import Cookies from 'js-cookie'


// выставляем CSRF заголовок для Django
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')
axios.defaults.baseURL = '/api'


createApp(App).use(router).mount('#app')

