<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">前端用户管理</h2>
    </div>

    <div style="display: flex; gap: 8px; margin-bottom: 16px">
      <el-input
        v-model="search"
        placeholder="搜索用户名或邮箱"
        style="width: 300px"
        clearable
        @keyup.enter="load"
      />
      <el-button type="primary" @click="load">查询</el-button>
    </div>

    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="email" label="邮箱" width="200" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '活跃' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_staff" label="管理员" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_staff ? 'warning' : 'info'">{{ row.is_staff ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="date_joined" label="注册时间" width="180" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button v-if="hasPerm('user:delete')" size="small" type="danger" @click="remove(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" title="编辑用户" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" disabled />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="活跃" inactive-text="禁用" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="form.is_staff" active-text="是" inactive-text="否" />
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
const saving = ref(false)
const currentId = ref(null)

const form = reactive({
  username: '',
  email: '',
  is_active: true,
  is_staff: false
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
    const res = await adminApi.get('/frontend-users', { params })
    items.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const handlePageChange = () => {
  load()
}

const edit = (row) => {
  currentId.value = row.id
  dialogVisible.value = true
  Object.assign(form, {
    username: row.username,
    email: row.email,
    is_active: row.is_active,
    is_staff: row.is_staff
  })
}

const save = async () => {
  if (!currentId.value) return
  saving.value = true
  try {
    await adminApi.put(`/frontend-users/${currentId.value}`, form)
    ElMessage.success('更新成功')
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

const remove = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除用户 "${row.username}" 吗？`, '提示', {
      type: 'warning'
    })
    await adminApi.delete(`/frontend-users/${row.id}`)
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









