<template>
  <div class="statistics-page">
    <div class="page-header">
      <h2 class="page-title">统计分析</h2>
      <div class="page-subtitle">回收 / 官方验 / 易淘（三线）核心指标与趋势</div>
    </div>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>日期范围</span>
          </template>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="loadStatistics"
            style="width: 100%"
          />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快捷选择</span>
          </template>
          <div class="quick-date-buttons">
            <el-button @click="setDateRange('today')">今天</el-button>
            <el-button @click="setDateRange('week')">最近7天</el-button>
            <el-button @click="setDateRange('month')">最近30天</el-button>
            <el-button @click="setDateRange('all')">全部</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-label">回收订单总数</div>
          <div class="stat-value">{{ stats.recycleOrdersTotal || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-label">已完成回收</div>
          <div class="stat-value">{{ stats.recycleCompleted || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-label">官方验订单总数</div>
          <div class="stat-value">{{ stats.verifiedOrdersTotal || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-label">官方验 GMV</div>
          <div class="stat-value">￥{{ formatMoney(stats.verifiedGMV ?? stats.totalGMV ?? 0) }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-label">易淘订单总数</div>
          <div class="stat-value">{{ stats.secondhandOrdersTotal || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-label">总 GMV（含易淘）</div>
          <div class="stat-value">￥{{ formatMoney(stats.totalGMVAll ?? stats.totalGMV ?? 0) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>订单趋势</span>
          <div class="header-right">
            <el-tag v-if="stats.startDate && stats.endDate" type="info" effect="plain">
              {{ stats.startDate }} ～ {{ stats.endDate }}（{{ stats.days || 0 }}天）
            </el-tag>
          </div>
        </div>
      </template>
      <div ref="chartEl" class="trend-chart"></div>
    </el-card>

    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>订单状态漏斗</span>
          <div class="header-right">
            <el-segmented v-model="activeFunnelKey" :options="funnelOptions" @change="renderFunnel" />
          </div>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col :span="14">
          <div ref="funnelChartEl" class="funnel-chart"></div>
        </el-col>
        <el-col :span="10">
          <el-table :data="funnelTable" border size="small">
            <el-table-column prop="label" label="状态" />
            <el-table-column prop="count" label="数量" width="110" />
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>维度拆分（TopN）</span>
          <div class="header-right breakdown-controls">
            <el-select v-model="breakdownType" style="width: 220px" @change="loadStatistics">
              <el-option label="回收-品牌 Top" value="recycle_brand" />
              <el-option label="回收-机型 Top" value="recycle_model" />
              <el-option label="库存-品牌 Top" value="inventory_brand" />
              <el-option label="库存-机型 Top" value="inventory_model" />
            </el-select>
            <el-input-number
              v-model="topN"
              :min="1"
              :max="50"
              controls-position="right"
              @change="loadStatistics"
            />
          </div>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col :span="12">
          <div ref="breakdownChartEl" class="breakdown-chart"></div>
        </el-col>
        <el-col :span="12">
          <el-table :data="breakdownRows" border size="small">
            <el-table-column prop="dim" label="维度" min-width="160" />
            <el-table-column prop="count" label="数量" width="90" />
            <el-table-column v-if="breakdownType.startsWith('recycle_')" prop="completed" label="完成" width="90" />
            <el-table-column v-if="breakdownType.startsWith('recycle_')" prop="disputes" label="异议" width="90" />
            <el-table-column v-if="breakdownType.startsWith('inventory_')" prop="ready" label="待上架" width="90" />
            <el-table-column v-if="breakdownType.startsWith('inventory_')" prop="listed" label="在售" width="80" />
            <el-table-column v-if="breakdownType.startsWith('inventory_')" prop="locked" label="锁定" width="80" />
            <el-table-column v-if="breakdownType.startsWith('inventory_')" prop="sold" label="已售" width="80" />
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>详细统计</span>
          <el-button type="primary" :disabled="statsTable.length === 0" @click="exportStatistics">导出 CSV</el-button>
        </div>
      </template>
      <el-table :data="statsTable" border>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="recycleOrders" label="回收订单" width="100" />
        <el-table-column prop="recycleCompleted" label="回收完成" width="100" />
        <el-table-column prop="recycleDisputes" label="价格异议" width="100" />
        <el-table-column prop="verifiedOrders" label="官方验订单" width="120" />
        <el-table-column prop="secondhandOrders" label="易淘订单" width="100" />
        <el-table-column prop="secondhandSettlementFailed" label="分账失败" width="100" />
        <el-table-column prop="gmv" label="GMV（含易淘）" width="160">
          <template #default="{ row }">￥{{ formatMoney(row.gmv) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const dateRange = ref([])
const stats = ref({})
const statsTable = ref([])

const breakdownType = ref('recycle_brand')
const topN = ref(10)

const chartEl = ref(null)
const funnelChartEl = ref(null)
const breakdownChartEl = ref(null)

const charts = {
  trend: null,
  funnel: null,
  breakdown: null,
}

const activeFunnelKey = ref('recycle')
const funnelOptions = [
  { label: '回收', value: 'recycle' },
  { label: '官方验', value: 'verified' },
  { label: '易淘', value: 'secondhand' },
]

const setDateRange = (type) => {
  const today = new Date()
  const formatDate = (d) => d.toISOString().split('T')[0]

  switch (type) {
    case 'today':
      dateRange.value = [formatDate(today), formatDate(today)]
      break
    case 'week': {
      const weekAgo = new Date(today)
      weekAgo.setDate(today.getDate() - 7)
      dateRange.value = [formatDate(weekAgo), formatDate(today)]
      break
    }
    case 'month': {
      const monthAgo = new Date(today)
      monthAgo.setDate(today.getDate() - 30)
      dateRange.value = [formatDate(monthAgo), formatDate(today)]
      break
    }
    case 'all':
      dateRange.value = []
      break
  }
  loadStatistics()
}

const formatMoney = (amount) => {
  if (!amount) return '0.00'
  const num = Number(amount)
  if (Number.isNaN(num)) return '0.00'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const renderChart = (trend) => {
  if (!chartEl.value) return
  if (!charts.trend) charts.trend = echarts.init(chartEl.value)

  const x = trend.map((r) => r.date)
  const recycleOrders = trend.map((r) => Number(r.recycleOrders || 0))
  const verifiedOrders = trend.map((r) => Number(r.verifiedOrders || 0))
  const secondhandOrders = trend.map((r) => Number(r.secondhandOrders || 0))
  const gmvAll = trend.map((r) => Number(r.verifiedGMV || 0) + Number(r.secondhandGMV || 0))

  charts.trend.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter: (v) => (typeof v === 'number' ? v.toLocaleString('zh-CN') : v),
    },
    legend: { top: 0 },
    grid: { left: 20, right: 20, bottom: 20, top: 40, containLabel: true },
    xAxis: { type: 'category', data: x, axisLabel: { rotate: x.length > 14 ? 35 : 0 } },
    yAxis: [
      { type: 'value', name: '订单数', minInterval: 1 },
      {
        type: 'value',
        name: 'GMV',
        axisLabel: { formatter: (v) => `￥${Number(v).toLocaleString('zh-CN')}` },
      },
    ],
    series: [
      { name: '回收订单', type: 'bar', stack: 'orders', data: recycleOrders },
      { name: '官方验订单', type: 'bar', stack: 'orders', data: verifiedOrders },
      { name: '易淘订单', type: 'bar', stack: 'orders', data: secondhandOrders },
      { name: 'GMV（含易淘）', type: 'line', yAxisIndex: 1, smooth: true, data: gmvAll },
    ],
  })
}

const funnelTable = computed(() => {
  const funnels = stats.value?.funnels || {}
  const list = Array.isArray(funnels?.[activeFunnelKey.value]) ? funnels[activeFunnelKey.value] : []
  return list.map((r) => ({ label: r.label, count: r.count }))
})

const breakdownRows = computed(() => {
  const b = stats.value?.breakdown
  if (!b || !Array.isArray(b.rows)) return []
  return b.rows
})

const renderFunnel = () => {
  const funnels = stats.value?.funnels || {}
  const list = Array.isArray(funnels?.[activeFunnelKey.value]) ? funnels[activeFunnelKey.value] : []
  if (!funnelChartEl.value) return
  if (!charts.funnel) charts.funnel = echarts.init(funnelChartEl.value)

  const data = list.map((r) => ({ name: r.label, value: Number(r.count || 0) }))
  charts.funnel.setOption({
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'funnel',
        sort: 'none',
        gap: 2,
        top: 10,
        bottom: 10,
        left: '8%',
        width: '84%',
        label: { formatter: '{b}: {c}' },
        data,
      },
    ],
  })
}

const renderBreakdown = () => {
  const rows = breakdownRows.value
  if (!breakdownChartEl.value) return
  if (!charts.breakdown) charts.breakdown = echarts.init(breakdownChartEl.value)

  const dims = rows.map((r) => r.dim)
  const counts = rows.map((r) => Number(r.count || 0))

  charts.breakdown.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 10, right: 10, top: 10, bottom: 10, containLabel: true },
    xAxis: { type: 'value', minInterval: 1 },
    yAxis: { type: 'category', data: dims, axisLabel: { interval: 0 } },
    series: [{ type: 'bar', data: counts, itemStyle: { color: '#409EFF' } }],
  })
}

const loadStatistics = async () => {
  try {
    const params = {
      include: 'trend,funnel,breakdown',
      breakdown: breakdownType.value,
      top_n: topN.value,
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const res = await adminApi.get('/statistics', { params })
    const data = res.data || {}
    stats.value = data

    const trend = Array.isArray(data.trend) ? data.trend : []
    statsTable.value = trend.map((r) => ({
      date: r.date,
      recycleOrders: r.recycleOrders || 0,
      recycleCompleted: r.recycleCompleted || 0,
      recycleDisputes: r.recycleDisputes || 0,
      verifiedOrders: r.verifiedOrders || 0,
      secondhandOrders: r.secondhandOrders || 0,
      secondhandSettlementFailed: r.secondhandSettlementFailed || 0,
      gmv: Number(r.verifiedGMV || 0) + Number(r.secondhandGMV || 0),
    }))

    await nextTick()
    renderChart(trend)
    renderFunnel()
    renderBreakdown()
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

const exportStatistics = () => {
  if (!statsTable.value.length) return

  const headers = [
    '日期',
    '回收订单',
    '回收完成',
    '价格异议',
    '官方验订单',
    '易淘订单',
    '分账失败',
    'GMV（含易淘）',
  ]

  const rows = statsTable.value.map((r) => ([
    r.date,
    r.recycleOrders,
    r.recycleCompleted,
    r.recycleDisputes,
    r.verifiedOrders,
    r.secondhandOrders,
    r.secondhandSettlementFailed,
    r.gmv,
  ]))

  const csvEscape = (v) => {
    const s = String(v ?? '')
    if (s.includes('"') || s.includes(',') || s.includes('\n')) return `"${s.replaceAll('"', '""')}"`
    return s
  }

  const csv = [headers, ...rows].map((line) => line.map(csvEscape).join(',')).join('\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  const start = stats.value.startDate || (dateRange.value?.[0] || 'start')
  const end = stats.value.endDate || (dateRange.value?.[1] || 'end')
  a.href = url
  a.download = `statistics_${start}_${end}.csv`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

const onResize = () => {
  if (charts.trend) charts.trend.resize()
  if (charts.funnel) charts.funnel.resize()
  if (charts.breakdown) charts.breakdown.resize()
}

onMounted(() => {
  setDateRange('month')
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  if (charts.trend) charts.trend.dispose()
  if (charts.funnel) charts.funnel.dispose()
  if (charts.breakdown) charts.breakdown.dispose()
})
</script>

<style scoped>
.statistics-page {
  padding: 0;
}

.page-header {
  margin-bottom: 16px;
}

.page-title {
  margin: 0 0 6px 0;
}

.page-subtitle {
  color: #909399;
  font-size: 13px;
}

.stat-card {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.quick-date-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.trend-chart {
  height: 320px;
  width: 100%;
}

.funnel-chart {
  height: 320px;
  width: 100%;
}

.breakdown-chart {
  height: 360px;
  width: 100%;
}

.breakdown-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
