<template>
  <div class="know-qa">
    <h2>AI 知识库问答</h2>

    <!-- Chat area -->
    <div class="qa-messages" ref="msgBox">
      <div v-if="messages.length === 0" class="qa-empty">
        <el-icon :size="40"><ChatDotSquare /></el-icon>
        <p>向校园知识库提问，获取基于文档的智能回答</p>
      </div>

      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="['qa-msg', msg.role === 'user' ? 'qa-user' : 'qa-ai']"
      >
        <div class="qa-role">{{ msg.role === 'user' ? '你' : 'AI' }}</div>
        <div class="qa-content">
          <div v-if="msg.role === 'assistant'" class="qa-answer">{{ msg.answer }}</div>
          <div v-else>{{ msg.content }}</div>

          <div v-if="msg.sources && msg.sources.length" class="qa-sources">
            <p class="qa-sources-title">引用来源</p>
            <div v-for="(s, si) in msg.sources" :key="si" class="qa-source-item">
              <span class="qa-source-score">{{ (s.score * 100).toFixed(0) }}%</span>
              <span class="qa-source-doc">{{ s.metadata?.title || '文档 #' + s.document_id }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="qa-msg qa-ai">
        <div class="qa-content">思考中...</div>
      </div>
    </div>

    <!-- Input area -->
    <div class="qa-input-bar">
      <el-input
        v-model="question"
        placeholder="输入问题，如：红黑树的插入时间复杂度是多少？"
        @keyup.enter="handleAsk"
        :disabled="loading"
        size="large"
      >
        <template #append>
          <el-button :loading="loading" @click="handleAsk" :icon="Promotion">提问</el-button>
        </template>
      </el-input>
      <div class="qa-input-options">
        <span>检索片段数:</span>
        <el-input-number v-model="topK" :min="1" :max="20" size="small" style="width: 80px" />
        <span>相似度阈值:</span>
        <el-input-number v-model="threshold" :min="0" :max="1" :step="0.1" size="small" style="width: 80px" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ChatDotSquare, Promotion } from '@element-plus/icons-vue'
import { queryKnowledge } from '@/api/knowledge'

const question = ref('')
const topK = ref(5)
const threshold = ref(0.3)
const loading = ref(false)
const messages = ref([])
const msgBox = ref(null)

async function handleAsk() {
  const q = question.value.trim()
  if (!q || loading.value) return

  messages.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true

  try {
    const res = await queryKnowledge({
      question: q,
      top_k: topK.value,
      similarity_threshold: threshold.value,
    })
    const data = res.data
    messages.value.push({
      role: 'assistant',
      answer: data.answer,
      sources: data.sources || [],
      scores: data.scores || [],
      chunkCount: data.chunk_count || 0,
    })
  } catch {
    messages.value.push({
      role: 'assistant',
      answer: '抱歉，查询知识库时出现错误，请稍后重试。',
      sources: [],
      scores: [],
    })
  } finally {
    loading.value = false
    await nextTick()
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
  }
}
</script>

<style scoped>
.know-qa { display: flex; flex-direction: column; height: 100%; }
.know-qa h2 { font-size: 18px; font-weight: 600; margin-bottom: 12px; flex-shrink: 0; }

.qa-messages { flex: 1; overflow-y: auto; padding-right: 8px; margin-bottom: 12px; }
.qa-empty { display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 200px; color: #909399; }
.qa-empty p { margin-top: 8px; font-size: 13px; }

.qa-msg { margin-bottom: 16px; }
.qa-role { font-size: 12px; font-weight: 600; margin-bottom: 4px; }
.qa-user .qa-role { color: #409eff; }
.qa-ai .qa-role { color: #67c23a; }
.qa-answer { line-height: 1.7; white-space: pre-wrap; }

.qa-sources { margin-top: 10px; padding: 10px 12px; background: #f8f9fc; border-radius: 6px;
  border: 1px solid #e8eaed; }
.qa-sources-title { font-size: 12px; color: #909399; margin-bottom: 6px; font-weight: 600; }
.qa-source-item { font-size: 12px; padding: 3px 0; display: flex; align-items: center; gap: 8px; }
.qa-source-score { color: #409eff; font-weight: 600; min-width: 36px; }
.qa-source-doc { color: #606266; }

.qa-input-bar { flex-shrink: 0; }
.qa-input-options { display: flex; align-items: center; gap: 8px; margin-top: 8px;
  font-size: 12px; color: #909399; }
</style>
