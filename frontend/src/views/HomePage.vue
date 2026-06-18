<template>
  <div class="landing-page">
    <div class="landing-logo">
      <span class="landing-logo-text">C</span>
    </div>
    <h1 class="landing-title">校园智能助手</h1>
    <p class="landing-subtitle">基于大语言模型与RAG知识库 · 智慧校园服务</p>

    <div class="landing-avatar" @click="goLogin" title="点击进入系统">
      <el-icon class="landing-avatar-icon"><UserFilled /></el-icon>
    </div>

    <div style="margin-top: 28px; display: flex; gap: 16px">
      <el-button type="primary" size="large" @click="goLogin">登录</el-button>
      <el-button size="large" @click="goRegister">注册</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goLogin() {
  router.push('/login')
}

function goRegister() {
  router.push('/register')
}
</script>
