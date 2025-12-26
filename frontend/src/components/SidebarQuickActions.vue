<template>
  <div class="quick-sidebar" :class="{ collapsed: isCollapsed }">
    <button class="qs-toggle" @click="toggleCollapse">
      <span v-if="isCollapsed">▶</span>
      <span v-else>◀</span>
    </button>
    <div class="qs-items" v-show="!isCollapsed">
      <button class="qs-item" @click="$router.push('/publish')">➕<span>发闲置</span></button>
      <button class="qs-item" @click="$router.push('/messages')">
        💬
        <span>消息</span>
        <sup v-if="unreadCount > 0" class="qs-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</sup>
      </button>
      <button class="qs-item" @click="openService">👤<span>客服</span></button>
      <div class="qs-divider"></div>
      <button class="qs-item back-top" @click="backToTop">⬆️<span>回到顶部</span></button>
    </div>
    <div class="qs-items-collapsed" v-show="isCollapsed">
      <button class="qs-item-icon" @click="$router.push('/publish')" title="发闲置">➕</button>
      <button class="qs-item-icon" @click="$router.push('/messages')" title="消息">
        💬
        <sup v-if="unreadCount > 0" class="qs-badge-small">{{ unreadCount > 99 ? '99+' : unreadCount }}</sup>
      </button>
      <button class="qs-item-icon" @click="openService" title="客服">👤</button>
      <div class="qs-divider-small"></div>
      <button class="qs-item-icon back-top" @click="backToTop" title="回到顶部">⬆️</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import websocket from '@/utils/websocket'

const unreadCount = ref(0)
const isCollapsed = ref(false)
const router = useRouter()
const authStore = useAuthStore()

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const getSupportUserId = async () => {
  const raw = localStorage.getItem('SUPPORT_USER_ID') || import.meta.env.VITE_SUPPORT_USER_ID
  const parsed = raw ? parseInt(raw, 10) : null
  if (Number.isFinite(parsed)) return parsed
  try {
    const res = await api.get('/support/service-user/')
    const id = res.data?.id
    if (id) {
      localStorage.setItem('SUPPORT_USER_ID', String(id))
      return id
    }
  } catch {
    // ignore
  }
  return null
}

const openService = async () => {
  if (!authStore.user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  const supportUserId = await getSupportUserId()
  if (!supportUserId) {
    ElMessage.warning('平台客服未配置')
    return
  }
  router.push(`/messages?user_id=${supportUserId}`)
}
const backToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

let lastRefresh = 0
const refreshGap = 1000 // 节流 1s

const loadUnread = async () => {
  const now = Date.now()
  if (now - lastRefresh < refreshGap) return
  const token = localStorage.getItem('token')
  if (!token) return
  lastRefresh = now
  try {
    const res = await api.get('/messages/conversations/')
    const list = Array.isArray(res.data) ? res.data : []
    unreadCount.value = list.reduce((sum, item) => sum + (item.unread_count || 0), 0)
  } catch (error) {
    // 静默失败
  }
}

const refreshUnreadHandler = () => loadUnread()

onMounted(() => {
  // 初始化拉一次（单次，不循环）
  loadUnread()
  window.addEventListener('refresh-unread', refreshUnreadHandler)
})

onBeforeUnmount(() => {
  window.removeEventListener('refresh-unread', refreshUnreadHandler)
})
</script>

<style scoped>
.quick-sidebar {
  position: fixed;
  right: 16px;
  top: 30%;
  z-index: 999;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 10px 8px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  border: 1px solid #eee;
  transition: all 0.3s ease;
}

.quick-sidebar.collapsed {
  padding: 10px 6px;
}

.qs-toggle {
  width: 100%;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 12px;
  cursor: pointer;
  font-size: 12px;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.qs-toggle:hover {
  background: #e8e8e8;
  color: #333;
}

.qs-items, .qs-items-collapsed {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.qs-item {
  width: 64px;
  height: 50px;
  border: none;
  background: #fff;
  border-radius: 12px;
  position: relative;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.qs-item-icon {
  width: 36px;
  height: 36px;
  border: none;
  background: #fff;
  border-radius: 10px;
  position: relative;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.qs-item:hover, .qs-item-icon:hover {
  background: #f7f7f7;
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}

.qs-badge {
  background: #ff4d4f;
  color: #fff;
  border-radius: 10px;
  padding: 0 5px;
  font-size: 9px;
  line-height: 14px;
  min-width: 16px;
  text-align: center;
  position: absolute;
  top: 2px;
  right: 4px;
}

.qs-badge-small {
  background: #ff4d4f;
  color: #fff;
  border-radius: 8px;
  padding: 0 4px;
  font-size: 8px;
  line-height: 12px;
  min-width: 14px;
  text-align: center;
  position: absolute;
  top: -2px;
  right: -2px;
}

.qs-item span {
  font-size: 11px;
  color: #333;
}

.qs-divider {
  width: 80%;
  height: 1px;
  background: #eee;
  margin: 2px 0;
}

.qs-divider-small {
  width: 60%;
  height: 1px;
  background: #eee;
  margin: 2px 0;
}

.back-top {
  background: #ffe400;
}

.back-top:hover {
  background: #ffd600;
}
</style>
