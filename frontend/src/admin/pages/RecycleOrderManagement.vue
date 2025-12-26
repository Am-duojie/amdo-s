<template>
  <div class="recycle-order-management admin-page">
    <div class="page-header">
      <div>
        <div class="page-title">回收订单管理</div>
        <div class="page-desc">查看、质检、定价、打款等全流程操作</div>
      </div>
      <el-space>
        <el-button :loading="loading" text :icon="Refresh" @click="handleRefresh">刷新</el-button>
      </el-space>
    </div>

    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" class="filter-form" @submit.prevent>
        <el-form-item label="订单状态">
          <el-select v-model="statusFilter" placeholder="全部" clearable style="width: 160px" @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="待寄出" value="pending" />
            <el-option label="已寄出" value="shipped" />
            <el-option label="已收货" value="received" />
            <el-option label="已检测" value="inspected" />
            <el-option label="已完成" value="completed" />
            <el-option label="已打款" value="paid" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="打款状态">
          <el-select v-model="paymentFilter" placeholder="全部" clearable style="width: 160px" @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="待打款" value="pending" />
            <el-option label="已打款" value="paid" />
            <el-option label="打款失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="search"
            placeholder="订单号 / 用户 / 品牌 / 型号"
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
        <el-form-item>
          <el-space>
            <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="stats-card">
      <div class="stats-grid">
        <div class="stat-item" v-for="stat in statItems" :key="stat.key">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <div class="table-toolbar">
        <div class="table-meta">
          <span>共 {{ pagination.total }} 条</span>
          <span v-if="statusFilter">· 状态：{{ getStatusText(statusFilter) }}</span>
          <span v-if="paymentFilter">· 打款：{{ getPaymentStatusText(paymentFilter) }}</span>
          <span v-if="search">· 关键词：{{ search }}</span>
        </div>
        <el-space>
          <el-button text :icon="Refresh" @click="handleRefresh">刷新</el-button>
        </el-space>
      </div>

      <el-table 
        :data="orders" 
        style="width: 100%" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        stripe
        empty-text="暂无订单"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="订单号" width="100" fixed="left">
          <template #default="{ row }">
            <el-link type="primary" @click="openDetail(row)">#{{ row.id }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="用户" width="120">
          <template #default="{ row }">
            {{ row.user?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="设备信息" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="product-title">{{ row.device_type }}</div>
            <div class="product-sub">
              {{ row.brand }} {{ row.model }} <span v-if="row.storage">/ {{ row.storage }}</span> / {{ getConditionText(row.condition) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="condition" label="成色" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getConditionType(row.condition)">
              {{ getConditionText(row.condition) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="价格" width="180">
          <template #default="{ row }">
            <div v-if="row.final_price" class="price-final">
              最终: ¥{{ row.final_price }}
              <span v-if="row.bonus > 0" class="price-bonus">(+¥{{ row.bonus }})</span>
            </div>
            <div v-else-if="row.estimated_price" class="price-estimate">
              预估: ¥{{ row.estimated_price }}
            </div>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="140" align="center">
          <template #default="{ row }">
            <el-tag :type="displayStatusTag(row).type" size="small">
              {{ displayStatusTag(row).text }}
            </el-tag>
            <el-tag v-if="row.payment_status === 'failed'" type="danger" size="small" style="margin-left: 4px">
              打款失败
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="流程进度" min-width="220">
          <template #default="{ row }">
            <div class="process-steps">
              <div 
                v-for="(step, index) in processSteps" 
                :key="step.value"
                class="process-step"
                :class="{ 
                  'active': isStepActive(row, step.value),
                  'completed': isStepCompleted(row, step.value)
                }"
              >
                <div class="step-dot"></div>
                <div class="step-label">{{ getProcessStepLabel(row, step.value) }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right" align="center">
          <template #default="{ row }">
            <el-space wrap>
              <el-button size="small" @click="openDetail(row)">详情</el-button>
              <el-button
                v-if="getPrimaryAction(row)"
                size="small"
                :type="getPrimaryAction(row).type || 'primary'"
                @click="handlePrimaryAction(row)"
              >
                {{ getPrimaryAction(row).label }}
              </el-button>
              <el-dropdown trigger="click" @command="(cmd) => handleMoreCommand(cmd, row)">
                <el-button size="small">
                  更多
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="detail">查看详情</el-dropdown-item>
                    <el-dropdown-item command="copy">复制订单号</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer">
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
    </el-card>
  </div>

  <!-- 详情/操作弹窗 -->
  <el-dialog
    v-model="detailDialogVisible"
    width="1200px"
    destroy-on-close
    :close-on-click-modal="false"
    :append-to-body="true"
    :title="currentOrder ? `回收订单 #${currentOrder.id}` : '回收订单详情'"
    @close="closeDetailDialog"
  >
    <RecycleOrderDetail
      v-if="currentOrder"
      :order-id="currentOrder.id"
      :initial-action="detailInitialAction"
      @updated="handleOrderUpdated"
    />
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import RecycleOrderDetail from './components/RecycleOrderDetail.vue'
import BatchActions from './components/BatchActions.vue'
import { useAdminAuthStore } from '@/stores/adminAuth'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getRecycleProcessSteps, getRecycleStatusTag, getRecycleStage, isRecycleStepActive, isRecycleStepCompleted } from '@/utils/recycleFlow'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)
const route = useRoute()

const orders = ref([])
const selectedOrders = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const paymentFilter = ref('')
const pagination = ref({ current: 1, pageSize: 20, total: 0 })
const detailDialogVisible = ref(false)
const currentOrder = ref(null)
const detailInitialAction = ref('')
const stats = ref({
  pending: 0,
  shipped: 0,
  inspected: 0,
  completed: 0
})

const statItems = computed(() => [
  { key: 'pending', label: '待寄出', value: stats.value.pending },
  { key: 'shipped', label: '已寄出', value: stats.value.shipped },
  { key: 'inspected', label: '已检测', value: stats.value.inspected },
  { key: 'completed', label: '已完成', value: stats.value.completed }
])

const statusMap = {
  pending: { text: '待寄出', type: 'info' },
  received: { text: '已收货', type: 'success' },
  shipped: { text: '已寄出', type: 'primary' },
  inspected: { text: '已检测', type: 'success' },
  completed: { text: '已完成', type: 'success' },
  paid: { text: '已打款', type: 'success' },
  cancelled: { text: '已取消', type: 'info' }
}

const conditionMap = {
  new: { text: '全新', type: 'success' },
  like_new: { text: '几乎全新', type: 'success' },
  good: { text: '良好', type: 'primary' },
  fair: { text: '一般', type: 'warning' },
  poor: { text: '较差', type: 'danger' }
}

// 流程步骤（按实际流程顺序）
const processSteps = [
  { label: '提交订单', value: 'pending' },
  { label: '已寄出', value: 'shipped' },
  { label: '已收货', value: 'received' },
  { label: '已检测', value: 'inspected' },
  { label: '已完成', value: 'completed' },
  { label: '已打款', value: 'paid' }
]

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'
const getConditionText = (condition) => conditionMap[condition]?.text || condition
const getConditionType = (condition) => conditionMap[condition]?.type || 'info'
const getPaymentStatusText = (status) => {
  const map = {
    pending: '待打款',
    paid: '已打款',
    failed: '打款失败'
  }
  return map[status] || status
}

const getProgressStage = (row) => getRecycleStage(row)

const displayStatusTag = (row) => getRecycleStatusTag(row)

const getProcessStepLabel = (row, stepValue) => {
  return getRecycleProcessSteps(row).find(s => s.value === stepValue)?.label || stepValue
}

const isStepCompleted = (row, stepValue) => {
  return isRecycleStepCompleted(row, stepValue)
}

const isStepActive = (row, stepValue) => {
  return isRecycleStepActive(row, stepValue)
}

const getPrimaryAction = (row) => {
  if (!row) return null
  if (row.status === 'shipped' && !row.received_at) return { label: '确认收货', type: 'success', action: 'receive' }
  if (row.status === 'received') return { label: '开始质检', type: 'primary', action: 'report' }
  if (row.status === 'inspected') return { label: '设置最终价', type: 'warning', action: 'final-price' }
  if (row.status === 'completed' && row.payment_status !== 'paid') return { label: '打款', type: 'primary', action: 'payment' }
  return null
}

const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    if (search.value) {
      params.search = search.value
    }
    const res = await adminApi.get('/inspection-orders', { params })
    orders.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
    
    // 加载统计信息
    await loadStats()
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await adminApi.get('/inspection-orders', { params: { page_size: 1 } })
    // 这里可以单独调用统计接口，或者从列表数据中统计
    // 简化处理：分别请求各状态的数量
    const [pendingRes, shippedRes, inspectedRes, completedRes] = await Promise.all([
      adminApi.get('/inspection-orders', { params: { status: 'pending', page_size: 1 } }),
      adminApi.get('/inspection-orders', { params: { status: 'shipped', page_size: 1 } }),
      adminApi.get('/inspection-orders', { params: { status: 'inspected', page_size: 1 } }),
      adminApi.get('/inspection-orders', { params: { status: 'completed', page_size: 1 } })
    ])
    stats.value = {
      pending: pendingRes.data?.count || 0,
      shipped: shippedRes.data?.count || 0,
      inspected: inspectedRes.data?.count || 0,
      completed: completedRes.data?.count || 0
    }
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const handlePageChange = () => {
  loadOrders()
}

const handleSizeChange = () => {
  pagination.value.current = 1
  loadOrders()
}

const handleRefresh = () => {
  loadOrders()
}

const handleSearch = () => {
  pagination.value.current = 1
  loadOrders()
}

const resetFilters = () => {
  statusFilter.value = ''
  paymentFilter.value = ''
  search.value = ''
  handleSearch()
}

const openDetail = (row, initialAction = '') => {
  currentOrder.value = row
  detailInitialAction.value = initialAction || ''
  detailDialogVisible.value = true
}

const openDetailById = (orderId) => {
  if (!orderId) return
  openDetail({ id: orderId })
}

const closeDetailDialog = () => {
  detailDialogVisible.value = false
  currentOrder.value = null
  detailInitialAction.value = ''
}

const handleOrderUpdated = () => {
  closeDetailDialog()
  loadOrders()
}

const handleSelectionChange = (selection) => {
  selectedOrders.value = selection
}

const handlePrimaryAction = async (row) => {
  const action = getPrimaryAction(row)
  if (!action) return
  if (action.action === 'receive') {
    try {
      await ElMessageBox.confirm('确认已收到用户寄出的设备？确认后将更新订单状态为“已收货”。', '确认收货', {
        type: 'warning',
        confirmButtonText: '确认',
        cancelButtonText: '取消'
      })
      await adminApi.post(`/inspection-orders/${row.id}/logistics`, { action: 'receive' })
      ElMessage.success('已确认收货')
      await loadOrders()
    } catch (error) {
      if (error !== 'cancel') {
        const msg = error.response?.data?.detail || '操作失败'
        ElMessage.error(msg)
      }
    }
    return
  }
  openDetail(row, action.action)
}

const handleMoreCommand = async (command, row) => {
  if (command === 'detail') {
    openDetail(row)
    return
  }
  if (command === 'copy') {
    const text = `#${row.id}`
    try {
      await navigator.clipboard.writeText(text)
      ElMessage.success('已复制订单号')
    } catch {
      ElMessage.success(text)
    }
  }
}

const batchUpdateStatus = async (items, newStatus) => {
  try {
    await ElMessageBox.confirm(
      `确认将选中的 ${items.length} 个订单批量更新状态为"${getStatusText(newStatus)}"吗？`,
      '确认批量操作',
      { type: 'warning' }
    )
    const ids = items.map(item => item.id)
    await adminApi.post('/inspection-orders/batch-update', {
      ids,
      status: newStatus
    })
    ElMessage.success('批量更新成功')
    selectedOrders.value = []
    await loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量更新失败')
    }
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
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
.recycle-order-management {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
}

.page-desc {
  color: #6b7280;
  font-size: 13px;
}

.filter-card,
.table-card,
.stats-card {
  border-radius: 10px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 18px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  border: 1px solid #ebeef5;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #409eff;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 10px;
}

.table-meta {
  display: flex;
  gap: 8px;
  color: #6b7280;
  font-size: 13px;
  flex-wrap: wrap;
}

.table-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.product-title {
  font-weight: 600;
  color: #111827;
  line-height: 1.4;
}

.product-sub {
  color: #6b7280;
  font-size: 12px;
  margin-top: 4px;
}

.price-final {
  font-weight: 700;
  color: #f56c6c;
}

.price-bonus {
  color: #67c23a;
  font-size: 12px;
  margin-left: 4px;
}

.price-estimate {
  color: #909399;
  font-size: 13px;
}

.text-muted {
  color: #c0c4cc;
}

.process-steps {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.process-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  position: relative;
  opacity: 0.4;
}

.process-step.completed,
.process-step.active {
  opacity: 1;
}

.step-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c0c4cc;
  transition: all 0.3s;
}

.process-step.completed .step-dot {
  background: #67c23a;
}

.process-step.active .step-dot {
  background: #409eff;
  width: 10px;
  height: 10px;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
}

.step-label {
  font-size: 11px;
  color: #909399;
  white-space: nowrap;
}

.process-step.completed .step-label,
.process-step.active .step-label {
  color: #303133;
  font-weight: 500;
}
</style>
