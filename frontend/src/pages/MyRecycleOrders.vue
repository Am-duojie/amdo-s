<template>
  <div class="my-recycle-orders">
    <div class="page-header">
      <h1 class="page-title">♻️ 我的回收订单</h1>
      <el-button type="primary" @click="goToCreateOrder">
        <el-icon><Plus /></el-icon>
        创建回收订单
      </el-button>
    </div>

    <!-- 状态筛选 -->
    <div class="status-filter">
      <el-radio-group v-model="selectedStatus" @change="loadOrders">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="pending">待估价</el-radio-button>
        <el-radio-button label="quoted">已估价</el-radio-button>
        <el-radio-button label="confirmed">已确认</el-radio-button>
        <el-radio-button label="shipped">已寄出</el-radio-button>
        <el-radio-button label="inspected">已检测</el-radio-button>
        <el-radio-button label="completed">已完成</el-radio-button>
        <el-radio-button label="cancelled">已取消</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 订单列表 -->
    <div class="orders-container" v-loading="loading">
      <div v-if="orders.length === 0" class="empty-state">
        <el-empty description="暂无回收订单">
          <el-button type="primary" @click="goToCreateOrder">创建回收订单</el-button>
        </el-empty>
      </div>

      <div v-else class="orders-list">
        <div 
          v-for="order in orders" 
          :key="order.id"
          class="order-card"
          @click="goToDetail(order.id)"
        >
          <div class="order-header">
            <div class="order-info">
              <span class="order-id">订单号：{{ order.id }}</span>
              <span class="order-device">{{ order.brand }} {{ order.model }}</span>
            </div>
            <el-tag :type="getStatusType(order.status)" size="large">
              {{ getStatusText(order.status) }}
            </el-tag>
          </div>

          <div class="order-body">
            <div class="order-details">
              <div class="detail-item">
                <span class="label">设备类型：</span>
                <span class="value">{{ order.device_type }}</span>
              </div>
              <div class="detail-item" v-if="order.storage">
                <span class="label">存储容量：</span>
                <span class="value">{{ order.storage }}</span>
              </div>
              <div class="detail-item">
                <span class="label">成色：</span>
                <span class="value">{{ getConditionText(order.condition) }}</span>
              </div>
              <div class="detail-item" v-if="order.estimated_price">
                <span class="label">预估价格：</span>
                <span class="value price">¥{{ order.estimated_price }}</span>
              </div>
              <div class="detail-item" v-if="order.final_price">
                <span class="label">最终价格：</span>
                <span class="value price final">¥{{ order.final_price }}</span>
              </div>
            </div>
          </div>

          <div class="order-footer">
            <div class="order-time">
              <el-icon><Clock /></el-icon>
              {{ formatDate(order.created_at) }}
            </div>
            <div class="order-actions">
              <el-button size="small" @click.stop="goToDetail(order.id)">
                查看详情
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="orders.length > 0">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadOrders"
        @current-change="loadOrders"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Clock } from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()

const loading = ref(false)
const selectedStatus = ref('all')
const orders = ref([])
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const statusMap = {
  pending: '待估价',
  quoted: '已估价',
  confirmed: '已确认',
  shipped: '已寄出',
  inspected: '已检测',
  completed: '已完成',
  cancelled: '已取消'
}

const conditionMap = {
  new: '全新',
  like_new: '几乎全新',
  good: '良好',
  fair: '一般',
  poor: '较差'
}

const getStatusText = (status) => {
  return statusMap[status] || status
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    quoted: 'warning',
    confirmed: 'primary',
    shipped: '',
    inspected: 'success',
    completed: 'success',
    cancelled: 'danger'
  }
  return typeMap[status] || ''
}

const getConditionText = (condition) => {
  return conditionMap[condition] || condition
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    }
    if (selectedStatus.value !== 'all') {
      params.status = selectedStatus.value
    }

    const res = await api.get('/recycle-orders/', { params })
    
    if (res.data.results) {
      orders.value = res.data.results
      pagination.value.total = res.data.count || res.data.results.length
    } else {
      orders.value = Array.isArray(res.data) ? res.data : []
      pagination.value.total = orders.value.length
    }
  } catch (error) {
    console.error('加载订单失败:', error)
    ElMessage.error('加载订单失败，请稍后重试')
    orders.value = []
  } finally {
    loading.value = false
  }
}

const goToDetail = (orderId) => {
  router.push(`/recycle-order/${orderId}`)
}

const goToCreateOrder = () => {
  router.push('/recycle')
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.my-recycle-orders {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 200px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.status-filter {
  margin-bottom: 24px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.orders-container {
  min-height: 400px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.order-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.order-id {
  font-size: 14px;
  color: #999;
}

.order-device {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.order-body {
  margin-bottom: 16px;
}

.order-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-item .label {
  font-size: 14px;
  color: #666;
}

.detail-item .value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.detail-item .value.price {
  color: #ff6600;
  font-size: 16px;
}

.detail-item .value.price.final {
  color: #ff4444;
  font-size: 18px;
  font-weight: 700;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.order-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #999;
}

.order-actions {
  display: flex;
  gap: 8px;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .order-details {
    grid-template-columns: 1fr;
  }

  .order-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>


