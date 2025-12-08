<template>
  <div class="admin-layout">
    <div class="admin-topbar">
      <el-button class="fold-btn" text circle @click="isCollapse = !isCollapse">
        <el-icon><component :is="isCollapse ? Expand : Fold" /></el-icon>
      </el-button>
      <div class="brand">
        <div class="brand-line">
          <span class="brand-badge">ADMIN</span>
          <span class="brand-main">易淘·管理后台</span>
        </div>
      </div>
      <div class="spacer"></div>
      <div class="user" v-if="admin.isAuthed">
        <div class="user-chip">
          <el-avatar size="small">{{ (admin.user?.username || 'U')[0].toUpperCase() }}</el-avatar>
          <span class="user-name">{{ admin.user?.username }}</span>
        </div>
        <el-button size="small" type="primary" plain @click="logout">退出</el-button>
      </div>
    </div>
    <div class="admin-body">
      <aside class="admin-sidebar" :style="{ width: isCollapse ? '64px' : '210px' }">
        <Sidebar :collapse="isCollapse" />
      </aside>
      <main class="admin-content">
        <div class="admin-nav">
          <Breadcrumb />
          <TagsView />
        </div>
        <AppMain />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminAuthStore } from '@/stores/adminAuth'
import Sidebar from './components/Sidebar.vue'
import Breadcrumb from './components/Breadcrumb.vue'
import TagsView from './components/TagsView.vue'
import AppMain from './components/AppMain.vue'
import { Fold, Expand } from '@element-plus/icons-vue'

const admin = useAdminAuthStore()
const isCollapse = ref(false)

const logout = async () => {
  await admin.logout()
  location.href = '/admin/login'
}

// 如果已登录但用户信息未加载，则加载用户信息
onMounted(() => {
  if (admin.isAuthed && !admin.user) {
    admin.loadUser()
  }
})
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: var(--admin-bg, #f6f7f9);
}

.admin-topbar {
  height: 50px;
  background: #304156;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 16px;
  position: sticky;
  top: 0;
  z-index: 120;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.admin-topbar .brand {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.brand-line {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 8px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.brand-main {
  font-weight: 800;
  font-size: 17px;
  letter-spacing: 0.2px;
}

.admin-topbar .spacer {
  flex: 1;
}

.admin-topbar .user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.admin-topbar .user-name {
  color: #fff;
}

.fold-btn {
  color: #fff;
  margin-right: 10px;
}

.admin-body {
  display: flex;
  height: calc(100vh - 50px);
}

.admin-sidebar {
  width: 210px;
  background: #001529;
  border-right: none;
  overflow-y: auto;
  padding: 12px 0;
  box-shadow: none;
}

.admin-content {
  flex: 1;
  padding: 14px 16px;
  overflow-y: auto;
  background: #f0f2f5;
}

.admin-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
  padding: 4px 0;
}
</style>
