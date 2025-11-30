<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <i class="bi bi-bag-heart-fill"></i>
        <h2>Магазин одежды</h2>
        <p>Добро пожаловать!</p>
      </div>

      <!-- Форма логина -->
      <form v-if="!showOtpInput" @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>
            <i class="bi bi-person-fill"></i>
            Имя пользователя
          </label>
          <input
            v-model="username"
            type="text"
            placeholder="Введите имя пользователя"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label>
            <i class="bi bi-lock-fill"></i>
            Пароль
          </label>
          <input
            v-model="password"
            type="password"
            placeholder="Введите пароль"
            required
            :disabled="loading"
          />
        </div>

        <button type="submit" class="btn-login" :disabled="loading">
          <span v-if="!loading">Войти</span>
          <span v-else>Загрузка...</span>
        </button>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>

      <!-- Форма ввода OTP -->
      <form v-else @submit.prevent="handleOtpVerify" class="otp-form">
        <div class="otp-info">
          <i class="bi bi-shield-lock-fill"></i>
          <p>Введите код подтверждения из консоли сервера</p>
          <p class="text-muted">Код отправлен для: {{ userStore.user?.email }}</p>
        </div>

        <div class="form-group">
          <label>
            <i class="bi bi-key-fill"></i>
            OTP код
          </label>
          <input
            v-model="otpCode"
            type="text"
            placeholder="Введите 6-значный код"
            maxlength="6"
            required
            :disabled="loading"
            class="otp-input"
          />
        </div>

        <button type="submit" class="btn-verify" :disabled="loading">
          <span v-if="!loading">Подтвердить</span>
          <span v-else>Проверка...</span>
        </button>

        <button type="button" @click="resetLogin" class="btn-back">
          <i class="bi bi-arrow-left"></i>
          Назад
        </button>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const otpCode = ref('')
const error = ref('')
const loading = ref(false)
const showOtpInput = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    const response = await userStore.login(username.value, password.value)
    
    if (response.otp_sent) {
      showOtpInput.value = true
      console.log('[Login] OTP отправлен, проверьте консоль сервера')
    }
  } catch (err) {
    error.value = err.message || 'Ошибка авторизации'
    console.error('[Login] Ошибка:', err)
  } finally {
    loading.value = false
  }
}

async function handleOtpVerify() {
  if (!otpCode.value || otpCode.value.length !== 6) {
    error.value = 'Введите корректный 6-значный код'
    return
  }

  error.value = ''
  loading.value = true

  try {
    const success = await userStore.verifyOtp(otpCode.value)
    
    if (success) {
      console.log('[Login] OTP подтвержден, переход на главную')
      router.push('/categories')
    } else {
      error.value = 'Неверный OTP код'
    }
  } catch (err) {
    error.value = err.message || 'Ошибка проверки OTP'
    console.error('[Login] Ошибка OTP:', err)
  } finally {
    loading.value = false
  }
}

function resetLogin() {
  showOtpInput.value = false
  otpCode.value = ''
  error.value = ''
  password.value = ''
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #fff0f5 0%, #ffe4e1 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border: 2px solid #ffb6c1;
  border-radius: 20px;
  padding: 40px;
  max-width: 450px;
  width: 100%;
  box-shadow: 0 10px 40px rgba(255, 105, 180, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header i {
  font-size: 60px;
  color: #ff1493;
  margin-bottom: 15px;
}

.login-header h2 {
  color: #d63384;
  margin: 0 0 10px 0;
  font-size: 1.8em;
}

.login-header p {
  color: #4b1a30;
  margin: 0;
  font-size: 1.1em;
}

.login-form,
.otp-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #d63384;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group input {
  padding: 12px 15px;
  border: 2px solid #ffb6c1;
  border-radius: 15px;
  background-color: #fff0f5;
  font-size: 1em;
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #ff1493;
  background-color: white;
}

.form-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.otp-input {
  text-align: center;
  font-size: 1.5em !important;
  letter-spacing: 8px;
  font-weight: bold;
}

.btn-login,
.btn-verify {
  background: #ff1493;
  color: white;
  border: none;
  border-radius: 15px;
  padding: 14px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-login:hover:not(:disabled),
.btn-verify:hover:not(:disabled) {
  background: #ff69b4;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 20, 147, 0.3);
}

.btn-login:disabled,
.btn-verify:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-back {
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 15px;
  padding: 10px;
  font-size: 1em;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-back:hover {
  background: #5a6268;
}

.otp-info {
  text-align: center;
  padding: 20px;
  background: #fff0f5;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
}

.otp-info i {
  font-size: 40px;
  color: #ff1493;
  margin-bottom: 10px;
}

.otp-info p {
  margin: 5px 0;
  color: #4b1a30;
}

.otp-info .text-muted {
  font-size: 0.9em;
  color: #999;
}

.error-message {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
  padding: 12px;
  border-radius: 10px;
  text-align: center;
  font-weight: 500;
}
</style>