import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue'),
    meta: { title: '校园智能助手' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginPage.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterPage.vue'),
    meta: { title: '注册' },
  },
  // ============== Student routes ==============
  {
    path: '/student',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiredRole: 'student' },
    children: [
      {
        path: 'home',
        name: 'StudentHome',
        component: () => import('@/views/student/StudentHome.vue'),
        meta: { title: '学生首页' },
      },
      {
        path: 'chat',
        name: 'StudentChat',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: 'AI 情感陪聊' },
      },
      {
        path: 'knowledge',
        name: 'StudentKnowledge',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: 'AI 校园知识库' },
      },
      {
        path: 'tutor',
        name: 'StudentTutor',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '导师查询' },
      },
      {
        path: 'chat-history',
        name: 'StudentChatHistory',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '聊天记录' },
      },
      {
        path: 'profile',
        name: 'StudentProfile',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '个人中心' },
      },
    ],
  },
  // ============== Teacher routes ==============
  {
    path: '/teacher',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiredRole: 'teacher' },
    children: [
      {
        path: 'home',
        name: 'TeacherHome',
        component: () => import('@/views/teacher/TeacherHome.vue'),
        meta: { title: '教师首页' },
      },
      {
        path: 'knowledge',
        name: 'TeacherKnowledge',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '知识库管理' },
      },
      {
        path: 'upload',
        name: 'TeacherUpload',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '上传资料' },
      },
      {
        path: 'tutor-card',
        name: 'TeacherTutorCard',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '我的导师名片' },
      },
      {
        path: 'profile',
        name: 'TeacherProfile',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '个人中心' },
      },
    ],
  },
  // ============== Admin routes ==============
  {
    path: '/admin',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiredRole: 'admin' },
    children: [
      {
        path: 'home',
        name: 'AdminHome',
        component: () => import('@/views/admin/AdminHome.vue'),
        meta: { title: '管理员首页' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'colleges',
        name: 'AdminColleges',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '学院管理' },
      },
      {
        path: 'teachers',
        name: 'AdminTeachers',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '导师管理' },
      },
      {
        path: 'knowledge',
        name: 'AdminKnowledge',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '知识库管理' },
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '分类管理' },
      },
      {
        path: 'logs',
        name: 'AdminLogs',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '系统日志' },
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/PlaceholderPage.vue'),
        meta: { title: '系统设置' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard — check auth and role
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const userInfo = JSON.parse(localStorage.getItem('user_info') || 'null')

  if (to.meta.requiredRole) {
    if (!token || !userInfo) {
      return next('/login')
    }
    if (userInfo.role !== to.meta.requiredRole) {
      // Redirect to own home
      const roleHome = `/${userInfo.role}/home`
      return next(roleHome)
    }
  }

  // If logged in, redirect login page to role home
  if (to.name === 'Login' && token && userInfo) {
    const roleHome = `/${userInfo.role}/home`
    return next(roleHome)
  }

  next()
})

export default router
