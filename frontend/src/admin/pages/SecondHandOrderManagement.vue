<template>
  <div class="order-page admin-page">
    <el-card shadow="hover" class="page-card">
      <div class="page-header">
        <div>
          <div class="page-title">
            <el-icon><List /></el-icon>
            <span>易淘订单管理</span>
          </div>
          <div class="page-desc">按状态/分账快速筛选，一键发货、退款、分账重试</div>
        </div>
        <el-space>
          <el-button :loading="loading" text :icon="Refresh" @click="handleRefresh">刷新</el-button>
        </el-space>
      </div>

      <el-form
        :model="filters"
        label-width="80px"
        class="filter-form"
        inline
        @submit.prevent
      >
        <el-form-item label="订单状态" class="form-item full-row">
          <el-radio-group v-model="filters.status" @change="handleSearch">
            <el-radio-button
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.value"
            >
              {{ item.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="分账状态" class="form-item field">
          <el-select
            v-model="filters.settlement"
            placeholder="全部"
            clearable
            style="width: 180px"
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="待分账" value="pending" />
            <el-option label="已分账" value="settled" />
            <el-option label="分账失败" value="failed" />
          </el-select>
        </el-form-item>

        <el-form-item label="关键词" class="form-item field">
          <el-input
            v-model="filters.keyword"
            placeholder="订单号 / 商品 / 买家"
            clearable
            style="width: 260px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item class="form-item actions">
          <el-space wrap>
            <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-space>
        </el-form-item>
      </el-form>

      <div class="table-toolbar">
        <div class="table-note">
          <span>共 {{ pagination.total }} 条记录</span>
          <span v-if="filters.status">· 状态：{{ getStatusText(filters.status) }}</span>
          <span v-if="filters.settlement">· 分账：{{ getSettlementStatusText(filters.settlement) }}</span>
          <span v-if="filters.keyword">· 关键词：{{ filters.keyword }}</span>
        </div>
        <el-space>
          <el-button text :icon="Refresh" @click="handleRefresh">刷新</el-button>
        </el-space>
      </div>

      <el-table
        :data="orders"
        v-loading="loading"
        border
        stripe
        table-layout="auto"
        empty-text="暂无订单"
      >
        <el-table-column prop="id" label="订单号" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">#{{ row.id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="商品信息" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="product-cell">
              <div class="product-icon">
                <el-icon><Goods /></el-icon>
              </div>
              <div class="product-info">
                <div class="product-title">{{ row.product?.title || row.product || '-' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="买家" width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="buyer-cell">
              <el-avatar :size="24">{{ (row.buyer?.username || 'U')[0].toUpperCase() }}</el-avatar>
              <span>{{ row.buyer?.username || row.buyer || '-' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">
            <span class="price-text">¥{{ row.total_price }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="settlement_status" label="分账" width="120" align="center">
          <template #default="{ row }">
            <el-tag
              v-if="row.settlement_status"
              :type="getSettlementStatusType(row.settlement_status)"
              size="small"
              effect="plain"
            >
              {{ getSettlementStatusText(row.settlement_status) }}
            </el-tag>
            <span v-else class="text-muted">待分账</span>
          </template>
        </el-table-column>

        <el-table-column label="物流信息" min-width="190" show-overflow-tooltip>
          <template #default="{ row }">
            <div v-if="row.carrier && row.tracking_number" class="logistics-cell">
              <div class="carrier-name">{{ row.carrier }}</div>
              <div class="tracking-no">
                <el-icon><Van /></el-icon>
                <span>{{ row.tracking_number }}</span>
              </div>
            </div>
            <span v-else class="text-muted">未发货</span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="240" fixed="right" align="center">
          <template #default="{ row }">
            <el-space wrap>
              <el-button link type="primary" @click="openDetail(row)">详情</el-button>
              <el-button
                v-if="hasPerm('payment:write') && row.status === 'paid'"
                link
                type="success"
                @click="shipOrder(row)"
              >
                发货
              </el-button>

              <el-dropdown
                v-if="hasPerm('payment:view') || hasPerm('payment:write')"
                trigger="click"
              >
                <el-button link type="info">
                  更多
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      v-if="hasPerm('payment:view') && row.status === 'paid'"
                      :icon="Refresh"
                      @click="queryPayment(row)"
                    >
                      查询支付
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-if="hasPerm('payment:view')"
                      :icon="Money"
                      @click="openSettlement(row)"
                    >
                      分账详情
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-if="hasPerm('payment:write')"
                      :icon="RefreshRight"
                      @click="retrySettlement(row)"
                    >
                      重试分账
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-if="hasPerm('payment:write') && row.status === 'paid'"
                      :icon="CircleClose"
                      divided
                      class="danger-text"
                      @click="refundOrder(row)"
                    >
                      退款
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.current"
          :total="pagination.total"
          :page-size="pagination.pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :page-sizes="[10, 20, 50, 100]"
          background
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="订单详情"
      width="900px"
      align-center
      destroy-on-close
      @close="closeDetailDialog"
    >
      <el-skeleton v-if="detailLoading" :rows="8" animated />
      <div v-else-if="orderDetail" class="detail-wrapper">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="订单号">#{{ orderDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getStatusType(orderDetail.status)">
              {{ getStatusText(orderDetail.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(orderDetail.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="交易号">
            {{ orderDetail.alipay_trade_no || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="分账状态">
            <el-tag
              v-if="orderDetail.settlement_status"
              :type="getSettlementStatusType(orderDetail.settlement_status)"
              effect="plain"
              size="small"
            >
              {{ getSettlementStatusText(orderDetail.settlement_status) }}
            </el-tag>
            <span v-else class="text-muted">待分账</span>
          </el-descriptions-item>
          <el-descriptions-item label="订单金额">¥{{ orderDetail.total_price }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>收货信息</el-divider>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="收货人">
            {{ orderDetail.shipping_name || '-' }}
            <span v-if="orderDetail.shipping_phone">（{{ orderDetail.shipping_phone }}）</span>
          </el-descriptions-item>
          <el-descriptions-item label="收货地址">
            {{ orderDetail.shipping_address || '-' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="orderDetail.note" label="买家备注">
            {{ orderDetail.note }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>人员信息</el-divider>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="买家">
            {{ orderDetail.buyer?.username || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="卖家">
            {{ orderDetail.product?.seller?.username || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="买家联系方式">
            {{ orderDetail.buyer_profile?.phone || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="卖家支付宝">
            {{ orderDetail.seller_profile?.alipay_login_id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="卖家实名">
            {{ orderDetail.seller_profile?.alipay_real_name || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>商品信息</el-divider>
        <div class="detail-product">
          <div class="product-cover">
            <img
              v-if="orderDetail.product?.images?.length"
              :src="getImageUrl(orderDetail.product.images[0].image)"
              alt="商品图片"
            />
            <div v-else class="no-image">无图</div>
          </div>
          <div class="product-content">
            <div class="product-title">{{ orderDetail.product?.title || '-' }}</div>
            <div class="product-desc" v-if="orderDetail.product?.description">
              {{ orderDetail.product.description }}
            </div>
            <div class="product-meta">
              <span class="price">¥{{ orderDetail.total_price }}</span>
              <el-tag size="small" effect="plain">
                {{ getConditionText(orderDetail.product?.condition) }}
              </el-tag>
              <span class="muted">地点：{{ orderDetail.product?.location || '-' }}</span>
            </div>
          </div>
        </div>

        <el-divider>物流信息</el-divider>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="物流公司">
            {{ orderDetail.carrier || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="运单号">
            {{ orderDetail.tracking_number || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="发货时间">
            {{ formatDateTime(orderDetail.shipped_at) || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="签收时间">
            {{ formatDateTime(orderDetail.delivered_at) || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>结算信息</el-divider>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="结算方式">
            <el-tag v-if="orderDetail.settlement_method==='TRANSFER'" type="warning" size="small" effect="plain">
              转账代结算
            </el-tag>
            <el-tag v-else-if="orderDetail.settlement_method==='ROYALTY'" type="success" size="small" effect="plain">
              分账结算
            </el-tag>
            <span v-else class="text-muted">待确定</span>
          </el-descriptions-item>
          <el-descriptions-item label="到账账户">
            {{ orderDetail.settlement_account || orderDetail.seller_profile?.alipay_login_id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="分账金额">
            ¥{{ orderDetail.seller_settle_amount ?? '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="平台佣金">
            ¥{{ orderDetail.platform_commission_amount ?? '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="分账时间">
            {{ formatDateTime(orderDetail.settled_at) || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="分账请求号">
            {{ orderDetail.settle_request_no || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="转账订单号">
            {{ orderDetail.transfer_order_id || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else class="text-muted">暂无详情</div>
    </el-dialog>

    <el-dialog
      v-model="showShipDialog"
      title="订单发货"
      width="480px"
      align-center
      @close="closeShipDialog"
    >
      <el-form :model="shipForm" label-position="top">
        <el-form-item label="物流公司" required>
          <el-select v-model="shipForm.carrier" placeholder="请选择物流公司" style="width: 100%">
            <el-option
              v-for="company in logisticsCompanies"
              :key="company"
              :label="company"
              :value="company"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="运单号" required>
          <el-input v-model="shipForm.tracking_number" placeholder="请输入运单号" :prefix-icon="Ticket" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeShipDialog">取消</el-button>
          <el-button type="primary" :loading="shipping" @click="confirmShip">确认发货</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="settlementDialogVisible"
      title="分账详情"
      width="680px"
      align-center
      destroy-on-close
    >
      <div v-if="settlementDetail" class="settlement-content">
        <div class="settlement-header">
          <div class="settlement-stat">
            <div class="label">分账状态</div>
            <div class="value">
              <el-tag
                v-if="settlementDetail.settlement_status"
                :type="getSettlementStatusType(settlementDetail.settlement_status)"
                effect="dark"
              >
                {{ getSettlementStatusText(settlementDetail.settlement_status) }}
              </el-tag>
              <span v-else>待分账</span>
            </div>
          </div>
          <div class="settlement-stat">
            <div class="label">卖家应收</div>
            <div class="value price">¥{{ settlementDetail.seller_settle_amount ?? '0.00' }}</div>
          </div>
          <div class="settlement-stat">
            <div class="label">平台佣金</div>
            <div class="value price">¥{{ settlementDetail.platform_commission_amount ?? '0.00' }}</div>
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ settlementDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="支付宝交易号">
            {{ settlementDetail.alipay_trade_no || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="结算方式">
            <el-tag v-if="settlementDetail.settlement_method==='TRANSFER'" type="warning" size="small" effect="plain">
              转账代结算
            </el-tag>
            <el-tag v-else-if="settlementDetail.settlement_method==='ROYALTY'" type="success" size="small" effect="plain">
              分账结算
            </el-tag>
            <el-tag v-else type="info" size="small">待确定</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="到账账户">
            <div class="text-truncate">
              {{ settlementDetail.settlement_account || settlementDetail.seller?.alipay_login_id || '-' }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="卖家姓名">
            {{ settlementDetail.seller?.alipay_real_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="分账时间">
            {{ formatDateTime(settlementDetail.settled_at) || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          v-if="settlementDetail.can_retry === false"
          title="不可重试：请检查卖家绑定状态或交易单号有效性"
          type="warning"
          show-icon
          :closable="false"
          class="mt-12"
        />

        <div class="history-section">
          <h4>分账历程</h4>
          <el-scrollbar max-height="300px">
            <el-empty v-if="!settlementHistory.length" description="暂无记录" :image-size="60" />
            <el-timeline v-else>
              <el-timeline-item
                v-for="h in settlementHistory"
                :key="h.id"
                :timestamp="formatDateTime(h.created_at)"
                :type="h.snapshot?.result === 'success' ? 'success' : 'danger'"
              >
                <div class="timeline-content">
                  <div class="timeline-title">
                    {{ getSettlementActionText(h.action) }}
                    <el-tag :type="getResultTagType(h.snapshot?.result)" size="small" class="ml-2">
                      {{ h.snapshot?.result === 'success' ? '成功' : '失败' }}
                    </el-tag>
                  </div>
                  <div v-if="h.snapshot?.code || h.snapshot?.msg" class="error-msg">
                    {{ h.snapshot?.msg || h.snapshot?.sub_msg || h.snapshot?.code }}
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-scrollbar>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeSettlementDialog">关闭</el-button>
          <el-button
            v-if="hasPerm('payment:write') && settlementDetail?.can_retry !== false"
            type="primary"
            :loading="retrying"
            @click="handleRetrySettlement"
          >
            重试分账
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminAuthStore } from '@/stores/adminAuth'
import { getImageUrl } from '@/utils/image'
import { LOGISTICS_COMPANIES } from '@/constants/logistics'
import {
  Search,
  List,
  Goods,
  Money,
  Van,
  Ticket,
  ArrowDown,
  Refresh,
  RefreshRight,
  CircleClose
} from '@element-plus/icons-vue'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)
const route = useRoute()

const statusOptions = [
  { label: '全部', value: '' },
  { label: '待付款', value: 'pending' },
  { label: '已付款', value: 'paid' },
  { label: '已发货', value: 'shipped' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
]

const filters = reactive({
  status: '',
  settlement: '',
  keyword: ''
})

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

const orders = ref([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const detailLoading = ref(false)
const orderDetail = ref(null)

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

const settlementStatusMap = {
  settled: { text: '已分账', type: 'success' },
  failed: { text: '分账失败', type: 'danger' },
  pending: { text: '待分账', type: 'warning' }
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
const getSettlementStatusText = (status) => settlementStatusMap[status]?.text || status
const getSettlementStatusType = (status) => settlementStatusMap[status]?.type || 'info'
const getConditionText = (condition) => conditionMap[condition] || condition || '-'

const getSettlementActionText = (action) => {
  const map = {
    settlement_auto: '自动分账',
    settlement_retry: '管理员重试',
    settlement_retry_transfer: '管理员重试(转账)'
  }
  return map[action] || action
}

const getResultTagType = (result) => (result === 'success' ? 'success' : 'danger')

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      status: filters.status || undefined,
      settlement_status: filters.settlement || undefined,
      search: filters.keyword || undefined
    }
    const res = await adminApi.get('/payment/orders', { params })
    orders.value = res.data?.results || []
    pagination.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载订单失败')
    orders.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadOrders()
}

const handleRefresh = () => {
  loadOrders()
}

const handlePageChange = (page) => {
  pagination.current = page
  loadOrders()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.current = 1
  loadOrders()
}

const resetFilters = () => {
  filters.status = ''
  filters.settlement = ''
  filters.keyword = ''
  handleSearch()
}

const openDetail = async (row) => {
  detailDialogVisible.value = true
  detailLoading.value = true
  orderDetail.value = null
  try {
    const res = await adminApi.get(`/payment/orders/${row.id}`)
    orderDetail.value = res.data?.order || null
  } catch (error) {
    ElMessage.error('获取订单详情失败')
    detailDialogVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

const openDetailById = (orderId) => {
  if (!orderId) return
  openDetail({ id: orderId })
}

const closeDetailDialog = () => {
  detailDialogVisible.value = false
  orderDetail.value = null
}

const shipOrder = (row) => {
  currentShipOrder.value = row
  shipForm.carrier = row.carrier || ''
  shipForm.tracking_number = row.tracking_number || ''
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
    closeShipDialog()
    loadOrders()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发货失败')
  } finally {
    shipping.value = false
  }
}

const closeShipDialog = () => {
  showShipDialog.value = false
  shipForm.carrier = ''
  shipForm.tracking_number = ''
  currentShipOrder.value = null
}

const logisticsCompanies = LOGISTICS_COMPANIES

const queryPayment = async (row) => {
  try {
    const res = await adminApi.post(`/payment/order/${row.id}/query`)
    if (res.data?.success) {
      ElMessage.success('查询成功：状态已更新')
      loadOrders()
    } else {
      ElMessage.warning('查询成功：状态未变')
    }
  } catch {
    ElMessage.error('查询支付失败')
  }
}

const refundOrder = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认退款订单 #${row.id}，金额 ¥${row.total_price}？`,
      '确认退款',
      { type: 'warning', confirmButtonText: '确认退款', cancelButtonText: '取消' }
    )
    const res = await adminApi.post(`/payment/order/${row.id}/refund`)
    if (res.data?.success) {
      ElMessage.success('退款申请提交成功')
      loadOrders()
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('退款失败')
  }
}

const openSettlement = async (row) => {
  try {
    const [detailRes, historyRes] = await Promise.all([
      adminApi.get(`/payment/order/${row.id}/settlement`),
      adminApi.get(`/payment/order/${row.id}/settlement/history`)
    ])
    settlementDetail.value = detailRes.data
    settlementHistory.value = historyRes.data?.history || []
    settlementDialogVisible.value = true
  } catch {
    ElMessage.error('获取分账详情失败')
  }
}

const closeSettlementDialog = () => {
  settlementDialogVisible.value = false
  settlementDetail.value = null
  settlementHistory.value = []
}

const retrySettlement = async (row) => {
  try {
    await ElMessageBox.confirm('确定要手动重试分账吗？', '提示', { type: 'warning' })
    retrying.value = true
    const res = await adminApi.post(`/payment/order/${row.id}/settlement/retry`)
    if (res.data?.success) {
      ElMessage.success('已提交重试请求')
      loadOrders()
      if (settlementDialogVisible.value && settlementDetail.value?.id === row.id) {
        openSettlement(row)
      }
    } else {
      ElMessage.error(res.data?.detail || '重试失败')
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('重试分账失败')
  } finally {
    retrying.value = false
  }
}

const handleRetrySettlement = () => {
  if (settlementDetail.value) retrySettlement(settlementDetail.value)
}

onMounted(async () => {
  await loadOrders()
  const orderId = parseInt(route.query.order_id, 10)
  if (orderId) {
    openDetailById(orderId)
  }
})

watch(
  () => route.query.order_id,
  (value) => {
    const orderId = parseInt(value, 10)
    if (orderId) {
      openDetailById(orderId)
    }
  }
)
</script>

<style scoped>
.order-page {
  padding: 16px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 64px);
}

.page-card {
  border-radius: 10px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.page-desc {
  color: #6b7280;
  font-size: 13px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 16px;
  align-items: center;
  margin-bottom: 12px;
  padding: 4px 0;
}

.form-item {
  margin: 0;
}

.form-item.full-row {
  flex: 1 1 100%;
}

.form-item.field {
  flex: 1 1 260px;
  min-width: 220px;
}

.form-item.actions {
  margin-left: auto;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  margin-bottom: 8px;
}

.table-note {
  color: #6b7280;
  font-size: 13px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.product-cell {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.product-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: #f4f5f7;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-title {
  font-weight: 500;
  color: #303133;
  line-height: 1.4;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.buyer-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-text {
  font-weight: 600;
  color: #303133;
}

.text-muted {
  color: #b1b3b8;
}

.logistics-cell .carrier-name {
  font-weight: 500;
}

.logistics-cell .tracking-no {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
}

.danger-text {
  color: #f56c6c;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.detail-wrapper {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.detail-product {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.detail-product .product-cover {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.detail-product .product-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-product .no-image {
  color: #909399;
  font-size: 13px;
}

.detail-product .product-content {
  flex: 1;
}

.detail-product .product-content .product-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
}

.detail-product .product-content .product-desc {
  color: #606266;
  margin-bottom: 8px;
}

.detail-product .product-content .product-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 6px;
}

.detail-product .product-content .product-meta .price {
  font-weight: 700;
  color: #f56c6c;
}

.detail-product .product-content .product-meta .muted {
  color: #909399;
}

.detail-product .product-content .product-contact {
  display: flex;
  gap: 16px;
  color: #606266;
}

.settlement-header {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  background: #f9fafc;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.settlement-stat {
  flex: 1;
  text-align: center;
}

.settlement-stat .label {
  color: #909399;
  font-size: 12px;
  margin-bottom: 6px;
}

.settlement-stat .value {
  font-weight: 600;
  color: #303133;
}

.settlement-stat .price {
  font-family: 'DIN Alternate', 'Helvetica Neue', Arial, sans-serif;
  color: #409eff;
  font-size: 18px;
}

.history-section {
  margin-top: 18px;
}

.history-section h4 {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  border-left: 3px solid #409eff;
  padding-left: 8px;
}

.timeline-title {
  font-weight: 500;
  font-size: 13px;
}

.error-msg {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.text-truncate {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mt-12 {
  margin-top: 12px;
}

@media only screen and (max-width: 768px) {
  .filter-form :deep(.el-form-item) {
    width: 100%;
  }
}
</style>
