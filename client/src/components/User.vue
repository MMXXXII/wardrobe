<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()
const user = ref(null)
const logoutVisible = ref(false)

async function fetchUser() {
  try {
    const response = await axios.get('/userprofile/info/')
    user.value = response.data
  } catch (error) {
    ElMessage.error('Ошибка загрузки профиля')
  }
}

async function logout() {
  await userStore.logout()
  logoutVisible.value = false
  ElMessage.success('Вы вышли из системы')
  router.push('/login')
}

onMounted(() => {
  fetchUser()
})
</script>

<template>
  <div class="page">
    <el-header>
      <h1>Профиль</h1>
    </el-header>

    <el-card>
      <el-descriptions title="Информация о пользователе" :column="1" border>
        <el-descriptions-item label="Имя пользователя">{{ user?.username || 'Не указано' }}</el-descriptions-item>
        <el-descriptions-item label="Email">{{ user?.email || 'Не указан' }}</el-descriptions-item>
        <el-descriptions-item label="Роль">
          <el-tag v-if="user?.is_superuser" type="danger">Администратор</el-tag>
          <el-tag v-else type="info">Пользователь</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card>
      <div class="profile-actions">
        <el-button type="danger" @click="logoutVisible = true">Выйти</el-button>
      </div>
    </el-card>

    <el-dialog v-model="logoutVisible" title="Подтверждение выхода" width="400px">
      <p>Вы уверены, что хотите выйти из системы?</p>
      <template #footer>
        <el-button @click="logoutVisible = false">Отмена</el-button>
        <el-button type="danger" @click="logout">Выйти</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-actions {
  text-align: center;
  padding: 20px 0;
}

h1 {
  margin-bottom: 20px;
}

.el-card {
  margin-bottom: 20px;
}
</style>