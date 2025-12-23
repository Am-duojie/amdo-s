<template>
  <div class="verified-order-detail-page">
    
    
    <div class="container">
      <div class="breadcrumb">
        <span class="breadcrumb-item" @click="goBack">官方验货</span>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-item" @click="goToProfile">我的官方验</span>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-item active">订单详情</span>
      </div>

      <el-card class="order-card" v-loading="loading">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <span class="header-title">验货订单详情</span>
              <span class="order-id">订单号：{{ order?.id }}</span>
            </div>
            <el-button @click="goBack">返回</el-button>
          </div>
        </template>

        <div v-if="order" class="order-content">
          <!-- 订单状态 -->
          <div class="order-status-section">
            <div class="status-header">
              <h3 class="section-title">订单状态</h3>
              <el-tag :type="getStatusType(order.status)" size="large">
                {{ getStatusText(order.status) }}
              </el-tag>
            </div>
            <OrderSteps :order="order" type="verified" />
          </div>

          <!-- 商品信息 -->
          <div class="product-section">
            <h3 class="section-title">商品信息</h3>
            <div class="product-card">
              <img 
                :src="order.product?.images?.length ? getImageUrl(order.product.images[0].image) : defaultImage"
                class="product-image"
              />
              <div class="product-details">
                <div class="product-title">{{ order.product?.title }}</div>
                <div class="product-tags">
                  <span class="tag verified-tag">✓ 官方验机</span>
                  <span class="tag condition-tag">{{ getConditionText(order.product?.condition) }}</span>
                </div>
                <div class="product-price-row">
                  <span class="price-label">商品价格：</span>
                  <span class="price-value">¥{{ order.product?.price }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 收货信息 -->
          <div class="shipping-section">
            <h3 class="section-title">收货信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">收货人：</span>
                <span class="info-value">{{ order.shipping_name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">联系电话：</span>
                <span class="info-value">{{ order.shipping_phone }}</span>
              </div>
              <div class="info-item full-width">
                <span class="info-label">收货地址：</span>
                <span class="info-value">{{ order.shipping_address }}</span>
              </div>
              <div class="info-item full-width" v-if="order.note">
                <span class="info-label">订单备注：</span>
                <span class="info-value">{{ order.note }}</span>
              </div>
            </div>
          </div>

          <!-- 订单信息 -->
          <div class="order-info-section">
            <h3 class="section-title">订单信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">订单编号：</span>
                <span class="info-value">{{ order.id }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">下单时间：</span>
                <span class="info-value">{{ formatDate(order.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">商品数量：</span>
                <span class="info-value">1</span>
              </div>
              <div class="info-item">
                <span class="info-label">订单总额：</span>
                <span class="info-value price">¥{{ order.total_price }}</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-section">
            <el-button v-if="order.status === 'pending'" type="warning" size="large" @click="handlePay">
              立即付款
            </el-button>
            <el-button v-if="order.status === 'shipped'" type="success" size="large" @click="handleConfirmReceive">
              确认收货
            </el-button>
            <el-button size="large" plain @click="goToProfile">
              返回订单列表
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import OrderSteps from '@/components/OrderSteps.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const order = ref(null)
const defaultImage = 'https://via.placeholder.com/200x200?text=No+Image'

const getStatusText = (status) => {
  const map = {
    'pending': '待付款',
    'paid': '待发货',
    'shipped': '待收货',
    'completed': '已完成',
    'cancelled': '已取消',
  }
  return map[status] || status
}

const getStatusType = (status) => {
  const map = {
    'pending': 'warning',
    'paid': 'info',
    'shipped': 'primary',
    'completed': 'success',
    'cancelled': 'danger',
  }
  return map[status] || ''
}

const getStepIndex = (status) => {
  const map = {
    'pending': 0,
    'paid': 1,
    'shipped': 2,
    'completed': 3,
    'cancelled': -1,
  }
  return map[status] || 0
}

const getStepTime = (step) => {
  if (!order.value) return ''
  const statusMap = {
    'paid': 'paid_at',
    'shipped': 'shipped_at',
    'completed': 'completed_at',
  }
  const timeField = statusMap[step]
  return timeField && order.value[timeField] ? formatDate(order.value[timeField]) : ''
}

const getConditionText = (condition) => {
  const map = {
    'new': '全新',
    'like_new': '99成新',
    'good': '95成新',
    'fair': '9成新',
    'poor': '8成新',
  }
  return map[condition] || '未知'
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const loadOrder = async () => {
  loading.value = true
  try {
    // 使用官方验货订单API
    const res = await api.get(`/verified-orders/${route.params.id}/`)
    order.value = res.data
  } catch (error) {
    ElMessage.error('加载订单失败')
    console.error(error)
    router.push('/profile?zone=verified&tab=verified-orders')
  } finally {
    loading.value = false
  }
}

const handlePay = () => {
  router.push(`/checkout/${order.value.id}`)
}

const handleConfirmReceive = async () => {
  try {
    await api.patch(`/verified-orders/${order.value.id}/`, { status: 'completed' })
    ElMessage.success('确认收货成功')
    await loadOrder()
  } catch (error) {
    ElMessage.error('确认收货失败')
  }
}

const goBack = () => {
  router.go(-1)
}

const goToProfile = () => {
  router.push('/profile?zone=verified&tab=verified-orders')
}

onMounted(() => {
  if (route.params.id) {
    loadOrder()
    // 检查是否是支付返回页面（支付宝支付成功后会通过 return_url 跳转回来）
    checkPaymentReturn()
  }
})

// 检查支付返回参数
const checkPaymentReturn = async () => {
  const query = route.query
  // 支付宝支付成功后会返回 out_trade_no 和 trade_status 等参数
  if (query.out_trade_no || query.trade_status) {
    // 延迟一下，确保订单数据已加载
    setTimeout(async () => {
      try {
        // 查询支付状态
        const res = await api.get(`/payment/query/${route.params.id}/?order_type=verified`)
        if (res.data.success && res.data.paid) {
          ElMessage.success('支付成功！')
          // 重新加载订单信息
          await loadOrder()
          // 清除 URL 参数，避免刷新时重复处理
          router.replace({ path: route.path, query: {} })
        } else if (query.trade_status) {
          // 如果支付宝返回了状态但查询未成功，可能是异步通知还未处理
          ElMessage.info('支付处理中，请稍候...')
          // 重新加载订单信息
          await loadOrder()
        }
      } catch (error) {
        console.error('检查支付状态失败:', error)
        // 即使查询失败，也重新加载订单（可能异步通知已处理）
        await loadOrder()
      }
    }, 500)
  }
}
</script>

<style scoped>
.verified-order-detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f9ff 0%, #f5f5f5 100%);
  padding-bottom: 40px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 14px;
}

.breadcrumb-item {
  color: #1890ff;
  cursor: pointer;
  transition: color 0.2s;
}

.breadcrumb-item:hover {
  color: #40a9ff;
}

.breadcrumb-item.active {
  color: #666;
  cursor: default;
}

.breadcrumb-separator {
  color: #999;
}

.order-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.order-id {
  font-size: 14px;
  color: #999;
}

.order-content {
  padding: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

/* 订单状态 */
.order-status-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid #f0f0f0;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

/* 商品信息 */
.product-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid #f0f0f0;
}

.product-card {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.product-image {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
}

.product-details {
  flex: 1;
}

.product-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.product-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tag {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.verified-tag {
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #bae7ff;
}

.condition-tag {
  background: #f5f5f5;
  color: #666;
}

.product-price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.price-label {
  font-size: 14px;
  color: #666;
}

.price-value {
  font-size: 24px;
  font-weight: 700;
  color: #ff4d4f;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  gap: 8px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 14px;
  color: #666;
  min-width: 100px;
}

.info-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.info-value.price {
  color: #ff4d4f;
  font-weight: 700;
  font-size: 18px;
}

.shipping-section,
.order-info-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid #f0f0f0;
}

.order-info-section {
  border-bottom: none;
}

/* 操作按钮 */
.action-section {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 768px) {
  .product-card {
    flex-direction: column;
  }
  
  .product-image {
    width: 100%;
    height: auto;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .action-section {
    flex-direction: column;
  }
}
</style>
