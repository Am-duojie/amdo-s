<template>
  <div class="admin-layout">
    <div class="admin-topbar">
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
      <aside class="admin-sidebar">
        <div class="menu-section">
          <div class="menu-title">数据看板</div>
          <router-link to="/admin/dashboard" class="nav-item">
            <el-icon><Odometer /></el-icon>
            <span>总览</span>
          </router-link>
        </div>

        <div class="menu-section">
          <div class="menu-title">回收业务</div>
          <router-link to="/admin/recycle-orders" class="nav-item">
            <el-icon><Tickets /></el-icon>
            <span>回收订单管理</span>
          </router-link>
        </div>

        <div class="menu-section">
          <div class="menu-title">官方验业务</div>
          <router-link to="/admin/verified-products" class="nav-item">
            <el-icon><Goods /></el-icon>
            <span>官方验商品管理</span>
          </router-link>
          <router-link to="/admin/verified-orders" class="nav-item">
            <el-icon><ShoppingCart /></el-icon>
            <span>官方验订单管理</span>
          </router-link>
        </div>

        <div class="menu-section">
          <div class="menu-title">易淘业务</div>
          <router-link v-if="hasPerm('payment:view')" to="/admin/secondhand-orders" class="nav-item">
            <el-icon><CreditCard /></el-icon>
            <span>易淘订单管理</span>
          </router-link>
          <router-link v-if="hasPerm('product:view')" to="/admin/products" class="nav-item">
            <el-icon><Box /></el-icon>
            <span>商品管理</span>
          </router-link>
          <router-link v-if="hasPerm('shop:view')" to="/admin/shops" class="nav-item">
            <el-icon><Shop /></el-icon>
            <span>店铺管理</span>
          </router-link>
        </div>

        <div class="menu-section">
          <div class="menu-title">内容管理</div>
          <router-link to="/admin/audit-queue" class="nav-item">
            <el-icon><DocumentChecked /></el-icon>
            <span>内容审核</span>
          </router-link>
        </div>

        <div class="menu-section" v-if="isSuper">
          <div class="menu-title">系统管理</div>
          <router-link to="/admin/users" class="nav-item">
            <el-icon><User /></el-icon>
            <span>管理员</span>
          </router-link>
          <router-link to="/admin/roles" class="nav-item">
            <el-icon><UserFilled /></el-icon>
            <span>角色权限</span>
          </router-link>
          <router-link to="/admin/audit-logs" class="nav-item">
            <el-icon><Document /></el-icon>
            <span>审计日志</span>
          </router-link>
          <router-link v-if="hasPerm('category:view')" to="/admin/categories" class="nav-item">
            <el-icon><List /></el-icon>
            <span>分类管理</span>
          </router-link>
          <router-link v-if="hasPerm('user:view')" to="/admin/frontend-users" class="nav-item">
            <el-icon><Avatar /></el-icon>
            <span>前端用户</span>
          </router-link>
          <router-link v-if="hasPerm('message:view')" to="/admin/messages" class="nav-item">
            <el-icon><ChatDotSquare /></el-icon>
            <span>消息管理</span>
          </router-link>
          <router-link v-if="hasPerm('address:view')" to="/admin/addresses" class="nav-item">
            <el-icon><Location /></el-icon>
            <span>地址管理</span>
          </router-link>
        </div>
      </aside>
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAdminAuthStore } from '@/stores/adminAuth'
import {
  Odometer, Tickets, Goods, ShoppingCart, CreditCard, Box, Shop,
  DocumentChecked, User, UserFilled, Document, List, Avatar,
  ChatDotSquare, Location
} from '@element-plus/icons-vue'

const admin = useAdminAuthStore()

const isSuper = computed(() => 
  admin.hasPerm('audit_log:view') && 
  admin.hasPerm('admin_user:view') && 
  admin.hasPerm('role:view')
)

const hasPerm = (p) => admin.hasPerm(p)

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
  height: 64px;
  background: linear-gradient(90deg, #0f172a 0%, #111827 100%);
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 120;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.16);
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
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.16);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.brand-main {
  font-weight: 800;
  font-size: 18px;
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

.admin-body {
  display: flex;
  height: calc(100vh - 56px);
}

.admin-sidebar {
  width: 240px;
  background: #fff;
  border-right: 1px solid var(--admin-border, #e5e7eb);
  overflow-y: auto;
  padding: 16px 0;
  box-shadow: 6px 0 18px rgba(0, 0, 0, 0.04);
}

.menu-section {
  margin-bottom: 18px;
}

.menu-title {
  padding: 0 16px 8px;
  font-size: 12px;
  font-weight: 700;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 11px 16px;
  color: #4b5563;
  text-decoration: none;
  transition: all 0.25s;
  border-left: 3px solid transparent;
  border-radius: 0 10px 10px 0;
  margin-right: 8px;
}

.nav-item:hover {
  background: #f8fafc;
  color: var(--admin-primary, #ff6a00);
}

.nav-item.router-link-active {
  background: #fff7ed;
  color: var(--admin-primary, #ff6a00);
  border-left-color: var(--admin-primary, #ff6a00);
  font-weight: 600;
  box-shadow: inset 0 1px 0 rgba(255, 106, 0, 0.08);
}

.nav-item .el-icon {
  font-size: 16px;
}

.admin-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: var(--admin-bg, #f6f7f9);
}
</style>
