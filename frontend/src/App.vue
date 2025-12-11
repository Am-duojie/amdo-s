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
import { computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import SidebarQuickActions from '@/components/SidebarQuickActions.vue'
import websocket from '@/utils/websocket'

const route = useRoute()
const hideSearch = computed(() => route.meta?.hideSearch === true)
const theme = computed(() => (route.meta?.theme === 'blue' ? 'blue' : 'yellow'))
const verifiedMode = computed(() => route.meta?.verifiedMode === true)
const isAdmin = computed(() => route.matched?.some(r => r.meta && r.meta.admin) === true)

const handleWsMessage = (data) => {
  if (data?.type === 'new_message' || data?.type === 'read_ack') {
    window.dispatchEvent(new CustomEvent('refresh-unread'))
  }
}

const connectWs = () => {
  const token = localStorage.getItem('token')
  if (token) {
    websocket.connect(token)
  }
}

let wsTimer = null

onMounted(() => {
  connectWs()
  websocket.on('message', handleWsMessage)
  websocket.on('connected', () => window.dispatchEvent(new CustomEvent('refresh-unread')))

  // 定时自检：若断开且有 token，尝试重连
  wsTimer = setInterval(() => {
    const token = localStorage.getItem('token')
    if (token && !websocket.isConnected) {
      websocket.connect(token)
    }
  }, 3000)

  window.addEventListener('focus', connectWs)
})

onBeforeUnmount(() => {
  websocket.off('message', handleWsMessage)
  if (wsTimer) clearInterval(wsTimer)
  window.removeEventListener('focus', connectWs)
})
</script>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
  width: 100%;
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
