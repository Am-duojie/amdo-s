<template>
  <div class="app-wrapper">
    <PageHeader :hideSearch="hideSearch" :theme="theme" :verifiedMode="verifiedMode" />
    <SidebarQuickActions />
    <el-main class="main-content">
      <router-view />
    </el-main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import SidebarQuickActions from '@/components/SidebarQuickActions.vue'

const route = useRoute()
const hideSearch = computed(() => route.meta?.hideSearch === true)
const theme = computed(() => (route.meta?.theme === 'blue' ? 'blue' : 'yellow'))
const verifiedMode = computed(() => route.meta?.verifiedMode === true)
</script>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
}

.main-content {
  flex: 1;
  padding: 0 !important;
  margin: 0;
  background: #f5f5f5;
}

:deep(.el-main) {
  padding: 0 !important;
}
</style>
