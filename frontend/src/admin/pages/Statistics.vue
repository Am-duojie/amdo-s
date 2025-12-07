<template>
  <div class="statistics-page">
    <h2 style="margin-bottom: 20px">统计分析</h2>

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

    <!-- 核心指标 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">回收订单总数</div>
          <div class="stat-value">{{ stats.recycleOrdersTotal || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">已完成回收</div>
          <div class="stat-value">{{ stats.recycleCompleted || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">官方验订单总数</div>
          <div class="stat-value">{{ stats.verifiedOrdersTotal || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">总GMV</div>
          <div class="stat-value">¥{{ formatMoney(stats.totalGMV || 0) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 订单趋势 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <span>订单趋势</span>
      </template>
      <div id="order-trend-chart" style="height: 300px"></div>
    </el-card>

    <!-- 详细统计表格 -->
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>详细统计</span>
          <el-button type="primary" @click="exportStatistics">导出数据</el-button>
        </div>
      </template>
      <el-table :data="statsTable" border>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="recycleOrders" label="回收订单" width="100" />
        <el-table-column prop="verifiedOrders" label="官方验订单" width="120" />
        <el-table-column prop="revenue" label="收入" width="120">
          <template #default="{ row }">
            ¥{{ formatMoney(row.revenue) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'

const dateRange = ref([])
const stats = ref({})
const statsTable = ref([])

const setDateRange = (type) => {
  const today = new Date()
  const formatDate = (d) => {
    return d.toISOString().split('T')[0]
  }
  
  switch (type) {
    case 'today':
      dateRange.value = [formatDate(today), formatDate(today)]
      break
    case 'week':
      const weekAgo = new Date(today)
      weekAgo.setDate(today.getDate() - 7)
      dateRange.value = [formatDate(weekAgo), formatDate(today)]
      break
    case 'month':
      const monthAgo = new Date(today)
      monthAgo.setDate(today.getDate() - 30)
      dateRange.value = [formatDate(monthAgo), formatDate(today)]
      break
    case 'all':
      dateRange.value = []
      break
  }
  loadStatistics()
}

const loadStatistics = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await adminApi.get('/statistics', { params })
    stats.value = res.data || {}
    // 这里可以处理统计数据
  } catch (error) {
    // 统计接口可能还未实现，先忽略错误
  }
}

const exportStatistics = () => {
  ElMessage.info('导出功能开发中')
}

const formatMoney = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

onMounted(() => {
  setDateRange('month')
  loadStatistics()
})
</script>

<style scoped>
.statistics-page {
  padding: 0;
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
</style>








