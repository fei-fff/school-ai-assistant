/**
 * User store — Pinia
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginApi, registerApi, getMeApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))

  function setToken(val) {
    token.value = val
    localStorage.setItem('access_token', val)
  }

  function setUserInfo(info) {
    userInfo.value = info
    localStorage.setItem('user_info', JSON.stringify(info))
  }

  function clearAuth() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  async function login(credentials) {
    const res = await loginApi(credentials)
    setToken(res.data.access_token)
    setUserInfo(res.data.user)
    return res.data
  }

  async function register(data) {
    const res = await registerApi(data)
    return res.data
  }

  async function fetchMe() {
    const res = await getMeApi()
    setUserInfo(res.data)
    return res.data
  }

  function logout() {
    clearAuth()
  }

  return {
    token,
    userInfo,
    setToken,
    setUserInfo,
    clearAuth,
    login,
    register,
    fetchMe,
    logout,
  }
})
