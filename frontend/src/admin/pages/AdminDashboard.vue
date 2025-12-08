<template>
  <div class="admin-dashboard admin-page">
    <div class="dash-header admin-section-header">
      <div>
        <div class="admin-section-title">
          <el-icon><Odometer /></el-icon>
          <span>全局总览</span>
        </div>
        <div class="admin-section-desc">覆盖回收、官方验、易淘三条业务的核心指标与待办</div>
      </div>
      <div class="header-actions">
        <el-tag type="info" effect="plain" v-if="lastUpdated">
          上次更新：{{ formatDateTime(lastUpdated) }}
        </el-tag>
        <el-button :loading="loading" type="primary" @click="loadDashboard">刷新数据</el-button>
      </div>
    </div>

    <!-- 关键指标 -->
<el-row :gutter="16" class="metric-row">
  <el-col :span="6" v-for="item in metricCards" :key="item.key">
    <el-card shadow="hover" class="admin-card metric-card">
      <div class="metric-top">
        <div class="metric-title">{{ item.title }}</div>
        <el-tag size="small" :type="item.tagType" effect="dark">{{ item.badge }}</el-tag>
      </div>
      <div class="metric-value">{{ item.display }}</div>
      <div class="metric-hint">
        <el-icon><Clock /></el-icon>
        <span>{{ item.desc }}</span>
      </div>
      <div class="metric-icon" :style="{ background: item.bg }">
        <el-icon :size="26">
          <component :is="item.icon" />
        </el-icon>
      </div>
    </el-card>
  </el-col>
</el-row>

    <!-- 待办与风险 -->
    <el-row :gutter="16" class="section-row">
      <el-col :span="8">
        <el-card shadow="hover" class="admin-card">
          <template #header>
            <div class="section-title">
              <span>回收待办</span>
              <el-tag size="small" type="warning" effect="plain">回收订单</el-tag>
            </div>
          </template>
          <div class="todo-list">
            <div class="todo-item">
              <div class="todo-label">待质检</div>
              <el-tag type="warning">{{ counts.recyclePendingInspection }}</el-tag>
              <el-button text type="primary" @click="go('/admin/inspection-orders')">去处理</el-button>
            </div>
            <div class="todo-item">
              <div class="todo-label">已完成待打款</div>
              <el-tag type="danger">{{ counts.recyclePendingPayment }}</el-tag>
              <el-button text type="primary" @click="go('/admin/inspection-orders')">去打款</el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="admin-card">
          <template #header>
            <div class="section-title">
              <span>官方验待办</span>
              <el-tag size="small" type="success" effect="plain">官方验</el-tag>
            </div>
          </template>
          <div class="todo-list">
            <div class="todo-item">
              <div class="todo-label">待审核商品</div>
              <el-tag type="warning">{{ counts.verifiedPendingAudit }}</el-tag>
              <el-button text type="primary" @click="go('/admin/verified-products')">去审核</el-button>
            </div>
            <div class="todo-item">
              <div class="todo-label">已付款待发货</div>
              <el-tag type="primary">{{ counts.verifiedPendingShipment }}</el-tag>
              <el-button text type="primary" @click="go('/admin/verified-orders')">去发货</el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="admin-card">
          <template #header>
            <div class="section-title">
              <span>易淘待办 / 风险</span>
              <el-tag size="small" type="info" effect="plain">二手交易</el-tag>
            </div>
          </template>
          <div class="todo-list">
            <div class="todo-item">
              <div class="todo-label">待发货（买家已付款）</div>
              <el-tag type="primary">{{ counts.secondhandPendingShipment }}</el-tag>
              <el-button text type="primary" @click="go('/admin/secondhand-orders')">去发货</el-button>
            </div>
            <div class="todo-item">
              <div class="todo-label">分账失败待重试</div>
              <el-tag type="danger">{{ counts.secondhandSettlementFailed }}</el-tag>
              <el-button text type="primary" @click="go('/admin/secondhand-orders')">去重试</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷入口与说明 -->
    <el-row :gutter="16" class="section-row">
      <el-col :span="16">
        <el-card shadow="hover" class="admin-card">
          <template #header>
            <div class="section-title">
              <span>快捷入口</span>
              <el-tag size="small" type="info" effect="plain">常用</el-tag>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" plain @click="go('/admin/recycle-orders')">回收订单</el-button>
            <el-button type="primary" plain @click="go('/admin/inspection-orders')">回收质检</el-button>
            <el-button type="primary" plain @click="go('/admin/verified-products')">官方验商品</el-button>
            <el-button type="primary" plain @click="go('/admin/verified-orders')">官方验订单</el-button>
            <el-button type="primary" plain @click="go('/admin/secondhand-orders')">易淘订单</el-button>
            <el-button type="primary" plain @click="go('/admin/payments')">支付/退款</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="admin-card">
          <template #header>
            <div class="section-title">
              <span>操作提示</span>
              <el-tag size="small" type="warning" effect="plain">提醒</el-tag>
            </div>
          </template>
          <div class="hint-list">
            <div class="hint-item">
              <el-icon><WarningFilled /></el-icon>
              官方验发货前核对地址与联系方式，避免售后纠纷。
            </div>
            <div class="hint-item">
              <el-icon><WarningFilled /></el-icon>
              分账失败优先检查卖家支付宝绑定或交易号有效性。
            </div>
            <div class="hint-item">
              <el-icon><WarningFilled /></el-icon>
              回收打款需确认终检价格，必要时电话复核。
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import {
  Odometer,
  ShoppingBag,
  DocumentChecked,
  Goods,
  Money,
  Clock,
  Tickets,
  ShoppingCart,
  CreditCard,
  WarningFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const timer = ref(null)
const lastUpdated = ref(null)

const metrics = ref({
  todayInspection: 0,
  todaySecondhand: 0,
  verifiedOrdersPaidToday: 0,
  verifiedOrdersCompletedToday: 0,
  gmvToday: 0
})

const counts = ref({
  recyclePendingInspection: 0,
  recyclePendingPayment: 0,
  verifiedPendingAudit: 0,
  verifiedPendingShipment: 0,
  secondhandPendingShipment: 0,
  secondhandSettlementFailed: 0
})

const fetchCount = async (url, params) => {
  try {
    const res = await adminApi.get(url, { params: { page_size: 1, ...params } })
    return res.data?.count || 0
  } catch (e) {
    return 0
  }
}

const loadDashboard = async () => {
  loading.value = true
  try {
    const res = await adminApi.get('/dashboard/metrics')
    metrics.value = { ...metrics.value, ...res.data }

    const [
      recycleInspection,
      recyclePayment,
      verifiedAudit,
      verifiedShip,
      secondhandShip,
      settlementFailed
    ] = await Promise.all([
      fetchCount('/inspection-orders', { status: 'shipped' }),
      fetchCount('/inspection-orders', { status: 'completed' }),
      fetchCount('/verified-listings', { status: 'pending' }),
      fetchCount('/verified-orders', { status: 'paid' }),
      fetchCount('/payment/orders', { status: 'paid' }),
      fetchCount('/payment/orders', { settlement_status: 'failed' })
    ])

    counts.value = {
      recyclePendingInspection: recycleInspection,
      recyclePendingPayment: recyclePayment,
      verifiedPendingAudit: verifiedAudit,
      verifiedPendingShipment: verifiedShip,
      secondhandPendingShipment: secondhandShip,
      secondhandSettlementFailed: settlementFailed
    }

    lastUpdated.value = new Date()
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const go = (path) => router.push(path)

const formatMoney = (amount) => {
  if (!amount) return '0.00'
  const num = Number(amount)
  if (Number.isNaN(num)) return '0.00'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDateTime = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const metricCards = computed(() => [
  {
    key: 'gmv',
    title: '今日 GMV',
    display: `¥${formatMoney(metrics.value.gmvToday)}`,
    desc: '含易淘、官方验已付款订单',
    badge: '交易',
    tagType: 'primary',
    bg: 'rgba(64, 158, 255, 0.20)',
    icon: Money
  },
  {
    key: 'secondhand',
    title: '今日易淘订单',
    display: metrics.value.todaySecondhand || 0,
    desc: '买家已付款订单数',
    badge: '易淘',
    tagType: 'info',
    bg: 'rgba(96, 165, 250, 0.18)',
    icon: CreditCard
  },
  {
    key: 'verified',
    title: '今日官方验订单',
    display: metrics.value.verifiedOrdersPaidToday || 0,
    desc: '已付款（含待发货）',
    badge: '官方验',
    tagType: 'success',
    bg: 'rgba(56, 189, 248, 0.18)',
    icon: ShoppingCart
  },
  {
    key: 'recycle',
    title: '今日回收订单',
    display: metrics.value.todayInspection || 0,
    desc: '新创建回收/质检订单',
    badge: '回收',
    tagType: 'warning',
    bg: 'rgba(129, 140, 248, 0.18)',
    icon: Tickets
  }
])

onMounted(() => {
  loadDashboard()
  timer.value = setInterval(loadDashboard, 60000)
})

onUnmounted(() => {
  if (timer.value) clearInterval(timer.value)
})
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dash-header .header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-row {
  margin-top: 4px;
}

.metric-card {
  position: relative;
  overflow: hidden;
  min-height: 140px;
}

.metric-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.metric-title {
  font-weight: 700;
  color: #1f2937;
}

.metric-value {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 6px;
}

.metric-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 13px;
}

.metric-icon {
  position: absolute;
  right: 14px;
  bottom: 14px;
  width: 54px;
  height: 54px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0f172a;
  opacity: 0.22;
}

.section-row {
  margin-top: 4px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  background: #f9fafb;
  border-radius: 10px;
}

.todo-label {
  font-weight: 600;
  color: #374151;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hint-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.hint-item {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #334155;
  background: #ecf5ff;
  border: 1px solid #d9ecff;
  border-radius: 10px;
  padding: 10px 12px;
}
</style>
