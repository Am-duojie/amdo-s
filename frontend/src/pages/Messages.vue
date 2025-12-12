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
              <h3>与 {{ selectedUser.username }} 的对话</h3>
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
                    <div class="message-text">{{ msg.content }}</div>
                    <div class="message-time">{{ formatTime(msg.created_at) }}</div>
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
                <el-button type="primary" :icon="Position" @click="handleSendMessage" :loading="loading" class="send-btn">
                  发送
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { UserFilled, Position } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
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

onMounted(() => {
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
  }
})

// 组件卸载时断开WebSocket
onUnmounted(() => {
  websocket.disconnect()
})

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
  } else {
    try {
      const res = await api.get(`/users/${userId}/`)
      selectedUser.value = res.data
    } catch (error) {
      ElMessage.error('获取用户信息失败')
    }
  }
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
    if (!websocket.send(messageData)) {
      // WebSocket失败时使用HTTP API
      await api.post('/messages/', messageData)
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
  
  // 如果是当前对话的消息，直接添加到消息列表
  if (selectedUser.value && 
      ((data.sender_id === selectedUser.value.id && data.receiver_id === authStore.user.id) ||
       (data.sender_id === authStore.user.id && data.receiver_id === selectedUser.value.id))) {
    messages.value.push({
      id: data.id,
      sender: { id: data.sender_id, username: data.sender_username },
      receiver: { id: data.receiver_id, username: data.receiver_username },
      content: data.content,
      created_at: data.created_at,
      is_read: data.is_read
    })
  }
  
  // 更新对话列表
  loadConversations()
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

.message-time {
  font-size: 10px;
  margin-top: 4px;
  opacity: 0.6;
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
