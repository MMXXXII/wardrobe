import { createRouter, createWebHistory } from "vue-router"
import { useUserStore } from "../stores/userStore"

import Categories from "../components/Categories.vue"
import Stores from "../components/Stores.vue"
import Products from "../components/Products.vue"
import Customers from "../components/Customers.vue"
import Orders from "../components/Orders.vue"
import Profile from "../components/User.vue"
import Login from "../components/Login.vue"

const routes = [
  { 
    path: "/", 
    redirect: "/categories" 
  },
  { 
    path: "/categories", 
    name: "categories",
    component: Categories,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/stores", 
    name: "stores", 
    component: Stores,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/products", 
    name: "products", 
    component: Products,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/customers", 
    name: "customers", 
    component: Customers,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/orders", 
    name: "orders",    
    component: Orders,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/profile", 
    name: "profile",    
    component: Profile,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/login", 
    name: "login",
    component: Login 
  },
  {
    path: "/brands",
    redirect: "/categories"
  },
  {
    path: "/clothing-types",
    redirect: "/categories"
  },
  {
    path: "/buyers",
    redirect: "/customers"
  },
  {
    path: "/purchases",
    redirect: "/orders"
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

let initialized = false

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  if (!initialized) {
    initialized = true
    const restored = userStore.initializeFromStorage()
  }
  
  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      next('/login')
      return
    }
    
    if (to.meta.requiresOtp && !userStore.isOtpVerified) {
      next('/login')
      return
    }
    
    next()
  } else if (to.path === '/login' && userStore.isAuthenticated && userStore.isOtpVerified) {
    next('/categories')
  } else {
    next()
  }
})

export default router
