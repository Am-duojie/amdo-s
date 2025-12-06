<template>
  <div class="inspection-order-detail">
    <div style="margin-bottom: 16px">
      <el-button size="small" @click="router.back()">返回列表</el-button>
    </div>
    
    <el-card v-loading="loading" shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>回收订单详情 #{{ detail.id }}</span>
          <div>
            <el-tag :type="getStatusType(detail.status)" size="large">{{ getStatusText(detail.status) }}</el-tag>
            <el-tag v-if="detail.payment_status === 'paid'" type="success" size="large" style="margin-left: 8px">已打款</el-tag>
            <el-tag v-if="detail.price_dispute" type="warning" size="large" style="margin-left: 8px">价格异议</el-tag>
          </div>
        </div>
      </template>

      <!-- 订单基本信息 -->
      <el-descriptions :column="2" border style="margin-bottom: 20px">
        <el-descriptions-item label="订单号">{{ detail.id }}</el-descriptions-item>
        <el-descriptions-item label="用户信息">
          {{ detail.user?.username || '-' }}
          <span v-if="detail.user?.email" style="color: #909399; margin-left: 8px">({{ detail.user.email }})</span>
        </el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ detail.device_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ detail.brand || '-' }}</el-descriptions-item>
        <el-descriptions-item label="型号">{{ detail.model || '-' }}</el-descriptions-item>
        <el-descriptions-item label="存储容量">{{ detail.storage || '-' }}</el-descriptions-item>
        <el-descriptions-item label="成色">{{ getConditionText(detail.condition) }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ detail.contact_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detail.contact_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ detail.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detail.note || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(detail.updated_at) }}</el-descriptions-item>
      </el-descriptions>

      <!-- 价格信息 -->
      <el-divider content-position="left">价格信息</el-divider>
      <el-descriptions :column="3" border style="margin-bottom: 20px">
        <el-descriptions-item label="预估价格">
          <span v-if="detail.estimated_price" style="font-size: 16px">¥{{ detail.estimated_price }}</span>
          <span v-else style="color: #909399">-</span>
        </el-descriptions-item>
        <el-descriptions-item label="最终价格">
          <span v-if="detail.final_price" style="font-size: 18px; font-weight: bold; color: #f56c6c">¥{{ detail.final_price }}</span>
          <span v-else style="color: #909399">-</span>
        </el-descriptions-item>
        <el-descriptions-item label="加价">
          <span v-if="detail.bonus">¥{{ detail.bonus }}</span>
          <span v-else style="color: #909399">-</span>
        </el-descriptions-item>
        <el-descriptions-item label="应付款项" :span="3">
          <span v-if="detail.total_price" style="font-size: 20px; font-weight: bold; color: #67c23a">¥{{ detail.total_price }}</span>
          <span v-else style="color: #909399">待确定最终价格</span>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 物流信息 -->
      <el-divider content-position="left">物流信息</el-divider>
      <el-descriptions :column="2" border style="margin-bottom: 20px">
        <el-descriptions-item label="物流公司">{{ detail.shipping_carrier || '-' }}</el-descriptions-item>
        <el-descriptions-item label="运单号">{{ detail.tracking_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="寄出时间">{{ formatTime(detail.shipped_at) }}</el-descriptions-item>
        <el-descriptions-item label="收到时间">{{ formatTime(detail.received_at) }}</el-descriptions-item>
      </el-descriptions>

      <!-- 质检信息 -->
      <el-divider content-position="left">质检信息</el-divider>
      <div v-if="detail.report" style="margin-bottom: 20px">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="质检时间">{{ formatTime(detail.inspected_at) }}</el-descriptions-item>
          <el-descriptions-item label="质检备注">{{ detail.report.remarks || '-' }}</el-descriptions-item>
          <el-descriptions-item label="检测项目">
            <pre style="background: #f5f7fa; padding: 12px; border-radius: 4px; max-height: 300px; overflow: auto">{{ JSON.stringify(detail.report.check_items || {}, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else style="margin-bottom: 20px; text-align: center; padding: 20px; background: #f5f7fa; border-radius: 4px">
        <el-empty description="暂无质检报告" :image-size="80" />
      </div>

      <!-- 打款信息 -->
      <el-divider v-if="detail.payment_status" content-position="left">打款信息</el-divider>
      <el-descriptions v-if="detail.payment_status" :column="2" border style="margin-bottom: 20px">
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

      <!-- 价格异议 -->
      <el-alert v-if="detail.price_dispute" type="warning" :closable="false" style="margin-bottom: 20px">
        <template #title>
          <div style="font-weight: bold">价格异议</div>
          <div style="margin-top: 8px">{{ detail.price_dispute_reason || '用户对价格有异议' }}</div>
        </template>
      </el-alert>

      <!-- 拒绝原因 -->
      <el-alert v-if="detail.reject_reason" type="error" :closable="false" style="margin-bottom: 20px">
        <template #title>
          <div style="font-weight: bold">拒绝原因</div>
          <div style="margin-top: 8px">{{ detail.reject_reason }}</div>
        </template>
      </el-alert>

      <!-- 操作按钮区域 -->
      <el-divider content-position="left">操作</el-divider>
      <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px">
        <!-- 估价操作：给出预估价格（设置价格后自动变为已估价状态） -->
        <el-button
          v-if="detail.status === 'pending'"
          type="primary"
          @click="showPriceDialog('estimated')"
        >
          给出预估价格
        </el-button>
        
        <!-- 快速标记为已估价（如果已有预估价格） -->
        <el-button
          v-if="detail.status === 'pending' && detail.estimated_price"
          type="warning"
          @click="quickMarkQuoted"
        >
          标记为已估价
        </el-button>

        <!-- 确认收到设备 -->
        <el-button
          v-if="detail.status === 'shipped' && !detail.received_at"
          type="success"
          @click="markReceived"
        >
          确认收到设备
        </el-button>

        <!-- 创建质检报告 -->
        <el-button
          v-if="['shipped', 'confirmed'].includes(detail.status)"
          type="primary"
          @click="showReportDialog = true"
        >
          {{ detail.report ? '更新质检报告' : '创建质检报告' }}
        </el-button>

        <!-- 更新最终价格 -->
        <el-button
          v-if="detail.status === 'inspected' || (detail.status === 'shipped' && detail.received_at)"
          type="warning"
          @click="showPriceDialog('final')"
        >
          更新最终价格
        </el-button>

        <!-- 完成订单 -->
        <el-button
          v-if="detail.status === 'inspected' && detail.final_price"
          type="success"
          @click="completeOrder"
        >
          完成订单
        </el-button>

        <!-- 打款 -->
        <el-button
          v-if="detail.status === 'completed' && detail.payment_status !== 'paid'"
          type="success"
          @click="showPaymentDialog = true"
        >
          执行打款
        </el-button>

        <!-- 发布为官方验商品 -->
        <el-button
          v-if="['inspected', 'completed'].includes(detail.status) && detail.final_price"
          type="primary"
          @click="publishToVerified"
          :loading="publishing"
        >
          发布为官方验商品
        </el-button>

        <!-- 取消订单 -->
        <el-button
          v-if="!['completed', 'cancelled'].includes(detail.status)"
          type="danger"
          @click="cancelOrder"
        >
          取消订单
        </el-button>
      </div>
    </el-card>

    <!-- 价格设置对话框 -->
    <el-dialog
      v-model="priceDialogVisible"
      :title="priceDialogType === 'estimated' ? '设置预估价格' : '设置最终价格'"
      width="500px"
    >
      <el-form :model="priceForm" label-width="120px">
        <el-form-item v-if="priceDialogType === 'estimated'" label="预估价格" required>
          <el-input-number
            v-model="priceForm.estimated_price"
            :precision="2"
            :min="0"
            :step="100"
            style="width: 100%"
            placeholder="请输入预估价格"
          />
        </el-form-item>
        <el-form-item v-if="priceDialogType === 'final'" label="最终价格" required>
          <el-input-number
            v-model="priceForm.final_price"
            :precision="2"
            :min="0"
            :step="100"
            style="width: 100%"
            placeholder="请输入最终价格"
          />
        </el-form-item>
        <el-form-item v-if="priceDialogType === 'final'" label="加价">
          <el-input-number
            v-model="priceForm.bonus"
            :precision="2"
            :min="0"
            :step="50"
            style="width: 100%"
            placeholder="额外加价（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="priceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingPrice" @click="savePrice">确定</el-button>
      </template>
    </el-dialog>

    <!-- 质检报告对话框 -->
    <el-dialog
      v-model="showReportDialog"
      title="质检报告"
      width="700px"
    >
      <el-form :model="reportForm" label-width="100px">
        <el-form-item label="检测项目JSON" required>
          <el-input
            v-model="reportForm.checkItemsJson"
            type="textarea"
            :rows="8"
            placeholder='例如: {"外观": "良好", "屏幕": "无划痕", "功能": "正常", "电池": "85%"}'
          />
        </el-form-item>
        <el-form-item label="质检备注">
          <el-input
            v-model="reportForm.remarks"
            type="textarea"
            :rows="4"
            placeholder="填写质检备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReportDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingReport" @click="saveReport">保存</el-button>
      </template>
    </el-dialog>

    <!-- 打款对话框 -->
    <el-dialog
      v-model="showPaymentDialog"
      title="执行打款"
      width="500px"
    >
      <el-form :model="paymentForm" label-width="100px">
        <el-form-item label="打款方式" required>
          <el-select v-model="paymentForm.payment_method" style="width: 100%">
            <el-option label="银行转账" value="bank" />
            <el-option label="支付宝" value="alipay" />
          </el-select>
        </el-form-item>
        <el-form-item label="打款账户" required>
          <el-input v-model="paymentForm.payment_account" placeholder="请输入用户提供的收款账户" />
        </el-form-item>
        <el-form-item label="打款金额">
          <el-input :value="`¥${detail.total_price || 0}`" disabled />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="paymentForm.note"
            type="textarea"
            :rows="3"
            placeholder="打款备注（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPaymentDialog = false">取消</el-button>
        <el-button type="primary" :loading="processingPayment" @click="executePayment">确认打款</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const orderId = parseInt(route.params.id)

const loading = ref(false)
const detail = ref({})
const publishing = ref(false)

// 价格对话框
const priceDialogVisible = ref(false)
const priceDialogType = ref('estimated') // estimated 或 final
const savingPrice = ref(false)
const priceForm = reactive({
  estimated_price: null,
  final_price: null,
  bonus: 0
})

// 质检报告对话框
const showReportDialog = ref(false)
const savingReport = ref(false)
const reportForm = reactive({
  checkItemsJson: '{}',
  remarks: ''
})

// 打款对话框
const showPaymentDialog = ref(false)
const processingPayment = ref(false)
const paymentForm = reactive({
  payment_method: 'bank',
  payment_account: '',
  note: ''
})

const statusMap = {
  pending: { text: '待估价', type: 'info' },
  quoted: { text: '已估价', type: 'warning' },
  confirmed: { text: '已确认', type: 'primary' },
  shipped: { text: '已寄出', type: 'primary' },
  inspected: { text: '已检测', type: 'success' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'info' }
}

const conditionMap = {
  new: '全新',
  like_new: '几乎全新',
  good: '良好',
  fair: '一般',
  poor: '较差'
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'
const getConditionText = (condition) => conditionMap[condition] || condition

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await adminApi.get(`/inspection-orders/${orderId}`)
    if (res.data?.success) {
      detail.value = res.data.item || {}
      // 初始化表单
      if (detail.value.report) {
        reportForm.checkItemsJson = JSON.stringify(detail.value.report.check_items || {}, null, 2)
        reportForm.remarks = detail.value.report.remarks || ''
      }
      priceForm.estimated_price = detail.value.estimated_price
      priceForm.final_price = detail.value.final_price
      priceForm.bonus = detail.value.bonus || 0
    }
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const showPriceDialog = (type) => {
  priceDialogType.value = type
  if (type === 'estimated') {
    priceForm.estimated_price = detail.value.estimated_price || 0
  } else {
    priceForm.final_price = detail.value.final_price || detail.value.estimated_price || 0
    priceForm.bonus = detail.value.bonus || 0
  }
  priceDialogVisible.value = true
}

const savePrice = async () => {
  savingPrice.value = true
  try {
    const data = {
      price_type: priceDialogType.value
    }
    if (priceDialogType.value === 'estimated') {
      if (!priceForm.estimated_price) {
        ElMessage.warning('请输入预估价格')
        return
      }
      data.estimated_price = priceForm.estimated_price
    } else {
      if (!priceForm.final_price) {
        ElMessage.warning('请输入最终价格')
        return
      }
      data.final_price = priceForm.final_price
      data.bonus = priceForm.bonus
    }
    
    await adminApi.put(`/inspection-orders/${orderId}/price`, data)
    ElMessage.success('价格更新成功')
    priceDialogVisible.value = false
    await loadDetail()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  } finally {
    savingPrice.value = false
  }
}

const markReceived = async () => {
  try {
    await ElMessageBox.confirm('确认已收到用户寄出的设备？', '确认', { type: 'warning' })
    await adminApi.post(`/inspection-orders/${orderId}/logistics`, { action: 'receive' })
    ElMessage.success('已标记为收到')
    await loadDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
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
    savingReport.value = true
    await adminApi.post(`/inspection-orders/${orderId}/report`, {
      check_items: checkItems,
      remarks: reportForm.remarks
    })
    ElMessage.success('质检报告保存成功')
    showReportDialog.value = false
    await loadDetail()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    savingReport.value = false
  }
}

const quickMarkQuoted = async () => {
  try {
    await ElMessageBox.confirm('确认标记为已估价？', '确认', { type: 'warning' })
    await adminApi.put(`/inspection-orders/${orderId}`, { status: 'quoted' })
    ElMessage.success('已标记为已估价')
    await loadDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const completeOrder = async () => {
  try {
    await ElMessageBox.confirm('确认完成订单？订单完成后可以进行打款。', '确认', { type: 'warning' })
    await adminApi.put(`/inspection-orders/${orderId}`, { status: 'completed' })
    ElMessage.success('订单已完成')
    await loadDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const executePayment = async () => {
  if (!paymentForm.payment_account) {
    ElMessage.warning('请输入打款账户')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认向账户 ${paymentForm.payment_account} 打款 ¥${detail.value.total_price || 0}？`,
      '确认打款',
      { type: 'warning' }
    )
    processingPayment.value = true
    const res = await adminApi.post(`/inspection-orders/${orderId}/payment`, paymentForm)
    ElMessage.success(res.data?.message || '打款成功')
    showPaymentDialog.value = false
    paymentForm.payment_account = ''
    paymentForm.note = ''
    await loadDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '打款失败')
    }
  } finally {
    processingPayment.value = false
  }
}

const publishToVerified = async () => {
  try {
    await ElMessageBox.confirm(
      '确认将此回收商品发布为官方验商品吗？发布后商品将自动上架。',
      '确认发布',
      { type: 'warning' }
    )
    publishing.value = true
    const res = await adminApi.post(`/inspection-orders/${orderId}/publish-verified`)
    if (res.data?.success) {
      ElMessage.success(`发布成功！商品ID：${res.data.verified_product_id}`)
      await loadDetail()
    } else {
      ElMessage.error(res.data?.detail || '发布失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '发布失败')
    }
  } finally {
    publishing.value = false
  }
}

const cancelOrder = async () => {
  try {
    const { value: reason } = await ElMessageBox.prompt('请输入取消原因', '取消订单', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputType: 'textarea',
      inputPlaceholder: '请填写取消原因'
    })
    await adminApi.put(`/inspection-orders/${orderId}`, { 
      status: 'cancelled',
      reject_reason: reason
    })
    ElMessage.success('订单已取消')
    await loadDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.inspection-order-detail {
  padding: 0;
}
</style>
