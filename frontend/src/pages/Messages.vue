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
          <el-empty v-if="filteredConversations.length === 0" description="暂无对话" :image-size="100" />
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
              :class="['message-line', { outgoing: msg.sender.id === authStore.user.id }]"
            >
              <el-avatar :icon="UserFilled" :size="38" class="message-avatar" />
              <div class="bubble-wrap">
                <div v-if="msg.sender.id !== authStore.user.id" class="message-sender">{{ msg.sender.username }}</div>
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
                    <div class="product-card">
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
                    v-if="msg.sender.id === authStore.user.id && !msg.recalled"
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

        <div v-if="selectedUser" class="chat-input">
          <div class="input-toolbar">
            <div class="toolbar-left">
              <el-upload
                :action="''"
                :auto-upload="false"
                :on-change="handleImageChange"
                :show-file-list="false"
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
            </div>
            <div class="toolbar-right">
              <el-button type="primary" class="send-btn" @click="handleSendMessage" :loading="loading">
                发送
              </el-button>
            </div>
          </div>
          <el-input
            v-model="messageContent"
            type="textarea"
            :autosize="{ minRows: 3, maxRows: 6 }"
            placeholder="输入消息，按 Enter 发送，支持图片/商品卡片"
            @keyup.enter.native="handleSendMessage"
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
        <div class="recommend-section">
          <div class="goods-header">
            <div>
              <div class="goods-title">TA的宝贝</div>
              <div class="goods-subtitle">常用推荐，快捷发送</div>
            </div>
            <div class="goods-extra">我的收藏</div>
          </div>
          <el-input
            v-model="goodsKeyword"
            :prefix-icon="Search"
            placeholder="搜索TA在售的宝贝"
            size="small"
            clearable
            class="goods-search"
          />
          <div class="goods-list compact">
            <div v-for="item in filteredGoods" :key="item.id" class="goods-card">
              <div class="goods-cover">
                <img :src="item.cover" alt="宝贝图片" />
                <span class="goods-price">¥{{ item.price }}</span>
              </div>
              <div class="goods-info">
                <div class="goods-name">{{ item.title }}</div>
                <div class="goods-desc">{{ item.desc }}</div>
                <div class="goods-actions">
                  <el-button
                    size="small"
                    type="primary"
                    plain
                    :disabled="!selectedUser"
                    @click="handleSendQuickRecommend(item)"
                  >
                    发送
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="drawer-section-title">我的商品</div>
        <div v-if="sellingProducts.length === 0 && !productsLoading" class="empty-products">
          <el-empty description="暂无在售商品" :image-size="100" />
        </div>
        <div v-else class="product-list">
          <div 
            v-for="product in sellingProducts" 
            :key="product.id"
            class="product-item"
            :class="{ 'disabled': product.status !== 'active' }"
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
              <el-tag 
                :type="product.status === 'active' ? 'success' : 'info'" 
                size="small"
                class="product-item-status"
              >
                {{ product.status === 'active' ? '在售' : '下架' }}
              </el-tag>
            </div>
            <div class="product-item-action">
              <el-button 
                type="primary" 
                size="default" 
                @click="handleSendProduct(product)" 
                :disabled="product.status !== 'active'"
              >
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { UserFilled, Position, Picture, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import websocket from '@/utils/websocket'
import { getImageUrl } from '@/utils/image'

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
const conversationKeyword = ref('')
const goodsKeyword = ref('')
const recommendedGoods = ref([
  {
    id: 'g1',
    title: '歌坦代下载不限速',
    price: '0.50',
    desc: '立即代下云盘清音源',
    cover: 'https://placehold.co/120x120/222/fff?text=Q'
  },
  {
    id: 'g2',
    title: 'Google One学生免费认证',
    price: '18.88',
    desc: '极速认证赠送权益',
    cover: 'https://placehold.co/120x120/4f46e5/fff?text=One'
  },
  {
    id: 'g3',
    title: 'Gemini 3Pro 学生认证服务',
    price: '6.88',
    desc: '附送多款AI礼品',
    cover: 'https://placehold.co/120x120/0ea5e9/fff?text=AI'
  },
  {
    id: 'g4',
    title: '拍下自动发货 · Google One',
    price: '9.99',
    desc: '到货快，售后稳',
    cover: 'https://placehold.co/120x120/6366f1/fff?text=GO'
  }
])

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
  if (!goodsKeyword.value.trim()) return recommendedGoods.value
  const key = goodsKeyword.value.trim().toLowerCase()
  return recommendedGoods.value.filter(
    (item) =>
      item.title.toLowerCase().includes(key) ||
      item.desc.toLowerCase().includes(key)
  )
})

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
        image: data.image,
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

const handleSendQuickRecommend = async (item) => {
  if (!selectedUser.value) {
    ElMessage.warning('请先选择对话')
    return
  }
  const content = `${item.title} ¥${item.price} ${item.desc || ''}`.trim()
  try {
    const payload = { receiver_id: selectedUser.value.id, content, message_type: 'text' }
    if (!websocket.send({ ...payload, type: 'chat_message' })) {
      await api.post('/messages/', payload)
      await loadMessages(selectedUser.value.id)
      await loadConversations()
    }
    ElMessage.success('已发送推荐')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送失败')
  }
}

const uploadImageFile = async (file) => {
  if (!selectedUser.value) {
    ElMessage.warning('请先选择对话')
    return
  }

  if (!file || !file.type?.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过5MB')
    return
  }

  loading.value = true
  try {
    const formData = new FormData()
    formData.append('image', file)
    formData.append('receiver_id', selectedUser.value.id)

    const res = await api.post('/messages/upload_image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    messages.value.push({
      id: res.data.id,
      sender: { id: authStore.user.id, username: authStore.user.username },
      receiver: { id: selectedUser.value.id, username: selectedUser.value.username },
      content: '',
      image: res.data.image,
      created_at: res.data.created_at,
      is_read: false,
      message_type: 'image',
      payload: res.data.payload,
      recalled: false
    })

    nextTick(() => {
      scrollToBottom()
    })

    loadConversations()
    ElMessage.success('图片已发送')
    emitUnreadRefresh()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送图片失败')
  } finally {
    loading.value = false
  }
}

const handleImageChange = async (file) => {
  await uploadImageFile(file?.raw)
}

const handlePasteImage = async (event) => {
  const items = event.clipboardData?.items || []
  let imageFile = null
  for (const item of items) {
    if (item.kind === 'file' && item.type?.startsWith('image/')) {
      imageFile = item.getAsFile()
      break
    }
  }
  if (!imageFile) return
  await uploadImageFile(imageFile)
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
  background: #f4f4f4;
  height: 100vh;
  overflow: hidden;
  padding: 24px 32px 32px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
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
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 14px;
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.08);
  padding: 16px 18px;
  overflow: hidden;
  box-sizing: border-box;
}

.sidebar-panel,
.chat-panel,
.goods-panel {
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
}

.message-line.outgoing .product-card {
  background: #e8f8e1;
  border-color: #95ec69;
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
  color: #6b7280;
}

.recall-btn {
  padding: 0;
}

.chat-input {
  border-top: 1px solid #f3f3f3;
  padding: 12px 16px 16px;
  background: #fafafa;
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
  flex-shrink: 0;
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
  min-width: 86px;
}

.chat-empty {
  padding: 24px;
}

.goods-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 10px;
  border-bottom: 1px solid #f3f3f3;
}

.goods-title {
  font-size: 16px;
  font-weight: 700;
  color: #111;
}

.goods-subtitle {
  font-size: 12px;
  color: #888;
}

.goods-extra {
  font-size: 12px;
  color: #3b82f6;
}

.goods-search {
  margin: 10px 0 12px;
}

.goods-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  max-height: 260px;
  padding-right: 4px;
}

.goods-card {
  display: flex;
  gap: 10px;
  padding: 10px;
  border: 1px solid #f3f3f3;
  border-radius: 10px;
  background: #fafafa;
  transition: all 0.2s;
}

.goods-card:hover {
  border-color: #d0e8ff;
  background: #f4f9ff;
  box-shadow: 0 8px 14px rgba(0, 0, 0, 0.05);
}

.goods-cover {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  background: #f2f2f2;
  flex-shrink: 0;
}

.goods-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.goods-price {
  position: absolute;
  left: 6px;
  bottom: 6px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 12px;
}

.goods-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.goods-name {
  font-size: 14px;
  font-weight: 600;
  color: #111;
}

.goods-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

.product-dialog-content {
  min-height: 300px;
}

.recommend-section {
  margin-bottom: 12px;
  border: 1px solid #f3f3f3;
  border-radius: 10px;
  padding: 12px;
  background: #fafafa;
}

.goods-list.compact {
  max-height: 240px;
}

.empty-products {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.product-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
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

.product-item.disabled {
  opacity: 0.6;
  background: #f5f5f5;
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

.product-item-status {
  align-self: flex-start;
}

.product-item-action {
  flex-shrink: 0;
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

.drawer-section-title {
  font-size: 14px;
  font-weight: 700;
  color: #111;
  margin: 4px 0;
}

.goods-actions {
  margin-top: 6px;
}

@media (max-width: 1200px) {
  .chat-shell {
    grid-template-columns: 1fr;
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
