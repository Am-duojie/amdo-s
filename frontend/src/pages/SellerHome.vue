<template>
  <div class="seller-home">
    <AppPageHeader title="卖家主页" :subtitle="sellerDisplayName" />
    <section class="seller-hero">
      <div class="seller-hero-card">
        <div class="seller-main">
          <el-avatar :size="56" :src="sellerAvatar" class="seller-avatar">
            {{ sellerInitial }}
          </el-avatar>
          <div class="seller-text">
            <div class="seller-name-row">
              <h1 class="seller-name">{{ sellerDisplayName }}</h1>
              <span v-if="sellerLocation" class="seller-location">{{ sellerLocation }}</span>
            </div>
            <p v-if="sellerBio" class="seller-bio">{{ sellerBio }}</p>
            <div v-if="sellerJoinText" class="seller-meta">{{ sellerJoinText }}</div>
          </div>
        </div>
        <div class="seller-stats">
          <div class="stat-box">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">宝贝</div>
          </div>
          <div class="stat-box">
            <div class="stat-value">{{ stats.active }}</div>
            <div class="stat-label">在售</div>
          </div>
          <div class="stat-box">
            <div class="stat-value">{{ stats.sold }}</div>
            <div class="stat-label">已售</div>
          </div>
        </div>
      </div>
    </section>

    <section class="seller-products">
      <div class="seller-toolbar">
        <div class="seller-tabs">
          <button
            class="tab-btn"
            :class="{ active: statusFilter === 'all' }"
            @click="setStatus('all')"
          >
            全部
          </button>
          <button
            class="tab-btn"
            :class="{ active: statusFilter === 'active' }"
            @click="setStatus('active')"
          >
            在售
          </button>
          <button
            class="tab-btn"
            :class="{ active: statusFilter === 'sold' }"
            @click="setStatus('sold')"
          >
            已售
          </button>
        </div>
        <div class="seller-sort">
          <el-select v-model="sortBy" size="small" placeholder="排序">
            <el-option label="最新发布" value="-created_at" />
            <el-option label="价格从低到高" value="price" />
            <el-option label="价格从高到低" value="-price" />
            <el-option label="最多浏览" value="-view_count" />
          </el-select>
        </div>
      </div>

      <div class="products-panel" v-loading="loading">
        <el-empty
          v-if="!loading && products.length === 0"
          description="暂无商品"
          :image-size="120"
        />
        <div v-else class="goods-list">
          <div
            v-for="product in products"
            :key="product.id"
            class="goods-card"
            :class="{ sold: product.status === 'sold' }"
            @click="router.push(`/products/${product.id}`)"
          >
            <div class="goods-img-box">
              <img
                :src="productImage(product)"
                loading="lazy"
                :alt="product.title"
                @error="(e) => (e.target.src = placeholderImage)"
              />
              <div v-if="product.status === 'sold'" class="sold-overlay">
                <span>卖掉了</span>
              </div>
            </div>
            <div class="goods-info">
              <div class="goods-title">{{ product.title }}</div>
              <div class="goods-price-row">
                <div class="price">
                  <span class="symbol">¥</span>
                  <span class="num">{{ formatPriceInt(product.price) }}</span>
                  <span class="decimal">{{ formatPriceDecimal(product.price) }}</span>
                </div>
                <div class="want-num">{{ product.view_count || 0 }}次浏览</div>
              </div>
              <div class="goods-footer">
                <span class="goods-tag" :class="product.status">{{ statusText(product.status) }}</span>
                <span class="goods-time">{{ formatDate(product.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

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
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AppPageHeader from '@/components/AppPageHeader.vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import { getResults, getCount } from '@/utils/responseGuard'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const sellerId = computed(() => String(route.params.id || ''))
const sellerInfo = ref(null)

const products = ref([])
const loading = ref(false)
const statusFilter = ref('all')
const sortBy = ref('-created_at')
const pagination = ref({
  current: 1,
  pageSize: 20,
  total: 0
})

const stats = ref({
  total: 0,
  active: 0,
  sold: 0
})

const placeholderImage = 'https://via.placeholder.com/400x220?text=No+Image'

const sellerDisplayName = computed(() => {
  return sellerInfo.value?.username || products.value[0]?.seller?.username || `卖家${sellerId.value}`
})

const sellerAvatar = computed(() => {
  return sellerInfo.value?.avatar || products.value[0]?.seller?.avatar || ''
})

const sellerLocation = computed(() => {
  return sellerInfo.value?.location || products.value[0]?.seller?.location || ''
})

const sellerBio = computed(() => {
  return sellerInfo.value?.bio || products.value[0]?.seller?.bio || ''
})

const sellerInitial = computed(() => sellerDisplayName.value?.charAt(0)?.toUpperCase() || '卖')

const sellerJoinText = computed(() => {
  const joined = sellerInfo.value?.date_joined || products.value[0]?.seller?.date_joined
  if (!joined) return ''
  return `加入 ${formatDate(joined)}`
})

const productImage = (product) => {
  if (product.images && product.images.length > 0) {
    return getImageUrl(product.images[0].image)
  }
  return placeholderImage
}

const statusText = (status) => {
  if (status === 'sold') return '已售'
  if (status === 'active') return '在售'
  if (status === 'removed') return '下架'
  if (status === 'pending') return '待审'
  return '未知'
}

const formatPriceInt = (price) => Math.floor(price).toLocaleString()
const formatPriceDecimal = (price) => {
  const decimal = price.toString().split('.')[1]
  return decimal ? `.${decimal}` : ''
}

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const setStatus = (status) => {
  if (statusFilter.value === status) return
  statusFilter.value = status
}

const handlePageChange = (page) => {
  pagination.value.current = page
  loadProducts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const loadSeller = async () => {
  if (!authStore.user) return
  try {
    const res = await api.get(`/users/${sellerId.value}/`)
    sellerInfo.value = res.data
  } catch (error) {
    // silent fallback to product data
  }
}

const loadStats = async () => {
  try {
    const activeRes = await api.get('/products/', {
      params: { seller: sellerId.value, status: 'active', page_size: 1 }
    })
    const soldRes = await api.get('/products/', {
      params: { seller: sellerId.value, status: 'sold', page_size: 1 }
    })
    const activeCount = getCount(activeRes.data)
    const soldCount = getCount(soldRes.data)
    stats.value = {
      active: activeCount,
      sold: soldCount,
      total: activeCount + soldCount
    }
  } catch (error) {
    stats.value = { total: 0, active: 0, sold: 0 }
  }
}

const loadProducts = async () => {
  if (!sellerId.value) return
  loading.value = true
  try {
    const params = {
      seller: sellerId.value,
      status: statusFilter.value,
      page: pagination.value.current,
      page_size: pagination.value.pageSize
    }
    if (sortBy.value) {
      params.ordering = sortBy.value
    }
    const res = await api.get('/products/', { params })
    products.value = getResults(res.data)
    pagination.value.total = getCount(res.data)

    if (!sellerInfo.value && products.value.length > 0) {
      sellerInfo.value = products.value[0].seller
    }
  } catch (error) {
    products.value = []
    pagination.value.total = 0
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProducts()
  loadStats()
  loadSeller()
})

watch(sellerId, () => {
  pagination.value.current = 1
  loadProducts()
  loadStats()
  loadSeller()
})

watch([statusFilter, sortBy], () => {
  pagination.value.current = 1
  loadProducts()
})
</script>

<style scoped>
.seller-home {
  min-height: 100vh;
  background: var(--bg-page);
  padding: 20px 20px 48px;
  box-sizing: border-box;
}

.seller-hero {
  max-width: 1200px;
  margin: 0 auto 20px;
}

.seller-hero-card {
  background: linear-gradient(135deg, #fff4db, #fffef9);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.seller-main {
  display: flex;
  gap: 12px;
  align-items: center;
}

.seller-avatar {
  border: 2px solid #fff;
  box-shadow: 0 4px 12px rgba(255, 136, 51, 0.2);
}

.seller-text {
  flex: 1;
}

.seller-name-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.seller-name {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.seller-location {
  font-size: 12px;
  color: #6b7280;
  background: #fff;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid #f0e6d2;
}

.seller-bio {
  margin: 6px 0 0;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.5;
}

.seller-meta {
  margin-top: 6px;
  font-size: 11px;
  color: #9ca3af;
}

.seller-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.stat-box {
  background: #fff;
  border-radius: 12px;
  padding: 10px 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #ff6a00;
}

.stat-label {
  font-size: 11px;
  color: #6b7280;
  margin-top: 2px;
}

.seller-products {
  max-width: 1200px;
  margin: 0 auto;
}

.seller-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 4px 16px;
}

.seller-tabs {
  display: flex;
  gap: 10px;
}

.tab-btn {
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #4b5563;
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  border-color: #ff6a00;
  color: #ff6a00;
}

.tab-btn.active {
  background: #ff6a00;
  color: #fff;
  border-color: #ff6a00;
  box-shadow: 0 6px 12px rgba(255, 106, 0, 0.2);
}

.products-panel {
  background: #fff;
  border-radius: 18px;
  padding: 20px;
  box-shadow: var(--shadow-md);
  min-height: 480px;
}

.goods-list {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.goods-card {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid transparent;
}

.goods-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: #ffe3c6;
}

.goods-card.sold {
  opacity: 0.85;
}

.goods-img-box {
  width: 100%;
  aspect-ratio: 1;
  background: #f3f4f6;
  position: relative;
  overflow: hidden;
}

.goods-img-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.goods-card:hover .goods-img-box img {
  transform: scale(1.05);
}

.sold-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #fff;
  font-weight: 700;
  letter-spacing: 2px;
}

.goods-info {
  padding: 14px;
}

.goods-title {
  font-size: 14px;
  color: #1f2937;
  line-height: 1.4;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 10px;
}

.goods-price-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 10px;
}

.goods-price-row .price {
  color: #ff6a00;
  font-weight: 700;
}

.goods-price-row .price .symbol {
  font-size: 12px;
}

.goods-price-row .price .num {
  font-size: 20px;
}

.goods-price-row .price .decimal {
  font-size: 12px;
}

.goods-price-row .want-num {
  font-size: 11px;
  color: #9ca3af;
}

.goods-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  color: #9ca3af;
}

.goods-tag {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  background: #f3f4f6;
  color: #6b7280;
}

.goods-tag.active {
  background: #fff7e6;
  color: #ff6a00;
}

.goods-tag.sold {
  background: #fdf2f2;
  color: #ef4444;
}

.goods-tag.removed {
  background: #f3f4f6;
  color: #9ca3af;
}

.pagination-wrapper {
  text-align: center;
  padding: 28px 0 8px;
}

@media (max-width: 1200px) {
  .goods-list {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .seller-hero-card {
    padding: 14px 16px;
  }

  .seller-main {
    flex-direction: column;
    align-items: flex-start;
  }

  .seller-stats {
    grid-template-columns: repeat(3, 1fr);
  }

  .goods-list {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .seller-home {
    padding: 12px 12px 36px;
  }

  .seller-toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .seller-tabs {
    flex-wrap: wrap;
  }

  .products-panel {
    padding: 16px;
  }

  .goods-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }
}
</style>
