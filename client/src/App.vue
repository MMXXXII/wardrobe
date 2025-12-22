<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/userStore'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const links = [
  { path: '/categories', label: 'Категории' },
  { path: '/products', label: 'Товары' },
  { path: '/stores', label: 'Магазины' },
  { path: '/orders', label: 'Заказы' },
  { path: '/customers', label: 'Покупатели', admin: true },
  { path: '/profile', label: 'Профиль' }
]

const showNav = computed(() => userStore.isAuthenticated)
</script>

<template>
  <div>
    <nav v-if="showNav">
      <button
        v-for="link in links"
        :key="link.path"
        v-show="!link.admin || userStore.user?.is_superuser"
        @click="router.push(link.path)"
      >
        {{ link.label }}
      </button>
    </nav>

    <router-view />
  </div>
</template>
