<template>
  <div class="know-page">
    <h2>上传知识文档</h2>

    <el-upload
      ref="uploadRef"
      class="know-upload"
      drag
      :auto-upload="false"
      :limit="1"
      :on-change="onFileChange"
      :on-remove="onFileRemove"
      :file-list="fileList"
      accept=".txt,.pdf,.docx,.md,.csv,.pptx"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">拖拽文件或<em>点击选择</em></div>
      <template #tip>
        <div class="el-upload__tip">支持 TXT / PDF / DOCX / MD / CSV / PPTX，最大 {{ maxSizeMb }}MB</div>
      </template>
    </el-upload>

    <el-input
      v-model="title"
      placeholder="文档标题（留空使用文件名）"
      style="max-width: 420px; margin-top: 16px"
      clearable
    />

    <div style="margin-top: 16px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap">
      <el-button type="primary" :loading="uploading" @click="handleUpload" :disabled="!selectedFile">
        {{ uploading ? '上传中...' : '上传' }}
      </el-button>
      <el-button
        v-if="uploadedDoc && !processing"
        type="success"
        @click="handleProcess"
      >
        立即处理
      </el-button>
      <el-button
        v-if="processing"
        type="warning"
        :loading="true"
      >
        处理中...
      </el-button>
    </div>

    <el-alert
      v-if="uploadError"
      :title="uploadError"
      type="error"
      :closable="true"
      @close="uploadError = ''"
      style="margin-top: 12px; max-width: 500px"
    />

    <el-alert
      v-if="uploadResult && !processing"
      :title="uploadResult"
      type="success"
      :closable="false"
      style="margin-top: 12px; max-width: 500px"
    />

    <div v-if="processResult" style="margin-top: 16px">
      <el-alert
        :title="processSummary"
        :type="processAllOk ? 'success' : 'warning'"
        :closable="false"
        style="margin-bottom: 12px; max-width: 500px"
      />
      <el-descriptions :column="2" border size="small" style="max-width: 500px">
        <el-descriptions-item label="文档 ID">{{ uploadedDoc?.id }}</el-descriptions-item>
        <el-descriptions-item label="阶段">
          <el-tag :type="stepType(processResult.current_step)" size="small">
            {{ stepLabel(processResult.current_step) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="解析">
          <el-tag :type="statusType(processResult.parse_status)" size="small">
            {{ processResult.parse_status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="摘要">
          <el-tag :type="statusType(processResult.summary_status)" size="small">
            {{ processResult.summary_status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="分类">
          <el-tag :type="statusType(processResult.classify_status)" size="small">
            {{ processResult.classify_status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="向量化">
          <el-tag :type="statusType(processResult.embedding_status)" size="small">
            {{ processResult.embedding_status }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadDocument, processDocument } from '@/api/knowledge'

const uploadRef = ref(null)
const title = ref('')
const selectedFile = ref(null)
const fileList = ref([])
const uploading = ref(false)
const processing = ref(false)
const uploadedDoc = ref(null)
const uploadResult = ref('')
const uploadError = ref('')
const processResult = ref(null)
const maxSizeMb = 50

const processAllOk = computed(() => {
  if (!processResult.value) return false
  const r = processResult.value
  return ['parse_status', 'summary_status', 'classify_status', 'embedding_status']
    .every((k) => r[k] === 'success')
})

const processSummary = computed(() => {
  if (!processResult.value) return ''
  const r = processResult.value
  const ok = ['parse_status', 'summary_status', 'classify_status', 'embedding_status']
    .filter((k) => r[k] === 'success').length
  if (ok === 4) return '全部处理完成，文档已就绪可查询'
  if (r.current_step === 'failed') return `处理失败: ${r.current_step} 阶段出错`
  return `处理完成: ${ok}/4 个阶段成功`
})

function onFileChange(file) {
  selectedFile.value = file.raw
}

function onFileRemove() {
  selectedFile.value = null
}

async function handleUpload() {
  if (!selectedFile.value) return
  uploading.value = true
  uploadError.value = ''
  uploadResult.value = ''
  processResult.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    if (title.value) {
      formData.append('title', title.value)
    }
    const res = await uploadDocument(formData)
    uploadedDoc.value = res.data
    uploadResult.value = `上传成功，文档 ID: ${res.data.id}`
  } catch (e) {
    uploadError.value = e?.response?.data?.message || '上传失败，请检查文件格式和大小后重试'
  } finally {
    uploading.value = false
  }
}

async function handleProcess() {
  if (!uploadedDoc.value) return
  processing.value = true
  uploadError.value = ''

  try {
    const res = await processDocument(uploadedDoc.value.id)
    processResult.value = res.data
  } catch (e) {
    uploadError.value = e?.response?.data?.message || '处理请求失败'
  } finally {
    processing.value = false
  }
}

function stepLabel(step) {
  const map = {
    uploaded: '已上传', parsed: '已解析', summarized: '已摘要',
    classified: '已分类', embedded: '已向量化', ready: '就绪', failed: '失败',
  }
  return map[step] || step
}

function stepType(step) {
  const map = { ready: 'success', failed: 'danger' }
  return map[step] || 'info'
}

function statusType(s) {
  const map = { success: 'success', processing: 'warning', failed: 'danger' }
  return map[s] || 'info'
}
</script>

<style scoped>
.know-page { padding: 0 4px; }
.know-page h2 { font-size: 18px; font-weight: 600; margin-bottom: 16px; }
.know-upload { max-width: 500px; }
</style>
