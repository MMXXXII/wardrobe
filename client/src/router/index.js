import { createRouter, createWebHistory } from 'vue-router'
import Brands from '../components/Brands.vue'
import Categories from '../components/Categories.vue'
import Items from '../components/Items.vue'
import Stores from '../components/Stores.vue'
import Purchases from '../components/Purchases.vue'

const routes = [
  { path: '/', redirect: '/brands' },
  { path: '/brands', component: Brands },
  { path: '/categories', component: Categories },
  { path: '/items', component: Items },
  { path: '/stores', component: Stores },
  { path: '/purchases', component: Purchases },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
