<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">官方验货商品管理</h2>
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
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
    </div>
    
    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status === 'active' ? '活跃' : '已下架' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="320" fixed="right">
        <template #default="{row}">
          <el-button v-if="hasPerm('verified:write')" size="small" type="primary" @click="update(row, 'publish')">发布</el-button>
          <el-button v-if="hasPerm('verified:write')" size="small" @click="update(row, 'unpublish')">下架</el-button>
          <el-button v-if="hasPerm('verified:write')" size="small" type="success" @click="update(row, 'audit-approve')">审核通过</el-button>
          <el-button v-if="hasPerm('verified:write')" size="small" type="danger" @click="update(row, 'audit-reject')">审核驳回</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
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
import { ElMessage } from 'element-plus'
import { useAdminAuthStore } from '@/stores/adminAuth'
const admin = useAdminAuthStore()
const items = ref([])
const pagination = ref({ current: 1, pageSize: 10, total: 0 })
const search = ref('')
const statusFilter = ref('')

const update = async (row, action) => {
  try {
    await adminApi.post(`/verified-listings/${row.id}/${action}`)
    ElMessage.success('操作成功')
    load()
  } catch (error) {
    ElMessage.error('操作失败')
  }
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
    const res = await adminApi.get('/verified-listings', { params })
    items.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const handlePageChange = () => load()
const hasPerm = (p) => admin.hasPerm(p)

onMounted(load)
</script>
