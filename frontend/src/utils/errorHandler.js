// 错误处理工具类
class ErrorHandler {
  static handle(error, defaultMessage = '操作失败') {
    console.error('错误详情:', error)
    
    let message = defaultMessage
    
    if (error.response) {
      // 服务器响应错误
      const status = error.response.status
      const data = error.response.data
      
      switch (status) {
        case 400:
          if (typeof data === 'object' && data !== null) {
            // 如果是字段错误，提取所有错误信息
            const errors = Object.values(data).flat()
            message = errors.join(', ')
          } else if (data.detail) {
            message = data.detail
          } else if (data.message) {
            message = data.message
          } else {
            message = '请求参数错误'
          }
          break
        case 401:
          message = '登录已过期，请重新登录'
          this.handleLogout()
          break
        case 403:
          message = '没有操作权限'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 429:
          message = '操作过于频繁，请稍后再试'
          break
        case 500:
          message = '服务器内部错误，请稍后再试'
          break
        default:
          if (data && data.message) {
            message = data.message
          } else if (data && data.detail) {
            message = data.detail
          } else {
            message = `服务器错误 (${status})`
          }
      }
    } else if (error.request) {
      // 请求发送失败
      message = '网络连接失败，请检查网络设置'
    } else {
      // 其他错误
      message = error.message || defaultMessage
    }
    
    return message
  }
  
  static handleLogout() {
    // 清除登录状态并跳转到登录页
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
  }
  
  static show(error, defaultMessage = '操作失败') {
    const message = this.handle(error, defaultMessage)
    
    // 使用Element Plus的消息提示
    if (typeof window !== 'undefined' && window.ElMessage) {
      window.ElMessage.error(message)
    } else if (typeof window !== 'undefined' && window.$message) {
      window.$message.error(message)
    } else {
      alert(message)
    }
    
    return message
  }
  
  static showSuccess(message) {
    if (typeof window !== 'undefined' && window.ElMessage) {
      window.ElMessage.success(message)
    } else if (typeof window !== 'undefined' && window.$message) {
      window.$message.success(message)
    } else {
      alert(message)
    }
  }
  
  static showWarning(message) {
    if (typeof window !== 'undefined' && window.ElMessage) {
      window.ElMessage.warning(message)
    } else if (typeof window !== 'undefined' && window.$message) {
      window.$message.warning(message)
    } else {
      alert(message)
    }
  }
  
  static showInfo(message) {
    if (typeof window !== 'undefined' && window.ElMessage) {
      window.ElMessage.info(message)
    } else if (typeof window !== 'undefined' && window.$message) {
      window.$message.info(message)
    } else {
      alert(message)
    }
  }
}

export default ErrorHandler