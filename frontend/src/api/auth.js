/**
 * Auth API — login, register, get current user.
 */
import http from './index'

export function loginApi(data) {
  return http.post('/auth/login', data)
}

export function registerApi(data) {
  return http.post('/auth/register', data)
}

export function getMeApi() {
  return http.get('/auth/me')
}
