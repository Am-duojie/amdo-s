<template>
  <div class="recycle-order-detail" v-loading="loading">
    <!-- 流程状态可视化 -->
    <el-card class="detail-section" shadow="never">
      <template #header>
        <span>订单流程</span>
      </template>
      <div class="process-timeline">
        <div 
          v-for="(step, index) in processSteps" 
          :key="step.value"
          class="timeline-step"
          :class="{ 
            'completed': isStepCompleted(step.value),
            'active': isStepActive(step.value),
            'pending': !isStepCompleted(step.value) && !isStepActive(step.value)
          }"
        >
          <div class="timeline-marker">
            <el-icon v-if="isStepCompleted(step.value)"><Check /></el-icon>
            <el-icon v-else-if="isStepActive(step.value)"><Loading /></el-icon>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="timeline-content">
            <div class="step-title">{{ step.label }}</div>
            <div class="step-time">{{ getStepTime(step.value) }}</div>
          </div>
          <div v-if="index < processSteps.length - 1" class="timeline-line"></div>
        </div>
      </div>
    </el-card>

    <!-- 订单基本信息 -->
    <el-card class="detail-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>订单信息</span>
          <div>
            <el-tag :type="getStatusType(detail.status)" size="large">{{ getStatusText(detail.status) }}</el-tag>
            <el-tag v-if="detail.payment_status === 'paid'" type="success" size="large" style="margin-left: 8px">已打款</el-tag>
            <el-tag v-if="detail.price_dispute" type="warning" size="large" style="margin-left: 8px">价格异议</el-tag>
          </div>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">#{{ detail.id }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ detail.user?.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ detail.device_type }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ detail.brand }}</el-descriptions-item>
        <el-descriptions-item label="型号">{{ detail.model }}</el-descriptions-item>
        <el-descriptions-item label="存储容量">{{ detail.storage || '-' }}</el-descriptions-item>
        <el-descriptions-item label="成色">
          <el-tag :type="getConditionType(detail.condition)">{{ getConditionText(detail.condition) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="预估价格">
          <span v-if="detail.estimated_price" style="font-size: 16px; color: #909399">
            ¥{{ detail.estimated_price }}
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="最终价格">
          <span v-if="detail.final_price" style="font-size: 18px; color: #f56c6c; font-weight: bold">
            ¥{{ detail.final_price }}
            <span v-if="detail.bonus > 0" style="color: #67c23a; font-size: 14px">(+¥{{ detail.bonus }})</span>
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="总金额">
          <span v-if="detail.total_price" style="font-size: 20px; color: #f56c6c; font-weight: bold">
            ¥{{ detail.total_price }}
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="联系人">{{ detail.contact_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detail.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ detail.address }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detail.note || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(detail.updated_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 物流信息 -->
    <el-card v-if="detail.status !== 'pending' && detail.status !== 'quoted'" class="detail-section" shadow="never">
      <template #header>
        <span>物流信息</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="物流公司">{{ detail.shipping_carrier || '-' }}</el-descriptions-item>
        <el-descriptions-item label="运单号">{{ detail.tracking_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="寄出时间">{{ formatTime(detail.shipped_at) }}</el-descriptions-item>
        <el-descriptions-item label="收到时间">
          <span v-if="detail.received_at">{{ formatTime(detail.received_at) }}</span>
          <el-button 
            v-else-if="detail.status === 'shipped' && hasPerm('inspection:write')"
            size="small"
            type="primary"
            @click="markReceived"
            :loading="markingReceived"
          >
            确认收到设备
          </el-button>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 质检报告 -->
    <el-card class="detail-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>质检报告</span>
          <el-button
            v-if="canCreateReport && hasPerm('inspection:write')"
            size="small"
            type="primary"
            @click="showReportDialog = true"
          >
            {{ detail.report ? '更新报告' : '创建报告' }}
          </el-button>
        </div>
      </template>
      <div v-if="detail.report">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="质检时间">
            {{ formatTime(detail.report.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="质检备注">
            {{ detail.report.remarks || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="检测项目">
            <pre class="check-items">{{ JSON.stringify(detail.report.check_items, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else style="color: #909399; text-align: center; padding: 20px">
        <el-empty description="暂无质检报告" />
      </div>
    </el-card>

    <!-- 价格管理 -->
    <el-card v-if="canManagePrice" class="detail-section" shadow="never">
      <template #header>
        <span>价格管理</span>
      </template>
      <el-form :model="priceForm" label-width="120px" style="max-width: 600px">
        <el-form-item label="预估价格">
          <el-input-number
            v-model="priceForm.estimated_price"
            :precision="2"
            :min="0"
            style="width: 100%"
            :disabled="detail.status !== 'pending'"
          />
        </el-form-item>
        <el-form-item label="最终价格" required>
          <el-input-number
            v-model="priceForm.final_price"
            :precision="2"
            :min="0"
            style="width: 100%"
            :disabled="detail.status === 'completed' || detail.payment_status === 'paid'"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px">
            根据质检结果调整最终回收价格
          </div>
        </el-form-item>
        <el-form-item label="加价">
          <el-input-number
            v-model="priceForm.bonus"
            :precision="2"
            :min="0"
            style="width: 100%"
            :disabled="detail.status === 'completed' || detail.payment_status === 'paid'"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px">
            额外加价金额（可选）
          </div>
        </el-form-item>
        <el-form-item>
          <el-button 
            v-if="detail.status === 'pending' && hasPerm('inspection:price')"
            type="primary" 
            :loading="savingPrice" 
            @click="saveEstimatedPrice"
          >
            设置预估价格并标记为已估价
          </el-button>
          <el-button 
            v-if="(detail.status === 'inspected' || detail.status === 'shipped') && hasPerm('inspection:price')"
            type="primary" 
            :loading="savingPrice" 
            @click="saveFinalPrice"
          >
            更新最终价格
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 打款信息 -->
    <el-card v-if="detail.status === 'completed' || detail.payment_status === 'paid'" class="detail-section" shadow="never">
      <template #header>
        <span>打款信息</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="打款状态">
          <el-tag :type="detail.payment_status === 'paid' ? 'success' : 'warning'">
            {{ detail.payment_status === 'paid' ? '已打款' : '待打款' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="打款方式">{{ detail.payment_method || '-' }}</el-descriptions-item>
        <el-descriptions-item label="打款账户">{{ detail.payment_account || '-' }}</el-descriptions-item>
        <el-descriptions-item label="打款时间">{{ formatTime(detail.paid_at) }}</el-descriptions-item>
        <el-descriptions-item label="打款备注" :span="2">{{ detail.payment_note || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 价格异议 -->
    <el-card v-if="detail.price_dispute" class="detail-section" shadow="never">
      <template #header>
        <span>价格异议</span>
      </template>
      <el-alert type="warning" :closable="false">
        <div>
          <div style="font-weight: bold; margin-bottom: 8px">异议原因：</div>
          <div>{{ detail.price_dispute_reason || '-' }}</div>
        </div>
      </el-alert>
    </el-card>

    <!-- 操作流程 -->
    <el-card class="detail-section" shadow="never">
      <template #header>
        <span>流程操作</span>
      </template>
      <div class="action-buttons">
        <!-- 估价操作 -->
        <el-button
          v-if="detail.status === 'pending' && hasPerm('inspection:write')"
          type="primary"
          @click="showPriceDialog('estimated')"
        >
          给出预估价格
        </el-button>
        
        <!-- 确认收货操作 -->
        <el-button
          v-if="detail.status === 'shipped' && !detail.received_at && hasPerm('inspection:write')"
          type="success"
          @click="markReceived"
          :loading="markingReceived"
        >
          确认收到设备
        </el-button>
        
        <!-- 开始质检 -->
        <el-button
          v-if="(detail.status === 'shipped' || detail.status === 'confirmed') && detail.received_at && hasPerm('inspection:write')"
          type="primary"
          @click="showReportDialog = true"
        >
          开始质检
        </el-button>
        
        <!-- 完成订单 -->
        <el-button
          v-if="detail.status === 'inspected' && detail.final_price && hasPerm('inspection:write')"
          type="success"
          @click="completeOrder"
          :loading="completing"
        >
          完成订单
        </el-button>
        
        <!-- 打款操作 -->
        <el-button
          v-if="canShowPaymentButton"
          type="warning"
          @click="openPaymentDialog"
        >
          打款给用户
        </el-button>
        <!-- 打款调试信息 -->
        <el-tag v-if="!canShowPaymentButton && detail.status === 'completed' && detail.payment_status !== 'paid'" 
                type="info" size="small" style="margin-left: 8px">
          权限不足或无最终价格
        </el-tag>
        
        <!-- 发布为官方验商品 -->
        <el-button
          v-if="detail.status === 'inspected' && detail.final_price && hasPerm('recycled:write')"
          type="success"
          @click="publishToVerified"
          :loading="publishing"
        >
          发布为官方验商品
        </el-button>
        
        <!-- 取消订单 -->
        <el-button
          v-if="['pending', 'quoted', 'confirmed'].includes(detail.status) && hasPerm('inspection:write')"
          type="danger"
          @click="cancelOrder"
        >
          取消订单
        </el-button>
      </div>
    </el-card>

    <!-- 质检报告对话框 -->
    <el-dialog
      v-model="showReportDialog"
      title="质检报告"
      width="700px"
      @close="resetReportForm"
    >
      <el-form :model="reportForm" label-width="100px">
        <el-form-item label="质检备注">
          <el-input
            v-model="reportForm.remarks"
            type="textarea"
            :rows="4"
            placeholder="请输入质检备注信息"
          />
        </el-form-item>
        <el-form-item label="检测项目">
          <el-input
            v-model="reportForm.checkItemsJson"
            type="textarea"
            :rows="8"
            placeholder='请输入JSON格式的检测项目，例如：{"外观": "良好", "屏幕": "无划痕", "功能": "正常"}'
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px">
            JSON格式：{"项目名": "检测结果", ...}
          </div>
        </el-form-item>
        <el-form-item label="最终价格" required>
          <el-input-number
            v-model="reportForm.final_price"
            :precision="2"
            :min="0"
            style="width: 100%"
            placeholder="根据质检结果设置最终价格"
          />
        </el-form-item>
        <el-form-item label="加价">
          <el-input-number
            v-model="reportForm.bonus"
            :precision="2"
            :min="0"
            style="width: 100%"
            placeholder="额外加价金额（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReportDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingReport" @click="saveReport">
          保存并完成质检
        </el-button>
      </template>
    </el-dialog>

    <!-- 价格对话框 -->
    <el-dialog
      v-model="priceDialogVisible"
      title="设置预估价格"
      width="500px"
      @close="priceDialogVisible = false"
    >
      <el-form :model="priceForm" label-width="120px">
        <el-form-item label="预估价格" required>
          <el-input-number
            v-model="priceForm.estimated_price"
            :precision="2"
            :min="0"
            style="width: 100%"
            placeholder="请输入预估价格"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px">
            设置预估价格后，订单状态将自动更新为"已估价"
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="priceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingPrice" @click="saveEstimatedPrice">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 打款对话框 -->
    <el-dialog
      v-model="showPaymentDialog"
      title="打款给用户"
      width="500px"
    >
      <el-alert
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <div>
          <div>打款金额：<strong style="color: #f56c6c; font-size: 18px">¥{{ detail.total_price || detail.final_price }}</strong></div>
          <div style="margin-top: 8px; font-size: 12px">
            请确认用户已同意最终价格，打款后订单将标记为已打款
          </div>
        </div>
      </el-alert>
      <el-form :model="paymentForm" label-width="100px">
        <el-form-item label="打款方式" required>
          <el-select v-model="paymentForm.payment_method" style="width: 100%">
            <el-option label="存入易淘钱包" value="wallet" />
            <el-option label="支付方直接转账" value="transfer" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="paymentForm.payment_method === 'transfer'" label="打款账户" required>
          <el-input
            v-model="paymentForm.payment_account"
            :placeholder="(detail.user && detail.user.alipay_login_id) ? ('已绑定：' + detail.user.alipay_login_id) : '请输入用户的收款账户'"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="paymentForm.note"
            type="textarea"
            :rows="3"
            placeholder="打款备注信息（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPaymentDialog = false">取消</el-button>
        <el-button type="primary" :loading="processingPayment" @click="processPayment">
          确认打款
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Loading } from '@element-plus/icons-vue'
import { useAdminAuthStore } from '@/stores/adminAuth'

const router = useRouter()

const props = defineProps({
  orderId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['updated'])

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)

const loading = ref(false)
const detail = ref({})
const savingPrice = ref(false)
const savingReport = ref(false)
const markingReceived = ref(false)
const updatingStatus = ref(false)
const completing = ref(false)
const processingPayment = ref(false)
const publishing = ref(false)

const showReportDialog = ref(false)
const priceDialogVisible = ref(false)
const showPaymentDialog = ref(false)

const priceForm = reactive({
  estimated_price: 0,
  final_price: 0,
  bonus: 0
})

const reportForm = reactive({
  remarks: '',
  checkItemsJson: '{}',
  final_price: 0,
  bonus: 0
})

const paymentForm = reactive({
  payment_method: 'wallet',
  payment_account: '',
  note: ''
})

// 打款按钮显示条件计算属性
const canShowPaymentButton = computed(() => {
  if (!detail.value) return false
  
  const hasCorrectStatus = ['completed', 'inspected'].includes(detail.value.status)
  const notPaid = detail.value.payment_status !== 'paid'
  const hasFinalPrice = !!detail.value.final_price
  const hasPermission = hasPerm('inspection:payment')
  
  // 调试信息
  console.log('打款按钮条件检查:', {
    hasCorrectStatus,
    notPaid,
    hasFinalPrice,
    hasPermission,
    currentStatus: detail.value.status,
    paymentStatus: detail.value.payment_status,
    finalPrice: detail.value.final_price,
    permissions: admin.user?.value?.permissions
  })
  
  return hasCorrectStatus && notPaid && hasFinalPrice && hasPermission
})

// 流程步骤
const processSteps = [
  { label: '提交订单', value: 'pending' },
  { label: '已估价', value: 'quoted' },
  { label: '已确认', value: 'confirmed' },
  { label: '已寄出', value: 'shipped' },
  { label: '已检测', value: 'inspected' },
  { label: '已完成', value: 'completed' },
  { label: '已打款', value: 'paid' }
]

const statusMap = {
  pending: { text: '待估价', type: 'info' },
  quoted: { text: '已估价', type: 'warning' },
  confirmed: { text: '已确认', type: 'primary' },
  shipped: { text: '已寄出', type: 'primary' },
  inspected: { text: '已检测', type: 'success' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'info' }
} 

const openPaymentDialog = () => {
  const loginId = (detail.value && detail.value.user && detail.value.user.alipay_login_id) ? detail.value.user.alipay_login_id : ''
  paymentForm.payment_method = loginId ? 'transfer' : 'wallet'
  paymentForm.payment_account = loginId || ''
  showPaymentDialog.value = true
}

const conditionMap = {
  new: { text: '全新', type: 'success' },
  like_new: { text: '几乎全新', type: 'success' },
  good: { text: '良好', type: 'primary' },
  fair: { text: '一般', type: 'warning' },
  poor: { text: '较差', type: 'danger' }
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'
const getConditionText = (condition) => conditionMap[condition]?.text || condition
const getConditionType = (condition) => conditionMap[condition]?.type || 'info'

const isStepCompleted = (stepValue) => {
  const stepIndex = processSteps.findIndex(s => s.value === stepValue)
  const currentIndex = processSteps.findIndex(s => s.value === detail.value.status)
  return currentIndex > stepIndex || (detail.value.payment_status === 'paid' && stepValue === 'paid')
}

const isStepActive = (stepValue) => {
  return detail.value.status === stepValue || (detail.value.payment_status === 'paid' && stepValue === 'paid')
}

const getStepTime = (stepValue) => {
  const timeMap = {
    pending: detail.value.created_at,
    quoted: detail.value.created_at,
    confirmed: detail.value.created_at,
    shipped: detail.value.shipped_at,
    inspected: detail.value.inspected_at,
    completed: detail.value.updated_at,
    paid: detail.value.paid_at
  }
  return formatTime(timeMap[stepValue])
}

const canCreateReport = computed(() => {
  return ['shipped', 'confirmed'].includes(detail.value.status) && detail.value.received_at
})

const canManagePrice = computed(() => {
  return ['pending', 'quoted', 'shipped', 'inspected'].includes(detail.value.status)
})

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await adminApi.get(`/inspection-orders/${props.orderId}`)
    if (res.data?.success) {
      detail.value = res.data.item || {}
      priceForm.estimated_price = detail.value.estimated_price || 0
      priceForm.final_price = detail.value.final_price || 0
      priceForm.bonus = detail.value.bonus || 0
      
      if (detail.value.report) {
        reportForm.remarks = detail.value.report.remarks || ''
        reportForm.checkItemsJson = JSON.stringify(detail.value.report.check_items || {}, null, 2)
      }
      reportForm.final_price = detail.value.final_price || detail.value.estimated_price || 0
      reportForm.bonus = detail.value.bonus || 0
    } else {
      ElMessage.error('加载失败')
    }
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const markReceived = async () => {
  try {
    markingReceived.value = true
    const res = await adminApi.post(`/inspection-orders/${props.orderId}/received`)
    if (res.data?.success) {
      ElMessage.success('已确认收到设备')
      await loadDetail()
      emit('updated')
    } else {
      ElMessage.error(res.data?.detail || '操作失败')
    }
  } catch (error) {
    console.error('确认收到设备失败:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.error || error.message || '操作失败'
    ElMessage.error(errorMsg)
  } finally {
    markingReceived.value = false
  }
}

const showPriceDialog = (type) => {
  if (type === 'estimated') {
    priceForm.estimated_price = detail.value.estimated_price || 0
  }
  priceDialogVisible.value = true
}

const saveEstimatedPrice = async () => {
  if (!priceForm.estimated_price || priceForm.estimated_price <= 0) {
    ElMessage.warning('请输入有效的预估价格')
    return
  }
  
  // 检查token是否存在
  const token = localStorage.getItem('ADMIN_TOKEN')
  if (!token) {
    ElMessage.error('登录已过期，请重新登录')
    setTimeout(() => {
      window.location.href = '/admin/login'
    }, 1000)
    return
  }
  
  try {
    savingPrice.value = true
    
    // 直接发送请求，让拦截器处理token
    await adminApi.put(`/inspection-orders/${props.orderId}/price`, {
      price_type: 'estimated',
      estimated_price: priceForm.estimated_price
    })
    ElMessage.success('预估价格设置成功，订单状态已更新为已估价')
    priceDialogVisible.value = false
    await loadDetail()
    emit('updated')
  } catch (error) {
    console.error('保存预估价格失败:', error, error.response)
    
    // 如果是401错误，拦截器已经处理了跳转和错误提示，这里不需要重复处理
    if (error.response?.status === 401) {
      // 拦截器已经显示了错误提示并会跳转，这里不需要额外处理
      return
    }
    
    // 其他错误显示具体错误信息
    const errorMsg = error.response?.data?.detail || error.response?.data?.error || error.message || '保存失败'
    ElMessage.error(errorMsg)
  } finally {
    savingPrice.value = false
  }
}

const saveFinalPrice = async () => {
  if (!priceForm.final_price || priceForm.final_price <= 0) {
    ElMessage.warning('请输入有效的最终价格')
    return
  }
  try {
    savingPrice.value = true
    await adminApi.put(`/inspection-orders/${props.orderId}/price`, {
      price_type: 'final',
      final_price: priceForm.final_price,
      bonus: priceForm.bonus || 0
    })
    ElMessage.success('价格更新成功')
    await loadDetail()
    emit('updated')
  } catch (error) {
    console.error('保存最终价格失败:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.error || error.message || '更新失败'
    ElMessage.error(errorMsg)
    
    // 如果是认证错误，提示用户重新登录
    if (error.response?.status === 401) {
      ElMessage.warning('登录已过期，请重新登录')
    }
  } finally {
    savingPrice.value = false
  }
}

  const saveReport = async () => {
    try {
      let checkItems = {}
      try {
        checkItems = JSON.parse(reportForm.checkItemsJson || '{}')
      } catch (e) {
        ElMessage.error('检测项目JSON格式错误')
        return
      }
      if (typeof checkItems !== 'object' || Array.isArray(checkItems) || checkItems === null) {
        ElMessage.error('检测项目必须是对象(JSON)')
        return
      }
      if (!reportForm.final_price || reportForm.final_price <= 0) {
        ElMessage.warning('请输入有效的最终价格')
        return
      }
      savingReport.value = true
    
    // 先保存质检报告
    await adminApi.post(`/inspection-orders/${props.orderId}/report`, {
      check_items: checkItems,
      remarks: reportForm.remarks
    })
    
    // 再更新最终价格
    await adminApi.put(`/inspection-orders/${props.orderId}/price`, {
      price_type: 'final',
      final_price: reportForm.final_price,
      bonus: reportForm.bonus || 0
    })
    
    ElMessage.success('质检报告保存成功，订单状态已更新为已检测')
    showReportDialog.value = false
    await loadDetail()
    emit('updated')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    savingReport.value = false
  }
}

const completeOrder = async () => {
  try {
    await ElMessageBox.confirm(
      '完成订单后，将等待用户确认价格。确认后可以进行打款操作。',
      '确认完成订单',
      { type: 'warning' }
    )
    completing.value = true
    await adminApi.put(`/inspection-orders/${props.orderId}`, { status: 'completed' })
    ElMessage.success('订单已完成')
    await loadDetail()
    emit('updated')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    completing.value = false
  }
}

const processPayment = async () => {
  if (!paymentForm.payment_method) {
    ElMessage.warning('请选择打款方式')
    return
  }
  if (paymentForm.payment_method === 'transfer' && !paymentForm.payment_account) {
    ElMessage.warning('请输入收款账户')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认向用户打款 ¥${detail.value.total_price || detail.value.final_price} 吗？`,
      '确认打款',
      { type: 'warning' }
    )
    processingPayment.value = true
    await adminApi.post(`/inspection-orders/${props.orderId}/payment`, {
      payment_method: paymentForm.payment_method,
      payment_account: paymentForm.payment_account,
      note: paymentForm.note
    })
    ElMessage.success('打款成功')
    showPaymentDialog.value = false
    await loadDetail()
    emit('updated')
  } catch (error) {
    if (error !== 'cancel') {
      const errorData = error.response?.data
      let errorMessage = '打款失败'
      if (errorData?.detail) {
        errorMessage = errorData.detail
        // 显示更详细的错误信息
        if (errorData.current_status) {
          errorMessage += ` (当前状态: ${errorData.current_status})`
        }
        if (errorData.payment_status) {
          errorMessage += ` (打款状态: ${errorData.payment_status})`
        }
      }
      ElMessage.error(errorMessage)
      console.error('打款失败详情:', errorData)
    }
  } finally {
    processingPayment.value = false
  }
}

const publishToVerified = async () => {
  try {
    await ElMessageBox.confirm(
      '确认将此回收商品发布为官方验商品吗？',
      '确认发布',
      { type: 'warning' }
    )
    publishing.value = true
    await adminApi.post(`/inspection-orders/${props.orderId}/publish-verified`)
    ElMessage.success('发布成功')
    await loadDetail()
    emit('updated')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('发布失败')
    }
  } finally {
    publishing.value = false
  }
}

const cancelOrder = async () => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      '请输入取消原因',
      '取消订单',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '请输入取消原因'
      }
    )
    await adminApi.put(`/inspection-orders/${props.orderId}`, {
      status: 'cancelled',
      reject_reason: reason
    })
    ElMessage.success('订单已取消')
    await loadDetail()
    emit('updated')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

const resetReportForm = () => {
  if (detail.value.report) {
    reportForm.remarks = detail.value.report.remarks || ''
    reportForm.checkItemsJson = JSON.stringify(detail.value.report.check_items || {}, null, 2)
  } else {
    reportForm.remarks = ''
    reportForm.checkItemsJson = '{}'
  }
  reportForm.final_price = detail.value.final_price || detail.value.estimated_price || 0
  reportForm.bonus = detail.value.bonus || 0
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.recycle-order-detail {
  padding: 0;
}

.detail-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.check-items {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 13px;
  margin: 0;
  max-height: 300px;
  overflow: auto;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.process-timeline {
  display: flex;
  align-items: flex-start;
  gap: 0;
  padding: 20px 0;
  overflow-x: auto;
}

.timeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  min-width: 120px;
  flex: 1;
}

.timeline-marker {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  position: relative;
  z-index: 2;
  transition: all 0.3s;
}

.timeline-step.pending .timeline-marker {
  background: #e4e7ed;
  color: #909399;
}

.timeline-step.active .timeline-marker {
  background: #409eff;
  color: #fff;
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
}

.timeline-step.completed .timeline-marker {
  background: #67c23a;
  color: #fff;
}

.timeline-content {
  margin-top: 8px;
  text-align: center;
}

.step-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.timeline-step.pending .step-title {
  color: #909399;
}

.step-time {
  font-size: 12px;
  color: #909399;
}

.timeline-line {
  position: absolute;
  top: 16px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #e4e7ed;
  z-index: 1;
}

.timeline-step:last-child .timeline-line {
  display: none;
}

.timeline-step.completed .timeline-line {
  background: #67c23a;
}
</style>
