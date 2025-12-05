<template>
  <div class="app-wrapper">
    <PageHeader v-if="!isAdmin" :hideSearch="hideSearch" :theme="theme" :verifiedMode="verifiedMode" />
    <SidebarQuickActions v-if="!isAdmin" />
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
const isAdmin = computed(() => route.matched?.some(r => r.meta && r.meta.admin) === true)
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
