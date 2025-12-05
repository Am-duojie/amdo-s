<template>
  <div class="admin-layout">
    <div class="admin-topbar">
      <div class="brand">易淘·管理后台</div>
      <div class="spacer"></div>
      <div class="user" v-if="admin.isAuthed">
        <span class="user-name">{{ admin.user?.username }}</span>
        <el-button size="small" @click="logout">退出</el-button>
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
  background: #f6f7f9;
}

.admin-topbar {
  height: 56px;
  background: #101820;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 16px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.admin-topbar .brand {
  font-weight: 700;
  font-size: 18px;
}

.admin-topbar .spacer {
  flex: 1;
}

.admin-topbar .user {
  display: flex;
  align-items: center;
  gap: 12px;
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
  border-right: 1px solid #eee;
  overflow-y: auto;
  padding: 16px 0;
}

.menu-section {
  margin-bottom: 24px;
}

.menu-title {
  padding: 0 16px 8px;
  font-size: 12px;
  font-weight: 600;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #606266;
  text-decoration: none;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

.nav-item.router-link-active {
  background: #ecf5ff;
  color: #409eff;
  border-left-color: #409eff;
  font-weight: 500;
}

.nav-item .el-icon {
  font-size: 16px;
}

.admin-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f6f7f9;
}
</style>
