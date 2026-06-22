<template>
  <div class="main-layout">
    <aside class="main-sidebar">
      <div class="sidebar-header"><div class="logo-sm">C</div><span>Campus AI</span></div>
      <el-menu :default-active="activeMenu" :router="true" background-color="#1d2b3a" text-color="#bfcbd9" active-text-color="#409eff" class="sidebar-menu">
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon><span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <span class="sidebar-user">{{ userDisplayName }}</span>
        <el-button link type="danger" size="small" @click="handleLogout">Logout</el-button>
      </div>
    </aside>
    <div class="main-content-area">
      <header class="main-header"><h3>{{ currentTitle }}</h3><el-tag size="small" :type="roleTagType">{{ roleLabel }}</el-tag></header>
      <div class="main-body"><router-view /></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChatDotRound, Collection, Search, User, Management, Postcard, Setting, Grid, Menu, Upload, Clock, Document, School } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute(); const router = useRouter(); const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)
const role = computed(() => userInfo.value?.role || '')
const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '')
const userDisplayName = computed(() => userInfo.value?.nickname || userInfo.value?.username || 'User')
const roleLabel = computed(() => ({student:'Student',teacher:'Teacher',admin:'Admin'}[role.value]||''))
const roleTagType = computed(() => ({student:'success',teacher:'warning',admin:'danger'}[role.value]||'info'))

const menuItems = computed(() => ({
  student: [
    { path: '/student/home', label: 'Home', icon: 'Menu' },
    { path: '/student/chat', label: 'AI Chat', icon: 'ChatDotRound' },
    { path: '/student/knowledge', label: 'Knowledge QA', icon: 'Collection' },
    { path: '/student/colleges', label: 'Mentors', icon: 'School' },
    { path: '/student/chat-history', label: 'History', icon: 'Clock' },
    { path: '/student/profile', label: 'Profile', icon: 'User' },
  ],
  teacher: [
    { path: '/teacher/home', label: 'Home', icon: 'Menu' },
    { path: '/teacher/knowledge', label: 'Knowledge', icon: 'Collection' },
    { path: '/teacher/upload', label: 'Upload', icon: 'Upload' },
    { path: '/teacher/card', label: 'My Card', icon: 'Postcard' },
    { path: '/teacher/profile', label: 'Profile', icon: 'User' },
  ],
  admin: [
    { path: '/admin/home', label: 'Home', icon: 'Menu' },
    { path: '/admin/users', label: 'Users', icon: 'Management' },
    { path: '/admin/colleges', label: 'Colleges', icon: 'School' },
    { path: '/admin/teachers', label: 'Mentors', icon: 'Postcard' },
    { path: '/admin/knowledge', label: 'Knowledge', icon: 'Collection' },
    { path: '/admin/categories', label: 'Categories', icon: 'Grid' },
    { path: '/admin/logs', label: 'Logs', icon: 'Document' },
    { path: '/admin/settings', label: 'Settings', icon: 'Setting' },
  ],
}[role.value] || []))

function handleLogout() { userStore.logout(); router.push('/') }
</script>
