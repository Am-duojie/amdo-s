<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">支付订单管理</h2>
    </div>
    
    <div style="display:flex;gap:8px;margin-bottom:16px">
      <el-select v-model="status" placeholder="订单状态" style="width:180px">
        <el-option label="全部" value="" />
        <el-option label="待付款" value="pending" />
        <el-option label="已付款" value="paid" />
        <el-option label="已发货" value="shipped" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
    </div>
    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="订单ID" width="100" />
      <el-table-column prop="product" label="商品" min-width="200" />
      <el-table-column prop="buyer" label="买家" width="160" />
      <el-table-column prop="total_price" label="金额" width="120">
        <template #default="{ row }">
          ¥{{ row.total_price }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="350">
        <template #default="{row}">
          <el-button v-if="hasPerm('payment:view')" size="small" @click="query(row)">查询支付</el-button>
          <el-button v-if="hasPerm('payment:write') && row.status === 'paid'" size="small" type="danger" @click="refund(row)">退款</el-button>
          <el-button v-if="hasPerm('order:ship') && row.status === 'paid'" size="small" type="primary" @click="openShipDialog(row)">发货</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
      <el-pagination 
        v-model:current-page="pagination.current" 
        :total="pagination.total" 
        :page-size="pagination.pageSize" 
        layout="prev, pager, next, total" 
        @current-change="handlePageChange" 
      />
    </div>

    <el-dialog v-model="shipDialogVisible" title="发货信息" width="500px">
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="物流公司" required>
          <el-input v-model="shipForm.carrier" placeholder="请输入物流公司名称" />
        </el-form-item>
        <el-form-item label="运单号" required>
          <el-input v-model="shipForm.tracking_number" placeholder="请输入运单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="shipping" @click="confirmShip">确认发货</el-button>
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

const items = ref([])
const pagination = ref({ current: 1, pageSize: 10, total: 0 })
const status = ref('')
const shipDialogVisible = ref(false)
const shipping = ref(false)
const currentShipOrder = ref(null)

const shipForm = reactive({
  carrier: '',
  tracking_number: ''
})
const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    paid: 'success',
    shipped: 'primary',
    completed: 'success',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待付款',
    paid: '已付款',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

const load = async () => {
  try {
    const res = await adminApi.get('/payment/orders', { 
      params: { 
        page: pagination.value.current, 
        page_size: pagination.value.pageSize, 
        status: status.value 
      } 
    })
    items.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  }
}
const handlePageChange = () => load()
const query = async (row) => {
  try {
    const res = await adminApi.post(`/payment/order/${row.id}/query`)
    const ok = res.data?.success
    if (ok && res.data.result) {
      ElMessage.success(`查询成功: ${JSON.stringify(res.data.result)}`)
    } else {
      ElMessage.error('查询失败')
    }
  } catch (error) {
    ElMessage.error('查询失败')
  }
}

const refund = async (row) => {
  try {
    await ElMessageBox.confirm(`确认退款订单 #${row.id} 金额 ￥${row.total_price}?`, '提示', {
      type: 'warning'
    })
    const res = await adminApi.post(`/payment/order/${row.id}/refund`)
    const ok = res.data?.success
    ElMessage[ok ? 'success' : 'error'](ok ? '退款成功' : '退款失败')
    if (ok) await load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('退款失败')
    }
  }
}
const openShipDialog = (row) => {
  currentShipOrder.value = row
  shipForm.carrier = ''
  shipForm.tracking_number = ''
  shipDialogVisible.value = true
}

const confirmShip = async () => {
  if (!shipForm.carrier || !shipForm.tracking_number) {
    ElMessage.warning('请填写完整的发货信息')
    return
  }
  if (!currentShipOrder.value) return
  
  shipping.value = true
  try {
    const res = await adminApi.post(`/payment/order/${currentShipOrder.value.id}/ship`, shipForm)
    const ok = res.data?.success
    if (ok) {
      ElMessage.success('发货成功')
      shipDialogVisible.value = false
      await load()
    } else {
      ElMessage.error('发货失败')
    }
  } catch (error) {
    ElMessage.error('发货失败')
  } finally {
    shipping.value = false
  }
}

onMounted(load)
</script>

