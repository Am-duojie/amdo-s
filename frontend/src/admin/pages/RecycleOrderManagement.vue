<template>
  <div class="recycle-order-management">
    <div class="page-header">
      <h2>回收订单管理</h2>
      <div class="header-actions">
        <el-select v-model="statusFilter" placeholder="筛选状态" style="width: 150px" clearable @change="loadOrders">
          <el-option label="全部" value="" />
          <el-option label="待估价" value="pending" />
          <el-option label="已估价" value="quoted" />
          <el-option label="已确认" value="confirmed" />
          <el-option label="已寄出" value="shipped" />
          <el-option label="已检测" value="inspected" />
          <el-option label="已完成" value="completed" />
          <el-option label="已打款" value="paid" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-input
          v-model="search"
          placeholder="搜索订单号、用户、品牌、型号"
          style="width: 250px; margin-left: 12px"
          clearable
          @keyup.enter="loadOrders"
        />
        <el-button type="primary" @click="loadOrders" style="margin-left: 12px">查询</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.pending }}</div>
        <div class="stat-label">待估价</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.shipped }}</div>
        <div class="stat-label">待质检</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.inspected }}</div>
        <div class="stat-label">待打款</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.completed }}</div>
        <div class="stat-label">已完成</div>
      </el-card>
    </div>

    <el-table 
      :data="orders" 
      style="width: 100%" 
      v-loading="loading"
      @selection-change="handleSelectionChange"
      stripe
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="订单号" width="100" fixed="left">
        <template #default="{ row }">
          <el-link type="primary" @click="viewDetail(row)">#{{ row.id }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="用户" width="120">
        <template #default="{ row }">
          {{ row.user?.username || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="设备信息" min-width="200">
        <template #default="{ row }">
          <div style="font-weight: 500">{{ row.device_type }}</div>
          <div style="color: #666; font-size: 12px; margin-top: 4px">
            {{ row.brand }} {{ row.model }}
          </div>
          <div v-if="row.storage" style="color: #999; font-size: 12px">{{ row.storage }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="condition" label="成色" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="getConditionType(row.condition)">
            {{ getConditionText(row.condition) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="价格" width="180">
        <template #default="{ row }">
          <div v-if="row.final_price" style="font-weight: bold; color: #f56c6c; font-size: 14px">
            最终: ¥{{ row.final_price }}
            <span v-if="row.bonus > 0" style="color: #67c23a; font-size: 12px">(+¥{{ row.bonus }})</span>
          </div>
          <div v-else-if="row.estimated_price" style="color: #909399; font-size: 13px">
            预估: ¥{{ row.estimated_price }}
          </div>
          <span v-else style="color: #c0c4cc">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusText(row.status) }}
          </el-tag>
          <el-tag v-if="row.payment_status === 'paid'" type="success" size="small" style="margin-left: 4px">
            已打款
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="流程进度" min-width="200">
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
              <div class="step-label">{{ step.label }}</div>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button
            v-if="canOperate(row)"
            size="small"
            type="primary"
            @click="viewDetail(row)"
          >
            {{ getActionText(row) }}
          </el-button>
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

    <!-- 批量操作 -->
    <BatchActions
      :selected-items="selectedOrders"
      @clear="selectedOrders = []"
    >
      <template #default="{ selectedItems, clearSelection }">
        <el-button
          v-if="hasPerm('inspection:write')"
          type="primary"
          @click="batchUpdateStatus(selectedItems, 'quoted')"
        >
          批量标记为已估价
        </el-button>
      </template>
    </BatchActions>

    <!-- 订单详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="回收订单详情"
      width="1200px"
      @close="closeDetailDialog"
      destroy-on-close
    >
      <RecycleOrderDetail
        v-if="currentOrder"
        :order-id="currentOrder.id"
        @updated="handleOrderUpdated"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import RecycleOrderDetail from './components/RecycleOrderDetail.vue'
import BatchActions from './components/BatchActions.vue'
import { useAdminAuthStore } from '@/stores/adminAuth'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)

const orders = ref([])
const selectedOrders = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const pagination = ref({ current: 1, pageSize: 20, total: 0 })
const detailDialogVisible = ref(false)
const currentOrder = ref(null)
const stats = ref({
  pending: 0,
  shipped: 0,
  inspected: 0,
  completed: 0
})

const statusMap = {
  pending: { text: '待估价', type: 'info' },
  quoted: { text: '已估价', type: 'warning' },
  confirmed: { text: '已确认', type: 'primary' },
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

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'
const getConditionText = (condition) => conditionMap[condition]?.text || condition
const getConditionType = (condition) => conditionMap[condition]?.type || 'info'

const isStepCompleted = (row, stepValue) => {
  const stepIndex = processSteps.findIndex(s => s.value === stepValue)
  const currentIndex = processSteps.findIndex(s => s.value === row.status)
  return currentIndex > stepIndex || (row.payment_status === 'paid' && stepValue === 'paid')
}

const isStepActive = (row, stepValue) => {
  return row.status === stepValue || (row.payment_status === 'paid' && stepValue === 'paid')
}

const canOperate = (row) => {
  return ['pending', 'shipped', 'confirmed', 'inspected', 'completed'].includes(row.status)
}

const getActionText = (row) => {
  if (row.status === 'pending') return '估价'
  if (row.status === 'shipped' || row.status === 'confirmed') return '质检'
  if (row.status === 'inspected') return '完成订单'
  if (row.status === 'completed' && row.payment_status !== 'paid') return '打款'
  return '处理'
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

const viewDetail = (row) => {
  currentOrder.value = row
  detailDialogVisible.value = true
}

const closeDetailDialog = () => {
  currentOrder.value = null
}

const handleOrderUpdated = () => {
  closeDetailDialog()
  loadOrders()
}

const handleSelectionChange = (selection) => {
  selectedOrders.value = selection
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

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.recycle-order-management {
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
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

.process-step.completed {
  opacity: 1;
}

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
