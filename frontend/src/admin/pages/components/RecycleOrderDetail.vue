<template>
  <div class="recycle-order-detail" v-loading="loading">
    <!-- 订单基本信息 -->
    <el-card class="detail-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>订单信息</span>
          <el-tag :type="getStatusType(detail.status)">{{ getStatusText(detail.status) }}</el-tag>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ detail.id }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ detail.user?.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ detail.device_type }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ detail.brand }}</el-descriptions-item>
        <el-descriptions-item label="型号">{{ detail.model }}</el-descriptions-item>
        <el-descriptions-item label="存储容量">{{ detail.storage || '-' }}</el-descriptions-item>
        <el-descriptions-item label="成色">{{ getConditionText(detail.condition) }}</el-descriptions-item>
        <el-descriptions-item label="预估价格">
          <span v-if="detail.estimated_price">¥{{ detail.estimated_price }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="最终价格">
          <span v-if="detail.final_price" style="color: #f56c6c; font-weight: bold">
            ¥{{ detail.final_price }}
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="加价">
          <span v-if="detail.bonus">¥{{ detail.bonus }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(detail.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ detail.contact_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detail.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ detail.address }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detail.note || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 物流信息 -->
    <el-card v-if="detail.status === 'shipped' || detail.status === 'inspected' || detail.status === 'completed'" class="detail-section" shadow="never">
      <template #header>
        <span>物流信息</span>
      </template>
      <div style="color: #909399; text-align: center; padding: 20px">
        <div>用户已寄出设备</div>
        <div style="margin-top: 8px; font-size: 12px">设备正在运输中，到达后可进行质检</div>
      </div>
    </el-card>

    <!-- 质检报告 -->
    <el-card class="detail-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>质检报告</span>
          <el-button
            v-if="canCreateReport"
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
    <el-card v-if="detail.status === 'inspected' || detail.status === 'shipped'" class="detail-section" shadow="never">
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
            disabled
          />
        </el-form-item>
        <el-form-item label="最终价格" required>
          <el-input-number
            v-model="priceForm.final_price"
            :precision="2"
            :min="0"
            style="width: 100%"
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
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px">
            额外加价金额（可选）
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="savingPrice" @click="updatePrice">
            更新价格
          </el-button>
          <el-button
            v-if="detail.status === 'inspected' && detail.final_price"
            type="success"
            :loading="completing"
            @click="completeOrder"
          >
            完成订单（等待用户确认）
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作流程 -->
    <el-card class="detail-section" shadow="never">
      <template #header>
        <span>流程操作</span>
      </template>
      <div class="action-buttons">
        <el-button
          v-if="detail.status === 'pending'"
          type="primary"
          @click="updateStatus('quoted')"
          :loading="updatingStatus"
        >
          标记为已估价
        </el-button>
        <el-button
          v-if="detail.status === 'quoted'"
          type="primary"
          @click="updateStatus('confirmed')"
          :loading="updatingStatus"
        >
          标记为已确认
        </el-button>
        <el-button
          v-if="detail.status === 'confirmed'"
          type="primary"
          @click="showLogisticsDialog = true"
          :loading="updatingStatus"
        >
          记录物流信息（用户已寄出）
        </el-button>
        <el-button
          v-if="detail.status === 'shipped'"
          type="success"
          @click="updateStatus('inspected')"
          :loading="updatingStatus"
        >
          确认到货，开始质检
        </el-button>
        <el-button
          v-if="detail.status === 'completed' && detail.final_price"
          type="warning"
          @click="showPaymentDialog = true"
          :loading="processingPayment"
        >
          打款给用户
        </el-button>
        <el-button
          v-if="detail.status === 'inspected' && detail.final_price"
          type="success"
          @click="publishToVerified"
          :loading="publishing"
        >
          发布为官方验商品
        </el-button>
        <el-button
          v-if="['pending', 'quoted', 'confirmed'].includes(detail.status)"
          type="danger"
          @click="updateStatus('cancelled')"
          :loading="updatingStatus"
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
      </el-form>
      <template #footer>
        <el-button @click="showReportDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingReport" @click="saveReport">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 物流信息对话框 -->
    <el-dialog
      v-model="showLogisticsDialog"
      title="记录物流信息"
      width="500px"
      @close="resetLogisticsForm"
    >
      <el-form :model="logisticsForm" label-width="100px">
        <el-form-item label="物流公司" required>
          <el-input v-model="logisticsForm.carrier" placeholder="请输入物流公司名称" />
        </el-form-item>
        <el-form-item label="运单号" required>
          <el-input v-model="logisticsForm.tracking_number" placeholder="请输入运单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLogisticsDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingLogistics" @click="saveLogistics">
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
          <div>打款金额：<strong style="color: #f56c6c; font-size: 18px">¥{{ detail.final_price }}</strong></div>
          <div style="margin-top: 8px; font-size: 12px">
            请确认用户已同意最终价格，打款后订单将标记为已完成
          </div>
        </div>
      </el-alert>
      <el-form :model="paymentForm" label-width="100px">
        <el-form-item label="打款方式">
          <el-select v-model="paymentForm.payment_method" style="width: 100%">
            <el-option label="银行转账" value="bank" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="微信支付" value="wechat" />
          </el-select>
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
import { useRoute } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  orderId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['updated'])

const route = useRoute()
const loading = ref(false)
const detail = ref({})
const savingPrice = ref(false)
const savingReport = ref(false)
const savingLogistics = ref(false)
const updatingStatus = ref(false)
const completing = ref(false)
const processingPayment = ref(false)
const publishing = ref(false)

const showReportDialog = ref(false)
const showLogisticsDialog = ref(false)
const showPaymentDialog = ref(false)

const priceForm = reactive({
  estimated_price: 0,
  final_price: 0,
  bonus: 0
})

const reportForm = reactive({
  remarks: '',
  checkItemsJson: '{}'
})

const logisticsForm = reactive({
  carrier: '',
  tracking_number: ''
})

const paymentForm = reactive({
  payment_method: 'bank',
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

const canCreateReport = computed(() => {
  return ['shipped', 'inspected', 'completed'].includes(detail.value.status)
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
    } else {
      ElMessage.error('加载失败')
    }
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const updateStatus = async (newStatus) => {
  try {
    await ElMessageBox.confirm(
      `确认将订单状态更新为"${getStatusText(newStatus)}"吗？`,
      '确认操作',
      { type: 'warning' }
    )
    updatingStatus.value = true
    await adminApi.put(`/inspection-orders/${props.orderId}/status`, null, {
      params: { status: newStatus }
    })
    ElMessage.success('状态更新成功')
    await loadDetail()
    emit('updated')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('更新失败')
    }
  } finally {
    updatingStatus.value = false
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
    await adminApi.post(`/inspection-orders/${props.orderId}/report`, {
      check_items: checkItems,
      remarks: reportForm.remarks
    })
    ElMessage.success('质检报告保存成功')
    showReportDialog.value = false
    await loadDetail()
    emit('updated')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    savingReport.value = false
  }
}

const saveLogistics = async () => {
  if (!logisticsForm.carrier || !logisticsForm.tracking_number) {
    ElMessage.warning('请填写完整的物流信息')
    return
  }
  try {
    savingLogistics.value = true
    await adminApi.post(`/inspection-orders/${props.orderId}/logistics`, {
      carrier: logisticsForm.carrier,
      tracking_number: logisticsForm.tracking_number
    })
    ElMessage.success('物流信息保存成功，订单状态已更新为已寄出')
    showLogisticsDialog.value = false
    resetLogisticsForm()
    await loadDetail()
    emit('updated')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    savingLogistics.value = false
  }
}

const updatePrice = async () => {
  if (!priceForm.final_price || priceForm.final_price <= 0) {
    ElMessage.warning('请输入有效的最终价格')
    return
  }
  try {
    savingPrice.value = true
    await adminApi.put(`/inspection-orders/${props.orderId}/price`, {
      final_price: priceForm.final_price,
      bonus: priceForm.bonus || 0
    })
    ElMessage.success('价格更新成功')
    await loadDetail()
    emit('updated')
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    savingPrice.value = false
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
    await updateStatus('completed')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    completing.value = false
  }
}

const processPayment = async () => {
  try {
    await ElMessageBox.confirm(
      `确认向用户打款 ¥${detail.value.final_price} 吗？`,
      '确认打款',
      { type: 'warning' }
    )
    processingPayment.value = true
    await adminApi.post(`/inspection-orders/${props.orderId}/payment`, {
      payment_method: paymentForm.payment_method,
      note: paymentForm.note
    })
    ElMessage.success('打款成功')
    showPaymentDialog.value = false
    await loadDetail()
    emit('updated')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('打款失败')
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

const resetReportForm = () => {
  if (detail.value.report) {
    reportForm.remarks = detail.value.report.remarks || ''
    reportForm.checkItemsJson = JSON.stringify(detail.value.report.check_items || {}, null, 2)
  } else {
    reportForm.remarks = ''
    reportForm.checkItemsJson = '{}'
  }
}

const resetLogisticsForm = () => {
  logisticsForm.carrier = ''
  logisticsForm.tracking_number = ''
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
</style>

