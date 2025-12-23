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
              <el-tag :type="statusTag.type" size="large">{{ statusTag.text }}</el-tag>
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
            <!-- 如果有模板信息，显示关联模板标签 -->
            <div class="info-item" v-if="order.template_info">
              <span class="label">关联模板：</span>
              <el-tag type="success" size="small">
                {{ order.template_info.device_type }} / {{ order.template_info.brand }} / {{ order.template_info.model }}
              </el-tag>
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
            <!-- 显示用户选择的配置 -->
            <div class="info-item" v-if="order.selected_color">
              <span class="label">颜色：</span>
              <span class="value">{{ order.selected_color }}</span>
            </div>
            <div class="info-item" v-if="order.selected_ram">
              <span class="label">运行内存：</span>
              <span class="value">{{ order.selected_ram }}</span>
            </div>
            <div class="info-item" v-if="order.selected_version">
              <span class="label">版本：</span>
              <span class="value">{{ order.selected_version }}</span>
            </div>
            <div class="info-item">
              <span class="label">成色：</span>
              <span class="value">{{ getConditionText(order.condition) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 问卷答案卡片 -->
        <el-card class="info-card" v-if="order.questionnaire_answers && Object.keys(order.questionnaire_answers).length > 0">
          <template #header>
            <span>问卷答案</span>
          </template>
          <div class="questionnaire-answers">
            <div 
              v-for="(answer, key) in order.questionnaire_answers" 
              :key="key"
              class="answer-item"
            >
              <span class="answer-label">{{ formatQuestionKey(key) }}：</span>
              <span class="answer-value">{{ formatAnswerValue(answer) }}</span>
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
        <BaseCard title="订单进度" shadow="sm">
          <OrderSteps :order="order" type="recycle" />
        </BaseCard>

        <!-- 联系信息 -->
        <el-card class="info-card" v-if="order.address">
          <template #header>
            <span>联系信息</span>
          </template>
          <div class="contact-info">
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

        <!-- 质检报告（外观对齐「官验商品详情」的验机评估报告区块） -->
        <div class="inspection-shell" v-if="shouldShowInspectionReport">
          <div class="detail-block inspection-block">
            <div class="block-title">质检评估报告</div>
            <InspectionReport
              v-if="inspectionReportForUi"
              :product-id="order.id"
              :report-data-prop="inspectionReportForUi"
            />
            <div v-else class="inspection-report-empty empty-report">
              <el-empty :description="reportMissing ? '质检报告暂未生成，可联系客服查询' : '质检报告生成中，稍后查看'">
                <el-button type="primary" plain @click="contactSupport">联系官方客服</el-button>
              </el-empty>
            </div>
          </div>
        </div>

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
            <template v-if="order.status === 'pending'">
              <el-alert type="info" :closable="false" style="margin-bottom: 16px;">订单已提交，请填写物流信息并寄出设备</el-alert>
              <el-button type="primary" size="large" @click="showShippingDialog = true">填写物流信息</el-button>
            </template>

            <template v-else-if="order.status === 'shipped'">
              <el-alert type="info" :closable="false" style="margin-bottom: 16px;">设备已寄出，等待平台收货与质检</el-alert>
            </template>

            <template v-else-if="order.status === 'received'">
              <el-alert type="info" :closable="false" style="margin-bottom: 16px;">平台已收货，等待质检中...</el-alert>
            </template>

            <template v-else-if="['inspected', 'completed'].includes(order.status) && order.price_dispute">
              <el-alert type="warning" :closable="false" style="margin-bottom: 16px;">
                <template #title>已提交最终价格异议，等待平台处理</template>
                <div v-if="order.price_dispute_reason" style="margin-top: 8px; color: #606266;">
                  异议原因：{{ order.price_dispute_reason }}
                </div>
              </el-alert>
              <el-button type="warning" size="large" @click="showFinalDisputeDialog = true">补充/修改异议</el-button>
              <el-button type="primary" plain size="large" @click="contactSupport">联系官方客服</el-button>
              <el-button type="danger" plain size="large" @click="cancelOrder">取消订单</el-button>
            </template>

            <template v-else-if="['inspected', 'completed'].includes(order.status) && !order.final_price_confirmed">
              <el-alert type="success" :closable="false" style="margin-bottom: 16px;">
                <template #title>质检已完成，请确认最终价格</template>
                <div style="margin-top: 8px;">
                  <div style="font-size: 16px; margin-bottom: 8px;">
                    最终价格: <span style="color: #f56c6c; font-weight: bold; font-size: 20px;">¥{{ order.final_price }}</span>
                    <span v-if="order.bonus > 0" style="color: #67c23a; font-size: 16px; margin-left: 8px;">+ 加价 ¥{{ order.bonus }}</span>
                  </div>
                  <div v-if="order.bonus > 0" style="font-size: 18px; color: #ff6600; font-weight: bold;">实付金额: ¥{{ (parseFloat(order.final_price) + parseFloat(order.bonus || 0)).toFixed(2) }}</div>
                </div>
              </el-alert>
              <el-button type="primary" size="large" @click="confirmFinalPrice">确认最终价格</el-button>
              <el-button type="warning" size="large" @click="showFinalDisputeDialog = true">对最终价格有异议</el-button>
              <el-button type="primary" plain size="large" @click="contactSupport">联系官方客服</el-button>
              <el-button type="danger" plain size="large" @click="cancelOrder">取消订单</el-button>
            </template>

            <template v-else-if="showPaymentPending">
              <el-alert type="warning" :closable="false" style="margin-bottom: 12px;">质检已完成，平台正在安排打款。</el-alert>
              <div class="cta-row">
                <el-button type="primary" plain size="large" @click="contactSupport">联系官方客服</el-button>
              </div>
            </template>

            <template v-else-if="order.status === 'completed' && order.payment_status === 'paid'">
              <el-alert type="success" :closable="false">订单已完成，打款已完成！</el-alert>
            </template>

            <template v-else-if="order.status === 'cancelled'">
              <el-alert type="warning" :closable="false">订单已取消，感谢您的支持。</el-alert>
            </template>

            <template v-else-if="order.payment_status === 'failed'">
              <el-alert type="error" :closable="false">打款失败，请联系客服处理。</el-alert>
            </template>
          </div>
        </el-card>
      </div>
    </div>



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
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import api from '@/utils/api'
import BaseCard from '@/components/BaseCard.vue'
import OrderSteps from '@/components/OrderSteps.vue'
import InspectionReport from '@/components/InspectionReport.vue'
import { getRecycleStatusTag } from '@/utils/recycleFlow'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const order = ref(null)
const inspectionReport = ref(null)
const reportMissing = ref(false)
const normalizedReport = computed(() => {
  if (!inspectionReport.value) return {}
  // 已标准化结构（含 categories）
  if (inspectionReport.value.categories) return { categories: inspectionReport.value.categories }
  // 如果 check_items 是数组，可能是分类数组或扁平项数组
  if (Array.isArray(inspectionReport.value.check_items)) {
    const arr = inspectionReport.value.check_items
    // 判断是否包含 title/group 结构
    if (arr.length && (arr[0].title || arr[0].groups)) {
      return { categories: arr }
    }
    // 否则当作扁平数组，元素里应有 label/value/pass
    return { items: arr.map(item => ({
      label: item.label || item.key || '',
      value: item.value,
      pass: typeof item.pass === 'boolean' ? item.pass : (item.value === 'pass' || item.value === true)
    })) }
  }
  return {}
})
const inspectionReportForUi = computed(() => {
  if (!inspectionReport.value || !order.value) return null

  const baseInfo = {
    model: `${order.value.brand || ''} ${order.value.model || ''}`.trim(),
    level: `外观 ${getConditionText(order.value.condition) || ''}`,
    spec: order.value.storage || '',
    color: order.value.selected_color || order.value.color || '',
    price: order.value.final_price || order.value.estimated_price || '',
    coverImage: order.value.cover_image || ''
  }

  const norm = normalizedReport.value || {}
  let categories = []

  if (norm.categories && norm.categories.length) {
    categories = norm.categories
  } else if (Array.isArray(norm.items) && norm.items.length) {
    categories = [{
      title: '检测结果',
      groups: [{
        name: '',
        items: norm.items.map(item => ({
          label: item.label || item.key || '',
          value: item.value ?? '',
          pass: typeof item.pass === 'boolean' ? item.pass : (item.value === 'pass' || item.value === true)
        }))
      }]
    }]
  } else if (inspectionReport.value.check_items) {
    categories = [{
      title: '检测结果',
      groups: [{
        name: '',
        items: Object.entries(inspectionReport.value.check_items).map(([key, val]) => ({
          label: key,
          value: val,
          pass: val === 'pass' || val === true
        }))
      }]
    }]
  }

  if (!categories.length) return null
  return { baseInfo, categories }
})

const statusTag = computed(() => getRecycleStatusTag(order.value))
const showPaymentPending = computed(() => {
  if (!order.value) return false
  if (order.value.payment_status === 'paid') return false
  if (order.value.price_dispute) return false
  return order.value.status === 'completed' && !!order.value.final_price_confirmed
})
const shouldShowInspectionReport = computed(() => {
  if (!order.value) return false
  return ['inspected', 'completed'].includes(order.value.status)
})

const showShippingDialog = ref(false)
const showFinalDisputeDialog = ref(false)

const shippingForm = ref({
  carrier: '',
  tracking_number: ''
})

const finalDisputeForm = ref({
  reason: ''
})

const statusMap = {
  pending: '待寄出',
  received: '已收货',
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

// 格式化问题key为中文标题
const formatQuestionKey = (key) => {
  const keyMap = {
    channel: '购买渠道',
    color: '颜色',
    storage: '存储容量',
    usage: '使用情况',
    accessories: '配件情况',
    screen_appearance: '屏幕外观',
    body: '机身外壳',
    display: '屏幕显示',
    front_camera: '前置摄像头',
    rear_camera: '后置摄像头',
    repair: '维修情况',
    screen_repair: '屏幕维修',
    functional: '功能检测'
  }
  return keyMap[key] || key
}

// 格式化答案值
const formatAnswerValue = (answer) => {
  if (!answer) return '未填写'
  
  // 如果是数组（多选）
  if (Array.isArray(answer)) {
    return answer.map(item => {
      if (typeof item === 'object' && item.label) {
        return item.label
      }
      return String(item)
    }).join('、')
  }
  
  // 如果是对象（单选）
  if (typeof answer === 'object' && answer.label) {
    return answer.label
  }
  
  // 其他情况直接返回字符串
  return String(answer)
}

const loadOrderDetail = async () => {
  loading.value = true
  try {
    const orderId = route.params.id
    const res = await api.get(`/recycle-orders/${orderId}/`)
    order.value = res.data
    // 先用订单自带的质检报告字段兜底（不同接口字段名可能不一致）
    if (order.value?.inspection_report) inspectionReport.value = order.value.inspection_report
    if (order.value?.inspection_reports) inspectionReport.value = order.value.inspection_reports
    if (order.value?.report) inspectionReport.value = order.value.report

    // 加载质检报告
    const fetchReport = async (path) => {
      const res = await api.get(path)
      const data = res.data?.report || res.data?.data || res.data
      if (data && Object.keys(data).length > 0) {
        inspectionReport.value = data
        reportMissing.value = false
        return true
      }
      return false
    }
    try {
      // 优先尝试后端下划线路径
      const ok = await fetchReport(`/recycle-orders/${orderId}/inspection_report/`)
      if (!ok) {
        await fetchReport(`/recycle-orders/${orderId}/inspection-report/`)
      }
    } catch (error) {
      if (!inspectionReport.value) inspectionReport.value = null
      reportMissing.value = true
    }


  } catch (error) {
    console.error('加载订单详情失败:', error)
    ElMessage.error('加载订单详情失败，请稍后重试')
    router.push('/my-recycle-orders')
  } finally {
    loading.value = false
  }
}

const submitShipping = async () => {
  if (!shippingForm.value.carrier || !shippingForm.value.tracking_number) {
    ElMessage.warning('请填写完整的物流信息')
    return
  }

  submitting.value = true
  try {
    // 提交物流信息，后端会自动将状态从 pending 变为 shipped
    await api.patch(`/recycle-orders/${order.value.id}/`, {
      shipping_carrier: shippingForm.value.carrier,
      tracking_number: shippingForm.value.tracking_number
    })
    ElMessage.success('物流信息已提交！订单状态已更新为已寄出')
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
    const finalPrice = order.value.final_price
    const bonus = order.value.bonus || 0
    const totalPrice = (parseFloat(finalPrice) + parseFloat(bonus)).toFixed(2)
    
    await ElMessageBox.confirm(
      `确认接受最终价格 ¥${finalPrice}${bonus > 0 ? ` + 加价 ¥${bonus}` : ''} = ¥${totalPrice} 吗？确认后订单将进入打款阶段。`, 
      '确认最终价格', 
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    submitting.value = true
    try {
      await api.post(`/recycle-orders/${order.value.id}/confirm_final_price/`)
      ElMessage.success('已确认最终价格，订单已进入打款阶段')
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

const cancelOrder = async () => {
  try {
    await ElMessageBox.confirm('确认取消此订单吗？', '确认', {
      confirmButtonText: '确认',
      cancelButtonText: '再想想',
      type: 'warning'
    })
    submitting.value = true
    await api.patch(`/recycle-orders/${order.value.id}/`, { status: 'cancelled' })
    ElMessage.success('订单已取消')
    await loadOrderDetail()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('取消订单失败:', e)
      ElMessage.error(e?.response?.data?.detail || '取消失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

const contactSupport = () => {
  ElMessageBox.alert(
    '请通过右侧客服入口或拨打客服电话 400-000-0000 与官方客服沟通。',
    '联系客服',
    { confirmButtonText: '知道了' }
  )
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

/* 强制质检报告分栏，保持与官方验详情一致 */
.detail-block {
  margin-top: 24px;
}

.block-title {
  font-weight: 600;
  margin-bottom: 12px;
}

.inspection-shell {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

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

.inspection-report-empty {
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

.questionnaire-answers {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.answer-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.answer-item:last-child {
  border-bottom: none;
}

.answer-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  min-width: 100px;
}

.answer-value {
  font-size: 14px;
  color: #333;
  flex: 1;
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
