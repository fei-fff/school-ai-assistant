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
import { Management, Collection, Grid, Setting } from '@element-plus/icons-vue'

const cards = [
  {
    title: '用户管理',
    desc: '管理所有注册用户信息与权限',
    icon: Management,
    path: '/admin/users',
  },
  {
    title: '知识库管理',
    desc: '审核与维护知识库文章内容',
    icon: Collection,
    path: '/admin/knowledge',
  },
  {
    title: '分类管理',
    desc: '管理知识库分类与标签体系',
    icon: Grid,
    path: '/admin/categories',
  },
  {
    title: '系统设置',
    desc: '配置系统参数与运行状态',
    icon: Setting,
    path: '/admin/settings',
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
