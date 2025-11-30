<template>
  <div class="profile-page">
    <div class="profile-card">
      <div class="profile-header">
        <div class="profile-icon">
          <i class="bi bi-person-circle"></i>
        </div>
        <h2>{{ user?.username || 'Пользователь' }}</h2>
      </div>

      <div class="profile-info">
        <div class="info-row">
          <span class="info-label">Имя пользователя:</span>
          <span class="info-value">{{ user?.username }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Email:</span>
          <span class="info-value">{{ user?.email || 'Не указан' }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Роль:</span>
          <span class="info-value">
            <span v-if="user?.is_superuser" class="badge bg-danger">Администратор</span>
            <span v-else class="badge bg-secondary">Пользователь</span>
          </span>
        </div>
      </div>

      <div class="profile-actions">
        <button @click="logout" class="btn-logout">
          <i class="bi bi-box-arrow-right"></i> Выйти
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()
const user = ref(null)

async function fetchUser() {
  try {
    const response = await axios.get('/userprofile/info/')
    user.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки профиля:', error)
  }
}

async function logout() {
  if (confirm('Вы уверены, что хотите выйти?')) {
    await userStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  fetchUser()
})
</script>

<style scoped>
.profile-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
  padding: 25px;
}

.profile-card {
  background: #fff0f5;
  border: 2px solid #ffb6c1;
  border-radius: 20px;
  padding: 40px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 10px 30px rgba(255, 105, 180, 0.2);
}

.profile-header {
  text-align: center;
  margin-bottom: 30px;
}

.profile-icon {
  font-size: 80px;
  color: #ff1493;
  margin-bottom: 15px;
}

.profile-header h2 {
  color: #d63384;
  margin: 0;
  font-size: 1.8em;
}

.profile-info {
  margin-bottom: 30px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  margin-bottom: 10px;
  background: white;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
}

.info-label {
  font-weight: bold;
  color: #d63384;
}

.info-value {
  color: #4b1a30;
}

.profile-actions {
  text-align: center;
}

.btn-logout {
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 15px;
  padding: 12px 30px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-logout:hover {
  background: #c82333;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(220, 53, 69, 0.3);
}

.badge {
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 0.9em;
}
</style>