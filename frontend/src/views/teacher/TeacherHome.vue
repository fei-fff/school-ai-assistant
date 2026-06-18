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
import { Collection, Postcard, User } from '@element-plus/icons-vue'

const cards = [
  {
    title: 'AI知识库管理',
    desc: '管理与维护校园知识库内容',
    icon: Collection,
    path: '/teacher/knowledge',
  },
  {
    title: '我的导师名片',
    desc: '编辑个人导师信息与研究方向',
    icon: Postcard,
    path: '/teacher/tutor-card',
  },
  {
    title: '个人中心',
    desc: '管理个人信息与设置',
    icon: User,
    path: '/teacher/profile',
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
