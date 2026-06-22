<template>
  <div class="page">
    <h2>{{ isNew ? 'Create Mentor Card' : 'My Mentor Card' }}</h2>
    <el-form :model="form" label-width="120px" style="max-width:600px" ref="f" :rules="rules">
      <el-form-item label="Real Name" prop="real_name">
        <el-input v-model="form.real_name" />
      </el-form-item>
      <el-form-item label="Title">
        <el-input v-model="form.title" placeholder="e.g. Professor" />
      </el-form-item>
      <el-form-item label="College">
        <el-select v-model="form.college_id" placeholder="Select" clearable style="width:100%">
          <el-option v-for="c in colleges" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="Research">
        <el-input v-model="form.research_direction" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item label="Lab">
        <el-input v-model="form.laboratory" />
      </el-form-item>
      <el-form-item label="Email">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item label="Phone">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="Homepage">
        <el-input v-model="form.homepage" />
      </el-form-item>
      <el-form-item label="Requirements">
        <el-input v-model="form.student_requirement" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="Introduction">
        <el-input v-model="form.introduction" type="textarea" :rows="4" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="save">
          {{ isNew ? 'Create' : 'Save' }}
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getMyCard, createMyCard, updateMyCard, listColleges } from '@/api/mentor'

const f = ref(null)
const saving = ref(false)
const isNew = ref(true)
const colleges = ref([])
const form = reactive({
  real_name: '', title: '', college_id: null, research_direction: '',
  laboratory: '', email: '', phone: '', homepage: '',
  student_requirement: '', introduction: '',
})
const rules = { real_name: [{ required: true, message: 'Required' }] }

onMounted(async () => {
  try {
    const res = await getMyCard()
    if (res.data) {
      isNew.value = false
      Object.assign(form, res.data)
    }
  } catch {}
  try { const r = await listColleges(); colleges.value = r.data || [] } catch {}
})

async function save() {
  const v = await f.value.validate().catch(() => false)
  if (!v) return
  saving.value = true
  try {
    if (isNew.value) {
      await createMyCard({ ...form, college_id: form.college_id || null })
    } else {
      await updateMyCard({ ...form, college_id: form.college_id || null })
    }
    ElMessage.success('Saved')
    isNew.value = false
  } finally { saving.value = false }
}
</script>

<style scoped>.page { padding: 0 4px; } h2 { font-size:18px; font-weight:600; margin-bottom:16px; }</style>
