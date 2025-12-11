<template>
  <div class="verified-device-inventory admin-page">
    <div class="page-header">
      <div>
        <div class="page-title">官方验库存（SN 级）</div>
        <div class="page-desc">单台设备管理：状态流转、上架、锁定/解锁、条码</div>
      </div>
      <el-space>
        <el-button :loading="loading" @click="handleRefresh" text :icon="Refresh">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDevice">新增设备</el-button>
      </el-space>
    </div>

    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="search"
            placeholder="SN / 品牌 / 型号"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="statusFilter" placeholder="全部" clearable style="width: 160px" @change="handleSearch">
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
        <el-form-item>
          <el-space>
            <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <div class="table-toolbar">
        <div class="table-meta">
          <span>共 {{ pagination.total }} 条</span>
          <span v-if="statusFilter">· 状态：{{ statusFilter }}</span>
          <span v-if="search">· 关键词：{{ search }}</span>
        </div>
        <el-space>
          <el-button text :icon="Refresh" @click="handleRefresh">刷新</el-button>
          <el-dropdown @command="cmd => handleBatchAction(cmd)">
            <el-button type="primary" plain :disabled="selected.length === 0">
              批量操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="lock">批量锁定</el-dropdown-item>
                <el-dropdown-item command="unlock">批量解锁</el-dropdown-item>
                <el-dropdown-item command="ready">批量待上架</el-dropdown-item>
                <el-dropdown-item command="sold">批量已售</el-dropdown-item>
                <el-dropdown-item command="remove">批量下架</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-space>
      </div>

      <el-table
        :data="devices"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="sn" label="SN/序列号" width="180" show-overflow-tooltip />
        <el-table-column label="设备" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="title">{{ row.brand }} {{ row.model }}</div>
            <div class="sub">{{ row.storage }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="condition" label="成色" width="90" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="location" label="仓位" width="120" />
        <el-table-column prop="suggested_price" label="建议价" width="110" align="right">
          <template #default="{ row }">
            <span v-if="row.suggested_price">¥{{ row.suggested_price }}</span>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="linked_product" label="关联商品" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.linked_product" type="success" size="small">已关联</el-tag>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="380" fixed="right">
          <template #default="{ row }">
            <el-space wrap>
              <el-button size="small" @click="openDetail(row)">详情</el-button>
              <el-button size="small" type="primary" @click="listProduct(row)">一键上架</el-button>
              <el-dropdown @command="cmd => handleAction(row, cmd)">
                <el-button size="small">
                  状态 <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="lock">锁定</el-dropdown-item>
                    <el-dropdown-item command="unlock">解锁</el-dropdown-item>
                    <el-dropdown-item command="ready">待上架</el-dropdown-item>
                    <el-dropdown-item command="repair">维修中</el-dropdown-item>
                    <el-dropdown-item command="sold">已售出</el-dropdown-item>
                    <el-dropdown-item command="remove">下架</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button size="small" @click="downloadBarcode(row)">条码</el-button>
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
          <el-descriptions-item label="SN/序列号">{{ currentDevice.sn }}</el-descriptions-item>
          <el-descriptions-item label="IMEI">{{ currentDevice.imei || '—' }}</el-descriptions-item>
          <el-descriptions-item label="品牌">{{ currentDevice.brand }}</el-descriptions-item>
          <el-descriptions-item label="型号">{{ currentDevice.model }}</el-descriptions-item>
          <el-descriptions-item label="容量">{{ currentDevice.storage }}</el-descriptions-item>
          <el-descriptions-item label="成色">{{ currentDevice.condition }}</el-descriptions-item>
          <el-descriptions-item label="仓位">{{ currentDevice.location || '—' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ currentDevice.status }}</el-descriptions-item>
          <el-descriptions-item label="建议售价">
            <span v-if="currentDevice.suggested_price">¥{{ currentDevice.suggested_price }}</span>
            <span v-else>—</span>
          </el-descriptions-item>
          <el-descriptions-item label="关联商品">
            <span v-if="currentDevice.linked_product">商品ID {{ currentDevice.linked_product }}</span>
            <span v-else>—</span>
          </el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <div class="section-title">质检/备注</div>
        <p class="note">{{ currentDevice.inspection_note || '—' }}</p>
      </div>
    </el-dialog>

    <!-- 新增设备（与商品页复用逻辑） -->
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
          <el-input-number v-model="deviceForm.suggested_price" :min="0" :precision="2" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注/质检">
          <el-input v-model="deviceForm.inspection_note" type="textarea" :rows="3" placeholder="可填质检要点/备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDeviceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createDeviceLoading" @click="submitCreateDevice">保存</el-button>
      </template>
    </el-dialog>

    <!-- 一键上架 -->
    <el-dialog
      v-model="quickListDialogVisible"
      title="一键上架"
      width="520px"
      destroy-on-close
    >
      <div class="quick-form" v-if="currentDevice">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="设备">{{ currentDevice.brand }} {{ currentDevice.model }} {{ currentDevice.storage }}</el-descriptions-item>
          <el-descriptions-item label="SN">{{ currentDevice.sn }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ currentDevice.status }}</el-descriptions-item>
        </el-descriptions>
        <el-form :inline="true" style="margin-top: 12px;">
          <el-form-item label="售价">
            <el-input-number v-model="quickPrice" :min="0.01" :precision="2" />
          </el-form-item>
          <el-form-item label="原价">
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
const pagination = ref({ current: 1, pageSize: 20, total: 0 })
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

const loadDevices = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize
    }
    if (search.value) params.search = search.value
    if (statusFilter.value) params.status = statusFilter.value
    const res = await adminApi.get('/verified-devices/', { params })
    devices.value = res.data?.results || []
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

const handleRefresh = () => {
  loadDevices()
}

const openDetail = (row) => {
  currentDevice.value = row
  detailDialogVisible.value = true
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
  // 简化：生成一个包含 SN 的文本供演示
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

