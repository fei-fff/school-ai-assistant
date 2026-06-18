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
        <div class="el-upload__tip">支持 TXT / PDF / DOCX / MD / CSV / PPTX</div>
      </template>
    </el-upload>

    <el-input
      v-model="title"
      placeholder="文档标题（留空使用文件名）"
      style="max-width: 400px; margin-top: 16px"
      clearable
    />

    <div style="margin-top: 16px; display: flex; gap: 12px; align-items: center">
      <el-button type="primary" :loading="uploading" @click="handleUpload" :disabled="!selectedFile">
        上传
      </el-button>
      <el-button v-if="uploadedDoc" type="success" :loading="processing" @click="handleProcess">
        立即处理
      </el-button>
    </div>

    <el-alert
      v-if="uploadResult"
      :title="uploadResult"
      type="success"
      :closable="false"
      style="margin-top: 16px; max-width: 500px"
    />

    <div v-if="processResult" style="margin-top: 16px">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="文档 ID">{{ uploadedDoc?.id }}</el-descriptions-item>
        <el-descriptions-item label="当前阶段">
          <el-tag :type="stepType(processResult.current_step)" size="small">
            {{ stepLabel(processResult.current_step) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="解析">{{ processResult.parse_status }}</el-descriptions-item>
        <el-descriptions-item label="摘要">{{ processResult.summary_status }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ processResult.classify_status }}</el-descriptions-item>
        <el-descriptions-item label="向量化">{{ processResult.embedding_status }}</el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
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
const processResult = ref(null)

function onFileChange(file) {
  selectedFile.value = file.raw
}

function onFileRemove() {
  selectedFile.value = null
}

async function handleUpload() {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    if (title.value) {
      formData.append('title', title.value)
    }
    const res = await uploadDocument(formData)
    uploadedDoc.value = res.data
    uploadResult.value = `上传成功！文档 ID: ${res.data.id}，点击"立即处理"启动流水线`
    ElMessage.success('上传成功')
  } catch {
    // handled by interceptor
  } finally {
    uploading.value = false
  }
}

async function handleProcess() {
  if (!uploadedDoc.value) return
  processing.value = true
  try {
    const res = await processDocument(uploadedDoc.value.id)
    processResult.value = res.data
    ElMessage.success('处理完成')
  } catch {
    // handled by interceptor
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
  return map[step] || ''
}
</script>

<style scoped>
.know-page { padding: 0 4px; }
.know-page h2 { font-size: 18px; font-weight: 600; margin-bottom: 16px; }
.know-upload { max-width: 500px; }
</style>
