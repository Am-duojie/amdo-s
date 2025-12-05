<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">审计日志</h2>
    </div>
    
    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="actor" label="操作者" width="140" />
      <el-table-column prop="target_type" label="对象类型" width="160" />
      <el-table-column prop="target_id" label="对象ID" width="100" />
      <el-table-column prop="action" label="动作" width="120" />
      <el-table-column prop="created_at" label="时间" width="200" />
      <el-table-column label="详情">
        <template #default="{row}">
          <pre style="white-space:pre-wrap">{{ JSON.stringify(row.snapshot_json, null, 2) }}</pre>
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
const items = ref([])
const pagination = ref({ current: 1, pageSize: 10, total: 0 })
const load = async () => {
  try {
    const res = await adminApi.get('/audit/logs', {
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
