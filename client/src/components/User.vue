<template>
  <div class="profile-container">
    <!-- Аватарка -->
    <div class="avatar">
      <i class="bi bi-person-fill"></i>
    </div>

    <h2>Профиль пользователя</h2>

    <!-- Загрузка -->
    <div v-if="userStore.loading" class="loading">Загрузка...</div>

    <!-- Информация о пользователе -->
    <div v-else-if="userStore.user" class="user-info">
      <p><strong>Имя пользователя:</strong> {{ userStore.user.username }}</p>
      <p><strong>Email:</strong> {{ userStore.user.email }}</p>

      <!-- Кнопка Админки для всех -->
      <a href="http://localhost:5173/admin" class="admin-btn" target="_blank">
        Админка
      </a>

      <!-- Кнопка выхода -->
      <button @click="handleLogout" class="logout-btn">Выход</button>
    </div>

    <!-- Ошибка -->
    <div v-else-if="userStore.error" class="error-message">
      {{ userStore.error }}
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore.js'

const router = useRouter()
const userStore = useUserStore()

onMounted(() => {
  if (!userStore.isAuthenticated) {
    router.push('/login')
  }
})

watch(
  () => userStore.user,
  (newUser) => {
    if (!newUser) {
      router.push('/login')
    }
  }
)

async function handleLogout() {
  try {
    await userStore.logout()
    router.push('/login')
  } catch (err) {
    console.error('Ошибка при выходе:', err)
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 500px;
  margin: 40px auto;
  padding: 35px 25px;
  border-radius: 20px;
  background: linear-gradient(145deg, #ffe4ec, #fff0f5);
  box-shadow: 0 12px 25px rgba(255, 105, 180, 0.2);
  color: #4b1a30;
  font-family: 'Arial', sans-serif;
  text-align: center;
}

/* Аватарка */
.avatar {
  width: 90px;
  height: 90px;
  margin: -60px auto 20px;
  background: linear-gradient(135deg, #ffb6c1, #ff69b4);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2.5rem;
  color: white;
  box-shadow: 0 6px 15px rgba(255, 105, 180, 0.3);
  border: 4px solid white;
}

/* Заголовок */
h2 {
  margin-bottom: 25px;
  color: #d63384;
  font-weight: bold;
}

/* Информация о пользователе */
.user-info p {
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 192, 203, 0.5);
  font-size: 16px;
}

/* Кнопка Админки */
.admin-btn {
  display: inline-block;
  width: 100%;
  padding: 12px 0;
  margin-top: 15px;
  border-radius: 25px;
  font-weight: bold;
  font-size: 16px;
  text-decoration: none;
  color: white;
  background: #ff1493;
  transition: all 0.25s ease;
}

.admin-btn:hover {
  background: #ff69b4;
  box-shadow: 0 6px 15px rgba(255, 20, 147, 0.4);
}

/* Кнопка выхода */
.logout-btn {
  width: 100%;
  padding: 12px 0;
  border-radius: 25px;
  font-weight: bold;
  font-size: 16px;
  margin-top: 15px;
  cursor: pointer;
  transition: all 0.25s ease;
  border: none;
  background: #ff6f91;
  color: white;
}

.logout-btn:hover {
  background: #ff4c7d;
  box-shadow: 0 6px 15px rgba(255, 76, 125, 0.4);
}

/* Загрузка и ошибка */
.loading {
  font-weight: bold;
  color: #d63384;
  padding: 20px;
}

.error-message {
  color: #c71585;
  font-weight: bold;
  margin-top: 10px;
}
</style>
