<template>
  <div class="admin-dashboard">
    <h2 style="margin-bottom: 20px">数据看板</h2>

    <!-- 关键指标 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon" style="background: #409eff">
            <el-icon :size="24"><ShoppingBag /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-label">今日回收订单</div>
            <div class="metric-value">{{ metrics.todayInspection }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon" style="background: #67c23a">
            <el-icon :size="24"><DocumentChecked /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-label">待审核商品</div>
            <div class="metric-value">{{ metrics.pendingAudit }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon" style="background: #e6a23c">
            <el-icon :size="24"><Goods /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-label">已发布官方验</div>
            <div class="metric-value">{{ metrics.verifiedPublished }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon" style="background: #f56c6c">
            <el-icon :size="24"><Money /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-label">今日GMV</div>
            <div class="metric-value">¥{{ formatMoney(metrics.gmvToday) }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 订单统计 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>官方验订单统计（今日）</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="已付款订单">
              {{ metrics.verifiedOrdersPaidToday }}
            </el-descriptions-item>
            <el-descriptions-item label="已完成订单">
              {{ metrics.verifiedOrdersCompletedToday }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>待处理任务</span>
          </template>
          <div class="pending-tasks">
            <div class="task-item">
              <span>待质检订单</span>
              <el-tag type="warning">{{ metrics.pendingInspection || 0 }}</el-tag>
            </div>
            <div class="task-item">
              <span>待发货订单</span>
              <el-tag type="primary">{{ metrics.pendingShipment || 0 }}</el-tag>
            </div>
            <div class="task-item">
              <span>待打款订单</span>
              <el-tag type="danger">{{ metrics.pendingPayment || 0 }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card>
      <template #header>
        <span>快捷操作</span>
      </template>
      <div class="quick-actions">
        <el-button type="primary" @click="$router.push('/admin/recycle-orders')">
          回收订单管理
        </el-button>
        <el-button type="success" @click="$router.push('/admin/verified-products')">
          官方验商品管理
        </el-button>
        <el-button type="warning" @click="$router.push('/admin/verified-orders')">
          官方验订单管理
        </el-button>
        <el-button @click="$router.push('/admin/secondhand-orders')">
          易淘订单管理
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import { ShoppingBag, DocumentChecked, Goods, Money } from '@element-plus/icons-vue'

const router = useRouter()

const metrics = ref({
  todayInspection: 0,
  pendingAudit: 0,
  verifiedPublished: 0,
  verifiedOrdersPaidToday: 0,
  verifiedOrdersCompletedToday: 0,
  gmvToday: 0,
  pendingInspection: 0,
  pendingShipment: 0,
  pendingPayment: 0
})

const loadMetrics = async () => {
  try {
    const res = await adminApi.get('/dashboard/metrics')
    metrics.value = { ...metrics.value, ...res.data }
    
    // 加载额外的统计数据
    try {
      // 待质检订单（状态为shipped的回收订单）
      const inspectionRes = await adminApi.get('/inspection-orders', {
        params: { status: 'shipped', page_size: 1 }
      })
      metrics.value.pendingInspection = inspectionRes.data?.count || 0
      
      // 待发货订单（状态为paid的官方验订单）
      const shipRes = await adminApi.get('/verified-orders', {
        params: { status: 'paid', page_size: 1 }
      })
      metrics.value.pendingShipment = shipRes.data?.count || 0
      
      // 待打款订单（状态为completed的回收订单，有final_price但未打款）
      const paymentRes = await adminApi.get('/inspection-orders', {
        params: { status: 'completed', page_size: 1 }
      })
      metrics.value.pendingPayment = paymentRes.data?.count || 0
    } catch (e) {
      // 忽略额外统计的错误
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const formatMoney = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

onMounted(() => {
  loadMetrics()
  // 每30秒刷新一次数据
  setInterval(loadMetrics, 30000)
})
</script>

<style scoped>
.admin-dashboard {
  padding: 0;
}

.metric-card {
  position: relative;
  overflow: hidden;
}

.metric-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0.2;
}

.metric-content {
  position: relative;
  z-index: 1;
}

.metric-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 12px;
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.pending-tasks {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
