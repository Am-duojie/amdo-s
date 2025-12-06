<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">回收订单管理</h2>
    </div>
    
    <!-- 筛选条件 -->
    <div style="margin-bottom: 16px; display: flex; gap: 12px; flex-wrap: wrap">
      <el-input
        v-model="search"
        placeholder="搜索订单号、用户、品牌、型号"
        style="width: 280px"
        clearable
        @keyup.enter="load"
        @clear="load"
      />
      <el-select v-model="statusFilter" placeholder="订单状态" style="width: 150px" clearable @change="load">
        <el-option label="全部" value="" />
        <el-option label="待估价" value="pending" />
        <el-option label="已估价" value="quoted" />
        <el-option label="已确认" value="confirmed" />
        <el-option label="已寄出" value="shipped" />
        <el-option label="已检测" value="inspected" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-select v-model="paymentFilter" placeholder="打款状态" style="width: 120px" clearable @change="load">
        <el-option label="全部" value="" />
        <el-option label="待打款" value="pending" />
        <el-option label="已打款" value="paid" />
        <el-option label="打款失败" value="failed" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
      <el-button @click="exportData">导出</el-button>
    </div>
    
    <!-- 订单列表 -->
    <el-table :data="items" style="width:100%" v-loading="loading">
      <el-table-column prop="id" label="订单号" width="100" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column label="设备信息" min-width="200">
        <template #default="{ row }">
          <div>{{ row.brand }} {{ row.model }}</div>
          <div style="color: #909399; font-size: 12px">{{ row.device_type }} / {{ row.storage || '-' }} / {{ getConditionText(row.condition) }}</div>
        </template>
      </el-table-column>
      <el-table-column label="价格信息" width="150">
        <template #default="{ row }">
          <div v-if="row.estimated_price" style="font-size: 12px; color: #909399">
            预估: ¥{{ row.estimated_price }}
          </div>
          <div v-if="row.final_price" style="font-weight: bold; color: #f56c6c">
            最终: ¥{{ row.total_price || row.final_price }}
          </div>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="140">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          <el-tag 
            v-if="row.payment_status" 
            :type="getPaymentStatusType(row.payment_status)" 
            size="small" 
            style="margin-left: 4px"
          >
            {{ getPaymentStatusText(row.payment_status) }}
          </el-tag>
          <el-tag v-if="row.price_dispute" type="warning" size="small" style="margin-left: 4px">价格异议</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="物流" width="150">
        <template #default="{ row }">
          <div v-if="row.shipping_carrier">{{ row.shipping_carrier }}</div>
          <div v-if="row.tracking_number" style="font-size: 12px; color: #909399">{{ row.tracking_number }}</div>
          <div v-else style="color: #909399; font-size: 12px">-</div>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{row}">
          <el-button size="small" type="primary" @click="open(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'

const router = useRouter()
const items = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const paymentFilter = ref('')
const pagination = reactive({ current: 1, pageSize: 20, total: 0 })

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

const getPaymentStatusText = (status) => paymentStatusMap[status]?.text || ''
const getPaymentStatusType = (status) => paymentStatusMap[status]?.type || 'info'

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const open = (row) => { 
  router.push(`/admin/inspection-orders/${row.id}`) 
}

const load = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    if (search.value) params.search = search.value
    if (statusFilter.value) params.status = statusFilter.value
    if (paymentFilter.value) params.payment_status = paymentFilter.value
    
    const res = await adminApi.get('/inspection-orders', { params })
    items.value = res.data?.results || []
    pagination.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = () => load()
const handleSizeChange = () => {
  pagination.current = 1
  load()
}

const exportData = () => {
  ElMessage.info('导出功能开发中')
}

onMounted(load)
</script>

<style scoped>
.el-table {
  font-size: 13px;
}
</style>
