<template>
  <div class="register-page">
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
      
      <!-- 注册表单 -->
      <el-form 
        ref="formRef"
        :model="form" 
        :rules="rules"
        class="register-form"
        @submit.prevent="handleSubmit"
      >
        <!-- 用户名 -->
        <el-form-item prop="username">
          <div class="input-wrapper">
            <el-input 
              v-model="form.username" 
              placeholder="请输入用户名（3-20个字符）"
              prefix-icon="User"
              clearable
              @blur="checkUsername"
            >
              <template #suffix>
                <el-icon v-if="usernameChecking" class="check-icon loading"><Loading /></el-icon>
                <el-icon v-else-if="usernameStatus?.available" class="check-icon success"><CircleCheck /></el-icon>
                <el-icon v-else-if="usernameStatus && !usernameStatus.available" class="check-icon error"><CircleClose /></el-icon>
              </template>
            </el-input>
          </div>
          <div v-if="usernameStatus" class="field-hint" :class="usernameStatus.available ? 'success' : 'error'">
            {{ usernameStatus.message }}
          </div>
        </el-form-item>
        
        <!-- 邮箱 -->
        <el-form-item prop="email">
          <div class="input-wrapper">
            <el-input 
              v-model="form.email" 
              type="email"
              placeholder="请输入邮箱（选填）"
              prefix-icon="Message"
              clearable
              @blur="checkEmail"
            >
              <template #suffix>
                <el-icon v-if="emailChecking" class="check-icon loading"><Loading /></el-icon>
                <el-icon v-else-if="emailStatus?.available && form.email" class="check-icon success"><CircleCheck /></el-icon>
                <el-icon v-else-if="emailStatus && !emailStatus.available" class="check-icon error"><CircleClose /></el-icon>
              </template>
            </el-input>
          </div>
          <div v-if="emailStatus && form.email" class="field-hint" :class="emailStatus.available ? 'success' : 'error'">
            {{ emailStatus.message }}
          </div>
        </el-form-item>
        
        <!-- 密码 -->
        <el-form-item prop="password">
          <div class="input-wrapper">
            <el-input 
              v-model="form.password" 
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码（至少6位）"
              prefix-icon="Lock"
              clearable
              @input="validatePassword"
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
          <!-- 密码强度指示器 -->
          <div v-if="form.password" class="password-strength">
            <div class="strength-bars">
              <div 
                v-for="i in 3" 
                :key="i" 
                class="strength-bar"
                :class="{ active: passwordStrength >= i, [`level-${passwordStrength}`]: passwordStrength >= i }"
              ></div>
            </div>
            <span class="strength-text" :class="`level-${passwordStrength}`">
              {{ ['', '弱', '中', '强'][passwordStrength] }}
            </span>
          </div>
        </el-form-item>
        
        <!-- 确认密码 -->
        <el-form-item prop="password2">
          <div class="input-wrapper">
            <el-input 
              v-model="form.password2" 
              :type="showPassword2 ? 'text' : 'password'"
              placeholder="请再次输入密码"
              prefix-icon="Lock"
              clearable
            >
              <template #suffix>
                <span @click="showPassword2 = !showPassword2" class="password-toggle">
                  <el-icon v-if="showPassword2">
                    <View />
                  </el-icon>
                  <el-icon v-else>
                    <Hide />
                  </el-icon>
                </span>
                <el-icon v-if="form.password2 && form.password === form.password2" class="check-icon success"><CircleCheck /></el-icon>
                <el-icon v-else-if="form.password2 && form.password !== form.password2" class="check-icon error"><CircleClose /></el-icon>
              </template>
            </el-input>
          </div>
        </el-form-item>
        
        <!-- 用户协议 -->
        <div class="agreement-section">
          <el-checkbox v-model="agreeToTerms" class="agreement-checkbox">
            我已阅读并同意
            <el-link type="primary" @click.prevent="showTermsDialog = true" :underline="false" class="agreement-link">
              《用户协议》
            </el-link>
            和
            <el-link type="primary" @click.prevent="showPrivacyDialog = true" :underline="false" class="agreement-link">
              《隐私政策》
            </el-link>
          </el-checkbox>
        </div>
        
        <!-- 注册按钮 -->
        <el-form-item>
          <el-button 
            type="primary"
            native-type="submit"
            class="submit-btn" 
            :loading="loading"
            :disabled="!agreeToTerms"
            block
          >
            立即注册
          </el-button>
        </el-form-item>
        
        <!-- 登录链接 -->
        <div class="login-section">
          <span class="login-text">已有账号？</span>
          <el-link 
            type="primary" 
            @click="$router.push('/login')" 
            class="login-link"
            :underline="false"
          >
            立即登录
          </el-link>
        </div>
      </el-form>
    </div>
    
    <!-- 底部信息 -->
    <div class="footer">
      <p>© 2024 咸鱼二手交易平台</p>
    </div>
    
    <!-- 用户协议对话框 -->
    <el-dialog v-model="showTermsDialog" title="用户协议" width="600px">
      <div class="dialog-content">
        <h3>欢迎使用咸鱼</h3>
        <p>在使用本平台服务前，请您仔细阅读本协议...</p>
        <p>1. 用户需保证提供信息真实有效</p>
        <p>2. 禁止发布违法违规商品信息</p>
        <p>3. 交易产生的纠纷由双方自行协商解决</p>
        <p>4. 平台保留最终解释权</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="showTermsDialog = false">我知道了</el-button>
      </template>
    </el-dialog>
    
    <!-- 隐私政策对话框 -->
    <el-dialog v-model="showPrivacyDialog" title="隐私政策" width="600px">
      <div class="dialog-content">
        <h3>隐私保护声明</h3>
        <p>我们重视您的隐私保护...</p>
        <p>1. 我们收集必要的用户信息用于提供服务</p>
        <p>2. 不会向第三方泄露您的个人信息</p>
        <p>3. 使用安全技术保护您的数据安全</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="showPrivacyDialog = false">我知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  User, Lock, Message, View, Hide, CircleClose, Close, 
  Loading, CircleCheck
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)

const form = ref({
  username: '',
  email: '',
  password: '',
  password2: ''
})

const loading = ref(false)
const showPassword = ref(false)
const showPassword2 = ref(false)
const errorMessage = ref('')
const agreeToTerms = ref(false)
const showTermsDialog = ref(false)
const showPrivacyDialog = ref(false)

const usernameStatus = ref(null)
const emailStatus = ref(null)
const usernameChecking = ref(false)
const emailChecking = ref(false)
const passwordStrength = ref(0)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  password2: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.value.password) {
          callback(new Error('两次密码输入不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 检查用户名
const checkUsername = async () => {
  if (!form.value.username || form.value.username.length < 3) {
    usernameStatus.value = null
    return
  }
  
  usernameChecking.value = true
  try {
    const result = await authStore.checkUsername(form.value.username)
    usernameStatus.value = result
  } catch (error) {
    console.error('检查用户名失败:', error)
  } finally {
    usernameChecking.value = false
  }
}

// 检查邮箱
const checkEmail = async () => {
  if (!form.value.email) {
    emailStatus.value = null
    return
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.value.email)) {
    emailStatus.value = { available: false, message: '邮箱格式不正确' }
    return
  }
  
  emailChecking.value = true
  try {
    const result = await authStore.checkEmail(form.value.email)
    emailStatus.value = result
  } catch (error) {
    console.error('检查邮箱失败:', error)
  } finally {
    emailChecking.value = false
  }
}

// 验证密码强度
const validatePassword = () => {
  const password = form.value.password
  if (!password) {
    passwordStrength.value = 0
    return
  }
  
  let strength = 0
  
  // 长度检查
  if (password.length >= 6) strength++
  
  // 包含字母和数字
  if (/[a-zA-Z]/.test(password) && /[0-9]/.test(password)) strength++
  
  // 包含特殊字符或长度>=10
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password) || password.length >= 10) strength++
  
  passwordStrength.value = strength
}

const handleSubmit = async () => {
  if (!agreeToTerms.value) {
    ElMessage.warning('请先同意用户协议和隐私政策')
    return
  }
  
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  errorMessage.value = ''
  
  try {
    const result = await authStore.register({
      username: form.value.username,
      email: form.value.email || undefined,
      password: form.value.password,
      password2: form.value.password2
    })

    if (result.success) {
      ElMessage.success({
        message: '注册成功，欢迎加入！',
        type: 'success',
        duration: 2000
      })
      
      setTimeout(() => {
        router.push('/')
      }, 500)
    } else {
      if (typeof result.error === 'object') {
        const errors = Object.values(result.error).flat()
        errorMessage.value = errors.join('；')
      } else {
        errorMessage.value = result.error || '注册失败'
      }
      
      setTimeout(() => {
        errorMessage.value = ''
      }, 5000)
    }
  } finally {
    loading.value = false
  }
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

/* 注册页面容器 */
.register-page {
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
.register-form {
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

/* 检查图标样式 */
.check-icon {
  font-size: 18px;
  margin-left: 4px;
}

.check-icon.success {
  color: #67c23a;
}

.check-icon.error {
  color: #ff4d4f;
}

.check-icon.loading {
  color: #999;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 密码切换按钮 */
.password-toggle {
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 4px;
}

/* 字段提示 */
.field-hint {
  margin-top: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.field-hint.success {
  background: #f0f9ff;
  color: #07c160;
  border: 1px solid #d1fae5;
}

.field-hint.error {
  background: #fff1f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

/* 密码强度指示器 */
.password-strength {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
  margin-left: 4px;
}

.strength-bars {
  display: flex;
  gap: 6px;
  flex: 1;
}

.strength-bar {
  height: 6px;
  background: #f5f5f5;
  border-radius: 3px;
  flex: 1;
  transition: all 0.3s ease;
}

.strength-bar.active {
  background: #ff6a00;
}

.strength-bar.active.level-1 {
  background: #ff4d4f;
}

.strength-bar.active.level-2 {
  background: #faad14;
}

.strength-bar.active.level-3 {
  background: #52c41a;
}

.strength-text {
  font-size: 12px;
  font-weight: 500;
  color: #999;
  min-width: 28px;
}

.strength-text.level-1 {
  color: #ff4d4f;
}

.strength-text.level-2 {
  color: #faad14;
}

.strength-text.level-3 {
  color: #52c41a;
}

/* 用户协议 */
.agreement-section {
  margin: 16px 0 24px;
  font-size: 13px;
  line-height: 1.5;
}

.agreement-checkbox {
  display: flex;
  align-items: flex-start;
}

:deep(.el-checkbox) {
  display: flex;
  align-items: flex-start;
}

:deep(.el-checkbox__label) {
  font-size: 13px;
  color: #666;
  margin-left: 6px;
  line-height: 1.5;
}

.agreement-link {
  color: #ff6a00;
  text-decoration: none;
  transition: color 0.2s;
}

.agreement-link:hover {
  color: #ff873d;
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
  display: flex;
  align-items: center;
  justify-content: center;
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
  opacity: 0.8;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-icon {
  animation: rotate 1s linear infinite;
  font-size: 18px;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 登录链接 */
.login-section {
  text-align: center;
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
}

.login-link {
  font-weight: 600;
  color: #ff6a00;
  text-decoration: none;
  transition: color 0.2s;
}

.login-link:hover {
  color: #ff873d;
  text-decoration: underline;
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

/* 对话框内容 */
.dialog-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  line-height: 1.8;
}

.dialog-content h3 {
  margin-bottom: 16px;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.dialog-content p {
  margin: 12px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-page {
    padding: 30px 16px;
  }
  
  .form-section {
    padding: 24px 16px;
    max-width: 100%;
  }
  
  .logo {
    width: 64px;
    height: 64px;
    font-size: 32px;
  }
  
  .logo-text {
    font-size: 20px;
  }
  
  .password-strength {
    gap: 8px;
  }
  
  .strength-bars {
    gap: 4px;
  }
}

@media (max-width: 480px) {
  .form-section {
    max-width: 100%;
  }
  
  .agreement-section {
    font-size: 12px;
  }
  
  :deep(.el-checkbox__label) {
    font-size: 12px;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #ff6a00;
  border-color: #ff6a00;
}

:deep(.el-checkbox__input.is-checked+.el-checkbox__label) {
  color: #ff6a00;
}

:deep(.el-checkbox__input.is-focus .el-checkbox__inner) {
  border-color: #ff6a00;
}

:deep(.el-link) {
  color: #ff6a00;
  font-size: 13px;
}

:deep(.el-link:hover) {
  color: #ff873d;
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid #f0f0f0;
  padding: 20px 24px 12px;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  padding: 20px 24px;
}

:deep(.el-dialog__footer) {
  border-top: 1px solid #f0f0f0;
  padding: 12px 24px 20px;
}

:deep(.el-button--primary) {
  background-color: #ff6a00;
  border-color: #ff6a00;
}

:deep(.el-button--primary:hover) {
  background-color: #ff873d;
  border-color: #ff873d;
}
</style>
