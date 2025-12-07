<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const loginForm = reactive({ username: '', password: '' })
const otpForm = reactive({ code: '' })
const error = ref('')
const loading = ref(false)
const showOtpInput = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    const response = await userStore.login(loginForm.username, loginForm.password)
    
    if (response.otp_sent) {
      showOtpInput.value = true
      ElMessage.info('OTP отправлен, проверьте консоль сервера')
    }
  } catch (err) {
    error.value = err.message || 'Ошибка авторизации'
  } finally {
    loading.value = false
  }
}

async function handleOtpVerify() {
  if (!otpForm.code || otpForm.code.length !== 6) {
    error.value = 'Введите корректный 6-значный код'
    return
  }

  error.value = ''
  loading.value = true

  try {
    const success = await userStore.verifyOtp(otpForm.code)
    
    if (success) {
      ElMessage.success('Вход выполнен')
      router.push('/categories')
    } else {
      error.value = 'Неверный OTP код'
    }
  } catch (err) {
    error.value = err.message || 'Ошибка проверки OTP'
  } finally {
    loading.value = false
  }
}

function resetLogin() {
  showOtpInput.value = false
  otpForm.code = ''
  error.value = ''
  loginForm.password = ''
}
</script>

<template>
  <div class="login-page">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>{{ showOtpInput ? 'Подтверждение' : 'Авторизация' }}</h2>
        </div>
      </template>


      <el-form v-if="!showOtpInput" @submit.prevent="handleLogin" :model="loginForm">
        <el-form-item label="Имя пользователя">
          <el-input v-model="loginForm.username" placeholder="Введите имя пользователя" :disabled="loading" />
        </el-form-item>

        <el-form-item label="Пароль">
          <el-input v-model="loginForm.password" type="password" placeholder="Введите пароль" :disabled="loading" show-password />
        </el-form-item>

        <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">
          Войти
        </el-button>

        <el-alert v-if="error" :title="error" type="error" :closable="false" style="margin-top: 15px" />
      </el-form>

      <el-form v-else @submit.prevent="handleOtpVerify" :model="otpForm">
  <el-alert title="Введите код из консоли сервера" type="info" :closable="false" style="margin-bottom: 20px">
    <template #default>
      <p style="margin: 5px 0 0 0; font-size: 0.9em">{{ userStore.user?.email }}</p>
    </template>
  </el-alert>

  <el-form-item label="OTP код">
    <el-input v-model="otpForm.code" placeholder="6-значный код" maxlength="6" :disabled="loading" style="text-align: center; font-size: 1.2em; letter-spacing: 4px" />
  </el-form-item>

  <div style="display: flex; justify-content: space-between;">
    <el-button type="primary" native-type="submit" :loading="loading" style="width: 48%">Подтвердить</el-button>
    <el-button @click="resetLogin" style="width: 48%">Назад</el-button>
  </div>

  <el-alert v-if="error" :title="error" type="error" :closable="false" style="margin-top: 15px" />
</el-form>

    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  font-weight: 700;
  color: #333;
}
</style>