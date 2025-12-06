import axios from 'axios'
import { ElMessage } from 'element-plus'

const DEFAULT_ADMIN_API_BASE = 'http://127.0.0.1:8000/admin-api'
const ADMIN_API_BASE_URL = (localStorage.getItem('ADMIN_API_BASE') || import.meta.env.VITE_ADMIN_API_URL || DEFAULT_ADMIN_API_BASE)

const adminApi = axios.create({
  baseURL: ADMIN_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// 请求拦截器：添加token
adminApi.interceptors.request.use((config) => {
  // 确保headers对象存在
  if (!config.headers) {
    config.headers = {}
  }
  
  const token = localStorage.getItem('ADMIN_TOKEN')
  if (token && token.trim()) {
    // 确保Authorization头被正确设置
    config.headers.Authorization = `Bearer ${token.trim()}`
    if (import.meta.env.DEV) {
      console.log('[AdminApi] 请求拦截:', config.method?.toUpperCase(), config.url, 'Token:', token.substring(0, 20) + '...')
    }
  } else {
    if (import.meta.env.DEV) {
      console.warn('[AdminApi] 请求拦截: 没有Token', config.method?.toUpperCase(), config.url)
    }
  }
  
  return config
}, (error) => {
  return Promise.reject(error)
})

// 响应拦截器：处理错误
adminApi.interceptors.response.use(
  (res) => {
    return res
  },
  async (error) => {
    const resp = error.response
    if (!resp) {
      // 网络错误
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        ElMessage.error('请求超时，请稍后重试')
      } else {
        ElMessage.error('网络错误：无法连接管理后台')
      }
      return Promise.reject(error)
    }

    // 401错误：登录过期
    if (resp.status === 401) {
      const url = error.config?.url || ''
      // 登录接口返回401时不做处理，交由页面处理
      if (url.startsWith('/auth/login')) {
        return Promise.reject(error)
      }
      
      // 检查当前是否在管理后台页面
      const isAdminPage = location.pathname.startsWith('/admin') && location.pathname !== '/admin/login'
      if (isAdminPage) {
        // 清除token
        try { 
          localStorage.removeItem('ADMIN_TOKEN')
          localStorage.removeItem('ADMIN_REFRESH_TOKEN')
          localStorage.removeItem('ADMIN_USER')
        } catch {}
        
        // 显示错误提示，但不立即跳转，让页面自己处理
        const errorMsg = resp.data?.detail || '登录已过期，请重新登录'
        ElMessage.error(errorMsg)
        
        // 延迟跳转，给用户看到错误提示的时间
        setTimeout(() => {
          if (location.pathname !== '/admin/login') {
            location.href = '/admin/login'
          }
        }, 1500)
      }
      return Promise.reject(error)
    }

    // 其他错误
    if (resp.status >= 500) {
      ElMessage.error('服务器错误，请稍后重试')
    } else if (resp.status === 403) {
      ElMessage.error('没有权限执行此操作')
    } else if (resp.status === 404) {
      ElMessage.error('请求的资源不存在')
    }
    
    return Promise.reject(error)
  }
)

export default adminApi
