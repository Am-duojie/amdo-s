<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">审核队列</h2>
    </div>
    
    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="队列ID" width="100" />
      <el-table-column prop="type" label="类型" width="120" />
      <el-table-column prop="rules_hit" label="命中规则" />
      <el-table-column label="操作" width="240">
        <template #default="{row}">
          <el-button v-if="hasPerm('audit:write')" size="small" type="success" @click="decision(row,'approve')">通过</el-button>
          <el-button v-if="hasPerm('audit:write')" size="small" type="danger" @click="decision(row,'reject')">驳回</el-button>
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
const decision = async (row, action) => {
  try {
    await adminApi.post(`/audit/queue/${row.id}/decision`, { action })
    ElMessage.success('已处理')
    load()
  } catch (error) {
    ElMessage.error('处理失败')
  }
}

const load = async () => {
  try {
    const res = await adminApi.get('/audit/queue', {
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
