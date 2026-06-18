/**
 * Axios 实例封装
 * - 自动携带 Bearer Token
 * - 401 自动跳转登录页
 * - 统一错误提示
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

// Request interceptor — attach token
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor — normalize errors
http.interceptors.response.use(
  (response) => {
    const body = response.data
    // If the API returns a non-2xx business code (like 400), treat it as an error
    if (body.code && body.code !== 200 && body.code !== 201) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(new Error(body.message))
    }
    return body
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      router.push('/login')
      ElMessage.warning('登录已过期，请重新登录')
    } else if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('网络错误，请稍后重试')
    }
    return Promise.reject(error)
  },
)

export default http
