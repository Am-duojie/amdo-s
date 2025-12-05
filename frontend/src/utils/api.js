import axios from 'axios'
import ErrorHandler from './errorHandler'

// API基础地址配置
// 本地开发: http://127.0.0.1:8000/api
// 生产环境: http://你的服务器IP:8000/api 或 https://你的域名/api
/** @type {string} */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

console.log('API基础地址:', API_BASE_URL)

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
    console.log('API请求:', config.method?.toUpperCase(), config.url, config.data)
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => {
    console.log('API响应:', response.status, response.config.url, response.data)
    return response
  },
  (error) => {
    console.error('API错误:', error)
    
    // 处理401未授权错误
    if (error.response?.status === 401) {
      ErrorHandler.handleLogout()
    }
    
    return Promise.reject(error)
  }
)

export default api
