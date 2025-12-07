<template>
  <div class="secondhand-order-management">
    <div class="page-header">
      <h2>易淘订单管理</h2>
      <div class="header-actions">
        <el-select v-model="statusFilter" placeholder="筛选状态" style="width: 150px" clearable>
          <el-option label="全部" value="" />
          <el-option label="待付款" value="pending" />
          <el-option label="已付款" value="paid" />
          <el-option label="已发货" value="shipped" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-select v-model="settleFilter" placeholder="分账状态" style="width: 150px; margin-left: 12px" clearable>
          <el-option label="全部" value="" />
          <el-option label="待分账" value="pending" />
          <el-option label="已分账" value="settled" />
          <el-option label="分账失败" value="failed" />
        </el-select>
        <el-input
          v-model="search"
          placeholder="搜索订单号、商品、买家"
          style="width: 250px; margin-left: 12px"
          clearable
          @keyup.enter="loadOrders"
        />
        <el-button type="primary" @click="loadOrders" style="margin-left: 12px">查询</el-button>
      </div>
    </div>

    <el-table :data="orders" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="订单号" width="100" />
      <el-table-column label="商品信息" min-width="200">
        <template #default="{ row }">
          <div style="font-weight: 500">{{ row.product?.title || row.product || '-' }}</div>
        </template>
      </el-table-column>
      <el-table-column label="买家" width="120">
        <template #default="{ row }">
          {{ row.buyer?.username || row.buyer || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="金额" width="120">
        <template #default="{ row }">
          <div style="font-weight: bold; color: #f56c6c">¥{{ row.total_price }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="分账状态" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.settlement_status" :type="row.settlement_status==='settled'?'success':(row.settlement_status==='failed'?'danger':'warning')">
            {{ row.settlement_status==='settled'?'已分账':(row.settlement_status==='failed'?'分账失败':'待分账') }}
          </el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="物流信息" width="180">
        <template #default="{ row }">
          <div v-if="row.carrier && row.tracking_number">
            <div>{{ row.carrier }}</div>
            <div style="color: #666; font-size: 12px">{{ row.tracking_number }}</div>
          </div>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button
            v-if="hasPerm('payment:write') && row.status === 'paid'"
            size="small"
            type="success"
            @click="shipOrder(row)"
          >
            发货
          </el-button>
          <el-button
            v-if="hasPerm('payment:view') && row.status === 'paid'"
            size="small"
            @click="queryPayment(row)"
          >
            查询支付
          </el-button>
          <el-button
            v-if="hasPerm('payment:write') && row.status === 'paid'"
            size="small"
            type="danger"
            @click="refundOrder(row)"
          >
            退款
          </el-button>
          <el-button v-if="hasPerm('payment:view')" size="small" type="success" @click="openSettlement(row)">分账详情</el-button>
          <el-button v-if="hasPerm('payment:write')" size="small" @click="retrySettlement(row)">重试分账</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="display: flex; justify-content: flex-end; margin-top: 16px">
      <el-pagination
        v-model:current-page="pagination.current"
        :total="pagination.total"
        :page-size="pagination.pageSize"
        layout="prev, pager, next, total, sizes"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 发货对话框 -->
    <el-dialog
      v-model="showShipDialog"
      title="订单发货"
      width="500px"
      @close="resetShipForm"
    >
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="物流公司" :required="true">
          <el-input v-model="shipForm.carrier" placeholder="请输入物流公司名称" />
        </el-form-item>
        <el-form-item label="运单号" :required="true">
          <el-input v-model="shipForm.tracking_number" placeholder="请输入运单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShipDialog = false">取消</el-button>
        <el-button type="primary" :loading="shipping" @click="confirmShip">
          确认发货
        </el-button>
      </template>
    </el-dialog>

    <!-- 分账详情 -->
  <el-dialog v-model="settlementDialogVisible" title="分账详情" width="600px">
      <div v-if="settlementDetail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="订单ID">{{ settlementDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">{{ getStatusText(settlementDetail.status) }}</el-descriptions-item>
          <el-descriptions-item label="支付宝交易号">{{ settlementDetail.alipay_trade_no || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分账状态">{{ settlementDetail.settlement_status || 'pending' }}</el-descriptions-item>
          <el-descriptions-item label="分账时间">{{ settlementDetail.settled_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="卖家分账金额">¥{{ settlementDetail.seller_settle_amount ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="平台佣金">¥{{ settlementDetail.platform_commission_amount ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="结算方式">
            <el-tag :type="settlementDetail.settlement_method==='TRANSFER'?'warning':'success'">
              {{ settlementDetail.settlement_method==='TRANSFER'?'转账代结算':'分账结算' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="结算到账账户">{{ settlementDetail.settlement_account || settlementDetail.seller?.alipay_login_id || '-' }}</el-descriptions-item>
          <el-descriptions-item v-if="settlementDetail.transfer_order_id" label="转账订单号">{{ settlementDetail.transfer_order_id }}</el-descriptions-item>
          <el-descriptions-item label="卖家姓名">{{ settlementDetail.seller?.alipay_real_name || '-' }}</el-descriptions-item>
        </el-descriptions>
        <div style="margin-top: 12px">
          <el-tag type="info" v-if="settlementDetail.can_retry===false">不可重试：请检查卖家绑定或交易号</el-tag>
          <el-tag type="success" v-else>可重试分账</el-tag>
        </div>
        <el-divider content-position="left">分账历程</el-divider>
        <el-empty v-if="!settlementHistory.length" description="暂无分账记录" />
        <el-timeline v-else>
          <el-timeline-item v-for="h in settlementHistory" :key="h.id" :timestamp="h.created_at" placement="top">
            <div style="font-weight: 500">{{ h.action==='settlement_retry'?'管理员重试':'自动分账' }}</div>
            <div style="color:#666; font-size:12px">{{ h.snapshot?.result || '-' }}</div>
            <div style="color:#999; font-size:12px">{{ h.snapshot?.code }} {{ h.snapshot?.sub_code }} {{ h.snapshot?.msg || '' }} {{ h.snapshot?.sub_msg || '' }}</div>
          </el-timeline-item>
        </el-timeline>
      </div>
      <template #footer>
        <el-button @click="settlementDialogVisible = false">关闭</el-button>
        <el-button v-if="hasPerm('payment:write')" type="primary" :loading="retrying" @click="retrySettlement(settlementDetail)">重试分账</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminAuthStore } from '@/stores/adminAuth'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)

const orders = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const settleFilter = ref('')
const pagination = ref({ current: 1, pageSize: 20, total: 0 })
const showShipDialog = ref(false)
const shipping = ref(false)
const currentShipOrder = ref(null)
const settlementDialogVisible = ref(false)
const settlementDetail = ref(null)
const settlementHistory = ref([])
const retrying = ref(false)

const shipForm = reactive({
  carrier: '',
  tracking_number: ''
})

const statusMap = {
  pending: { text: '待付款', type: 'warning' },
  paid: { text: '已付款', type: 'success' },
  shipped: { text: '已发货', type: 'primary' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'info' }
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'

const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize
    }
    if (statusFilter.value) params.status = statusFilter.value
    if (settleFilter.value) params.settlement_status = settleFilter.value
    const res = await adminApi.get('/payment/orders', { params })
    orders.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = () => {
  loadOrders()
}

const handleSizeChange = () => {
  pagination.value.current = 1
  loadOrders()
}

const viewDetail = (row) => {
  ElMessage.info('订单详情功能开发中')
}

const shipOrder = (row) => {
  currentShipOrder.value = row
  showShipDialog.value = true
}

const confirmShip = async () => {
  if (!shipForm.carrier || !shipForm.tracking_number) {
    ElMessage.warning('请填写完整的物流信息')
    return
  }
  if (!currentShipOrder.value) return

  try {
    shipping.value = true
    await adminApi.post(`/payment/order/${currentShipOrder.value.id}/ship`, shipForm)
    ElMessage.success('发货成功')
    showShipDialog.value = false
    resetShipForm()
    await loadOrders()
  } catch (error) {
    ElMessage.error('发货失败')
  } finally {
    shipping.value = false
  }
}

const queryPayment = async (row) => {
  try {
    const res = await adminApi.post(`/payment/order/${row.id}/query`)
    if (res.data?.success) {
      ElMessage.success('查询成功')
    } else {
      ElMessage.error('查询失败')
    }
  } catch (error) {
    ElMessage.error('查询失败')
  }
}

const refundOrder = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认退款订单 #${row.id}，金额 ¥${row.total_price}？`,
      '确认退款',
      { type: 'warning' }
    )
    const res = await adminApi.post(`/payment/order/${row.id}/refund`)
    if (res.data?.success) {
      ElMessage.success('退款成功')
      await loadOrders()
    } else {
      ElMessage.error('退款失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('退款失败')
    }
  }
}

const openSettlement = async (row) => {
    try {
      const res = await adminApi.get(`/payment/order/${row.id}/settlement`)
      settlementDetail.value = res.data
      const his = await adminApi.get(`/payment/order/${row.id}/settlement/history`)
      settlementHistory.value = his.data?.history || []
      settlementDialogVisible.value = true
    } catch (error) {
      ElMessage.error('获取分账详情失败')
    }
  }
  const retrySettlement = async (row) => {
    try {
      await ElMessageBox.confirm(`重试分账订单 #${row.id}？`, '提示', { type: 'warning' })
      retrying.value = true
      const res = await adminApi.post(`/payment/order/${row.id}/settlement/retry`)
      const ok = res.data?.success
      ElMessage[ok ? 'success' : 'error'](ok ? '已重试分账' : (res.data?.detail || '重试失败'))
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('重试分账失败')
      }
    } finally {
      retrying.value = false
    }
  }


const resetShipForm = () => {
  shipForm.carrier = ''
  shipForm.tracking_number = ''
  currentShipOrder.value = null
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.secondhand-order-management {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
}
</style>





