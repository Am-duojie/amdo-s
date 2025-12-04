<template>
  <div class="login-page">
    <!-- Logo区域 -->
    <div class="logo-section">
      <div class="logo-wrapper">
        <div class="logo">🐟</div>
        <h1 class="logo-text">咸鱼 - 二手交易平台</h1>
      </div>
    </div>
    
    <!-- 表单区域 -->
    <div class="form-section">
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
          <div class="input-wrapper">
            <el-input 
              v-model="form.username" 
              placeholder="请输入用户名或手机号"
              prefix-icon="User"
              clearable
              @keyup.enter="handleSubmit"
            />
          </div>
        </el-form-item>
        
        <el-form-item prop="password">
          <div class="input-wrapper">
            <el-input 
              v-model="form.password" 
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              prefix-icon="Lock"
              clearable
              @keyup.enter="handleSubmit"
            >
              <template #suffix>
                <span @click="showPassword = !showPassword" class="password-toggle">
                  <el-icon v-if="showPassword">
                    <View />
                  </el-icon>
                  <el-icon v-else>
                    <Hide />
                  </el-icon>
                </span>
              </template>
            </el-input>
          </div>
        </el-form-item>
        
        <!-- 记住我和忘记密码 -->
        <div class="form-options">
          <el-checkbox v-model="rememberMe" class="remember-checkbox">
            记住用户名
          </el-checkbox>
          <el-link 
            type="primary" 
            @click="showForgotPassword" 
            class="forgot-link"
            :underline="false"
          >
            忘记密码？
          </el-link>
        </div>
        
        <!-- 登录按钮 -->
        <el-form-item>
          <el-button 
            type="primary"
            native-type="submit"
            class="submit-btn" 
            :loading="loading"
            block
          >
            登录
          </el-button>
        </el-form-item>
        
        <!-- 注册链接 -->
        <div class="register-section">
          <span class="register-text">还没有账号？</span>
          <el-link 
            type="primary" 
            @click="$router.push('/register')" 
            class="register-link"
            :underline="false"
          >
            立即注册
          </el-link>
        </div>
        
        <!-- 其他登录方式 -->
        <div class="other-login">
          <div class="divider">
            <span class="divider-text">其他登录方式</span>
          </div>
          <div class="other-login-methods">
            <div class="login-method wechat">
              <el-icon class="method-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="24" height="24">
                  <path d="M921.6 256c-30.464 0-55.04 24.576-55.04 55.04v40.96c0 5.12 4.096 9.216 9.216 9.216h36.864c30.464 0 55.04 24.576 55.04 55.04v281.6c0 30.464-24.576 55.04-55.04 55.04h-36.864c-5.12 0-9.216 4.096-9.216 9.216v40.96c0 30.464-24.576 55.04-55.04 55.04h-368.64c-30.464 0-55.04-24.576-55.04-55.04v-40.96c0-5.12-4.096-9.216-9.216-9.216h-36.864c-30.464 0-55.04-24.576-55.04-55.04v-281.6c0-30.464 24.576-55.04 55.04-55.04h36.864c5.12 0 9.216-4.096 9.216-9.216v-40.96c0-30.464 24.576-55.04 55.04-55.04h368.64z m-194.56 512h204.8v-204.8h-204.8v204.8z m-102.4 0h102.4v-204.8h-102.4v204.8z m-102.4 0h102.4v-204.8h-102.4v204.8z" fill="currentColor" />
                </svg>
              </el-icon>
              <span>微信登录</span>
            </div>
            <div class="login-method qq">
              <el-icon class="method-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </el-icon>
              <span>QQ登录</span>
            </div>
          </div>
        </div>
      </el-form>
    </div>
    
    <!-- 底部信息 -->
    <div class="footer">
      <p>© 2024 咸鱼二手交易平台</p>
    </div>
    
    <!-- 忘记密码对话框 -->
    <el-dialog 
      v-model="forgotPasswordVisible" 
      title="密码重置" 
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="resetForm">
        <el-form-item label="注册邮箱">
          <el-input 
            v-model="resetForm.email" 
            type="email"
            placeholder="请输入注册时的邮箱地址"
            :prefix-icon="Message"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="forgotPasswordVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleResetPassword" 
          :loading="resetLoading"
        >
          发送重置链接
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  User, Lock, View, Hide, CircleClose, Close, 
  Loading, InfoFilled, Message 
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)

const form = ref({
  username: '',
  password: ''
})

const resetForm = ref({
  email: ''
})

const loading = ref(false)
const resetLoading = ref(false)
const errorMessage = ref('')
const forgotPasswordVisible = ref(false)
const showPassword = ref(false)
const rememberMe = ref(false)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

// 页面加载时读取记住的用户名
onMounted(() => {
  const savedUsername = localStorage.getItem('rememberedUsername')
  if (savedUsername) {
    form.value.username = savedUsername
    rememberMe.value = true
  }
})

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  errorMessage.value = ''
  
  try {
    const result = await authStore.login(form.value.username, form.value.password)

    if (result.success) {
      // 记住用户名
      if (rememberMe.value) {
        localStorage.setItem('rememberedUsername', form.value.username)
      } else {
        localStorage.removeItem('rememberedUsername')
      }
      
      ElMessage.success({
        message: '登录成功，欢迎回来！',
        type: 'success',
        duration: 2000
      })
      
      // 延迟跳转，让用户看到成功消息
      setTimeout(() => {
        router.push('/')
      }, 500)
    } else {
      errorMessage.value = result.error || '登录失败，请检查用户名和密码'
      // 自动清除错误消息
      setTimeout(() => {
        errorMessage.value = ''
      }, 5000)
    }
  } finally {
    loading.value = false
  }
}

const showForgotPassword = () => {
  forgotPasswordVisible.value = true
  resetForm.value.email = ''
}

const handleResetPassword = async () => {
  if (!resetForm.value.email) {
    ElMessage.warning('请输入邮箱地址')
    return
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(resetForm.value.email)) {
    ElMessage.warning('请输入有效的邮箱地址')
    return
  }

  resetLoading.value = true
  // TODO: 实现密码重置功能（需要后端支持）
  setTimeout(() => {
    resetLoading.value = false
    ElMessage.success('重置链接已发送到您的邮箱，请检查邮件')
    forgotPasswordVisible.value = false
  }, 1000)
}
</script>

<style scoped>
/* 全局样式重置 */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #333;
  background-color: #f5f5f5;
}

/* 登录页面容器 */
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  background-color: #fff;
}

/* Logo区域 */
.logo-section {
  text-align: center;
  margin-bottom: 40px;
}

.logo-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo {
  width: 80px;
  height: 80px;
  background-color: #ff6a00;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(255, 106, 0, 0.2);
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  color: #ff6a00;
  margin: 0;
}

/* 表单区域 */
.form-section {
  width: 100%;
  max-width: 400px;
  background-color: #fff;
  border-radius: 12px;
  padding: 32px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
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

.input-wrapper {
  margin-bottom: 16px;
}

/* Element Plus 样式覆盖 */
:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-form-item__error) {
  font-size: 12px;
  padding-top: 4px;
  color: #ff4d4f;
}

:deep(.el-input) {
  width: 100%;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  height: 48px;
  box-shadow: none;
  transition: all 0.3s ease;
  border-color: #d9d9d9;
}

:deep(.el-input__wrapper:hover) {
  border-color: #ff6a00;
  box-shadow: 0 0 0 2px rgba(255, 106, 0, 0.1);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #ff6a00;
  box-shadow: 0 0 0 2px rgba(255, 106, 0, 0.1);
}

:deep(.el-input__prefix) {
  color: #999;
  margin-right: 8px;
}

:deep(.el-input__input) {
  font-size: 15px;
}

:deep(.el-input__suffix-inner) {
  color: #999;
}

.password-toggle {
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
}

:deep(.el-checkbox__label) {
  font-size: 14px;
  color: #666;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #ff6a00;
  border-color: #ff6a00;
}

:deep(.el-checkbox__input.is-checked+.el-checkbox__label) {
  color: #ff6a00;
}

.forgot-link {
  font-size: 14px;
  color: #ff6a00;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  height: 48px;
  background-color: #ff6a00;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.submit-btn:hover:not(:disabled) {
  background-color: #ff873d;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 106, 0, 0.3);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  background-color: #ffd7b3;
  cursor: not-allowed;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 注册链接 */
.register-section {
  text-align: center;
  margin-bottom: 24px;
  font-size: 14px;
  color: #666;
}

.register-link {
  font-weight: 600;
  color: #ff6a00;
  text-decoration: none;
}

.register-link:hover {
  text-decoration: underline;
}

/* 其他登录方式 */
.other-login {
  margin-top: 20px;
}

.divider {
  display: flex;
  align-items: center;
  margin: 20px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background-color: #e8e8e8;
}

.divider-text {
  padding: 0 16px;
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}

.other-login-methods {
  display: flex;
  justify-content: center;
  gap: 32px;
}

.login-method {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 12px;
  border-radius: 8px;
}

.login-method:hover {
  background-color: #fafafa;
  transform: translateY(-2px);
}

.method-icon {
  font-size: 24px;
  color: #666;
  margin-bottom: 4px;
}

.login-method.wechat .method-icon {
  color: #07c160;
}

.login-method.qq .method-icon {
  color: #12b7f5;
}

.login-method span {
  font-size: 12px;
  color: #666;
}

/* 底部信息 */
.footer {
  margin-top: 40px;
  text-align: center;
  font-size: 12px;
  color: #999;
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
  .login-page {
    padding: 30px 16px;
  }
  
  .form-section {
    padding: 24px 16px;
  }
  
  .logo {
    width: 64px;
    height: 64px;
    font-size: 32px;
  }
  
  .logo-text {
    font-size: 20px;
  }
  
  .other-login-methods {
    gap: 24px;
  }
}

@media (max-width: 480px) {
  .form-section {
    max-width: 100%;
  }
}

/* 复选框样式覆盖 */
:deep(.el-checkbox__input.is-focus .el-checkbox__inner) {
  border-color: #ff6a00;
}

/* 链接样式覆盖 */
:deep(.el-link) {
  color: #ff6a00;
}

:deep(.el-link:hover) {
  color: #ff873d;
}
</style>
