<script setup>
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const username = ref('')
const password = ref('')

onMounted(async () => {
  await userStore.fetchUserInfo()
  if (userStore.isAuthenticated) {
    router.replace('/products')
  }
})

async function handleLogin() {
  await userStore.login(username.value, password.value)
  router.replace('/products')
}

async function handleLogout() {
  await userStore.logout()
  router.replace('/login')
}
</script>

<template>
  <el-container class="full-screen" v-if="route.path === '/profile'">
    <el-card class="profile-card" shadow="hover">
      <template #header>
        <span>Профиль пользователя</span>
      </template>

      <el-progress v-if="userStore.loading" indeterminate />

      <div v-else-if="userStore.user">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Имя пользователя">
            {{ userStore.user.username }}
          </el-descriptions-item>
          <el-descriptions-item label="Email">
            {{ userStore.user.email }}
          </el-descriptions-item>
        </el-descriptions>

        <el-button type="danger" class="mt" @click="handleLogout" block>
          Выход
        </el-button>
      </div>
    </el-card>
  </el-container>

  <el-container class="full-screen" v-else>
    <el-card class="login-card" shadow="always">
      <el-form @submit.prevent="handleLogin">
        <h2 class="title">Вход в систему</h2>

        <el-form-item>
          <el-input
            v-model="username"
            placeholder="Имя пользователя"
            clearable
            autocomplete="username"
            size="large"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="password"
            type="password"
            placeholder="Пароль"
            show-password
            clearable
            autocomplete="current-password"
            size="large"
          />
        </el-form-item>

        <el-form-item class="actions">
          <el-button
            type="primary"
            :loading="userStore.loading"
            block
            size="large"
            native-type="submit"
          >
            Войти
          </el-button>
        </el-form-item>

        <el-alert
          v-if="userStore.error"
          title="Ошибка"
          type="error"
          show-icon
          class="alert"
        />
      </el-form>
    </el-card>
  </el-container>
</template>


<style scoped>
.full-screen {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  width: 100%;
  max-width: 480px;
  padding: 32px 28px;
}

.profile-card {
  width: 100%;
  max-width: 600px;
}

.title {
  text-align: center;
  margin-bottom: 28px;
}

.actions {
  margin-top: 20px;
}

.alert {
  margin-top: 20px;
}

.mt {
  margin-top: 20px;
}

</style>
