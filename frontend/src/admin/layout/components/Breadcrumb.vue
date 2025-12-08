<template>
  <el-breadcrumb separator=">">
    <el-breadcrumb-item v-for="(item, index) in crumbs" :key="item.path || index">
      <span class="crumb-label" v-if="index === crumbs.length - 1">{{ item.title }}</span>
      <router-link v-else :to="item.path">{{ item.title }}</router-link>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const crumbs = computed(() =>
  route.matched
    .filter(r => r.meta && r.meta.title && !r.meta.hidden)
    .map(r => ({ title: r.meta.title, path: r.path ? `/${r.path.replace(/^\/+/, '')}` : '/' }))
)
</script>

<style scoped>
.crumb-label {
  color: #606266;
  font-weight: 500;
}
</style>

