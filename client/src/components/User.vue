<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const userStore = useUserStore()

const logoutVisible = ref(false)

async function logout()
{
  await userStore.logout()
  logoutVisible.value = false
  ElMessage.success('Вы вышли из системы')
  router.push('/login')
}

onMounted(async () =>
{
  await userStore.fetchUserInfo()
})
</script>

<template>
  <div>
    <h1>Профиль</h1>

    <div>
      <div>
        Имя пользователя:
        {{ userStore.user?.username || 'Не указано' }}
      </div>

      <div>
        Email:
        {{ userStore.user?.email || 'Не указан' }}
      </div>

      <div>
        Роль:
        {{ userStore.user?.is_superuser ? 'Администратор' : 'Пользователь' }}
      </div>
    </div>

    <el-button type="danger" @click="logoutVisible = true">
      Выйти
    </el-button>

    <el-dialog v-model="logoutVisible" title="Выход">
      <div>Вы уверены, что хотите выйти?</div>

      <el-button @click="logoutVisible = false">
        Отмена
      </el-button>

      <el-button type="danger" @click="logout">
        Выйти
      </el-button>
    </el-dialog>
  </div>
</template>
