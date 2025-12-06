<template>
  <div class="recycle-order-detail">
    <div class="page-header">
      <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
      <h1 class="page-title">回收订单详情</h1>
    </div>

    <div v-loading="loading" class="detail-container">
      <div v-if="order" class="detail-content">
        <!-- 订单基本信息 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>订单信息</span>
              <el-tag :type="getStatusType(order.status)" size="large">
                {{ getStatusText(order.status) }}
              </el-tag>
            </div>
          </template>
          <div class="order-info-grid">
            <div class="info-item">
              <span class="label">订单号：</span>
              <span class="value">#{{ order.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">创建时间：</span>
              <span class="value">{{ formatDate(order.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="label">设备类型：</span>
              <span class="value">{{ order.device_type }}</span>
            </div>
            <div class="info-item">
              <span class="label">品牌型号：</span>
              <span class="value">{{ order.brand }} {{ order.model }}</span>
            </div>
            <div class="info-item" v-if="order.storage">
              <span class="label">存储容量：</span>
              <span class="value">{{ order.storage }}</span>
            </div>
            <div class="info-item">
              <span class="label">成色：</span>
              <span class="value">{{ getConditionText(order.condition) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 价格信息 -->
        <el-card class="info-card" v-if="order.estimated_price || order.final_price">
          <template #header>
            <span>价格信息</span>
          </template>
          <div class="price-info">
            <div class="price-item" v-if="order.estimated_price">
              <span class="label">预估价格：</span>
              <span class="value estimated">¥{{ order.estimated_price }}</span>
            </div>
            <div class="price-item" v-if="order.bonus > 0">
              <span class="label">活动加价：</span>
              <span class="value bonus">+¥{{ order.bonus }}</span>
            </div>
            <div class="price-item" v-if="order.final_price">
              <span class="label">最终价格：</span>
              <span class="value final">¥{{ order.final_price }}</span>
            </div>
            <div class="price-item total" v-if="order.final_price && order.bonus">
              <span class="label">实付金额：</span>
              <span class="value total">¥{{ (parseFloat(order.final_price) + parseFloat(order.bonus || 0)).toFixed(2) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 流程进度 -->
        <el-card class="info-card">
          <template #header>
            <span>订单进度</span>
          </template>
          <el-steps :active="getStepActive()" finish-status="success" align-center>
            <el-step title="提交订单" :description="formatDate(order.created_at)"></el-step>
            <el-step title="已估价" :description="order.estimated_price ? '¥' + order.estimated_price : '待估价'"></el-step>
            <el-step title="已确认" :description="order.status === 'confirmed' ? '已确认估价' : '待确认'"></el-step>
            <el-step title="已寄出" :description="order.shipped_at ? formatDate(order.shipped_at) : '待寄出'"></el-step>
            <el-step title="已检测" :description="order.inspected_at ? formatDate(order.inspected_at) : '待检测'"></el-step>
            <el-step title="已完成" :description="order.status === 'completed' ? '订单完成' : '待完成'"></el-step>
          </el-steps>
        </el-card>

        <!-- 联系信息 -->
        <el-card class="info-card" v-if="order.contact_name || order.contact_phone || order.address">
          <template #header>
            <span>联系信息</span>
          </template>
          <div class="contact-info">
            <div class="info-item" v-if="order.contact_name">
              <span class="label">联系人：</span>
              <span class="value">{{ order.contact_name }}</span>
            </div>
            <div class="info-item" v-if="order.contact_phone">
              <span class="label">联系电话：</span>
              <span class="value">{{ order.contact_phone }}</span>
            </div>
            <div class="info-item" v-if="order.address">
              <span class="label">收货地址：</span>
              <span class="value">{{ order.address }}</span>
            </div>
          </div>
        </el-card>

        <!-- 物流信息 -->
        <el-card class="info-card" v-if="order.shipping_carrier || order.tracking_number">
          <template #header>
            <span>物流信息</span>
          </template>
          <div class="logistics-info">
            <div class="info-item" v-if="order.shipping_carrier">
              <span class="label">物流公司：</span>
              <span class="value">{{ order.shipping_carrier }}</span>
            </div>
            <div class="info-item" v-if="order.tracking_number">
              <span class="label">运单号：</span>
              <span class="value">{{ order.tracking_number }}</span>
            </div>
            <div class="info-item" v-if="order.shipped_at">
              <span class="label">寄出时间：</span>
              <span class="value">{{ formatDate(order.shipped_at) }}</span>
            </div>
            <div class="info-item" v-if="order.received_at">
              <span class="label">收到时间：</span>
              <span class="value">{{ formatDate(order.received_at) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 质检报告 -->
        <el-card class="info-card" v-if="inspectionReport">
          <template #header>
            <span>质检报告</span>
          </template>
          <div class="inspection-report">
            <div class="report-time" v-if="inspectionReport.created_at">
              <span class="label">质检时间：</span>
              <span class="value">{{ formatDate(inspectionReport.created_at) }}</span>
            </div>
            <div class="report-items" v-if="inspectionReport.check_items">
              <div 
                v-for="(value, key) in inspectionReport.check_items" 
                :key="key"
                class="check-item"
              >
                <span class="check-label">{{ getCheckItemLabel(key) }}：</span>
                <el-tag :type="value === 'pass' || value === true ? 'success' : 'danger'" size="small">
                  {{ getCheckItemValue(value) }}
                </el-tag>
              </div>
            </div>
            <div class="report-remarks" v-if="inspectionReport.remarks">
              <span class="label">质检备注：</span>
              <p class="value">{{ inspectionReport.remarks }}</p>
            </div>
          </div>
        </el-card>

        <!-- 打款信息 -->
        <el-card class="info-card" v-if="order.payment_status !== 'pending' || order.paid_at">
          <template #header>
            <span>打款信息</span>
          </template>
          <div class="payment-info">
            <div class="info-item">
              <span class="label">打款状态：</span>
              <el-tag :type="order.payment_status === 'paid' ? 'success' : 'danger'">
                {{ getPaymentStatusText(order.payment_status) }}
              </el-tag>
            </div>
            <div class="info-item" v-if="order.payment_method">
              <span class="label">打款方式：</span>
              <span class="value">{{ order.payment_method }}</span>
            </div>
            <div class="info-item" v-if="order.payment_account">
              <span class="label">打款账户：</span>
              <span class="value">{{ order.payment_account }}</span>
            </div>
            <div class="info-item" v-if="order.paid_at">
              <span class="label">打款时间：</span>
              <span class="value">{{ formatDate(order.paid_at) }}</span>
            </div>
            <div class="info-item" v-if="order.payment_note">
              <span class="label">打款备注：</span>
              <span class="value">{{ order.payment_note }}</span>
            </div>
          </div>
        </el-card>

        <!-- 操作区域 -->
        <el-card class="action-card">
          <div class="action-buttons">
            <!-- 待估价状态：等待管理员估价 -->
            <template v-if="order.status === 'pending'">
              <el-alert type="info" :closable="false">
                订单已提交，等待管理员估价中...
              </el-alert>
            </template>

            <!-- 已估价状态：确认估价或提出异议 -->
            <template v-if="order.status === 'quoted'">
              <el-button type="primary" size="large" @click="showConfirmDialog = true">
                确认估价并填写地址
              </el-button>
              <el-button type="warning" size="large" @click="showDisputeDialog = true">
                对价格有异议
              </el-button>
            </template>

            <!-- 已确认状态：填写物流信息 -->
            <template v-if="order.status === 'confirmed'">
              <el-alert type="info" :closable="false" style="margin-bottom: 16px;">
                订单已确认，请填写物流信息并寄出设备
              </el-alert>
              <el-button type="primary" size="large" @click="showShippingDialog = true">
                填写物流信息
              </el-button>
            </template>

            <!-- 已寄出状态：等待平台检测 -->
            <template v-if="order.status === 'shipped'">
              <el-alert type="info" :closable="false">
                设备已寄出，等待平台收到并检测中...
              </el-alert>
            </template>

            <!-- 已检测状态：确认最终价格或提出异议 -->
            <template v-if="order.status === 'inspected'">
              <el-button type="primary" size="large" @click="confirmFinalPrice">
                确认最终价格
              </el-button>
              <el-button type="warning" size="large" @click="showFinalDisputeDialog = true">
                对最终价格有异议
              </el-button>
            </template>

            <!-- 已完成状态：等待打款 -->
            <template v-if="order.status === 'completed'">
              <el-alert type="success" :closable="false" v-if="order.payment_status === 'paid'">
                订单已完成，打款已完成！
              </el-alert>
              <el-alert type="info" :closable="false" v-else>
                订单已完成，等待平台打款中...
              </el-alert>
            </template>

            <!-- 已取消状态 -->
            <template v-if="order.status === 'cancelled'">
              <el-alert type="warning" :closable="false">
                订单已取消
                <span v-if="order.reject_reason">：{{ order.reject_reason }}</span>
              </el-alert>
            </template>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 确认估价对话框 -->
    <el-dialog v-model="showConfirmDialog" title="确认估价并填写信息" width="600px">
      <el-form :model="confirmForm" label-width="100px">
        <el-divider content-position="left">联系信息</el-divider>
        <el-form-item label="联系人姓名" required>
          <el-input v-model="confirmForm.contact_name" placeholder="请输入联系人姓名"></el-input>
        </el-form-item>
        <el-form-item label="联系电话" required>
          <el-input v-model="confirmForm.contact_phone" placeholder="请输入联系电话"></el-input>
        </el-form-item>
        <el-form-item label="收货地址" required>
          <el-input 
            v-model="confirmForm.address" 
            type="textarea" 
            :rows="3"
            placeholder="请输入详细的收货地址"
          ></el-input>
        </el-form-item>
        
        <el-divider content-position="left">物流信息（可选，也可稍后填写）</el-divider>
        <el-form-item label="物流公司">
          <el-select v-model="confirmForm.shipping_carrier" placeholder="请选择物流公司（可选）" style="width: 100%">
            <el-option label="顺丰速运" value="顺丰速运"></el-option>
            <el-option label="圆通速递" value="圆通速递"></el-option>
            <el-option label="申通快递" value="申通快递"></el-option>
            <el-option label="中通快递" value="中通快递"></el-option>
            <el-option label="韵达快递" value="韵达快递"></el-option>
            <el-option label="EMS" value="EMS"></el-option>
            <el-option label="其他" value="其他"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="运单号">
          <el-input v-model="confirmForm.tracking_number" placeholder="请输入运单号（可选）"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showConfirmDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmEstimate" :loading="submitting">确认</el-button>
      </template>
    </el-dialog>

    <!-- 价格异议对话框 -->
    <el-dialog v-model="showDisputeDialog" title="价格异议" width="600px">
      <el-form :model="disputeForm" label-width="100px">
        <el-form-item label="异议原因" required>
          <el-input 
            v-model="disputeForm.reason" 
            type="textarea" 
            :rows="4"
            placeholder="请说明您对预估价格的异议原因"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDisputeDialog = false">取消</el-button>
        <el-button type="warning" @click="submitDispute" :loading="submitting">提交异议</el-button>
      </template>
    </el-dialog>

    <!-- 填写物流信息对话框 -->
    <el-dialog v-model="showShippingDialog" title="填写物流信息" width="600px">
      <el-form :model="shippingForm" label-width="100px">
        <el-form-item label="物流公司" required>
          <el-select v-model="shippingForm.carrier" placeholder="请选择物流公司" style="width: 100%">
            <el-option label="顺丰速运" value="顺丰速运"></el-option>
            <el-option label="圆通速递" value="圆通速递"></el-option>
            <el-option label="申通快递" value="申通快递"></el-option>
            <el-option label="中通快递" value="中通快递"></el-option>
            <el-option label="韵达快递" value="韵达快递"></el-option>
            <el-option label="EMS" value="EMS"></el-option>
            <el-option label="其他" value="其他"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="运单号" required>
          <el-input v-model="shippingForm.tracking_number" placeholder="请输入运单号"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShippingDialog = false">取消</el-button>
        <el-button type="primary" @click="submitShipping" :loading="submitting">确认</el-button>
      </template>
    </el-dialog>

    <!-- 最终价格异议对话框 -->
    <el-dialog v-model="showFinalDisputeDialog" title="最终价格异议" width="600px">
      <el-form :model="finalDisputeForm" label-width="100px">
        <el-form-item label="异议原因" required>
          <el-input 
            v-model="finalDisputeForm.reason" 
            type="textarea" 
            :rows="4"
            placeholder="请说明您对最终价格的异议原因"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFinalDisputeDialog = false">取消</el-button>
        <el-button type="warning" @click="submitFinalDispute" :loading="submitting">提交异议</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const order = ref(null)
const inspectionReport = ref(null)

const showConfirmDialog = ref(false)
const showDisputeDialog = ref(false)
const showShippingDialog = ref(false)
const showFinalDisputeDialog = ref(false)

const confirmForm = ref({
  contact_name: '',
  contact_phone: '',
  address: '',
  shipping_carrier: '',
  tracking_number: ''
})

const disputeForm = ref({
  reason: ''
})

const shippingForm = ref({
  carrier: '',
  tracking_number: ''
})

const finalDisputeForm = ref({
  reason: ''
})

const statusMap = {
  pending: '待估价',
  quoted: '已估价',
  confirmed: '已确认',
  shipped: '已寄出',
  inspected: '已检测',
  completed: '已完成',
  cancelled: '已取消'
}

const conditionMap = {
  new: '全新',
  like_new: '几乎全新',
  good: '良好',
  fair: '一般',
  poor: '较差'
}

const getStatusText = (status) => statusMap[status] || status
const getConditionText = (condition) => conditionMap[condition] || condition

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    quoted: 'warning',
    confirmed: 'primary',
    shipped: '',
    inspected: 'success',
    completed: 'success',
    cancelled: 'danger'
  }
  return typeMap[status] || ''
}

const getPaymentStatusText = (status) => {
  const map = {
    pending: '待打款',
    paid: '已打款',
    failed: '打款失败'
  }
  return map[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStepActive = () => {
  const stepMap = {
    pending: 0,
    quoted: 1,
    confirmed: 2,
    shipped: 3,
    inspected: 4,
    completed: 5
  }
  return stepMap[order.value?.status] ?? 0
}

const getCheckItemLabel = (key) => {
  const labelMap = {
    screen: '屏幕',
    battery: '电池',
    camera: '摄像头',
    speaker: '扬声器',
    charging: '充电功能',
    buttons: '按键',
    housing: '外观',
    other: '其他'
  }
  return labelMap[key] || key
}

const getCheckItemValue = (value) => {
  if (value === true || value === 'pass') return '通过'
  if (value === false || value === 'fail') return '不通过'
  return String(value)
}

const loadOrderDetail = async () => {
  loading.value = true
  try {
    const orderId = route.params.id
    const res = await api.get(`/recycle-orders/${orderId}/`)
    order.value = res.data

    // 加载质检报告
    try {
      const reportRes = await api.get(`/recycle-orders/${orderId}/inspection-report/`)
      inspectionReport.value = reportRes.data
    } catch (error) {
      // 如果没有质检报告，忽略错误
      inspectionReport.value = null
    }

    // 初始化表单数据
    if (order.value.contact_name) {
      confirmForm.value.contact_name = order.value.contact_name
    }
    if (order.value.contact_phone) {
      confirmForm.value.contact_phone = order.value.contact_phone
    }
    if (order.value.address) {
      confirmForm.value.address = order.value.address
    }
  } catch (error) {
    console.error('加载订单详情失败:', error)
    ElMessage.error('加载订单详情失败，请稍后重试')
    router.push('/my-recycle-orders')
  } finally {
    loading.value = false
  }
}

const confirmEstimate = async () => {
  if (!confirmForm.value.contact_name || !confirmForm.value.contact_phone || !confirmForm.value.address) {
    ElMessage.warning('请填写完整的联系信息')
    return
  }

  submitting.value = true
  try {
    const updateData = {
      status: 'confirmed',
      contact_name: confirmForm.value.contact_name,
      contact_phone: confirmForm.value.contact_phone,
      address: confirmForm.value.address
    }

    // 如果填写了物流信息，一起提交
    if (confirmForm.value.shipping_carrier && confirmForm.value.tracking_number) {
      updateData.shipping_carrier = confirmForm.value.shipping_carrier
      updateData.tracking_number = confirmForm.value.tracking_number
      updateData.status = 'shipped'  // 如果填写了物流信息，直接变为已寄出状态
      updateData.shipped_at = new Date().toISOString()
    }

    const res = await api.patch(`/recycle-orders/${order.value.id}/`, updateData)
    
    if (updateData.status === 'shipped') {
      ElMessage.success('确认成功！物流信息已提交，订单状态已更新为已寄出')
    } else {
      ElMessage.success('确认成功！请填写物流信息并寄出设备')
    }
    
    showConfirmDialog.value = false
    // 重置表单
    confirmForm.value = {
      contact_name: '',
      contact_phone: '',
      address: '',
      shipping_carrier: '',
      tracking_number: ''
    }
    await loadOrderDetail()
  } catch (error) {
    console.error('确认估价失败:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.status?.[0] || '确认失败，请稍后重试'
    ElMessage.error(errorMsg)
  } finally {
    submitting.value = false
  }
}

const submitDispute = async () => {
  if (!disputeForm.value.reason.trim()) {
    ElMessage.warning('请填写异议原因')
    return
  }

  submitting.value = true
  try {
    await api.patch(`/recycle-orders/${order.value.id}/`, {
      price_dispute: true,
      price_dispute_reason: disputeForm.value.reason
    })
    ElMessage.success('异议已提交，等待管理员重新评估')
    showDisputeDialog.value = false
    disputeForm.value.reason = ''
    await loadOrderDetail()
  } catch (error) {
    console.error('提交异议失败:', error)
    ElMessage.error(error.response?.data?.detail || '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const submitShipping = async () => {
  if (!shippingForm.value.carrier || !shippingForm.value.tracking_number) {
    ElMessage.warning('请填写完整的物流信息')
    return
  }

  submitting.value = true
  try {
    await api.patch(`/recycle-orders/${order.value.id}/`, {
      status: 'shipped',
      shipping_carrier: shippingForm.value.carrier,
      tracking_number: shippingForm.value.tracking_number,
      shipped_at: new Date().toISOString()
    })
    ElMessage.success('物流信息已提交！设备寄出后，请等待平台检测')
    showShippingDialog.value = false
    shippingForm.value = { carrier: '', tracking_number: '' }
    await loadOrderDetail()
  } catch (error) {
    console.error('提交物流信息失败:', error)
    ElMessage.error(error.response?.data?.detail || '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const confirmFinalPrice = async () => {
  try {
    await ElMessageBox.confirm('确认接受最终价格吗？', '确认', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'info'
    })

    submitting.value = true
    try {
      await api.patch(`/recycle-orders/${order.value.id}/`, {
        status: 'completed'
      })
      ElMessage.success('已确认最终价格，订单已完成')
      await loadOrderDetail()
    } catch (error) {
      console.error('确认最终价格失败:', error)
      ElMessage.error(error.response?.data?.detail || '确认失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  } catch {
    // 用户取消
  }
}

const submitFinalDispute = async () => {
  if (!finalDisputeForm.value.reason.trim()) {
    ElMessage.warning('请填写异议原因')
    return
  }

  submitting.value = true
  try {
    await api.patch(`/recycle-orders/${order.value.id}/`, {
      price_dispute: true,
      price_dispute_reason: finalDisputeForm.value.reason
    })
    ElMessage.success('异议已提交，等待管理员处理')
    showFinalDisputeDialog.value = false
    finalDisputeForm.value.reason = ''
    await loadOrderDetail()
  } catch (error) {
    console.error('提交异议失败:', error)
    ElMessage.error(error.response?.data?.detail || '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/my-recycle-orders')
}

onMounted(() => {
  loadOrderDetail()
})
</script>

<style scoped>
.recycle-order-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 200px);
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

.detail-container {
  min-height: 400px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item .label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.info-item .value {
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

.price-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.price-item.total {
  border-top: 2px solid #ff6600;
  border-bottom: none;
  padding-top: 16px;
  margin-top: 8px;
}

.price-item .label {
  font-size: 16px;
  color: #666;
}

.price-item .value {
  font-size: 18px;
  font-weight: 600;
}

.price-item .value.estimated {
  color: #ff6600;
}

.price-item .value.bonus {
  color: #4caf50;
}

.price-item .value.final {
  color: #ff4444;
  font-size: 20px;
}

.price-item .value.total {
  color: #ff6600;
  font-size: 24px;
  font-weight: 700;
}

.contact-info,
.logistics-info,
.payment-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.inspection-report {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-time {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.report-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.check-label {
  font-size: 14px;
  color: #666;
}

.report-remarks {
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.report-remarks .label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.report-remarks .value {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
}

.action-card {
  border-radius: 12px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (max-width: 768px) {
  .order-info-grid {
    grid-template-columns: 1fr;
  }

  .report-items {
    grid-template-columns: 1fr;
  }
}
</style>

