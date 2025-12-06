<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">商品管理</h2>
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
        <el-option label="活跃" value="active" />
        <el-option label="已下架" value="removed" />
        <el-option label="已售出" value="sold" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
    </div>

    <el-table :data="items" style="width: 100%">
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
      <el-table-column prop="shop" label="店铺" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="320" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button v-if="hasPerm('product:write')" size="small" type="primary" @click="doAction(row, 'publish')">发布</el-button>
          <el-button v-if="hasPerm('product:write')" size="small" @click="doAction(row, 'unpublish')">下架</el-button>
          <el-button v-if="hasPerm('product:write')" size="small" type="success" @click="doAction(row, 'mark-sold')">标记已售</el-button>
          <el-button v-if="hasPerm('product:delete')" size="small" type="danger" @click="remove(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" title="编辑商品" width="700px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="原价">
          <el-input-number v-model="form.original_price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="成色">
          <el-input v-model="form.condition" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="活跃" value="active" />
            <el-option label="已下架" value="removed" />
            <el-option label="已售出" value="sold" />
          </el-select>
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="form.location" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" />
        </el-form-item>
        <el-form-item label="微信">
          <el-input v-model="form.contact_wechat" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
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

const form = reactive({
  title: '',
  description: '',
  price: 0,
  original_price: 0,
  condition: '',
  status: 'active',
  location: '',
  contact_phone: '',
  contact_wechat: ''
})

const getStatusType = (status) => {
  const map = {
    active: 'success',
    removed: 'info',
    sold: 'warning'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    active: '活跃',
    removed: '已下架',
    sold: '已售出'
  }
  return map[status] || status
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
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const handlePageChange = () => {
  load()
}

const edit = async (row) => {
  currentId.value = row.id
  dialogVisible.value = true
  // 加载商品详情
  try {
    // 由于后端没有提供详情接口，这里先使用列表中的数据
    Object.assign(form, {
      title: row.title || '',
      description: '',
      price: row.price || 0,
      original_price: 0,
      condition: '',
      status: row.status || 'active',
      location: '',
      contact_phone: '',
      contact_wechat: ''
    })
  } catch (error) {
    ElMessage.error('加载商品详情失败')
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

const doAction = async (row, action) => {
  try {
    await adminApi.post(`/products/${row.id}/${action}`)
    ElMessage.success('操作成功')
    await load()
  } catch (error) {
    ElMessage.error('操作失败')
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



