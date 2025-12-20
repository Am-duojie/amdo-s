<template>
  <div class="statistics-page">
    <div class="page-header">
      <h2 class="page-title">统计分析</h2>
      <div class="page-subtitle">回收 / 官方验 / 易淘（三线）核心指标与趋势</div>
    </div>

    <el-card class="filters-card" style="margin-bottom: 14px">
      <template #header>
        <div class="filters-header">
          <div class="filters-title">筛选</div>
          <el-popover placement="bottom-end" :width="360" trigger="hover">
            <template #reference>
              <el-button class="rule-button" size="small" round>统计规则</el-button>
            </template>
            <div class="methodology-body">
              <div>时间口径：按创建时间（<code>created_at</code>）统计</div>
              <div>订单数/趋势：{{ excludeCancelledOrders ? '默认排除已取消（cancelled）' : '包含已取消（cancelled）' }}</div>
              <div>成交 GMV：仅统计已付款/已完成（<code>paid</code>/<code>completed</code>）</div>
              <div>下单 GMV：统计全部订单（{{ includeCancelledInOrderGMV ? '包含已取消（cancelled）' : '默认不含已取消（cancelled）' }}）</div>
              <div>漏斗：始终展示全量状态分布（含已取消），便于解释转化与取消原因</div>
              <div>履约/异常/SLA/调价分布：基于回收订单筛选结果（recycle_statuses）</div>
              <div>易淘价格分布：基于已付款/已完成订单统计</div>
            </div>
          </el-popover>
        </div>
      </template>

      <el-row :gutter="16" class="filters-grid">
        <el-col :span="10">
          <div class="filter-block">
            <div class="filter-block-title">日期范围</div>
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
          </div>
        </el-col>

        <el-col :span="7">
          <div class="filter-block">
            <div class="filter-block-title">快捷日期</div>
            <el-segmented
              v-model="quickDate"
              :options="quickDateOptions"
              @change="onQuickDateChange"
            />
          </div>
        </el-col>

        <el-col :span="7">
          <div class="filter-block">
            <div class="filter-block-title">口径开关</div>
            <div class="toggle-list">
              <div class="toggle-item">
                <div class="toggle-text">订单数排除已取消</div>
                <el-switch v-model="excludeCancelledOrders" @change="loadStatistics" />
              </div>
              <div class="toggle-item">
                <div class="toggle-text">下单GMV包含已取消</div>
                <el-switch v-model="includeCancelledInOrderGMV" @change="loadStatistics" />
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-collapse class="advanced-collapse">
        <el-collapse-item title="高级：按状态过滤（影响趋势/汇总/维度拆分）">
          <el-row :gutter="16">
            <el-col :span="8">
              <div class="filter-block-title">回收状态</div>
              <el-select
                v-model="recycleStatuses"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                placeholder="全部"
                @change="loadStatistics"
                style="width: 100%"
              >
                <el-option
                  v-for="opt in recycleStatusOptions"
                  :key="opt.key"
                  :label="opt.label"
                  :value="opt.key"
                />
              </el-select>
            </el-col>
            <el-col :span="8">
              <div class="filter-block-title">官方验订单状态</div>
              <el-select
                v-model="verifiedStatuses"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                placeholder="全部"
                @change="loadStatistics"
                style="width: 100%"
              >
                <el-option
                  v-for="opt in verifiedStatusOptions"
                  :key="opt.key"
                  :label="opt.label"
                  :value="opt.key"
                />
              </el-select>
            </el-col>
            <el-col :span="8">
              <div class="filter-block-title">易淘订单状态</div>
              <el-select
                v-model="secondhandStatuses"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                placeholder="全部"
                @change="loadStatistics"
                style="width: 100%"
              >
                <el-option
                  v-for="opt in secondhandStatusOptions"
                  :key="opt.key"
                  :label="opt.label"
                  :value="opt.key"
                />
              </el-select>
            </el-col>
          </el-row>
        </el-collapse-item>
      </el-collapse>
    </el-card>

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
          <div class="stat-label">成交 GMV（含易淘）</div>
          <div class="stat-value">￥{{ formatMoney(stats.totalGMVAllPaid ?? stats.totalGMVAll ?? 0) }}</div>
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
          <div class="stat-label">下单 GMV（含易淘）</div>
          <div class="stat-value">￥{{ formatMoney(stats.totalGMVAllAll ?? stats.totalGMVAll ?? 0) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="kpi-row">
      <el-col :span="8">
        <el-card class="kpi-card">
          <div class="kpi-title">回收完成率</div>
          <div class="kpi-value">{{ formatRate(recycleCompletionRate) }}</div>
          <div class="kpi-meta">{{ recycleCompletedCount }} / {{ recycleTotalAllCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="kpi-card">
          <div class="kpi-title">回收取消率</div>
          <div class="kpi-value">{{ formatRate(recycleCancelRate) }}</div>
          <div class="kpi-meta">{{ recycleCancelledCount }} / {{ recycleTotalAllCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="kpi-card">
          <div class="kpi-title">回收均值单价</div>
          <div class="kpi-value">￥{{ formatMoney(recycleAvgPrice) }}</div>
          <div class="kpi-meta">成交 GMV / 完成单</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="kpi-row">
      <el-col :span="8">
        <el-card class="kpi-card">
          <div class="kpi-title">易淘完成率</div>
          <div class="kpi-value">{{ formatRate(secondhandCompletionRate) }}</div>
          <div class="kpi-meta">{{ secondhandCompletedCount }} / {{ secondhandTotalAllCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="kpi-card">
          <div class="kpi-title">易淘取消率</div>
          <div class="kpi-value">{{ formatRate(secondhandCancelRate) }}</div>
          <div class="kpi-meta">{{ secondhandCancelledCount }} / {{ secondhandTotalAllCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="kpi-card">
          <div class="kpi-title">易淘均值单价</div>
          <div class="kpi-value">￥{{ formatMoney(secondhandAvgPrice) }}</div>
          <div class="kpi-meta">成交 GMV / 已付款单</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>订单趋势</span>
          <div class="trend-header-right">
            <el-segmented
              v-model="gmvTrendScope"
              :options="gmvScopeOptions"
              @change="renderTrend"
              size="small"
              class="trend-segmented"
            />
            <el-tag
              v-if="stats.startDate && stats.endDate"
              class="trend-range-tag"
              size="small"
              round
              effect="plain"
              type="info"
            >
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
            <el-table-column label="转化率" width="110">
              <template #default="{ row }">
                <span v-if="row.key === 'cancelled'">
                  {{ row.conversion != null ? (row.conversion * 100).toFixed(1) + '%' : '-' }}
                </span>
                <span v-else>
                  {{ row.conversion != null ? (row.conversion * 100).toFixed(1) + '%' : '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="流失" width="90">
              <template #default="{ row }">
                <span v-if="row.dropOff != null">{{ row.dropOff }}</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>回收履约效率与异常</span>
          <el-tag class="trend-range-tag" size="small" round effect="plain" type="info">回收主线</el-tag>
        </div>
      </template>

      <el-row :gutter="16" class="flow-grid">
        <el-col :span="14" class="flow-left">
          <el-table :data="flowTimingRows" border size="small" class="flow-table">
            <el-table-column prop="label" label="环节耗时" min-width="180" />
            <el-table-column prop="sample" label="样本量" width="90" />
            <el-table-column prop="median" label="中位数" width="120" />
            <el-table-column prop="p90" label="P90" width="120" />
            <el-table-column prop="p95" label="P95" width="120" />
          </el-table>
        </el-col>
        <el-col :span="10" class="flow-right">
          <div class="exception-grid">
            <div v-for="item in exceptionCards" :key="item.key" class="exception-card" :class="`is-${item.level}`">
              <div class="exception-title">{{ item.title }}</div>
              <div class="exception-value">{{ item.value }}</div>
              <div class="exception-meta">{{ item.meta }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="16" class="flow-grid-sla">
        <el-col :span="24">
          <div class="sla-block">
            <div class="sla-title">超时占比（SLA）</div>
            <div class="sla-attribution">
              <div v-for="item in slaAttribution" :key="item.key" class="sla-pill" :class="`is-${item.level}`">
                <span class="sla-pill-title">{{ item.owner }}</span>
                <span class="sla-pill-value">{{ item.rate }}</span>
              </div>
            </div>
            <el-table :data="slaRows" border size="small" class="sla-table">
              <el-table-column prop="label" label="环节" min-width="160" />
              <el-table-column prop="threshold" label="阈值" width="120" />
              <el-table-column prop="rate" label="超时占比" width="120" />
              <el-table-column prop="count" label="超时/样本" width="140" />
            </el-table>
            <div v-if="slaInsight" class="sla-insight">{{ slaInsight }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>调价幅度分布（估价偏差）</span>
          <el-tag class="trend-range-tag" size="small" round effect="plain" type="info">回收主线</el-tag>
        </div>
      </template>
      <div ref="priceGapChartEl" class="gap-chart"></div>
      <div class="gap-note">
        说明：按 |final - estimated| / estimated 分桶，越集中在低区间代表估价越稳定。
        <span v-if="gapSummary"> {{ gapSummary }}</span>
      </div>
    </el-card>

    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>易淘价格区间分布</span>
          <el-tag class="trend-range-tag" size="small" round effect="plain" type="info">易淘主线</el-tag>
        </div>
      </template>
      <div ref="secondhandPriceChartEl" class="gap-chart"></div>
      <div class="gap-note">说明：统计已付款订单的价格区间分布。</div>
    </el-card>

    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>维度拆分（TopN）</span>
          <div class="header-right breakdown-controls">
            <el-select v-model="breakdownType" style="width: 220px" @change="loadStatistics">
              <el-option label="回收-品牌 Top" value="recycle_brand" />
              <el-option label="回收-机型 Top" value="recycle_model" />
              <el-option label="官方验订单-品牌 GMV Top" value="verified_brand" />
              <el-option label="官方验订单-机型 GMV Top" value="verified_model" />
              <el-option label="易淘订单-分类 GMV Top" value="secondhand_category" />
              <el-option label="易淘订单-商品 GMV Top" value="secondhand_product" />
              <el-option label="库存-品牌 Top" value="inventory_brand" />
              <el-option label="库存-机型 Top" value="inventory_model" />
            </el-select>
            <el-segmented
              v-if="breakdownHasGMV"
              v-model="breakdownMetric"
              :options="breakdownMetricOptions"
              @change="onBreakdownMetricChange"
            />
            <el-segmented
              v-if="breakdownHasGMV && breakdownMetric === 'gmv' && gmvBreakdownActive"
              v-model="breakdownGMVScope"
              :options="breakdownGMVScopeOptions"
              @change="loadStatistics"
            />
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
            <el-table-column v-if="breakdownHasGMV" prop="gmv" label="GMV" width="140">
              <template #default="{ row }">￥{{ formatMoney(row.gmv || 0) }}</template>
            </el-table-column>
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
        <el-table-column prop="gmvPaid" label="成交GMV" width="160">
          <template #default="{ row }">￥{{ formatMoney(row.gmvPaid) }}</template>
        </el-table-column>
        <el-table-column prop="gmvAll" label="下单GMV" width="160">
          <template #default="{ row }">￥{{ formatMoney(row.gmvAll) }}</template>
        </el-table-column>
        <el-table-column prop="gmvSelected" :label="gmvTrendScope === 'paid' ? 'GMV(成交)' : 'GMV(下单)'" width="160">
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

const excludeCancelledOrders = ref(true)
const includeCancelledInOrderGMV = ref(true)
const recycleStatuses = ref([])
const verifiedStatuses = ref([])
const secondhandStatuses = ref([])

const quickDate = ref('month')
const quickDateOptions = [
  { label: '今天', value: 'today' },
  { label: '近7天', value: 'week' },
  { label: '近30天', value: 'month' },
  { label: '全部', value: 'all' },
]

const onQuickDateChange = (v) => {
  setDateRange(String(v))
}

const gmvTrendScope = ref('paid')
const gmvScopeOptions = [
  { label: '成交GMV', value: 'paid' },
  { label: '下单GMV', value: 'all' },
]

const breakdownType = ref('recycle_brand')
const topN = ref(10)
const breakdownMetric = ref('count')
const breakdownMetricOptions = [
  { label: '数量', value: 'count' },
  { label: 'GMV', value: 'gmv' },
]
const breakdownGMVScope = ref('paid')
const breakdownGMVScopeOptions = [
  { label: '成交GMV', value: 'paid' },
  { label: '下单GMV', value: 'all' },
]

const chartEl = ref(null)
const funnelChartEl = ref(null)
const breakdownChartEl = ref(null)
const priceGapChartEl = ref(null)
const secondhandPriceChartEl = ref(null)

const charts = {
  trend: null,
  funnel: null,
  breakdown: null,
  gap: null,
  secondhandPrice: null,
}

const activeFunnelKey = ref('recycle')
const funnelOptions = [
  { label: '回收', value: 'recycle' },
  { label: '官方验', value: 'verified' },
  { label: '易淘', value: 'secondhand' },
]

const recycleStatusOptions = computed(() => (stats.value?.funnels?.recycle || []).map((r) => ({ key: r.key, label: r.label })))
const verifiedStatusOptions = computed(() => (stats.value?.funnels?.verified || []).map((r) => ({ key: r.key, label: r.label })))
const secondhandStatusOptions = computed(() => (stats.value?.funnels?.secondhand || []).map((r) => ({ key: r.key, label: r.label })))

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

const formatDuration = (hours) => {
  if (hours == null) return '-'
  const h = Number(hours)
  if (!Number.isFinite(h)) return '-'
  if (h >= 24) {
    const days = h / 24
    return `${days.toFixed(1)} 天`
  }
  return `${h.toFixed(1)} 小时`
}

const formatRate = (rate) => {
  if (rate == null) return '-'
  const r = Number(rate)
  if (!Number.isFinite(r)) return '-'
  return `${(r * 100).toFixed(1)}%`
}

const recycleTotalAllCount = computed(() => (
  stats.value?.recycleOrdersTotalAll
  ?? (stats.value?.funnels?.recycle || []).reduce((sum, r) => sum + Number(r.count || 0), 0)
))

const recycleCompletedCount = computed(() => Number(stats.value?.recycleCompleted || 0))
const recycleCancelledCount = computed(() => Number(stats.value?.recycleCancelledTotal || 0))

const recycleCompletionRate = computed(() => {
  const total = Number(recycleTotalAllCount.value || 0)
  if (!total) return 0
  return recycleCompletedCount.value / total
})

const recycleCancelRate = computed(() => {
  const total = Number(recycleTotalAllCount.value || 0)
  if (!total) return 0
  return recycleCancelledCount.value / total
})

const recycleAvgPrice = computed(() => {
  const completed = Number(recycleCompletedCount.value || 0)
  if (!completed) return 0
  const gmv = Number(stats.value?.recycleGMVCompleted || 0)
  return gmv / completed
})

const secondhandTotalAllCount = computed(() => (
  stats.value?.secondhandOrdersTotalAll
  ?? (stats.value?.funnels?.secondhand || []).reduce((sum, r) => sum + Number(r.count || 0), 0)
))

const secondhandCompletedCount = computed(() => Number(stats.value?.secondhandCompleted || 0))
const secondhandCancelledCount = computed(() => Number(stats.value?.secondhandCancelledTotal || 0))
const secondhandPaidTotal = computed(() => Number(stats.value?.secondhandPaidTotal || 0))

const secondhandCompletionRate = computed(() => {
  const total = Number(secondhandTotalAllCount.value || 0)
  if (!total) return 0
  return secondhandCompletedCount.value / total
})

const secondhandCancelRate = computed(() => {
  const total = Number(secondhandTotalAllCount.value || 0)
  if (!total) return 0
  return secondhandCancelledCount.value / total
})

const secondhandAvgPrice = computed(() => {
  const paid = Number(secondhandPaidTotal.value || 0)
  if (!paid) return 0
  const gmv = Number(stats.value?.secondhandGMVPaid || 0)
  return gmv / paid
})

const flowTimingRows = computed(() => {
  const timings = stats.value?.recycle_flow?.timings || {}
  const items = [
    { key: 'created_to_shipped', label: '创建 → 寄出' },
    { key: 'shipped_to_received', label: '寄出 → 收货' },
    { key: 'received_to_inspected', label: '收货 → 质检' },
    { key: 'inspected_to_paid', label: '质检 → 打款' },
    { key: 'created_to_paid', label: '创建 → 打款' },
  ]
  return items.map((item) => {
    const stat = timings[item.key] || {}
    return {
      label: item.label,
      sample: stat.sample ?? '-',
      median: formatDuration(stat.median_hours),
      p90: formatDuration(stat.p90_hours),
      p95: formatDuration(stat.p95_hours),
    }
  })
})

const exceptionCards = computed(() => {
  const ex = stats.value?.recycle_flow?.exceptions || {}
  const counts = ex.counts || {}
  const items = [
    {
      key: 'cancelled',
      title: '取消率',
      value: formatRate(ex.cancelled_rate),
      meta: `${counts.cancelled ?? 0} / ${counts.total ?? 0}`,
      raw: ex.cancelled_rate ?? 0,
    },
    {
      key: 'dispute',
      title: '价格异议率',
      value: formatRate(ex.dispute_rate),
      meta: `${counts.dispute ?? 0} / ${counts.total ?? 0}`,
      raw: ex.dispute_rate ?? 0,
    },
    {
      key: 'payment_failed',
      title: '打款失败率',
      value: formatRate(ex.payment_failed_rate),
      meta: `${counts.payment_failed ?? 0} / ${counts.total ?? 0}`,
      raw: ex.payment_failed_rate ?? 0,
    },
    {
      key: 'unconfirmed',
      title: '质检后未确认',
      value: formatRate(ex.unconfirmed_rate),
      meta: `${counts.unconfirmed ?? 0} / ${counts.total ?? 0}`,
      raw: ex.unconfirmed_rate ?? 0,
    },
  ]
  return items.map((item) => ({
    ...item,
    level: item.raw >= 0.2 ? 'high' : item.raw >= 0.1 ? 'mid' : 'low',
  }))
})

const slaRows = computed(() => {
  const items = stats.value?.recycle_flow?.sla || []
  return items.map((item) => ({
    key: item.key,
    label: item.label,
    threshold: formatDuration(item.threshold_hours),
    rate: formatRate(item.overtime_rate),
    count: `${item.overtime_count ?? 0} / ${item.total ?? 0}`,
    rawRate: item.overtime_rate ?? 0,
    overtimeCount: item.overtime_count ?? 0,
    total: item.total ?? 0,
  }))
})

const slaAttribution = computed(() => {
  const items = stats.value?.recycle_flow?.sla_attribution || []
  return items.map((item) => {
    const raw = item.overtime_rate ?? 0
    return {
      key: item.key,
      owner: item.owner,
      rate: formatRate(raw),
      level: raw >= 0.3 ? 'high' : raw >= 0.15 ? 'mid' : 'low',
    }
  })
})

const slaInsight = computed(() => {
  const rows = slaRows.value || []
  if (!rows.length) return ''
  const top = [...rows].sort((a, b) => (b.rawRate || 0) - (a.rawRate || 0))[0]
  if (!top || top.total === 0) return ''
  const rateText = formatRate(top.rawRate)
  const countText = `${top.overtimeCount} / ${top.total}`
  if ((top.rawRate || 0) >= 0.3) {
    return `提示：${top.label} 超时率 ${rateText}（${countText}）偏高，建议优先关注该环节。`
  }
  return `提示：${top.label} 超时率最高（${rateText}，${countText}），可作为优化优先级参考。`
})

const renderChart = (trend) => {
  if (!chartEl.value) return
  if (!charts.trend) charts.trend = echarts.init(chartEl.value)

  const x = trend.map((r) => r.date)
  const recycleOrders = trend.map((r) => Number(r.recycleOrders || 0))
  const verifiedOrders = trend.map((r) => Number(r.verifiedOrders || 0))
  const secondhandOrders = trend.map((r) => Number(r.secondhandOrders || 0))
  const gmvSeriesName = gmvTrendScope.value === 'paid' ? '成交GMV（含易淘）' : '下单GMV（含易淘）'
  const gmvAll = trend.map((r) => (
    gmvTrendScope.value === 'paid'
      ? (Number(r.verifiedGMVPaid || 0) + Number(r.secondhandGMVPaid || 0))
      : (Number(r.verifiedGMVAll || 0) + Number(r.secondhandGMVAll || 0))
  ))

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
      { name: gmvSeriesName, type: 'line', yAxisIndex: 1, smooth: true, data: gmvAll },
    ],
    graphic: [
      {
        type: 'text',
        right: 10,
        top: 6,
        style: {
          text: '柱=订单数  线=GMV',
          fill: '#909399',
          fontSize: 11,
        },
      },
    ],
  })
}

const funnelTable = computed(() => {
  const funnels = stats.value?.funnels || {}
  const list = Array.isArray(funnels?.[activeFunnelKey.value]) ? funnels[activeFunnelKey.value] : []
  const labelByKey = {}
  const countByKey = {}
  for (const item of list) {
    labelByKey[item.key] = item.label
    countByKey[item.key] = Number(item.count || 0)
  }

  const statusOrder = {
    recycle: ['pending', 'shipped', 'received', 'inspected', 'completed', 'cancelled'],
    verified: ['pending', 'paid', 'shipped', 'completed', 'cancelled'],
    secondhand: ['pending', 'paid', 'shipped', 'completed', 'cancelled'],
  }

  const order = statusOrder[activeFunnelKey.value] || list.map((x) => x.key)

  const mainOrder = order.filter((k) => k !== 'cancelled')
  const totalMain = mainOrder.length ? (countByKey[mainOrder[0]] ?? 0) : 0
  const cancelled = countByKey.cancelled ?? 0

  const rows = []
  let prev = null
  for (const key of mainOrder) {
    const count = countByKey[key] ?? 0
    const conv = prev && prev > 0 ? count / prev : null
    const drop = prev != null ? Math.max(0, prev - count) : null
    rows.push({
      key,
      label: labelByKey[key] || key,
      count,
      conversion: conv,
      dropOff: drop,
    })
    prev = count
  }

  if (order.includes('cancelled')) {
    rows.push({
      key: 'cancelled',
      label: labelByKey.cancelled || '已取消',
      count: cancelled,
      conversion: totalMain > 0 ? cancelled / totalMain : null,
      dropOff: null,
    })
  }

  return rows
})

const breakdownRows = computed(() => {
  const b = stats.value?.breakdown
  if (!b || !Array.isArray(b.rows)) return []
  return b.rows
})

const breakdownHasGMV = computed(() => {
  const b = stats.value?.breakdown
  if (!b) return false
  if (b.defaultMetric === 'gmv') return true
  return breakdownRows.value.some((r) => r.gmv != null)
})

const gmvBreakdownActive = computed(() => breakdownType.value.startsWith('verified_') || breakdownType.value.startsWith('secondhand_'))

const showIncludeCancelledInOrderGMV = computed(() => (
  gmvTrendScope.value === 'all'
  || (gmvBreakdownActive.value && breakdownMetric.value === 'gmv' && breakdownGMVScope.value === 'all')
))

const onBreakdownMetricChange = () => {
  if (breakdownMetric.value === 'gmv' && gmvBreakdownActive.value) {
    loadStatistics()
    return
  }
  renderBreakdown()
}

const renderTrend = () => {
  const trend = Array.isArray(stats.value?.trend) ? stats.value.trend : []
  if (statsTable.value?.length) {
    statsTable.value = statsTable.value.map((r) => ({
      ...r,
      gmv: (gmvTrendScope.value === 'paid' ? r.gmvPaid : r.gmvAll),
    }))
  }
  renderChart(trend)
}

const renderFunnel = () => {
  const funnels = stats.value?.funnels || {}
  const list = Array.isArray(funnels?.[activeFunnelKey.value]) ? funnels[activeFunnelKey.value] : []
  if (!funnelChartEl.value) return
  if (!charts.funnel) charts.funnel = echarts.init(funnelChartEl.value)

  const orderByKey = {
    recycle: ['pending', 'shipped', 'received', 'inspected', 'completed', 'cancelled'],
    verified: ['pending', 'paid', 'shipped', 'completed', 'cancelled'],
    secondhand: ['pending', 'paid', 'shipped', 'completed', 'cancelled'],
  }

  const map = new Map(list.map((r) => [r.key, r]))
  const ordered = (orderByKey[activeFunnelKey.value] || list.map((x) => x.key))
    .filter((k) => map.has(k))
    .map((k) => map.get(k))

  const main = ordered.filter((r) => r.key !== 'cancelled')
  let prev = null
  const data = ordered.map((r) => {
    const value = Number(r.count || 0)
    const conv = prev && prev > 0 ? value / prev : null
    if (r.key !== 'cancelled') prev = value
    return { name: r.label, value, conv }
  })

  charts.funnel.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p) => {
        const v = Number(p?.data?.value || 0)
        const conv = p?.data?.conv
        const convText = typeof conv === 'number' ? `<br/>转化率：${(conv * 100).toFixed(1)}%` : ''
        return `${p.name}<br/>数量：${v}${convText}`
      },
    },
    series: [
      {
        type: 'funnel',
        sort: 'none',
        gap: 2,
        top: 10,
        bottom: 10,
        left: '8%',
        width: '84%',
        label: { formatter: (p) => `${p.name}: ${Number(p.value || 0)}` },
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
  const values = rows.map((r) => {
    const metric = breakdownHasGMV.value ? breakdownMetric.value : 'count'
    if (metric === 'gmv') return Number(r.gmv || 0)
    return Number(r.count || 0)
  })
  const metricLabel = breakdownHasGMV.value && breakdownMetric.value === 'gmv' ? 'GMV' : '数量'

  charts.breakdown.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 10, right: 10, top: 10, bottom: 10, containLabel: true },
    xAxis: {
      type: 'value',
      minInterval: breakdownHasGMV.value && breakdownMetric.value === 'gmv' ? 0 : 1,
      axisLabel: breakdownHasGMV.value && breakdownMetric.value === 'gmv'
        ? { formatter: (v) => `￥${Number(v).toLocaleString('zh-CN')}` }
        : undefined,
    },
    yAxis: { type: 'category', data: dims, axisLabel: { interval: 0 } },
    series: [{ name: metricLabel, type: 'bar', data: values, itemStyle: { color: '#409EFF' } }],
  })
}

const renderGapChart = () => {
  if (!priceGapChartEl.value) return
  if (!charts.gap) charts.gap = echarts.init(priceGapChartEl.value)

  const bins = stats.value?.price_gap_distribution?.bins || []
  const labels = bins.map((b) => b.label)
  const values = bins.map((b) => Number(b.count || 0))

  charts.gap.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 10, right: 10, top: 10, bottom: 20, containLabel: true },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '订单数',
        type: 'bar',
        data: values,
        itemStyle: { color: '#6B8EF7' },
        barWidth: 32,
      },
    ],
  })
}

const renderSecondhandPriceChart = () => {
  if (!secondhandPriceChartEl.value) return
  if (!charts.secondhandPrice) charts.secondhandPrice = echarts.init(secondhandPriceChartEl.value)

  const bins = stats.value?.secondhand_price_distribution?.bins || []
  const labels = bins.map((b) => b.label)
  const values = bins.map((b) => Number(b.count || 0))

  charts.secondhandPrice.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 10, right: 10, top: 10, bottom: 20, containLabel: true },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '订单数',
        type: 'bar',
        data: values,
        itemStyle: { color: '#34D399' },
        barWidth: 32,
      },
    ],
  })
}

const gapSummary = computed(() => {
  const bins = stats.value?.price_gap_distribution?.bins || []
  const total = stats.value?.price_gap_distribution?.total || 0
  if (!total || !bins.length) return ''
  const mid = bins.reduce((sum, b) => sum + (Number(b.count || 0) * Number((b.mid || 0))), 0)
  const avg = mid / total
  if (!Number.isFinite(avg)) return ''
  return `样本 ${total} 单，平均误差约 ${(avg * 100).toFixed(1)}%。`
})

const loadStatistics = async () => {
  try {
    const params = {
      include: 'trend,funnel,breakdown,flow,gap,secondhand',
      breakdown: breakdownType.value,
      top_n: topN.value,
      exclude_cancelled_orders: excludeCancelledOrders.value ? 'true' : 'false',
      include_cancelled_in_order_gmv: includeCancelledInOrderGMV.value ? 'true' : 'false',
      recycle_statuses: recycleStatuses.value.join(','),
      verified_statuses: verifiedStatuses.value.join(','),
      secondhand_statuses: secondhandStatuses.value.join(','),
    }
    if (gmvBreakdownActive.value) {
      params.breakdown_gmv_scope = breakdownGMVScope.value
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const res = await adminApi.get('/statistics', { params })
    const data = res.data || {}
    stats.value = data

    if (data?.breakdown?.defaultMetric) {
      breakdownMetric.value = data.breakdown.defaultMetric
    } else if (!breakdownHasGMV.value) {
      breakdownMetric.value = 'count'
    }

    const trend = Array.isArray(data.trend) ? data.trend : []
    statsTable.value = trend.map((r) => ({
      date: r.date,
      recycleOrders: r.recycleOrders || 0,
      recycleCompleted: r.recycleCompleted || 0,
      recycleDisputes: r.recycleDisputes || 0,
      verifiedOrders: r.verifiedOrders || 0,
      secondhandOrders: r.secondhandOrders || 0,
      secondhandSettlementFailed: r.secondhandSettlementFailed || 0,
      gmvPaid: Number(r.verifiedGMVPaid || 0) + Number(r.secondhandGMVPaid || 0),
      gmvAll: Number(r.verifiedGMVAll || 0) + Number(r.secondhandGMVAll || 0),
      gmv: (gmvTrendScope.value === 'paid'
        ? (Number(r.verifiedGMVPaid || 0) + Number(r.secondhandGMVPaid || 0))
        : (Number(r.verifiedGMVAll || 0) + Number(r.secondhandGMVAll || 0))),
    }))

    await nextTick()
    renderChart(trend)
    renderFunnel()
    renderBreakdown()
    renderGapChart()
    renderSecondhandPriceChart()
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
    '成交GMV（含易淘）',
    '下单GMV（含易淘）',
    '调价分布样本数',
    '调价分布(0-5%)',
    '调价分布(5-10%)',
    '调价分布(10-20%)',
    '调价分布(20-30%)',
    '调价分布(30%+)',
    'SLA创建→寄出阈值',
    'SLA创建→寄出超时率',
    'SLA创建→寄出超时/样本',
    'SLA寄出→收货阈值',
    'SLA寄出→收货超时率',
    'SLA寄出→收货超时/样本',
    '易淘价格分布样本数',
    '易淘价格分布(0-500)',
    '易淘价格分布(500-1000)',
    '易淘价格分布(1000-2000)',
    '易淘价格分布(2000-4000)',
    '易淘价格分布(4000+)',
  ]

  const gapBins = stats.value?.price_gap_distribution?.bins || []
  const gapCounts = (label) => (gapBins.find((b) => b.label === label)?.count ?? 0)
  const gapTotal = stats.value?.price_gap_distribution?.total ?? 0

  const slaList = stats.value?.recycle_flow?.sla || []
  const slaByKey = {}
  for (const item of slaList) {
    slaByKey[item.key] = item
  }

  const shBins = stats.value?.secondhand_price_distribution?.bins || []
  const shCounts = (label) => (shBins.find((b) => b.label === label)?.count ?? 0)
  const shTotal = stats.value?.secondhand_price_distribution?.total ?? 0

  const rows = statsTable.value.map((r) => ([
    r.date,
    r.recycleOrders,
    r.recycleCompleted,
    r.recycleDisputes,
    r.verifiedOrders,
    r.secondhandOrders,
    r.secondhandSettlementFailed,
    r.gmvPaid,
    r.gmvAll,
    gapTotal,
    gapCounts('0-5%'),
    gapCounts('5-10%'),
    gapCounts('10-20%'),
    gapCounts('20-30%'),
    gapCounts('30%+'),
    formatDuration(slaByKey.created_to_shipped?.threshold_hours),
    formatRate(slaByKey.created_to_shipped?.overtime_rate),
    `${slaByKey.created_to_shipped?.overtime_count ?? 0} / ${slaByKey.created_to_shipped?.total ?? 0}`,
    formatDuration(slaByKey.shipped_to_received?.threshold_hours),
    formatRate(slaByKey.shipped_to_received?.overtime_rate),
    `${slaByKey.shipped_to_received?.overtime_count ?? 0} / ${slaByKey.shipped_to_received?.total ?? 0}`,
    shTotal,
    shCounts('0-500'),
    shCounts('500-1000'),
    shCounts('1000-2000'),
    shCounts('2000-4000'),
    shCounts('4000+'),
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
  if (charts.gap) charts.gap.resize()
  if (charts.secondhandPrice) charts.secondhandPrice.resize()
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
  if (charts.gap) charts.gap.dispose()
  if (charts.secondhandPrice) charts.secondhandPrice.dispose()
})
</script>

<style scoped>
.statistics-page {
  padding: 0;
}

.page-header {
  margin-bottom: 10px;
}

.page-title {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
}

.page-subtitle {
  color: #909399;
  font-size: 12px;
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

.kpi-row {
  margin-bottom: 14px;
}

.kpi-card {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #eef0f3;
  box-shadow: 0 6px 14px rgba(31, 41, 55, 0.05);
}

.kpi-card :deep(.el-card__body) {
  padding: 12px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.kpi-title {
  font-size: 13px;
  color: #6b7280;
}

.kpi-value {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.kpi-meta {
  font-size: 12px;
  color: #9ca3af;
}

.quick-date-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.methodology-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

.methodology-body code {
  background: rgba(64, 158, 255, 0.08);
  padding: 1px 6px;
  border-radius: 6px;
  color: #303133;
}

.filters-card :deep(.el-card__header) {
  padding: 8px 14px;
}

.filters-card :deep(.el-card__body) {
  padding: 10px 14px 12px 14px;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters-title {
  font-weight: 600;
}

.filters-grid {
  margin-bottom: 6px;
}

.filter-block-title {
  font-size: 12px;
  color: #606266;
  margin-bottom: 6px;
}

.toggle-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.toggle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 8px;
  background: rgba(144, 147, 153, 0.06);
}

.toggle-text {
  color: #303133;
  font-size: 12px;
}

.advanced-collapse :deep(.el-collapse-item__header) {
  font-weight: 600;
  color: #303133;
}

.rule-button {
  --el-button-bg-color: rgba(144, 147, 153, 0.12);
  --el-button-border-color: transparent;
  --el-button-text-color: #606266;
  --el-button-hover-bg-color: rgba(144, 147, 153, 0.18);
  --el-button-hover-border-color: transparent;
  --el-button-hover-text-color: #303133;
  --el-button-active-bg-color: rgba(144, 147, 153, 0.24);
  --el-button-active-border-color: transparent;
  --el-button-active-text-color: #303133;
}

.rule-button:focus-visible {
  outline: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.trend-header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.trend-segmented {
  --el-segmented-bg-color: rgba(144, 147, 153, 0.12);
  --el-segmented-item-selected-bg-color: var(--el-color-primary);
  --el-segmented-item-hover-bg-color: rgba(144, 147, 153, 0.16);
}

.trend-range-tag {
  --el-tag-bg-color: rgba(144, 147, 153, 0.10);
  --el-tag-border-color: transparent;
  --el-tag-text-color: #606266;
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

.gap-chart {
  height: 260px;
  width: 100%;
}

.gap-note {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.breakdown-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.exception-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.exception-card {
  padding: 14px;
  border-radius: 12px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #eef0f3;
  box-shadow: 0 8px 20px rgba(31, 41, 55, 0.06);
}

.exception-card.is-high {
  border-color: rgba(239, 68, 68, 0.35);
  box-shadow: 0 10px 24px rgba(239, 68, 68, 0.12);
}

.exception-card.is-high .exception-value {
  color: #ef4444;
}

.exception-card.is-mid {
  border-color: rgba(245, 158, 11, 0.35);
  box-shadow: 0 10px 24px rgba(245, 158, 11, 0.12);
}

.exception-card.is-mid .exception-value {
  color: #d97706;
}

.exception-title {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.exception-value {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.exception-meta {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}

.sla-block {
  margin-top: 14px;
  padding: 12px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #eef0f3;
  box-shadow: 0 6px 16px rgba(31, 41, 55, 0.05);
}

.sla-title {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.sla-attribution {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.sla-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: #f6f7fb;
  border: 1px solid #eef0f3;
  font-size: 12px;
  color: #4b5563;
}

.sla-pill-title {
  color: #6b7280;
}

.sla-pill-value {
  font-weight: 600;
  color: #111827;
}

.sla-pill.is-high {
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.08);
}

.sla-pill.is-high .sla-pill-value {
  color: #ef4444;
}

.sla-pill.is-mid {
  border-color: rgba(245, 158, 11, 0.35);
  background: rgba(245, 158, 11, 0.08);
}

.sla-pill.is-mid .sla-pill-value {
  color: #d97706;
}

.sla-insight {
  margin-top: 10px;
  padding: 8px 10px;
  background: #f6f7fb;
  border-radius: 8px;
  color: #4b5563;
  font-size: 12px;
}

.flow-grid {
  align-items: flex-start;
}

.flow-grid-sla {
  margin-top: 12px;
}

.flow-left :deep(.el-table__inner-wrapper),
.flow-right :deep(.el-table__inner-wrapper) {
  border-radius: 10px;
}

.flow-table :deep(.el-table__header-wrapper th),
.sla-table :deep(.el-table__header-wrapper th) {
  background: #f6f7fb;
  color: #4b5563;
  font-weight: 600;
}

.flow-table :deep(.el-table__row td),
.sla-table :deep(.el-table__row td) {
  padding: 10px 8px;
}
</style>
