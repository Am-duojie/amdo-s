<template>
  <div>
    <el-button type="primary" @click="openCreate">新增用户</el-button>
    <el-table :data="items" style="margin-top:8px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="role" label="角色" width="140" />
      <el-table-column label="权限">
        <template #default="{ row }">
          <el-tag v-for="p in (row.permissions||[])" :key="p" class="mr4" type="info">{{ p }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{row}">
          <el-space wrap>
            <el-button size="small" @click="edit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </el-space>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:8px">
      <el-pagination
        v-model:current-page="pagination.current"
        :total="pagination.total"
        :page-size="pagination.pageSize"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>

    <el-dialog v-model="createVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="420px">
      <el-form :model="form">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="角色"><el-select v-model="form.role"><el-option label="super" value="super" /><el-option label="auditor" value="auditor" /></el-select></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible=false">取消</el-button>
        <el-button v-if="!isEdit" type="primary" :loading="creating" @click="create">确定</el-button>
        <el-button v-else type="primary" :loading="creating" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
const items = ref([])
const pagination = ref({ current: 1, pageSize: 10, total: 0 })
const createVisible = ref(false)
const isEdit = ref(false)
const creating = ref(false)
const form = reactive({ username: '', role: 'auditor', email: '', password: '' })
const currentEditId = ref(null)

const openCreate = () => {
  isEdit.value = false
  currentEditId.value = null
  createVisible.value = true
  form.username = ''
  form.role = 'auditor'
  form.email = ''
  form.password = ''
}

const create = async () => {
  creating.value = true
  try {
    await adminApi.post('/users', form)
    ElMessage.success('已创建')
    createVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const edit = (row) => {
  isEdit.value = true
  currentEditId.value = row.id
  createVisible.value = true
  form.username = row.username
  form.email = row.email || ''
  form.role = row.role || 'auditor'
  form.password = ''
}
const remove = async (row) => { try { await adminApi.delete(`/users/${row.id}`) ; ElMessage.success('已删除'); load() } catch { ElMessage.error('删除失败') } }
const saveEdit = async () => {
  if (!currentEditId.value) {
    ElMessage.error('未找到用户ID')
    return
  }
  creating.value = true
  try {
    const updateData = { role: form.role, email: form.email }
    if (form.password) {
      updateData.password = form.password
    }
    await adminApi.put(`/users/${currentEditId.value}`, updateData)
    ElMessage.success('已保存')
    createVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    creating.value = false
  }
}
const load = async () => { try { const res = await adminApi.get('/users', { params: { page: pagination.value.current, page_size: pagination.value.pageSize } }); items.value = res.data?.results || [] ; pagination.value.total = res.data?.count || items.value.length } catch {} }
const handlePageChange = () => load()
onMounted(load)
</script>
