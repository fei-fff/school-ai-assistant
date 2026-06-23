<template>
  <div class="uc">
    <div class="uc-msgs" ref="box">
      <div v-if="msgs.length === 0" class="uc-empty">
        <div class="uc-avatar-ai">AI</div>
        <p>你好，我是校园智能助手</p>
        <p class="uc-hint">可以问我课程问题、情绪困扰、或帮你找导师</p>
      </div>

      <div v-for="(m, i) in msgs" :key="i" :class="['uc-msg', m.role]">
        <template v-if="m.role === 'assistant'">
          <div class="uc-avatar-ai">AI</div>
          <div class="uc-bubble">
            <div class="uc-meta">
              <span class="uc-time">{{ m.time }}</span>
              <el-tag v-if="m.intent" size="small" type="info" effect="plain">{{ intentLabel(m.intent) }}</el-tag>
            </div>
            <div class="uc-text">{{ m.content }}</div>
          </div>
        </template>
        <template v-else>
          <div class="uc-bubble user">{{ m.content }}</div>
          <div class="uc-avatar-u">{{ userShortName }}</div>
        </template>
      </div>

      <div v-if="loading" class="uc-msg assistant">
        <div class="uc-avatar-ai">AI</div>
        <div class="uc-bubble">
          <div class="uc-typing"><span></span><span></span><span></span></div>
        </div>
      </div>
    </div>

    <div class="uc-bar">
      <el-input v-model="input" placeholder="输入消息，按回车发送..." size="large"
        @keyup.enter="send" :disabled="loading">
        <template #append><el-button :loading="loading" @click="send">发送</el-button></template>
      </el-input>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { sendMessage } from '@/api/chat'

const userStore = useUserStore()
const input = ref(''); const loading = ref(false); const msgs = ref([]); const box = ref(null)
const userShortName = computed(() => (userStore.userInfo?.username || 'U')[0].toUpperCase())

function intentLabel(i) {
  return {emotion:'情绪',mentor:'导师',knowledge:'知识'}[i] || i
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  const now = new Date().toLocaleTimeString('zh-CN', {hour:'2-digit',minute:'2-digit'})
  msgs.value.push({ role: 'user', content: text, time: now })
  input.value = ''; loading.value = true
  const history = msgs.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }))
  try {
    const res = await sendMessage(text, history)
    const d = res.data
    msgs.value.push({ role: 'assistant', content: d.answer, intent: d.intent,
      time: new Date().toLocaleTimeString('zh-CN', {hour:'2-digit',minute:'2-digit'}) })
  } catch {
    msgs.value.push({ role: 'assistant', content: '抱歉，出了点问题。', time: now })
  } finally {
    loading.value = false
    await nextTick(); if (box.value) box.value.scrollTop = box.value.scrollHeight
  }
}
</script>

<style scoped>
.uc { display: flex; flex-direction: column; height: 100%; }
.uc-msgs { flex: 1; overflow-y: auto; padding-right: 8px; }
.uc-empty { display: flex; flex-direction: column; align-items: center; padding-top: 60px; }
.uc-empty p { font-size: 15px; color: #303133; margin-top: 12px; }
.uc-hint { font-size: 12px !important; color: #c0c4cc !important; margin-top: 4px !important; }
.uc-msg { display: flex; gap: 8px; margin-bottom: 16px; align-items: flex-start; }
.uc-msg.user { justify-content: flex-end; }
.uc-avatar-ai { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg,#409eff,#337ecc);
  color:#fff; display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0; }
.uc-avatar-u { width: 32px; height: 32px; border-radius: 50%; background: #e8eaed;
  color:#606266; display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0; }
.uc-bubble { background: #f0f5ff; border-radius: 12px 12px 12px 2px; padding: 10px 14px; max-width: 70%; }
.uc-bubble.user { background: #409eff; color: #fff; border-radius: 12px 12px 2px 12px; }
.uc-meta { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
.uc-time { font-size: 11px; color: #909399; }
.uc-text { font-size: 14px; line-height: 1.6; white-space: pre-wrap; }
.uc-typing { display: flex; gap: 4px; padding: 4px 0; }
.uc-typing span { width: 6px; height: 6px; border-radius: 50%; background: #909399; animation: bounce 1.2s infinite; }
.uc-typing span:nth-child(2) { animation-delay: .2s; }
.uc-typing span:nth-child(3) { animation-delay: .4s; }
@keyframes bounce { 0%,60%,100% { transform: translateY(0); } 30% { transform: translateY(-4px); } }
.uc-bar { flex-shrink: 0; margin-top: 10px; }
</style>
