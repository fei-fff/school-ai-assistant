import http from './index'

export function sendMessage(message, history = []) {
  return http.post('/chat', { message, history })
}
