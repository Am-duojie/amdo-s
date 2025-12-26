<template>
  <div class="verified-order-management admin-page">
    <div class="page-header">
      <div>
        <div class="page-title">官方验订单管理</div>
        <div class="page-desc">查看、发货、收货、取消等操作</div>
      </div>
      <el-space>
        <el-button :loading="loading" text :icon="Refresh" @click="handleRefresh">刷新</el-button>
      </el-space>
    </div>

    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" class="filter-form" @submit.prevent>
        <el-form-item label="状态">
          <el-select v-model="statusFilter" placeholder="全部" clearable style="width: 160px" @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="待付款" value="pending" />
            <el-option label="已付款" value="paid" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="search"
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
        <el-form-item>
          <el-space>
            <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <div class="table-toolbar">
        <div class="table-meta">
          <span>共 {{ pagination.total }} 条</span>
          <span v-if="statusFilter">· 状态：{{ getStatusText(statusFilter) }}</span>
          <span v-if="search">· 关键词：{{ search }}</span>
        </div>
        <el-space>
          <el-button text :icon="Refresh" @click="handleRefresh">刷新</el-button>
        </el-space>
      </div>

      <el-table :data="orders" style="width: 100%" v-loading="loading" empty-text="暂无订单">
        <el-table-column prop="id" label="订单号" width="100" />
        <el-table-column label="商品信息" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="product-title">{{ row.product?.title || '-' }}</div>
            <div v-if="row.product" class="product-sub">
              {{ row.product.brand }} {{ row.product.model }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="买家" width="140" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.buyer?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">
            <div class="price">¥{{ row.total_price }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="物流信息" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div v-if="row.carrier && row.tracking_number">
              <div>{{ row.carrier }}</div>
              <div class="text-sub">{{ row.tracking_number }}</div>
            </div>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="360" fixed="right" align="center">
          <template #default="{ row }">
            <el-space wrap>
              <el-button size="small" @click="viewDetail(row)">详情</el-button>
              <el-button
                v-if="hasPerm('verified:write') && row.status === 'pending'"
                size="small"
                type="primary"
                @click="markPaid(row)"
              >
                标记已付款
              </el-button>
              <el-button
                v-if="hasPerm('verified:write') && row.status === 'paid'"
                size="small"
                type="success"
                @click="shipOrder(row)"
              >
                发货
              </el-button>
              <el-button
                v-if="hasPerm('verified:write') && row.status === 'shipped'"
                size="small"
                type="warning"
                @click="completeOrder(row)"
              >
                确认收货
              </el-button>
              <el-button
                v-if="hasPerm('verified:write') && ['pending', 'paid'].includes(row.status)"
                size="small"
                type="danger"
                @click="cancelOrder(row)"
              >
                取消
              </el-button>
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

    <!-- 订单详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="订单详情"
      width="900px"
    >
      <VerifiedOrderDetail
        v-if="currentOrder"
        :order-id="currentOrder.id"
        @updated="handleOrderUpdated"
      />
    </el-dialog>

    <!-- 发货对话框 -->
    <el-dialog
      v-model="showShipDialog"
      title="订单发货"
      width="500px"
      @close="resetShipForm"
    >
      <el-form :model="shipForm" label-width="100px">
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
          <el-input v-model="shipForm.tracking_number" placeholder="请输入运单号" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="shipForm.note"
            type="textarea"
            :rows="3"
            placeholder="发货备注（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShipDialog = false">取消</el-button>
        <el-button type="primary" :loading="shipping" @click="confirmShip">
          确认发货
        </el-button>
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
import VerifiedOrderDetail from './components/VerifiedOrderDetail.vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { LOGISTICS_COMPANIES } from '@/constants/logistics'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)
const route = useRoute()

const orders = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const pagination = ref({ current: 1, pageSize: 20, total: 0 })
const detailDialogVisible = ref(false)
const currentOrder = ref(null)
const showShipDialog = ref(false)
const shipping = ref(false)

const shipForm = reactive({
  carrier: '',
  tracking_number: '',
  note: ''
})

const logisticsCompanies = LOGISTICS_COMPANIES

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
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    if (search.value) {
      params.search = search.value
    }
    const res = await adminApi.get('/verified-orders', { params })
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

const openDetailById = (orderId) => {
  if (!orderId) return
  currentOrder.value = { id: orderId }
  detailDialogVisible.value = true
}

const markPaid = async (row) => {
  try {
    await ElMessageBox.confirm('确认标记订单为已付款？', '确认操作', { type: 'warning' })
    await adminApi.post(`/verified-orders/${row.id}/mark-paid`)
    ElMessage.success('操作成功')
    await loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      const data = error.response?.data
      const detail = data?.detail || data?.error
      const message = detail || (typeof data === 'string' ? data : '操作失败')
      ElMessage.error(message)
    }
  }
}

const shipOrder = (row) => {
  currentOrder.value = row
  showShipDialog.value = true
}

const confirmShip = async () => {
  if (!shipForm.carrier || !shipForm.tracking_number) {
    ElMessage.warning('请填写完整的物流信息')
    return
  }
  if (!currentOrder.value) return

  try {
    shipping.value = true
    await adminApi.post(`/verified-orders/${currentOrder.value.id}/ship`, {
      carrier: shipForm.carrier,
      tracking_number: shipForm.tracking_number,
      note: shipForm.note
    })
    ElMessage.success('发货成功')
    showShipDialog.value = false
    resetShipForm()
    await loadOrders()
  } catch (error) {
    const data = error.response?.data
    const detail = data?.detail || data?.error
    const message = detail || (typeof data === 'string' ? data : '发货失败')
    ElMessage.error(message)
  } finally {
    shipping.value = false
  }
}

const completeOrder = async (row) => {
  try {
    await ElMessageBox.confirm('确认订单已完成（用户已收货）？', '确认操作', { type: 'warning' })
    await adminApi.post(`/verified-orders/${row.id}/complete`)
    ElMessage.success('操作成功')
    await loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      const data = error.response?.data
      const detail = data?.detail || data?.error
      const message = detail || (typeof data === 'string' ? data : '操作失败')
      ElMessage.error(message)
    }
  }
}

const cancelOrder = async (row) => {
  try {
    await ElMessageBox.confirm('确认取消订单？', '确认操作', { type: 'warning' })
    await adminApi.post(`/verified-orders/${row.id}/cancel`)
    ElMessage.success('订单已取消')
    await loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      const data = error.response?.data
      const detail = data?.detail || data?.error
      const message = detail || (typeof data === 'string' ? data : '操作失败')
      ElMessage.error(message)
    }
  }
}

const resetShipForm = () => {
  shipForm.carrier = ''
  shipForm.tracking_number = ''
  shipForm.note = ''
  currentOrder.value = null
}

const handleOrderUpdated = () => {
  detailDialogVisible.value = false
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
  search.value = ''
  handleSearch()
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
.verified-order-management {
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
.table-card {
  border-radius: 10px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 18px;
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

.price {
  font-weight: 700;
  color: #f56c6c;
}

.text-sub {
  color: #666;
  font-size: 12px;
}

.text-muted {
  color: #909399;
}
</style>





