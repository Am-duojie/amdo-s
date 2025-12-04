class WebSocketManager {
  constructor() {
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 5000
    this.listeners = new Map()
    this.isConnected = false
  }

  connect(token) {
    if (!token) {
      console.error('WebSocket需要token')
      return
    }

    const wsUrl = `ws://127.0.0.1:8000/ws/chat/?token=${token}`
    
    try {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket连接成功')
        this.isConnected = true
        this.reconnectAttempts = 0
        this.emit('connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.emit('message', data)
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('WebSocket连接关闭')
        this.isConnected = false
        this.emit('disconnected')
        this.handleReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error)
        this.emit('error', error)
      }
    } catch (error) {
      console.error('WebSocket连接失败:', error)
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`尝试重连 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)
      
      setTimeout(() => {
        const token = localStorage.getItem('token')
        if (token) {
          this.connect(token)
        }
      }, this.reconnectInterval)
    }
  }

  send(data) {
    if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
      return true
    }
    console.error('WebSocket未连接，无法发送消息')
    return false
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.isConnected = false
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('WebSocket事件处理错误:', error)
        }
      })
    }
  }
}

export default new WebSocketManager()