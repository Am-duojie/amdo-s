const WS_BASE = import.meta.env.VITE_WS_BASE || `ws://127.0.0.1:8000`

class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Map()
    this.isConnected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 20
    this.reconnectInterval = 2000
    this.selfCheckTimer = null
  }

  connect(token) {
    if (!token) {
      console.warn('WebSocket需要token')
      return
    }

    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return
    }

    const wsUrl = `${WS_BASE}/ws/chat/?token=${token}`
    console.info('[WS] connect ->', wsUrl)

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
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

      this.ws.onclose = (evt) => {
        this.isConnected = false
        console.warn('[WS] close', evt?.code, evt?.reason)
        this.emit('disconnected')
        this.handleReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('[WS] error', error)
        this.emit('error', error)
      }
    } catch (error) {
      console.error('WebSocket连接失败:', error)
    }

    this.startSelfCheck()
  }

  startSelfCheck() {
    if (this.selfCheckTimer) return
    this.selfCheckTimer = setInterval(() => {
      const token = localStorage.getItem('token')
      if (!token) return
      if (!this.isConnected) {
        this.connect(token)
      }
    }, 5000)
  }

  stopSelfCheck() {
    if (this.selfCheckTimer) {
      clearInterval(this.selfCheckTimer)
      this.selfCheckTimer = null
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        const token = localStorage.getItem('token')
        if (token) {
          this.connect(token)
        }
      }, this.reconnectInterval)
    }
  }

  send(data) {
    if (!data.type) data.type = 'chat_message'
    if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
      return true
    }
    return false
  }

  disconnect() {
    this.stopSelfCheck()
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
      const arr = this.listeners.get(event)
      const idx = arr.indexOf(callback)
      if (idx > -1) arr.splice(idx, 1)
    }
  }

  emit(event, data) {
    if (!this.listeners.has(event)) return
    this.listeners.get(event).forEach((cb) => {
      try {
        cb(data)
      } catch (e) {
        console.error('WebSocket事件处理错误:', e)
      }
    })
  }
}

export default new WebSocketService()