<template>
  <div class="placeholder-page">
    <el-icon class="icon"><Clock /></el-icon>
    <p>{{ message }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const message = computed(() => `「${route.meta.title}」功能开发中，敬请期待`)
</script>
