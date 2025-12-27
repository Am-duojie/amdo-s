
<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">{{ labels.title }}</h2>
    </div>

    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" :label="labels.roleName" />
      <el-table-column prop="description" :label="labels.description" />
      <el-table-column :label="labels.permissions" min-width="400">
        <template #default="{ row }">
          <el-tag v-for="p in (row.permissions || [])" :key="p" class="mr4" type="info" size="small">{{ formatPermission(p) }}</el-tag>
          <span v-if="!row.permissions || row.permissions.length === 0" style="color: #999">{{ labels.noPermissions }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="labels.actions" width="160" fixed="right">
        <template #default="{ row }">
          <el-space wrap>
            <el-button size="small" @click="editRole(row)">{{ labels.edit }}</el-button>
            <el-button size="small" type="danger" @click="removeRole(row)">{{ labels.delete }}</el-button>
          </el-space>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" :title="labels.editRole" width="820px">
      <el-form :model="form" label-width="100px">
        <el-form-item :label="labels.roleName" required>
          <el-input v-model="form.name" disabled />
        </el-form-item>
        <el-form-item :label="labels.description">
          <el-input v-model="form.description" :placeholder="labels.descriptionPlaceholder" />
        </el-form-item>
        <el-form-item :label="labels.permissions" required>
          <el-transfer
            v-model="form.permissions"
            filterable
            :filter-method="filterMethod"
            :filter-placeholder="labels.permissionsFilterPlaceholder"
            :titles="[labels.permissionsAll, labels.permissionsSelected]"
            :data="transferData"
          />
          <div style="font-size: 12px; color: #666; margin-top: 4px">
            {{ labels.permissionsTip }}
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">{{ labels.cancel }}</el-button>
        <el-button type="primary" :loading="saving" @click="saveRole">{{ labels.save }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatPermission } from '@/admin/utils/permissionLabels'

const labels = {
  title: '\u89d2\u8272\u7ba1\u7406',
  roleName: '\u89d2\u8272\u540d\u79f0',
  roleNamePlaceholder: '\u5982\uff1aauditor \u6216 superadmin',
  description: '\u63cf\u8ff0',
  descriptionPlaceholder: '\u89d2\u8272\u8bf4\u660e',
  permissions: '\u6743\u9650',
  permissionsFilterPlaceholder: '\u641c\u7d22\u6743\u9650',
  permissionsTip: '\u63d0\u793a\uff1a\u53ef\u4ee5\u901a\u8fc7 /admin-api/permissions \u63a5\u53e3\u67e5\u770b\u6240\u6709\u53ef\u7528\u7684\u6743\u9650\u4ee3\u7801',
  permissionsAll: '\u53ef\u9009\u6743\u9650',
  permissionsSelected: '\u5df2\u9009\u6743\u9650',
  saveUpdate: '\u4fdd\u5b58/\u66f4\u65b0',
  reset: '\u91cd\u7f6e',
  actions: '\u64cd\u4f5c',
  edit: '\u7f16\u8f91',
  delete: '\u5220\u9664',
  editRole: '\u7f16\u8f91\u89d2\u8272',
  cancel: '\u53d6\u6d88',
  save: '\u4fdd\u5b58',
  noPermissions: '\u65e0\u6743\u9650',
  loadFailed: '\u52a0\u8f7d\u5931\u8d25',
  saveSuccess: '\u4fdd\u5b58\u6210\u529f',
  saveFailed: '\u4fdd\u5b58\u5931\u8d25',
  roleNameRequired: '\u8bf7\u8f93\u5165\u89d2\u8272\u540d',
  deleteConfirm: '\u786e\u8ba4\u5220\u9664\u8be5\u89d2\u8272\u5417\uff1f',
  deleteSuccess: '\u5220\u9664\u6210\u529f',
  deleteFailed: '\u5220\u9664\u5931\u8d25',
  deleteInUse: '\u8be5\u89d2\u8272\u5df2\u88ab\u4f7f\u7528\uff0c\u65e0\u6cd5\u5220\u9664'
}

const items = ref([])
const allPermissions = ref([])
const transferData = ref([])
const form = reactive({ name: '', description: '', permissions: [] })
const saving = ref(false)
const isEdit = ref(false)
const editVisible = ref(false)

const fetchRoles = async () => {
  try {
    const res = await adminApi.get('/roles')
    items.value = res.data?.results || res.data || []
    allPermissions.value = res.data?.all_permissions || []
    transferData.value = allPermissions.value.map((code) => ({
      key: code,
      label: formatPermission(code),
      initial: `${code} ${formatPermission(code)}`.toLowerCase(),
    }))
  } catch (error) {
    ElMessage.error(labels.loadFailed)
  }
}

const resetForm = () => {
  isEdit.value = false
  form.name = ''
  form.description = ''
  form.permissions = []
}

const editRole = (row) => {
  isEdit.value = true
  editVisible.value = true
  form.name = row.name
  form.description = row.description || ''
  form.permissions = row.permissions || []
}

const saveRole = async () => {
  if (!form.name) {
    ElMessage.warning(labels.roleNameRequired)
    return
  }

  saving.value = true
  try {
    await adminApi.post('/roles', {
      name: form.name,
      description: form.description,
      permissions: form.permissions
    })
    ElMessage.success(labels.saveSuccess)
    editVisible.value = false
    await fetchRoles()
  } catch (error) {
    ElMessage.error(labels.saveFailed)
  } finally {
    saving.value = false
  }
}

const filterMethod = (query, item) => {
  return item.initial.includes(query.toLowerCase())
}

const removeRole = async (row) => {
  try {
    await ElMessageBox.confirm(labels.deleteConfirm, labels.actions, { type: 'warning' })
    await adminApi.delete(`/roles/${row.id}`)
    ElMessage.success(labels.deleteSuccess)
    await fetchRoles()
  } catch (error) {
    if (error === 'cancel') return
    const detail = error?.response?.data?.detail
    if (detail === 'role in use') {
      ElMessage.error(labels.deleteInUse)
    } else {
      ElMessage.error(labels.deleteFailed)
    }
  }
}

onMounted(fetchRoles)
</script>

<style scoped>
.mr4 {
  margin-right: 4px;
  margin-bottom: 4px;
}

.el-transfer {
  width: 100%;
}

.el-transfer-panel {
  width: 320px;
  height: 360px;
}

.el-transfer-panel__body {
  height: 300px;
}
</style>
