// 获取完整的图片URL
export function getImageUrl(imagePath) {
  if (!imagePath || typeof imagePath !== 'string') return null
  // 如果已经是完整URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  // 否则拼接后端地址
  // 尝试从环境变量或localStorage获取API基础URL
  let baseUrl = import.meta.env.VITE_API_URL
  if (!baseUrl) {
    const backendNgrokUrl = localStorage.getItem('BACKEND_NGROK_URL')
    if (backendNgrokUrl) {
      baseUrl = backendNgrokUrl.replace('/api', '')
    } else {
      baseUrl = 'http://127.0.0.1:8000'
    }
  } else {
    baseUrl = baseUrl.replace('/api', '')
  }
  return `${baseUrl}${imagePath}`
}
