// src/router/index.js
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
    name: "categories",  // ← ДОБАВИЛИ name
    component: Categories,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/stores", 
    name: "stores",      // ← ДОБАВИЛИ name
    component: Stores,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/products", 
    name: "products",    // ← ДОБАВИЛИ name
    component: Products,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/customers", 
    name: "customers",   // ← ДОБАВИЛИ name
    component: Customers,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/orders", 
    name: "orders",      // ← ДОБАВИЛИ name
    component: Orders,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/profile", 
    name: "profile",     // ← ДОБАВИЛИ name
    component: Profile,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/login", 
    name: "login",
    component: Login 
  },
  // перенаправления...
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
    console.log('[Store] Initialized from storage:', restored)
  }
  
  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      console.log('[Router] Not authenticated, redirecting to login')
      next('/login')
      return
    }
    
    if (to.meta.requiresOtp && !userStore.isOtpVerified) {
      console.log('[Router] OTP not verified, redirecting to login')
      next('/login')
      return
    }
    
    next()
  } else if (to.path === '/login' && userStore.isAuthenticated && userStore.isOtpVerified) {
    console.log('[Router] Already authenticated, redirecting to categories')
    next('/categories')
  } else {
    next()
  }
})

export default router
