import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/views/HomePage.vue') },
  { path: '/login', name: 'Login', component: () => import('@/views/LoginPage.vue') },
  { path: '/register', name: 'Register', component: () => import('@/views/RegisterPage.vue') },

  // Student
  { path: '/student', component: () => import('@/layouts/MainLayout.vue'), meta: { requiredRole: 'student' }, children: [
    { path: 'home', name: 'StudentHome', component: () => import('@/views/HomePage.vue'), meta: { title: '首页' } },
    { path: 'chat', name: 'StudentChat', component: () => import('@/views/chat/UnifiedChatPage.vue'), meta: { title: 'AI 聊天' } },
    { path: 'knowledge', name: 'StudentKnowledge', component: () => import('@/views/knowledge/QAQueryPage.vue'), meta: { title: '知识库问答' } },
    { path: 'colleges', name: 'StudentColleges', component: () => import('@/views/mentor/MentorRecommendPage.vue'), meta: { title: '导师推荐' } },
    { path: 'mentors/:collegeId', name: 'StudentMentors', component: () => import('@/views/mentor/MentorListPage.vue') },
    { path: 'mentor/:id', name: 'StudentMentorDetail', component: () => import('@/views/mentor/MentorDetailPage.vue'), meta: { title: '导师详情' } },
    { path: 'profile', name: 'StudentProfile', component: () => import('@/views/profile/UserProfilePage.vue'), meta: { title: '我的画像' } },
  ]},

  // Teacher
  { path: '/teacher', component: () => import('@/layouts/MainLayout.vue'), meta: { requiredRole: 'teacher' }, children: [
    { path: 'home', name: 'TeacherHome', component: () => import('@/views/HomePage.vue'), meta: { title: '首页' } },
    { path: 'chat', name: 'TeacherChat', component: () => import('@/views/chat/UnifiedChatPage.vue'), meta: { title: 'AI 聊天' } },
    { path: 'card', name: 'TeacherCard', component: () => import('@/views/mentor/TeacherCardPage.vue'), meta: { title: '我的名片' } },
    { path: 'knowledge', name: 'TeacherKnowledge', component: () => import('@/views/knowledge/DocumentListPage.vue'), meta: { title: '知识库管理' } },
    { path: 'upload', name: 'TeacherUpload', component: () => import('@/views/knowledge/DocumentUploadPage.vue'), meta: { title: '上传资料' } },
    { path: 'profile', name: 'TeacherProfile', component: () => import('@/views/profile/UserProfilePage.vue'), meta: { title: '我的画像' } },
  ]},

  // Admin
  { path: '/admin', component: () => import('@/layouts/MainLayout.vue'), meta: { requiredRole: 'admin' }, children: [
    { path: 'home', name: 'AdminHome', component: () => import('@/views/HomePage.vue'), meta: { title: '首页' } },
    { path: 'users', name: 'AdminUsers', component: () => import('@/views/PlaceholderPage.vue') },
    { path: 'colleges', name: 'AdminColleges', component: () => import('@/views/PlaceholderPage.vue') },
    { path: 'teachers', name: 'AdminTeachers', component: () => import('@/views/PlaceholderPage.vue') },
    { path: 'knowledge', name: 'AdminKnowledge', component: () => import('@/views/knowledge/DocumentListPage.vue') },
    { path: 'categories', name: 'AdminCategories', component: () => import('@/views/PlaceholderPage.vue') },
    { path: 'settings', name: 'AdminSettings', component: () => import('@/views/PlaceholderPage.vue') },
  ]},
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const t = localStorage.getItem('access_token')
  const u = JSON.parse(localStorage.getItem('user_info') || 'null')
  if (to.meta.requiredRole) {
    if (!t || !u) return next('/login')
    if (u.role !== to.meta.requiredRole) return next(`/${u.role}/home`)
  }
  if (to.name === 'Login' && t && u) return next(`/${u.role}/home`)
  next()
})

export default router
