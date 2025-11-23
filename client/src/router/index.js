import { createRouter, createWebHistory } from "vue-router"
import { useUserStore } from "../stores/userStore"
import Brands from "../components/Brands.vue"
import ClothingTypes from "../components/ClothingTypes.vue"
import Buyers from "../components/Buyers.vue"
import Stores from "../components/Stores.vue"
import Purchases from "../components/Purchases.vue"
import Profile from "../components/User.vue"
import Login from "../components/Login.vue"

const routes = [
  { 
    path: "/", 
    redirect: "/brands" 
  },
  { 
    path: "/brands", 
    component: Brands,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/clothing-types", 
    component: ClothingTypes,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/buyers", 
    component: Buyers,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/stores", 
    component: Stores,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/purchases", 
    component: Purchases,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/profile", 
    component: Profile,
    meta: { requiresAuth: true, requiresOtp: true }
  },
  { 
    path: "/login", 
    component: Login 
  },
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
    console.log('[v0] Store initialized from storage:', restored)
  }
  
  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      console.log('[v0] Not authenticated, redirecting to login')
      next('/login')
      return
    }
    
    if (to.meta.requiresOtp && !userStore.isOtpVerified) {
      console.log('[v0] OTP not verified, redirecting to login')
      next('/login')
      return
    }
    
    next()
  } else if (to.path === '/login' && userStore.isAuthenticated && userStore.isOtpVerified) {
    console.log('[v0] Already authenticated, redirecting to brands')
    next('/brands')
  } else {
    next()
  }
})

export default router
