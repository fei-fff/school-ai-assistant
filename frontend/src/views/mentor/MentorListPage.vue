<template>
  <div class="page">
    <h2>Mentors</h2>
    <div v-if="loading">Loading...</div>
    <div v-else-if="mentors.length === 0" class="empty">No mentors in this college yet.</div>
    <div v-else class="grid">
      <el-card v-for="m in mentors" :key="m.id" shadow="hover" class="card"
               @click="$router.push('/student/mentor/' + m.id)">
        <p class="name">{{ m.real_name }}</p>
        <p class="title">{{ m.title || 'Teacher' }}</p>
        <p class="dir">{{ m.research_direction || '' }}</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { listMentors } from '@/api/mentor'

const route = useRoute()
const collegeId = route.params.collegeId
const mentors = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const r = await listMentors({ college_id: collegeId, page_size: 100 })
    mentors.value = r.data?.items || []
  } catch {}
  loading.value = false
})
</script>

<style scoped>
.page { padding: 0 4px; } h2 { font-size:18px; font-weight:600; margin-bottom:16px; }
.empty { color:#909399; text-align:center; padding:40px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.card { cursor: pointer; padding: 12px; }
.name { font-size:15px; font-weight:600; }
.title { font-size:13px; color:#909399; margin-top:4px; }
.dir { font-size:12px; color:#c0c4cc; margin-top:4px; }
</style>
