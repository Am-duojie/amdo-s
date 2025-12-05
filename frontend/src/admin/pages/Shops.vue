<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">店铺管理</h2>
      <el-button v-if="hasPerm('shop:write')" type="primary" @click="openCreate">新增店铺</el-button>
    </div>
    
    <div style="display: flex; gap: 8px; margin-bottom: 16px">
      <el-input
        v-model="search"
        placeholder="搜索店铺名称或店主"
        style="width: 300px"
        clearable
        @keyup.enter="load"
      />
      <el-button type="primary" @click="load">查询</el-button>
    </div>

    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="店铺名称" />
      <el-table-column prop="owner" label="店主" width="140" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_verified" label="已认证" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_verified ? 'success' : 'info'">{{ row.is_verified ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="rating" label="评分" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button v-if="hasPerm('shop:delete')" size="small" type="danger" @click="remove(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑店铺' : '新增店铺'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="店铺名称" required>
          <el-input v-model="form.name" placeholder="请输入店铺名称" />
        </el-form-item>
        <el-form-item label="店主" required>
          <el-select
            v-model="form.owner_id"
            filterable
            remote
            :remote-method="searchUsers"
            placeholder="请输入用户名搜索"
            style="width: 100%"
          >
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="活跃" value="active" />
            <el-option label="暂停" value="paused" />
            <el-option label="关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="已认证">
          <el-switch v-model="form.is_verified" />
        </el-form-item>
        <el-form-item label="评分">
          <el-input-number v-model="form.rating" :min="0" :max="5" :step="0.1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入店铺描述" />
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
const userOptions = ref([])

const form = reactive({
  name: '',
  owner_id: null,
  status: 'active',
  is_verified: false,
  rating: 0,
  contact_phone: '',
  address: '',
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
    const res = await adminApi.get('/shops', { params })
    items.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const searchUsers = async (query) => {
  if (!query) return
  try {
    const res = await adminApi.get('/frontend-users', { params: { search: query, page_size: 10 } })
    userOptions.value = res.data?.results || []
  } catch {}
}

const handlePageChange = () => {
  load()
}

const openCreate = () => {
  isEdit.value = false
  dialogVisible.value = true
  Object.assign(form, {
    name: '',
    owner_id: null,
    status: 'active',
    is_verified: false,
    rating: 0,
    contact_phone: '',
    address: '',
    description: ''
  })
  userOptions.value = []
}

const edit = (row) => {
  isEdit.value = true
  dialogVisible.value = true
  // 需要先获取完整的店铺信息
  Object.assign(form, {
    name: row.name,
    owner_id: null, // 需要获取owner_id
    status: row.status || 'active',
    is_verified: row.is_verified || false,
    rating: row.rating || 0,
    contact_phone: '',
    address: '',
    description: ''
  })
  // 加载完整信息
  loadShopDetail(row.id)
}

const loadShopDetail = async (id) => {
  try {
    // 由于后端没有提供详情接口，这里先使用列表中的数据
    // 如果需要编辑，可能需要后端提供详情接口
    ElMessage.warning('编辑功能需要后端提供详情接口')
  } catch {}
}

const save = async () => {
  if (!form.name) {
    ElMessage.warning('请输入店铺名称')
    return
  }
  if (!form.owner_id) {
    ElMessage.warning('请选择店主')
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      // 找到当前编辑的店铺ID
      const shopId = items.value.find(s => s.name === form.name)?.id
      if (shopId) {
        await adminApi.put(`/shops/${shopId}`, form)
        ElMessage.success('更新成功')
      } else {
        ElMessage.error('未找到店铺')
      }
    } else {
      await adminApi.post('/shops', form)
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
    await ElMessageBox.confirm(`确认删除店铺 "${row.name}" 吗？`, '提示', {
      type: 'warning'
    })
    await adminApi.delete(`/shops/${row.id}`)
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
.mr4 {
  margin-right: 4px;
}
</style>

