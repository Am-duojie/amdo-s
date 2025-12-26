<template>
  <div class="service-chat-page">
    <div class="page-header">
      <h2>客服对话</h2>
      <el-button size="small" @click="loadConversations">刷新</el-button>
    </div>

    <div class="chat-shell">
      <div class="chat-sidebar">
        <el-input
          v-model="keyword"
          placeholder="搜索用户"
          clearable
          class="search-input"
        />
        <el-scrollbar class="conversation-list">
          <div
            v-for="item in filteredConversations"
            :key="item.user.id"
            class="conversation-item"
            :class="{ active: selectedUser?.id === item.user.id }"
            @click="selectConversation(item.user)"
          >
            <div class="conversation-header">
              <span class="conversation-name">{{ item.user.username }}</span>
              <span v-if="item.unread_count" class="conversation-badge">{{ item.unread_count }}</span>
            </div>
            <div class="conversation-preview">{{ item.last_message?.content || '-' }}</div>
          </div>
          <el-empty v-if="!loadingConversations && filteredConversations.length === 0" description="暂无会话" />
        </el-scrollbar>
      </div>

      <div class="chat-panel">
        <div class="chat-panel-header">
          <div class="chat-title">{{ selectedUser?.username || '请选择用户' }}</div>
          <el-button size="small" @click="refreshMessages" :disabled="!selectedUser">刷新消息</el-button>
        </div>

        <el-scrollbar class="chat-messages">
          <div v-if="loadingMessages" class="loading-row">
            <el-skeleton :rows="4" animated />
          </div>
          <div v-else>
            <div v-for="msg in messages" :key="msg.id" class="message-row" :class="{ self: msg.sender?.id === serviceUserId }">
              <div
                class="message-bubble"
                :class="{ product: msg.message_type === 'product', image: msg.message_type === 'image' }"
              >
                <div v-if="msg.message_type === 'product'" class="message-product">
                  <div class="product-card" @click="handleMessageProductClick(msg)">
                    <img
                      v-if="msg.payload?.cover"
                      :src="getImageUrl(msg.payload.cover)"
                      alt="商品图片"
                      class="product-image"
                    />
                    <div class="product-info">
                      <div class="product-title">{{ msg.payload?.title || '商品' }}</div>
                      <div class="product-price">¥{{ msg.payload?.price || '0.00' }}</div>
                    </div>
                  </div>
                </div>
                <div v-else-if="msg.message_type === 'image'" class="message-image">
                  <el-image
                    v-if="msg.image"
                    :src="getImageUrl(msg.image)"
                    :preview-src-list="[getImageUrl(msg.image)]"
                    fit="cover"
                    :hide-on-click-modal="true"
                    class="message-image-img"
                  />
                  <div v-else>[图片]</div>
                </div>
                <div v-else>{{ msg.content || '[消息]' }}</div>
              </div>
              <div class="message-time">{{ formatTime(msg.created_at) }}</div>
            </div>
            <el-empty v-if="selectedUser && messages.length === 0" description="暂无消息" />
          </div>
        </el-scrollbar>

        <div v-show="!isPreviewing" class="chat-input">
          <div class="chat-actions">
            <el-button size="small" plain @click="triggerImageUpload" :disabled="!selectedUser">图片</el-button>
            <el-button size="small" plain @click="openOrderDrawer" :disabled="!selectedUser">发送商品</el-button>
            <input ref="imageInputRef" type="file" accept="image/*" multiple class="hidden-input" @change="handleImageChange" />
          </div>
          <div v-if="pendingImageUrls.length" class="pending-image-list">
            <div v-for="(url, index) in pendingImageUrls" :key="url" class="pending-image-item">
              <img :src="url" alt="待发送图片" />
              <el-button
                link
                type="danger"
                size="small"
                @click="removePendingImage(index)"
              >
                移除
              </el-button>
            </div>
          </div>
          <el-input
            v-model="messageText"
            type="textarea"
            :rows="2"
            placeholder="输入消息"
            @paste="handlePasteImage"
          />
          <el-button type="primary" class="send-btn" :loading="sending" @click="sendMessage" :disabled="!selectedUser">
            发送
          </el-button>
        </div>
      </div>
    </div>

    <el-drawer v-model="orderDrawerVisible" title="选择订单商品" size="420px">
      <div class="drawer-header">
        <el-input v-model="orderKeyword" placeholder="搜索订单/商品" clearable />
        <el-button size="small" @click="loadOrderItems">搜索</el-button>
      </div>
      <el-tabs v-model="orderType" @tab-change="loadOrderItems">
        <el-tab-pane label="易淘订单" name="secondhand" />
        <el-tab-pane label="官方验订单" name="verified" />
        <el-tab-pane label="回收订单" name="recycle" />
      </el-tabs>
      <div class="drawer-body" v-loading="orderLoading">
        <div v-if="orderItems.length === 0 && !orderLoading" class="empty-items">
          <el-empty description="暂无可选订单" />
        </div>
        <div v-else class="order-list">
          <div v-for="item in orderItems" :key="`${orderType}-${item.id}`" class="order-item">
            <div class="order-cover">
              <img v-if="item.cover" :src="getImageUrl(item.cover)" alt="封面" />
              <div v-else class="order-cover-empty">无图</div>
            </div>
            <div class="order-info">
              <div class="order-title">{{ item.title }}</div>
              <div class="order-price">¥{{ item.price || '0.00' }}</div>
            </div>
            <div class="order-action">
              <el-button size="small" type="primary" @click="sendProduct(item)">发送</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import adminApi from '@/utils/adminApi'
import { getImageUrl } from '@/utils/image'

const conversations = ref([])
const messages = ref([])
const selectedUser = ref(null)
const serviceUserId = ref(null)
const serviceToken = ref('')
const wsRef = ref(null)
const wsConnected = ref(false)
let reconnectTimer = null
const imageInputRef = ref(null)
const keyword = ref('')
const messageText = ref('')
const loadingConversations = ref(false)
const loadingMessages = ref(false)
const sending = ref(false)
const orderDrawerVisible = ref(false)
const orderType = ref('secondhand')
const orderKeyword = ref('')
const orderItems = ref([])
const orderLoading = ref(false)
const pendingImageFiles = ref([])
const pendingImageUrls = ref([])
const isPreviewing = ref(false)
let previewObserver = null
const router = useRouter()

const filteredConversations = computed(() => {
  const key = keyword.value.trim().toLowerCase()
  if (!key) return conversations.value
  return conversations.value.filter((item) => (item.user?.username || '').toLowerCase().includes(key))
})

const loadConversations = async () => {
  loadingConversations.value = true
  try {
    const res = await adminApi.get('/service/conversations')
    serviceUserId.value = res.data?.service_user_id || serviceUserId.value
    conversations.value = res.data?.results || []
  } catch (error) {
    ElMessage.error('加载会话失败')
  } finally {
    loadingConversations.value = false
  }
}

const getWsBase = () => {
  if (import.meta.env.VITE_WS_BASE) return import.meta.env.VITE_WS_BASE
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = window.location.hostname === 'localhost' ? 'localhost' : '127.0.0.1'
  return `${protocol}://${host}:8000`
}

const ensureServiceToken = async () => {
  if (serviceToken.value) return serviceToken.value
  const res = await adminApi.get('/service/token')
  serviceToken.value = res.data?.token || ''
  serviceUserId.value = res.data?.service_user_id || serviceUserId.value
  return serviceToken.value
}

const connectWs = async () => {
  const token = await ensureServiceToken()
  if (!token || wsRef.value) return
  const wsUrl = `${getWsBase()}/ws/chat/?token=${token}`
  const ws = new WebSocket(wsUrl)
  wsRef.value = ws

  ws.onopen = () => {
    wsConnected.value = true
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleWsMessage(data)
    } catch {
      // ignore
    }
  }

  ws.onclose = () => {
    wsConnected.value = false
    wsRef.value = null
    if (!reconnectTimer) {
      reconnectTimer = setTimeout(() => {
        reconnectTimer = null
        connectWs()
      }, 2000)
    }
  }

  ws.onerror = () => {
    wsConnected.value = false
  }
}

const handleWsMessage = async (data) => {
  if (!data || data.type !== 'new_message') return
  const fallbackContent = data.message_type === 'image'
    ? '[图片]'
    : data.message_type === 'product'
      ? `[商品]${data.product_title || ''}`
      : ''
  const msg = {
    id: data.id,
    sender: { id: data.sender_id, username: data.sender_username },
    receiver: { id: data.receiver_id, username: data.receiver_username },
    content: data.content || fallbackContent,
    message_type: data.message_type,
    image: data.image || '',
    payload: data.payload,
    created_at: data.created_at,
    recalled: data.recalled
  }

  const peerId = msg.sender.id === serviceUserId.value ? msg.receiver.id : msg.sender.id
  const existing = conversations.value.find((item) => item.user.id === peerId)
  if (existing) {
    existing.last_message = { content: msg.content, message_type: msg.message_type, created_at: msg.created_at }
    if (msg.sender.id !== serviceUserId.value && (!selectedUser.value || selectedUser.value.id !== peerId)) {
      existing.unread_count = (existing.unread_count || 0) + 1
    }
  } else {
    conversations.value.unshift({
      user: msg.sender.id === serviceUserId.value ? msg.receiver : msg.sender,
      last_message: { content: msg.content, message_type: msg.message_type, created_at: msg.created_at },
      unread_count: msg.sender.id === serviceUserId.value ? 0 : 1
    })
  }

  if (selectedUser.value && selectedUser.value.id === peerId) {
    appendMessage(msg)
    await markRead(peerId)
  }
}

const loadMessages = async (userId) => {
  if (!userId) return
  loadingMessages.value = true
  try {
    const res = await adminApi.get('/service/messages', { params: { user_id: userId } })
    serviceUserId.value = res.data?.service_user_id || serviceUserId.value
    messages.value = res.data?.results || []
    await markRead(userId)
  } catch (error) {
    ElMessage.error('加载消息失败')
  } finally {
    loadingMessages.value = false
  }
}

const markRead = async (userId) => {
  if (!userId) return
  try {
    await adminApi.post('/service/messages/read', { user_id: userId })
    await loadConversations()
  } catch {
    // ignore
  }
}

const selectConversation = (user) => {
  selectedUser.value = user
  clearPendingImages()
  loadMessages(user.id)
}

const refreshMessages = () => {
  if (!selectedUser.value) return
  loadMessages(selectedUser.value.id)
}

const sendMessage = async () => {
  if (!selectedUser.value) return
  const hasText = !!messageText.value.trim()
  const hasImage = pendingImageFiles.value.length > 0
  if (!hasText && !hasImage) return
  sending.value = true
  try {
    if (hasText) {
      const payload = {
        type: 'chat_message',
        receiver_id: selectedUser.value.id,
        content: messageText.value.trim(),
        message_type: 'text'
      }

      if (wsRef.value && wsConnected.value) {
        wsRef.value.send(JSON.stringify(payload))
      } else {
        const res = await adminApi.post('/service/messages', {
          user_id: selectedUser.value.id,
          content: messageText.value.trim()
        })
        const newMsg = res.data?.message
        if (newMsg) appendMessage(newMsg)
      }
      messageText.value = ''
    }
    if (hasImage) {
      for (const file of pendingImageFiles.value) {
        await uploadImage(file)
      }
      clearPendingImages()
    }
    await loadConversations()
  } catch (error) {
    ElMessage.error('发送失败')
  } finally {
    sending.value = false
  }
}

const triggerImageUpload = () => {
  if (!imageInputRef.value) return
  imageInputRef.value.value = ''
  imageInputRef.value.click()
}

const handleImageChange = async (event) => {
  const files = Array.from(event.target.files || [])
  if (!files.length || !selectedUser.value) return
  addPendingImages(files)
}

const normalizeImagePath = (value) => {
  if (!value) return ''
  return getImageUrl(value) || value
}

const isDuplicateMessage = (msg) => {
  if (!msg) return true
  const senderId = msg.sender?.id || msg.sender_id
  const receiverId = msg.receiver?.id || msg.receiver_id
  const image = normalizeImagePath(msg.image)
  return messages.value.some((item) => {
    if (item.id && msg.id && item.id === msg.id) return true
    const itemSenderId = item.sender?.id || item.sender_id
    const itemReceiverId = item.receiver?.id || item.receiver_id
    if (itemSenderId !== senderId || itemReceiverId !== receiverId) return false
    if (item.message_type !== msg.message_type) return false
    if (msg.message_type === 'image' && item.image && image) {
      return normalizeImagePath(item.image) === image
    }
    return false
  })
}

const appendMessage = (msg) => {
  if (!msg || isDuplicateMessage(msg)) return
  messages.value.push(msg)
}

const clearPendingImages = () => {
  pendingImageUrls.value.forEach((url) => {
    URL.revokeObjectURL(url)
  })
  pendingImageUrls.value = []
  pendingImageFiles.value = []
}

const addPendingImages = (files) => {
  if (!files || files.length === 0) return
  const nextFiles = [...pendingImageFiles.value]
  const nextUrls = [...pendingImageUrls.value]
  for (const file of files) {
    if (!file || !file.type?.startsWith('image/')) {
      ElMessage.error('请选择图片文件')
      continue
    }
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过5MB')
      continue
    }
    if (nextFiles.length >= 5) {
      ElMessage.warning('最多支持 5 张图片')
      break
    }
    nextFiles.push(file)
    nextUrls.push(URL.createObjectURL(file))
  }
  pendingImageFiles.value = nextFiles
  pendingImageUrls.value = nextUrls
}

const removePendingImage = (index) => {
  if (index < 0 || index >= pendingImageFiles.value.length) return
  const url = pendingImageUrls.value[index]
  if (url) URL.revokeObjectURL(url)
  pendingImageFiles.value.splice(index, 1)
  pendingImageUrls.value.splice(index, 1)
}

const uploadImage = async (file) => {
  if (!selectedUser.value) {
    ElMessage.warning('请先选择用户')
    return
  }
  if (!file || !file.type?.startsWith('image/')) return
  if (file.size > 5 * 1024 * 1024) return
  const formData = new FormData()
  formData.append('image', file)
  formData.append('user_id', selectedUser.value.id)
  try {
    const res = await adminApi.post('/service/messages/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const msg = res.data?.message
    if (msg) appendMessage(msg)
    await loadConversations()
  } catch (error) {
    ElMessage.error('发送图片失败')
  }
}

const handlePasteImage = async (event) => {
  if (!selectedUser.value) return
  const items = event.clipboardData?.items || []
  const imageFiles = []
  for (const item of items) {
    if (item.kind === 'file' && item.type?.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) imageFiles.push(file)
    }
  }
  if (imageFiles.length === 0) return
  event.preventDefault()
  addPendingImages(imageFiles)
}

const openOrderDrawer = async () => {
  orderDrawerVisible.value = true
  await loadOrderItems()
}

const loadOrderItems = async () => {
  orderLoading.value = true
  try {
    const res = await adminApi.get('/service/order-items', {
      params: {
        type: orderType.value,
        keyword: orderKeyword.value,
        page_size: 50
      }
    })
    orderItems.value = res.data?.results || []
  } catch (error) {
    ElMessage.error('加载订单商品失败')
  } finally {
    orderLoading.value = false
  }
}

const sendProduct = async (item) => {
  if (!selectedUser.value) return
  try {
    const res = await adminApi.post('/service/messages/product', {
      user_id: selectedUser.value.id,
      item_type: item.type || orderType.value,
      item_id: item.id
    })
    const msg = res.data?.message
    if (msg) appendMessage(msg)
    orderDrawerVisible.value = false
    await loadConversations()
  } catch (error) {
    ElMessage.error('发送商品失败')
  }
}

const handleMessageProductClick = (msg) => {
  const payload = msg?.payload || {}
  if (payload.type === 'secondhand' && payload.order_id) {
    router.push({ path: '/admin/secondhand-orders', query: { order_id: payload.order_id } })
    return
  }
  if (payload.type === 'verified' && payload.order_id) {
    router.push({ path: '/admin/verified-orders', query: { order_id: payload.order_id } })
    return
  }
  if (payload.type === 'recycle' && (payload.recycle_order_id || payload.order_id)) {
    router.push({
      path: '/admin/recycle-orders',
      query: { order_id: payload.recycle_order_id || payload.order_id }
    })
  }
}

const formatTime = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadConversations()
  connectWs()
  const updatePreviewState = () => {
    isPreviewing.value = !!document.querySelector('.el-image-viewer__wrapper')
  }
  updatePreviewState()
  previewObserver = new MutationObserver(updatePreviewState)
  previewObserver.observe(document.body, { childList: true, subtree: true })
})

onUnmounted(() => {
  if (wsRef.value) {
    wsRef.value.close()
    wsRef.value = null
  }
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  if (previewObserver) {
    previewObserver.disconnect()
    previewObserver = null
  }
})
</script>

<style scoped>
.service-chat-page {
  padding: 8px 6px 16px;
  height: calc(100vh - 80px);
  box-sizing: border-box;
  background: linear-gradient(180deg, #f4f6fb 0%, #eef2f7 100%);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.page-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.chat-shell {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 12px;
  height: 100%;
  min-height: 620px;
}

.chat-sidebar,
.chat-panel {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.search-input {
  padding: 12px;
}

.conversation-list {
  padding: 0 12px 12px;
  flex: 1;
  min-height: 0;
}

.conversation-item {
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 8px;
  background: #fafafa;
}

.conversation-item.active,
.conversation-item:hover {
  border-color: #409eff;
  background: #eef6ff;
}

.conversation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  margin-bottom: 4px;
}

.conversation-name {
  color: #303133;
}

.conversation-badge {
  background: #ff4d4f;
  color: #fff;
  font-size: 12px;
  padding: 0 6px;
  border-radius: 10px;
}

.conversation-preview {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #eef0f4;
  background: #f9fbff;
}

.chat-title {
  font-weight: 700;
  color: #303133;
}

.chat-messages {
  flex: 1;
  padding: 12px 16px;
  background: #f3f6fb;
  min-height: 0;
}

.loading-row {
  padding: 20px 0;
}

.message-row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 12px;
}

.message-row.self {
  align-items: flex-end;
}

.message-bubble {
  background: #fff;
  padding: 10px 14px;
  border-radius: 14px;
  max-width: 70%;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-row.self .message-bubble {
  background: linear-gradient(135deg, #409eff 0%, #2563eb 100%);
  color: #fff;
}

.message-bubble.product,
.message-bubble.image {
  background: #fff;
  color: #111827;
  border: 1px solid #e5e7eb;
}

.message-row.self .message-bubble.product,
.message-row.self .message-bubble.image {
  background: #fff;
  color: #111827;
}

.message-product .product-card {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.message-product .product-image {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  object-fit: cover;
  background: #f0f0f0;
}

.message-product .product-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-product .product-title {
  font-weight: 600;
}

.message-product .product-price {
  color: #ff4d4f;
  font-weight: 700;
}

.message-image-img {
  width: 200px;
  height: 140px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.chat-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px 16px 14px;
  border-top: 1px solid #e6ebf2;
  background: #f9fbff;
  position: relative;
  z-index: 1;
}

.send-btn {
  align-self: flex-end;
}

.pending-image-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(86px, 1fr));
  gap: 10px;
  padding: 10px;
  border: 1px dashed #d1d5db;
  border-radius: 10px;
  background: #fff;
}

.pending-image-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.pending-image-item img {
  width: 72px;
  height: 72px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}


.chat-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-actions .el-button {
  border-radius: 10px;
}

.chat-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  background: #fff;
  box-shadow: inset 0 0 0 1px #e6ebf2;
}

.chat-input :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.18);
}

.chat-input :deep(.el-textarea__inner) {
  resize: none;
}

.hidden-input {
  display: none;
}

.drawer-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.drawer-body {
  min-height: 320px;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px;
  border: 1px solid #eef0f4;
  border-radius: 10px;
  background: #fff;
}

.order-cover img {
  width: 56px;
  height: 56px;
  object-fit: cover;
  border-radius: 8px;
  background: #f2f2f2;
}

.order-cover-empty {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  background: #f2f2f2;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #999;
}

.order-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-title {
  font-weight: 600;
}

.order-price {
  color: #ff4d4f;
  font-weight: 700;
}

@media (max-width: 960px) {
  .chat-shell {
    grid-template-columns: 1fr;
  }
}
</style>
