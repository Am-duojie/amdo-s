<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">角色管理</h2>
    </div>
    
    <el-card style="margin-bottom: 16px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="角色名" required>
          <el-input v-model="form.name" placeholder="如：auditor 或 superadmin" style="width: 400px" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" placeholder="角色说明" style="width: 400px" />
        </el-form-item>
        <el-form-item label="权限" required>
          <el-input 
            v-model="form.permsText" 
            type="textarea" 
            :rows="3"
            placeholder="权限代码，用逗号分隔，如：dashboard:view,verified:view,verified:write" 
            style="width: 500px"
          />
          <div style="font-size: 12px; color: #666; margin-top: 4px">
            提示：可以通过 /admin-api/permissions 接口查看所有可用的权限代码
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="saveRole">保存/更新</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="角色名" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="权限" min-width="400">
        <template #default="{ row }">
          <el-tag v-for="p in (row.permissions||[])" :key="p" class="mr4" type="info" size="small">{{ p }}</el-tag>
          <span v-if="!row.permissions || row.permissions.length === 0" style="color: #999">无权限</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editRole(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'

const items = ref([])
const form = reactive({ name: '', description: '', permsText: '' })
const saving = ref(false)
const isEdit = ref(false)

const fetchRoles = async () => {
  try {
    const res = await adminApi.get('/roles')
    items.value = res.data?.results || res.data || []
  } catch (error) {
    ElMessage.error('加载失败')
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
    ElMessage.warning('请输入角色名')
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
    ElMessage.success('保存成功')
    resetForm()
    await fetchRoles()
  } catch (error) {
    ElMessage.error('保存失败')
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
