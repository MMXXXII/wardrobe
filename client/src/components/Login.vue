<template>
  <div class="login-container">
    <div class="avatar">
      <i class="bi bi-person-fill"></i>
    </div>
    <h2>Вход в аккаунт</h2>

    <!-- Форма логина -->
    <form v-if="!showOtpInput" @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">Имя пользователя:</label>
        <input type="text" v-model="username" id="username" required />
      </div>
      <div class="form-group">
        <label for="password">Пароль:</label>
        <input type="password" v-model="password" id="password" required />
      </div>

      <button type="submit" :disabled="userStore.loading">
        {{ userStore.loading ? 'Загрузка...' : 'Далее' }}
      </button>
    </form>

    <!-- Форма OTP -->
    <form v-else @submit.prevent="handleOtpSubmit">
      <div class="otp-info">
        <p class="info-title">Введите код подтверждения</p>
        <p class="info-text">Код действителен 5 минут</p>
      </div>
      <div class="form-group">
        <label for="otp">Код подтверждения:</label>
        <input type="text" v-model="otpCode" id="otp" required maxlength="6" inputmode="numeric" placeholder="000000"/>
      </div>

      <button type="submit" :disabled="userStore.loading || otpCode.length !== 6">
        {{ userStore.loading ? 'Проверка...' : 'Подтвердить' }}
      </button>
      <button type="button" @click="handleBack" class="back-btn" :disabled="userStore.loading">
        Назад
      </button>
    </form>

    <div v-if="userStore.error" class="error-message">
      {{ userStore.error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const otpCode = ref('')
const showOtpInput = ref(false)

async function handleLogin() {
  try {
    const result = await userStore.login(username.value, password.value)
    showOtpInput.value = true      // показываем OTP
    userStore.error = null
  } catch (err) {
    console.error(err)
  }
}

async function handleOtpSubmit() {
  try {
    const success = await userStore.verifyOtp(otpCode.value)
    if (success) {
      username.value = ''
      password.value = ''
      otpCode.value = ''
      showOtpInput.value = false
      router.push('/brands')
    }
  } catch (err) {
    console.error(err)
  }
}

function handleBack() {
  showOtpInput.value = false
  username.value = ''
  password.value = ''
  otpCode.value = ''
  userStore.error = null
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 35px 25px;
  border-radius: 20px;
  background: linear-gradient(145deg, #ffe4ec, #fff0f5);
  box-shadow: 0 12px 25px rgba(255, 105, 180, 0.2);
  text-align: center;
  color: #4b1a30;
  font-family: 'Arial', sans-serif;
}

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

h2 {
  margin-bottom: 25px;
  color: #d63384;
  font-weight: bold;
}

.form-group {
  margin-bottom: 15px;
  text-align: left;
}

label {
  font-weight: bold;
  margin-bottom: 5px;
  display: block;
}

input {
  width: 100%;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
  box-sizing: border-box;
  transition: all 0.25s;
}

input:focus {
  outline: none;
  border-color: #ff69b4;
  box-shadow: 0 0 8px rgba(255, 105, 180, 0.3);
  background-color: #ffe4ec;
}

button {
  width: 100%;
  padding: 12px;
  border-radius: 25px;
  border: none;
  font-weight: bold;
  font-size: 16px;
  margin-top: 10px;
  cursor: pointer;
  background: #ff1493;
  color: white;
  transition: all 0.25s;
}

button:hover:not(:disabled) {
  background: #ff69b4;
  box-shadow: 0 6px 15px rgba(255, 20, 147, 0.4);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.back-btn {
  background: #6c757d;
}

.back-btn:hover:not(:disabled) {
  background: #5a6268;
}

.error-message {
  color: red;
  margin-top: 10px;
  padding: 10px;
  background-color: #ffe6e6;
  border-radius: 4px;
}

.otp-info {
  background-color: #fff0f5;
  border-left: 4px solid #ff1493;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.info-title {
  margin: 0 0 10px 0;
  font-weight: bold;
  color: #d63384;
}

.info-text {
  margin: 0;
  color: #666;
  font-size: 14px;
}
</style>
