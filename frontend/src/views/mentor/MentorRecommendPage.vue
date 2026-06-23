<template>
  <div class="mr">
    <h2>导师推荐</h2>

    <div class="mr-filters">
      <el-select v-model="collegeId" placeholder="全部学院" clearable style="width:200px" @change="search">
        <el-option v-for="c in colleges" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-input v-model="query" placeholder="搜索研究方向..." clearable style="width:240px" @keyup.enter="search">
        <template #append><el-button @click="search" :icon="Search" /></template>
      </el-input>
    </div>

    <div v-if="loading" class="mr-loading">推荐中...</div>
    <div v-else-if="mentors.length===0" class="mr-empty">
      <el-icon :size="36"><School /></el-icon>
      <p>暂无匹配导师，试试其他关键词</p>
    </div>
    <div v-else class="mr-grid">
      <el-card v-for="m in mentors" :key="m.mentor_id||m.id" shadow="hover" class="mr-card"
               @click="$router.push('/student/mentor/'+(m.mentor_id||m.id))">
        <div class="mrc-top">
          <div class="mrc-avatar">{{ (m.name||m.real_name||'?')[0] }}</div>
          <div class="mrc-info">
            <p class="mrc-name">{{ m.name||m.real_name }}</p>
            <p class="mrc-title">{{ m.title || '教师' }}</p>
            <p class="mrc-college">{{ collegeName(m.college_id) }}</p>
          </div>
        </div>
        <div class="mrc-tags">
          <el-tag v-if="m.match_reason" size="small" type="warning" effect="plain">{{ m.match_reason }}</el-tag>
          <el-tag v-if="m.research_direction" size="small" effect="plain">{{ m.research_direction }}</el-tag>
          <el-tag v-if="m.score" size="small" type="success" effect="plain">{{ (m.score*100).toFixed(0) }}% 匹配</el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, School } from '@element-plus/icons-vue'
import { listColleges, listMentors } from '@/api/mentor'
import http from '@/api/index'

const query = ref(''); const collegeId = ref(null); const loading = ref(false)
const mentors = ref([]); const colleges = ref([])

function collegeName(id) {
  const c = colleges.value.find(x=>x.id===id)
  return c ? c.name : ''
}

async function search() {
  loading.value = true
  try {
    if (query.value) {
      const r = await http.get('/mentor/recommend', { params: { query: query.value, college_id: collegeId.value||undefined } })
      mentors.value = r.data || []
    } else {
      const r = await listMentors({ college_id: collegeId.value||undefined, page_size: 50 })
      mentors.value = r.data?.items || []
    }
  } catch { mentors.value = [] }
  loading.value = false
}

onMounted(async () => {
  try { const r = await listColleges(); colleges.value = r.data || [] } catch {}
})
</script>

<style scoped>
.mr { padding: 0 4px; }
.mr h2 { font-size: 18px; font-weight: 600; margin-bottom: 16px; }
.mr-filters { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.mr-loading { text-align:center; padding:40px; color:#909399; }
.mr-empty { display:flex; flex-direction:column; align-items:center; padding:40px; color:#909399; }
.mr-empty p { margin-top:8px; font-size:13px; }
.mr-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.mr-card { cursor: pointer; }
.mrc-top { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
.mrc-avatar { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg,#409eff,#337ecc);
  color:#fff; display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:700; flex-shrink:0; }
.mrc-name { font-size: 15px; font-weight: 600; }
.mrc-title { font-size: 12px; color: #909399; }
.mrc-college { font-size: 12px; color: #409eff; }
.mrc-tags { display: flex; flex-wrap: wrap; gap: 6px; }
</style>
