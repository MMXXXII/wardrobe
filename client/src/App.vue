<template>
  <div class="container py-4">

    <!-- Новый красивый хедер -->
    <header v-if="$route.path !== '/login'" class="main-app-header">
      <div class="main-app-header-content">

        <div class="nav-left">
          <router-link class="nav-item" to="/categories">Категории</router-link>
          <router-link class="nav-item" to="/products">Товары</router-link>
          <router-link class="nav-item" to="/stores">Магазины</router-link>
          <router-link class="nav-item" to="/orders">Заказы</router-link>
          <router-link v-if="userStore.user && userStore.user.is_superuser" class="nav-item" to="/customers">
            Покупатели
          </router-link>
        </div>

        <div class="nav-right">
          <router-link v-if="userStore.isAuthenticated" class="profile-btn" to="/profile">
            <i class="bi bi-person-fill"></i>
          </router-link>
        </div>

      </div>
    </header>

    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from './stores/userStore'

const userStore = useUserStore()

onMounted(async () => {
  // Гарантировано загрузим профиль пользователя на старте
  if (!userStore.user) {
    try {
      await userStore.getUserInfo()
    } catch (e) {
      // Если не авторизован — user останется null и Покупатели не покажутся
    }
  }
})
</script>

<style scoped>
/* Главный хедер в едином стиле */
.main-app-header {
  background: linear-gradient(135deg, #fff5f8 0%, #f5f0ff 100%);
  padding: 26px 32px;
  border-radius: 24px;
  margin-bottom: 36px;
  box-shadow: 0 12px 45px rgba(255, 20, 147, 0.08);
  animation: headerDrop 0.6s ease;
}

/* Анимация – как в Orders Page */
@keyframes headerDrop {
  from {
    opacity: 0;
    transform: translateY(-28px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.main-app-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Навигация */
.nav-left {
  display: flex;
  gap: 28px;
}

/* Ссылки */
.nav-item {
  text-decoration: none;
  font-weight: 700;
  font-size: 1.15rem;
  color: #d63384;
  padding-bottom: 3px;
  position: relative;
  transition: 0.25s;
}

.nav-item:hover {
  color: #ff1493;
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 0;
  width: 0;
  height: 3px;
  background: linear-gradient(135deg, #ff6b9d, #d63384);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.nav-item:hover::after {
  width: 100%;
}

/* Кнопка профиля — стиль карточек */
.profile-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b9d, #d63384);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.35rem;
  transition: 0.25s;
  box-shadow: 0 5px 18px rgba(255, 20, 147, 0.25);
}

.profile-btn:hover {
  transform: scale(1.12);
  box-shadow: 0 10px 26px rgba(255, 20, 147, 0.35);
}
</style>
