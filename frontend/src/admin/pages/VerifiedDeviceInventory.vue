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
            type="success"
            size="small"
            :icon="Upload"
            @click="openImportFromRecycle"
          >
            从回收订单入库
          </el-button>
          <el-button
            v-if="hasPerm('verified:write')"
            type="primary"
            size="small"
            :icon="Plus"
            @click="openCreate"
          >
            手动新增库存设备
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
          <el-descriptions-item label="运行内存">{{ currentDevice.ram || '—' }}</el-descriptions-item>
          <el-descriptions-item label="版本/地区">{{ currentDevice.version || '—' }}</el-descriptions-item>
          <el-descriptions-item label="颜色">{{ currentDevice.color || '—' }}</el-descriptions-item>
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
        <el-form-item label="SN/序列号" required>
          <el-input
            v-model="deviceForm.sn"
            placeholder="请填写唯一的 SN/序列号"
          />
        </el-form-item>
        <el-form-item label="IMEI/MEID">
          <el-input v-model="deviceForm.imei" placeholder="可选" />
        </el-form-item>
        <el-form-item label="品牌" required>
          <el-input v-model="deviceForm.brand" placeholder="例：Apple" @blur="resolveTemplateForForm" />
        </el-form-item>
        <el-form-item label="型号" required>
          <el-input v-model="deviceForm.model" placeholder="例：iPhone 14 Pro" @blur="resolveTemplateForForm" />
        </el-form-item>
        <el-form-item label="容量" required>
          <el-select
            v-model="deviceForm.storage"
            placeholder="请选择（来源：机型模板）"
            style="width: 100%;"
            :disabled="!templateResolved"
          >
            <el-option
              v-for="s in (templateInfo?.storages || [])"
              :key="s"
              :label="s"
              :value="s"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="运行内存">
          <el-select
            v-model="deviceForm.ram"
            filterable
            clearable
            placeholder="请选择（来源：机型模板）"
            style="width: 100%;"
            :disabled="!templateResolved || (templateInfo?.ram_options || []).length === 0"
          >
            <el-option
              v-for="s in (templateInfo?.ram_options || [])"
              :key="s"
              :label="s"
              :value="s"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="版本/地区">
          <el-select
            v-model="deviceForm.version"
            filterable
            clearable
            placeholder="请选择（来源：机型模板）"
            style="width: 100%;"
            :disabled="!templateResolved || (templateInfo?.version_options || []).length === 0"
          >
            <el-option
              v-for="s in (templateInfo?.version_options || [])"
              :key="s"
              :label="s"
              :value="s"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="颜色">
          <el-select
            v-model="deviceForm.color"
            filterable
            clearable
            placeholder="请选择（来源：机型模板）"
            style="width: 100%;"
            :disabled="!templateResolved || (templateInfo?.color_options || []).length === 0"
          >
            <el-option
              v-for="s in (templateInfo?.color_options || [])"
              :key="s"
              :label="s"
              :value="s"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="templateResolveError">
          <el-alert
            :title="templateResolveError"
            type="warning"
            :closable="false"
            show-icon
          />
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
        <el-button type="primary" :loading="formLoading" :disabled="!templateResolved" @click="submitForm">
          {{ editingDevice ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="importDialogVisible"
      title="从回收订单入库"
      width="920px"
      destroy-on-close
    >
      <div class="import-toolbar">
        <el-input
          v-model="importSearch"
          placeholder="输入 订单号 / 用户 / 品牌 / 型号 关键词"
          clearable
          style="width: 360px"
          @keyup.enter="loadImportOrders"
          @clear="loadImportOrders"
        />
        <el-button type="primary" :loading="importLoading" @click="loadImportOrders">查询订单</el-button>
        <span class="import-hint">默认仅显示“已完成且未入库”的回收订单，可多选批量入库</span>
      </div>

      <el-table
        :data="importOrders"
        v-loading="importLoading"
        stripe
        style="width: 100%"
        @selection-change="handleImportSelectionChange"
        empty-text="暂无可入库的回收订单"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="订单号" width="110">
          <template #default="{ row }">
            <span class="sn-text">#{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column label="用户" width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.user?.username || '-' }}</template>
        </el-table-column>
        <el-table-column label="设备信息" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="product-title">{{ row.brand }} {{ row.model }}</div>
            <div class="product-sub">{{ row.storage }} · {{ getConditionText(row.condition) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="回收成本" width="120" align="right">
          <template #default="{ row }">
            <span v-if="row.total_price">¥{{ row.total_price }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="SN/序列号" width="200">
          <template #default="{ row }">
            <el-input v-model="importDraft(row.id).sn" placeholder="必填" size="small" clearable />
          </template>
        </el-table-column>
        <el-table-column label="IMEI/MEID" width="200">
          <template #default="{ row }">
            <el-input v-model="importDraft(row.id).imei" placeholder="可选" size="small" clearable />
          </template>
        </el-table-column>
      </el-table>

      <div class="import-footer">
        <div class="import-meta">已选择 {{ importSelected.length }} 条</div>
        <div class="import-defaults">
          <span class="import-default-label">默认仓位</span>
          <el-input v-model="importDefaults.location" placeholder="可选，入库后可再编辑" style="width: 220px" />
          <span class="import-default-label">建议售价</span>
          <el-input-number
            v-model="importDefaults.suggested_price"
            :min="0"
            :precision="2"
            controls-position="right"
            style="width: 220px"
            placeholder="可选（留空=按订单成本）"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importSubmitting" @click="submitImport">
          一键入库（选订单）
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
import { Search, Refresh, Plus, Box, Upload } from '@element-plus/icons-vue'

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
const importDialogVisible = ref(false)
const importLoading = ref(false)
const importSubmitting = ref(false)
const importSearch = ref('')
const importOrders = ref([])
const importSelected = ref([])
const importDrafts = reactive({})
const importDefaults = reactive({
  location: '',
  suggested_price: null
})

const templateInfo = ref(null)
const templateResolveError = ref('')
const templateResolved = computed(() => !!templateInfo.value?.id)

const deviceForm = reactive({
  template_id: null,
  sn: '',
  imei: '',
  brand: '',
  model: '',
  storage: '',
  ram: '',
  version: '',
  color: '',
  condition: 'good',
  location: '',
  suggested_price: null,
  inspection_note: ''
})

const resolveTemplateForForm = async () => {
  templateResolveError.value = ''
  templateInfo.value = null
  deviceForm.template_id = null

  const brand = (deviceForm.brand || '').trim()
  const model = (deviceForm.model || '').trim()
  if (!brand || !model) return

  try {
    const res = await adminApi.get('/recycle-templates/resolve', { params: { brand, model } })
    templateInfo.value = res.data
    deviceForm.template_id = res.data?.id || null

    const t = res.data || {}
    const ensureIn = (val, options) => (options || []).includes(val) ? val : ''

    if ((t.storages || []).length === 1) deviceForm.storage = deviceForm.storage || t.storages[0]
    else deviceForm.storage = ensureIn(deviceForm.storage, t.storages)

    if ((t.ram_options || []).length === 1) deviceForm.ram = deviceForm.ram || t.ram_options[0]
    else deviceForm.ram = ensureIn(deviceForm.ram, t.ram_options)

    if ((t.version_options || []).length === 1) deviceForm.version = deviceForm.version || t.version_options[0]
    else deviceForm.version = ensureIn(deviceForm.version, t.version_options)

    if ((t.color_options || []).length === 1) deviceForm.color = deviceForm.color || t.color_options[0]
    else deviceForm.color = ensureIn(deviceForm.color, t.color_options)
  } catch (error) {
    templateResolveError.value = error?.response?.data?.detail || '未找到机型模板（请先创建并启用）'
  }
}

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
  templateInfo.value = null
  templateResolveError.value = ''
  Object.assign(deviceForm, {
    template_id: null,
    sn: '',
    imei: '',
    brand: '',
    model: '',
    storage: '',
    ram: '',
    version: '',
    color: '',
    condition: 'good',
    location: '',
    suggested_price: null,
    inspection_note: ''
  })
  showFormDialog.value = true
}

const openEdit = (row) => {
  editingDevice.value = row
  templateInfo.value = null
  templateResolveError.value = ''
  Object.assign(deviceForm, {
    template_id: row.template_id || null,
    sn: row.sn,
    imei: row.imei || '',
    brand: row.brand,
    model: row.model,
    storage: row.storage,
    ram: row.ram || '',
    version: row.version || '',
    color: row.color || '',
    condition: row.condition,
    location: row.location || '',
    suggested_price: row.suggested_price,
    inspection_note: row.inspection_note || ''
  })
  resolveTemplateForForm()
  showFormDialog.value = true
}

const submitForm = async () => {
  if (!deviceForm.sn) {
    ElMessage.warning('请填写 SN/序列号')
    return
  }
  if (!deviceForm.brand || !deviceForm.model || !deviceForm.storage) {
    ElMessage.warning('请填写必填项')
    return
  }

  formLoading.value = true
  try {
    if (editingDevice.value) {
      const payload = { ...deviceForm }
      await adminApi.patch(`/verified-devices/${editingDevice.value.id}/`, payload)
      ElMessage.success('更新成功')
    } else {
      const payload = { ...deviceForm }
      await adminApi.post('/verified-devices/', payload)
      ElMessage.success('创建成功')
    }
    showFormDialog.value = false
    await loadDevices()
  } catch (error) {
    const data = error?.response?.data
    const msg =
      data?.detail ||
      data?.template_id ||
      data?.storage ||
      data?.ram ||
      data?.version ||
      data?.color ||
      (data && typeof data === 'object' ? Object.values(data).flat()?.[0] : null) ||
      '操作失败'
    ElMessage.error(msg)
  } finally {
    formLoading.value = false
  }
}

const resetForm = () => {
  editingDevice.value = null
}

const openImportFromRecycle = async () => {
  importDialogVisible.value = true
  await loadImportOrders()
}

const loadImportOrders = async () => {
  importLoading.value = true
  try {
    const res = await adminApi.get('/verified-devices/available-recycle-orders/', {
      params: { page: 1, page_size: 50, search: importSearch.value || '' }
    })
    importOrders.value = res.data?.results || []
    for (const row of importOrders.value) {
      if (!importDrafts[row.id]) {
        importDrafts[row.id] = { sn: '', imei: '' }
      }
    }
  } catch (e) {
    importOrders.value = []
  } finally {
    importLoading.value = false
  }
}

const handleImportSelectionChange = (selection) => {
  importSelected.value = selection || []
}

const importDraft = (orderId) => {
  if (!importDrafts[orderId]) {
    importDrafts[orderId] = { sn: '', imei: '' }
  }
  return importDrafts[orderId]
}

const submitImport = async () => {
  if (!importSelected.value.length) {
    ElMessage.warning('请先选择要入库的回收订单')
    return
  }
  for (const row of importSelected.value) {
    const d = importDraft(row.id)
    if (!d.sn || !String(d.sn).trim()) {
      ElMessage.warning(`请填写订单 #${row.id} 的 SN/序列号`)
      return
    }
  }

  importSubmitting.value = true
  try {
    const tasks = importSelected.value.map((row) => {
      const d = importDraft(row.id)
      const suggested =
        importDefaults.suggested_price !== null && importDefaults.suggested_price !== undefined && importDefaults.suggested_price !== ''
          ? importDefaults.suggested_price
          : (row.total_price ?? null)
      return adminApi.post('/verified-devices/from-recycle-order/', {
        recycle_order_id: row.id,
        sn: String(d.sn).trim(),
        imei: (d.imei || '').trim(),
        location: (importDefaults.location || '').trim(),
        suggested_price: suggested,
        inspection_note: ''
      })
    })

    const results = await Promise.allSettled(tasks)
    const ok = results.filter(r => r.status === 'fulfilled').length
    const failed = results.length - ok
    if (failed === 0) {
      ElMessage.success(`入库成功：${ok} 条`)
      importDialogVisible.value = false
    } else {
      const firstFail = results.find(r => r.status === 'rejected')
      const reason = firstFail?.reason?.response?.data?.detail || firstFail?.reason?.message || '部分订单入库失败'
      ElMessage.warning(`入库成功：${ok} 条，失败：${failed} 条（${reason}）`)
    }
    await loadDevices()
    await loadImportOrders()
  } catch (e) {
    ElMessage.error('入库失败')
  } finally {
    importSubmitting.value = false
  }
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

.import-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.import-hint {
  color: #6b7280;
  font-size: 12px;
}

.import-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.import-meta {
  color: #374151;
  font-size: 13px;
}

.import-defaults {
  display: flex;
  align-items: center;
  gap: 10px;
}

.import-default-label {
  color: #4b5563;
  font-size: 12px;
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
