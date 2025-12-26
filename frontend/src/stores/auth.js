import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(true)

  const init = async () => {
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (token && savedUser) {
      user.value = JSON.parse(savedUser)
      // 验证token是否有效
      try {
        const res = await api.get('/users/me/')
        user.value = res.data
        localStorage.setItem('user', JSON.stringify(res.data))
      } catch {
        // Token无效，尝试刷新或登出
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        user.value = null
      }
    }
    loading.value = false
  }

  const login = async (username, password) => {
    try {
      console.log('尝试登录:', { username, password })
      // 使用新的登录端点
      const response = await api.post('/auth/login/', { username, password })
      console.log('登录响应:', response.data)
      const token = response.data.access
      const refreshToken = response.data.refresh
      localStorage.setItem('token', token)
      localStorage.setItem('refreshToken', refreshToken)
      
      // 登录后拉取最新的用户资料，确保路由守卫与页面状态正确
      try {
        const me = await api.get('/users/me/')
        user.value = me.data
        localStorage.setItem('user', JSON.stringify(me.data))
      } catch {
        user.value = response.data.user
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }
      
      return { success: true }
    } catch (error) {
      console.error('登录错误:', error)
      console.error('错误响应:', error.response?.data)
      return {
        success: false,
        error: error.response?.data?.error || error.response?.data?.detail || '登录失败'
      }
    }
  }

  const register = async (userData) => {
    try {
      console.log('注册请求数据:', userData)
      const response = await api.post('/users/register/', userData)
      console.log('注册响应:', response.data)
      const token = response.data.token
      localStorage.setItem('token', token)
      
      user.value = response.data.user
      localStorage.setItem('user', JSON.stringify(response.data.user))
      
      return { success: true }
    } catch (error) {
      console.error('注册错误:', error)
      console.error('注册错误响应:', error.response?.data)
      return {
        success: false,
        error: error.response?.data || '注册失败'
      }
    }
  }

  const checkUsername = async (username) => {
    try {
      const response = await api.post('/users/check_username/', { username })
      return response.data
    } catch (error) {
      console.error('检查用户名错误:', error)
      return {
        available: false,
        message: error.response?.data?.error || '检查失败'
      }
    }
  }

  const checkEmail = async (email) => {
    try {
      const response = await api.post('/users/check_email/', { email })
      return response.data
    } catch (error) {
      console.error('检查邮箱错误:', error)
      return {
        available: false,
        message: error.response?.data?.error || '检查失败'
      }
    }
  }

  const updateProfile = async (profileData) => {
    try {
      const response = await api.patch('/users/me/', profileData)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      return { success: true, message: '更新成功' }
    } catch (error) {
      console.error('更新个人资料错误:', error)
      return {
        success: false,
        error: error.response?.data || '更新失败'
      }
    }
  }

  const changePassword = async (oldPassword, newPassword, newPassword2) => {
    try {
      const response = await api.post('/users/change-password/', {
        old_password: oldPassword,
        new_password: newPassword,
        new_password2: newPassword2
      })
      // 更新token
      localStorage.setItem('token', response.data.token)
      return { success: true, message: response.data.message }
    } catch (error) {
      console.error('修改密码错误:', error)
      return {
        success: false,
        error: error.response?.data?.error || '修改失败'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    user.value = null
  }

  return {
    user,
    loading,
    init,
    login,
    register,
    checkUsername,
    checkEmail,
    updateProfile,
    changePassword,
    logout
  }
})






