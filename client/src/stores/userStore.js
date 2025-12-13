import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const isOtpVerified = ref(false)
  const isSuperUser = ref(false)
  const loading = ref(false)
  const error = ref(null)
  const pendingUsername = ref(null)

  function initializePending() {
    const savedPending = sessionStorage.getItem('pending_username')
    if (savedPending) {
      pendingUsername.value = savedPending
    }
  }

  async function login(usernameParam, passwordParam) {
    loading.value = true
    error.value = null

    const response = await axios.post('/userprofile/login/', {
      username: usernameParam,
      password: passwordParam,
    })

    loading.value = false

    if (response.data.is_authenticated === false && response.data.otp_sent) {
      user.value = {
        username: response.data.username,
        email: response.data.email,
        is_superuser: response.data.is_superuser || false,
      }
      pendingUsername.value = usernameParam
      sessionStorage.setItem('pending_username', usernameParam)
      return response.data
    } else {
      error.value = response.data.error || 'Ошибка авторизации'
      throw new Error(error.value)
    }
  }

  async function verifyOtp(otpKey) {
    loading.value = true
    error.value = null

    const response = await axios.post('/userprofile/otp-login/', {
      key: otpKey,
      username: pendingUsername.value,
    })

    loading.value = false

    if (response.data.success && response.data.is_authenticated) {
      await fetchUserInfo()
      pendingUsername.value = null
      sessionStorage.removeItem('pending_username')
      return true
    } else {
      error.value = response.data.error || 'Неверный OTP код'
      return false
    }
  }

  async function fetchUserInfo() {
    const response = await axios.get('/userprofile/info/', { 
      validateStatus: status => status < 500 
    })
    
    if (response.status === 200) {
      user.value = response.data
      isAuthenticated.value = true
      isSuperUser.value = response.data.is_superuser || false
      isOtpVerified.value = true
    } else if (response.status === 403) {
      resetAuthState()
    } else {
      resetAuthState()
    }
  }

  async function checkOtpStatus() {
    const response = await axios.get('/userprofile/otp-status/')
    isOtpVerified.value = response.data.otp_good
    return isOtpVerified.value
  }

  async function logout() {
    loading.value = true
    
    if (isAuthenticated.value) {
      await axios.post('/userprofile/logout/')
    }
    
    resetAuthState()
    sessionStorage.removeItem('pending_username')
    loading.value = false
  }

  function resetAuthState() {
    user.value = null
    isAuthenticated.value = false
    isOtpVerified.value = false
    isSuperUser.value = false
    pendingUsername.value = null
    error.value = null
  }

  return {
    user,
    isAuthenticated,
    isOtpVerified,
    isSuperUser,
    loading,
    error,
    pendingUsername,

    initializePending,
    login,
    verifyOtp,
    fetchUserInfo,
    checkOtpStatus,
    logout,
    resetAuthState,
  }
})