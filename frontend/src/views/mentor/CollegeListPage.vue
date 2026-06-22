<template>
  <div class="page">
    <h2>Colleges</h2>
    <div v-if="loading">Loading...</div>
    <div v-else class="grid">
      <el-card v-for="c in colleges" :key="c.id" shadow="hover" class="card"
               @click="$router.push('/student/mentors/' + c.id)">
        <el-icon :size="28"><School /></el-icon>
        <p class="name">{{ c.name }}</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { School } from '@element-plus/icons-vue'
import { listColleges } from '@/api/mentor'

const colleges = ref([])
const loading = ref(true)

onMounted(async () => {
  try { const r = await listColleges(); colleges.value = r.data || [] } catch {}
  loading.value = false
})
</script>

<style scoped>
.page { padding: 0 4px; } h2 { font-size:18px; font-weight:600; margin-bottom:16px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
.card { cursor: pointer; text-align: center; padding: 16px 8px; }
.name { font-size:14px; font-weight:600; margin-top:8px; }
</style>
