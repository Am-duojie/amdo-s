<template>
  <div class="payment-return-page">
    <div class="container">
      <el-card class="result-card" v-loading="processing">
        <div v-if="!processing" class="result-content">
          <el-result
            v-if="result === 'success'"
            icon="success"
            title="支付成功"
            sub-title="正在跳转到订单详情..."
          >
            <template #extra>
              <el-button type="primary" @click="goToOrder">立即查看订单</el-button>
            </template>
          </el-result>
          
          <el-result
            v-else-if="result === 'processing'"
            icon="info"
            title="支付处理中"
            sub-title="正在查询支付状态，请稍候..."
          />
          
          <el-result
            v-else-if="result === 'failed'"
            icon="error"
            title="支付失败"
            :sub-title="errorMessage || '支付未成功，请重试'"
          >
            <template #extra>
              <el-button type="primary" @click="goToOrder">查看订单</el-button>
              <el-button @click="goBack">返回</el-button>
            </template>
          </el-result>
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

const route = useRoute()
const router = useRouter()

const processing = ref(true)
const result = ref('processing') // success, failed, processing
const errorMessage = ref('')

const orderId = ref(null)
const orderType = ref('normal')

const handleAuthenticationError = error => {
  const status = error.response?.status
  if ([400, 401, 403].includes(status)) {
    result.value = 'failed'
    errorMessage.value = error.response?.data?.error || '请先登录后在订单中查看支付结果'
    processing.value = false
    return true
  }
  return false
}

const notifyPaymentSuccess = () => {
  if (!orderId.value) return
  const key = `payment_status_${orderId.value}`
  const payload = {
    status: 'paid',
    order_type: orderType.value,
    ts: Date.now()
  }
  localStorage.setItem(key, JSON.stringify(payload))
}

onMounted(() => {
  // 从 URL 参数获取订单信息
  orderId.value = route.query.order_id
  orderType.value = route.query.order_type || 'normal'
  
  if (!orderId.value) {
    result.value = 'failed'
    errorMessage.value = '订单ID缺失'
    processing.value = false
    return
  }
  
  // 检查支付宝返回的参数
  checkPaymentResult()
})

const checkPaymentResult = async () => {
  try {
    // 检查 URL 参数中是否有支付宝返回的参数
    const query = route.query
    const hasAlipayParams = query.out_trade_no || query.trade_status || query.trade_no
    
    // 无论是否有支付宝参数，都查询支付状态
    // 因为后端会主动查询支付宝接口获取最新状态
    await checkPaymentStatus(hasAlipayParams)
  } catch (error) {
    if (handleAuthenticationError(error)) {
      return
    }
    console.error('检查支付结果失败:', error)
    result.value = 'failed'
    errorMessage.value = error.response?.data?.error || '查询支付状态失败'
    processing.value = false
  }
}

const checkPaymentStatus = async (hasAlipayParams = false) => {
  try {
    const res = await api.get(`/payment/query/${orderId.value}/?order_type=${orderType.value}`)
    
    if (res.data.success && res.data.paid) {
      result.value = 'success'
      processing.value = false
      notifyPaymentSuccess()
      ElMessage.success('支付成功！')
      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        goToOrder()
      }, 2000)
    } else {
      // 支付可能还在处理中，进行重试
      result.value = 'processing'
      
      // 如果第一次查询失败，等待后重试（最多重试3次）
      let retryCount = 0
      const maxRetries = 3
      
      const retryCheck = async () => {
        if (retryCount >= maxRetries) {
          result.value = 'failed'
          errorMessage.value = '支付状态查询超时，请稍后查看订单状态'
          processing.value = false
          return
        }
        
        retryCount++
        await new Promise(resolve => setTimeout(resolve, 2000)) // 等待2秒
        
        try {
          const retryRes = await api.get(`/payment/query/${orderId.value}/?order_type=${orderType.value}`)
          if (retryRes.data.success && retryRes.data.paid) {
            result.value = 'success'
            processing.value = false
            notifyPaymentSuccess()
            ElMessage.success('支付成功！')
            setTimeout(() => {
              goToOrder()
            }, 2000)
          } else {
            // 继续重试
            await retryCheck()
          }
        } catch (error) {
          if (handleAuthenticationError(error)) {
            return
          }
          console.error(`第${retryCount}次查询失败:`, error)
          // 继续重试
          await retryCheck()
        }
      }
      
      // 开始重试
      await retryCheck()
    }
  } catch (error) {
    if (handleAuthenticationError(error)) {
      return
    }
    console.error('查询支付状态失败:', error)
    result.value = 'processing'
    errorMessage.value = error.response?.data?.error || '查询支付状态失败，正在重试...'
    
    // 如果查询失败，也进行重试
    setTimeout(async () => {
      try {
        await checkPaymentStatus()
      } catch (retryError) {
        result.value = 'failed'
        errorMessage.value = '查询支付状态失败，请稍后查看订单状态'
        processing.value = false
      }
    }, 3000)
  }
}

const goToOrder = () => {
  processing.value = false
  if (orderType.value === 'verified') {
    router.push(`/verified-order/${orderId.value}`)
  } else {
    router.push(`/order/${orderId.value}`)
  }
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.payment-return-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f9ff 0%, #f5f5f5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.container {
  width: 100%;
  max-width: 600px;
}

.result-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-content {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
