<template>
  <div class="verified-device-inventory admin-page">
    <div class="header-tabs">
      <el-button size="small" plain>官方验订单</el-button>
      <el-button size="small" type="primary">官方验库存</el-button>
      <el-button size="small" plain @click="goProducts">官方验商品</el-button>
    </div>

    <div class="page-header">
      <div>
        <div class="page-title">官方验库存管理</div>
        <div class="page-desc">审核、上架、批量操作与详情查看</div>
      </div>
      <el-space>
        <el-button :loading="loading" @click="loadDevices" text :icon="Refresh">刷新</el-button>
        <el-button type="success" plain @click="openQuickList">一键上架（选设备）</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDevice">新增设备</el-button>
      </el-space>
    </div>

    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="状态">
          <el-select v-model="statusFilter" placeholder="全部" clearable style="width: 140px" @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="待处理" value="pending" />
            <el-option label="维修/翻新中" value="repairing" />
            <el-option label="待上架" value="ready" />
            <el-option label="在售" value="listed" />
            <el-option label="已锁定" value="locked" />
            <el-option label="已售出" value="sold" />
            <el-option label="已下架" value="removed" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键字">
          <el-input
            v-model="search"
            placeholder="标题 / 品牌 / 型号"
            clearable
            style="width: 260px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-space>
            <el-button type="warning" :icon="Search" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <div class="table-toolbar">
        <div class="table-meta">
          <span>共 {{ pagination.total }} 条</span>
          <span v-if="statusFilter">· 状态：{{ statusText(statusFilter) }}</span>
          <span v-if="search">· 关键字：{{ search }}</span>
        </div>
        <el-space>
          <el-button text :icon="Refresh" @click="loadDevices">刷新</el-button>
          <el-button type="success" plain @click="openQuickList" :disabled="selected.length === 0">一键上架（选设备）</el-button>
        </el-space>
      </div>

      <el-table
        :data="devices"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="商品信息" min-width="320" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="title">{{ row.brand }} {{ row.model }} {{ row.storage }}</div>
            <div class="sub">模板：{{ row.template_name || '—' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="suggested_price" label="价格" width="140" align="right">
          <template #default="{ row }">
            <span class="price">¥{{ displayPrice(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="condition" label="成色" width="110">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ statusText(row.condition) || row.condition }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="linked_product_id" label="销量" width="90">
          <template #default="{ row }">
            <span>{{ row.sales_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-space wrap>
              <el-button size="small" @click="openDetail(row)">详情</el-button>
              <el-button size="small" type="primary" @click="listProduct(row)">编辑</el-button>
              <el-button size="small" type="warning" @click="handleAction(row, 'remove')">下架</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer">
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
    </el-card>

    <!-- 设备详情 -->
    <el-dialog v-model="detailDialogVisible" title="设备详情" width="720px" destroy-on-close>
      <div v-if="currentDevice">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="SN">{{ currentDevice.sn }}</el-descriptions-item>
          <el-descriptions-item label="IMEI">{{ currentDevice.imei || '—' }}</el-descriptions-item>
          <el-descriptions-item label="品牌">{{ currentDevice.brand }}</el-descriptions-item>
          <el-descriptions-item label="型号">{{ currentDevice.model }}</el-descriptions-item>
          <el-descriptions-item label="容量">{{ currentDevice.storage }}</el-descriptions-item>
          <el-descriptions-item label="成色">{{ statusText(currentDevice.condition) || currentDevice.condition }}</el-descriptions-item>
          <el-descriptions-item label="模板">{{ currentDevice.template_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="类目">{{ currentDevice.category_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="仓位">{{ currentDevice.location || '—' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusTagType(currentDevice.status)" size="small">{{ statusText(currentDevice.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="建议售价">
            <span v-if="currentDevice.suggested_price">¥{{ currentDevice.suggested_price }}</span>
            <span v-else>—</span>
          </el-descriptions-item>
          <el-descriptions-item label="关联商品">
            <span v-if="currentDevice.linked_product_id">商品ID {{ currentDevice.linked_product_id }}</span>
            <span v-else>—</span>
          </el-descriptions-item>
          <el-descriptions-item label="入库时间">{{ currentDevice.created_at }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <div class="section-title">质检/备注</div>
        <p class="note">{{ currentDevice.inspection_note || '—' }}</p>
      </div>
    </el-dialog>

    <!-- 新增设备 -->
    <el-dialog
      v-model="createDeviceDialogVisible"
      title="新增官方验库存设备"
      width="520px"
      destroy-on-close
    >
      <el-form :model="deviceForm" label-width="100px" :inline="false">
        <el-form-item label="演示模式">
          <el-switch v-model="autoGenerateSn" active-text="自动生成SN/IMEI" inactive-text="手动填写" />
        </el-form-item>
        <el-form-item label="SN/序列号">
          <el-input v-model="deviceForm.sn" placeholder="留空则自动生成" :disabled="autoGenerateSn" />
        </el-form-item>
        <el-form-item label="IMEI/MEID">
          <el-input v-model="deviceForm.imei" placeholder="可选" />
        </el-form-item>
        <el-form-item label="品牌/型号">
          <el-input v-model="deviceForm.brand" placeholder="品牌" style="width: 45%; margin-right: 10px;" />
          <el-input v-model="deviceForm.model" placeholder="型号" style="width: 45%;" />
        </el-form-item>
        <el-form-item label="容量/成色">
          <el-input v-model="deviceForm.storage" placeholder="如 128GB" style="width: 45%; margin-right: 10px;" />
          <el-select v-model="deviceForm.condition" style="width: 45%;">
            <el-option label="99成新" value="like_new" />
            <el-option label="95成新" value="good" />
            <el-option label="9成新" value="fair" />
            <el-option label="8成新" value="poor" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓位">
          <el-input v-model="deviceForm.location" placeholder="仓库/货架位" />
        </el-form-item>
        <el-form-item label="建议售价">
          <el-input-number v-model="deviceForm.suggested_price" :min="0" :precision="2" style="width: 200px" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input type="textarea" v-model="deviceForm.inspection_note" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDeviceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createDeviceLoading" @click="submitCreateDevice">保存</el-button>
      </template>
    </el-dialog>

    <!-- 快速上架 -->
    <el-dialog v-model="quickListDialogVisible" title="一键上架（选设备）" width="420px" destroy-on-close>
      <div>
        <div class="section-title">售价设置</div>
        <el-form label-width="100px">
          <el-form-item label="售价">
            <el-input-number v-model="quickPrice" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="划线价">
            <el-input-number v-model="quickOriginalPrice" :min="0" :precision="2" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="quickListDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="quickLoading" @click="listSelectedDevice">一键上架</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus, ArrowDown } from '@element-plus/icons-vue'

const devices = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const hasProduct = ref('')
const dateRange = ref([])
const pagination = ref({ current: 1, pageSize: 20, total: 0 })
const salesFallback = (row) => (row.sales_count || 0)
const selected = ref([])

const detailDialogVisible = ref(false)
const currentDevice = ref(null)

const quickListDialogVisible = ref(false)
const quickPrice = ref(null)
const quickOriginalPrice = ref(null)
const quickLoading = ref(false)

const createDeviceDialogVisible = ref(false)
const createDeviceLoading = ref(false)
const autoGenerateSn = ref(true)
const deviceForm = reactive({
  sn: '',
  imei: '',
  brand: '',
  model: '',
  storage: '',
  condition: 'good',
  location: '',
  suggested_price: null,
  inspection_note: ''
})

const statusText = (val) => {
  const map = {
    pending: '待处理',
    repairing: '维修/翻新中',
    ready: '待上架',
    listed: '在售',
    locked: '已锁定',
    sold: '已售出',
    removed: '已下架',
    like_new: '99成新',
    good: '95成新',
    fair: '9成新',
    poor: '8成新'
  }
  return map[val] || val || ''
}
const statusTagType = (val) => {
  switch (val) {
    case 'ready':
      return 'success'
    case 'listed':
      return 'success'
    case 'locked':
      return 'warning'
    case 'sold':
      return 'info'
    case 'removed':
      return 'info'
    case 'repairing':
      return 'warning'
    default:
      return ''
  }
}

const displayPrice = (row) => {
  const price = row.suggested_price || row.cost_price || 0
  return Number(price).toFixed(2)
}

const loadDevices = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize,
      status: statusFilter.value || undefined,
      has_product: hasProduct.value || undefined,
      created_from: dateRange.value?.[0] || undefined,
      created_to: dateRange.value?.[1] || undefined,
    }
    if (search.value) {
      params.brand = search.value
      params.model = search.value
    }
    const res = await adminApi.get('/official-inventory/', { params })
    devices.value = (res.data?.results || []).map(item => ({
      ...item,
      sales_count: item.sales_count || 0
    }))
    pagination.value.total = res.data?.count || 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.value.current = 1
  loadDevices()
}

const resetFilters = () => {
  search.value = ''
  statusFilter.value = ''
  hasProduct.value = ''
  dateRange.value = []
  handleSearch()
}

const handlePageChange = () => {
  loadDevices()
}

const handleSizeChange = () => {
  pagination.value.current = 1
  loadDevices()
}

const handleSelectionChange = (rows) => {
  selected.value = rows
}

const openDetail = (row) => {
  currentDevice.value = row
  detailDialogVisible.value = true
}

const goProducts = () => {
  window.location.href = '#/admin/verified-products'
}

const openCreateDevice = () => {
  createDeviceDialogVisible.value = true
  Object.assign(deviceForm, {
    sn: '',
    imei: '',
    brand: '',
    model: '',
    storage: '',
    condition: 'good',
    location: '',
    suggested_price: null,
    inspection_note: ''
  })
  autoGenerateSn.value = true
}

const submitCreateDevice = async () => {
  createDeviceLoading.value = true
  try {
    const payload = { ...deviceForm }
    if (autoGenerateSn.value || !payload.sn) {
      delete payload.sn
    }
    await adminApi.post('/verified-devices/', payload)
    ElMessage.success('新增设备成功')
    createDeviceDialogVisible.value = false
    loadDevices()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '新增设备失败')
  } finally {
    createDeviceLoading.value = false
  }
}

const handleAction = async (row, action) => {
  try {
    await adminApi.post(`/verified-devices/${row.id}/${action}/`)
    ElMessage.success('操作成功')
    loadDevices()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  }
}

const listProduct = (row) => {
  currentDevice.value = row
  quickPrice.value = row.suggested_price || null
  quickOriginalPrice.value = null
  quickListDialogVisible.value = true
}

const listSelectedDevice = async () => {
  if (!currentDevice.value) {
    ElMessage.warning('未选择设备')
    return
  }
  if (!quickPrice.value) {
    ElMessage.warning('请输入售价')
    return
  }
  quickLoading.value = true
  try {
    await adminApi.post(`/verified-devices/${currentDevice.value.id}/list-product/`, {
      price: quickPrice.value,
      original_price: quickOriginalPrice.value
    })
    ElMessage.success('上架成功')
    quickListDialogVisible.value = false
    loadDevices()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '上架失败')
  } finally {
    quickLoading.value = false
  }
}

const downloadBarcode = (row) => {
  const data = `SN:${row.sn}`
  const blob = new Blob([data], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `barcode-${row.sn}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

const handleBatchAction = async (action) => {
  if (selected.value.length === 0) return
  try {
    await Promise.all(selected.value.map(item => adminApi.post(`/verified-devices/${item.id}/${action}/`)))
    ElMessage.success('批量操作成功')
    loadDevices()
  } catch (e) {
    ElMessage.error('批量操作失败')
  }
}

onMounted(() => {
  loadDevices()
})
</script>

<style scoped>
.verified-device-inventory {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.page-title {
  font-size: 20px;
  font-weight: 700;
}
.page-desc {
  color: #666;
  margin-top: 4px;
}
.filter-card,
.table-card {
  margin-top: 0;
}
.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.table-meta {
  color: #666;
  font-size: 13px;
}
.title {
  font-weight: 600;
}
.sub {
  color: #888;
  font-size: 12px;
}
.quick-form {
  margin-top: 12px;
}
.section-title {
  font-weight: 600;
  margin-bottom: 6px;
}
.note {
  color: #555;
  white-space: pre-wrap;
}
.is-selected {
  background: #f5f7fa;
}
</style>
