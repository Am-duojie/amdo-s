<template>
  <div class="verified-device-inventory admin-page">
    <el-card shadow="never" class="admin-card page-card">
      <div class="page-header admin-section-header">
        <div>
          <div class="page-title admin-section-title">
            <el-icon><Box /></el-icon>
            <span>官方验库存管理</span>
          </div>
          <div class="page-desc admin-section-desc">
            设备入库、质检、仓位管理与库存追踪
          </div>
        </div>
        <el-space>
          <el-button :loading="loading" text :icon="Refresh" @click="handleRefresh">刷新</el-button>
          <el-button
            v-if="hasPerm('verified:write')"
            type="primary"
            size="small"
            :icon="Plus"
            @click="openCreate"
          >
            新增库存设备
          </el-button>
        </el-space>
      </div>

      <div class="status-grid">
        <div v-for="card in statusCards" :key="card.key" class="status-card">
          <div class="status-top">
            <span class="status-label">{{ card.label }}</span>
            <el-tag :type="card.tag" size="small" effect="plain">{{ card.badge }}</el-tag>
          </div>
          <div class="status-value">{{ card.count }}</div>
          <div class="status-hint">{{ card.hint }}</div>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover" class="admin-card filter-card">
      <el-form :inline="true" class="filter-form" @submit.prevent>
        <el-form-item label="状态">
          <el-select
            v-model="statusFilter"
            placeholder="全部"
            clearable
            style="width: 160px"
            @change="handleSearch"
          >
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
            placeholder="SN / 品牌 / 型号"
            clearable
            style="width: 260px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-space>
            <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="admin-card table-card">
      <div class="table-toolbar admin-toolbar">
        <div class="admin-toolbar__meta">
          <span>共 {{ pagination.total }} 条库存</span>
          <el-tag v-if="statusFilter" size="small" effect="plain">{{ getStatusText(statusFilter) }}</el-tag>
          <el-tag v-if="search" size="small" effect="plain" type="info">关键词：{{ search }}</el-tag>
        </div>
        <el-space>
          <el-button text :icon="Refresh" @click="handleRefresh">刷新</el-button>
        </el-space>
      </div>

      <el-table
        :data="devices"
        style="width: 100%"
        v-loading="loading"
        stripe
        highlight-current-row
        @selection-change="handleSelectionChange"
        empty-text="暂无库存设备"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="SN/序列号" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="sn-text">{{ row.sn }}</div>
            <div class="sub-muted" v-if="row.imei">IMEI: {{ row.imei }}</div>
          </template>
        </el-table-column>
        <el-table-column label="设备信息" min-width="260" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="product-title">{{ row.brand }} {{ row.model }}</div>
            <div class="product-sub">{{ row.storage }} · {{ getConditionText(row.condition) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="仓位" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.location" size="small" effect="plain" type="info">{{ row.location }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="建议售价" width="120" align="right">
          <template #default="{ row }">
            <div v-if="row.suggested_price" class="price">¥{{ row.suggested_price }}</div>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关联商品" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.linked_product_id" size="small" type="success" effect="plain">已关联</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="入库时间" width="180" />
        <el-table-column label="操作" width="320" fixed="right" align="center">
          <template #default="{ row }">
            <el-space wrap>
              <el-button size="small" @click="viewDetail(row)">详情</el-button>
              <el-button
                v-if="hasPerm('verified:write')"
                size="small"
                type="primary"
                @click="openEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                v-if="hasPerm('verified:write') && row.status === 'ready' && !row.linked_product_id"
                size="small"
                type="success"
                @click="quickList(row)"
              >
                上架
              </el-button>
              <el-button
                v-if="hasPerm('verified:write') && row.status === 'pending'"
                size="small"
                type="warning"
                @click="updateStatus(row, 'ready')"
              >
                标记待上架
              </el-button>
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

    <BatchActions
      :selected-items="selectedDevices"
      @clear="selectedDevices = []"
    >
      <template #default="{ selectedItems }">
        <el-button
          v-if="hasPerm('verified:write')"
          type="success"
          @click="batchUpdateStatus(selectedItems, 'ready')"
        >
          批量标记待上架
        </el-button>
        <el-button
          v-if="hasPerm('verified:write')"
          @click="batchUpdateStatus(selectedItems, 'removed')"
        >
          批量下架
        </el-button>
      </template>
    </BatchActions>

    <el-dialog
      v-model="detailDialogVisible"
      title="设备详情"
      width="720px"
    >
      <div v-if="currentDevice">
        <div class="detail-head">
          <div>
            <div class="detail-title">{{ currentDevice.brand }} {{ currentDevice.model }} {{ currentDevice.storage }}</div>
            <div class="detail-sn">SN: {{ currentDevice.sn }}</div>
          </div>
          <el-tag :type="getStatusType(currentDevice.status)" size="small">
            {{ getStatusText(currentDevice.status) }}
          </el-tag>
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ currentDevice.id }}</el-descriptions-item>
          <el-descriptions-item label="SN/序列号">{{ currentDevice.sn }}</el-descriptions-item>
          <el-descriptions-item label="IMEI/MEID">{{ currentDevice.imei || '—' }}</el-descriptions-item>
          <el-descriptions-item label="品牌">{{ currentDevice.brand }}</el-descriptions-item>
          <el-descriptions-item label="型号">{{ currentDevice.model }}</el-descriptions-item>
          <el-descriptions-item label="容量">{{ currentDevice.storage }}</el-descriptions-item>
          <el-descriptions-item label="成色">
            {{ getConditionText(currentDevice.condition) }}
          </el-descriptions-item>
          <el-descriptions-item label="仓位">{{ currentDevice.location || '—' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentDevice.status)" size="small">
              {{ getStatusText(currentDevice.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="建议售价">
            <span v-if="currentDevice.suggested_price">¥{{ currentDevice.suggested_price }}</span>
            <span v-else>—</span>
          </el-descriptions-item>
          <el-descriptions-item label="关联商品">
            <span v-if="currentDevice.linked_product_id">
              商品ID {{ currentDevice.linked_product_id }}
            </span>
            <span v-else>—</span>
          </el-descriptions-item>
          <el-descriptions-item label="入库时间">{{ currentDevice.created_at }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <div class="section-title">质检/备注</div>
        <p class="note">{{ currentDevice.inspection_note || '—' }}</p>
      </div>
    </el-dialog>

    <el-dialog
      v-model="showFormDialog"
      :title="editingDevice ? '编辑库存设备' : '新增库存设备'"
      width="620px"
      @close="resetForm"
      destroy-on-close
    >
      <el-form :model="deviceForm" label-width="110px" :inline="false">
        <el-form-item label="演示模式" v-if="!editingDevice">
          <el-switch v-model="autoGenerateSn" active-text="自动生成SN/IMEI" inactive-text="手动填写" />
        </el-form-item>
        <el-form-item label="SN/序列号" required>
          <el-input
            v-model="deviceForm.sn"
            placeholder="留空则自动生成"
            :disabled="autoGenerateSn && !editingDevice"
          />
        </el-form-item>
        <el-form-item label="IMEI/MEID">
          <el-input v-model="deviceForm.imei" placeholder="可选" />
        </el-form-item>
        <el-form-item label="品牌" required>
          <el-input v-model="deviceForm.brand" placeholder="例：Apple" />
        </el-form-item>
        <el-form-item label="型号" required>
          <el-input v-model="deviceForm.model" placeholder="例：iPhone 14 Pro" />
        </el-form-item>
        <el-form-item label="容量" required>
          <el-input v-model="deviceForm.storage" placeholder="例：128GB" />
        </el-form-item>
        <el-form-item label="成色" required>
          <el-select v-model="deviceForm.condition" style="width: 100%;">
            <el-option label="全新" value="new" />
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
          <el-input-number
            v-model="deviceForm.suggested_price"
            :min="0"
            :precision="2"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="备注/质检">
          <el-input
            v-model="deviceForm.inspection_note"
            type="textarea"
            :rows="3"
            placeholder="可填质检要点/备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFormDialog = false">取消</el-button>
        <el-button type="primary" :loading="formLoading" @click="submitForm">
          {{ editingDevice ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="quickListDialogVisible"
      title="快速上架商品"
      width="520px"
      destroy-on-close
    >
      <div v-if="currentDevice">
        <el-alert
          title="设备信息"
          type="info"
          :closable="false"
          style="margin-bottom: 16px"
        >
          <div>{{ currentDevice.brand }} {{ currentDevice.model }} {{ currentDevice.storage }}</div>
          <div style="font-size: 12px; margin-top: 4px;">SN: {{ currentDevice.sn }}</div>
        </el-alert>
        <el-form label-width="100px">
          <el-form-item label="售价" required>
            <el-input-number
              v-model="quickPrice"
              :min="0.01"
              :precision="2"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="划线价">
            <el-input-number
              v-model="quickOriginalPrice"
              :min="0"
              :precision="2"
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="quickListDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="quickLoading" @click="confirmQuickList">
          确认上架
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminAuthStore } from '@/stores/adminAuth'
import BatchActions from './components/BatchActions.vue'
import { Search, Refresh, Plus, Box } from '@element-plus/icons-vue'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)

const devices = ref([])
const selectedDevices = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const pagination = ref({ current: 1, pageSize: 20, total: 0 })
const detailDialogVisible = ref(false)
const currentDevice = ref(null)
const showFormDialog = ref(false)
const editingDevice = ref(null)
const formLoading = ref(false)
const autoGenerateSn = ref(true)
const quickListDialogVisible = ref(false)
const quickPrice = ref(null)
const quickOriginalPrice = ref(null)
const quickLoading = ref(false)

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

const statusMap = {
  pending: { text: '待处理', type: 'warning' },
  repairing: { text: '维修/翻新中', type: 'warning' },
  ready: { text: '待上架', type: 'success' },
  listed: { text: '在售', type: 'success' },
  locked: { text: '已锁定', type: 'info' },
  sold: { text: '已售出', type: 'info' },
  removed: { text: '已下架', type: 'info' }
}

const conditionMap = {
  new: '全新',
  like_new: '99成新',
  good: '95成新',
  fair: '9成新',
  poor: '8成新'
}

const statusCards = computed(() => {
  const counts = devices.value.reduce((acc, item) => {
    acc[item.status] = (acc[item.status] || 0) + 1
    return acc
  }, {})
  return [
    {
      key: 'total',
      label: '库存总量',
      badge: '全部',
      tag: 'info',
      count: pagination.value.total,
      hint: '符合筛选条件的库存设备总数'
    },
    {
      key: 'pending',
      label: '待处理',
      badge: '质检/维修',
      tag: 'warning',
      count: counts.pending || 0,
      hint: '等待质检或维修完成'
    },
    {
      key: 'ready',
      label: '待上架',
      badge: '可立即上架',
      tag: 'success',
      count: counts.ready || 0,
      hint: '可直接创建官方验商品'
    },
    {
      key: 'listed',
      label: '在售',
      badge: '已关联商品',
      tag: 'primary',
      count: counts.listed || 0,
      hint: '已上架到官方验商品池'
    }
  ]
})

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'
const getConditionText = (condition) => conditionMap[condition] || condition

const loadDevices = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    if (search.value) {
      params.search = search.value
    }
    const res = await adminApi.get('/verified-devices/', { params })
    devices.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = () => {
  loadDevices()
}

const handleSizeChange = () => {
  pagination.value.current = 1
  loadDevices()
}

const viewDetail = (row) => {
  currentDevice.value = row
  detailDialogVisible.value = true
}

const openCreate = () => {
  editingDevice.value = null
  autoGenerateSn.value = true
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
  showFormDialog.value = true
}

const openEdit = (row) => {
  editingDevice.value = row
  Object.assign(deviceForm, {
    sn: row.sn,
    imei: row.imei || '',
    brand: row.brand,
    model: row.model,
    storage: row.storage,
    condition: row.condition,
    location: row.location || '',
    suggested_price: row.suggested_price,
    inspection_note: row.inspection_note || ''
  })
  showFormDialog.value = true
}

const submitForm = async () => {
  if (!deviceForm.brand || !deviceForm.model || !deviceForm.storage) {
    ElMessage.warning('请填写必填项')
    return
  }

  formLoading.value = true
  try {
    const payload = { ...deviceForm }
    if (!editingDevice.value && (autoGenerateSn.value || !payload.sn)) {
      delete payload.sn
    }

    if (editingDevice.value) {
      await adminApi.put(`/verified-devices/${editingDevice.value.id}/`, payload)
      ElMessage.success('更新成功')
    } else {
      await adminApi.post('/verified-devices/', payload)
      ElMessage.success('创建成功')
    }
    showFormDialog.value = false
    await loadDevices()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '操作失败')
  } finally {
    formLoading.value = false
  }
}

const resetForm = () => {
  editingDevice.value = null
}

const updateStatus = async (row, newStatus) => {
  try {
    await adminApi.patch(`/verified-devices/${row.id}/`, { status: newStatus })
    ElMessage.success('状态更新成功')
    await loadDevices()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const quickList = (row) => {
  currentDevice.value = row
  quickPrice.value = row.suggested_price || null
  quickOriginalPrice.value = null
  quickListDialogVisible.value = true
}

const confirmQuickList = async () => {
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
    await loadDevices()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '上架失败')
  } finally {
    quickLoading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedDevices.value = selection
}

const batchUpdateStatus = async (items, newStatus) => {
  try {
    const statusText = getStatusText(newStatus)
    await ElMessageBox.confirm(
      `确认将选中的 ${items.length} 个设备批量更新为“${statusText}”状态吗？`,
      '确认批量操作',
      { type: 'warning' }
    )
    const promises = items.map(item =>
      adminApi.patch(`/verified-devices/${item.id}/`, { status: newStatus })
    )
    await Promise.all(promises)
    ElMessage.success('批量操作成功')
    selectedDevices.value = []
    await loadDevices()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量操作失败')
    }
  }
}

const handleRefresh = () => {
  loadDevices()
}

const handleSearch = () => {
  pagination.value.current = 1
  loadDevices()
}

const resetFilters = () => {
  statusFilter.value = ''
  search.value = ''
  handleSearch()
}

const goOrders = () => {
  window.location.href = '#/admin/verified-orders'
}

const goProducts = () => {
  window.location.href = '#/admin/verified-products'
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

.page-card {
  padding-bottom: 8px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
}

.page-desc {
  color: #6b7280;
  font-size: 13px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.status-card {
  border: 1px solid var(--admin-border);
  border-radius: 10px;
  padding: 12px 14px;
  background: #fff;
}

.status-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.status-label {
  color: #4b5563;
  font-size: 13px;
}

.status-value {
  font-size: 26px;
  font-weight: 800;
  color: #111827;
}

.status-hint {
  color: #9ca3af;
  font-size: 12px;
  margin-top: 2px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 18px;
}

.table-card {
  border-radius: 10px;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 10px;
}

.table-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.sn-text {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #111827;
}

.product-title {
  font-weight: 600;
  color: #111827;
  line-height: 1.4;
}

.product-sub {
  color: #6b7280;
  font-size: 12px;
  margin-top: 4px;
}

.sub-muted {
  color: #9ca3af;
  font-size: 12px;
  margin-top: 2px;
}

.price {
  font-weight: 700;
  color: #f56c6c;
}

.text-muted {
  color: #909399;
}

.section-title {
  font-weight: 600;
  margin-bottom: 12px;
  font-size: 14px;
}

.note {
  color: #666;
  white-space: pre-wrap;
  line-height: 1.6;
  background: #f9fafb;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px dashed #e5e7eb;
}

.detail-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.detail-title {
  font-weight: 700;
  font-size: 16px;
}

.detail-sn {
  color: #6b7280;
  font-size: 12px;
  margin-top: 2px;
}
</style>
