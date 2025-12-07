<template>
  <div class="checkout-page">
    
    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <template v-else-if="product">
      <div class="checkout-container">
        <!-- 左侧主体 -->
        <div class="checkout-main">
          <!-- 收货地址 -->
          <div class="section address-section">
            <div class="section-header">
              <h2 class="section-title">收货地址</h2>
              <span class="manage-link" @click="router.push('/profile?tab=address')">
                管理地址
              </span>
            </div>
            
            <div class="delivery-type">
              <el-icon class="check-icon"><CircleCheckFilled /></el-icon>
              <span>快递邮寄</span>
            </div>

            <div class="address-list" v-if="addresses.length > 0">
              <div 
                v-for="(addr, index) in addresses" 
                :key="addr.id"
                class="address-card"
                :class="{ active: selectedAddressId === addr.id }"
                @click="selectedAddressId = addr.id"
              >
                <div class="address-radio">
                  <el-icon v-if="selectedAddressId === addr.id" class="radio-checked"><Select /></el-icon>
                  <span v-else class="radio-unchecked"></span>
                </div>
                <div class="address-content">
                  <div class="address-region">{{ addr.province }} {{ addr.city }} {{ addr.district }}</div>
                  <div class="address-detail">{{ addr.detail_address }}</div>
                  <div class="address-contact">
                    <span class="contact-name">{{ addr.name }}</span>
                    <span class="contact-phone">{{ addr.phone }}</span>
                    <el-tag v-if="addr.is_default" size="small" type="danger" effect="plain">默认</el-tag>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="no-address" @click="router.push('/profile?tab=address')">
              <el-icon><Plus /></el-icon>
              <span>添加收货地址</span>
            </div>
          </div>

          <!-- 订单信息 -->
          <div class="section order-section">
            <h2 class="section-title">订单信息</h2>
            
            <div class="order-product">
              <div class="product-image">
                <img v-if="product.images?.length" :src="getImageUrl(product.images[0].image)" />
                <el-icon v-else><PictureFilled /></el-icon>
              </div>
              <div class="product-info">
                <div class="product-title">{{ product.title }}</div>
                <div class="product-price">¥{{ product.price }}</div>
              </div>
            </div>

            <div class="quantity-row">
              <span class="quantity-label">购买数量</span>
              <div class="quantity-control">
                <el-button :icon="Minus" size="small" :disabled="quantity <= 1" @click="quantity--" />
                <span class="quantity-value">{{ quantity }}</span>
                <el-button :icon="Plus" size="small" :disabled="quantity >= 1" @click="quantity++" />
              </div>
            </div>

            <div class="note-row">
              <span class="note-label">买家留言</span>
              <el-input 
                v-model="orderNote" 
                placeholder="选填：可填写特殊要求"
                :maxlength="200"
                show-word-limit
              />
            </div>
          </div>
        </div>

        <!-- 右侧价格明细 -->
        <div class="checkout-sidebar">
          <div class="price-card">
            <h3 class="price-title">价格明细</h3>
            
            <div class="price-row">
              <span class="price-label">商品总价</span>
              <span class="price-value">共{{ quantity }}件宝贝</span>
              <span class="price-amount">¥{{ product.price }}</span>
            </div>
            
            <div class="price-row">
              <span class="price-label">运费</span>
              <span class="price-value"></span>
              <span class="price-amount free">¥0.00</span>
            </div>
            
            <el-divider />
            
            <div class="total-row">
              <span class="total-label">合计：</span>
              <span class="total-amount">¥{{ totalPrice }}</span>
            </div>
            
            <el-button 
              type="warning" 
              size="large" 
              class="submit-btn"
              :loading="submitting"
              :disabled="addresses.length === 0"
              @click="handleSubmit"
            >
              确认购买
            </el-button>
          </div>
        </div>
      </div>
    </template>

    <!-- 支付对话框 -->
    <el-dialog
      v-model="paymentDialogVisible"
      title="选择支付方式"
      width="460px"
      :close-on-click-modal="false"
      class="payment-dialog"
      :append-to-body="true"
    >
      <div class="payment-options">
        <div 
          class="payment-option"
          :class="{ active: paymentType === 'alipay' }"
        >
          <div class="option-icon alipay">💰</div>
          <span class="option-name">支付宝</span>
        </div>
      </div>
      
      <div class="payment-amount">
        <span>支付金额</span>
        <span class="amount">¥{{ totalPrice }}</span>
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
          type="warning" 
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CircleCheckFilled, Select, Plus, Minus, PictureFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import { getImageUrl } from '@/utils/image'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const product = ref(null)
const quantity = ref(1)
const orderNote = ref('')
const submitting = ref(false)

// 地址相关
const addresses = ref([])
const selectedAddressId = ref(null)

// 支付相关
const paymentDialogVisible = ref(false)
const paymentType = ref('alipay')
const paymentLoading = ref(false)
const qrcodeUrl = ref('')
const checkingPayment = ref(false)
const currentOrderId = ref(null)
let paymentCheckTimer = null

const totalPrice = computed(() => {
  return (parseFloat(product.value?.price || 0) * quantity.value).toFixed(2)
})

onMounted(async () => {
  // 检查登录状态
  if (!authStore.user) {
    await authStore.init()
  }
  
  if (!authStore.user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  // 加载商品信息
  await loadProduct()
  
  // 加载保存的地址
  await loadAddresses()
})

onBeforeUnmount(() => {
  if (paymentCheckTimer) {
    clearInterval(paymentCheckTimer)
  }
})

const loadProduct = async () => {
  try {
    const productId = route.params.id
    const res = await api.get(`/products/${productId}/`)
    product.value = res.data
    
    // 检查商品状态
    if (product.value.status !== 'active') {
      ElMessage.warning('商品已下架或已售出')
      router.push(`/products/${productId}`)
      return
    }
    
    // 检查是否是自己的商品
    if (authStore.user?.id === product.value.seller?.id) {
      ElMessage.warning('不能购买自己的商品')
      router.push(`/products/${productId}`)
      return
    }
  } catch (error) {
    ElMessage.error('商品加载失败')
    router.push('/products')
  } finally {
    loading.value = false
  }
}

const loadAddresses = async () => {
  try {
    const res = await api.get('/addresses/')
    addresses.value = res.data?.results || res.data || []
    
    // 默认选中默认地址或第一个地址
    if (addresses.value.length > 0) {
      const defaultAddr = addresses.value.find(addr => addr.is_default)
      selectedAddressId.value = defaultAddr ? defaultAddr.id : addresses.value[0].id
    }
  } catch (error) {
    console.error('加载地址失败:', error)
    ElMessage.error('加载收货地址失败')
  }
}

const handleSubmit = async () => {
  if (!selectedAddressId.value) {
    ElMessage.warning('请选择收货地址')
    return
  }
  
  const selectedAddr = addresses.value.find(addr => addr.id === selectedAddressId.value)
  if (!selectedAddr) return

  submitting.value = true
  try {
    // 格式化地址字符串
    const fullAddress = `${selectedAddr.province} ${selectedAddr.city} ${selectedAddr.district} ${selectedAddr.detail_address}`
    
    // 创建订单
    const orderData = {
      product_id: product.value.id,
      shipping_name: selectedAddr.name,
      shipping_phone: selectedAddr.phone,
      shipping_address: fullAddress,
      note: orderNote.value
    }
    
    const res = await api.post('/orders/', orderData)
    currentOrderId.value = res.data.id
    
    // 打开支付弹窗
    paymentDialogVisible.value = true
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '订单创建失败')
  } finally {
    submitting.value = false
  }
}

const createPayment = async () => {
  paymentLoading.value = true
  try {
    const res = await api.post('/payment/create/', {
      order_id: currentOrderId.value,
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
        startPaymentCheck()
        ElMessage.success('支付二维码已生成')
      } else {
        ElMessage.error('支付创建失败：未返回支付信息')
      }
    } else {
      ElMessage.error(res.data.error || '支付创建失败')
    }
  } catch (error) {
    console.error('创建支付错误:', error)
    ElMessage.error(error.response?.data?.error || '支付创建失败')
  } finally {
    paymentLoading.value = false
  }
}

const startPaymentCheck = () => {
  if (paymentCheckTimer) clearInterval(paymentCheckTimer)
  
  paymentCheckTimer = setInterval(checkPaymentStatus, 3000)
}

const checkPaymentStatus = async () => {
  if (!currentOrderId.value) return
  
  checkingPayment.value = true
  try {
    const res = await api.get(`/payment/query/${currentOrderId.value}/?order_type=normal`)
    if (res.data.success && res.data.paid) {
      clearInterval(paymentCheckTimer)
      ElMessage.success('支付成功')
      paymentDialogVisible.value = false
      router.push('/profile?tab=bought')
    }
  } catch (error) {
    console.error('查询支付状态失败:', error)
  } finally {
    checkingPayment.value = false
  }
}


const closePaymentDialog = () => {
  ElMessageBox.confirm('确定要取消支付吗？订单已创建，您可以稍后在订单列表中继续支付。', '取消支付', {
    confirmButtonText: '确定离开',
    cancelButtonText: '继续支付',
    type: 'warning'
  }).then(() => {
    paymentDialogVisible.value = false
    if (paymentCheckTimer) clearInterval(paymentCheckTimer)
    router.push('/profile?tab=bought')
  }).catch(() => {})
}
</script>

<style scoped>
.checkout-page {
  background: #f5f5f5;
  min-height: 100vh;
}

.loading-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
}

.checkout-container {
  max-width: 1200px;
  margin: 20px auto;
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.checkout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.manage-link {
  color: #409eff;
  cursor: pointer;
  font-size: 14px;
}

/* 地址部分 */
.delivery-type {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #ff6a00;
  font-weight: 500;
}

.address-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.address-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
  display: flex;
  gap: 12px;
}

.address-card:hover {
  border-color: #ff6a00;
  background: #fffcf9;
}

.address-card.active {
  border-color: #ff6a00;
  background: #fffcf9;
  box-shadow: 0 0 0 1px #ff6a00 inset;
}

.address-radio {
  padding-top: 2px;
}

.radio-checked {
  color: #ff6a00;
  font-size: 18px;
}

.radio-unchecked {
  display: block;
  width: 16px;
  height: 16px;
  border: 1px solid #ccc;
  border-radius: 50%;
}

.address-content {
  flex: 1;
}

.address-region {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.address-detail {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.address-contact {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 10px;
}

.edit-btn {
  position: absolute;
  top: 10px;
  right: 10px;
}

.no-address {
  border: 1px dashed #ccc;
  border-radius: 8px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #999;
  cursor: pointer;
  transition: all 0.2s;
}

.no-address:hover {
  border-color: #ff6a00;
  color: #ff6a00;
  background: #fffcf9;
}

/* 订单商品 */
.order-product {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.product-image {
  width: 80px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-image .el-icon {
  width: 100%;
  height: 100%;
  font-size: 24px;
  color: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-title {
  font-size: 16px;
  color: #333;
  line-height: 1.4;
}

.product-price {
  font-size: 18px;
  color: #ff2442;
  font-weight: 600;
}

.quantity-row, .note-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.quantity-label, .note-label {
  width: 80px;
  font-size: 14px;
  color: #333;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.quantity-value {
  font-size: 16px;
  font-weight: 500;
  width: 30px;
  text-align: center;
}

/* 侧边栏 */
.checkout-sidebar {
  width: 320px;
  position: sticky;
  top: 20px;
}

.price-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.price-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 20px 0;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
}

.price-amount {
  font-weight: 500;
  color: #333;
}

.price-amount.free {
  color: #52c41a;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin: 20px 0;
}

.total-label {
  font-size: 16px;
  font-weight: 500;
}

.total-amount {
  font-size: 28px;
  color: #ff2442;
  font-weight: 700;
  line-height: 1;
}

.submit-btn {
  width: 100%;
  font-size: 16px;
  font-weight: 600;
  border-radius: 24px;
}

/* 支付弹窗 */
.payment-options {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.payment-option {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-option:hover, .payment-option.active {
  border-color: #ff6a00;
  background: #fffcf9;
  color: #ff6a00;
}

.option-icon {
  font-size: 32px;
}

.payment-amount {
  text-align: center;
  margin-bottom: 20px;
  font-size: 16px;
  color: #666;
}

.payment-amount .amount {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-left: 8px;
}

.qrcode-container {
  text-align: center;
}

.qrcode-img {
  width: 200px;
  height: 200px;
  margin-bottom: 10px;
}

.qrcode-tip {
  color: #666;
  font-size: 14px;
}
</style>
