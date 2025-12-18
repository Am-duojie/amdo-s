<template>
  <div class="intelligent-analysis admin-page">
    <el-card shadow="never" class="header-card">
      <template #header>
        <div class="header">
          <div>
            <div class="title">智能分析</div>
            <div class="desc">支持批量在线推理（分布/TopN/分页）与单条订单推理（建议回收价 + 风险）</div>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="批量分析" name="batch">
          <div class="batch-controls">
            <el-form inline>
              <el-form-item label="日期范围">
                <el-date-picker
                  v-model="batchDateRange"
                  type="daterange"
                  range-separator="~"
                  start-placeholder="开始"
                  end-placeholder="结束"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="batchStatuses" multiple clearable placeholder="全部" style="width: 260px">
                  <el-option label="待寄出" value="pending" />
                  <el-option label="已寄出" value="shipped" />
                  <el-option label="已收货" value="received" />
                  <el-option label="已检测" value="inspected" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已取消" value="cancelled" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="loadingSummary || loadingBatch" @click="reloadBatchAll">刷新分析</el-button>
              </el-form-item>
              <el-form-item>
                <el-button :loading="loadingSummary" @click="loadSummary">只刷新概览</el-button>
              </el-form-item>
            </el-form>
          </div>

          <div class="summary-grid" v-loading="loadingSummary">
            <el-card shadow="never" class="summary-card">
              <div class="summary-title">订单总数</div>
              <div class="summary-value">{{ summary?.total ?? '-' }}</div>
              <div class="summary-sub">样本计算：{{ summary?.sampled ?? '-' }}</div>
            </el-card>
            <el-card shadow="never" class="summary-card">
              <div class="summary-title">均值：建议回收价</div>
              <div class="summary-value">¥{{ formatMoney(summary?.avg?.suggested_final_price) }}</div>
            </el-card>
            <el-card shadow="never" class="summary-card">
              <div class="summary-title">均值：异议风险</div>
              <div class="summary-value">{{ formatRisk(summary?.avg?.risk_dispute) }}</div>
            </el-card>
            <el-card shadow="never" class="summary-card">
              <div class="summary-title">均值：取消风险</div>
              <div class="summary-value">{{ formatRisk(summary?.avg?.risk_cancel) }}</div>
            </el-card>
          </div>

          <div class="charts-row" v-loading="loadingSummary">
            <el-card shadow="never" class="chart-card">
              <template #header><span>异议风险分布</span></template>
              <div ref="riskDisputeEl" class="chart" />
            </el-card>
            <el-card shadow="never" class="chart-card">
              <template #header><span>预估价偏离分布（|建议-预估|/预估）</span></template>
              <div ref="gapEl" class="chart" />
            </el-card>
          </div>

          <div class="tables-row" v-loading="loadingSummary">
            <el-card shadow="never" class="table-card">
              <template #header><span>高风险 Top10（按异议风险）</span></template>
              <el-table :data="summary?.top?.high_risk_orders || []" size="small" style="width: 100%">
                <el-table-column prop="id" label="订单ID" width="90" />
                <el-table-column label="机型">
                  <template #default="{ row }">{{ row.brand }} {{ row.model }}</template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="110">
                  <template #default="{ row }">{{ statusText(row.status) }}</template>
                </el-table-column>
                <el-table-column prop="risk_dispute" label="异议风险" width="110">
                  <template #default="{ row }"><el-tag :type="riskTagType(row.risk_dispute)">{{ formatRisk(row.risk_dispute) }}</el-tag></template>
                </el-table-column>
                <el-table-column prop="risk_cancel" label="取消风险" width="110">
                  <template #default="{ row }"><el-tag :type="riskTagType(row.risk_cancel)">{{ formatRisk(row.risk_cancel) }}</el-tag></template>
                </el-table-column>
                <el-table-column label="操作" width="110">
                  <template #default="{ row }">
                    <el-button size="small" type="primary" link @click="goDetailById(row.id)">详情</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>

            <el-card shadow="never" class="table-card">
              <template #header><span>品牌 Top10（按平均异议风险）</span></template>
              <el-table :data="summary?.top?.brands_by_risk || []" size="small" style="width: 100%">
                <el-table-column prop="brand" label="品牌" />
                <el-table-column prop="count" label="样本量" width="100" />
                <el-table-column prop="avg_risk_dispute" label="平均异议风险" width="140">
                  <template #default="{ row }">{{ formatRisk(row.avg_risk_dispute) }}</template>
                </el-table-column>
                <el-table-column prop="avg_gap_ratio" label="平均偏离" width="120">
                  <template #default="{ row }">{{ formatRisk(row.avg_gap_ratio) }}</template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>

          <el-card shadow="never" class="batch-table-card" v-loading="loadingBatch">
            <template #header>
              <div class="result-header">
                <div>批量推理列表</div>
                <div class="result-actions">
                  <el-button size="small" @click="loadBatch">刷新列表</el-button>
                </div>
              </div>
            </template>
            <el-table :data="batchRows" size="small" style="width: 100%">
              <el-table-column prop="id" label="订单ID" width="90" />
              <el-table-column prop="created_at" label="创建时间" width="170">
                <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
              </el-table-column>
              <el-table-column label="机型" min-width="160">
                <template #default="{ row }">{{ row.brand }} {{ row.model }} {{ row.storage }}</template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="110">
                <template #default="{ row }">{{ statusText(row.status) }}</template>
              </el-table-column>
              <el-table-column label="建议价" width="120">
                <template #default="{ row }">¥{{ row.ml?.suggested_final_price ?? '-' }}</template>
              </el-table-column>
              <el-table-column label="预估价" width="110">
                <template #default="{ row }">¥{{ row.estimated_price ?? '-' }}</template>
              </el-table-column>
              <el-table-column label="异议风险" width="110">
                <template #default="{ row }"><el-tag :type="riskTagType(row.ml?.risk_dispute)">{{ formatRisk(row.ml?.risk_dispute) }}</el-tag></template>
              </el-table-column>
              <el-table-column label="取消风险" width="110">
                <template #default="{ row }"><el-tag :type="riskTagType(row.ml?.risk_cancel)">{{ formatRisk(row.ml?.risk_cancel) }}</el-tag></template>
              </el-table-column>
              <el-table-column label="偏离" width="100">
                <template #default="{ row }">{{ formatRisk(row.gap_ratio) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button size="small" type="primary" link @click="goDetailById(row.id)">详情</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="pager">
              <el-pagination
                v-model:current-page="batchPage"
                v-model:page-size="batchPageSize"
                :total="batchTotal"
                layout="total, sizes, prev, pager, next"
                :page-sizes="[10, 20, 50, 100]"
                @current-change="loadBatch"
                @size-change="handleBatchSizeChange"
              />
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="单条分析" name="single">
          <div class="controls">
            <el-form inline>
              <el-form-item label="选择订单">
                <el-select
                  v-model="selectedOrderId"
                  filterable
                  clearable
                  placeholder="从最近订单中选择"
                  style="width: 360px"
                  @change="handleSelectOrder"
                >
                  <el-option
                    v-for="o in recentOrders"
                    :key="o.id"
                    :label="`#${o.id} / ${o.brand || '-'} ${o.model || '-'} / ${statusText(o.status)} / ${formatTime(o.created_at)}`"
                    :value="o.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="订单号">
                <el-input v-model="orderIdInput" placeholder="输入订单ID" style="width: 180px" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="loadingDetail" @click="loadByInput">查询</el-button>
              </el-form-item>
              <el-form-item>
                <el-button :loading="loadingRecent" @click="loadRecentOrders">刷新最近订单</el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-card v-loading="loadingDetail" shadow="never" class="result-card">
            <template #header>
              <div class="result-header">
                <div>分析结果</div>
                <div class="result-actions" v-if="detail?.id">
                  <el-button size="small" type="primary" plain @click="goDetail">打开质检详情</el-button>
                  <el-button size="small" :loading="refreshingMl" @click="refreshMl">重新计算</el-button>
                </div>
              </div>
            </template>

            <div v-if="!detail?.id" style="color: #909399; padding: 12px">
              请选择或输入一个回收订单，然后点击“查询”。
            </div>

            <template v-else>
              <el-descriptions :column="2" border style="margin-bottom: 16px">
                <el-descriptions-item label="订单号">#{{ detail.id }}</el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="statusTagType(detail.status)">{{ statusText(detail.status) }}</el-tag>
                  <el-tag v-if="detail.payment_status === 'failed'" type="danger" style="margin-left: 8px">打款失败</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="机型">
                  {{ detail.device_type || '-' }} / {{ detail.brand || '-' }} / {{ detail.model || '-' }} / {{ detail.storage || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="成色">{{ conditionText(detail.condition) }}</el-descriptions-item>
                <el-descriptions-item label="预估价">¥{{ detail.estimated_price ?? '-' }}</el-descriptions-item>
                <el-descriptions-item label="最终价">¥{{ detail.final_price ?? '-' }}</el-descriptions-item>
              </el-descriptions>

              <div v-if="detail.ml" class="ml-block">
                <el-descriptions :column="3" border>
                  <el-descriptions-item label="建议回收价">
                    <span class="big">¥{{ detail.ml.suggested_final_price }}</span>
                    <el-tag size="small" type="info" style="margin-left: 8px">{{ detail.ml.model_version }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="建议区间">
                    <span v-if="detail.ml.suggested_range?.length === 2">¥{{ detail.ml.suggested_range[0] }} ~ ¥{{ detail.ml.suggested_range[1] }}</span>
                    <span v-else style="color: #909399">-</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="异议风险">
                    <el-tag :type="riskTagType(detail.ml.risk_dispute)">{{ formatRisk(detail.ml.risk_dispute) }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="取消风险">
                    <el-tag :type="riskTagType(detail.ml.risk_cancel)">{{ formatRisk(detail.ml.risk_cancel) }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="关键因素" :span="2">
                    <span v-if="detail.ml.top_factors?.length">
                      {{ detail.ml.top_factors.map((f) => `${f.label}：${f.value}`).join('；') }}
                    </span>
                    <span v-else style="color: #909399">-</span>
                  </el-descriptions-item>
                </el-descriptions>
              </div>

              <el-alert
                v-else
                type="warning"
                show-icon
                title="未返回智能分析结果"
                description="该订单可能缺少必要字段，或后端在线推理发生异常。可点击“重新计算”尝试。"
              />
            </template>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import adminApi from '@/utils/adminApi'
import * as echarts from 'echarts'

const router = useRouter()

const activeTab = ref('batch')

const recentOrders = ref([])
const loadingRecent = ref(false)
const selectedOrderId = ref(null)
const orderIdInput = ref('')

const detail = ref(null)
const loadingDetail = ref(false)
const refreshingMl = ref(false)

// batch analysis
const batchDateRange = ref([])
const batchStatuses = ref([])
const summary = ref(null)
const loadingSummary = ref(false)

const batchRows = ref([])
const loadingBatch = ref(false)
const batchPage = ref(1)
const batchPageSize = ref(20)
const batchTotal = ref(0)

const riskDisputeEl = ref(null)
const gapEl = ref(null)
let riskDisputeChart = null
let gapChart = null

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const formatMoney = (v) => {
  const n = Number(v)
  if (!Number.isFinite(n)) return '-'
  return n.toFixed(2)
}

const statusText = (status) => {
  const mapping = {
    pending: '待寄出',
    shipped: '已寄出',
    received: '已收货',
    inspected: '已检测',
    completed: '已完成',
    cancelled: '已取消'
  }
  return mapping[status] || status || '-'
}

const statusTagType = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'inspected') return 'warning'
  if (status === 'cancelled') return 'danger'
  return 'info'
}

const conditionText = (c) => {
  const mapping = { new: '全新', like_new: '近新', good: '良好', fair: '一般', poor: '较差' }
  return mapping[c] || c || '-'
}

const riskTagType = (risk) => {
  const r = Number(risk || 0)
  if (r >= 0.7) return 'danger'
  if (r >= 0.4) return 'warning'
  return 'success'
}

const formatRisk = (risk) => `${Math.round(Number(risk || 0) * 100)}%`

const toYmd = (d) => {
  if (!d) return null
  return String(d)
}

const buildBatchParams = () => {
  const [d1, d2] = batchDateRange.value || []
  return {
    statuses: (batchStatuses.value || []).join(','),
    date_from: d1 || null,
    date_to: d2 || null
  }
}

const loadRecentOrders = async () => {
  loadingRecent.value = true
  try {
    const res = await adminApi.get('/inspection-orders', { params: { page: 1, page_size: 20 } })
    recentOrders.value = res.data?.results || []
  } catch (e) {
    ElMessage.error('加载最近订单失败')
  } finally {
    loadingRecent.value = false
  }
}

const loadSummary = async () => {
  loadingSummary.value = true
  try {
    const res = await adminApi.get('/recycle-ml/summary', { params: { ...buildBatchParams(), max_items: 2000 } })
    if (res.data?.success) {
      summary.value = res.data
      await nextTick()
      renderCharts()
    } else {
      ElMessage.error(res.data?.detail || '加载概览失败')
    }
  } catch (e) {
    ElMessage.error('加载概览失败')
  } finally {
    loadingSummary.value = false
  }
}

const loadBatch = async () => {
  loadingBatch.value = true
  try {
    const res = await adminApi.get('/recycle-ml/batch', {
      params: { ...buildBatchParams(), page: batchPage.value, page_size: batchPageSize.value }
    })
    if (res.data?.success) {
      batchRows.value = res.data.results || []
      batchTotal.value = res.data.count || 0
    } else {
      ElMessage.error(res.data?.detail || '加载列表失败')
    }
  } catch (e) {
    ElMessage.error('加载列表失败')
  } finally {
    loadingBatch.value = false
  }
}

const reloadBatchAll = async () => {
  batchPage.value = 1
  await Promise.all([loadSummary(), loadBatch()])
}

const handleBatchSizeChange = async () => {
  batchPage.value = 1
  await loadBatch()
}

const loadDetail = async (id) => {
  if (!id) return
  loadingDetail.value = true
  try {
    const res = await adminApi.get(`/inspection-orders/${id}`)
    if (res.data?.success) {
      detail.value = res.data.item || null
    } else {
      detail.value = null
      ElMessage.error('订单不存在或无权限')
    }
  } catch (e) {
    detail.value = null
    ElMessage.error('加载订单详情失败')
  } finally {
    loadingDetail.value = false
  }
}

const handleSelectOrder = async (id) => {
  if (!id) return
  orderIdInput.value = String(id)
  await loadDetail(id)
}

const loadByInput = async () => {
  const raw = String(orderIdInput.value || '').trim()
  if (!raw) {
    ElMessage.warning('请输入订单ID')
    return
  }
  const id = Number(raw)
  if (!Number.isFinite(id) || id <= 0) {
    ElMessage.warning('订单ID格式不正确')
    return
  }
  selectedOrderId.value = id
  await loadDetail(id)
}

const refreshMl = async () => {
  if (!detail.value?.id) return
  refreshingMl.value = true
  try {
    const res = await adminApi.get('/recycle-ml/predict', { params: { order_id: detail.value.id } })
    if (res.data?.success && res.data?.ml) {
      detail.value = { ...(detail.value || {}), ml: res.data.ml }
      ElMessage.success('已重新计算')
    } else {
      ElMessage.error(res.data?.detail || '重新计算失败')
    }
  } catch (e) {
    ElMessage.error('重新计算失败')
  } finally {
    refreshingMl.value = false
  }
}

const goDetail = () => {
  if (!detail.value?.id) return
  router.push(`/admin/inspection-orders/${detail.value.id}`)
}

const goDetailById = (id) => {
  if (!id) return
  router.push(`/admin/inspection-orders/${id}`)
}

const ensureCharts = () => {
  if (riskDisputeEl.value && !riskDisputeChart) {
    riskDisputeChart = echarts.init(riskDisputeEl.value)
  }
  if (gapEl.value && !gapChart) {
    gapChart = echarts.init(gapEl.value)
  }
}

const renderCharts = () => {
  if (!summary.value?.distributions) return
  ensureCharts()

  const rd = summary.value.distributions?.risk_dispute_bins
  const gap = summary.value.distributions?.gap_ratio_bins

  if (riskDisputeChart && rd?.counts?.length) {
    const x = rd.bins.slice(0, -1).map((b, idx) => `${Math.round(b * 100)}~${Math.round(rd.bins[idx + 1] * 100)}%`)
    riskDisputeChart.setOption({
      grid: { left: 36, right: 16, top: 18, bottom: 30 },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: x, axisLabel: { interval: 1, rotate: 30 } },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: rd.counts, itemStyle: { color: '#409eff' } }]
    })
  }

  if (gapChart && gap?.counts?.length) {
    const x = gap.bins.slice(0, -1).map((b, idx) => `${Math.round(b * 100)}~${Math.round(gap.bins[idx + 1] * 100)}%`)
    gapChart.setOption({
      grid: { left: 36, right: 16, top: 18, bottom: 30 },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: x, axisLabel: { interval: 1, rotate: 30 } },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: gap.counts, itemStyle: { color: '#67c23a' } }]
    })
  }
}

onMounted(async () => {
  await loadRecentOrders()
  await reloadBatchAll()
})

onBeforeUnmount(() => {
  if (riskDisputeChart) {
    riskDisputeChart.dispose()
    riskDisputeChart = null
  }
  if (gapChart) {
    gapChart.dispose()
    gapChart = null
  }
})
</script>

<style scoped>
.header-card {
  margin-bottom: 16px;
}

.header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.title {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.2;
}

.desc {
  margin-top: 6px;
  color: #6b7280;
  font-size: 13px;
}

.controls {
  padding-top: 6px;
}

.batch-controls {
  padding-top: 6px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.summary-card {
  border: 1px solid #eef0f4;
}

.summary-title {
  color: #6b7280;
  font-size: 12px;
}

.summary-value {
  margin-top: 6px;
  font-size: 22px;
  font-weight: 800;
}

.summary-sub {
  margin-top: 4px;
  color: #9aa3af;
  font-size: 12px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.chart-card {
  border: 1px solid #eef0f4;
}

.chart {
  height: 260px;
  width: 100%;
}

.tables-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.table-card {
  border: 1px solid #eef0f4;
}

.batch-table-card {
  margin-top: 12px;
  border: 1px solid #eef0f4;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.big {
  font-size: 18px;
  font-weight: 700;
}

.ml-block {
  margin-top: 12px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

@media (max-width: 1200px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
  .tables-row {
    grid-template-columns: 1fr;
  }
}
</style>
