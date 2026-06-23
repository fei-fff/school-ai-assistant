<template>
  <div class="dash">
    <div class="dash-hero">
      <h1>校园智能助手</h1>
      <p>AI 驱动的智慧校园服务平台 — 聊天 · 知识库 · 导师推荐</p>
      <el-button type="primary" size="large" @click="$router.push(`/${role}/chat`)">开始对话</el-button>
    </div>

    <div class="dash-grid">
      <el-card shadow="hover" class="dash-card" @click="$router.push(`/${role}/chat`)">
        <el-icon :size="28"><ChatDotRound /></el-icon>
        <p class="dc-title">AI 对话</p>
        <p class="dc-desc">情绪感知 · 知识问答 · 导师咨询，一个入口搞定</p>
      </el-card>

      <el-card shadow="hover" class="dash-card" @click="$router.push(`/${role}/knowledge`)">
        <el-icon :size="28"><Collection /></el-icon>
        <p class="dc-title">知识库问答</p>
        <p class="dc-desc">基于校园文档的 RAG 智能检索，精准回答</p>
      </el-card>

      <el-card shadow="hover" class="dash-card" @click="$router.push(`/${role}/colleges`)">
        <el-icon :size="28"><School /></el-icon>
        <p class="dc-title">导师推荐</p>
        <p class="dc-desc">智能匹配研究方向，找到最适合的导师</p>
      </el-card>

      <el-card v-if="role==='teacher'" shadow="hover" class="dash-card" @click="$router.push('/teacher/card')">
        <el-icon :size="28"><Postcard /></el-icon>
        <p class="dc-title">我的名片</p>
        <p class="dc-desc">编辑导师资料，让学生更容易找到你</p>
      </el-card>

      <el-card v-if="role==='teacher'" shadow="hover" class="dash-card" @click="$router.push('/teacher/upload')">
        <el-icon :size="28"><Upload /></el-icon>
        <p class="dc-title">上传资料</p>
        <p class="dc-desc">上传知识文档，丰富校园知识库</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { ChatDotRound, Collection, School, Postcard, Upload } from '@element-plus/icons-vue'

const userStore = useUserStore()
const role = computed(() => userStore.userInfo?.role || 'student')
</script>

<style scoped>
.dash { padding: 0; }
.dash-hero { text-align: center; padding: 40px 0 32px; }
.dash-hero h1 { font-size: 26px; font-weight: 700; color: #1d2b3a; margin-bottom: 8px; }
.dash-hero p { font-size: 14px; color: #909399; margin-bottom: 20px; }
.dash-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; margin-top: 8px; }
.dash-card { cursor: pointer; text-align: center; padding: 24px 12px; transition: border-color .2s, box-shadow .2s; }
.dash-card:hover { border-color: #409eff; box-shadow: 0 2px 12px rgba(64,158,255,.15); }
.dash-card .el-icon { color: #409eff; margin-bottom: 10px; }
.dc-title { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
.dc-desc { font-size: 12px; color: #909399; line-height: 1.5; }
</style>
