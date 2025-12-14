<template>
  <div class="order-detail-page">
    
    <div class="container">
      <el-card class="order-card">
        <template #header>
          <div class="card-header">
            <span class="header-title">订单详情</span>
            <el-button @click="$router.go(-1)">返回</el-button>
          </div>
        </template>

        <el-loading v-loading="loading">
          <div v-if="order" class="order-content">
            <!-- 订单状态 -->
            <div class="order-status">
              <OrderSteps :order="order" type="trade" />
              <div class="current-status">
                <el-tag :type="getStatusType(order.status)" size="large">
                  {{ getStatusText(order.status) }}
                </el-tag>
              </div>
            </div>

            <!-- 收货信息 -->
            <div class="section">
              <h3>收货信息</h3>
              <div class="shipping-info">
                <div class="info-row">
                  <span class="label">收货人：</span>
                  <span class="value">{{ order.shipping_name }}</span>
                </div>
                <div class="info-row">
                  <span class="label">联系电话：</span>
                  <span class="value">{{ order.shipping_phone }}</span>
                </div>
                <div class="info-row">
                  <span class="label">收货地址：</span>
                  <span class="value">{{ order.shipping_address }}</span>
                </div>
                <div v-if="order.note" class="info-row">
                  <span class="label">备注：</span>
                  <span class="value">{{ order.note }}</span>
                </div>
              </div>
            </div>

            <!-- 物流信息 -->
            <div class="section" v-if="order.status === 'shipped' || order.status === 'completed'">
              <h3>物流信息</h3>
              <div class="shipping-info">
                <div class="info-row" v-if="order.carrier">
                  <span class="label">物流公司：</span>
                  <span class="value">{{ order.carrier }}</span>
                </div>
                <div class="info-row" v-if="order.tracking_number">
                  <span class="label">运单号：</span>
                  <span class="value">{{ order.tracking_number }}</span>
                </div>
                <div class="info-row" v-if="order.shipped_at">
                  <span class="label">发货时间：</span>
                  <span class="value">{{ formatDate(order.shipped_at) }}</span>
                </div>
                <div class="info-row" v-if="order.delivered_at">
                  <span class="label">签收时间：</span>
                  <span class="value">{{ formatDate(order.delivered_at) }}</span>
                </div>
              </div>
            </div>

            <!-- 商品信息 -->
            <div class="section">
              <h3>商品信息</h3>
              <div class="product-info" @click="$router.push(`/products/${order.product.id}`)">
                <img
                  v-if="order.product.images && order.product.images.length > 0"
                  :src="getImageUrl(order.product.images[0].image)"
                  :alt="order.product.title"
                  class="product-img"
                />
                <div v-else class="no-image">
                  <el-icon><PictureFilled /></el-icon>
                </div>
                <div class="product-details">
                  <div class="product-title">{{ order.product.title }}</div>
                  <div class="product-desc">{{ order.product.description }}</div>
                  <div class="product-meta">
                    <span class="product-price">¥{{ order.total_price }}</span>
                    <span class="product-condition">{{ getConditionText(order.product.condition) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 卖家信息 -->
            <div class="section">
              <h3>卖家信息</h3>
              <div class="seller-info">
                <div class="info-row">
                  <span class="label">卖家：</span>
                  <span class="value">{{ order.product.seller.username }}</span>
                </div>
                <div v-if="order.product.contact_phone" class="info-row">
                  <span class="label">联系电话：</span>
                  <span class="value">{{ order.product.contact_phone }}</span>
                </div>
                <div v-if="order.product.contact_wechat" class="info-row">
                  <span class="label">微信：</span>
                  <span class="value">{{ order.product.contact_wechat }}</span>
                </div>
                <div class="info-row">
                  <span class="label">交易地点：</span>
                  <span class="value">{{ order.product.location }}</span>
                </div>
              </div>
            </div>

            <!-- 订单操作 -->
            <div class="order-actions">
              <el-button @click="contactSeller">联系卖家</el-button>
              <!-- 支付按钮 -->
              <el-button
                v-if="isBuyer && order.status === 'pending'"
                type="primary"
                @click="showPaymentDialog"
                :loading="paymentLoading"
              >
                立即支付
              </el-button>
              <el-button
                v-if="isSeller && order.status === 'paid'"
                type="primary"
                @click="showShippingDialog"
              >
                确认发货
              </el-button>
              <el-button
                v-if="isBuyer && order.status === 'shipped'"
                type="success"
                @click="handleStatusUpdate('completed')"
              >
                确认收货
              </el-button>
              <el-button
                v-if="isBuyer && order.status === 'pending'"
                type="danger"
                @click="handleCancelOrder"
              >
                取消订单
              </el-button>
            </div>

            <!-- 结算信息（卖家可见） -->
            <div class="section" v-if="isSeller && order.settlement_status">
              <h3>结算信息</h3>
              <div style="margin-bottom:8px">
                <el-tag :type="order.settlement_status==='settled'?'success':(order.settlement_status==='failed'?'danger':'warning')">
                  {{ order.settlement_status==='settled'?'已结算到账':(order.settlement_status==='failed'?'结算失败':'待结算') }}
                </el-tag>
                <el-tag v-if="order.settlement_method==='TRANSFER'" type="warning" style="margin-left:8px">
                  转账代结算
                </el-tag>
                <el-tag v-else-if="order.settlement_method==='ROYALTY'" type="success" style="margin-left:8px">
                  分账结算
                </el-tag>
                <el-tag v-else-if="order.settlement_status==='pending'" type="info" style="margin-left:8px">
                  待分账
                </el-tag>
                <el-tag v-else-if="order.settlement_status==='failed'" type="danger" style="margin-left:8px">
                  分账失败
                </el-tag>
              </div>
              <div class="info-row">
                <span class="label">到账账户：</span>
                <span class="value">{{ order.settlement_account || order.product?.seller?.profile?.alipay_login_id || '-' }}</span>
              </div>
              <div class="info-row" v-if="order.transfer_order_id">
                <span class="label">转账订单号：</span>
                <span class="value">{{ order.transfer_order_id }}</span>
              </div>
              <div class="info-row">
                <span class="label">分账金额：</span>
                <span class="value">¥{{ order.seller_settle_amount ?? '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">平台佣金：</span>
                <span class="value">¥{{ order.platform_commission_amount ?? '-' }}</span>
              </div>
            </div>
          </div>
        </el-loading>
      </el-card>
      
      <!-- 支付对话框 -->
      <el-dialog
        v-model="paymentDialogVisible"
        title="选择支付方式"
        width="500px"
        @close="closePaymentDialog"
      >
        <div class="payment-options">
          <div 
            class="payment-option"
            :class="{ active: paymentType === 'alipay' }"
          >
            <div class="option-icon">💰</div>
            <div class="option-name">支付宝</div>
          </div>
        </div>
        
        <div class="payment-amount">
          支付金额：<span class="amount">¥{{ order?.total_price }}</span>
        </div>
        
      <el-alert 
        title="点击确认支付后将跳转到支付宝支付页面" 
        type="info" 
        :closable="false"
        show-icon
        style="margin-top: 12px;"
      />
      
      <template #footer>
        <el-button @click="closePaymentDialog">取消</el-button>
        <el-button 
          type="primary" 
          @click="createPayment"
          :loading="paymentLoading"
        >
          确认支付
        </el-button>
        <el-button 
          type="success" 
          @click="checkPaymentStatus"
          :loading="checkingPayment"
        >
          我已支付完成
        </el-button>
      </template>
    </el-dialog>

    <!-- 发货对话框 -->
    <el-dialog
      v-model="shippingDialogVisible"
      title="填写物流信息"
      width="500px"
      @close="closeShippingDialog"
    >
      <el-form :model="shippingForm" label-width="100px">
        <el-form-item label="物流公司" required>
          <el-input v-model="shippingForm.carrier" placeholder="请输入物流公司名称，如：顺丰、圆通、中通等" />
        </el-form-item>
        <el-form-item label="运单号" required>
          <el-input v-model="shippingForm.tracking_number" placeholder="请输入运单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeShippingDialog">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmShipping"
          :loading="shippingLoading"
        >
          确认发货
        </el-button>
      </template>
    </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { PictureFilled } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import OrderSteps from '@/components/OrderSteps.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const orderId = computed(() => route.params.id)
const order = ref(null)
const loading = ref(false)

// 支付相关状态
const paymentDialogVisible = ref(false)
const paymentType = ref('alipay')  // 仅支持支付宝支付
const paymentLoading = ref(false)
const qrcodeUrl = ref('')
const checkingPayment = ref(false)
let paymentCheckTimer = null

// 发货相关状态
const shippingDialogVisible = ref(false)
const shippingLoading = ref(false)
const shippingForm = ref({
  carrier: '',
  tracking_number: ''
})

const isBuyer = computed(() => {
  return order.value && authStore.user?.id === order.value.buyer?.id
})

const isSeller = computed(() => {
  return order.value && authStore.user?.id === order.value.product?.seller?.id
})

onMounted(() => {
  if (orderId.value) {
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
        const res = await api.get(`/payment/query/${orderId.value}/?order_type=normal`)
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

const loadOrder = async () => {
  loading.value = true
  try {
    const res = await api.get(`/orders/${orderId.value}/`)
    order.value = res.data
  } catch (error) {
    ElMessage.error('加载订单详情失败')
    router.go(-1)
  } finally {
    loading.value = false
  }
}

const handleStatusUpdate = async (newStatus) => {
  try {
    const confirmText = {
      'paid': '确认已付款？',
      'shipped': '确认已发货？',
      'completed': '确认已收货？'
    }[newStatus]

    await ElMessageBox.confirm(confirmText, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await api.patch(`/orders/${orderId.value}/update_status/`, { status: newStatus })
    ElMessage.success('订单状态更新成功')
    await loadOrder()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('更新失败')
    }
  }
}

// 显示发货对话框
const showShippingDialog = () => {
  shippingForm.value = {
    carrier: order.value?.carrier || '',
    tracking_number: order.value?.tracking_number || ''
  }
  shippingDialogVisible.value = true
}

// 关闭发货对话框
const closeShippingDialog = () => {
  shippingDialogVisible.value = false
  shippingForm.value = {
    carrier: '',
    tracking_number: ''
  }
}

// 确认发货
const confirmShipping = async () => {
  if (!shippingForm.value.carrier || !shippingForm.value.tracking_number) {
    ElMessage.warning('请填写完整的物流信息')
    return
  }

  shippingLoading.value = true
  try {
    await api.patch(`/orders/${orderId.value}/update_status/`, {
      status: 'shipped',
      carrier: shippingForm.value.carrier,
      tracking_number: shippingForm.value.tracking_number
    })
    ElMessage.success('发货成功')
    closeShippingDialog()
    await loadOrder()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发货失败')
  } finally {
    shippingLoading.value = false
  }
}

const handleCancelOrder = async () => {
  try {
    await ElMessageBox.confirm('确定要取消此订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await api.patch(`/orders/${orderId.value}/update_status/`, { status: 'cancelled' })
    ElMessage.success('订单已取消')
    router.push('/profile?tab=bought')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

const contactSeller = () => {
  if (order.value?.product?.seller) {
    router.push(`/messages?user_id=${order.value.product.seller.id}&product_id=${order.value.product.id}`)
  }
}

// 显示支付对话框
const showPaymentDialog = () => {
  paymentDialogVisible.value = true
  paymentType.value = 'alipay'
  qrcodeUrl.value = ''
}

// 关闭支付对话框
const closePaymentDialog = () => {
  paymentDialogVisible.value = false
  qrcodeUrl.value = ''
  if (paymentCheckTimer) {
    clearInterval(paymentCheckTimer)
    paymentCheckTimer = null
  }
}

// 创建支付订单
const createPayment = async () => {
  paymentLoading.value = true
  try {
    const res = await api.post('/payment/create/', {
      order_id: orderId.value,
      order_type: 'normal'  // normal: 易淘订单, verified: 官方验订单
    })
    
    if (res.data.success) {
      // 优先使用表单提交方式（更可靠）
      if (res.data.form_html) {
        // 创建新窗口并写入表单HTML，自动提交
        const newWindow = window.open('', '_blank')
        if (newWindow) {
          newWindow.document.write(res.data.form_html)
          newWindow.document.close()
        } else {
          // 如果弹窗被阻止，使用当前窗口
          document.write(res.data.form_html)
          document.close()
        }
        return
      }
      
      // 备用方案：如果返回支付URL（支付宝），直接跳转
      if (res.data.payment_url) {
        // 尝试在新窗口打开
        const newWindow = window.open(res.data.payment_url, '_blank')
        if (!newWindow) {
          // 如果弹窗被阻止，使用当前窗口
          window.location.href = res.data.payment_url
        }
        return
      }
      
      // 如果返回二维码（易支付），显示二维码
      if (res.data.qrcode) {
        qrcodeUrl.value = res.data.qrcode
        ElMessage.success('支付二维码已生成，请扫码支付')
        // 开始定时检查支付状态
        startPaymentCheck()
      } else {
        ElMessage.error('支付创建失败：未返回支付信息')
      }
    } else {
      ElMessage.error(res.data.error || '创建支付失败')
    }
  } catch (error) {
    console.error('创建支付错误:', error)
    ElMessage.error(error.response?.data?.error || '创建支付失败')
  } finally {
    paymentLoading.value = false
  }
}

// 开始定时检查支付状态
const startPaymentCheck = () => {
  // 每3秒检查一次支付状态
  paymentCheckTimer = setInterval(async () => {
    await checkPaymentStatus(true)
  }, 3000)
}

// 检查支付状态
const checkPaymentStatus = async (isAutoCheck = false) => {
  if (!isAutoCheck) {
    checkingPayment.value = true
  }
  
  try {
    const res = await api.get(`/payment/query/${orderId.value}/?order_type=normal`)
    
    if (res.data.success && res.data.paid) {
      // 支付成功
      ElMessage.success('支付成功！')
      closePaymentDialog()
      await loadOrder()  // 重新加载订单信息
    } else if (!isAutoCheck) {
      ElMessage.warning('尚未检测到支付，请完成支付后再试')
    }
  } catch (error) {
    if (!isAutoCheck) {
      console.error('查询支付状态错误:', error)
      ElMessage.error('查询支付状态失败')
    }
  } finally {
    checkingPayment.value = false
  }
}


const getStepIndex = (status) => {
  const stepMap = {
    'pending': 0,
    'paid': 1,
    'shipped': 2,
    'completed': 3,
    'cancelled': 0
  }
  return stepMap[status] || 0
}

const getStepTime = (step) => {
  // 这里简化处理，实际应该记录每个步骤的时间
  return order.value?.updated_at ? formatDate(order.value.updated_at) : ''
}

const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    paid: 'info',
    shipped: '',
    completed: 'success',
    cancelled: 'info',
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待付款',
    paid: '已付款',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消',
  }
  return map[status] || status
}

const getConditionText = (condition) => {
  const map = {
    new: '全新',
    like_new: '几乎全新',
    good: '良好',
    fair: '一般',
    poor: '较差'
  }
  return map[condition] || condition
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 清理定时器
onBeforeUnmount(() => {
  if (paymentCheckTimer) {
    clearInterval(paymentCheckTimer)
  }
})
</script>

<style scoped>
.order-detail-page {
  background: #f5f7f9;
  min-height: 100vh;
  padding: 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 20px;
}

.order-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.order-content {
  padding: 20px 0;
}

.order-status {
  margin-bottom: 40px;
}

.current-status {
  text-align: center;
  margin-top: 20px;
}

.section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.section:last-child {
  border-bottom: none;
  margin-bottom: 20px;
}

.section h3 {
  margin-bottom: 16px;
  color: #333;
  font-size: 16px;
  font-weight: bold;
}

.info-row {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.label {
  color: #666;
  width: 100px;
  flex-shrink: 0;
}

.value {
  color: #333;
  flex: 1;
}

.product-info {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.product-info:hover {
  background: #f5f5f5;
}

.product-img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
}

.no-image {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 8px;
  color: #ccc;
}

.product-details {
  flex: 1;
}

.product-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.product-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-price {
  font-size: 20px;
  font-weight: bold;
  color: #ff6a00;
}

.product-condition {
  background: #e8f4fd;
  color: #1890ff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.order-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

/* 支付对话框样式 */
.payment-options {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.payment-option {
  flex: 1;
  padding: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.payment-option:hover {
  border-color: #ff6a00;
  background: #fff8f0;
}

.payment-option.active {
  border-color: #ff6a00;
  background: #fff8f0;
}

.option-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.option-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.payment-amount {
  text-align: center;
  font-size: 16px;
  margin-bottom: 20px;
}

.payment-amount .amount {
  font-size: 24px;
  font-weight: bold;
  color: #ff6a00;
  margin-left: 8px;
}

.qrcode-container {
  text-align: center;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-top: 20px;
}

.qrcode-img {
  width: 200px;
  height: 200px;
  margin: 0 auto;
}

.qrcode-tip {
  margin-top: 16px;
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .container {
    padding: 20px 10px;
  }
  
  .product-info {
    flex-direction: column;
  }
  
  .product-img,
  .no-image {
    width: 80px;
    height: 80px;
  }
  
  .order-actions {
    flex-direction: column;
  }
}
</style>
