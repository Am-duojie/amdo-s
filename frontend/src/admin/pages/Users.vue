
<template>
  <div>
    <el-button type="primary" @click="openCreate">{{ labels.addUser }}</el-button>
    <el-table :data="items" style="margin-top:8px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" :label="labels.username" />
      <el-table-column prop="role" :label="labels.role" width="140" />
      <el-table-column :label="labels.permissions">
        <template #default="{ row }">
          <el-tag v-for="p in (row.permissions || [])" :key="p" class="mr4" type="info">{{ formatPermission(p) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="labels.actions" width="180">
        <template #default="{row}">
          <el-space wrap>
            <el-button size="small" @click="edit(row)">{{ labels.edit }}</el-button>
            <el-button size="small" type="danger" @click="remove(row)">{{ labels.delete }}</el-button>
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

    <el-dialog v-model="createVisible" :title="isEdit ? labels.editUser : labels.addUser" width="420px">
      <el-form :model="form">
        <el-form-item :label="labels.username"><el-input v-model="form.username" /></el-form-item>
        <el-form-item :label="labels.role">
          <el-select v-model="form.role">
            <el-option v-for="role in roles" :key="role.name" :label="role.name" :value="role.name" />
          </el-select>
        </el-form-item>
        <el-form-item :label="labels.email"><el-input v-model="form.email" /></el-form-item>
        <el-form-item :label="labels.password"><el-input v-model="form.password" type="password" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible=false">{{ labels.cancel }}</el-button>
        <el-button v-if="!isEdit" type="primary" :loading="creating" @click="create">{{ labels.confirm }}</el-button>
        <el-button v-else type="primary" :loading="creating" @click="saveEdit">{{ labels.save }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import { formatPermission } from '@/admin/utils/permissionLabels'

const labels = {
  addUser: '\u65b0\u589e\u7528\u6237',
  editUser: '\u7f16\u8f91\u7528\u6237',
  username: '\u7528\u6237\u540d',
  role: '\u89d2\u8272',
  roleSuper: '\u8d85\u7ea7\u7ba1\u7406\u5458',
  roleAuditor: '\u5ba1\u6838\u5458',
  permissions: '\u6743\u9650',
  actions: '\u64cd\u4f5c',
  edit: '\u7f16\u8f91',
  delete: '\u5220\u9664',
  email: '\u90ae\u7bb1',
  password: '\u5bc6\u7801',
  cancel: '\u53d6\u6d88',
  confirm: '\u786e\u5b9a',
  save: '\u4fdd\u5b58',
  created: '\u5df2\u521b\u5efa',
  createFailed: '\u521b\u5efa\u5931\u8d25',
  saved: '\u5df2\u4fdd\u5b58',
  saveFailed: '\u4fdd\u5b58\u5931\u8d25',
  deleted: '\u5df2\u5220\u9664',
  deleteFailed: '\u5220\u9664\u5931\u8d25',
  missingUserId: '\u672a\u627e\u5230\u7528\u6237ID'
}

const items = ref([])
const pagination = ref({ current: 1, pageSize: 10, total: 0 })
const roles = ref([])
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
  form.role = roles.value[0]?.name || 'auditor'
  form.email = ''
  form.password = ''
}

const create = async () => {
  creating.value = true
  try {
    await adminApi.post('/users', form)
    ElMessage.success(labels.created)
    createVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(labels.createFailed)
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
  form.role = row.role || roles.value[0]?.name || 'auditor'
  form.password = ''
}

const remove = async (row) => {
  try {
    await adminApi.delete(`/users/${row.id}`)
    ElMessage.success(labels.deleted)
    load()
  } catch {
    ElMessage.error(labels.deleteFailed)
  }
}

const saveEdit = async () => {
  if (!currentEditId.value) {
    ElMessage.error(labels.missingUserId)
    return
  }
  creating.value = true
  try {
    const updateData = { role: form.role, email: form.email }
    if (form.password) {
      updateData.password = form.password
    }
    await adminApi.put(`/users/${currentEditId.value}`, updateData)
    ElMessage.success(labels.saved)
    createVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(labels.saveFailed)
  } finally {
    creating.value = false
  }
}

const load = async () => {
  try {
    if (!roles.value.length) {
      await loadRoles()
    }
    const res = await adminApi.get('/users', {
      params: { page: pagination.value.current, page_size: pagination.value.pageSize }
    })
    items.value = res.data?.results || []
    pagination.value.total = res.data?.count || items.value.length
  } catch {
  }
}

const handlePageChange = () => load()

const loadRoles = async () => {
  try {
    const res = await adminApi.get('/roles')
    roles.value = res.data?.results || []
    if (!roles.value.length) {
      roles.value = [{ name: 'super' }, { name: 'auditor' }]
    }
  } catch {
    roles.value = [{ name: 'super' }, { name: 'auditor' }]
  }
}

onMounted(async () => {
  await loadRoles()
  await load()
})
</script>

<style scoped>
.mr4 {
  margin-right: 4px;
  margin-bottom: 4px;
}
</style>
