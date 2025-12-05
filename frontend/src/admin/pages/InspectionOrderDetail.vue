<template>
  <div>
    <div style="margin-bottom: 16px">
      <el-button size="small" @click="router.back()">返回列表</el-button>
    </div>
    
    <el-card>
      <div style="display:flex;gap:24px">
        <div style="flex:1">
          <div>编号：{{ detail.id }}</div>
          <div>设备：{{ detail.brand }} {{ detail.model }}</div>
          <div>成色：{{ detail.condition }}</div>
          <div>预约：{{ detail.appointment_at || '-' }}</div>
        </div>
        <div style="width:280px">
          <div style="margin-bottom: 8px; font-weight: 600">当前状态：{{ status }}</div>
          <el-select v-model="status" placeholder="选择新状态" style="width:100%">
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
          <el-button v-if="hasPerm('inspection:write')" type="primary" :loading="saving" style="margin-top:8px;width:100%" @click="updateStatus">更新状态</el-button>
        </div>
      </div>
    </el-card>
    <el-card style="margin-top:12px">
      <div style="font-weight:600;margin-bottom:8px">质检报告</div>
      <el-input v-model="reportRemarks" type="textarea" :rows="3" placeholder="质检备注" />
      <el-input v-model="reportJson" type="textarea" :rows="6" placeholder="检测项目JSON" style="margin-top:8px" />
      <el-button v-if="hasPerm('inspection:write')" type="primary" :loading="uploading" style="margin-top:8px" @click="uploadReport">上传报告</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import { useAdminAuthStore } from '@/stores/adminAuth'
const admin = useAdminAuthStore()

const route = useRoute()
const router = useRouter()
const detail = ref({})
const status = ref('created')
const statuses = ['created','scheduled','inspecting','inspected','pricing','seller_confirmed','paid','received','stocked','published']
const saving = ref(false)
const reportRemarks = ref('')
const reportJson = ref('')
const uploading = ref(false)

const load = async () => {
  try {
    const id = route.params.id
    const res = await adminApi.get(`/inspection-orders/${id}`)
    if (res.data?.success) {
      detail.value = res.data.item
      status.value = res.data.item.status || 'created'
      reportRemarks.value = res.data.item.report?.remarks || ''
      reportJson.value = JSON.stringify(res.data.item.report?.check_items || {}, null, 2)
    } else {
      ElMessage.error('未找到质检单')
      router.replace('/admin/inspection-orders')
    }
  } catch (error) {
    ElMessage.error('加载失败')
    router.replace('/admin/inspection-orders')
  }
}

const updateStatus = async () => {
  if (!detail.value.id) {
    ElMessage.error('质检单信息不完整')
    return
  }
  saving.value = true
  try {
    await adminApi.put(`/inspection-orders/${detail.value.id}/status`, null, { params: { status: status.value } })
    ElMessage.success('状态已更新')
    await load()
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

const uploadReport = async () => {
  if (!detail.value.id) {
    ElMessage.error('质检单信息不完整')
    return
  }
  uploading.value = true
  try {
    let items = {}
    try {
      items = JSON.parse(reportJson.value || '{}')
    } catch (e) {
      ElMessage.error('JSON格式错误，请检查检测项目JSON')
      return
    }
    await adminApi.post(`/inspection-orders/${detail.value.id}/report`, {
      check_items: items,
      remarks: reportRemarks.value
    })
    ElMessage.success('报告已上传')
    await load()
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

onMounted(load)
const hasPerm = (p) => admin.hasPerm(p)
</script>
