<template>
  <div class="verified-product-detail-page">
    <PageHeader :theme="'blue'" :verifiedMode="true" />
    
    <div class="container" v-loading="loading">
      <!-- 面包屑导航 -->
      <div class="breadcrumb">
        <span class="breadcrumb-item" @click="goBack">官方验货</span>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-item active">商品详情</span>
      </div>

      <div v-if="product" class="product-detail-content">
        <!-- 商品图片和基本信息 -->
        <div class="product-main-section">
          <!-- 左侧图片区域 -->
          <div class="product-images">
            <div class="main-image">
              <img 
                :src="currentImageUrl" 
                :alt="product.title"
                @error="handleImageError"
              />
              <div class="verified-badge">✓ 官方验机</div>
            </div>
            <div class="thumbnail-list" v-if="product.images && product.images.length > 1">
              <div 
                v-for="(img, index) in product.images" 
                :key="index"
                class="thumbnail-item"
                :class="{ active: currentImageIndex === index }"
                @click="currentImageIndex = index"
              >
                <img :src="getImageUrl(img.image)" :alt="`${product.title} ${index + 1}`" />
              </div>
            </div>
          </div>

          <!-- 右侧商品信息 -->
          <div class="product-info-section">
            <div class="product-header">
              <div class="product-title">{{ product.title }}</div>
              <div class="product-subtitle" v-if="product.brand || product.model">
                {{ [product.brand, product.model].filter(Boolean).join(' ') }}
              </div>
            </div>

            <!-- 价格区域 -->
            <div class="price-section">
              <div class="current-price">¥{{ formatPrice(product.price) }}</div>
              <div class="original-price" v-if="product.original_price && product.original_price > product.price">
                原价：¥{{ formatPrice(product.original_price) }}
              </div>
            </div>

            <!-- 商品标签 -->
            <div class="product-tags">
              <span class="tag verified-tag">✓ 官方验机</span>
              <span class="tag condition-tag" :class="getConditionClass(product.condition)">
                {{ getConditionText(product.condition) }}
              </span>
              <span class="tag" v-if="product.storage">{{ product.storage }}</span>
            </div>

            <!-- 商品规格 -->
            <div class="product-specs" v-if="hasSpecs">
              <div class="spec-item" v-if="product.brand">
                <span class="spec-label">品牌：</span>
                <span class="spec-value">{{ product.brand }}</span>
              </div>
              <div class="spec-item" v-if="product.model">
                <span class="spec-label">型号：</span>
                <span class="spec-value">{{ product.model }}</span>
              </div>
              <div class="spec-item" v-if="product.storage">
                <span class="spec-label">存储：</span>
                <span class="spec-value">{{ product.storage }}</span>
              </div>
              <div class="spec-item" v-if="product.screen_size">
                <span class="spec-label">屏幕：</span>
                <span class="spec-value">{{ product.screen_size }}</span>
              </div>
              <div class="spec-item" v-if="product.battery_health">
                <span class="spec-label">电池：</span>
                <span class="spec-value">{{ product.battery_health }}</span>
              </div>
              <div class="spec-item" v-if="product.charging_type">
                <span class="spec-label">充电：</span>
                <span class="spec-value">{{ product.charging_type }}</span>
              </div>
            </div>

            <!-- 统计信息 -->
            <div class="stats-row">
              <span class="stat">{{ product.view_count || 0 }} 浏览</span>
              <span class="stat-divider">|</span>
              <span class="stat">{{ product.sales_count || 0 }} 已售</span>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button 
                class="action-btn favorite-btn"
                size="large"
                @click="handleFavorite"
                :disabled="!authStore.user"
              >
                <el-icon>
                  <StarFilled v-if="product.is_favorited" />
                  <Star v-else />
                </el-icon>
                {{ product.is_favorited ? '已收藏' : '收藏' }}
              </el-button>
              
              <el-button
                v-if="product.status === 'active'"
                class="action-btn buy-btn"
                type="warning"
                size="large"
                @click="handleBuy"
                :disabled="!authStore.user || (authStore.user && authStore.user.id === product.seller?.id)"
              >
                立即购买
              </el-button>
              <el-button v-else class="action-btn disabled-btn" size="large" disabled>
                {{ product.status === 'sold' ? '已售出' : '已下架' }}
              </el-button>
            </div>

            <!-- 保障信息 -->
            <div class="guarantee-info">
              <div class="guarantee-item">
                <el-icon><CircleCheck /></el-icon>
                <span>官方验机，品质保证</span>
              </div>
              <div class="guarantee-item">
                <el-icon><CircleCheck /></el-icon>
                <span>7天无理由退货</span>
              </div>
              <div class="guarantee-item">
                <el-icon><CircleCheck /></el-icon>
                <span>全国包邮</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 商品详情和质检报告 -->
        <div class="product-detail-section">
          <el-tabs v-model="activeTab" class="detail-tabs">
            <el-tab-pane label="商品详情" name="detail">
              <div class="detail-content">
                <div class="detail-text" v-html="formatDescription(product.description)"></div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="质检报告" name="report">
              <div class="report-content">
                <div class="report-header">
                  <h3>官方验机报告</h3>
                  <span class="report-time" v-if="product.verified_at">
                    验机时间：{{ formatDate(product.verified_at) }}
                  </span>
                </div>
                <div class="report-items">
                  <div class="report-item" v-if="product.condition">
                    <span class="report-label">成色等级：</span>
                    <span class="report-value">{{ getConditionText(product.condition) }}</span>
                  </div>
                  <div class="report-item" v-if="product.battery_health">
                    <span class="report-label">电池健康：</span>
                    <span class="report-value">{{ product.battery_health }}</span>
                  </div>
                  <div class="report-item" v-if="product.screen_size">
                    <span class="report-label">屏幕尺寸：</span>
                    <span class="report-value">{{ product.screen_size }}</span>
                  </div>
                  <div class="report-item" v-if="product.storage">
                    <span class="report-label">存储容量：</span>
                    <span class="report-value">{{ product.storage }}</span>
                  </div>
                  <div class="report-item" v-if="product.charging_type">
                    <span class="report-label">充电方式：</span>
                    <span class="report-value">{{ product.charging_type }}</span>
                  </div>
                  <div class="report-item">
                    <span class="report-label">验机状态：</span>
                    <span class="report-value verified">✓ 已通过官方验机</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <!-- 购买对话框 -->
    <el-dialog v-model="showOrderDialog" title="确认购买" width="480px" @close="resetOrderForm">
      <div v-if="product" class="order-product-preview">
        <div class="preview-image">
          <img v-if="product.images?.length" :src="getImageUrl(product.images[0].image)" />
        </div>
        <div class="preview-info">
          <div class="preview-title">{{ product.title }}</div>
          <div class="preview-price">¥{{ product.price }}</div>
        </div>
      </div>
      
      <el-divider />
      
      <el-form :model="orderForm" label-width="90px">
        <el-form-item label="收货人" required>
          <el-input v-model="orderForm.shipping_name" placeholder="请输入收货人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" required>
          <el-input v-model="orderForm.shipping_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="收货地址" required>
          <el-input v-model="orderForm.shipping_address" type="textarea" :rows="2" placeholder="请输入详细收货地址" />
        </el-form-item>
        <el-form-item label="留言">
          <el-input v-model="orderForm.note" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showOrderDialog = false">取消</el-button>
        <el-button type="warning" @click="handleOrderSubmit" :loading="orderLoading">
          确认购买 ¥{{ product?.price }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Star, StarFilled, CircleCheck } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import { getImageUrl } from '@/utils/image'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const product = ref(null)
const loading = ref(true)
const currentImageIndex = ref(0)
const activeTab = ref('detail')
const showOrderDialog = ref(false)
const orderLoading = ref(false)
const orderForm = ref({
  shipping_name: '',
  shipping_phone: '',
  shipping_address: '',
  note: ''
})

const defaultImage = 'https://via.placeholder.com/400x400?text=No+Image'

const currentImageUrl = computed(() => {
  if (product.value?.images && product.value.images.length > 0) {
    return getImageUrl(product.value.images[currentImageIndex.value].image)
  }
  return defaultImage
})

const hasSpecs = computed(() => {
  return !!(product.value?.brand || product.value?.model || product.value?.storage || 
           product.value?.screen_size || product.value?.battery_health || product.value?.charging_type)
})

const getConditionText = (condition) => {
  const map = {
    'new': '全新',
    'like_new': '99成新',
    'good': '95成新',
  }
  return map[condition] || '未知'
}

const getConditionClass = (condition) => {
  const classMap = {
    'new': 'condition-new',
    'like_new': 'condition-like-new',
    'good': 'condition-good',
  }
  return classMap[condition] || ''
}

const formatPrice = (price) => {
  return Number(price).toFixed(0)
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const formatDescription = (desc) => {
  if (!desc) return ''
  // 将换行符转换为 <br>
  return desc.replace(/\n/g, '<br>')
}

const handleImageError = (e) => {
  e.target.src = defaultImage
}

const goBack = () => {
  router.push('/verified-products')
}

const loadProduct = async () => {
  try {
    const res = await api.get(`/verified-products/${route.params.id}/`)
    product.value = res.data
  } catch (error) {
    ElMessage.error('商品加载失败')
    router.push('/verified-products')
  } finally {
    loading.value = false
  }
}

const handleFavorite = async () => {
  if (!authStore.user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  try {
    if (product.value.is_favorited) {
      await api.delete(`/verified-favorites/${product.value.id}/`)
      ElMessage.success('已取消收藏')
    } else {
      await api.post('/verified-favorites/', { product_id: product.value.id })
      ElMessage.success('已收藏')
    }
    loadProduct()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleBuy = () => {
  if (!authStore.user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  if (authStore.user.id === product.value.seller.id) {
    ElMessage.warning('不能购买自己的商品')
    return
  }
  if (product.value.status !== 'active') {
    ElMessage.warning('商品已下架或已售出')
    return
  }
  showOrderDialog.value = true
}

const resetOrderForm = () => {
  orderForm.value = {
    shipping_name: '',
    shipping_phone: '',
    shipping_address: '',
    note: ''
  }
}

const handleOrderSubmit = async () => {
  if (!orderForm.value.shipping_name || !orderForm.value.shipping_phone || !orderForm.value.shipping_address) {
    ElMessage.warning('请填写完整的收货信息')
    return
  }
  
  orderLoading.value = true
  try {
    const res = await api.post('/verified-orders/', {
      product_id: product.value.id,
      shipping_name: orderForm.value.shipping_name,
      shipping_phone: orderForm.value.shipping_phone,
      shipping_address: orderForm.value.shipping_address,
      note: orderForm.value.note
    })
    ElMessage.success('订单创建成功')
    showOrderDialog.value = false
    router.push(`/verified-order/${res.data.id}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建订单失败')
  } finally {
    orderLoading.value = false
  }
}

onMounted(() => {
  loadProduct()
})
</script>

<style scoped>
.verified-product-detail-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.breadcrumb {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.breadcrumb-item {
  cursor: pointer;
  transition: color 0.2s;
}

.breadcrumb-item:hover {
  color: #1890ff;
}

.breadcrumb-item.active {
  color: #333;
  cursor: default;
}

.breadcrumb-separator {
  color: #ccc;
}

.product-detail-content {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.product-main-section {
  display: grid;
  grid-template-columns: 500px 1fr;
  gap: 40px;
  margin-bottom: 40px;
  padding-bottom: 40px;
  border-bottom: 1px solid #f0f0f0;
}

.product-images {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.main-image {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  background: #f5f5f5;
  border-radius: 12px;
  overflow: hidden;
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.verified-badge {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 6px 12px;
  background: #1890ff;
  color: #fff;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.thumbnail-list {
  display: flex;
  gap: 12px;
  overflow-x: auto;
}

.thumbnail-item {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  flex-shrink: 0;
}

.thumbnail-item:hover {
  border-color: #1890ff;
}

.thumbnail-item.active {
  border-color: #1890ff;
}

.thumbnail-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-header {
  margin-bottom: 8px;
}

.product-title {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.product-subtitle {
  font-size: 16px;
  color: #666;
}

.price-section {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin: 20px 0;
}

.current-price {
  font-size: 32px;
  font-weight: 700;
  color: #ff4d4f;
}

.original-price {
  font-size: 16px;
  color: #999;
  text-decoration: line-through;
}

.product-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.verified-tag {
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #bae7ff;
}

.condition-tag {
  background: #f0f0f0;
  color: #666;
}

.condition-tag.condition-new {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.condition-tag.condition-like-new {
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #bae7ff;
}

.condition-tag.condition-good {
  background: #f9f0ff;
  color: #722ed1;
  border: 1px solid #d3adf7;
}

.product-specs {
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.spec-item {
  display: flex;
  align-items: center;
}

.spec-label {
  color: #666;
  font-size: 14px;
  margin-right: 8px;
}

.spec-value {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.stats-row {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #999;
  font-size: 14px;
}

.stat-divider {
  color: #e0e0e0;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.action-btn {
  flex: 1;
}

.buy-btn {
  background: #ff4d4f;
  border-color: #ff4d4f;
}

.buy-btn:hover {
  background: #ff7875;
  border-color: #ff7875;
}

.guarantee-info {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.guarantee-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.guarantee-item .el-icon {
  color: #52c41a;
}

.product-detail-section {
  margin-top: 40px;
}

.detail-tabs {
  margin-top: 20px;
}

.detail-content {
  padding: 24px;
  min-height: 200px;
}

.detail-text {
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
}

.report-content {
  padding: 24px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.report-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.report-time {
  font-size: 14px;
  color: #999;
}

.report-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.report-label {
  font-size: 14px;
  color: #666;
  margin-right: 12px;
  min-width: 100px;
}

.report-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.report-value.verified {
  color: #52c41a;
  font-weight: 600;
}

.order-product-preview {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.preview-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-info {
  flex: 1;
}

.preview-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.preview-price {
  font-size: 18px;
  font-weight: 700;
  color: #ff4d4f;
}

@media (max-width: 768px) {
  .product-main-section {
    grid-template-columns: 1fr;
  }
  
  .product-specs {
    grid-template-columns: 1fr;
  }
}
</style>

