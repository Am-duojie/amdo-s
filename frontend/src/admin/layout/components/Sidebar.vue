<template>
  <div class="sidebar" :class="{ collapsed: collapse }">
    <div
      v-for="groupKey in displayGroups"
      :key="groupKey"
      class="menu-section"
    >
      <div class="menu-title">{{ groupTitles[groupKey] }}</div>
      <router-link
        v-for="item in groupedRoutes[groupKey]"
        :key="item.path"
        :to="`/admin/${item.path}`"
        class="nav-item"
        :class="{ active: isActive(item) }"
      >
        <el-icon v-if="item.meta?.icon && iconComponents[item.meta.icon]" class="nav-icon">
          <component :is="iconComponents[item.meta.icon]" />
        </el-icon>
        <span>{{ item.meta?.title || item.name }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAdminAuthStore } from '@/stores/adminAuth'
import {
  Odometer,
  TrendCharts,
  MagicStick,
  Tickets,
  Goods,
  ShoppingCart,
  CreditCard,
  Box,
  Shop,
  DocumentChecked,
  User,
  UserFilled,
  Document,
  List,
  Avatar,
  ChatDotSquare,
  Location,
  Money
} from '@element-plus/icons-vue'

const props = defineProps({
  collapse: {
    type: Boolean,
    default: false
  }
})

const iconComponents = {
  Odometer,
  TrendCharts,
  MagicStick,
  Tickets,
  Goods,
  ShoppingCart,
  CreditCard,
  Box,
  Shop,
  DocumentChecked,
  User,
  UserFilled,
  Document,
  List,
  Avatar,
  ChatDotSquare,
  Location,
  Money
}

const groupTitles = {
  dashboard: '数据看板',
  recycle: '回收业务',
  verified: '官方验业务',
  secondhand: '易淘业务',
  content: '内容管理',
  system: '系统管理',
  legacy: '历史'
}

const groupOrder = ['dashboard', 'recycle', 'verified', 'secondhand', 'content', 'system', 'legacy']

const route = useRoute()
const router = useRouter()
const admin = useAdminAuthStore()

const adminChildren = computed(() => {
  const adminRoute = router.options.routes.find(r => r.path === '/admin')
  if (!adminRoute || !adminRoute.children) return []
  return adminRoute.children.filter(r => !r.meta?.hidden)
})

const hasPerm = (perm) => {
  if (!perm) return true
  return admin.hasPerm(perm)
}

const groupedRoutes = computed(() => {
  const groups = {}
  for (const r of adminChildren.value) {
    if (!hasPerm(r.meta?.perm)) continue
    const g = r.meta?.group && groupTitles[r.meta.group] ? r.meta.group : 'system'
    if (!groups[g]) groups[g] = []
    groups[g].push(r)
  }
  return groups
})

const displayGroups = computed(() => {
  const ordered = groupOrder.filter(g => groupedRoutes.value[g]?.length > 0 && g !== 'legacy')
  const legacy = groupedRoutes.value.legacy?.length ? ['legacy'] : []
  return [...ordered, ...legacy]
})

const isActive = (item) => {
  return route.path.startsWith(`/admin/${item.path}`)
}
</script>

<style scoped>
.sidebar {
  height: 100%;
}

.menu-section {
  margin-bottom: 12px;
}

.menu-title {
  padding: 6px 20px;
  font-size: 12px;
  font-weight: 700;
  color: #8c99ae;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  color: #bfcbd9;
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: #263445;
  color: #fff;
}

.nav-item.active {
  background: #1f2d3d;
  color: #fff;
  border-left-color: #409eff;
  font-weight: 600;
}

.nav-icon {
  font-size: 16px;
}

.sidebar.collapsed .menu-title {
  display: none;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 10px 12px;
}

.sidebar.collapsed .nav-item span {
  display: none;
}
</style>
