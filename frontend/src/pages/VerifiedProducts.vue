<template>
  <div class="verified-products-page">
    <PageHeader :theme="'blue'" :verifiedMode="true" />
    
    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 左侧筛选栏 -->
      <aside class="filter-sidebar">
        <div class="filter-header">
          <span class="filter-icon">🔍</span>
          <span class="filter-title">筛选</span>
        </div>

        <!-- 分类筛选 -->
        <div class="filter-section">
          <div class="section-title">分类</div>
          <div class="category-grid">
            <div 
              v-for="cat in deviceCategories" 
              :key="cat.type"
              class="category-btn"
              :class="{ active: activeCategory === cat.type }"
              @click="selectCategory(cat.type)"
            >
              {{ cat.name }}
            </div>
          </div>
        </div>

        <!-- 品牌筛选 -->
        <div class="filter-section">
          <div class="section-title">品牌</div>
          <div class="brand-list">
            <div 
              class="brand-item"
              :class="{ active: selectedBrand === '' }"
              @click="selectBrand('')"
            >
              <div class="radio-btn" :class="{ checked: selectedBrand === '' }">
                <span v-if="selectedBrand === ''" class="radio-dot"></span>
              </div>
              <span class="brand-label">全部</span>
            </div>
            <div 
              v-for="brand in currentBrands" 
              :key="brand.name"
              class="brand-item"
              :class="{ active: selectedBrand === brand.name }"
              @click="selectBrand(brand.name)"
            >
              <div class="radio-btn" :class="{ checked: selectedBrand === brand.name }">
                <span v-if="selectedBrand === brand.name" class="radio-dot"></span>
              </div>
              <span class="brand-label">{{ brand.name }}</span>
            </div>
          </div>
        </div>

        <!-- 成色筛选 -->
        <div class="filter-section">
          <div class="section-title">成色</div>
          <div class="condition-grid">
            <div 
              v-for="condition in conditionOptions" 
              :key="condition.value"
              class="condition-btn"
              :class="{ 
                active: filters.condition === condition.value,
                [condition.color]: filters.condition === condition.value
              }"
              @click="selectCondition(condition.value)"
            >
              {{ condition.label }}
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧商品区域 -->
      <div class="products-area">
        <!-- 顶部导航标签 -->
        <div class="top-tabs">
          <div 
            class="tab-item"
            :class="{ active: activeTab === 'market' }"
            @click="activeTab = 'market'"
          >
            逛市场
          </div>
          <div 
            class="tab-item"
            :class="{ active: activeTab === 'recommend' }"
            @click="activeTab = 'recommend'"
          >
            猜你喜欢
          </div>
        </div>

        <!-- 商品列表头部 -->
        <div class="products-header">
          <div class="header-left">
            <h2 class="products-title">全部商品</h2>
            <span class="products-count">共{{ pagination.total }}件商品</span>
          </div>
          <div class="header-right">
            <div class="search-box">
              <span class="search-icon">🔍</span>
              <input 
                v-model="searchKeyword" 
                placeholder="当前结果中搜索"
                class="search-input"
                @keyup.enter="handleSearch"
              />
            </div>
          </div>
        </div>

        <!-- 商品列表 -->
        <div class="products-container">
          <!-- 加载状态 -->
          <div v-if="loading && products.length === 0" class="loading-state">
            <div class="loading-spinner"></div>
            <div class="loading-text">加载中...</div>
          </div>

          <!-- 空状态 -->
          <div v-else-if="!loading && products.length === 0" class="empty-state">
            <div class="empty-icon">📦</div>
            <div class="empty-text">暂无符合条件的商品</div>
            <button class="empty-btn" @click="clearAllFilters">清空筛选</button>
          </div>

          <!-- 商品网格 -->
          <div v-else class="products-grid">
            <div 
              v-for="product in products" 
              :key="product.id"
              class="product-card"
              @click="goToDetail(product.id)"
            >
              <div class="product-image-wrapper">
                <img 
                  :src="product.images?.length ? product.images[0].image : defaultImage"
                  :alt="product.title"
                  class="product-image"
                  loading="lazy"
                  @error="handleImageError"
                />
                <div class="condition-badge" :class="getConditionBadgeClass(product.condition)">
                  {{ getConditionText(product.condition) }}
                </div>
              </div>
              
              <div class="product-info">
                <div class="product-brand">{{ getBrandName(product.title) }}</div>
                <div class="product-name">{{ product.title }}</div>
                
                <div class="product-price-row">
                  <div class="current-price">¥{{ formatPrice(product.price) }}</div>
                  <div class="original-price" v-if="product.original_price && product.original_price > product.price">
                    ¥{{ formatPrice(product.original_price) }}
                  </div>
                </div>
                
                <div class="product-tags" v-if="getProductTags(product).length > 0">
                  <span 
                    v-for="(tag, idx) in getProductTags(product)" 
                    :key="idx"
                    class="product-tag"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="pagination.total > pagination.pageSize">
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

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const products = ref([])
const categories = ref([])
const searchKeyword = ref('')
const activeCategory = ref('全部')
const selectedBrand = ref('')
const activeTab = ref('market')
const showChat = ref(false)

const pagination = ref({
  current: 1,
  pageSize: 6,
  total: 0
})

const filters = ref({
  condition: '不限',
})

const defaultImage = 'https://via.placeholder.com/300x300?text=No+Image'

// 设备分类
const deviceCategories = [
  { type: '全部', name: '全部' },
  { type: '手机', name: '手机' },
  { type: '平板', name: '平板' },
  { type: '电脑', name: '电脑' },
  { type: '耳机', name: '耳机' },
  { type: '手表', name: '手表' },
]

// 成色选项
const conditionOptions = [
  { label: '不限', value: '不限', color: 'black' },
  { label: '全新', value: 'new', color: 'green' },
  { label: '99新', value: 'like_new', color: 'blue' },
  { label: '95新', value: 'good', color: 'purple' },
  { label: '9成新', value: 'fair', color: 'orange' },
  { label: '8成新', value: 'poor', color: 'gray' },
]

// 品牌数据
const brandData = {
  全部: [
    { name: 'Apple' },
    { name: 'Samsung' },
    { name: 'Huawei' },
    { name: 'Sony' },
    { name: '小米' },
    { name: 'OPPO' },
    { name: 'vivo' },
    { name: '荣耀' },
  ],
  手机: [
    { name: 'Apple' },
    { name: 'Samsung' },
    { name: 'Huawei' },
    { name: '小米' },
    { name: 'OPPO' },
    { name: 'vivo' },
    { name: '荣耀' },
  ],
  平板: [
    { name: 'Apple' },
    { name: 'Samsung' },
    { name: 'Huawei' },
    { name: '小米' },
  ],
  电脑: [
    { name: 'Apple' },
    { name: '联想' },
    { name: '戴尔' },
    { name: '华硕' },
  ],
  耳机: [
    { name: 'Apple' },
    { name: 'Sony' },
    { name: 'Huawei' },
    { name: '小米' },
  ],
  手表: [
    { name: 'Apple' },
    { name: 'Samsung' },
    { name: 'Huawei' },
  ],
}

const currentBrands = computed(() => {
  return brandData[activeCategory.value] || brandData['全部']
})

// 成色文本映射
const conditionTextMap = {
  'new': '全新',
  'like_new': '99新',
  'good': '95新',
  'fair': '9成新',
  'poor': '8成新',
}

const getConditionText = (condition) => {
  return conditionTextMap[condition] || '99新'
}

const getConditionBadgeClass = (condition) => {
  const classMap = {
    'new': 'badge-green',
    'like_new': 'badge-blue',
    'good': 'badge-purple',
    'fair': 'badge-orange',
    'poor': 'badge-gray',
  }
  return classMap[condition] || 'badge-blue'
}

const getBrandName = (title) => {
  const brands = ['APPLE', 'SAMSUNG', 'HUAWEI', 'SONY', '小米', 'OPPO', 'vivo', '荣耀', '联想', '戴尔', '华硕']
  for (const brand of brands) {
    if (title.toUpperCase().includes(brand.toUpperCase())) {
      return brand.toUpperCase()
    }
  }
  return 'UNKNOWN'
}

const getProductTags = (product) => {
  const tags = []
  const title = product.title || ''
  const desc = product.description || ''
  
  if (/官方|保修|验机/.test(title + desc)) {
    tags.push('官方保修')
  }
  if (/拍照|相机|像素/.test(title + desc)) {
    tags.push('拍照神机')
  }
  if (/生产力|办公|M2|M1|芯片/.test(title + desc)) {
    tags.push('生产力')
  }
  if (/M2|M1/.test(title + desc)) {
    tags.push('M2芯片')
  }
  
  return tags.slice(0, 2)
}

const formatPrice = (price) => {
  return Number(price).toFixed(0)
}

// 选择分类
const selectCategory = (category) => {
  activeCategory.value = category
  selectedBrand.value = ''
  pagination.value.current = 1
  loadProducts()
}

// 选择品牌
const selectBrand = (brand) => {
  selectedBrand.value = brand
  pagination.value.current = 1
  loadProducts()
}

// 选择成色
const selectCondition = (condition) => {
  filters.value.condition = condition
  pagination.value.current = 1
  loadProducts()
}

// 搜索
const handleSearch = () => {
  pagination.value.current = 1
  loadProducts()
}

// 清空筛选
const clearAllFilters = () => {
  activeCategory.value = '全部'
  selectedBrand.value = ''
  filters.value.condition = '不限'
  searchKeyword.value = ''
  pagination.value.current = 1
  loadProducts()
}

// 加载分类
const loadCategories = async () => {
  try {
    const res = await api.get('/categories/')
    categories.value = res.data.results || res.data || []
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

// 加载商品
const loadProducts = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize,
      status: 'active',
    }

    // 分类筛选
    if (activeCategory.value !== '全部' && categories.value.length > 0) {
      const categoryMapping = {
        '手机': '手机数码',
        '平板': '平板/笔记本',
        '电脑': '电脑办公',
        '手表': '智能穿戴',
        '耳机': '耳机音响',
      }
      const categoryName = categoryMapping[activeCategory.value] || activeCategory.value
      const matchedCategory = categories.value.find(cat => cat.name === categoryName)
      if (matchedCategory) {
        params.category = matchedCategory.id
      }
    }

    // 品牌筛选
    if (selectedBrand.value) {
      params.search = selectedBrand.value
    }

    // 成色筛选
    if (filters.value.condition && filters.value.condition !== '不限') {
      params.condition = filters.value.condition
    }

    // 搜索关键词
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }

    // 排序
    params.ordering = '-created_at'

    const res = await api.get('/verified-products/', { params })
    
    if (res.data.results) {
      products.value = res.data.results
      pagination.value.total = res.data.count || 0
    } else if (Array.isArray(res.data)) {
      products.value = res.data
      pagination.value.total = res.data.length
    } else {
      products.value = []
      pagination.value.total = 0
    }

  } catch (error) {
    console.error('加载商品失败:', error)
    ElMessage.error('加载商品失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

// 分页
const handlePageChange = (page) => {
  pagination.value.current = page
  loadProducts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 跳转详情
const goToDetail = (id) => {
  router.push(`/verified-products/${id}`)
}

// 跳转个人中心
const goToProfile = () => {
  if (!authStore.user) {
    router.push('/login')
  } else {
    router.push('/verified-profile')
  }
}

// 图片处理
const handleImageError = (e) => {
  e.target.src = defaultImage
}

onMounted(() => {
  loadCategories()
  loadProducts()
})
</script>

<style scoped>
.verified-products-page {
  min-height: 100vh;
  background: #f5f5f5;
  position: relative;
}

/* 主容器 */
.main-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

/* 左侧筛选栏 */
.filter-sidebar {
  width: 240px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  position: sticky;
  top: 100px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  height: fit-content;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.filter-icon {
  font-size: 18px;
}

.filter-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.filter-section {
  margin-bottom: 32px;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 12px;
}

/* 分类网格 */
.category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.category-btn {
  padding: 10px 16px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.category-btn:hover {
  background: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
}

.category-btn.active {
  background: #1890ff;
  border-color: #1890ff;
  color: #fff;
  font-weight: 600;
}

/* 品牌列表 */
.brand-list {
  max-height: 300px;
  overflow-y: auto;
  padding-right: 4px;
}

.brand-list::-webkit-scrollbar {
  width: 4px;
}

.brand-list::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 2px;
}

.brand-list::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 2px;
}

.brand-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  cursor: pointer;
  transition: all 0.2s;
}

.brand-item:hover {
  color: #1890ff;
}

.brand-item.active {
  color: #1890ff;
}

.radio-btn {
  width: 18px;
  height: 18px;
  border: 2px solid #d9d9d9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.radio-btn.checked {
  border-color: #1890ff;
  background: #1890ff;
}

.radio-dot {
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
}

.brand-label {
  font-size: 14px;
  color: #333;
}

.brand-item.active .brand-label {
  color: #1890ff;
  font-weight: 500;
}

/* 成色网格 */
.condition-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.condition-btn {
  padding: 10px 16px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.condition-btn:hover {
  background: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
}

.condition-btn.active {
  border-color: #333;
  color: #fff;
  font-weight: 600;
}

.condition-btn.active.black {
  background: #333;
  border-color: #333;
}

.condition-btn.active.green {
  background: #52c41a;
  border-color: #52c41a;
}

.condition-btn.active.blue {
  background: #1890ff;
  border-color: #1890ff;
}

.condition-btn.active.purple {
  background: #722ed1;
  border-color: #722ed1;
}

.condition-btn.active.orange {
  background: #fa8c16;
  border-color: #fa8c16;
}

.condition-btn.active.gray {
  background: #8c8c8c;
  border-color: #8c8c8c;
}

/* 右侧商品区域 */
.products-area {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 顶部标签 */
.top-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.tab-item {
  padding: 8px 20px;
  font-size: 15px;
  color: #666;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.tab-item:hover {
  color: #1890ff;
  background: #f0f9ff;
}

.tab-item.active {
  color: #1890ff;
  font-weight: 600;
  background: #e6f7ff;
}

/* 商品列表头部 */
.products-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.products-title {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.products-count {
  font-size: 14px;
  color: #999;
}

.header-right {
  display: flex;
  align-items: center;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  transition: all 0.2s;
}

.search-box:focus-within {
  background: #fff;
  border-color: #1890ff;
}

.search-icon {
  font-size: 16px;
  color: #999;
}

.search-input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: #333;
  width: 200px;
}

.search-input::placeholder {
  color: #999;
}

/* 商品容器 */
.products-container {
  min-height: 400px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f0f0f0;
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 16px;
  color: #999;
  font-size: 14px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 16px;
  color: #666;
  margin-bottom: 24px;
}

.empty-btn {
  padding: 10px 24px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.empty-btn:hover {
  background: #40a9ff;
  transform: translateY(-2px);
}

/* 商品网格 */
.products-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.product-card {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.product-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.15);
  transform: translateY(-4px);
}

.product-image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 100%;
  background: #f5f5f5;
  overflow: hidden;
}

.product-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s;
}

.product-card:hover .product-image {
  transform: scale(1.05);
}

.condition-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  z-index: 2;
}

.badge-green {
  background: #52c41a;
}

.badge-blue {
  background: #1890ff;
}

.badge-purple {
  background: #722ed1;
}

.badge-orange {
  background: #fa8c16;
}

.badge-gray {
  background: #8c8c8c;
}

.product-info {
  padding: 16px;
}

.product-brand {
  font-size: 12px;
  color: #999;
  margin-bottom: 6px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.product-name {
  font-size: 15px;
  color: #333;
  font-weight: 600;
  margin-bottom: 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 42px;
}

.product-price-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 12px;
}

.current-price {
  font-size: 20px;
  font-weight: 700;
  color: #ff4d4f;
}

.original-price {
  font-size: 14px;
  color: #999;
  text-decoration: line-through;
}

.product-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.product-tag {
  padding: 4px 10px;
  background: #f0f9ff;
  color: #1890ff;
  border: 1px solid #bae7ff;
  border-radius: 4px;
  font-size: 12px;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}


/* 响应式 */
@media (max-width: 1200px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
  }
  
  .filter-sidebar {
    width: 100%;
    position: static;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .products-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-box {
    width: 100%;
  }
  
  .search-input {
    width: 100%;
  }
}
</style>
