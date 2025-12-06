import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import adminApi from '@/utils/adminApi'

export const useAdminAuthStore = defineStore('adminAuth', () => {
  const user = ref(null)
  const loading = ref(true)

  const init = async () => {
    const token = localStorage.getItem('ADMIN_TOKEN')
    const refreshToken = localStorage.getItem('ADMIN_REFRESH_TOKEN')
    const savedUser = localStorage.getItem('ADMIN_USER')
    
    if (token && savedUser) {
      user.value = JSON.parse(savedUser)
      // 验证token是否有效
      try {
        const res = await adminApi.get('/auth/me')
        if (res.data?.user) {
          user.value = res.data.user
          localStorage.setItem('ADMIN_USER', JSON.stringify(res.data.user))
        }
      } catch (error) {
        // Token可能已过期，清除状态
        localStorage.removeItem('ADMIN_TOKEN')
        localStorage.removeItem('ADMIN_REFRESH_TOKEN')
        localStorage.removeItem('ADMIN_USER')
        user.value = null
      }
    } else {
      // 没有token，清除所有状态
      localStorage.removeItem('ADMIN_TOKEN')
      localStorage.removeItem('ADMIN_REFRESH_TOKEN')
      localStorage.removeItem('ADMIN_USER')
      user.value = null
    }
    loading.value = false
  }

  const login = async (username, password) => {
    try {
      loading.value = true
      const response = await adminApi.post('/auth/login', { username, password })
      const { token, refresh_token, user: userData } = response.data || {}
      
      if (token) {
        localStorage.setItem('ADMIN_TOKEN', token)
        if (refresh_token) {
          localStorage.setItem('ADMIN_REFRESH_TOKEN', refresh_token)
        }
        
        // 登录后拉取最新的用户资料
        try {
          const me = await adminApi.get('/auth/me')
          if (me.data?.user) {
            user.value = me.data.user
            localStorage.setItem('ADMIN_USER', JSON.stringify(me.data.user))
          } else if (userData) {
            user.value = userData
            localStorage.setItem('ADMIN_USER', JSON.stringify(userData))
          }
        } catch (error) {
          console.error('获取用户信息失败:', error)
          // 如果获取用户信息失败，使用登录返回的用户信息
          if (userData) {
            user.value = userData
            localStorage.setItem('ADMIN_USER', JSON.stringify(userData))
          } else {
            // 如果都没有，至少设置一个基本的用户对象
            user.value = { username, permissions: [] }
            localStorage.setItem('ADMIN_USER', JSON.stringify(user.value))
          }
        }
        
        // 确保 loading 状态已更新
        loading.value = false
        
        return { success: true }
      }
      
      loading.value = false
      return {
        success: false,
        error: '登录失败：未收到token'
      }
    } catch (error) {
      console.error('登录错误:', error)
      loading.value = false
      return {
        success: false,
        error: error.response?.data?.detail || error.response?.data?.error || '登录失败，请检查用户名和密码'
      }
    }
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('ADMIN_REFRESH_TOKEN')
      if (refreshToken) {
        await adminApi.post('/auth/logout', { refresh_token: refreshToken })
      }
    } catch (error) {
      console.error('登出错误:', error)
    } finally {
      localStorage.removeItem('ADMIN_TOKEN')
      localStorage.removeItem('ADMIN_REFRESH_TOKEN')
      localStorage.removeItem('ADMIN_USER')
      user.value = null
    }
  }

  const hasPerm = (code) => {
    if (!user.value) return false
    const perms = user.value.permissions || []
    // 支持通配符权限
    if (perms.includes('*')) return true
    return perms.includes(code)
  }

  const isAuthed = computed(() => {
    const token = localStorage.getItem('ADMIN_TOKEN')
    return !!token && !!user.value
  })

  return {
    user,
    loading,
    init,
    login,
    logout,
    hasPerm,
    isAuthed
  }
})
