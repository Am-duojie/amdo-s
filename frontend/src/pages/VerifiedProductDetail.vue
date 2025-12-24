<template>
  <div class="verified-detail-page xianyu-style">
    <div v-if="loading" class="loading">
      <el-skeleton :rows="8" animated />
    </div>

    <div v-else-if="error" class="error">
      <el-empty description="加载失败">
        <el-button type="primary" @click="loadProduct">重试</el-button>
      </el-empty>
    </div>

    <div v-else-if="product" class="detail-container">
      <div class="seller-header">
        <div class="seller-left">
          <el-avatar :size="48" class="seller-avatar">
            {{ product.seller?.username?.[0] || '官' }}
          </el-avatar>
          <div class="seller-info">
            <div class="seller-name">{{ product.seller?.username || '官方验' }}</div>
            <div class="seller-stats">
              <span class="stat-item">平台专业质检上架</span>
            </div>
          </div>
        </div>
      </div>

      <div class="main-content">
        <div class="image-section">
          <div v-if="images.length > 1" class="thumbnail-list">
            <div
              v-for="(src, index) in images"
              :key="index"
              class="thumbnail-item"
              :class="{ active: currentImage === index }"
              @click="currentImage = index"
              @mouseenter="currentImage = index"
            >
              <img :src="src" :alt="product.title" />
            </div>
          </div>

          <div class="main-image-wrapper">
            <el-image
              v-if="images.length"
              :src="images[currentImage]"
              :preview-src-list="images"
              :initial-index="currentImage"
              fit="contain"
              class="main-image"
            />
            <div v-else class="no-image">
              <el-icon><PictureFilled /></el-icon>
              <p>暂无图片</p>
            </div>
          </div>
        </div>

        <div class="info-section">
          <div class="price-area">
            <div class="price-row">
              <span class="currency">¥</span>
              <span class="price-value">{{ product.price }}</span>
              <span v-if="product.original_price" class="original-price">¥{{ product.original_price }}</span>
              <span class="shipping-tag">包邮</span>
            </div>
            <div class="condition-badge" :class="getConditionClass(product.condition)">
              {{ conditionText }}
            </div>
          </div>

          <div class="stats-row">
            <span class="stat">{{ product.favorite_count || 0 }} 人收藏</span>
            <span class="stat-divider">|</span>
            <span class="stat">{{ product.view_count || 0 }} 浏览</span>
          </div>

          <div class="description-area">
            <div class="product-title">{{ product.title }}</div>
            <div v-if="product.description" class="product-desc-wrapper">
              <div class="product-desc" :class="{ 'is-collapsed': descShouldCollapse && !descExpanded }">
                {{ product.description }}
              </div>
              <div v-if="descShouldCollapse" class="desc-toggle" @click="descExpanded = !descExpanded">
                <span class="desc-toggle-text">{{ descExpanded ? '收起' : '展开' }}</span>
                <el-icon class="desc-toggle-icon" :class="{ expanded: descExpanded }">
                  <ArrowDown />
                </el-icon>
              </div>
            </div>
          </div>

          <div class="action-area">
            <el-button
              class="action-btn buy-btn"
              size="large"
              type="warning"
              @click="handleBuyVerified"
            >
              立即购买
            </el-button>
            <el-button
              class="action-btn favorite-btn"
              size="large"
              @click="toggleVerifiedFavorite"
            >
              <el-icon>
                <StarFilled v-if="product.is_favorited" />
                <Star v-else />
              </el-icon>
              {{ product.is_favorited ? '已收藏' : '收藏' }}
            </el-button>
          </div>

          <div class="main-specs">
            <div class="specs-simple">
              <div v-for="item in specItems" :key="item.key" class="spec-col">
                <span class="label">{{ item.label }}：</span>
                <span class="value">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 验机报告 -->
      <div class="detail-block inspection-block">
        <div class="block-title">验机评估报告</div>
        <InspectionReport :product-id="product.id" />
      </div>

      <!-- 底部详情图：按需求移除，仅保留质检报告 -->
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
 import { PictureFilled, Star, StarFilled, ArrowDown } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import InspectionReport from '@/components/InspectionReport.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const product = ref(null)
const loading = ref(false)
const error = ref(null)
const currentImage = ref(0)
const favoriteId = ref(null)

const conditionMap = {
  new: '全新',
  like_new: '几乎全新',
  good: '成色良好',
  fair: '成色一般',
  poor: '成色较旧'
}

const images = computed(() => {
  if (!product.value) return []
  const arr = product.value.images || []
  return arr.map(img => resolveImageField(img)).filter(Boolean)
})

const conditionText = computed(() => conditionMap[product.value?.condition] || '—')

const descExpanded = ref(false)
const descShouldCollapse = computed(() => {
  const text = (product.value?.description || '').trim()
  if (!text) return false
  const lines = text.split(/\r?\n/).length
  return text.length > 160 || lines > 6
})

const specItems = computed(() => {
  const p = product.value || {}
  const items = []

  if (p.brand) items.push({ key: 'brand', label: '品牌', value: p.brand })
  if (p.model) items.push({ key: 'model', label: '型号', value: p.model })
  if (p.storage) items.push({ key: 'storage', label: '存储容量', value: p.storage })
  if (p.version) items.push({ key: 'version', label: '版本', value: p.version })
  if (p.color) items.push({ key: 'color', label: '颜色', value: p.color })

  items.push({ key: 'condition', label: '成色', value: conditionText.value })

  if (p.ram) items.push({ key: 'ram', label: '运行内存', value: p.ram })
  if (p.repair_status) items.push({ key: 'repair_status', label: '拆修和功能', value: p.repair_status })
  if (p.battery_health) items.push({ key: 'battery_health', label: '电池健康', value: p.battery_health })

  return items
})

const getConditionClass = (condition) => {
  const map = {
    new: 'cond-new',
    like_new: 'cond-like-new',
    good: 'cond-good',
    fair: 'cond-fair',
    poor: 'cond-poor'
  }
  return map[condition] || 'cond-good'
}

function resolveImageField(img) {
  if (!img) return null
  if (typeof img === 'string') return getImageUrl(img)
  if (img.url) return getImageUrl(img.url)
  if (img.image) return getImageUrl(img.image)
  if (img.image_url) return getImageUrl(img.image_url)
  if (img.imageUrl) return getImageUrl(img.imageUrl)
  return null
}

function normalizeProduct(data) {
  const imgs = []
  if (Array.isArray(data.detail_images)) {
    data.detail_images.forEach(img => {
      const val = img?.image || img?.url || img
      if (val) imgs.push({ image: val })
    })
  }
  if (!imgs.length && data.cover_image) imgs.push({ image: data.cover_image })
  if (!imgs.length && Array.isArray(data.images)) {
    data.images.forEach(img => {
      const val = img?.image || img?.url || img
      if (val) imgs.push({ image: val })
    })
  }
  data.images = imgs
  if (!data.seller) data.seller = { username: '官方验' }
  return data
}

async function loadProduct() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(`/verified-products/${route.params.id}/`)
    product.value = normalizeProduct(res.data)
    descExpanded.value = false
    addToVerifiedBrowseHistory(product.value)
    favoriteId.value = null
    if (product.value?.is_favorited) {
      await ensureFavoriteId()
    }
  } catch (err) {
    error.value = err
    ElMessage.error('商品加载失败')
    router.push('/verified-products')
  } finally {
    loading.value = false
  }
}

async function ensureFavoriteId() {
  if (!authStore.user || !product.value?.id) return null
  if (favoriteId.value) return favoriteId.value
  try {
    const res = await api.get('/verified-favorites/', { params: { page: 1, page_size: 100 } })
    const list = res.data?.results || res.data || []
    const hit = (list || []).find((f) => f?.product?.id === product.value.id)
    if (hit?.id) favoriteId.value = hit.id
  } catch {
    // ignore
  }
  return favoriteId.value
}

async function toggleVerifiedFavorite() {
  if (!authStore.user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  if (!product.value) return

  try {
    if (product.value.is_favorited) {
      const id = await ensureFavoriteId()
      if (id) await api.delete(`/verified-favorites/${id}/`)
      product.value.is_favorited = false
      favoriteId.value = null
      product.value.favorite_count = Math.max((product.value.favorite_count || 1) - 1, 0)
      ElMessage.success('已取消收藏')
    } else {
      const res = await api.post('/verified-favorites/', { product_id: product.value.id })
      product.value.is_favorited = true
      favoriteId.value = res.data?.id || favoriteId.value
      product.value.favorite_count = (product.value.favorite_count || 0) + 1
      ElMessage.success('已收藏')
    }
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.response?.data?.product_id || '操作失败'
    ElMessage.error(msg)
  }
}

function handleBuyVerified() {
  if (!authStore.user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  if (authStore.user.id === product.value?.seller?.id) {
    ElMessage.warning('不能购买自己的商品')
    return
  }
  if (product.value?.status !== 'active') {
    ElMessage.warning('商品已下架或已售出')
    return
  }
  router.push(`/checkout/${route.params.id}?order_type=verified`)
}

function addToVerifiedBrowseHistory(p) {
  if (!authStore.user || !p) return
  const historyKey = `browse_history_verified_${authStore.user?.id}`
  const stored = localStorage.getItem(historyKey)
  let list = []
  if (stored) {
    try { list = JSON.parse(stored) || [] } catch { list = [] }
  }

  const historyItem = {
    productId: p.id,
    title: p.title,
    price: p.price,
    image: p.images?.length ? getImageUrl(p.images[0].image) : null,
    timestamp: Date.now()
  }

  list = list.filter(item => item.productId !== p.id)
  list.unshift(historyItem)
  if (list.length > 50) list = list.slice(0, 50)
  localStorage.setItem(historyKey, JSON.stringify(list))
}

onMounted(loadProduct)
</script>

<style scoped>
.verified-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px 48px;
}
.detail-container {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.seller-header {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.seller-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.seller-avatar {
  background: #f2f6fc;
  color: #409eff;
  font-weight: 700;
}

.seller-name {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.seller-stats {
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
}

.main-content {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.image-section {
  display: flex;
  gap: 14px;
  width: 52%;
}

.thumbnail-list {
  width: 78px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 420px;
  overflow-y: auto;
  padding-right: 4px;
}

.thumbnail-item {
  width: 70px;
  height: 70px;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  background: #fafafa;
  flex: 0 0 auto;
}

.thumbnail-item.active {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.15);
}

.thumbnail-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.main-image-wrapper {
  flex: 1;
  border-radius: 12px;
  background: #fafafa;
  overflow: hidden;
  height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-image {
  width: 100%;
  height: 100%;
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  gap: 8px;
}

.info-section {
  flex: 1;
  min-width: 0;
}

.price-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.currency {
  font-size: 18px;
  color: #ff6a00;
  font-weight: 700;
}

.price-value {
  font-size: 30px;
  font-weight: 800;
  color: #ff6a00;
}

.original-price {
  margin-left: 8px;
  color: #c0c4cc;
  text-decoration: line-through;
  font-size: 14px;
}

.shipping-tag {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.condition-badge {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid #e9e9e9;
  background: #f7f7f7;
  color: #606266;
}

.cond-new { background: #ecf5ff; border-color: #d9ecff; color: #409eff; }
.cond-like-new { background: #f0f9eb; border-color: #e1f3d8; color: #67c23a; }
.cond-good { background: #fdf6ec; border-color: #faecd8; color: #e6a23c; }
.cond-fair { background: #f4f4f5; border-color: #e9e9eb; color: #909399; }
.cond-poor { background: #fef0f0; border-color: #fde2e2; color: #f56c6c; }

.stats-row {
  margin-top: 8px;
  color: #c0c4cc;
  font-size: 12px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.stat-divider {
  opacity: 0.6;
}

.description-area {
  margin-top: 14px;
}

.product-title {
  font-size: 18px;
  font-weight: 800;
  color: #303133;
  line-height: 1.4;
}

.product-desc {
  margin-top: 8px;
  color: #606266;
  line-height: 1.7;
  font-size: 14px;
  white-space: pre-wrap;
}

.product-desc.is-collapsed {
  position: relative;
  overflow: hidden;
  max-height: calc(1.7em * 8);
}

.product-desc.is-collapsed::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: calc(1.7em * 1.6);
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0), #fff);
}

.desc-toggle {
  margin-top: 6px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 4px;
  color: #409eff;
  cursor: pointer;
  user-select: none;
  font-size: 14px;
}

.desc-toggle-icon {
  transition: transform 0.18s ease;
}

.desc-toggle-icon.expanded {
  transform: rotate(180deg);
}

.action-area {
  margin-top: 18px;
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
}
/* 主要规格 */
.main-specs {
  margin-top: 14px;
}

.specs-title {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
  margin-bottom: 10px;
}

.specs-simple {
  display: grid;
  grid-template-columns: 1fr 1fr;
  row-gap: 12px;
  column-gap: 40px;
  font-size: 14px;
}

.spec-col {
  display: flex;
  gap: 6px;
  min-width: 0;
}

.spec-col .label {
  color: #909399;
  white-space: nowrap;
}

.spec-col .value {
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .specs-simple {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
.detail-block {
  margin-top: 24px;
}
.block-title {
  font-weight: 600;
  margin-bottom: 12px;
}
.detail-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}
.loading,
.error {
  padding: 40px 0;
}
@media (max-width: 960px) {
  .main-content {
    flex-direction: column;
  }
  .image-section {
    width: 100%;
  }
  .thumbnail-list {
    flex-direction: row;
    width: 100%;
    max-height: none;
    overflow-x: auto;
    overflow-y: hidden;
    padding-right: 0;
  }
  .main-image-wrapper {
    height: 320px;
  }
}

/* 验机报告区块 */
.inspection-block {
  background: var(--bg-page, #f5f7fa);
  padding: 40px 20px;
  border-radius: 16px;
  margin-top: 24px;
}

.inspection-block .block-title {
  text-align: center;
  margin-bottom: 30px;
}
</style>
