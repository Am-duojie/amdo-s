<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">质检单管理</h2>
    </div>
    
    <el-table :data="items" style="width:100%">
      <el-table-column prop="id" label="编号" width="80" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="device" label="设备" />
      <el-table-column prop="appointment_at" label="预约时间" width="160" />
      <el-table-column label="操作" width="160">
        <template #default="{row}">
          <el-button size="small" @click="open(row)">详情</el-button>
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
import { useRouter } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
const items = ref([])
const pagination = ref({ current: 1, pageSize: 10, total: 0 })
const router = useRouter()
const open = (row) => { router.push(`/admin/inspection-orders/${row.id}`) }
const load = async () => {
  try {
    const res = await adminApi.get('/inspection-orders', {
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
onMounted(load)
</script>
