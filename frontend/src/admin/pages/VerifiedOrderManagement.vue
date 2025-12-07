<template>
  <div class="verified-order-management">
    <div class="page-header">
      <h2>官方验订单管理</h2>
      <div class="header-actions">
        <el-select v-model="statusFilter" placeholder="筛选状态" style="width: 150px" clearable>
          <el-option label="全部" value="" />
          <el-option label="待付款" value="pending" />
          <el-option label="已付款" value="paid" />
          <el-option label="已发货" value="shipped" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
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
          <div style="font-weight: 500">{{ row.product?.title || '-' }}</div>
          <div v-if="row.product" style="color: #666; font-size: 12px; margin-top: 4px">
            {{ row.product.brand }} {{ row.product.model }}
          </div>
        </template>
      </el-table-column>
      <el-table-column label="买家" width="120">
        <template #default="{ row }">
          {{ row.buyer?.username || '-' }}
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
          <el-input v-model="shipForm.carrier" placeholder="请输入物流公司名称" />
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
import { ref, reactive, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminAuthStore } from '@/stores/adminAuth'
import VerifiedOrderDetail from './components/VerifiedOrderDetail.vue'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)

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

const markPaid = async (row) => {
  try {
    await ElMessageBox.confirm('确认标记订单为已付款？', '确认操作', { type: 'warning' })
    await adminApi.post(`/verified-orders/${row.id}/mark-paid`)
    ElMessage.success('操作成功')
    await loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
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
    ElMessage.error('发货失败')
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
      ElMessage.error('操作失败')
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
      ElMessage.error('操作失败')
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

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.verified-order-management {
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







