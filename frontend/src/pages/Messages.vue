<template>
  <div class="messages-page">
    <div class="chat-shell">
      <div class="sidebar-panel">
        <div class="sidebar-header">
          <div class="sidebar-title">消息</div>
          <el-input
            v-model="conversationKeyword"
            :prefix-icon="Search"
            placeholder="搜索联系人或内容"
            clearable
            size="large"
            class="conversation-search"
          />
        </div>

        <el-scrollbar class="conversation-list">
          <el-empty
            v-if="filteredConversations.length === 0"
            description="暂无对话"
            :image-size="100"
          />
          <div
            v-for="item in filteredConversations"
            :key="item.user.id"
            :class="['conversation-item', { active: selectedUser?.id === item.user.id }]"
            @click="handleSelectUser(item.user.id)"
          >
            <div class="conversation-avatar">
              <el-badge :value="item.unread_count" :hidden="!(item.unread_count > 0)">
                <el-avatar :icon="UserFilled" :size="44" />
              </el-badge>
            </div>
            <div class="conversation-meta">
              <div class="conversation-top">
                <span class="conversation-name">{{ item.user.username }}</span>
                <span class="conversation-time">{{ getConversationTime(item) }}</span>
              </div>
              <div class="conversation-bottom">
                <span class="conversation-preview">{{ getConversationPreview(item) }}</span>
                <el-tag
                  v-if="item.unread_count > 0"
                  type="danger"
                  size="small"
                  effect="dark"
                  class="unread-tag"
                >
                  {{ item.unread_count }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>

      <div class="chat-panel">
        <div class="chat-header">
          <div class="chat-peer">
            <el-avatar v-if="selectedUser" :size="40" :icon="UserFilled" />
            <div class="peer-text">
              <div class="peer-name">{{ selectedUser ? selectedUser.username : '请选择一个对话' }}</div>
              <div class="peer-sub" v-if="selectedUser">即时沟通 · {{ wsConnected ? '实时在线' : '稍后重试' }}</div>
            </div>
          </div>
          <div class="chat-status">
            <el-tag :type="wsConnected ? 'success' : 'danger'" size="small" effect="plain">
              {{ wsConnected ? '实时连接正常' : '实时未连接，已走HTTP' }}
            </el-tag>
          </div>
        </div>

        <div v-if="selectedUser" class="chat-body">
          <el-scrollbar ref="scrollbarRef" class="chat-scroll" height="100%">
            <div
              v-for="msg in messages"
              :key="msg.id"
              :class="['message-line', { outgoing: msg.sender?.id === authStore.user.id }]"
            >
              <el-avatar :icon="UserFilled" :size="38" class="message-avatar" />
              <div class="bubble-wrap">
                <div v-if="msg.sender?.id !== authStore.user.id" class="message-sender">
                  {{ msg.sender?.username || '对方' }}
                </div>
                <div
                  class="message-bubble"
                  :class="{
                    recalled: msg.recalled,
                    product: msg.message_type === 'product',
                    image: msg.message_type === 'image'
                  }"
                >
                  <div v-if="msg.recalled" class="message-text recalled">消息已撤回</div>
                  <div v-else-if="msg.message_type === 'product'" class="message-product">
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
                    <div v-else class="message-text">[图片]</div>
                  </div>
                  <div v-else class="message-text">{{ msg.content }}</div>
                </div>
                <div class="message-meta">
                  <span class="message-time">{{ formatTime(msg.created_at) }}</span>
                  <span
                    v-if="msg.sender?.id === authStore.user.id && !msg.recalled"
                    class="read-status"
                  >
                    {{ msg.is_read ? '已读' : '未读' }}
                  </span>
                  <el-button
                    v-if="showRecallButton(msg)"
                    link
                    type="danger"
                    size="small"
                    class="recall-btn"
                    @click="handleRecall(msg)"
                  >
                    撤回
                  </el-button>
                </div>
              </div>
            </div>
          </el-scrollbar>
        </div>
        <el-empty v-else class="chat-empty" description="请选择一个对话" :image-size="120" />

        <div v-if="selectedUser" v-show="!isPreviewing" class="chat-input">
          <div class="input-toolbar">
            <div class="toolbar-left">
              <el-upload
                :action="''"
                :auto-upload="false"
                :on-change="handleImageChange"
                :show-file-list="false"
                multiple
                accept="image/*"
                class="upload-btn-wrapper"
              >
                <el-button text :icon="Picture" class="toolbar-btn">图片</el-button>
              </el-upload>
              <el-button
                text
                :icon="Position"
                class="toolbar-btn"
                @click="openProductDialog"
                :loading="productsLoading"
              >
                发送商品
              </el-button>
              <el-button
                text
                :icon="Tickets"
                class="toolbar-btn"
                @click="openOrderDialog"
              >
                订单商品
              </el-button>
            </div>
            <div class="toolbar-right">
              <el-button type="primary" class="send-btn" @click="handleSendMessage" :loading="loading">
                发送
              </el-button>
            </div>
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
            v-model="messageContent"
            type="textarea"
            :autosize="{ minRows: 3, maxRows: 6 }"
            placeholder="输入消息，按 Enter 发送，支持图片/商品卡片"
            @keyup.enter.exact.prevent="handleSendMessage"
            @paste.prevent="handlePasteImage"
            class="chat-textarea"
          />
        </div>
      </div>
    </div>

    <el-drawer
      v-model="productDialogVisible"
      title="选择要发送的商品"
      size="360px"
      direction="rtl"
      :close-on-click-modal="true"
      class="product-drawer"
    >
        <div v-loading="productsLoading" class="drawer-body">
          <el-tabs v-model="productSource" @tab-change="loadChatProducts">
            <el-tab-pane label="我的商品" name="mine" />
            <el-tab-pane label="对方在售" name="other" />
          </el-tabs>
          <el-input
            v-model="goodsKeyword"
            :prefix-icon="Search"
            placeholder="搜索商品"
            size="small"
            clearable
            class="goods-search"
          />
        <div v-if="filteredGoods.length === 0 && !productsLoading" class="empty-products">
          <el-empty description="暂无在售商品" :image-size="100" />
        </div>
        <div v-else class="product-list">
          <div
            v-for="product in filteredGoods"
            :key="product.id"
            class="product-item"
          >
            <div class="product-item-image">
              <img
                v-if="product.images && product.images.length > 0"
                :src="getImageUrl(product.images[0].image)"
                alt="商品图片"
              />
              <div v-else class="no-image">暂无图片</div>
            </div>
            <div class="product-item-info">
              <div class="product-item-title">{{ product.title }}</div>
              <div class="product-item-price">¥{{ product.price }}</div>
            </div>
            <div class="product-item-action">
              <el-button type="primary" size="default" @click="handleSendProduct(product)">
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="productDialogVisible = false">关闭</el-button>
      </template>
    </el-drawer>

    <el-drawer
      v-model="orderDialogVisible"
      title="选择订单商品"
      size="420px"
      direction="rtl"
      :close-on-click-modal="true"
      class="order-drawer"
    >
      <div class="drawer-body">
        <div class="order-search">
          <el-input
            v-model="orderKeyword"
            placeholder="搜索订单/商品"
            size="small"
            clearable
          />
          <el-button size="small" @click="loadOrderItems">搜索</el-button>
        </div>
        <el-tabs v-model="orderType" @tab-change="loadOrderItems">
          <el-tab-pane label="易淘订单" name="secondhand" />
          <el-tab-pane label="官方验订单" name="verified" />
          <el-tab-pane label="回收订单" name="recycle" />
        </el-tabs>
        <div v-loading="orderLoading" class="order-list">
          <el-empty v-if="!orderLoading && orderItems.length === 0" description="暂无可选订单" />
          <div v-else>
            <div v-for="item in orderItems" :key="`${item.type}-${item.id}`" class="order-item">
              <div class="order-item-image">
                <img v-if="item.cover" :src="getImageUrl(item.cover)" alt="封面" />
                <div v-else class="no-image">暂无图片</div>
              </div>
              <div class="order-item-info">
                <div class="order-item-title">{{ item.title }}</div>
                <div class="order-item-price">¥{{ item.price || '0.00' }}</div>
              </div>
              <div class="order-item-action">
                <el-button type="primary" size="default" @click="handleSendOrderItem(item)">
                  发送
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="orderDialogVisible = false">关闭</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { UserFilled, Position, Picture, Search, Tickets } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import websocket from '@/utils/websocket'
import { getImageUrl } from '@/utils/image'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const conversations = ref([])
const selectedUser = ref(null)
const messages = ref([])
const messageContent = ref('')
const loading = ref(false)
const scrollbarRef = ref(null)
const wsConnected = ref(websocket.isConnected)
const pendingImageFiles = ref([])
const pendingImageUrls = ref([])
const isPreviewing = ref(false)
let previewObserver = null

const productDialogVisible = ref(false)
const productSource = ref('mine')
const sellingProducts = ref([])
const productsLoading = ref(false)
const conversationKeyword = ref('')
const goodsKeyword = ref('')
const orderDialogVisible = ref(false)
const orderType = ref('secondhand')
const orderKeyword = ref('')
const orderItems = ref([])
const orderLoading = ref(false)

const filteredConversations = computed(() => {
  if (!conversationKeyword.value.trim()) return conversations.value
  const key = conversationKeyword.value.trim().toLowerCase()
  return conversations.value.filter((item) => {
    const name = item.user.username?.toLowerCase() || ''
    const preview = getConversationPreview(item).toLowerCase()
    return name.includes(key) || preview.includes(key)
  })
})

const filteredGoods = computed(() => {
  if (!goodsKeyword.value.trim()) return sellingProducts.value
  const key = goodsKeyword.value.trim().toLowerCase()
  return sellingProducts.value.filter(
    (item) => item.title?.toLowerCase().includes(key)
  )
})

const normalizeMessage = (raw) => {
  if (!raw) return null
  if (raw.sender && raw.receiver) {
    return raw
  }
  return {
    id: raw.id,
    sender: { id: raw.sender_id, username: raw.sender_username },
    receiver: { id: raw.receiver_id, username: raw.receiver_username },
    content: raw.content || '',
    created_at: raw.created_at,
    is_read: raw.is_read,
    message_type: raw.message_type || 'text',
    image: raw.image || '',
    payload: raw.payload || {},
    recalled: raw.recalled || false
  }
}

const normalizeImagePath = (value) => {
  if (!value) return ''
  return getImageUrl(value) || value
}

const isDuplicateMessage = (msg) => {
  if (!msg) return true
  const senderId = msg.sender?.id
  const receiverId = msg.receiver?.id
  const image = normalizeImagePath(msg.image)
  return messages.value.some((item) => {
    if (item.id && msg.id && item.id === msg.id) return true
    if (item.sender?.id !== senderId || item.receiver?.id !== receiverId) return false
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

const loadConversations = async () => {
  try {
    const res = await api.get('/messages/conversations/')
    conversations.value = res.data || []
  } catch (error) {
    console.error('加载对话列表失败:', error)
  }
}

const loadMessages = async (userId) => {
  loading.value = true
  try {
    const res = await api.get('/messages/with_user/', { params: { user_id: userId } })
    messages.value = (res.data || []).map(normalizeMessage)
    nextTick(scrollToBottom)
    await markRead(userId)
  } catch (error) {
    console.error('加载消息失败:', error)
  } finally {
    loading.value = false
  }
}

const markRead = async (userId) => {
  if (!userId) return
  try {
    await api.post('/messages/read/', { user_id: userId })
    messages.value = messages.value.map((msg) => {
      if (msg.sender?.id === userId && msg.receiver?.id === authStore.user.id) {
        return { ...msg, is_read: true }
      }
      return msg
    })
    loadConversations()
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

const handleSelectUser = async (userId) => {
  const conversation = conversations.value.find((c) => c.user.id === userId)
  if (conversation) {
    selectedUser.value = conversation.user
  } else {
    try {
      const res = await api.get(`/users/${userId}/`)
      selectedUser.value = res.data
    } catch (error) {
      ElMessage.error('获取用户信息失败')
    }
  }
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

const handleSendMessage = async () => {
  if (!selectedUser.value) return
  const hasText = !!messageContent.value.trim()
  const hasImage = pendingImageFiles.value.length > 0
  if (!hasText && !hasImage) return
  loading.value = true
  try {
    if (hasText) {
      const payload = {
        receiver_id: selectedUser.value.id,
        content: messageContent.value,
        message_type: 'text'
      }
      if (!websocket.send({ ...payload, type: 'chat_message' })) {
        await api.post('/messages/', payload)
        await loadMessages(selectedUser.value.id)
        await loadConversations()
      }
      messageContent.value = ''
    }
    if (hasImage) {
      for (const file of pendingImageFiles.value) {
        await uploadImageFile(file)
      }
      clearPendingImages()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送消息失败')
  } finally {
    loading.value = false
  }
}

const handleSendProduct = async (product) => {
  if (!selectedUser.value) return
  try {
    const payload = {
      receiver_id: selectedUser.value.id,
      product_id: product.id,
      content: '',
      message_type: 'product'
    }
    if (!websocket.send({ ...payload, type: 'chat_message' })) {
      await api.post('/messages/', payload)
      await loadMessages(selectedUser.value.id)
      await loadConversations()
    }
    productDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送商品失败')
  }
}

const handleMessageProductClick = (msg) => {
  const payload = msg?.payload || {}
  if (payload.type === 'secondhand' && payload.order_id) {
    router.push(`/order/${payload.order_id}`)
    return
  }
  if (payload.type === 'verified' && payload.order_id) {
    router.push(`/verified-order/${payload.order_id}`)
    return
  }
  if (payload.type === 'recycle' && (payload.recycle_order_id || payload.order_id)) {
    router.push(`/recycle-order/${payload.recycle_order_id || payload.order_id}`)
    return
  }
  if (payload.product_id) {
    router.push(`/products/${payload.product_id}`)
    return
  }
  if (payload.verified_product_id) {
    router.push(`/verified-products/${payload.verified_product_id}`)
  }
}

const showRecallButton = (msg) => {
  if (!msg || msg.recalled) return false
  if (msg.sender?.id !== authStore.user.id) return false
  const deadlineSource = msg.recallable_until || msg.created_at
  if (!deadlineSource) return false
  const deadline = msg.recallable_until
    ? new Date(msg.recallable_until).getTime()
    : new Date(msg.created_at).getTime() + 2 * 60 * 1000
  return Date.now() <= deadline
}

const handleRecall = async (msg) => {
  try {
    await ElMessageBox.confirm('确认撤回该消息吗？', '撤回消息', {
      type: 'warning',
      confirmButtonText: '撤回',
      cancelButtonText: '取消'
    })
    await api.post(`/messages/${msg.id}/recall/`)
    messages.value = messages.value.map((item) =>
      item.id === msg.id ? { ...item, recalled: true } : item
    )
    loadConversations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '撤回失败')
    }
  }
}

const handleWebSocketMessage = (raw) => {
  const data = normalizeMessage(raw)
  if (raw?.type === 'read_ack') {
    messages.value = messages.value.map((msg) => {
      if (msg.sender?.id === authStore.user.id && msg.receiver?.id === raw.peer_id) {
        return { ...msg, is_read: true }
      }
      return msg
    })
    loadConversations()
    return
  }

  if (raw?.type === 'message_recalled') {
    messages.value = messages.value.map((msg) =>
      msg.id === raw.message_id ? { ...msg, recalled: true } : msg
    )
    loadConversations()
    return
  }

  if (data && selectedUser.value) {
    const peerId = selectedUser.value.id
    const isCurrent =
      (data.sender?.id === peerId && data.receiver?.id === authStore.user.id) ||
      (data.sender?.id === authStore.user.id && data.receiver?.id === peerId)
    if (isCurrent) {
      appendMessage(data)
      nextTick(scrollToBottom)
      if (data.sender?.id === peerId) {
        markRead(peerId)
      }
    }
  }
  loadConversations()
}

const uploadImageFile = async (file) => {
  if (!selectedUser.value) {
    ElMessage.warning('请先选择对话')
    return
  }
  if (!file || !file.type?.startsWith('image/')) return
  if (file.size > 5 * 1024 * 1024) return
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('image', file)
    formData.append('receiver_id', selectedUser.value.id)
    const res = await api.post('/messages/upload_image/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    appendMessage(normalizeMessage(res.data))
    nextTick(scrollToBottom)
    loadConversations()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送图片失败')
  } finally {
    loading.value = false
  }
}

const handleImageChange = async (file) => {
  if (!selectedUser.value) {
    ElMessage.warning('请先选择对话')
    return
  }
  addPendingImages([file?.raw].filter(Boolean))
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

const getConversationPreview = (item) => {
  if (!item?.last_message) return '没有更多消息'
  if (item.last_message.recalled) return '对方撤回了一条消息'
  if (item.last_message.message_type === 'image') return '[图片]'
  if (item.last_message.message_type === 'product') return '[商品卡片]'
  return item.last_message.content || '...'
}

const getConversationTime = (item) => {
  const time = item?.last_message?.created_at
  if (!time) return ''
  return formatTime(time)
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

const loadSellingProducts = async () => {
  if (!authStore.user?.id) return
  productsLoading.value = true
  try {
    const res = await api.get('/products/', { params: { seller: authStore.user.id, status: 'active' } })
    sellingProducts.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载商品失败:', error)
    sellingProducts.value = []
  } finally {
    productsLoading.value = false
  }
}

const openProductDialog = async () => {
  productSource.value = 'mine'
  await loadChatProducts()
  productDialogVisible.value = true
}

const loadChatProducts = async () => {
  if (!authStore.user?.id) return
  productsLoading.value = true
  try {
    const sellerId = productSource.value === 'mine'
      ? authStore.user.id
      : selectedUser.value?.id
    if (!sellerId) {
      sellingProducts.value = []
      ElMessage.warning('请先选择对话对象')
      return
    }
    const res = await api.get('/products/', { params: { seller: sellerId, status: 'active' } })
    sellingProducts.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载商品失败:', error)
    sellingProducts.value = []
  } finally {
    productsLoading.value = false
  }
}

const openOrderDialog = async () => {
  orderDialogVisible.value = true
  await loadOrderItems()
}

const buildOrderItem = (type, order) => {
  if (type === 'secondhand') {
    const product = order.product || {}
    const images = product.images || []
    const cover = images.find((img) => img.is_primary)?.image || images[0]?.image || ''
    return {
      id: order.id,
      type,
      title: product.title || `订单#${order.id}`,
      price: product.price || order.total_price,
      cover,
      payload: {
        type,
        order_id: order.id,
        product_id: product.id,
        title: product.title || `订单#${order.id}`,
        price: String(product.price || order.total_price || ''),
        cover
      }
    }
  }

  if (type === 'verified') {
    const product = order.product || {}
    const detailImages = product.detail_images || []
    const cover = product.cover_image || detailImages[0]?.image || detailImages[0] || product.images?.[0]?.image || ''
    return {
      id: order.id,
      type,
      title: product.title || `官方验订单#${order.id}`,
      price: product.price || order.total_price,
      cover,
      payload: {
        type,
        order_id: order.id,
        verified_product_id: product.id,
        title: product.title || `官方验订单#${order.id}`,
        price: String(product.price || order.total_price || ''),
        cover
      }
    }
  }

  const title = `${order.brand || ''} ${order.model || ''}`.trim() || `回收订单#${order.id}`
  const price = order.final_price || order.estimated_price || ''
  return {
    id: order.id,
    type: 'recycle',
    title,
    price,
    cover: '',
    payload: {
      type: 'recycle',
      recycle_order_id: order.id,
      title,
      price: String(price || ''),
      cover: ''
    }
  }
}

const loadOrderItems = async () => {
  if (!authStore.user) return
  orderLoading.value = true
  try {
    let res
    if (orderType.value === 'verified') {
      res = await api.get('/verified-orders/')
    } else if (orderType.value === 'recycle') {
      res = await api.get('/recycle-orders/')
    } else {
      res = await api.get('/orders/')
    }
    const raw = res.data?.results || res.data || []
    const keyword = orderKeyword.value.trim().toLowerCase()
    const items = raw.map((order) => buildOrderItem(orderType.value, order))
    orderItems.value = keyword
      ? items.filter((item) => item.title.toLowerCase().includes(keyword))
      : items
  } catch (error) {
    orderItems.value = []
    ElMessage.error('加载订单失败')
  } finally {
    orderLoading.value = false
  }
}

const handleSendOrderItem = async (item) => {
  if (!selectedUser.value) return
  try {
    const payload = {
      receiver_id: selectedUser.value.id,
      content: '',
      message_type: 'product',
      payload: item.payload
    }
    if (item.type === 'secondhand' && item.payload?.product_id) {
      payload.product_id = item.payload.product_id
    }
    if (!websocket.send({ ...payload, type: 'chat_message' })) {
      await api.post('/messages/', payload)
      await loadMessages(selectedUser.value.id)
      await loadConversations()
    }
    orderDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送订单商品失败')
  }
}

const handleWsConnected = () => {
  wsConnected.value = true
}

const handleWsDisconnected = () => {
  wsConnected.value = false
}

onMounted(() => {
  loadConversations()
  const userId = route.query.user_id
  if (userId) {
    handleSelectUser(parseInt(userId, 10))
  }

  const token = localStorage.getItem('token')
  if (token) {
    websocket.connect(token)
    wsConnected.value = websocket.isConnected
    websocket.on('message', handleWebSocketMessage)
    websocket.on('connected', handleWsConnected)
    websocket.on('disconnected', handleWsDisconnected)
  }

  const updatePreviewState = () => {
    isPreviewing.value = !!document.querySelector('.el-image-viewer__wrapper')
  }
  updatePreviewState()
  previewObserver = new MutationObserver(updatePreviewState)
  previewObserver.observe(document.body, { childList: true, subtree: true })
})

onUnmounted(() => {
  websocket.off('message', handleWebSocketMessage)
  websocket.off('connected', handleWsConnected)
  websocket.off('disconnected', handleWsDisconnected)
  websocket.disconnect()
  if (previewObserver) {
    previewObserver.disconnect()
    previewObserver = null
  }
})

watch(
  () => selectedUser.value?.id,
  (userId) => {
    if (userId) {
      loadMessages(userId)
      clearPendingImages()
      if (productDialogVisible.value && productSource.value === 'other') {
        loadChatProducts()
      }
    }
  }
)

watch(
  () => messages.value.length,
  () => {
    nextTick(scrollToBottom)
  }
)
</script>

<style scoped>
.messages-page {
  background: #f4f4f4;
  min-height: 100vh;
  padding: 24px 32px 32px;
  box-sizing: border-box;
}

.chat-shell {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 12px;
  max-width: 1220px;
  width: 100%;
  height: calc(100vh - 136px);
  min-height: 720px;
  margin: 0 auto;
  padding: 16px 18px;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 14px;
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  box-sizing: border-box;
}

.sidebar-panel,
.chat-panel {
  background: #fff;
  border-radius: 10px;
  box-sizing: border-box;
}

.sidebar-panel {
  padding: 14px;
  border: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.sidebar-header {
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f3f3;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 600;
  color: #111;
  margin-bottom: 10px;
}

.conversation-search {
  width: 100%;
}

.conversation-search :deep(.el-input__wrapper) {
  border-radius: 20px;
  background: #f4f5f7;
  box-shadow: none;
}

.conversation-list {
  margin-top: 12px;
  padding-right: 4px;
  flex: 1;
  min-height: 0;
}

.conversation-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
  border: 1px solid transparent;
  background: #fff;
}

.conversation-item:hover {
  background: #f5f5f5;
}

.conversation-item.active {
  background: #eaf6ff;
  border-color: #8fd1ff;
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.04);
}

.conversation-avatar :deep(.el-badge__content.is-fixed) {
  transform: translate(4px, -8px);
}

.conversation-meta {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.conversation-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.conversation-name {
  font-size: 15px;
  font-weight: 600;
  color: #111;
}

.conversation-time {
  font-size: 12px;
  color: #999;
}

.conversation-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.conversation-preview {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unread-tag {
  margin-left: 6px;
}

.chat-panel {
  border: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.chat-header {
  padding: 14px 16px;
  border-bottom: 1px solid #f3f3f3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fafafa;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.chat-peer {
  display: flex;
  align-items: center;
  gap: 10px;
}

.peer-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.peer-name {
  font-size: 16px;
  font-weight: 600;
  color: #111;
}

.peer-sub {
  font-size: 12px;
  color: #888;
}

.chat-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-body {
  flex: 1;
  min-height: 0;
  padding: 16px;
  overflow: hidden;
}

.chat-scroll {
  flex: 1;
  min-height: 0;
  height: 100%;
  padding-right: 8px;
  overflow-y: auto;
}

.message-line {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  margin-bottom: 18px;
}

.message-line.outgoing {
  flex-direction: row-reverse;
}

.message-avatar {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.bubble-wrap {
  max-width: 72%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.message-sender {
  font-size: 12px;
  margin-bottom: 4px;
  color: #6b7280;
}

.message-bubble {
  background: #f6f6f6;
  padding: 10px 14px;
  border-radius: 10px;
  line-height: 1.6;
  color: #111;
  word-break: break-word;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.message-line.outgoing .message-bubble {
  background: #95ec69;
  color: #0f2a12;
}

.message-bubble.product,
.message-bubble.image {
  background: #fff;
  color: #111827;
  border: 1px solid #e5e7eb;
}

.message-line.outgoing .message-bubble.product,
.message-line.outgoing .message-bubble.image {
  background: #fff;
  color: #111827;
}

.message-bubble.recalled {
  background: #f7f7f7;
  color: #9ca3af;
  font-style: italic;
}

.message-product .product-card {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  cursor: pointer;
}

.message-line.outgoing .product-card {
  background: #fff;
  border-color: #e5e7eb;
}

.product-image {
  width: 56px;
  height: 56px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}

.product-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.product-title {
  font-size: 14px;
  font-weight: 600;
  color: #111;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-price {
  font-size: 15px;
  font-weight: 700;
  color: #ff6a00;
}

.message-image-img {
  max-width: 320px;
  max-height: 320px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  display: block;
}

.message-image-img:hover {
  opacity: 0.95;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #9ca3af;
}

.message-line.outgoing .message-meta {
  justify-content: flex-end;
}

.read-status {
  font-size: 11px;
  color: #6b7280;
}

.recall-btn {
  padding: 0;
}

.chat-empty {
  padding: 24px;
}

.chat-input {
  border-top: 1px solid #f3f3f3;
  padding: 12px 16px 16px;
  background: #fafafa;
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.pending-image-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(86px, 1fr));
  gap: 10px;
  padding: 10px;
  border: 1px dashed #d1d5db;
  border-radius: 10px;
  background: #fff;
  margin-bottom: 10px;
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


.input-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toolbar-btn {
  color: #4b5563;
}

.toolbar-btn:hover {
  color: #111827;
}

.upload-btn-wrapper :deep(.el-upload) {
  display: inline-block;
}

.chat-textarea :deep(.el-textarea__inner) {
  border-radius: 12px;
  background: #fff;
  min-height: 96px;
  line-height: 1.6;
}

.send-btn {
  background: #ff6a00;
  min-width: 86px;
}

.send-btn:hover {
  background: #ff8533;
  border-color: #ff8533;
}

.product-drawer :deep(.el-drawer__body) {
  padding: 0;
}

.drawer-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: calc(100vh - 120px);
  overflow-y: auto;
}

.goods-search {
  margin-bottom: 12px;
}

.empty-products {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 240px;
}

.product-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.product-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s;
}

.product-item:hover {
  border-color: #ff6a00;
  box-shadow: 0 2px 8px rgba(255, 106, 0, 0.1);
}

.product-item-image {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-item-image .no-image {
  color: #999;
  font-size: 12px;
}

.product-item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.product-item-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-item-price {
  font-size: 16px;
  font-weight: 600;
  color: #ff6a00;
}

.product-item-action {
  flex-shrink: 0;
}

.order-drawer :deep(.el-drawer__body) {
  padding: 0;
}

.order-search {
  display: flex;
  gap: 8px;
  align-items: center;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  background: #fff;
  transition: all 0.3s;
}

.order-item:hover {
  border-color: #ff6a00;
  box-shadow: 0 2px 8px rgba(255, 106, 0, 0.1);
}

.order-item-image {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.order-item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.order-item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.order-item-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.order-item-price {
  font-size: 16px;
  font-weight: 600;
  color: #ff6a00;
}

.order-item-action {
  flex-shrink: 0;
}

@media (max-width: 1200px) {
  .chat-shell {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 600px;
  }
}

@media (max-width: 768px) {
  .messages-page {
    padding: 12px;
  }

  .chat-shell {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .chat-scroll {
    height: 420px;
  }
}
</style>
