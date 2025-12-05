import axios from 'axios'
import { ElMessage } from 'element-plus'

const DEFAULT_ADMIN_API_BASE = 'http://127.0.0.1:8000/admin-api'
const ADMIN_API_BASE_URL = (localStorage.getItem('ADMIN_API_BASE') || import.meta.env.VITE_ADMIN_API_URL || DEFAULT_ADMIN_API_BASE)

const adminApi = axios.create({
  baseURL: ADMIN_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

adminApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('ADMIN_TOKEN')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let isRefreshing = false
let refreshPromise = null

adminApi.interceptors.response.use(
  (res) => res,
  async (error) => {
    const resp = error?.response
    if (!resp) {
      // 网络错误，尝试回退到默认基础地址重试一次
      try {
        const cfg = error.config || {}
        if ((ADMIN_API_BASE_URL !== DEFAULT_ADMIN_API_BASE) && !cfg.__retriedWithFallback) {
          const retry = axios.create({ baseURL: DEFAULT_ADMIN_API_BASE, headers: cfg.headers || { 'Content-Type': 'application/json' } })
          const token = localStorage.getItem('ADMIN_TOKEN')
          if (token) retry.defaults.headers.Authorization = `Bearer ${token}`
          cfg.__retriedWithFallback = true
          const method = (cfg.method || 'get').toLowerCase()
          const url = cfg.url || '/'
          const data = cfg.data
          const params = cfg.params
          const resp2 = await retry.request({ method, url, data, params })
          try { localStorage.setItem('ADMIN_API_BASE', DEFAULT_ADMIN_API_BASE) } catch {}
          return resp2
        }
      } catch (e) {
        // ignore
      }
      ElMessage.error('网络错误：无法连接管理后台')
      return Promise.reject(error)
    }
    if (resp.status === 401) {
      const url = error.config?.url || ''
      // 登录/刷新接口返回401时不做刷新与重定向，交由页面处理
      if (url.startsWith('/auth/')) {
        return Promise.reject(error)
      }
      const refreshToken = localStorage.getItem('ADMIN_REFRESH_TOKEN')
      if (!refreshToken) {
        try { localStorage.removeItem('ADMIN_TOKEN'); localStorage.removeItem('ADMIN_REFRESH_TOKEN') } catch {}
        location.href = '/admin/login'
        return Promise.reject(error)
      }
      if (!isRefreshing) {
        isRefreshing = true
        refreshPromise = adminApi.post('/auth/refresh', { refresh_token: refreshToken })
          .then(r => {
            const nt = r.data?.token
            if (nt) localStorage.setItem('ADMIN_TOKEN', nt)
            return nt
          })
          .catch(() => {
            try { localStorage.removeItem('ADMIN_TOKEN'); localStorage.removeItem('ADMIN_REFRESH_TOKEN') } catch {}
            location.href = '/admin/login'
            throw error
          })
          .finally(() => { isRefreshing = false })
      }
      try {
        const nt = await refreshPromise
        if (nt) {
          const cfg = error.config
          cfg.headers = cfg.headers || {}
          cfg.headers.Authorization = `Bearer ${nt}`
          return adminApi.request(cfg)
        }
      } catch (e) {
        return Promise.reject(e)
      }
    }
    const msg = resp.data?.detail || resp.data?.error || resp.statusText || '请求失败'
    if (resp.status === 403) {
      ElMessage.error('没有权限执行该操作')
    } else {
      ElMessage.error(`错误 ${resp.status}: ${msg}`)
    }
    return Promise.reject(error)
  }
)

export default adminApi
