<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">商品管理</h2>
    </div>

    <div style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; align-items: center">
      <el-tag v-if="selectedIds.length" type="info">已选 {{ selectedIds.length }} 项</el-tag>
      <el-button
        v-if="hasPerm('product:write')"
        :disabled="!canBatchApprove"
        type="primary"
        @click="batchApprove"
      >
        批量通过审核
      </el-button>
      <el-button
        v-if="hasPerm('product:write')"
        :disabled="!canBatchUnpublish"
        @click="batchUnpublish"
      >
        批量下架
      </el-button>
      <el-button
        v-if="hasPerm('product:delete')"
        :disabled="!canBatchDelete"
        type="danger"
        @click="batchDelete"
      >
        批量删除
      </el-button>
    </div>

    <div style="display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap">
      <el-input
        v-model="search"
        placeholder="搜索商品标题、品牌、型号"
        style="width: 300px"
        clearable
        @keyup.enter="load"
      />
      <el-select v-model="statusFilter" placeholder="商品状态" style="width: 150px" clearable>
        <el-option label="全部" value="" />
        <el-option label="待审核" value="pending" />
        <el-option label="活跃" value="active" />
        <el-option label="已下架" value="removed" />
        <el-option label="已售出" value="sold" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
    </div>

    <el-table
      :data="items"
      style="width: 100%"
      :row-key="(row) => row.id"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="48" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="商品标题" min-width="200" />
      <el-table-column prop="price" label="价格" width="120">
        <template #default="{ row }">
          ¥{{ row.price }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="seller" label="卖家" width="120" />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="360" fixed="right">
        <template #default="{ row }">
          <el-space wrap>
            <el-button size="small" :disabled="row.status === 'sold'" @click="edit(row)">编辑</el-button>
            <el-button
              v-if="hasPerm('product:write') && canPublish(row)"
              size="small"
              type="primary"
              @click="row.status === 'pending' ? review(row) : doAction(row, 'publish')"
            >
              {{ row.status === 'pending' ? '通过审核' : '发布' }}
            </el-button>
            <el-button
              v-if="hasPerm('product:write') && canUnpublish(row)"
              size="small"
              @click="doAction(row, 'unpublish')"
            >
              下架
            </el-button>
            <el-button
              v-if="hasPerm('product:write') && canMarkSold(row)"
              size="small"
              type="success"
              @click="doAction(row, 'mark-sold')"
            >
              标记已售
            </el-button>
            <el-button v-if="hasPerm('product:delete')" size="small" type="danger" @click="remove(row)">删除</el-button>
          </el-space>
        </template>
      </el-table-column>
    </el-table>

    <div style="display: flex; justify-content: flex-end; margin-top: 16px">
      <el-pagination
        v-model:current-page="pagination.current"
        :total="pagination.total"
        :page-size="pagination.pageSize"
        layout="prev, pager, next, total"
        @current-change="handlePageChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'review' ? '审核商品' : '编辑商品'" width="700px">
      <el-skeleton v-if="detailLoading" :rows="6" animated />
      <el-form v-else :model="form" label-width="100px">
        <el-form-item v-if="images.length" label="图片">
          <div class="images-grid">
            <el-image
              v-for="(img, index) in images"
              :key="img.id || index"
              :src="img.image"
              :preview-src-list="previewSrcList"
              :initial-index="index"
              fit="cover"
              class="product-image-thumb"
            />
          </div>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" :disabled="dialogMode === 'review'" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="6" :disabled="dialogMode === 'review'" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" :disabled="dialogMode === 'review'" />
        </el-form-item>
        <el-form-item label="原价">
          <el-input-number v-model="form.original_price" :min="0" :precision="2" style="width: 100%" :disabled="dialogMode === 'review'" />
        </el-form-item>
        <el-form-item label="成色">
          <el-input v-model="form.condition" :disabled="dialogMode === 'review'" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%" :disabled="dialogMode === 'review'">
            <el-option label="待审核" value="pending" />
            <el-option label="活跃" value="active" />
            <el-option label="已下架" value="removed" />
            <el-option label="已售出" value="sold" />
          </el-select>
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="form.location" :disabled="dialogMode === 'review'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          v-if="dialogMode === 'review'"
          type="primary"
          :loading="reviewApproving"
          @click="approveReview"
        >
          通过审核
        </el-button>
        <el-button v-else type="primary" :loading="saving" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminAuthStore } from '@/stores/adminAuth'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)

const items = ref([])
const search = ref('')
const statusFilter = ref('')
const pagination = ref({ current: 1, pageSize: 10, total: 0 })
const dialogVisible = ref(false)
const saving = ref(false)
const currentId = ref(null)
const currentRow = ref(null)
const dialogMode = ref('edit') // edit | review
const detailLoading = ref(false)
const reviewApproving = ref(false)
const images = ref([])
const previewSrcList = ref([])
const selectedRows = ref([])

const selectedIds = computed(() => selectedRows.value.map((r) => r.id).filter(Boolean))
const canBatchApprove = computed(() => {
  if (!selectedRows.value.length) return false
  return selectedRows.value.every((r) => r.status === 'pending')
})
const canBatchUnpublish = computed(() => {
  if (!selectedRows.value.length) return false
  return selectedRows.value.every((r) => r.status !== 'sold')
})
const canBatchDelete = computed(() => {
  if (!selectedRows.value.length) return false
  return selectedRows.value.every((r) => r.status !== 'sold')
})

const form = reactive({
  title: '',
  description: '',
  price: 0,
  original_price: 0,
  condition: '',
  status: 'active',
  location: ''
})

const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    active: 'success',
    removed: 'info',
    sold: 'warning'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待审核',
    active: '活跃',
    removed: '已下架',
    sold: '已售出'
  }
  return map[status] || status
}

const canPublish = (row) => row?.status === 'pending' || row?.status === 'removed'
const canUnpublish = (row) => row?.status === 'active' || row?.status === 'pending'
const canMarkSold = (row) => row?.status === 'active'

const handleSelectionChange = (rows) => {
  selectedRows.value = rows || []
}

const load = async () => {
  try {
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize
    }
    if (search.value) {
      params.search = search.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const res = await adminApi.get('/products', { params })
    items.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
    selectedRows.value = []
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const handlePageChange = () => {
  load()
}

const loadDetail = async (id) => {
  detailLoading.value = true
  try {
    const res = await adminApi.get(`/products/${id}`)
    const data = res.data || {}
    Object.assign(form, {
      title: data.title || '',
      description: data.description || '',
      price: data.price || 0,
      original_price: data.original_price || 0,
      condition: data.condition || '',
      status: data.status || 'pending',
      location: data.location || ''
    })
    images.value = Array.isArray(data.images) ? data.images : []
    previewSrcList.value = images.value.map((i) => i.image).filter(Boolean)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '加载商品详情失败')
  } finally {
    detailLoading.value = false
  }
}

const openDialog = async (row, mode = 'edit') => {
  currentRow.value = row || null
  currentId.value = row?.id || null
  dialogMode.value = mode
  dialogVisible.value = true
  images.value = []
  previewSrcList.value = []
  if (currentId.value) {
    await loadDetail(currentId.value)
  }
}

const saveEdit = async () => {
  if (!currentId.value) return
  saving.value = true
  try {
    await adminApi.put(`/products/${currentId.value}`, form)
    ElMessage.success('更新成功')
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

const approveReview = async () => {
  if (!currentRow.value) return
  try {
    await ElMessageBox.confirm('确认通过审核并上架该商品吗？', '通过审核', { type: 'warning' })
    reviewApproving.value = true
    await adminApi.post(`/products/${currentRow.value.id}/publish`)
    ElMessage.success('已通过审核')
    dialogVisible.value = false
    await load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.detail || '操作失败')
    }
  } finally {
    reviewApproving.value = false
  }
}

const doAction = async (row, action) => {
  try {
    if (action === 'unpublish') {
      const { value } = await ElMessageBox.prompt('请输入下架原因（将展示给卖家）', '下架商品', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '例如：信息不实 / 重复发布 / 违规内容',
      })
      await adminApi.post(`/products/${row.id}/${action}`, { reason: value || '' })
    } else {
      await adminApi.post(`/products/${row.id}/${action}`)
    }
    ElMessage.success('操作成功')
    await load()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '操作失败')
  }
}

const edit = async (row) => openDialog(row, 'edit')

const review = async (row) => openDialog(row, 'review')

const batchApprove = async () => {
  if (!selectedRows.value.length) return
  try {
    await ElMessageBox.confirm(`确认通过审核并上架选中的 ${selectedRows.value.length} 个商品吗？`, '批量通过审核', {
      type: 'warning'
    })
    const results = await Promise.allSettled(selectedIds.value.map((id) => adminApi.post(`/products/${id}/publish`)))
    const success = results.filter((r) => r.status === 'fulfilled').length
    const failed = results.length - success
    if (failed) {
      ElMessage.warning(`已通过 ${success} 个，失败 ${failed} 个`)
    } else {
      ElMessage.success(`已通过 ${success} 个`)
    }
    await load()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(error?.response?.data?.detail || '操作失败')
  }
}

const batchUnpublish = async () => {
  if (!selectedRows.value.length) return
  try {
    const { value } = await ElMessageBox.prompt('请输入下架原因（将展示给卖家）', '批量下架', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '例如：信息不实 / 重复发布 / 违规内容'
    })
    const reason = (value || '').trim()
    const results = await Promise.allSettled(selectedIds.value.map((id) => adminApi.post(`/products/${id}/unpublish`, { reason })))
    const success = results.filter((r) => r.status === 'fulfilled').length
    const failed = results.length - success
    if (failed) {
      ElMessage.warning(`已下架 ${success} 个，失败 ${failed} 个`)
    } else {
      ElMessage.success(`已下架 ${success} 个`)
    }
    await load()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(error?.response?.data?.detail || '操作失败')
  }
}

const batchDelete = async () => {
  if (!selectedRows.value.length) return
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 个商品吗？删除后不可恢复。`, '批量删除', {
      type: 'warning'
    })
    const results = await Promise.allSettled(selectedIds.value.map((id) => adminApi.delete(`/products/${id}`)))
    const success = results.filter((r) => r.status === 'fulfilled').length
    const failed = results.length - success
    if (failed) {
      ElMessage.warning(`已删除 ${success} 个，失败 ${failed} 个`)
    } else {
      ElMessage.success(`已删除 ${success} 个`)
    }
    await load()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(error?.response?.data?.detail || '删除失败')
  }
}

const remove = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除商品 "${row.title}" 吗？`, '提示', {
      type: 'warning'
    })
    await adminApi.delete(`/products/${row.id}`)
    ElMessage.success('删除成功')
    await load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.images-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  width: 100%;
}

.product-image-thumb {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #eee;
}

@media (max-width: 720px) {
  .images-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>

