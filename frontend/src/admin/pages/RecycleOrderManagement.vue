<template>
  <div class="recycle-order-management">
    <div class="page-header">
      <h2>回收订单管理</h2>
      <div class="header-actions">
        <el-select v-model="statusFilter" placeholder="筛选状态" style="width: 150px" clearable>
          <el-option label="全部" value="" />
          <el-option label="待估价" value="pending" />
          <el-option label="已估价" value="quoted" />
          <el-option label="已确认" value="confirmed" />
          <el-option label="已寄出" value="shipped" />
          <el-option label="已检测" value="inspected" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-input
          v-model="search"
          placeholder="搜索用户、品牌、型号"
          style="width: 250px; margin-left: 12px"
          clearable
          @keyup.enter="loadOrders"
        />
        <el-button type="primary" @click="loadOrders" style="margin-left: 12px">查询</el-button>
      </div>
    </div>

    <el-table 
      :data="orders" 
      style="width: 100%" 
      v-loading="loading"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="订单号" width="100" />
      <el-table-column label="用户" width="120">
        <template #default="{ row }">
          {{ row.user?.username || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="设备信息" min-width="200">
        <template #default="{ row }">
          <div>{{ row.device_type }}</div>
          <div style="color: #666; font-size: 12px">{{ row.brand }} {{ row.model }}</div>
          <div v-if="row.storage" style="color: #999; font-size: 12px">{{ row.storage }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="condition" label="成色" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ getConditionText(row.condition) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="价格" width="150">
        <template #default="{ row }">
          <div v-if="row.final_price">
            <div style="font-weight: bold; color: #f56c6c">最终: ¥{{ row.final_price }}</div>
          </div>
          <div v-if="row.estimated_price" style="color: #909399; font-size: 12px">
            预估: ¥{{ row.estimated_price }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button
            v-if="canInspect(row)"
            size="small"
            type="primary"
            @click="startInspection(row)"
          >
            开始质检
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
        <el-button
          v-if="hasPerm('inspection:write')"
          type="success"
          @click="batchUpdateStatus(selectedItems, 'inspected')"
        >
          批量标记为已检测
        </el-button>
      </template>
    </BatchActions>

    <!-- 订单详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="回收订单详情"
      width="900px"
      @close="closeDetailDialog"
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
import { ElMessage, ElMessageBox } from 'element-plus'
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

const canInspect = (row) => {
  return row.status === 'shipped' || row.status === 'confirmed'
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
  currentOrder.value = row
  detailDialogVisible.value = true
}

const startInspection = (row) => {
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
</style>

