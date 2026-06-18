<template>
  <div class="main-layout">
    <!-- Sidebar -->
    <aside class="main-sidebar">
      <div class="sidebar-header">
        <div class="logo-sm">C</div>
        <span>校园智能助手</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :router="true"
        background-color="#1d2b3a"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        class="sidebar-menu"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <span class="sidebar-user">{{ userDisplayName }}</span>
        <el-button link type="danger" size="small" @click="handleLogout">退出</el-button>
      </div>
    </aside>

    <!-- Main content -->
    <div class="main-content-area">
      <header class="main-header">
        <h3>{{ currentTitle }}</h3>
        <el-tag size="small" :type="roleTagType">{{ roleLabel }}</el-tag>
      </header>
      <div class="main-body">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChatDotRound,
  Collection,
  Search,
  User,
  Management,
  Postcard,
  Setting,
  Grid,
  Menu,
  Upload,
  Clock,
  Document,
  School,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)
const role = computed(() => userInfo.value?.role || '')

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '')

const userDisplayName = computed(() => {
  return userInfo.value?.nickname || userInfo.value?.username || '用户'
})

const roleLabel = computed(() => {
  const map = { student: '学生', teacher: '教师', admin: '管理员' }
  return map[role.value] || ''
})

const roleTagType = computed(() => {
  const map = { student: 'success', teacher: 'warning', admin: 'danger' }
  return map[role.value] || 'info'
})

const menuItems = computed(() => {
  const menus = {
    student: [
      { path: '/student/home',         label: '首页',           icon: 'Menu' },
      { path: '/student/chat',         label: 'AI 情感陪聊',     icon: 'ChatDotRound' },
      { path: '/student/knowledge',    label: 'AI 校园知识库',   icon: 'Collection' },
      { path: '/student/tutor',        label: '导师查询',        icon: 'Search' },
      { path: '/student/chat-history', label: '聊天记录',        icon: 'Clock' },
      { path: '/student/profile',      label: '个人中心',        icon: 'User' },
    ],
    teacher: [
      { path: '/teacher/home',       label: '首页',           icon: 'Menu' },
      { path: '/teacher/knowledge',  label: '知识库管理',      icon: 'Collection' },
      { path: '/teacher/upload',     label: '上传资料',        icon: 'Upload' },
      { path: '/teacher/tutor-card', label: '我的导师名片',    icon: 'Postcard' },
      { path: '/teacher/profile',    label: '个人中心',        icon: 'User' },
    ],
    admin: [
      { path: '/admin/home',       label: '首页',         icon: 'Menu' },
      { path: '/admin/users',      label: '用户管理',      icon: 'Management' },
      { path: '/admin/colleges',   label: '学院管理',      icon: 'School' },
      { path: '/admin/teachers',   label: '导师管理',      icon: 'Postcard' },
      { path: '/admin/knowledge',  label: '知识库管理',    icon: 'Collection' },
      { path: '/admin/categories', label: '分类管理',      icon: 'Grid' },
      { path: '/admin/logs',       label: '系统日志',      icon: 'Document' },
      { path: '/admin/settings',   label: '系统设置',      icon: 'Setting' },
    ],
  }
  return menus[role.value] || []
})

function handleLogout() {
  userStore.logout()
  router.push('/')
}
</script>
