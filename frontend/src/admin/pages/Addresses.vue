<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">地址管理</h2>
    </div>

    <div style="display: flex; gap: 8px; margin-bottom: 16px">
      <el-input
        v-model="search"
        placeholder="搜索姓名、电话或地址"
        style="width: 300px"
        clearable
        @keyup.enter="load"
      />
      <el-button type="primary" @click="load">查询</el-button>
    </div>

    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user" label="用户" width="120" />
      <el-table-column prop="name" label="收货人" width="120" />
      <el-table-column prop="phone" label="电话" width="140" />
      <el-table-column prop="address" label="地址" min-width="300" />
      <el-table-column prop="is_default" label="默认地址" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_default ? 'success' : 'info'">{{ row.is_default ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button v-if="hasPerm('address:delete')" size="small" type="danger" @click="remove(row)">删除</el-button>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminAuthStore } from '@/stores/adminAuth'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)

const items = ref([])
const search = ref('')
const pagination = ref({ current: 1, pageSize: 10, total: 0 })

const load = async () => {
  try {
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize
    }
    if (search.value) {
      params.search = search.value
    }
    const res = await adminApi.get('/addresses', { params })
    items.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const handlePageChange = () => {
  load()
}

const remove = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除地址 "${row.name} - ${row.address}" 吗？`, '提示', {
      type: 'warning'
    })
    await adminApi.delete(`/addresses/${row.id}`)
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


