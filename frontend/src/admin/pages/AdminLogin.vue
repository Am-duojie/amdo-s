<template>
  <div class="admin-login-page">
    <div class="admin-topbar">
      <div class="brand">易淘·管理后台</div>
    </div>
    
    <div class="login-container">
      <div class="login-card">
        <div class="logo-section">
          <div class="logo">🔐</div>
          <h1 class="title">管理后台登录</h1>
        </div>
        
        <!-- 错误提示 -->
        <transition name="fade">
          <div v-if="errorMessage" class="error-alert">
            <el-icon class="error-icon"><CircleClose /></el-icon>
            <span>{{ errorMessage }}</span>
            <el-icon class="close-icon" @click="errorMessage = ''"><Close /></el-icon>
          </div>
        </transition>
        
        <!-- 登录表单 -->
        <el-form 
          ref="formRef"
          :model="form" 
          :rules="rules"
          class="login-form"
          @submit.prevent="handleSubmit"
        >
          <el-form-item prop="username">
            <el-input 
              v-model="form.username" 
              placeholder="请输入用户名"
              prefix-icon="User"
              clearable
              size="large"
              @keyup.enter="handleSubmit"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              v-model="form.password" 
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              prefix-icon="Lock"
              clearable
              size="large"
              @keyup.enter="handleSubmit"
            >
              <template #suffix>
                <span @click="showPassword = !showPassword" class="password-toggle">
                  <el-icon v-if="showPassword"><View /></el-icon>
                  <el-icon v-else><Hide /></el-icon>
                </span>
              </template>
            </el-input>
          </el-form-item>
          
          <!-- 登录按钮 -->
          <el-form-item>
            <el-button 
              type="primary"
              native-type="submit"
              class="submit-btn" 
              :loading="loading"
              :disabled="loading"
              size="large"
              block
              @click="handleSubmit"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  User, Lock, View, Hide, CircleClose, Close
} from '@element-plus/icons-vue'
import { useAdminAuthStore } from '@/stores/adminAuth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const adminAuthStore = useAdminAuthStore()
const formRef = ref(null)

const form = ref({
  username: '',
  password: ''
})

const loading = ref(false)
const errorMessage = ref('')
const showPassword = ref(false)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 3, message: '密码至少3位', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  // 验证表单
  try {
    await formRef.value.validate()
  } catch (error) {
    // 验证失败，显示错误提示
    console.log('表单验证失败:', error)
    return
  }

  // 如果密码为空或太短，直接返回
  if (!form.value.password || form.value.password.length < 3) {
    ElMessage.warning('请输入有效的密码')
    return
  }

  loading.value = true
  errorMessage.value = ''
  
  try {
    const result = await adminAuthStore.login(form.value.username, form.value.password)

    if (result.success) {
      ElMessage.success({
        message: '登录成功',
        type: 'success',
        duration: 2000
      })
      
      // 确保状态已更新后再跳转
      // 等待一个 tick，确保 Vue 响应式系统已更新
      await new Promise(resolve => {
        setTimeout(() => {
          // 再次确认登录状态
          if (adminAuthStore.isAuthed) {
            resolve()
          } else {
            // 如果状态还没更新，再等一会儿
            setTimeout(resolve, 200)
          }
        }, 100)
      })
      
      // 使用 push 跳转
      try {
        await router.push('/admin/dashboard')
      } catch (err) {
        console.warn('路由跳转失败，使用 location.href:', err)
        // 如果路由跳转失败，使用 location.href 强制跳转
        window.location.href = '/admin/dashboard'
      }
    } else {
      errorMessage.value = result.error || '登录失败，请检查用户名和密码'
      // 自动清除错误消息
      setTimeout(() => {
        errorMessage.value = ''
      }, 5000)
    }
  } catch (error) {
    console.error('登录错误:', error)
    errorMessage.value = '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 如果已经登录，直接跳转
  if (adminAuthStore.isAuthed) {
    router.replace('/admin/dashboard')
  }
})
</script>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  background: #f6f7f9;
  display: flex;
  flex-direction: column;
}

.admin-topbar {
  height: 56px;
  background: #101820;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 16px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.admin-topbar .brand {
  font-weight: 700;
  font-size: 18px;
}

.login-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 12px;
  padding: 40px 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.logo-section {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin: 0 auto 16px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 0;
}

/* 错误提示 */
.error-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff1f0;
  border: 1px solid #ffccc7;
  color: #f5222d;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 13px;
}

.error-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.close-icon {
  margin-left: auto;
  cursor: pointer;
  font-size: 14px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.close-icon:hover {
  opacity: 1;
}

/* 表单样式 */
.login-form {
  width: 100%;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__error) {
  font-size: 12px;
  padding-top: 4px;
  color: #f56c6c;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: none;
  transition: all 0.3s ease;
  border-color: #dcdfe6;
}

:deep(.el-input__wrapper:hover) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.password-toggle {
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.password-toggle:hover {
  color: #409eff;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 8px;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #66b1ff, #85c1ff);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 30px 16px;
  }
  
  .login-card {
    padding: 32px 24px;
  }
  
  .logo {
    width: 56px;
    height: 56px;
    font-size: 28px;
  }
  
  .title {
    font-size: 20px;
  }
}
</style>
