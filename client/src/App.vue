<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/userStore'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const leftLinks = [
  { path: '/categories', label: 'Категории' },
  { path: '/products', label: 'Товары' },
  { path: '/stores', label: 'Магазины' },
  { path: '/orders', label: 'Заказы' },
  { path: '/customers', label: 'Покупатели', admin: true }
]

const showNav = computed(() => route.path !== '/login' && userStore.isAuthenticated)

const openDjangoAdmin = () => {
  window.open('http://localhost:8000/admin/', '_blank')
}
</script>

<template>
  <div id="app">
    <nav v-if="showNav" class="main-nav">
      <a
        v-for="link in leftLinks"
        :key="link.path"
        v-show="!link.admin || userStore.user?.is_superuser"
        @click.prevent="router.push(link.path)"
        class="nav-link"
        :class="{ active: route.path === link.path }"
      >
        {{ link.label }}
      </a>

      <div class="spacer"></div>

      <a
        @click.prevent="router.push('/profile')"
        class="nav-link profile-link"
        :class="{ active: route.path === '/profile' }"
      >
        {{ userStore.user?.username || userStore.user?.email || 'Профиль' }}
      </a>

      <a
        v-if="userStore.user?.is_superuser"
        @click.prevent="openDjangoAdmin"
        class="nav-link admin-link"
      >
        Админка
      </a>
    </nav>

    <router-view />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}

#app {
  min-height: 100vh;
  background: #f5f5f5;
}

.main-nav {
  background: white;
  padding: 15px 30px 15px 150px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 25px;
}

.spacer {
  flex-grow: 1;
  min-width: 0;
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-weight: 700;
  padding: 8px 16px;
  border-radius: 4px;
  transition: all 0.3s;
  cursor: pointer;
  font-size: 0.95rem;
}

.nav-link:hover {
  background: #f0f0f0;
  color: #409eff;
}

.nav-link.active {
  color: #409eff;
  background: #ecf5ff;
}

.profile-link {
  font-weight: 800;
  font-size: 1rem;
}

.admin-link {
  background: #dc3545;
  color: white;
  padding: 10px 20px;
}

.admin-link:hover {
  background: #c82333;
  color: white;
}
</style>
