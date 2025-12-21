
<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">{{ labels.title }}</h2>
    </div>

    <el-card style="margin-bottom: 16px">
      <el-form :model="form" label-width="100px">
        <el-form-item :label="labels.roleName" required>
          <el-input v-model="form.name" :placeholder="labels.roleNamePlaceholder" style="width: 400px" />
        </el-form-item>
        <el-form-item :label="labels.description">
          <el-input v-model="form.description" :placeholder="labels.descriptionPlaceholder" style="width: 400px" />
        </el-form-item>
        <el-form-item :label="labels.permissions" required>
          <el-input
            v-model="form.permsText"
            type="textarea"
            :rows="3"
            :placeholder="labels.permissionsPlaceholder"
            style="width: 500px"
          />
          <div style="font-size: 12px; color: #666; margin-top: 4px">
            {{ labels.permissionsTip }}
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="saveRole">{{ labels.saveUpdate }}</el-button>
          <el-button @click="resetForm">{{ labels.reset }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>

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
      <el-table-column :label="labels.actions" width="120" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editRole(row)">{{ labels.edit }}</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import { formatPermission } from '@/admin/utils/permissionLabels'

const labels = {
  title: '\u89d2\u8272\u7ba1\u7406',
  roleName: '\u89d2\u8272\u540d\u79f0',
  roleNamePlaceholder: '\u5982\uff1aauditor \u6216 superadmin',
  description: '\u63cf\u8ff0',
  descriptionPlaceholder: '\u89d2\u8272\u8bf4\u660e',
  permissions: '\u6743\u9650',
  permissionsPlaceholder: '\u6743\u9650\u4ee3\u7801\uff0c\u7528\u9017\u53f7\u5206\u9694\uff0c\u5982\uff1adashboard:view,verified:view,verified:write',
  permissionsTip: '\u63d0\u793a\uff1a\u53ef\u4ee5\u901a\u8fc7 /admin-api/permissions \u63a5\u53e3\u67e5\u770b\u6240\u6709\u53ef\u7528\u7684\u6743\u9650\u4ee3\u7801',
  saveUpdate: '\u4fdd\u5b58/\u66f4\u65b0',
  reset: '\u91cd\u7f6e',
  actions: '\u64cd\u4f5c',
  edit: '\u7f16\u8f91',
  noPermissions: '\u65e0\u6743\u9650',
  loadFailed: '\u52a0\u8f7d\u5931\u8d25',
  saveSuccess: '\u4fdd\u5b58\u6210\u529f',
  saveFailed: '\u4fdd\u5b58\u5931\u8d25',
  roleNameRequired: '\u8bf7\u8f93\u5165\u89d2\u8272\u540d'
}

const items = ref([])
const form = reactive({ name: '', description: '', permsText: '' })
const saving = ref(false)
const isEdit = ref(false)

const fetchRoles = async () => {
  try {
    const res = await adminApi.get('/roles')
    items.value = res.data?.results || res.data || []
  } catch (error) {
    ElMessage.error(labels.loadFailed)
  }
}

const resetForm = () => {
  isEdit.value = false
  form.name = ''
  form.description = ''
  form.permsText = ''
}

const editRole = (row) => {
  isEdit.value = true
  form.name = row.name
  form.description = row.description || ''
  form.permsText = (row.permissions || []).join(', ')
}

const saveRole = async () => {
  if (!form.name) {
    ElMessage.warning(labels.roleNameRequired)
    return
  }

  saving.value = true
  try {
    const permissions = form.permsText.split(',').map(s => s.trim()).filter(Boolean)
    await adminApi.post('/roles', {
      name: form.name,
      description: form.description,
      permissions
    })
    ElMessage.success(labels.saveSuccess)
    resetForm()
    await fetchRoles()
  } catch (error) {
    ElMessage.error(labels.saveFailed)
  } finally {
    saving.value = false
  }
}

onMounted(fetchRoles)
</script>

<style scoped>
.mr4 {
  margin-right: 4px;
  margin-bottom: 4px;
}
</style>
