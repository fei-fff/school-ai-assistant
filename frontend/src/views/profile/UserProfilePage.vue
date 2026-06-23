<template>
  <div class="pp" v-if="profile">
    <h2>我的画像</h2>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header>情绪状态</template>
          <div class="pp-big">
            <span :class="'pp-emo pp-'+profile.emotion_state">{{ emotionLabel }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header>学院</template>
          <p class="pp-val">{{ profile.college || '未设置' }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" style="margin-top:16px">
      <template #header>兴趣标签</template>
      <div class="pp-tags">
        <el-tag v-for="t in interestTags" :key="t" size="default" type="success" effect="plain">{{ t }}</el-tag>
        <span v-if="interestTags.length===0" class="pp-empty">暂无记录，多聊聊感兴趣的话题吧</span>
      </div>
    </el-card>

    <el-card shadow="hover" style="margin-top:16px">
      <template #header>常聊话题</template>
      <div class="pp-list">
        <div v-for="t in topicList" :key="t" class="pp-item">{{ t }}</div>
        <span v-if="topicList.length===0" class="pp-empty">暂无记录</span>
      </div>
    </el-card>
  </div>
  <div v-else class="pp-loading">加载中...</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import http from '@/api/index'

const userStore = useUserStore()
const profile = ref(null)

const interestTags = computed(() => {
  if (!profile.value?.interests) return []
  return profile.value.interests.split(',').map(s=>s.trim()).filter(Boolean).slice(0,10)
})
const topicList = computed(() => {
  if (!profile.value?.frequent_topics) return []
  return profile.value.frequent_topics.split(',').map(s=>s.trim()).filter(Boolean).slice(0,8)
})
const emotionLabel = computed(() => {
  const m = {stress:'压力',happy:'开心',sad:'难过',neutral:'平静',negative:'负面',positive:'积极',anxiety:'焦虑'}
  return m[profile.value?.emotion_state] || profile.value?.emotion_state || '暂无'
})

onMounted(async () => {
  try {
    const uid = userStore.userInfo?.id
    if (uid) {
      const r = await http.get(`/user/profile/${uid}`)
      profile.value = r.data
    }
  } catch { profile.value = {} }
})
</script>

<style scoped>
.pp { padding: 0 4px; }
.pp h2 { font-size: 18px; font-weight: 600; margin-bottom: 16px; }
.pp-big { text-align: center; padding: 12px 0; }
.pp-emo { font-size: 28px; font-weight: 700; padding: 8px 20px; border-radius: 8px; }
.pp-stress { background: #fef0f0; color: #f56c6c; }
.pp-happy { background: #f0f9eb; color: #67c23a; }
.pp-neutral { background: #f5f7fa; color: #909399; }
.pp-negative { background: #fef0f0; color: #f56c6c; }
.pp-positive { background: #f0f9eb; color: #67c23a; }
.pp-val { font-size: 16px; font-weight: 600; }
.pp-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.pp-list { display: flex; flex-direction: column; gap: 6px; }
.pp-item { padding: 6px 12px; background: #f5f7fa; border-radius: 6px; font-size: 13px; }
.pp-empty { color: #c0c4cc; font-size: 13px; }
.pp-loading { text-align:center; padding:40px; color:#909399; }
</style>
