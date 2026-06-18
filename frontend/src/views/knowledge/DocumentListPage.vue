<template>
  <div class="know-page">
    <h2>知识文档</h2>

    <div v-if="loading" style="text-align: center; padding: 40px">加载中...</div>

    <el-table v-else :data="documents" stripe style="width: 100%" size="medium">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
      <el-table-column prop="file_name" label="文件名" width="160" show-overflow-tooltip />
      <el-table-column label="阶段" width="100">
        <template #default="{ row }">
          <el-tag :type="stepTag(row.current_step)" size="small">{{ stepLabel(row.current_step) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="240">
        <template #default="{ row }">
          <span class="status-dot" :class="statusClass(row.parse_status)" title="解析">P</span>
          <span class="status-dot" :class="statusClass(row.summary_status)" title="摘要">S</span>
          <span class="status-dot" :class="statusClass(row.classify_status)" title="分类">C</span>
          <span class="status-dot" :class="statusClass(row.embedding_status)" title="向量">E</span>
          <span style="font-size: 11px; color: #909399; margin-left: 6px">
            P:解析 S:摘要 C:分类 E:向量
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="refreshStatus(row)">刷新</el-button>
          <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin-top: 12px; display: flex; justify-content: center">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchList"
      />
    </div>

    <el-alert
      v-if="errorMsg"
      :title="errorMsg"
      type="error"
      show-icon
      :closable="false"
      style="margin-top: 12px"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listDocuments, getDocumentStatus, deleteDocument } from '@/api/knowledge'

const documents = ref([])
const loading = ref(true)
const errorMsg = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

onMounted(() => fetchList())

async function fetchList() {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await listDocuments({ page: page.value, page_size: pageSize.value })
    documents.value = res.data.items || []
    total.value = res.data.total || 0
  } catch {
    errorMsg.value = '加载文档列表失败'
  } finally {
    loading.value = false
  }
}

async function refreshStatus(row) {
  try {
    const res = await getDocumentStatus(row.id)
    Object.assign(row, res.data)
    ElMessage.success('状态已刷新')
  } catch {
    ElMessage.error('刷新失败')
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除「${row.title}」？`, '确认', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteDocument(row.id)
    documents.value = documents.value.filter((d) => d.id !== row.id)
    ElMessage.success('已删除')
  } catch {
    ElMessage.error('删除失败')
  }
}

function stepLabel(step) {
  const map = {
    uploaded: '已上传', parsed: '已解析', summarized: '已摘要',
    classified: '已分类', embedded: '已向量化', ready: '就绪', failed: '失败',
  }
  return map[step] || step
}

function stepTag(step) {
  const map = { ready: 'success', failed: 'danger' }
  return map[step] || 'info'
}

function statusClass(s) {
  const map = { success: 'st-ok', processing: 'st-proc', failed: 'st-fail' }
  return map[s] || 'st-wait'
}
</script>

<style scoped>
.know-page { padding: 0 4px; }
.know-page h2 { font-size: 18px; font-weight: 600; margin-bottom: 16px; }

.status-dot {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 2px;
}
.st-ok { background: #67c23a; }
.st-proc { background: #e6a23c; }
.st-fail { background: #f56c6c; }
.st-wait { background: #c0c4cc; }
</style>
