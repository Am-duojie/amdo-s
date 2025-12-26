<template>
  <div class="platform-settings admin-page">
    <div class="page-header">
      <div>
        <div class="page-title">平台设置</div>
        <div class="page-desc">管理回收订单的平台收件信息</div>
      </div>
      <el-space>
        <el-button :loading="loading" text :icon="Refresh" @click="loadSettings">刷新</el-button>
      </el-space>
    </div>

    <el-card shadow="hover" class="form-card">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="收件人" prop="name">
          <el-input v-model="form.name" placeholder="填写收件人姓名" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="填写联系电话" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" type="textarea" :rows="3" placeholder="填写收件地址" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import adminApi from '@/utils/adminApi'

const loading = ref(false)
const saving = ref(false)
const formRef = ref(null)
const form = ref({
  name: '',
  phone: '',
  address: ''
})

const rules = {
  name: [{ required: true, message: '请填写收件人', trigger: 'blur' }],
  phone: [{ required: true, message: '请填写电话', trigger: 'blur' }],
  address: [{ required: true, message: '请填写地址', trigger: 'blur' }]
}

const loadSettings = async () => {
  loading.value = true
  try {
    const res = await adminApi.get('/settings/recipient')
    const data = res.data || {}
    form.value = {
      name: data.name || '',
      phone: data.phone || '',
      address: data.address || ''
    }
  } catch (error) {
    ElMessage.error('加载平台收件信息失败')
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    await adminApi.put('/settings/recipient', { ...form.value })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  if (!formRef.value) return
  formRef.value.resetFields()
}

onMounted(loadSettings)
</script>

<style scoped>
.platform-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
}

.page-desc {
  color: #6b7280;
  font-size: 13px;
}

.form-card {
  border-radius: 12px;
}
</style>
