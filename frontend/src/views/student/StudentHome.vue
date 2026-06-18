<template>
  <div>
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="8" v-for="card in cards" :key="card.title">
        <el-card shadow="hover" class="home-card" @click="$router.push(card.path)">
          <div class="card-inner">
            <el-icon :size="32"><component :is="card.icon" /></el-icon>
            <div>
              <p class="card-title">{{ card.title }}</p>
              <p class="card-desc">{{ card.desc }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ChatDotRound, Collection, Search, User } from '@element-plus/icons-vue'

const cards = [
  {
    title: 'AI聊天',
    desc: '与智能助手对话，解答学习生活问题',
    icon: ChatDotRound,
    path: '/student/chat',
  },
  {
    title: 'AI知识库',
    desc: '探索校园知识库，获取权威信息',
    icon: Collection,
    path: '/student/knowledge',
  },
  {
    title: '导师查询',
    desc: '查找导师信息与研究方向',
    icon: Search,
    path: '/student/tutor',
  },
  {
    title: '个人中心',
    desc: '管理个人信息与设置',
    icon: User,
    path: '/student/profile',
  },
]
</script>

<style scoped>
.home-card {
  cursor: pointer;
  margin-bottom: 16px;
  transition: border-color 0.2s;
}
.home-card:hover {
  border-color: #409eff;
}
.card-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
.card-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
