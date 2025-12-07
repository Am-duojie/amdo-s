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

      <!-- 订单流程进度 -->
      <el-divider content-position="left">订单流程</el-divider>
      <div style="margin-bottom: 30px; padding: 20px; background: #f5f7fa; border-radius: 8px">
        <el-steps :active="getProcessStepIndex()" finish-status="success" align-center>
          <el-step 
            title="提交订单" 
            :description="formatTime(detail.created_at)"
            :status="getStepStatus('pending')"
          />
          <el-step 
            title="已估价" 
            :description="formatTime(detail.status === 'quoted' ? detail.updated_at : null)"
            :status="getStepStatus('quoted')"
          />
          <el-step 
            title="已确认" 
            :description="formatTime(detail.status === 'confirmed' ? detail.updated_at : null)"
            :status="getStepStatus('confirmed')"
          />
          <el-step 
            title="已寄出" 
            :description="formatTime(detail.shipped_at)"
            :status="getStepStatus('shipped')"
          />
          <el-step 
            title="已检测" 
            :description="formatTime(detail.inspected_at)"
            :status="getStepStatus('inspected')"
          />
          <el-step 
            title="已完成" 
            :description="getCompletedStepDescription()"
            :status="getStepStatus('completed')"
          />
          <el-step 
            title="已打款" 
            :description="getPaidStepDescription()"
            :status="getStepStatus('paid')"
          />
        </el-steps>
      </div>

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
      <el-divider v-if="detail.payment_status || (detail.status === 'completed' || detail.status === 'inspected')" content-position="left">
        <span>打款信息</span>
        <el-button
          v-if="canShowPaymentButton"
          type="success"
          size="small"
          style="margin-left: 16px"
          @click="openPaymentDialog"
        >
          {{ detail.payment_status === 'failed' ? '重新打款' : '执行打款' }}
        </el-button>
      </el-divider>
      <el-descriptions v-if="detail.payment_status || (detail.status === 'completed' || detail.status === 'inspected')" :column="2" border style="margin-bottom: 20px">
        <el-descriptions-item label="打款状态">
          <el-tag :type="getPaymentStatusType(detail.payment_status)">
            {{ getPaymentStatusText(detail.payment_status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="打款方式">
          <span v-if="detail.payment_status === 'paid'">存入用户钱包</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="打款账户">
          <span v-if="detail.payment_status === 'paid'">易淘账户钱包</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="打款时间">{{ formatTime(detail.paid_at) }}</el-descriptions-item>
        <el-descriptions-item label="打款金额" v-if="detail.payment_status === 'paid'">
          <span style="font-size: 16px; font-weight: bold; color: #67c23a">¥{{ detail.total_price || 0 }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="打款备注" :span="detail.payment_status === 'paid' ? 1 : 2">
          <div style="white-space: pre-wrap; word-break: break-all">{{ detail.payment_note || '-' }}</div>
        </el-descriptions-item>
        <el-descriptions-item v-if="detail.payment_status === 'failed'" label="失败原因" :span="2">
          <el-alert type="error" :closable="false" style="margin-top: 8px">
            <template #title>
              <div style="white-space: pre-wrap; word-break: break-all">{{ detail.payment_note || '打款失败，请重试' }}</div>
            </template>
          </el-alert>
        </el-descriptions-item>
        <el-descriptions-item v-if="canShowPaymentButton && detail.payment_status !== 'paid'" label="操作提示" :span="2">
          <el-alert type="info" :closable="false">
            <template #title>
              <div v-if="detail.payment_status === 'failed'">
                上次打款失败，可以重新执行打款操作。打款金额将存入用户的易淘账户钱包中。
              </div>
              <div v-else>
                订单已完成，可以执行打款操作。打款金额将存入用户的易淘账户钱包中。
              </div>
            </template>
          </el-alert>
        </el-descriptions-item>
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
      :title="detail.payment_status === 'failed' ? '重新打款' : '执行打款'"
      width="500px"
    >
      <el-alert
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      >
        <template #title>
          <div>打款将直接存入用户的易淘账户钱包中，用户可以在钱包中提取到支付宝账户</div>
        </template>
      </el-alert>
      <el-alert
        v-if="detail.payment_status === 'failed'"
        type="warning"
        :closable="false"
        style="margin-bottom: 16px"
      >
        <template #title>
          <div>上次打款失败，请检查信息后重新打款</div>
          <div v-if="detail.payment_note" style="margin-top: 8px; font-size: 12px; white-space: pre-wrap">{{ detail.payment_note }}</div>
        </template>
      </el-alert>
      <el-form :model="paymentForm" label-width="120px">
        <el-form-item label="订单号">
          <el-input :value="`#${detail.id}`" disabled />
        </el-form-item>
        <el-form-item label="收款用户">
          <el-input :value="detail.user?.username || '-'" disabled />
        </el-form-item>
        <el-form-item label="设备信息">
          <el-input :value="`${detail.brand || ''} ${detail.model || ''} ${detail.storage || ''}`.trim()" disabled />
        </el-form-item>
        <el-form-item label="打款金额" required>
          <div style="display: flex; align-items: center; gap: 12px">
            <el-input :value="`¥${detail.total_price || 0}`" disabled style="flex: 1" />
            <span style="font-size: 20px; font-weight: bold; color: #f56c6c">¥{{ detail.total_price || 0 }}</span>
          </div>
          <div style="font-size: 12px; color: #909399; margin-top: 8px; padding: 8px; background: #f5f7fa; border-radius: 4px">
            <div>最终价格: ¥{{ detail.final_price || 0 }}</div>
            <div>加价: ¥{{ detail.bonus || 0 }}</div>
            <div style="font-weight: bold; margin-top: 4px">合计: ¥{{ detail.total_price || 0 }}</div>
          </div>
        </el-form-item>
        <el-form-item label="打款方式">
          <el-input value="存入用户钱包" disabled />
          <div style="font-size: 12px; color: #909399; margin-top: 4px">
            金额将存入用户的易淘账户钱包，用户可以在钱包中提取到支付宝账户
          </div>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="paymentForm.note"
            type="textarea"
            :rows="3"
            placeholder="打款备注（可选，如：订单完成奖励等）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPaymentDialog = false">取消</el-button>
        <el-button type="success" :loading="processingPayment" @click="executePayment" size="large">
          {{ detail.payment_status === 'failed' ? '重新打款' : '确认打款' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
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
  note: ''
})

// 打开打款对话框时，初始化表单
const openPaymentDialog = () => {
  // 验证是否可以打款
  if (!canShowPaymentButton.value) {
    ElMessage.warning('当前订单不符合打款条件')
    return
  }
  
  // 验证订单信息
  if (!detail.value.final_price) {
    ElMessage.error('订单尚未确定最终价格，无法打款')
    return
  }
  
  if (!detail.value.user) {
    ElMessage.error('订单用户信息缺失，无法打款')
    return
  }
  
  // 重置表单
  paymentForm.note = ''
  
  // 如果已有打款备注（失败重试时），预填充
  if (detail.value.payment_status === 'failed' && detail.value.payment_note) {
    // 不预填充，让用户重新输入
    paymentForm.note = ''
  }
  
  // 打开对话框
  showPaymentDialog.value = true
}

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

const paymentStatusMap = {
  pending: { text: '待打款', type: 'info' },
  paid: { text: '已打款', type: 'success' },
  failed: { text: '打款失败', type: 'danger' }
}

const getPaymentStatusText = (status) => paymentStatusMap[status]?.text || (status ? '未知' : '待打款')
const getPaymentStatusType = (status) => paymentStatusMap[status]?.type || 'info'

// 计算是否可以显示打款按钮
const canShowPaymentButton = computed(() => {
  if (!detail.value) {
    return false
  }
  
  const status = detail.value.status
  const paymentStatus = detail.value.payment_status
  const finalPrice = detail.value.final_price
  
  // 订单状态必须是已完成或已检测
  if (status !== 'completed' && status !== 'inspected') {
    return false
  }
  
  // 必须有最终价格
  if (!finalPrice || finalPrice <= 0) {
    return false
  }
  
  // 打款状态不能是已打款
  if (paymentStatus === 'paid') {
    return false
  }
  
  // 其他情况（pending、failed、null、undefined）都可以显示
  return true
})

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

// 获取流程步骤索引
const getProcessStepIndex = () => {
  const status = detail.value.status
  const paymentStatus = detail.value.payment_status
  
  // 根据订单状态确定当前步骤
  const statusMap = {
    'pending': 0,
    'quoted': 1,
    'confirmed': 2,
    'shipped': 3,
    'inspected': 4,
    'completed': 5,
  }
  
  let index = statusMap[status] ?? 0
  
  // 如果订单已完成
  if (status === 'completed') {
    // 如果已打款，显示最后一个步骤（已打款）
    if (paymentStatus === 'paid') {
      index = 6
    }
    // 如果未打款，显示已完成步骤（步骤5），但"已打款"步骤会显示为process状态
    else {
      index = 5
    }
  }
  
  return index
}

// 获取步骤状态
const getStepStatus = (step) => {
  const status = detail.value.status
  const paymentStatus = detail.value.payment_status
  
  // 提交订单 - 总是完成
  if (step === 'pending') {
    return 'success'
  }
  
  // 已估价
  if (step === 'quoted') {
    if (['quoted', 'confirmed', 'shipped', 'inspected', 'completed'].includes(status)) {
      return 'success'
    }
    return 'wait'
  }
  
  // 已确认
  if (step === 'confirmed') {
    if (['confirmed', 'shipped', 'inspected', 'completed'].includes(status)) {
      return 'success'
    }
    return 'wait'
  }
  
  // 已寄出
  if (step === 'shipped') {
    if (['shipped', 'inspected', 'completed'].includes(status)) {
      return 'success'
    }
    return 'wait'
  }
  
  // 已检测
  if (step === 'inspected') {
    if (['inspected', 'completed'].includes(status)) {
      return 'success'
    }
    return 'wait'
  }
  
  // 已完成
  if (step === 'completed') {
    // 订单状态为已完成时，已完成步骤显示为成功
    if (status === 'completed') {
      return 'success'
    }
    // 如果订单状态在已完成之前，已完成步骤等待
    return 'wait'
  }
  
  // 已打款
  if (step === 'paid') {
    // 如果已打款，显示为成功
    if (paymentStatus === 'paid') {
      return 'success'
    }
    // 如果订单已完成但未打款，显示为进行中（待处理）
    if (status === 'completed' && !paymentStatus) {
      return 'process' // 当前待处理步骤，高亮显示
    }
    // 其他情况等待
    return 'wait'
  }
  
  return 'wait'
}

// 获取"已完成"步骤的描述
const getCompletedStepDescription = () => {
  const status = detail.value.status
  // 如果订单已完成，显示完成时间
  if (status === 'completed') {
    return formatTime(detail.value.updated_at)
  }
  // 如果订单已检测，显示检测时间（即将完成）
  if (status === 'inspected' && detail.value.inspected_at) {
    return formatTime(detail.value.inspected_at)
  }
  return '-'
}

// 获取"已打款"步骤的描述
const getPaidStepDescription = () => {
  const paymentStatus = detail.value.payment_status
  const status = detail.value.status
  
  // 如果已打款，显示打款时间
  if (paymentStatus === 'paid' && detail.value.paid_at) {
    return formatTime(detail.value.paid_at)
  }
  // 如果订单已完成但未打款，显示提示信息
  if (status === 'completed' && !paymentStatus) {
    return '待打款'
  }
  // 如果打款失败，显示失败提示
  if (paymentStatus === 'failed') {
    return '打款失败'
  }
  return '-'
}

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await adminApi.get(`/inspection-orders/${orderId}`)
    if (res.data?.success) {
      detail.value = res.data.item || {}
      console.log('[详情] 订单详情已加载:', {
        id: detail.value.id,
        status: detail.value.status,
        payment_status: detail.value.payment_status,
        total_price: detail.value.total_price
      })
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
    console.error('[详情] 加载失败:', error)
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
      if (typeof checkItems !== 'object' || Array.isArray(checkItems) || checkItems === null) {
        ElMessage.error('检测项目必须是对象(JSON)')
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
  // 再次验证打款条件
  if (!canShowPaymentButton.value) {
    ElMessage.warning('当前订单不符合打款条件，请刷新页面后重试')
    showPaymentDialog.value = false
    return
  }
  
  // 验证必要信息
  if (!detail.value.final_price) {
    ElMessage.error('订单尚未确定最终价格，无法打款')
    return
  }
  
  if (!detail.value.user) {
    ElMessage.error('订单用户信息缺失，无法打款')
    return
  }
  
  try {
    // 构建详细的确认信息
    const username = detail.value.user?.username || '用户'
    const orderId = detail.value.id
    const brand = detail.value.brand || ''
    const model = detail.value.model || ''
    const finalPrice = detail.value.final_price || 0
    const bonus = detail.value.bonus || 0
    const totalPrice = detail.value.total_price || 0
    const isRetry = detail.value.payment_status === 'failed'
    
    const confirmMessage = isRetry
      ? `确认重新向用户 ${username} 打款？\n\n` +
        `📋 订单信息：\n` +
        `   订单号: #${orderId}\n` +
        `   设备: ${brand} ${model}\n` +
        `   最终价格: ¥${finalPrice}\n` +
        `   加价: ¥${bonus}\n` +
        `   打款总额: ¥${totalPrice}\n\n` +
        `💰 打款说明：\n` +
        `   金额将存入用户的易淘账户钱包中\n` +
        `   用户可以在钱包中提取到支付宝账户\n\n` +
        `⚠️ 确认后将立即执行打款操作，无法撤销！`
      : `确认向用户 ${username} 打款？\n\n` +
        `📋 订单信息：\n` +
        `   订单号: #${orderId}\n` +
        `   设备: ${brand} ${model}\n` +
        `   最终价格: ¥${finalPrice}\n` +
        `   加价: ¥${bonus}\n` +
        `   打款总额: ¥${totalPrice}\n\n` +
        `💰 打款说明：\n` +
        `   金额将存入用户的易淘账户钱包中\n` +
        `   用户可以在钱包中提取到支付宝账户\n\n` +
        `⚠️ 确认后将立即执行打款操作，无法撤销！`
    
    // 显示确认对话框
    await ElMessageBox.confirm(
      confirmMessage,
      isRetry ? '⚠️ 确认重新打款' : '⚠️ 确认打款',
      { 
        type: 'warning',
        confirmButtonText: '确认打款',
        cancelButtonText: '取消',
        dangerouslyUseHTMLString: false,
        distinguishCancelAndClose: true
      }
    )
    
    // 开始处理打款
    processingPayment.value = true
    
    // 调用打款API
    const res = await adminApi.post(`/inspection-orders/${orderId}/payment`, {
      note: paymentForm.note || ''
    })
    
    // 检查响应
    if (res.data?.success) {
      // 打款成功
      ElMessage.success({
        message: res.data?.message || '打款成功！金额已存入用户钱包。',
        duration: 3000,
        showClose: true
      })
      
      // 关闭对话框
      showPaymentDialog.value = false
      paymentForm.note = ''
      
      // 刷新详情以更新流程进度和打款信息
      await loadDetail()
    } else {
      // 打款失败
      const errorMsg = res.data?.detail || '打款失败，请重试'
      ElMessage.error({
        message: errorMsg,
        duration: 5000,
        showClose: true
      })
      
      // 刷新详情以显示失败状态
      await loadDetail()
    }
  } catch (error) {
    // 处理错误
    if (error === 'cancel' || error === 'close') {
      // 用户取消，不显示错误
      return
    }
    
    // API错误
    let errorMsg = '打款失败，请稍后重试'
    if (error.response) {
      // 服务器返回错误
      errorMsg = error.response.data?.detail || error.response.data?.message || errorMsg
    } else if (error.message) {
      // 网络错误或其他错误
      errorMsg = error.message
    }
    
    ElMessage.error({
      message: errorMsg,
      duration: 5000,
      showClose: true
    })
    
    // 刷新详情以显示失败状态
    await loadDetail()
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
