<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">分类管理</h2>
      <el-button v-if="hasPerm('category:write')" type="primary" @click="openCreate">新增分类</el-button>
    </div>

    <div style="display: flex; gap: 8px; margin-bottom: 16px">
      <el-input
        v-model="search"
        placeholder="搜索分类名称"
        style="width: 300px"
        clearable
        @keyup.enter="load"
      />
      <el-button type="primary" @click="load">查询</el-button>
    </div>

    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="分类名称" />
      <el-table-column prop="type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag>{{ row.type || 'digital' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-space wrap>
            <el-button size="small" @click="edit(row)">编辑</el-button>
            <el-button v-if="hasPerm('category:delete')" size="small" type="danger" @click="remove(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '新增分类'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="分类名称" required>
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="数码" value="digital" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入分类描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
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
const pagination = ref({ current: 1, pageSize: 10, total: 0 })
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const currentId = ref(null)

const form = reactive({
  name: '',
  type: 'digital',
  description: ''
})

const load = async () => {
  try {
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize
    }
    if (search.value) {
      params.search = search.value
    }
    const res = await adminApi.get('/categories', { params })
    items.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const handlePageChange = () => {
  load()
}

const openCreate = () => {
  isEdit.value = false
  currentId.value = null
  dialogVisible.value = true
  Object.assign(form, {
    name: '',
    type: 'digital',
    description: ''
  })
}

const edit = (row) => {
  isEdit.value = true
  currentId.value = row.id
  dialogVisible.value = true
  Object.assign(form, {
    name: row.name,
    type: row.type || 'digital',
    description: row.description || ''
  })
}

const save = async () => {
  if (!form.name) {
    ElMessage.warning('请输入分类名称')
    return
  }
  saving.value = true
  try {
    if (isEdit.value && currentId.value) {
      await adminApi.put(`/categories/${currentId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await adminApi.post('/categories', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    saving.value = false
  }
}

const remove = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除分类 "${row.name}" 吗？`, '提示', {
      type: 'warning'
    })
    await adminApi.delete(`/categories/${row.id}`)
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













