<template>
  <div class="admin-login">
    <div class="card">
      <div class="title">登录管理后台</div>
      <el-form :model="form" @submit.prevent="onSubmit">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="onSubmit">登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminAuthStore } from '@/stores/adminAuth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const admin = useAdminAuthStore()
const form = reactive({ username: '', password: '' })
const loading = ref(false)

const onSubmit = async () => {
  loading.value = true
  const ok = await admin.login(form.username, form.password)
  loading.value = false
  if (ok) {
    ElMessage.success('登录成功')
    router.replace('/admin/dashboard')
  } else {
    ElMessage.error('登录失败')
  }
}
</script>

<style scoped>
.admin-login { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f6f7f9; }
.card { width: 360px; background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }
.title { font-weight: 700; font-size: 18px; margin-bottom: 12px; }
</style>
