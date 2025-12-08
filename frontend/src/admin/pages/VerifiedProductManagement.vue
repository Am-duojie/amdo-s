<template>
  <div class="verified-product-management admin-page">
    <div class="page-header">
      <div>
        <div class="page-title">官方验商品管理</div>
        <div class="page-desc">审核、上下架、批量操作与详情查看</div>
      </div>
      <el-space>
        <el-button :loading="loading" @click="handleRefresh" text :icon="Refresh">刷新</el-button>
        <el-button
          v-if="hasPerm('verified:write')"
          type="primary"
          :icon="Plus"
          @click="showCreateDialog = true"
        >
          新增商品
        </el-button>
      </el-space>
    </div>

    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" class="filter-form" @submit.prevent>
        <el-form-item label="状态">
          <el-select v-model="statusFilter" placeholder="全部" clearable style="width: 160px" @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="待审核" value="pending" />
            <el-option label="在售" value="active" />
            <el-option label="已售出" value="sold" />
            <el-option label="已下架" value="removed" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="search"
            placeholder="标题 / 品牌 / 型号"
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

    <el-card shadow="hover" class="table-card">
      <div class="table-toolbar">
        <div class="table-meta">
          <span>共 {{ pagination.total }} 条</span>
          <span v-if="statusFilter">· 状态：{{ getStatusText(statusFilter) }}</span>
          <span v-if="search">· 关键词：{{ search }}</span>
        </div>
        <el-space>
          <el-button text :icon="Refresh" @click="handleRefresh">刷新</el-button>
        </el-space>
      </div>

      <el-table 
        :data="products" 
        style="width: 100%" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        empty-text="暂无商品"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="商品信息" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="product-title">{{ row.title }}</div>
            <div class="product-sub">{{ row.brand }} {{ row.model }} {{ row.storage }}</div>
          </template>
        </el-table-column>
        <el-table-column label="价格" width="120" align="right">
          <template #default="{ row }">
            <div class="price">¥{{ row.price }}</div>
            <div v-if="row.original_price" class="price-origin">
              ¥{{ row.original_price }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="condition" label="成色" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ getConditionText(row.condition) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="销量" width="100" align="center">
          <template #default="{ row }">
            <div>{{ row.sales_count || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="300" fixed="right" align="center">
          <template #default="{ row }">
            <el-space wrap>
              <el-button size="small" @click="viewDetail(row)">详情</el-button>
              <el-button
                v-if="hasPerm('verified:write') && row.status === 'pending'"
                size="small"
                type="success"
                @click="updateStatus(row, 'active')"
              >
                审核通过
              </el-button>
              <el-button
                v-if="hasPerm('verified:write') && row.status === 'active'"
                size="small"
                @click="updateStatus(row, 'removed')"
              >
                下架
              </el-button>
              <el-button
                v-if="hasPerm('verified:write') && row.status === 'removed'"
                size="small"
                type="primary"
                @click="updateStatus(row, 'active')"
              >
                上架
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

    <!-- 批量操作 -->
    <BatchActions
      :selected-items="selectedProducts"
      @clear="selectedProducts = []"
    >
      <template #default="{ selectedItems, clearSelection }">
        <el-button
          v-if="hasPerm('verified:write')"
          type="success"
          @click="batchUpdateStatus(selectedItems, 'active')"
        >
          批量上架
        </el-button>
        <el-button
          v-if="hasPerm('verified:write')"
          @click="batchUpdateStatus(selectedItems, 'removed')"
        >
          批量下架
        </el-button>
      </template>
    </BatchActions>

    <!-- 商品详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="商品详情"
      width="900px"
    >
      <VerifiedProductDetail
        v-if="currentProduct"
        :product-id="currentProduct.id"
        @updated="handleProductUpdated"
      />
    </el-dialog>

    <!-- 创建商品对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新增官方验商品"
      width="800px"
      @close="resetCreateForm"
    >
      <VerifiedProductForm
        @created="handleProductCreated"
        @cancel="showCreateDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminAuthStore } from '@/stores/adminAuth'
import VerifiedProductDetail from './components/VerifiedProductDetail.vue'
import VerifiedProductForm from './components/VerifiedProductForm.vue'
import BatchActions from './components/BatchActions.vue'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)

const products = ref([])
const selectedProducts = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const pagination = ref({ current: 1, pageSize: 20, total: 0 })
const detailDialogVisible = ref(false)
const currentProduct = ref(null)
const showCreateDialog = ref(false)

const statusMap = {
  pending: { text: '待审核', type: 'warning' },
  active: { text: '在售', type: 'success' },
  sold: { text: '已售出', type: 'info' },
  removed: { text: '已下架', type: 'info' }
}

const conditionMap = {
  new: '全新',
  like_new: '99成新',
  good: '95成新'
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'
const getConditionText = (condition) => conditionMap[condition] || condition

const loadProducts = async () => {
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
    const res = await adminApi.get('/verified-listings', { params })
    products.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = () => {
  loadProducts()
}

const handleSizeChange = () => {
  pagination.value.current = 1
  loadProducts()
}

const viewDetail = (row) => {
  currentProduct.value = row
  detailDialogVisible.value = true
}

const updateStatus = async (row, newStatus) => {
  try {
    const action = newStatus === 'active' ? 'publish' : 'unpublish'
    await adminApi.post(`/verified-listings/${row.id}/${action}`)
    ElMessage.success('操作成功')
    await loadProducts()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleProductUpdated = () => {
  detailDialogVisible.value = false
  loadProducts()
}

const handleProductCreated = () => {
  showCreateDialog.value = false
  loadProducts()
}

const resetCreateForm = () => {
  // 表单重置由子组件处理
}

const handleSelectionChange = (selection) => {
  selectedProducts.value = selection
}

const batchUpdateStatus = async (items, newStatus) => {
  try {
    await ElMessageBox.confirm(
      `确认将选中的 ${items.length} 个商品批量${newStatus === 'active' ? '上架' : '下架'}吗？`,
      '确认批量操作',
      { type: 'warning' }
    )
    const promises = items.map(item => {
      const action = newStatus === 'active' ? 'publish' : 'unpublish'
      return adminApi.post(`/verified-listings/${item.id}/${action}`)
    })
    await Promise.all(promises)
    ElMessage.success('批量操作成功')
    selectedProducts.value = []
    await loadProducts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量操作失败')
    }
  }
}

onMounted(() => {
  loadProducts()
})

const handleRefresh = () => {
  loadProducts()
}

const handleSearch = () => {
  pagination.value.current = 1
  loadProducts()
}

const resetFilters = () => {
  statusFilter.value = ''
  search.value = ''
  handleSearch()
}
</script>

<style scoped>
.verified-product-management {
  display: flex;
  flex-direction: column;
  gap: 12px;
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

.filter-card {
  border-radius: 10px;
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

.table-meta {
  display: flex;
  gap: 8px;
  color: #6b7280;
  font-size: 13px;
  flex-wrap: wrap;
}

.table-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
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

.price {
  font-weight: 700;
  color: #f56c6c;
}

.price-origin {
  color: #909399;
  font-size: 12px;
  text-decoration: line-through;
}
</style>

