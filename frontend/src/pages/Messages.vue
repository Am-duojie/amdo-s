<template>
  <div class="messages-page">
    
    <div class="messages-container">
      <el-card class="messages-card">
        <el-row class="messages-row">
          <el-col :span="8" class="conversations-col">
            <h3 class="conversations-title">对话列表</h3>
            <el-scrollbar height="500px">
              <div
                v-for="item in conversations"
                :key="item.user.id"
                :class="['conversation-item', { active: selectedUser?.id === item.user.id }]"
                @click="handleSelectUser(item.user.id)"
              >
                <div class="conversation-header">
                  <div class="conversation-user">
                    <el-avatar :icon="UserFilled" :size="40" />
                    <div class="user-info">
                      <div class="username">{{ item.user.username }}</div>
                      <div class="last-message">{{ item.last_message.content }}</div>
                    </div>
                  </div>
                  <el-badge v-if="item.unread_count > 0" :value="item.unread_count" />
                </div>
              </div>
              <el-empty v-if="conversations.length === 0" description="暂无对话" :image-size="100" />
            </el-scrollbar>
          </el-col>
          <el-col :span="16" class="messages-col">
            <div v-if="selectedUser" class="messages-header">
              <div class="messages-header-row">
                <h3>与 {{ selectedUser.username }} 的对话</h3>
                <el-tag size="small" :type="wsConnected ? 'success' : 'danger'" class="ws-status-tag">
                  {{ wsConnected ? '实时连接正常' : '实时未连接，已走HTTP' }}
                </el-tag>
              </div>
            </div>
            <el-empty v-if="!selectedUser" description="请选择一个对话" :image-size="100" />
            <div v-else class="messages-content">
              <el-scrollbar height="400px" ref="scrollbarRef">
                <div
                  v-for="msg in messages"
                  :key="msg.id"
                  :class="['message-item', { 'message-right': msg.sender.id === authStore.user.id }]"
                >
                  <div class="message-bubble">
                    <div class="message-sender">{{ msg.sender.username }}</div>
                    <div v-if="msg.recalled" class="message-text recalled">消息已撤回</div>
                    <div v-else-if="msg.message_type === 'product'" class="message-product">
                      <div class="product-title">[商品] {{ msg.payload?.title }}</div>
                      <div class="product-price">¥{{ msg.payload?.price }}</div>
                    </div>
                    <div v-else class="message-text">{{ msg.content }}</div>
                    <div class="message-time-row">
                      <span class="message-time">{{ formatTime(msg.created_at) }}</span>
                      <span v-if="msg.sender.id === authStore.user.id && !msg.recalled" class="read-status">
                        {{ msg.is_read ? '已读' : '未读' }}
                      </span>
                    </div>
                    <div v-if="showRecallButton(msg)" class="message-actions">
                      <el-button link type="danger" size="small" @click="handleRecall(msg)">撤回</el-button>
                    </div>
                  </div>
                </div>
              </el-scrollbar>
            </div>
            <div v-if="selectedUser" class="message-input">
              <el-input
                v-model="messageContent"
                type="textarea"
                :rows="3"
                placeholder="输入消息..."
                @keyup.ctrl.enter="handleSendMessage"
                class="input-textarea"
              />
              <div class="input-actions">
                <el-button @click="openProductDialog" :loading="productsLoading" class="send-btn">
                  发送商品
                </el-button>
                <el-button type="primary" :icon="Position" @click="handleSendMessage" :loading="loading" class="send-btn">
                  发送
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <el-dialog v-model="productDialogVisible" title="选择要发送的商品" width="50%">
      <el-table :data="sellingProducts" style="width: 100%" height="320" v-loading="productsLoading">
        <el-table-column prop="title" label="标题" min-width="160" />
        <el-table-column prop="price" label="价格" width="120">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="success" v-if="row.status === 'active'">在售</el-tag>
            <el-tag type="info" v-else>下架</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleSendProduct(row)" :disabled="row.status !== 'active'">
              发送
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="productDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { UserFilled, Position } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import websocket from '@/utils/websocket'

const route = useRoute()
const authStore = useAuthStore()

const conversations = ref([])
const selectedUser = ref(null)
const messages = ref([])
const messageContent = ref('')
const loading = ref(false)
const scrollbarRef = ref(null)
const wsConnected = ref(false)
const isPageVisible = ref(typeof document !== 'undefined' ? document.visibilityState === 'visible' : true)
const isWindowFocused = ref(typeof document !== 'undefined' ? document.hasFocus() : true)
const isOnMessagesPage = () => route.path?.includes('/messages')
const productDialogVisible = ref(false)
const sellingProducts = ref([])
const productsLoading = ref(false)

onMounted(() => {
  wsConnected.value = websocket.isConnected
  websocket.on('connected', () => {
    wsConnected.value = true
  })
  websocket.on('disconnected', () => {
    wsConnected.value = false
  })

  loadConversations()
  const userId = route.query.user_id
  const productId = route.query.product_id
  if (userId) {
    handleSelectUser(parseInt(userId), productId ? parseInt(productId) : null)
  }
  
  // 连接WebSocket
  const token = localStorage.getItem('token')
  if (token) {
    websocket.connect(token)
    
    websocket.on('message', (data) => {
      handleWebSocketMessage(data)
    })
    websocket.on('connected', () => {
      wsConnected.value = true
    })
    websocket.on('disconnected', () => {
      wsConnected.value = false
    })
    websocket.on('error', () => {
      wsConnected.value = false
    })
  }
})

// 组件卸载时断开WebSocket
onUnmounted(() => {
  websocket.off('connected', () => {})
  websocket.off('disconnected', () => {})
})

const handleVisibilityChange = () => {
  isPageVisible.value = document.visibilityState === 'visible'
}
const handleFocus = () => {
  isWindowFocused.value = true
}
const handleBlur = () => {
  isWindowFocused.value = false
}

if (typeof document !== 'undefined') {
  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('focus', handleFocus)
  window.addEventListener('blur', handleBlur)
}

watch(() => selectedUser.value?.id, (userId) => {
  if (userId) {
    loadMessages(userId)
  }
})

watch(() => messages.value.length, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

const loadConversations = async () => {
  try {
    const res = await api.get('/messages/conversations/')
    conversations.value = res.data
  } catch (error) {
    console.error('加载对话列表失败:', error)
  }
}

const loadMessages = async (userId) => {
  loading.value = true
  try {
    const res = await api.get('/messages/with_user/', { params: { user_id: userId } })
    messages.value = res.data
    // 标记已读
    api.post('/messages/read/', { user_id: userId }).catch(() => {})
    nextTick(() => {
      scrollToBottom()
    })
  } catch (error) {
    console.error('加载消息失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSelectUser = async (userId, productId = null) => {
  const conversation = conversations.value.find((c) => c.user.id === userId)
  if (conversation) {
    selectedUser.value = conversation.user
    setConversationUnread(userId, 0)
  } else {
    try {
      const res = await api.get(`/users/${userId}/`)
      selectedUser.value = res.data
    } catch (error) {
      ElMessage.error('获取用户信息失败')
    }
  }

  // 进入对话时立即清空未读（后端已标记，前端主动刷新侧边栏角标）
  markMessagesReadLocal(userId)
  emitUnreadRefresh()
  markAsRead(userId)
}

const handleSendMessage = async () => {
  if (!messageContent.value.trim() || !selectedUser.value) return

  loading.value = true
  try {
    const productId = route.query.product_id
    const messageData = {
      receiver_id: selectedUser.value.id,
      product_id: productId ? parseInt(productId) : null,
      content: messageContent.value,
    }
    
    // 尝试通过WebSocket发送
    if (!websocket.send({ ...messageData, type: 'chat_message', message_type: 'text' })) {
      ElMessage.warning('实时连接不可用，已改为HTTP发送')
      // WebSocket失败时使用HTTP API
      await api.post('/messages/', { ...messageData, message_type: 'text' })
      loadMessages(selectedUser.value.id)
      loadConversations()
    }
    
    messageContent.value = ''
  } catch (error) {
    ElMessage.error('发送消息失败')
  } finally {
    loading.value = false
  }
}

const handleWebSocketMessage = (data) => {
  console.log('收到WebSocket消息:', data)
  if (data.type === 'new_message') {
    const isCurrent =
      selectedUser.value &&
      ((data.sender_id === selectedUser.value.id && data.receiver_id === authStore.user.id) ||
        (data.sender_id === authStore.user.id && data.receiver_id === selectedUser.value.id))

    if (isCurrent) {
      messages.value.push({
        id: data.id,
        sender: { id: data.sender_id, username: data.sender_username },
        receiver: { id: data.receiver_id, username: data.receiver_username },
        content: data.content,
        created_at: data.created_at,
        is_read: false, // 新消息统一视为未读，等阅读后再改
        message_type: data.message_type,
        payload: data.payload,
        recalled: data.recalled
      })
      // 如果当前会话且本端是接收者，立即上报已读
      // 仅在当前会话、我是接收方、WS已连、页面可见时自动已读（放宽：不再要求窗口聚焦）
      if (
        data.receiver_id === authStore.user.id &&
        wsConnected.value &&
        isPageVisible.value &&
        isOnMessagesPage()
      ) {
        markAsRead(data.sender_id)
        markMessagesReadLocal(data.sender_id)
        setConversationUnread(data.sender_id, 0)
      } else {
        // 我是发送者，不动未读计数
        if (data.sender_id === authStore.user.id) {
          setConversationUnread(data.receiver_id, 0)
        }
      }
    } else {
      // 不在当前会话且本端是接收者，增加未读
      if (data.receiver_id === authStore.user.id) {
        incrementConversationUnread(data.sender_id)
      }
    }
    if (data.receiver_id === authStore.user.id) {
      emitUnreadRefresh()
    }
  }

  if (data.type === 'message_recalled') {
    const target = messages.value.find((m) => m.id === data.message_id)
    if (target) {
      target.recalled = true
      target.message_type = 'recall'
      target.content = '消息已撤回'
    }
    loadConversations()
  }

  if (data.type === 'read_ack') {
    // 对方已读当前会话的消息，更新本端已发消息的已读状态
    let changed = false
    if (data.peer_id) {
      messages.value.forEach((m) => {
        if (m.sender.id === authStore.user.id && m.receiver.id === data.peer_id && !m.recalled && !m.is_read) {
          m.is_read = true
          changed = true
        }
      })
      // 已读回执后，清除对应会话未读
      setConversationUnread(data.peer_id, 0)
    }
    if (changed) {
      messages.value = [...messages.value]
    }
    // 会话列表同步更新未读
    loadConversations()
    emitUnreadRefresh()
  }
}

const markAsRead = async (peerId) => {
  if (!peerId) return
  if (!wsConnected.value) return
  try {
    await api.post('/messages/read/', { user_id: peerId })
    markMessagesReadLocal(peerId)
    setConversationUnread(peerId, 0)
    emitUnreadRefresh()
  } catch (error) {
    // 静默失败，避免打扰用户
  }
}

const emitUnreadRefresh = () => {
  window.dispatchEvent(new CustomEvent('refresh-unread'))
}

const setConversationUnread = (peerId, count) => {
  const conv = conversations.value.find((c) => c.user?.id === peerId)
  if (conv) conv.unread_count = count
}

const incrementConversationUnread = (peerId) => {
  const conv = conversations.value.find((c) => c.user?.id === peerId)
  if (conv) {
    conv.unread_count = (conv.unread_count || 0) + 1
  } else {
    // 若不存在会话，追加一个临时会话记录
    conversations.value.unshift({
      user: { id: peerId, username: `用户${peerId}` },
      last_message: null,
      unread_count: 1,
    })
  }
}

const markMessagesReadLocal = (peerId) => {
  let changed = false
  messages.value.forEach((m) => {
    if (m.sender.id === peerId && m.receiver.id === authStore.user.id && !m.is_read) {
      m.is_read = true
      changed = true
    }
  })
  if (changed) {
    // 触发视图更新
    messages.value = [...messages.value]
  }
}

const showRecallButton = (msg) => {
  if (!msg || msg.recalled) return false
  if (msg.sender.id !== authStore.user.id) return false
  if (!msg.recallable_until) return false
  return new Date(msg.recallable_until) > new Date()
}

const handleRecall = async (msg) => {
  try {
    await ElMessageBox.confirm('确定撤回这条消息？', '撤回', { type: 'warning' })
    await api.post(`/messages/${msg.id}/recall/`)
    msg.recalled = true
    msg.message_type = 'recall'
    msg.content = '消息已撤回'
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '撤回失败')
    }
  }
}

const openProductDialog = async () => {
  if (!selectedUser.value) {
    ElMessage.warning('请先选择对话')
    return
  }
  productDialogVisible.value = true
  if (sellingProducts.value.length === 0) {
    await loadSellingProducts()
  }
}

const loadSellingProducts = async () => {
  productsLoading.value = true
  try {
    const res = await api.get('/products/my_products/')
    sellingProducts.value = (res.data || []).filter((p) => p.status === 'active')
  } catch (error) {
    ElMessage.error('加载在售商品失败')
  } finally {
    productsLoading.value = false
  }
}

const handleSendProduct = async (product) => {
  if (!selectedUser.value) {
    ElMessage.warning('请先选择对话')
    return
  }
  try {
    const payload = { receiver_id: selectedUser.value.id, product_id: product.id, message_type: 'product', content: '' }
    if (!websocket.send({ ...payload, type: 'chat_message' })) {
      await api.post('/messages/', payload)
      await loadMessages(selectedUser.value.id)
      await loadConversations()
    }
    productDialogVisible.value = false
    ElMessage.success('商品已发送')
    emitUnreadRefresh()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送商品失败')
  }
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / (1000 * 60))
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  return date.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  if (scrollbarRef.value) {
    const scrollbar = scrollbarRef.value
    scrollbar.setScrollTop(scrollbar.wrapRef.scrollHeight)
  }
}
</script>

<style scoped>
.messages-page {
  background: #f5f7f9;
  min-height: 100vh;
  padding: 0;
}

.messages-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px;
}

.messages-card {
  border-radius: 8px;
}

.messages-row {
  min-height: 600px;
}

.conversations-col {
  border-right: 1px solid #e8e8e8;
  padding-right: 16px;
}

.conversations-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e8e8e8;
}

.conversation-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
}

.conversation-item:hover {
  background: #f5f5f5;
}

.conversation-item.active {
  background: #fff5e6;
  border: 1px solid #ff6a00;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-user {
  display: flex;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.last-message {
  font-size: 12px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.messages-col {
  padding-left: 16px;
  display: flex;
  flex-direction: column;
}

.messages-header {
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 12px;
  margin-bottom: 12px;
}

.messages-header-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ws-status-tag {
  transform: translateY(-2px);
}

.messages-header h3 {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.messages-content {
  flex: 1;
  margin-bottom: 16px;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
}

.message-item.message-right {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 12px;
  position: relative;
}

.message-item:not(.message-right) .message-bubble {
  background: #f0f0f0;
  color: #333;
}

.message-item.message-right .message-bubble {
  background: #ff6a00;
  color: #fff;
}

.message-sender {
  font-size: 12px;
  margin-bottom: 4px;
  opacity: 0.8;
}

.message-text {
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-text.recalled {
  color: #9ca3af;
  font-style: italic;
}

.message-product {
  background: #f3f4f6;
  border-radius: 6px;
  padding: 8px 10px;
  margin-bottom: 6px;
  color: #333;
}

.message-product .product-title {
  font-weight: 600;
}

.message-product .product-price {
  color: #f59e0b;
  margin-top: 4px;
}

.message-actions {
  margin-top: 4px;
  text-align: right;
}

.message-time {
  font-size: 10px;
  margin-top: 4px;
  opacity: 0.6;
}

.message-time-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.read-status {
  font-size: 11px;
  color: #6b7280;
}

.message-input {
  border-top: 1px solid #e8e8e8;
  padding-top: 12px;
}

.input-textarea {
  margin-bottom: 8px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

.send-btn {
  background: #ff6a00;
  border-color: #ff6a00;
}

.send-btn:hover {
  background: #ff8533;
  border-color: #ff8533;
}

@media (max-width: 768px) {
  .messages-row {
    flex-direction: column;
  }
  
  .conversations-col {
    border-right: none;
    border-bottom: 1px solid #e8e8e8;
    padding-right: 0;
    padding-bottom: 16px;
    margin-bottom: 16px;
  }
  
  .messages-col {
    padding-left: 0;
  }
}
</style>
