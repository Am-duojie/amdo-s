<template>
  <header class="header-sticky" :class="{ 'blue-theme': props.theme === 'blue' }">
    <div class="header-content">
      <!-- Logo -->
      <div class="brand-logo" @click="goHome">
        <span class="logo-text">{{ brandText }}</span>
      </div>

      

      <!-- 搜索区 -->
      <SearchBox v-if="!hideSearch"
        v-model="searchKeyword"
        :placeholder="searchPlaceholder"
        @search="handleSearch"
      />

      <!-- 右侧用户区 -->
      <div class="user-section">
        <template v-if="authStore.user">
          <!-- 订单入口 -->
          <div class="order-link" @click="goToOrders">
            <el-icon class="order-icon"><Tickets /></el-icon>
            <span class="order-text">订单</span>
          </div>
          
          <!-- 悬停展开菜单 -->
          <div class="user-dropdown">
            <div
              class="user-info"
              role="button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <div class="user-avatar-block">
                <img
                  v-if="authStore.user.avatar"
                  :src="authStore.user.avatar"
                  class="user-avatar"
                  alt="用户头像"
                />
                <div v-else class="user-avatar-default">{{ userInitial }}</div>
              </div>
              <div class="user-meta">
                <span class="user-meta-name">{{ userDisplayName }}</span>
              </div>
            </div>
            
            <!-- 自定义下拉菜单 -->
            <div class="custom-dropdown">
              <!-- 用户信息卡片 -->
              <div class="user-profile-card">
                <div class="profile-header">
                  <img v-if="authStore.user.avatar" :src="authStore.user.avatar" class="profile-avatar" />
                  <div v-else class="profile-avatar-default">{{ userInitial }}</div>
                  <div class="profile-info">
                    <div class="profile-name">{{ authStore.user.username }}</div>
                    <div class="profile-stats">
                      <span class="stat-item">0 粉丝</span>
                      <span class="stat-divider">|</span>
                      <span class="stat-item">0 关注</span>
                    </div>
                  </div>
                </div>
                
                <!-- 功能选项 -->
                <div class="profile-menu">
                  <div class="profile-menu-item" @click="handleUserMenuCommand('trade')">
                    <span class="menu-text">我的交易</span>
                    <span class="menu-count">0</span>
                    <span class="menu-arrow">›</span>
                  </div>
                  <div class="profile-menu-item" @click="handleUserMenuCommand('favorites')">
                    <span class="menu-text">我的收藏</span>
                    <span class="menu-count">0</span>
                    <span class="menu-arrow">›</span>
                  </div>
                  <div class="profile-menu-item" @click="handleUserMenuCommand('settings')">
                    <span class="menu-text">账户设置</span>
                    <span class="menu-count">0</span>
                    <span class="menu-arrow">›</span>
                  </div>
                  <div class="profile-menu-item" @click="switchZone">
                    <span class="menu-text">{{ props.verifiedMode ? '切换到易淘' : '进入官方验' }}</span>
                    <span class="menu-count"></span>
                    <span class="menu-arrow">&gt;</span>
                  </div>
                </div>
                
                <!-- 退出登录 -->
                <div class="logout-item" @click="handleUserMenuCommand('logout')">
                  <span class="logout-text">退出登录</span>
                </div>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="login-btn" @click="goToLogin">登录/注册</div>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Tickets } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import SearchBox from '@/components/SearchBox.vue'

// Props
const props = defineProps({
  hideSearch: {
    type: Boolean,
    default: false
  },
  theme: {
    type: String,
    default: 'yellow', // 'yellow' 或 'blue'
    validator: (value) => ['yellow', 'blue'].includes(value)
  },
  verifiedMode: {
    type: Boolean,
    default: false  // 是否为官方验货模式
  }
})

const router = useRouter()
const authStore = useAuthStore()

const brandText = computed(() => (props.verifiedMode ? '官方验' : '易淘'))
const userDisplayName = computed(() => authStore.user?.nickname || authStore.user?.username || '易淘用户')
const userInitial = computed(() => authStore.user?.username?.charAt(0)?.toUpperCase() || 'U')

// 搜索相关
const searchKeyword = ref('')
const hotWords = ref([])

// 动态搜索提示
const searchPlaceholder = computed(() => {
  if (hotWords.value.length >= 3) {
    const samples = hotWords.value.slice(0, 3)
    return `搜索好物，例如 ${samples.join(' / ')}`
  }
  return props.verifiedMode ? '搜索官方验好物' : '搜索二手好物'
})

// 加载热词 - 优化：使用防抖和缓存
const loadHotWords = async () => {
  try {
    const endpoint = props.verifiedMode ? '/verified-products/' : '/products/'
    const res = await api.get(endpoint, { params: { status: 'active', page_size: 10 } })
    const productList = res.data.results || res.data
    
    if (!productList || productList.length === 0) return
    
    // 从商品标题中提取关键词 - 优化：使用Set避免重复检查
    const wordsSet = new Set()
    productList.forEach(product => {
      if (product.title) {
        const title = product.title.trim()
        if (title.length >= 2) {
          const keyword = title.length > 12 ? title.substring(0, 8) : title
          wordsSet.add(keyword)
        }
      }
    })
    
    hotWords.value = Array.from(wordsSet).slice(0, 8) // 减少热词数量
  } catch (err) {
    console.error('加载热词失败:', err)
    hotWords.value = [] // 确保hotWords始终是数组
  }
}

// 搜索处理
const handleSearch = () => {
  const kw = searchKeyword.value.trim()
  if (props.verifiedMode) {
    router.push({ path: '/verified-products', query: kw ? { search: kw } : {} })
  } else {
    router.push({ path: '/products', query: kw ? { search: kw } : {} })
  }
}

// 用户菜单处理
const handleUserMenuCommand = async (command) => {
  switch (command) {
    case 'trade':
      // 如果是官方验货模式，跳转到官方验货订单页面
      if (props.verifiedMode) {
        router.push('/profile?zone=verified&tab=verified-orders')
      } else {
        router.push('/profile?tab=bought')  // 跳转到我的交易（默认显示我买到的）
      }
      break
    case 'favorites':
      // 如果是官方验货模式，跳转到官方验货收藏页面
      if (props.verifiedMode) {
        router.push('/profile?zone=verified&tab=verified-favorites')
      } else {
        router.push('/profile?tab=favorites')  // 跳转到我的收藏
      }
      break
    case 'settings':
      router.push('/profile?tab=address')  // 账户设置为账号共享
      break
    case 'products':
      // 如果是官方验货模式，跳转到官方验货个人中心
      if (props.verifiedMode) {
        router.push('/profile?zone=verified&tab=verified-orders')
      } else {
        router.push('/profile')
      }
      break
    case 'orders':
      // 如果是官方验货模式，跳转到官方验货订单页面
      if (props.verifiedMode) {
        router.push('/profile?zone=verified&tab=verified-orders')
      } else {
        router.push('/profile?tab=bought')
      }
      break
    case 'messages':
      router.push('/messages')
      break
    case 'profile':
      // 如果是官方验货模式，跳转到官方验货个人中心
      if (props.verifiedMode) {
        router.push('/profile?zone=verified&tab=verified-orders')
      } else {
        router.push('/profile')
      }
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        authStore.logout()
        ElMessage.success('已退出登录')
        router.push('/')
      } catch {
        // 取消退出
      }
      break
  }
}

const goToLogin = () => router.push('/login')
const goToRecycle = () => router.push('/recycle')

const goHome = () => {
  router.push(props.verifiedMode ? '/verified-products' : '/')
}

const switchZone = () => {
  if (props.verifiedMode) {
    router.push('/')
    return
  }
  const newTab = window.open('/verified-products', '_blank', 'noopener,noreferrer')
  if (newTab) newTab.opener = null
}

const goToOrders = () => {
  // 如果是官方验货模式，跳转到官方验货订单页面
  if (props.verifiedMode) {
    router.push('/profile?zone=verified&tab=verified-orders')
  } else {
    router.push('/profile?tab=bought')
  }
}

onMounted(() => {
  loadHotWords()
})
</script>

<style scoped>
/* ==================== 顶部导航 ==================== */
.header-sticky {
  background: #ffe400;
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 16px 0;
  margin: 0;
  box-shadow: 0 4px 24px rgba(0,0,0,0.1);
  border-bottom: 2px solid rgba(255,255,255,0.3);
  transition: background 0.3s;
  width: 100%;
  left: 0;
  right: 0;
}

/* 蓝色主题 */
.header-sticky.blue-theme {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  border-bottom: 2px solid #1890ff;
  box-shadow: 0 4px 24px rgba(24, 144, 255, 0.15);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 20px;
  width: 100%;
}

/* Logo */
  .brand-logo { 
    cursor: pointer; 
    flex-shrink: 0;
    display: flex;
    align-items: center;
    padding: 8px 12px;
    border-radius: 8px;
    transition: opacity 0.2s ease;
  }
  .brand-logo:hover { 
    opacity: 0.9;
  }
  .logo-text { 
    font-size: 28px; 
    font-weight: 800; 
    color: #2b2b2b;
    line-height: 1;
    letter-spacing: 0.5px;
  }

/* 官方质检回收入口 */
/* 头部不再显示回收入口 */

/* 蓝色主题下的回收入口 */
.blue-theme .recycle-entry {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.blue-theme .recycle-entry:hover {
  background: linear-gradient(135deg, #40a9ff, #1890ff);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.4);
}

/* 蓝色主题下的搜索框 */
.blue-theme .search-box {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(24, 144, 255, 0.3);
}

.blue-theme .search-box:focus-within {
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

.blue-theme .search-btn {
  background: linear-gradient(135deg, #1890ff, #096dd9);
}

.blue-theme .search-btn:hover {
  background: linear-gradient(135deg, #40a9ff, #1890ff);
}

/* 蓝色主题下的订单入口 */
.blue-theme .order-link {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(24, 144, 255, 0.2);
}

.blue-theme .order-link:hover {
  background: #fff;
  border-color: #1890ff;
  color: #1890ff;
}

/* 蓝色主题下的登录按钮 */
.blue-theme .login-btn {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  border-color: #1890ff;
}

.blue-theme .login-btn:hover {
  background: linear-gradient(135deg, #40a9ff, #1890ff);
}
.recycle-entry:active {
  transform: translateY(0);
}
.recycle-icon {
  font-size: 20px;
  line-height: 1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}
.recycle-text {
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

/* 搜索区域 */
.search-section { 
  flex: 1;
  max-width: 580px;
}

.search-box {
  display: flex;
  height: 46px;
  background: rgba(255,255,255,0.9);
  border-radius: 23px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  border: 2px solid rgba(255,255,255,0.5);
  transition: all 0.2s ease;
}
.search-box:focus-within {
  box-shadow: 0 6px 24px rgba(255,102,0,0.15);
  border-color: rgba(255,102,0,0.3);
  transform: translateY(-1px);
}

.search-box .search-input {
  flex: 1;
  border: none;
  padding: 0 20px;
  font-size: 14px;
  outline: none;
  background: transparent;
  color: #222;
}
.search-box .search-input::placeholder { 
  color: #999;
  font-weight: 400;
}

.search-box .search-btn {
  padding: 0 26px;
  background: linear-gradient(135deg, #ff6600, #ff8833);
  border: none;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: -2px 0 8px rgba(0,0,0,0.05);
}
.search-box .search-btn:hover { 
  background: linear-gradient(135deg, #ff7722, #ff9944);
  box-shadow: -2px 0 12px rgba(0,0,0,0.1);
}
.search-box .search-btn .search-icon { 
    font-size: 14px;
  }

/* 用户区域 */
.user-section {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
  margin-left: auto;
  justify-content: flex-end;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.dropdown-arrow { display: none; }

.user-avatar-block {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  position: relative;
}

.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.user-meta-name {
  font-size: 14px;
  color: #333;
  font-weight: 600;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-meta-desc { display: none; }

/* 自定义下拉菜单 */
.user-dropdown {
  position: relative;
  display: inline-block;
}

.custom-dropdown {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 4px;
  min-width: 280px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.8);
  background: #fff;
  overflow: hidden;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transform: translateY(6px);
  transition: opacity 0.08s cubic-bezier(0.4, 0, 0.2, 1), transform 0.08s cubic-bezier(0.4, 0, 0.2, 1), visibility 0.08s linear;
}

.user-dropdown:hover .custom-dropdown {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

/* 用户资料卡片 */
.user-profile-card {
  width: 100%;
}

.profile-header {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.profile-avatar, .profile-avatar-default {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 12px;
}

.profile-avatar {
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.profile-avatar-default {
  background: linear-gradient(135deg, #ff6600, #ff8833);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.profile-stats {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
}

.stat-item {
  margin-right: 4px;
}

.stat-divider {
  margin: 0 6px;
  color: #e0e0e0;
}

/* 功能菜单 */
.profile-menu {
  padding: 8px 0;
}

.profile-menu-item {
  height: auto;
  padding: 12px 16px;
  margin: 0;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.profile-menu-item:hover {
  background: #fafafa;
}

.menu-text {
  flex: 1;
}

.menu-count {
  font-size: 12px;
  color: #666;
  margin-right: 8px;
}

.menu-arrow {
  font-size: 16px;
  color: #ccc;
}

/* 退出登录项 */
.logout-item {
  height: auto;
  padding: 12px 16px;
  margin: 0;
  transition: all 0.2s ease;
  cursor: pointer;
  font-size: 14px;
  color: #ff4444;
  text-align: center;
  border-top: 1px solid #f0f0f0;
}

.logout-item:hover {
  background: #fff2f2;
}

/* 移除Element Plus默认样式 */
:deep(.el-dropdown-menu__item) {
  padding: 0;
  margin: 0;
  height: auto;
  line-height: normal;
}

:deep(.el-dropdown-menu__item:hover) {
  background: transparent;
}

:deep(.el-dropdown-menu__item--divided::before) {
  display: none;
}

.user-avatar, .user-avatar-default {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  flex-shrink: 0;
  border: none;
  box-shadow: none;
}
.user-avatar { object-fit: cover; }
.user-avatar-default { background: #ddd; color: #666; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; }
.user-name {
  font-size: 14px;
  color: #222;
  font-weight: 500;
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-dropdown:hover .user-name {
  color: #ff6600;
}

.order-link {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.2s;
}

.order-link:hover {
  background: #fff;
  border-color: rgba(0, 0, 0, 0.14);
}
.order-link .order-icon { display: inline-flex; font-size: 16px; }

.login-btn {
  font-size: 14px;
  color: #fff;
  cursor: pointer;
  padding: 10px 20px;
  background: linear-gradient(135deg, #ff6600, #ff8833);
  border-radius: 12px;
  font-weight: 500;
  border: 1px solid rgba(255,102,0,0.3);
  transition: all 0.25s ease;
}
.login-btn:hover { 
  background: linear-gradient(135deg, #ff7722, #ff9944);
  border-color: rgba(255,102,0,0.5);
  transform: translateY(-1px);
}

/* 响应式 */
@media (max-width: 768px) {
  .header-content { 
    gap: 12px; 
    padding: 0 12px;
  }
  .brand-logo {
    padding: 6px 12px;
    gap: 6px;
  }
  .logo-icon { font-size: 24px; }
  .logo-text { font-size: 28px; }
  .search-section { display: none; }
  .recycle-entry {
    padding: 10px 16px;
    font-size: 13px;
    gap: 6px;
  }
  .recycle-icon { font-size: 18px; }
  .recycle-text { 
    display: inline; 
    font-size: 12px;
  }
  .user-info {
    padding: 8px 12px;
    gap: 8px;
    border-radius: 10px;
  }
  .user-avatar, .user-avatar-default {
    width: 28px;
    height: 28px;
    font-size: 13px;
  }
  .user-name { 
    font-size: 13px;
    max-width: 60px;
  }
  .order-link {
    padding: 8px 12px;
    font-size: 13px;
    gap: 6px;
    border-radius: 10px;
  }
  .order-link .order-icon { 
    font-size: 16px; 
  }
  .login-btn {
    padding: 8px 18px;
    font-size: 13px;
  }
}
</style>
