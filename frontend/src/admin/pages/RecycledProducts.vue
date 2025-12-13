<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">回收商品管理</h2>
    </div>
    
    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="condition" label="成色" width="120" />
      <el-table-column prop="price" label="价格" width="120" />
      <el-table-column label="操作" width="220">
        <template #default="{row}">
          <el-space wrap>
            <el-button v-if="hasPerm('recycled:write')" size="small" @click="publish(row)">发布官方验</el-button>
            <el-button v-if="hasPerm('recycled:write')" size="small" type="warning" @click="toggleStock(row)">上下架</el-button>
          </el-space>
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
const publish = async (row) => {
  try {
    await adminApi.post(`/recycled-products/${row.id}/publish`)
    ElMessage.success('已发布')
    load()
  } catch (error) {
    ElMessage.error('发布失败')
  }
}

const toggleStock = async (row) => {
  try {
    await adminApi.put(`/recycled-products/${row.id}/stock`, { toggle: row.status !== 'active' })
    ElMessage.success('已更新')
    load()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const load = async () => {
  try {
    const res = await adminApi.get('/recycled-products', {
      params: {
        page: pagination.value.current,
        page_size: pagination.value.pageSize
      }
    })
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
