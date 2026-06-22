<template>
  <div class="uc">
    <div class="uc-header">校园智能助手</div>

    <div class="uc-msgs" ref="box">
      <div v-if="msgs.length === 0" class="uc-empty">
        <el-icon :size="36"><ChatDotRound /></el-icon>
        <p>问我任何问题 — 知识、情绪还是导师建议。</p>
      </div>

      <div v-for="(m, i) in msgs" :key="i" :class="['uc-msg', m.role]">
        <div class="uc-label">{{ m.role === 'user' ? '你' : 'AI' }}</div>
        <div class="uc-content">{{ m.content }}</div>
        <div v-if="m.intent" class="uc-meta">
          <el-tag size="small" type="info">{{ m.intent }}</el-tag>
        </div>
      </div>

      <div v-if="loading" class="uc-msg assistant">
        <div class="uc-label">AI</div>
        <div class="uc-content uc-thinking">思考中...</div>
      </div>
    </div>

    <div class="uc-bar">
      <el-input v-model="input" placeholder="输入消息..." size="large"
                @keyup.enter="send" :disabled="loading">
        <template #append>
          <el-button :loading="loading" @click="send">发送</el-button>
        </template>
      </el-input>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ChatDotRound } from '@element-plus/icons-vue'
import { sendMessage } from '@/api/chat'

const input = ref('')
const loading = ref(false)
const msgs = ref([])
const box = ref(null)

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

  msgs.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true

  const history = msgs.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }))

  try {
    const res = await sendMessage(text, history)
    const d = res.data
    msgs.value.push({ role: 'assistant', content: d.answer, intent: d.intent })
  } catch {
    msgs.value.push({ role: 'assistant', content: '抱歉，出了点问题。' })
  } finally {
    loading.value = false
    await nextTick()
    if (box.value) box.value.scrollTop = box.value.scrollHeight
  }
}
</script>

<style scoped>
.uc { display: flex; flex-direction: column; height: 100%; }
.uc-header { font-size: 16px; font-weight: 600; padding: 8px 0 12px; border-bottom: 1px solid #e8eaed; margin-bottom: 8px; flex-shrink: 0; }
.uc-msgs { flex: 1; overflow-y: auto; padding-right: 4px; }
.uc-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 180px; color: #909399; }
.uc-empty p { margin-top: 8px; font-size: 13px; }
.uc-msg { margin-bottom: 14px; }
.uc-msg.user .uc-label { color: #409eff; }
.uc-msg.assistant .uc-label { color: #67c23a; }
.uc-label { font-size: 11px; font-weight: 600; margin-bottom: 2px; }
.uc-content { line-height: 1.6; white-space: pre-wrap; }
.uc-thinking { color: #909399; font-style: italic; }
.uc-meta { margin-top: 4px; }
.uc-bar { flex-shrink: 0; margin-top: 8px; }
</style>
