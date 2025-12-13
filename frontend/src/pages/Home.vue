<template>
  <div class="xy-home">

    <!-- 1) 促销网格区域 -->
    <div class="promo-section">
      <div class="promo-wrapper">
        <div class="promo-container">
          <!-- 左侧：分类侧栏 -->
          <div class="category-sidebar-promo">
            <div class="cat-header">全部分类</div>
            <ul class="cat-list-promo">
              <li 
                v-for="(cat, idx) in categories" 
                :key="cat.id"
                @mouseenter="activeCategory = cat.id"
                @click="goToCategory(cat.id)"
                :class="{ active: activeCategory === cat.id }"
              >
                <span class="cat-icon">{{ catIcons[idx % catIcons.length] }}</span>
                <span class="cat-name">{{ cat.name }}</span>
              </li>
            </ul>
          </div>

          <!-- 右侧：促销网格 -->
          <div class="promo-grid">
          <!-- 旧机换钱 - 大卡片 -->
          <div class="grid-item recycle-card" @click="goToRecycle">
            <div class="card-content">
              <div class="badge">官方自营</div>
              <h2>旧机换钱</h2>
              <p>比回收站高 20%</p>
              <button class="action-btn">免费估价</button>
            </div>
            <div class="card-img">📱</div>
          </div>

          <!-- 官方验专区 -->
          <div class="grid-item medium-card verified-promo" @click="goToVerifiedProducts">
            <div class="card-content">
              <div class="badge">官方质检</div>
              <h3>官方验专区</h3>
              <p>正品保障，7天无理由</p>
            </div>
          </div>

          <!-- 热门推荐 -->
          <div class="grid-item medium-card hot-promo" @click="goToCategoryByName('手机')">
            <div class="card-content">
              <div class="badge">热门</div>
              <h3>手机专区</h3>
              <p>热门机型低价淘</p>
            </div>
          </div>

          <!-- 电脑专区 -->
          <div class="grid-item medium-card computer-promo" @click="goToCategoryByName('电脑')">
            <div class="card-content">
              <div class="badge">省心购</div>
              <h3>电脑专区</h3>
              <p>笔记本台式机一站式</p>
            </div>
          </div>

          <!-- 平板专区 -->
          <div class="grid-item medium-card tablet-promo" @click="goToCategoryByName('平板')">
            <div class="card-content">
              <div class="badge">热卖</div>
              <h3>平板专区</h3>
              <p>iPad/安卓平板精选</p>
            </div>
          </div>
          </div>
        </div>
      </div>
    </div>


    <!-- 3) 商品流列表 - 标签和商品统一大框 -->
    <main class="main-flow">
      <div class="products-wrapper">
        <div class="flow-tabs-section">
          <div class="flow-tabs">
            <div 
              v-for="tab in tabs" 
              :key="tab.id"
              class="tab-item"
              :class="{ active: activeTab === tab.id }"
              @click="switchTab(tab.id)"
            >
              <div class="tab-title">{{ tab.name }}</div>
              <div class="tab-sub">{{ tab.desc }}</div>
            </div>
          </div>
        </div>

        <div class="goods-list" v-loading="loading">
          <div 
            v-for="product in products" 
            :key="product.id" 
            class="goods-card"
            @click="goToDetail(product.id)"
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

        <div class="loading-state">
          <el-button v-if="hasMore" :loading="loadingMore" text @click="loadMore">
            {{ loadingMore ? '正在加载更多...' : '点击加载更多' }}
          </el-button>
          <div v-else class="no-more">没有更多了，去发布一个吧~</div>
        </div>
      </div>
    </main>

    

    <!-- 4) 页脚（简洁） -->
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Document, List, Star, ChatDotRound, User, SwitchButton, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import { useAuthStore } from '@/stores/auth'
import { getResults } from '@/utils/responseGuard'

const router = useRouter()
const authStore = useAuthStore()

// 状态
const activeCategory = ref(null)
const activeTab = ref('recommend')
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)
const products = ref([])


// 数码分类
const categories = ref([])
const catIcons = ['📱','📷','💻','📘','🎧','🎮','💾','⌚']

// 分类商品数据
const phoneProducts = ref([])
const cameraProducts = ref([])
const computerProducts = ref([])
const tabletProducts = ref([])
const verifiedProducts = ref([])

// 根据分类名称加载商品
const loadCategoryProducts = async () => {
  try {
    // 获取所有商品
    const res = await api.get('/products/', { params: { status: 'active', page_size: 50 } })
    const allProducts = res.data.results || res.data || []
    
    // 按标题关键词分类
    phoneProducts.value = allProducts.filter(p => 
      /手机|iPhone|华为|小米|OPPO|vivo|三星|荣耀/i.test(p.title)
    ).slice(0, 4)
    
    cameraProducts.value = allProducts.filter(p => 
      /相机|摄像|镜头|佳能|尼康|索尼|富士|单反|微单/i.test(p.title)
    ).slice(0, 4)
    
    computerProducts.value = allProducts.filter(p => 
      /电脑|笔记本|台式|MacBook|ThinkPad|联想|戴尔|华硕|显卡|CPU/i.test(p.title)
    ).slice(0, 4)
    
    tabletProducts.value = allProducts.filter(p => 
      /平板|iPad|Pro|Air|安卓平板|华为平板|小米平板/i.test(p.title)
    ).slice(0, 4)

    // 加载官方验货商品
    try {
      const verifiedRes = await api.get('/verified-products/', { params: { page_size: 3 } })
      verifiedProducts.value = verifiedRes.data?.results || verifiedRes.data || []
    } catch (err) {
      console.error('加载官方验货商品失败:', err)
      verifiedProducts.value = []
    }

    // 如果某分类商品不足，用其他商品填充
    const fillProducts = allProducts.filter(p => 
      !phoneProducts.value.includes(p) && 
      !cameraProducts.value.includes(p) && 
      !computerProducts.value.includes(p) && 
      !tabletProducts.value.includes(p)
    )
    
    if (phoneProducts.value.length < 3) {
      phoneProducts.value = [...phoneProducts.value, ...fillProducts.slice(0, 3 - phoneProducts.value.length)]
    }
    if (cameraProducts.value.length < 3) {
      cameraProducts.value = [...cameraProducts.value, ...fillProducts.slice(0, 3 - cameraProducts.value.length)]
    }
    if (computerProducts.value.length < 3) {
      computerProducts.value = [...computerProducts.value, ...fillProducts.slice(0, 3 - computerProducts.value.length)]
    }
    if (tabletProducts.value.length < 3) {
      tabletProducts.value = [...tabletProducts.value, ...fillProducts.slice(0, 3 - tabletProducts.value.length)]
    }
  } catch (err) {
    console.error('加载分类商品失败:', err)
  }
}

// 根据分类名称跳转
const goToCategoryByName = (name) => {
  router.push({ path: '/products', query: { search: name } })
}

// 标签
const tabs = ref([
  { id: 'recommend', name: '猜你喜欢', desc: '为你推荐' },
  { id: 'fresh', name: '最新发布', desc: '刚刚上架' },
  { id: 'nearby', name: '同城好物', desc: '就在身边' },
  { id: 'low_price', name: '捡漏专区', desc: '超低价格' },
])

// 工具方法
const formatPriceInt = (price) => Math.floor(price).toLocaleString()
const formatPriceDecimal = (price) => {
  const decimal = price.toString().split('.')[1]
  return decimal ? `.${decimal}` : ''
}

const resolveVerifiedThumb = (p) => {
  // 优先 detail_images / images / cover_image / image_url
  const fallback = 'https://via.placeholder.com/80'
  if (!p) return fallback
  const pick = (img) => {
    if (!img) return null
    if (typeof img === 'string') return getImageUrl(img)
    if (img.image) return getImageUrl(img.image)
    if (img.url) return getImageUrl(img.url)
    if (img.image_url) return getImageUrl(img.image_url)
    if (img.imageUrl) return getImageUrl(img.imageUrl)
    return null
  }
  if (Array.isArray(p.detail_images) && p.detail_images.length) {
    const src = pick(p.detail_images[0])
    if (src) return src
  }
  if (Array.isArray(p.images) && p.images.length) {
    const src = pick(p.images[0])
    if (src) return src
  }
  if (p.cover_image) {
    const src = pick(p.cover_image)
    if (src) return src
  }
  return fallback
}


const switchTab = (id) => {
  activeTab.value = id
  products.value = []
  loadProducts()
}

const goToPublish = () => router.push('/publish')
const goToDetail = (id) => router.push(`/products/${id}`)
const goToProfile = () => router.push('/profile')
const goToVerifiedProducts = () => router.push('/verified-products')
const goToVerifiedDetail = (id) => router.push(`/verified-products/${id}`)
const goToRecycle = () => router.push('/recycle')

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
      router.push('/profile')  // 跳转到个人中心
      break
    case 'orders':
      router.push('/profile?tab=bought')  // 跳转到个人中心的"我买到的"
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

// 加载分类（从后端）
const loadCategories = async () => {
  try {
    const res = await api.get('/categories/')
    let allCategories = getResults(res.data)
    
    // 按数码产品重要性排序
    const categoryOrder = ['手机', '平板', '笔记本电脑', '台式电脑', '摄影摄像', '智能手表', '耳机音响', '游戏设备', '数码配件', '其他数码']
    allCategories.sort((a, b) => {
      const indexA = categoryOrder.indexOf(a.name)
      const indexB = categoryOrder.indexOf(b.name)
      return indexA - indexB
    })
    
    categories.value = allCategories
  } catch (err) {
    console.error('加载分类失败:', err)
    categories.value = []
  }
}

// 点击分类，跳到商品列表并带上分类筛选
const goToCategory = (categoryId) => {
  if (!categoryId) return
  router.push({ path: '/products', query: { category: categoryId } })
}

// 加载商品
const loadProducts = async (append = false) => {
  if (!append) loading.value = true
  else loadingMore.value = true

  try {
    const params = {
      status: 'active',
      page: append ? Math.ceil(products.value.length / 30) + 1 : 1,
      page_size: 30,
      ordering: activeTab.value === 'fresh' ? '-created_at' : (activeTab.value === 'low_price' ? 'price' : '-created_at'),
    }

    const res = await api.get('/products/', { params })
    const newProducts = getResults(res.data)

    if (append) products.value.push(...newProducts)
    else products.value = newProducts

    hasMore.value = !!res.data.next
  } catch (error) {
    console.error('加载商品失败:', error)
    ElMessage.error('加载商品失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => loadProducts(true)

onMounted(async () => {
  // 初始化认证状态
  if (!authStore.user && !authStore.loading) {
    await authStore.init()
  }
  loadCategories()
  loadProducts()
  loadCategoryProducts()
  const onScrollLoadMore = () => {
    if (loadingMore.value || loading.value || !hasMore.value) return
    const scrollBottom = window.innerHeight + window.scrollY
    const docHeight = document.documentElement.scrollHeight || document.body.scrollHeight
    if (scrollBottom >= docHeight - 200) loadMore()
  }
  window.addEventListener('scroll', onScrollLoadMore, { passive: true })
  onBeforeUnmount(() => {
    window.removeEventListener('scroll', onScrollLoadMore)
  })
})
</script>

<style scoped>
/* ==================== 易淘官网风格 - 精致美观版 ==================== */
.xy-home {
  margin: 0;
  padding: 0;
  width: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", "Microsoft YaHei", sans-serif;
  background: var(--bg-page);
  min-height: 100vh;
  color: var(--text-primary);
}

/* ==================== 顶部导航 ==================== */
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

/* Logo - 易淘特色字体 */
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

/* 用户区域 - 靠右对齐 */
.user-section {
  display: flex;
  align-items: center;
  gap: 20px;
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

/* ==================== 促销网格区域 ==================== */
.promo-section {
  padding: 20px 0;
  background: var(--bg-page);
}

.promo-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.promo-container {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

/* 分类侧栏 - 在促销区域左侧 */
.category-sidebar-promo {
  width: 200px;
  flex-shrink: 0;
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 16px;
  height: 315px; /* 与回收卡片高度一致：150px * 2 + 15px gap = 315px */
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.category-sidebar-promo .cat-header {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--brand-orange);
}

.category-sidebar-promo .cat-list-promo {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  flex: 1;
  overflow-y: auto;
}

.category-sidebar-promo .cat-list-promo li {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.15s;
  color: var(--text-primary);
  font-size: 13px;
  border-radius: var(--radius-md);
  background: var(--bg-page);
  text-align: center;
}

.category-sidebar-promo .cat-list-promo li:hover {
  background: linear-gradient(135deg, #fff7e6, #ffe8cc);
  color: var(--brand-orange);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.category-sidebar-promo .cat-list-promo li.active {
  background: linear-gradient(135deg, #fff7e6, #ffe8cc);
  color: var(--brand-orange);
  font-weight: 600;
}

.category-sidebar-promo .cat-list-promo li .cat-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.category-sidebar-promo .cat-list-promo li .cat-name {
  font-size: 12px;
  line-height: 1.3;
}

.promo-grid {
  flex: 1;
  display: grid;
  /* 左侧占 1.2 份宽，右侧两列各占 1 份 */
  grid-template-columns: 1.2fr 1fr 1fr;
  grid-template-rows: 150px 150px;
  gap: 15px;
}

/* 旧机换钱大卡片 */
.recycle-card {
  /* 占据左侧第1列，跨越2行 -> 形成垂直长条 */
  grid-column: 1 / 2;
  grid-row: 1 / 3;
  
  /* 视觉样式：红橙渐变，模仿闲鱼 */
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
  color: white;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(255, 107, 107, 0.3);
}

.recycle-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(255, 107, 107, 0.4);
}

.recycle-card .card-content {
  position: relative;
  z-index: 2;
}

.recycle-card .badge {
  background: rgba(255, 255, 255, 0.2);
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 10px;
  backdrop-filter: blur(10px);
}

.recycle-card h2 {
  font-size: 28px;
  margin: 0 0 8px 0;
  font-weight: 800;
}

.recycle-card p {
  font-size: 14px;
  opacity: 0.9;
  margin: 5px 0 0 0;
}

.recycle-card .action-btn {
  background: white;
  color: #ff6b6b;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  font-weight: bold;
  width: fit-content;
  margin-top: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.recycle-card .action-btn:hover {
  background: #fff8f0;
  transform: scale(1.05);
}

.recycle-card .card-img {
  position: absolute;
  bottom: 10px;
  right: 10px;
  font-size: 80px;
  transform: rotate(-15deg);
  opacity: 0.3;
  z-index: 1;
  line-height: 1;
  pointer-events: none;
}

/* 中等卡片 */
.medium-card {
  border-radius: var(--radius-lg);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: var(--shadow-sm);
}

.medium-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.verified-promo {
  background: linear-gradient(145deg, #e6f7ff 0%, #bae7ff 100%);
}

.hot-promo {
  background: linear-gradient(145deg, #fffef5 0%, #fff3cd 100%);
}

.medium-card .badge {
  background: rgba(255, 255, 255, 0.8);
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  margin-bottom: 8px;
  font-weight: 600;
}

.medium-card h3 {
  font-size: 18px;
  margin: 0 0 6px 0;
  font-weight: 700;
  color: var(--text-primary);
}

.medium-card p {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
}

.computer-promo {
  background: linear-gradient(145deg, #f0fffe 0%, #b5f5ec 100%);
}

.tablet-promo {
  background: linear-gradient(145deg, #fff8f5 0%, #ffd8c2 100%);
}

/* ==================== 首屏区域 ==================== */
.hero-section { 
  padding: 20px 0;
  background: var(--bg-page);
}

/* 分类和推荐的统一大框 */
.hero-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-container { 
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  display: flex;
  gap: 0;
  overflow: hidden;
}

/* 分类侧栏 - 在大框内部 */
.category-sidebar { 
  width: 190px;
  flex-shrink: 0;
  background: #fafafa;
  border-right: 1px solid #f0f0f0;
  padding: 16px 0;
}
.cat-header { display: none; }
.cat-list { 
  list-style: none; 
  padding: 0; 
  margin: 0;
}
.cat-list li { 
  padding: 11px 18px;
  display: flex; 
  align-items: center; 
  cursor: pointer; 
  transition: all 0.15s; 
  color: var(--text-primary); 
  font-size: 14px;
}
.cat-list li:hover { 
  background: linear-gradient(90deg, #fff7e6, transparent); 
  color: var(--brand-orange); 
}
.cat-list li .cat-icon { margin-right: 10px; font-size: 15px; }
.cat-list li .cat-name { flex: 1; }
.cat-list li .el-icon { display: none; }

/* 推荐卡片区域 - 在大框内部 */
.category-boxes {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 16px;
  padding: 16px;
  background: var(--bg-white);
}

.category-box {
  border-radius: var(--radius-md);
  padding: 18px 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  min-height: 160px;
  position: relative;
  overflow: hidden;
}

.category-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.3) 0%, transparent 50%);
  pointer-events: none;
}

.category-box:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

/* 卡片渐变色 - 更柔和 */
.phone-box { background: linear-gradient(145deg, #fffef5 0%, #fff3cd 100%); }
.verified-box { background: linear-gradient(145deg, #e6f7ff 0%, #bae7ff 100%); }
.camera-box { background: linear-gradient(145deg, #fef5f8 0%, #ffd9e8 100%); }
.computer-box { background: linear-gradient(145deg, #f0fffe 0%, #b5f5ec 100%); }
.tablet-box { background: linear-gradient(145deg, #fff8f5 0%, #ffd8c2 100%); }

.box-header { margin-bottom: 14px; position: relative; z-index: 1; }

.box-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.title-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.play-icon {
  font-size: 10px;
  color: var(--brand-orange);
  background: rgba(255,102,0,0.1);
  padding: 2px 6px;
  border-radius: 10px;
}

.box-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

/* 宣传标签 */
.promo-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.promo-tag {
  font-size: 11px;
  color: #1890ff;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
  white-space: nowrap;
  border: 1px solid rgba(24, 144, 255, 0.3);
  box-shadow: 0 1px 3px rgba(24, 144, 255, 0.15);
  transition: all 0.2s ease;
}

.promo-tag:hover {
  background: #fff;
  border-color: rgba(24, 144, 255, 0.5);
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.25);
  transform: translateY(-1px);
}

.box-products {
  display: flex;
  gap: 10px;
  flex: 1;
  align-items: flex-end;
  position: relative;
  z-index: 1;
}

.mini-product {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255,255,255,0.9);
  border-radius: var(--radius-sm);
  padding: 10px 6px 8px;
  transition: all 0.25s;
  backdrop-filter: blur(10px);
}

.mini-product:hover {
  transform: translateY(-4px) scale(1.02);
  background: #fff;
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.mini-product img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  margin-bottom: 8px;
}

.mini-price {
  font-size: 14px;
  font-weight: 700;
  color: var(--price-color);
}

/* ==================== 商品流区域 ==================== */
.main-flow { 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 0 20px 60px;
}

/* 商品和标签的统一大框 */
.products-wrapper {
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 20px;
  margin-top: 20px;
}

/* 标签栏区域 */
.flow-tabs-section { 
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.flow-tabs { 
  display: flex; 
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.flow-tabs .tab-item { 
  cursor: pointer; 
  padding: 8px 20px;
  border-radius: var(--radius-full);
  background: var(--bg-page);
  transition: all 0.2s;
  border: 1px solid transparent;
}

.flow-tabs .tab-item .tab-title { 
  font-size: 13px; 
  font-weight: 500; 
  color: var(--text-secondary);
}

.flow-tabs .tab-item .tab-sub { display: none; }

.flow-tabs .tab-item:hover {
  background: #eee;
}

.flow-tabs .tab-item.active {
  background: linear-gradient(135deg, #fff8f0, #ffe8cc);
  border-color: #ffc069;
}

.flow-tabs .tab-item.active .tab-title { 
  color: var(--brand-orange);
  font-weight: 600;
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

/* 加载更多 */
.loading-state { 
  text-align: center; 
  padding: 40px 0 20px;
}

.loading-state .no-more { 
  color: var(--text-light); 
  font-size: 13px;
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
  .header-content, .hero-wrapper, .main-flow {
    max-width: 100%;
  }
  .goods-list { grid-template-columns: repeat(4, 1fr); }
}

@media (max-width: 992px) {
  .goods-list { grid-template-columns: repeat(3, 1fr); }
  .category-boxes { grid-template-columns: 1fr 1fr; }
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
  .promo-wrapper { padding: 0 12px; }
  .promo-container {
    flex-direction: column;
  }
  .category-sidebar-promo {
    width: 100%;
    margin-bottom: 12px;
  }
  .category-sidebar-promo .cat-list-promo {
    grid-template-columns: repeat(3, 1fr);
  }
  .promo-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    gap: 12px;
  }
  .recycle-card {
    grid-column: 1;
    grid-row: 1;
    min-height: 200px;
  }
  .medium-card {
    grid-column: 1;
    min-height: 120px;
  }
  .hero-container { flex-direction: column; }
  .hero-wrapper { padding: 0 12px; }
  .products-wrapper { padding: 16px; margin-top: 16px; }
  .category-sidebar { 
    width: 100%; 
    padding: 12px;
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
  }
  .cat-list { 
    display: flex; 
    flex-wrap: wrap; 
    gap: 8px; 
  }
  .cat-list li { 
    padding: 8px 14px; 
    background: var(--bg-white); 
    border-radius: var(--radius-full);
    font-size: 12px;
    border: 1px solid #eee;
  }
  .category-boxes { grid-template-columns: 1fr; gap: 12px; padding: 12px; }
  .category-box { min-height: 140px; }
  .goods-list { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .goods-info { padding: 10px; }
  .goods-title { font-size: 13px; height: 38px; }
  .flow-tabs-section { padding-bottom: 12px; margin-bottom: 12px; }
  .flow-tabs { gap: 8px; }
  .flow-tabs .tab-item { padding: 6px 14px; }
  .flow-tabs .tab-item .tab-title { font-size: 12px; }
}
</style>
