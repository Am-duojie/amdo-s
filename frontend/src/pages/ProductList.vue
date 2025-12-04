<template>
  <div class="xy-product-list">
    <!-- 1) 顶部导航 - 易淘风格 -->
    <header class="header-sticky">
      <div class="header-content">
        <!-- Logo -->
        <div class="brand-logo" @click="router.push('/')">
          <span class="logo-icon">🛒</span>
          <span class="logo-text">易淘</span>
        </div>

        <!-- 搜索区 -->
        <div class="search-section">
          <div class="search-box">
            <input 
              v-model="searchText" 
              :placeholder="searchPlaceholder" 
              @keyup.enter="handleSearch"
              class="search-input"
            />
            <button class="search-btn" @click="handleSearch">
              <span class="search-icon">🔍</span>搜索
            </button>
          </div>
        </div>

        <!-- 右侧用户区 -->
        <div class="user-section">
          <template v-if="authStore.user">
            <!-- 订单入口 -->
            <div class="order-link" @click="goToOrders">
              <span class="order-icon">📋</span>
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
                  <span class="user-meta-desc">个人中心</span>
                </div>
                <span class="dropdown-arrow" aria-hidden="true">▼</span>
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

    <!-- 主内容区域 -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- 筛选区域 -->
        <div class="filter-section">
          <div class="filter-header">
            <span class="filter-title">筛选条件</span>
            <el-button text @click="handleReset" size="small">清空</el-button>
          </div>
          
          <div class="filter-grid">
            <!-- 分类筛选 -->
            <div class="filter-item">
              <label class="filter-label">分类</label>
              <el-select v-model="filters.category" placeholder="全部分类" clearable @change="onCategoryChange" @clear="onCategoryClear">
                <el-option
                  v-for="cat in categories"
                  :key="cat.id"
                  :label="cat.name"
                  :value="String(cat.id)"
                />
              </el-select>
            </div>

            <!-- 成色筛选 -->
            <div class="filter-item">
              <label class="filter-label">成色</label>
              <el-select v-model="filters.condition" placeholder="全部成色" clearable>
                <el-option label="全新" value="new" />
                <el-option label="几乎全新" value="like_new" />
                <el-option label="良好" value="good" />
                <el-option label="一般" value="fair" />
                <el-option label="较差" value="poor" />
              </el-select>
            </div>

            <!-- 价格筛选 -->
            <div class="filter-item price-filter">
              <label class="filter-label">价格范围</label>
              <div class="price-inputs">
                <el-input-number
                  v-model="filters.minPrice"
                  :min="0"
                  :max="999999"
                  placeholder="最低"
                  size="small"
                  :controls="false"
                />
                <span class="price-separator">-</span>
                <el-input-number
                  v-model="filters.maxPrice"
                  :min="0"
                  :max="999999"
                  placeholder="最高"
                  size="small"
                  :controls="false"
                />
              </div>
            </div>

            <!-- 排序 -->
            <div class="filter-item">
              <label class="filter-label">排序</label>
              <el-select v-model="sortBy" placeholder="默认排序">
                <el-option label="默认" value="" />
                <el-option label="价格从低到高" value="price" />
                <el-option label="价格从高到低" value="-price" />
                <el-option label="最新发布" value="-created_at" />
                <el-option label="最多浏览" value="-view_count" />
              </el-select>
            </div>
          </div>
        </div>

        <!-- 商品列表 - 与主页风格一致 -->
        <div class="products-wrapper" v-loading="loading">
          <div class="result-header">
            <span class="result-count">找到 <span class="count-num">{{ pagination.total }}</span> 件商品</span>
          </div>

          <el-empty v-if="!loading && products.length === 0" description="暂无商品，换个条件试试吧~" />
          
          <div v-else class="goods-list">
            <div 
              v-for="product in products" 
              :key="product.id" 
              class="goods-card"
              @click="router.push(`/products/${product.id}`)"
            >
              <div class="goods-img-box">
                <img 
                  :src="product.images && product.images.length > 0 ? getImageUrl(product.images[0].image) : 'https://via.placeholder.com/400x220?text=No+Image'" 
                  loading="lazy" 
                  :alt="product.title"
                  @error="(e) => (e.target.src = 'https://via.placeholder.com/400x220?text=No+Image')"
                />
                <div class="goods-status" v-if="product.view_count > 300">热门</div>
              </div>
              <div class="goods-info">
                <div class="goods-title">{{ product.title }}</div>
                <div class="goods-price-row">
                  <div class="price">
                    <span class="symbol">¥</span>
                    <span class="num">{{ formatPriceInt(product.price) }}</span>
                    <span class="decimal">{{ formatPriceDecimal(product.price) }}</span>
                  </div>
                  <div class="want-num">{{ product.favorite_count || 0 }}人收藏</div>
                </div>
                <div class="seller-row">
                  <div class="seller-left">
                    <div class="seller-avatar-s"></div>
                    <span class="seller-name">{{ product.seller?.username || '匿名用户' }}</span>
                  </div>
                  <div class="credit-tag" v-if="product.view_count > 100">热度</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div v-if="pagination.total > pagination.pageSize" class="pagination-wrapper">
            <el-pagination
              v-model:current-page="pagination.current"
              :total="pagination.total"
              :page-size="pagination.pageSize"
              layout="prev, pager, next"
              background
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="simple-footer">
      <div class="footer-inner">
        <p class="footer-links">
          <a href="#">关于我们</a> | <a href="#">用户协议</a> | <a href="#">隐私政策</a> | <a href="#">联系我们</a>
        </p>
        <p class="copyright">
          © 2024 易淘 版权所有
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Document, List, Star, ChatDotRound, User, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 用户信息计算属性
const userDisplayName = computed(() => authStore.user?.nickname || authStore.user?.username || '易淘用户')
const userInitial = computed(() => authStore.user?.username?.charAt(0)?.toUpperCase() || 'U')

const products = ref([])
const categories = ref([])
const loading = ref(false)
const searchText = ref(route.query.search || '')
const sortBy = ref('')
const filters = ref({
  category: route.query.category ? String(route.query.category) : '',
  condition: '',
  status: 'active',
  minPrice: null,
  maxPrice: null,
})
const pagination = ref({
  current: 1,
  pageSize: 30,
  total: 0,
})

// 热词（从数据库商品动态生成）
const hotWords = ref([])

// 动态搜索提示（从热词中随机选取）
const searchPlaceholder = computed(() => {
  if (hotWords.value.length >= 3) {
    const samples = hotWords.value.slice(0, 3)
    return `搜索好物，例如 ${samples.join(' / ')}`
  }
  return '搜索二手好物'
})

// 加载热词（从数据库获取更多商品生成）
const loadHotWords = async () => {
  try {
    const res = await api.get('/products/', { 
      params: { status: 'active', page_size: 30 } 
    })
    const productList = res.data.results || res.data
    
    if (!productList || productList.length === 0) return
    
    // 从商品标题中提取关键词
    const words = []
    productList.forEach(product => {
      if (product.title) {
        // 提取标题的核心关键词（前8个字符或完整短标题）
        const title = product.title.trim()
        const keyword = title.length > 12 ? title.substring(0, 8) : title
        if (keyword.length >= 2 && !words.includes(keyword)) {
          words.push(keyword)
        }
      }
    })
    
    // 取最多10个热词
    hotWords.value = words.slice(0, 10)
  } catch (err) {
    console.error('加载热词失败:', err)
  }
}

const goToLogin = () => router.push('/login')
const goToOrders = () => router.push('/profile?tab=bought')

onMounted(() => {
  loadCategories()
  loadHotWords()
  loadProducts()
})

// 监听路由中的 category 变化（从首页分类点击跳转时生效）
watch(() => route.query.category, (val) => {
  filters.value.category = val ? String(val) : ''
  pagination.value.current = 1
  loadProducts()
})

const onCategoryChange = (val) => {
  // 同步到路由，便于刷新/分享保留筛选条件
  router.replace({ path: '/products', query: { ...route.query, category: val || '' } })
  pagination.value.current = 1
  loadProducts()
}

const onCategoryClear = () => {
  filters.value.category = ''
  router.replace({ path: '/products', query: { ...route.query, category: '' } })
  pagination.value.current = 1
  loadProducts()
}

watch([() => filters.value.category, () => filters.value.condition, () => filters.value.minPrice, () => filters.value.maxPrice, sortBy], () => {
  pagination.value.current = 1
  loadProducts()
})

const loadCategories = async () => {
  try {
    const res = await api.get('/categories/')
    // 兼容 DRF 分页结构：优先使用 results
    categories.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

const loadProducts = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize,
      search: searchText.value,
      category: filters.value.category,
      condition: filters.value.condition,
      status: filters.value.status,
      min_price: filters.value.minPrice,
      max_price: filters.value.maxPrice,
    }
    
    if (sortBy.value) {
      params.ordering = sortBy.value
    }
    
    const res = await api.get('/products/', { params })
    
    // 处理分页数据
    if (res.data.results) {
      // DRF 分页格式
      products.value = res.data.results
      pagination.value.total = res.data.count || 0
    } else if (Array.isArray(res.data)) {
      // 数组格式
      products.value = res.data
      pagination.value.total = res.data.length
    } else {
      products.value = []
      pagination.value.total = 0
    }
    
    console.log('加载商品成功:', {
      page: pagination.value.current,
      total: pagination.value.total,
      count: products.value.length,
      category: filters.value.category,
      params: params
    })
    
    // 调试：显示返回的商品分类
    if (products.value.length > 0) {
      const categories_in_results = [...new Set(products.value.map(p => p.category?.name || '无分类'))]
      console.log('返回商品的分类:', categories_in_results)
    }
  } catch (error) {
    console.error('加载商品失败:', error)
    products.value = []
    pagination.value.total = 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.value.current = 1
  loadProducts()
}

const handleReset = () => {
  searchText.value = ''
  filters.value = {
    category: '',
    condition: '',
    status: 'active',
    minPrice: null,
    maxPrice: null,
  }
  sortBy.value = ''
  pagination.value.current = 1
  loadProducts()
}

const handlePageChange = (page) => {
  console.log('页面切换:', page)
  pagination.value.current = page
  loadProducts()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 价格格式化
const formatPriceInt = (price) => Math.floor(price).toLocaleString()
const formatPriceDecimal = (price) => {
  const decimal = price.toString().split('.')[1]
  return decimal ? `.${decimal}` : ''
}

// 处理用户菜单命令
const handleUserMenuCommand = async (command) => {
  switch (command) {
    case 'trade':
      router.push('/profile?tab=bought')  // 跳转到我的交易（默认显示我买到的）
      break
    case 'favorites':
      router.push('/profile?tab=favorites')  // 跳转到我的收藏
      break
    case 'settings':
      router.push('/profile?tab=address')  // 跳转到账户设置（默认显示收货地址）
      break
    case 'products':
      router.push('/profile')
      break
    case 'orders':
      router.push('/profile?tab=bought')
      break
    case 'messages':
      router.push('/messages')
      break
    case 'profile':
      router.push('/profile')
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
</script>

<style scoped>
/* ==================== 易淘官网风格 - 与主页统一 ==================== */
.xy-product-list {
  --brand: #ffe400;
  --brand-orange: #ff6600;
  --price-color: #ff2442;
  --text-primary: #222;
  --text-secondary: #666;
  --text-light: #999;
  --bg-page: #f5f5f5;
  --bg-white: #fff;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 50px;
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
  
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", "Microsoft YaHei", sans-serif;
  background: var(--bg-page);
  min-height: 100vh;
  color: var(--text-primary);
  margin: 0;
  padding: 0;
  width: 100%;
}

/* ==================== 顶部导航 - 与主页一致 ==================== */
.header-sticky {
  background: linear-gradient(135deg, #ffe400 0%, #ffd000 50%, #ffe400 100%);
  background-size: 200% 200%;
  animation: gradientShift 10s ease infinite;
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 16px 0;
  margin: 0;
  box-shadow: 0 4px 24px rgba(0,0,0,0.1);
  border-bottom: 2px solid rgba(255,255,255,0.3);
  width: 100%;
  left: 0;
  right: 0;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 40px;
  padding: 0 20px;
}

/* Logo */
.brand-logo { 
  cursor: pointer; 
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.6));
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.brand-logo:hover { 
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.12);
  background: linear-gradient(135deg, rgba(255,255,255,1), rgba(255,255,255,0.8));
}
.logo-icon {
  font-size: 32px;
  line-height: 1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
  animation: bounce 2s ease-in-out infinite;
}
.logo-text { 
  font-size: 36px; 
  font-weight: 900; 
  background: linear-gradient(135deg, #ff6600, #ff8833);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  letter-spacing: -1px;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-4px) scale(1.05); }
}

/* 搜索区域 */
.search-section { 
  flex: 1;
  max-width: 580px;
}

.search-box {
  display: flex;
  height: 44px;
  background: var(--bg-white);
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.search-box .search-input {
  flex: 1;
  border: none;
  padding: 0 20px;
  font-size: 14px;
  outline: none;
  background: transparent;
}
.search-box .search-input::placeholder { color: var(--text-light); }

.search-box .search-btn {
  padding: 0 24px;
  background: var(--brand-orange);
  border: none;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: background 0.2s;
}
.search-box .search-btn:hover { background: #ff7722; }
.search-box .search-btn .search-icon { font-size: 13px; }

/* 用户区域 */
.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  margin-left: auto;
  justify-content: flex-end;
}

/* 自定义下拉菜单 */
.user-dropdown {
  position: relative;
  display: inline-block;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 10px 16px;
  border-radius: 14px;
  background: rgba(255,255,255,0.92);
  transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
  border: 1px solid rgba(255,255,255,0.4);
}
.user-dropdown:hover .user-info { 
  background: #fff8e6;
  border-color: rgba(255,106,0,0.3);
  box-shadow: 0 6px 18px rgba(255,106,0,0.12);
}

.dropdown-arrow {
  font-size: 12px;
  color: #666;
  margin-left: 2px;
  transition: transform 0.1s cubic-bezier(0.4, 0, 0.2, 1), color 0.1s linear;
}
.user-dropdown:hover .dropdown-arrow {
  color: #ff6600;
  transform: rotate(180deg);
}

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
  color: #222;
  font-weight: 600;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-dropdown:hover .user-meta-name {
  color: #ff6600;
}

.user-meta-desc {
  font-size: 11px;
  color: #999;
  letter-spacing: 0.2px;
}
.user-dropdown:hover .user-meta-desc {
  color: #ffb347;
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

.user-avatar, .user-avatar-default {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
}
.user-avatar { 
  object-fit: cover; 
  border: 2px solid rgba(255,106,0,0.15);
  transition: all 0.25s ease;
}
.user-info:hover .user-avatar {
  border-color: rgba(255,106,0,0.4);
}
.user-avatar-default {
  background: linear-gradient(135deg, #ff6600, #ff8833);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
  border: 2px solid rgba(255,106,0,0.15);
  transition: all 0.25s ease;
}
.user-info:hover .user-avatar-default {
  border-color: rgba(255,106,0,0.4);
}
.user-name {
  font-size: 14px;
  color: #222;
  font-weight: 500;
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-info:hover .user-name {
  color: #ff6600;
}

.order-link {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #222;
  cursor: pointer;
  padding: 10px 16px;
  border-radius: 12px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(8px);
  transition: all 0.25s ease;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,0.3);
}
.order-link:hover { 
  background: #fff8e6;
  border-color: rgba(255,106,0,0.2);
  color: #ff6600; 
}
.order-link .order-icon {
  font-size: 18px;
  line-height: 1;
}

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

/* ==================== 主内容区域 ==================== */
.main-content { 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 0 20px 60px;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-top: 20px;
}

/* ==================== 筛选区域 ==================== */
.filter-section {
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 20px 24px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.filter-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  align-items: end;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.price-filter .price-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-separator {
  color: var(--text-light);
  font-size: 14px;
}

/* ==================== 商品列表区域 ==================== */
.products-wrapper {
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 20px;
  min-height: 600px;
}

.result-header {
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.result-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.count-num {
  color: var(--brand-orange);
  font-weight: 600;
  font-size: 16px;
}

/* 商品网格 - 5列 */
.goods-list { 
  display: grid; 
  grid-template-columns: repeat(5, 1fr); 
  gap: 16px;
}

.goods-card { 
  background: var(--bg-white); 
  border-radius: var(--radius-md); 
  overflow: hidden; 
  cursor: pointer; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
}

.goods-card:hover { 
  transform: translateY(-6px); 
  box-shadow: var(--shadow-lg);
}

.goods-img-box { 
  width: 100%; 
  aspect-ratio: 1;
  background: var(--bg-page); 
  position: relative;
  overflow: hidden;
}

.goods-img-box img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.goods-card:hover .goods-img-box img {
  transform: scale(1.08);
}

.goods-img-box .goods-status { 
  position: absolute; 
  top: 10px; 
  left: 10px; 
  background: linear-gradient(135deg, #ff6a00, #ee3f00);
  color: #fff; 
  font-size: 10px; 
  padding: 3px 8px; 
  border-radius: 4px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.goods-info { padding: 14px; }

.goods-title { 
  font-size: 14px; 
  color: var(--text-primary); 
  line-height: 1.5; 
  height: 42px; 
  overflow: hidden; 
  display: -webkit-box; 
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 10px;
  font-weight: 400;
}

.goods-price-row { 
  display: flex; 
  align-items: baseline; 
  justify-content: space-between;
  margin-bottom: 10px;
}

.goods-price-row .price { color: var(--price-color); font-weight: 700; }
.goods-price-row .price .symbol { font-size: 12px; }
.goods-price-row .price .num { font-size: 20px; }
.goods-price-row .price .decimal { font-size: 12px; }
.goods-price-row .want-num { font-size: 11px; color: var(--text-light); }

.seller-row { 
  display: flex; 
  align-items: center; 
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-light);
}

.seller-row .seller-left { display: flex; align-items: center; gap: 6px; }
.seller-row .seller-avatar-s { 
  width: 16px; 
  height: 16px; 
  background: linear-gradient(135deg, #e0e0e0, #bdbdbd); 
  border-radius: 50%;
}
.seller-row .seller-name {
  max-width: 55px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.seller-row .credit-tag { 
  color: var(--brand-orange); 
  background: #fff7e6;
  padding: 2px 6px; 
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
}

/* 分页 */
.pagination-wrapper { 
  text-align: center; 
  padding: 40px 0 20px;
}

/* 页脚 */
.simple-footer { 
  background: var(--bg-white); 
  padding: 32px 0; 
  text-align: center;
  border-top: 1px solid #eee;
}

.simple-footer .footer-links a { 
  color: var(--text-light); 
  text-decoration: none; 
  margin: 0 12px; 
  font-size: 12px;
  transition: color 0.2s;
}
.simple-footer .footer-links a:hover { color: var(--text-secondary); }

.simple-footer .copyright { 
  margin-top: 12px; 
  color: #ccc; 
  font-size: 11px;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1240px) {
  .header-content, .main-content {
    max-width: 100%;
  }
  .goods-list { grid-template-columns: repeat(4, 1fr); }
}

@media (max-width: 992px) {
  .goods-list { grid-template-columns: repeat(3, 1fr); }
  .filter-grid { grid-template-columns: repeat(2, 1fr); }
  .search-section { max-width: 400px; }
}

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
  .main-content { padding: 16px 12px 40px; }
  .filter-section { padding: 16px; }
  .filter-grid { grid-template-columns: 1fr; gap: 12px; }
  .products-wrapper { padding: 16px; }
  .goods-list { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .goods-info { padding: 10px; }
  .goods-title { font-size: 13px; height: 38px; }
}
</style>
