<template>
  <div class="container py-4">
    <!-- Навбар виден только если не на /login -->
    <nav v-if="$route.path !== '/login'" class="mb-4 d-flex justify-content-between align-items-center">
      <div class="categories">
        <router-link class="category-link" to="/brands">Бренды</router-link>
        <router-link class="category-link" to="/clothing-types">Типы одежды</router-link>
        <router-link class="category-link" to="/buyers">Покупатели</router-link>
        <router-link class="category-link" to="/purchases">Покупки</router-link>
        <router-link class="category-link" to="/stores">Магазины</router-link>
      </div>

      <!-- Кнопка Профиля -->
      <div class="d-flex align-items-center">
        <router-link 
          v-if="userStore.isAuthenticated" 
          class="profile-btn" 
          to="/profile"
        >
          <i class="bi bi-person-fill"></i>
        </router-link>
      </div>
    </nav>

    <router-view />
  </div>
</template>

<script setup>
import { useUserStore } from './stores/userStore'

const userStore = useUserStore()
</script>

<style scoped>
/* Кнопка профиля */
.profile-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffb6c1, #ff69b4);
  color: white;
  font-size: 1.2rem;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.profile-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(255, 105, 180, 0.4);
}

.profile-btn i {
  line-height: 1;
}

/* Категории текстом */
.categories {
  display: flex;
  gap: 20px;
  font-weight: bold;
}

.category-link {
  text-decoration: none;
  color: #d63384; /* мягкий розовый */
  font-size: 1.1rem;
  transition: all 0.25s;
  position: relative;
}

.category-link::after {
  content: '';
  display: block;
  height: 2px;
  width: 0;
  background: #ff69b4;
  transition: width 0.3s;
  position: absolute;
  bottom: -4px;
  left: 0;
}

.category-link:hover {
  color: #ff1493;
}

.category-link:hover::after {
  width: 100%;
}
</style>
