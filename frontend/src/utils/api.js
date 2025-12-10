import axios from 'axios'
import ErrorHandler from './errorHandler'

// API基础地址配置
// 本地开发: http://127.0.0.1:8000/api
// 生产环境: http://你的服务器IP:8000/api 或 https://你的域名/api
// ngrok 访问: 自动检测并使用后端的 ngrok 地址

// 检测是否通过 ngrok 访问
const isNgrokAccess = typeof window !== 'undefined' && 
  (window.location.hostname.includes('ngrok-free.dev') || 
   window.location.hostname.includes('ngrok.io') || 
   window.location.hostname.includes('ngrok.app'))

// 如果通过 ngrok 访问，尝试从 localStorage 获取后端 ngrok 地址
// 或者使用环境变量，或者从当前域名推断（假设后端和前端使用相同的 ngrok 账户）
let API_BASE_URL = import.meta.env.VITE_API_URL

if (!API_BASE_URL) {
  if (isNgrokAccess) {
    // 通过 ngrok 访问时，尝试获取后端地址
    const backendNgrokUrl = localStorage.getItem('BACKEND_NGROK_URL') || 
                           import.meta.env.VITE_BACKEND_NGROK_URL
    
    if (backendNgrokUrl) {
      API_BASE_URL = `${backendNgrokUrl}/api`
    } else {
      // 如果前端和后端使用相同的 ngrok 账户，可以尝试推断
      // 但通常前后端地址不同，所以需要手动配置
      console.warn('通过 ngrok 访问但未配置后端地址，请设置 BACKEND_NGROK_URL')
      // 临时方案：使用相对路径，但这需要 vite proxy 支持（通过 ngrok 时可能不工作）
      API_BASE_URL = '/api'
    }
  } else {
    // 本地访问，使用 localhost
    API_BASE_URL = 'http://127.0.0.1:8000/api'
  }
}
const API_DEBUG = (import.meta.env.VITE_API_DEBUG === 'true') || import.meta.env.DEV || (typeof localStorage !== 'undefined' && localStorage.getItem('DEBUG_API') === 'true')
if (API_DEBUG) console.log('API基础地址:', API_BASE_URL)

/** @type {import('axios').AxiosInstance} */
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15秒超时（云服务器可能需要更长时间）
})

// 请求拦截器 - 添加token
api.interceptors.request.use(
  (config) => {
    if (API_DEBUG) console.log('API请求:', config.method?.toUpperCase(), config.url, config.data)
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    if (API_DEBUG) console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => {
    if (API_DEBUG) console.log('API响应:', response.status, response.config.url, response.data)
    return response
  },
  (error) => {
    if (API_DEBUG) console.error('API错误:', error)
    const status = error.response?.status
    const url = error.response?.config?.url || ''
    // 登录/注册等接口返回401时不要强制登出，交由页面显示错误
    if (status === 401) {
      const isAuthEndpoint =
        url.includes('/auth/login/') ||
        url.includes('/users/register/') ||
        url.includes('/users/check_username/') ||
        url.includes('/users/check_email/')

      // 拉取消息/未读等轮询接口，401 时不触发登出，直接让调用方处理
      const isMessageEndpoint =
        url.includes('/messages/conversations') ||
        url.includes('/messages/with_user') ||
        url.includes('/messages/read') ||
        url.includes('/messages/query')

      if (!isAuthEndpoint && !isMessageEndpoint) {
        const refreshToken = localStorage.getItem('refreshToken')
        if (refreshToken) {
          ErrorHandler.handleLogout()
        } else {
          ErrorHandler.handleLogout()
        }
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
