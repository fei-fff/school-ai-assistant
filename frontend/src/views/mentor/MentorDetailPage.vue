<template>
  <div class="page" v-if="m">
    <h2>{{ m.real_name }}</h2>
    <el-descriptions :column="2" border>
      <el-descriptions-item label="Title">{{ m.title || '-' }}</el-descriptions-item>
      <el-descriptions-item label="Research">{{ m.research_direction || '-' }}</el-descriptions-item>
      <el-descriptions-item label="Lab">{{ m.laboratory || '-' }}</el-descriptions-item>
      <el-descriptions-item label="Email">{{ m.email || '-' }}</el-descriptions-item>
      <el-descriptions-item label="Phone">{{ m.phone || '-' }}</el-descriptions-item>
      <el-descriptions-item label="Homepage">
        <a v-if="m.homepage" :href="m.homepage" target="_blank">{{ m.homepage }}</a>
        <span v-else>-</span>
      </el-descriptions-item>
    </el-descriptions>
    <div v-if="m.introduction" style="margin-top:16px">
      <h3>Introduction</h3>
      <p style="white-space:pre-wrap; color:#606266">{{ m.introduction }}</p>
    </div>
    <div v-if="m.student_requirement" style="margin-top:16px">
      <h3>Requirements</h3>
      <p style="white-space:pre-wrap; color:#606266">{{ m.student_requirement }}</p>
    </div>
  </div>
  <div v-else class="page">Loading...</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getMentorDetail } from '@/api/mentor'

const route = useRoute()
const m = ref(null)

onMounted(async () => {
  try { const r = await getMentorDetail(route.params.id); m.value = r.data } catch {}
})
</script>

<style scoped>
.page { padding: 0 4px; } h2 { font-size:18px; font-weight:600; margin-bottom:16px; }
h3 { font-size:14px; font-weight:600; margin-bottom:8px; }
</style>
