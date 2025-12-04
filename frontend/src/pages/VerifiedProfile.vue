<template>
  <div class="verified-profile-page">
    <PageHeader :theme="'blue'" :verifiedMode="true" />
    
    <div class="profile-container">
      <!-- 左侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="user-avatar-large">
            <el-avatar :size="80" :src="authStore.user?.avatar">
              {{ authStore.user?.username?.[0]?.toUpperCase() || '用' }}
            </el-avatar>
          </div>
          <div class="user-name">{{ authStore.user?.username }}</div>
          <div class="user-badge verified-badge">
            <span class="badge-icon">✓</span>
            <span class="badge-text">官方验货用户</span>
          </div>
        </div>

        <div class="sidebar-menu">
          <div 
            class="menu-item" 
            :class="{ active: activeMenu === 'home' }" 
            @click="switchMenu('home')"
          >
            <span class="menu-icon">🏠</span>
            <span class="menu-text">我的官方验</span>
          </div>

          <div 
            class="menu-item" 
            :class="{ active: activeMenu === 'orders' }" 
            @click="switchMenu('orders')"
          >
            <span class="menu-icon">📦</span>
            <span class="menu-text">订单管理</span>
            <span class="menu-badge" v-if="orderStats.total > 0">{{ orderStats.total }}</span>
          </div>

          <div 
            class="menu-item" 
            :class="{ active: activeMenu === 'favorites' }" 
            @click="switchMenu('favorites')"
          >
            <span class="menu-icon">❤️</span>
            <span class="menu-text">我的收藏</span>
            <span class="menu-badge" v-if="favorites.length > 0">{{ favorites.length }}</span>
          </div>

          <div 
            class="menu-item" 
            :class="{ active: activeMenu === 'history' }" 
            @click="switchMenu('history')"
          >
            <span class="menu-icon">👁️</span>
            <span class="menu-text">历史浏览</span>
            <span class="menu-badge" v-if="browseHistory.length > 0">{{ browseHistory.length }}</span>
          </div>

          <div 
            class="menu-item" 
            :class="{ active: activeMenu === 'recycle' }" 
            @click="switchMenu('recycle')"
          >
            <span class="menu-icon">♻️</span>
            <span class="menu-text">回收订单</span>
            <span class="menu-badge" v-if="recycleOrders.length > 0">{{ recycleOrders.length }}</span>
          </div>

          <div 
            class="menu-item" 
            :class="{ active: activeMenu === 'service' }" 
            @click="switchMenu('service')"
          >
            <span class="menu-icon">💬</span>
            <span class="menu-text">联系客服</span>
          </div>

          <div 
            class="menu-item" 
            :class="{ active: activeMenu === 'settings' }" 
            @click="switchMenu('settings')"
          >
            <span class="menu-icon">⚙️</span>
            <span class="menu-text">账户设置</span>
          </div>
        </div>

        <div class="sidebar-footer">
          <div class="back-link" @click="goToMainProfile">
            <span class="link-icon">←</span>
            <span class="link-text">返回易淘主站</span>
          </div>
        </div>
      </aside>

      <!-- 右侧主体内容 -->
      <div class="main-content">
        <!-- 我的官方验首页 -->
        <div class="content-section" v-if="activeMenu === 'home'">
          <div class="section-header">
            <h2 class="section-title">我的官方验</h2>
            <div class="section-stats">
              <div class="stat-card">
                <div class="stat-value">{{ orderStats.total }}</div>
                <div class="stat-label">验货订单</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ favorites.length }}</div>
                <div class="stat-label">收藏商品</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ browseHistory.length }}</div>
                <div class="stat-label">浏览记录</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ recycleOrders.length }}</div>
                <div class="stat-label">回收订单</div>
              </div>
            </div>
          </div>

          <div class="quick-actions">
            <div class="action-card" @click="goToVerifiedProducts">
              <div class="action-icon">🛒</div>
              <div class="action-text">浏览验货商品</div>
            </div>
            <div class="action-card" @click="goToRecycle">
              <div class="action-icon">♻️</div>
              <div class="action-text">设备回收</div>
            </div>
            <div class="action-card" @click="switchMenu('orders')">
              <div class="action-icon">📦</div>
              <div class="action-text">查看订单</div>
            </div>
            <div class="action-card" @click="switchMenu('service')">
              <div class="action-icon">💬</div>
              <div class="action-text">联系客服</div>
            </div>
          </div>

          <div class="recent-section">
            <h3 class="recent-title">最近订单</h3>
            <div class="recent-orders" v-if="recentOrders.length > 0">
              <div 
                v-for="order in recentOrders.slice(0, 5)" 
                :key="order.id"
                class="recent-order-item"
                @click="goToOrderDetail(order.id)"
              >
                <img 
                  :src="order.product?.images?.length ? getImageUrl(order.product.images[0].image) : defaultImage"
                  class="order-image"
                />
                <div class="order-info">
                  <div class="order-title">{{ order.product?.title }}</div>
                  <div class="order-meta">
                    <span class="order-status" :class="getStatusClass(order.status)">
                      {{ getStatusText(order.status) }}
                    </span>
                    <span class="order-price">¥{{ order.total_price }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-recent">
              <div class="empty-text">暂无最近订单</div>
              <button class="empty-btn" @click="goToVerifiedProducts">去逛逛</button>
            </div>
          </div>
        </div>

        <!-- 订单管理 -->
        <div class="content-section" v-if="activeMenu === 'orders'">
          <div class="section-header">
            <h2 class="section-title">订单管理</h2>
          </div>

          <!-- 状态筛选标签 -->
          <div class="order-status-tabs">
            <div 
              v-for="tab in orderStatusTabs" 
              :key="tab.value"
              class="status-tab"
              :class="{ active: currentOrderStatus === tab.value }"
              @click="filterOrdersByStatus(tab.value)"
            >
              {{ tab.label }}
            </div>
          </div>

          <!-- 订单列表 -->
          <div class="orders-list" v-loading="loading">
            <div v-if="filteredOrders.length === 0" class="empty-state">
              <div class="empty-icon">📦</div>
              <div class="empty-text">暂无订单</div>
              <button class="empty-btn" @click="goToVerifiedProducts">去逛逛</button>
            </div>
            <div v-else>
              <div 
                v-for="order in filteredOrders" 
                :key="order.id"
                class="order-card"
              >
                <!-- 订单头部 -->
                <div class="order-header">
                  <div class="order-info-left">
                    <span class="order-id">订单号：{{ order.id }}</span>
                    <span class="order-time">{{ formatDate(order.created_at) }}</span>
                  </div>
                  <div class="order-status-text" :class="getStatusClass(order.status)">
                    {{ getStatusText(order.status) }}
                  </div>
                </div>

                <!-- 订单内容 -->
                <div class="order-body" @click="goToOrderDetail(order.id)">
                  <!-- 卖家信息 -->
                  <div class="seller-info-row">
                    <div class="seller-left">
                      <el-avatar :size="32" :src="order.product?.seller?.avatar">
                        {{ order.product?.seller?.username?.[0]?.toUpperCase() || 'X' }}
                      </el-avatar>
                      <span class="seller-name">{{ order.product?.seller?.username || '匿名用户' }}</span>
                      <el-tag type="warning" size="small">卖家</el-tag>
                    </div>
                    <div class="order-status-badge-top" :class="getStatusClass(order.status)">
                      {{ getStatusBadgeText(order.status) }}
                    </div>
                  </div>

                  <!-- 商品信息 -->
                  <div class="product-row">
                    <img 
                      :src="order.product?.images?.length ? getImageUrl(order.product.images[0].image) : defaultImage"
                      class="product-image"
                    />
                    <div class="product-details">
                      <div class="product-description">
                        {{ order.product?.title || '商品已下架' }}
                      </div>
                      <div class="product-title-collapsed" v-if="order.product?.description">
                        【商品标题】{{ order.product.description.slice(0, 50) }}...
                      </div>
                      <div class="product-price-row">
                        <span class="price-label">¥</span>
                        <span class="price-value">{{ order.total_price }}</span>
                      </div>
                    </div>
                    <el-button class="more-btn" size="small" plain>更多</el-button>
                  </div>
                </div>

                <!-- 订单底部 -->
                <div class="order-footer">
                  <div class="order-date">{{ formatDate(order.created_at) }}</div>
                  <div class="order-actions">
                    <el-button 
                      size="small" 
                      plain
                      @click.stop="handleContactSeller(order)"
                    >
                      联系卖家
                    </el-button>
                    <el-button 
                      v-if="order.status === 'pending'" 
                      type="warning" 
                      size="small"
                      @click.stop="handlePay(order)"
                    >
                      立即付款
                    </el-button>
                    <el-button 
                      v-if="order.status === 'shipped'" 
                      type="success" 
                      size="small"
                      @click.stop="handleConfirmReceive(order)"
                    >
                      确认收货
                    </el-button>
                    <el-button 
                      size="small" 
                      plain
                      @click.stop="goToOrderDetail(order.id)"
                    >
                      查看详情
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 我的收藏 -->
        <div class="content-section" v-if="activeMenu === 'favorites'">
          <div class="section-header">
            <h2 class="section-title">我的收藏</h2>
            <span class="section-count">共 {{ favorites.length }} 件</span>
          </div>
          <div class="favorites-grid" v-loading="loading">
            <div v-if="favorites.length === 0" class="empty-state">
              <div class="empty-icon">❤️</div>
              <div class="empty-text">暂无收藏</div>
              <button class="empty-btn" @click="goToVerifiedProducts">去逛逛</button>
            </div>
            <div v-else class="products-grid">
              <div 
                v-for="fav in favorites" 
                :key="fav.id"
                class="product-card"
                @click="goToProductDetail(fav.product?.id)"
              >
                <div class="product-image-wrapper">
                  <img 
                    :src="fav.product?.images?.length ? getImageUrl(fav.product.images[0].image) : defaultImage"
                    class="product-image"
                  />
                  <div class="verified-badge">✓ 官方验机</div>
                  <div class="favorite-btn" @click.stop="removeFavorite(fav)">
                    <span class="favorite-icon">❤️</span>
                  </div>
                </div>
                <div class="product-info">
                  <div class="product-title">{{ fav.product?.title }}</div>
                  <div class="product-price">¥{{ fav.product?.price }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 历史浏览 -->
        <div class="content-section" v-if="activeMenu === 'history'">
          <div class="section-header">
            <h2 class="section-title">历史浏览</h2>
            <div class="header-actions">
              <span class="section-count">共 {{ browseHistory.length }} 条记录</span>
              <el-button 
                v-if="browseHistory.length > 0" 
                size="small" 
                text
                @click="clearBrowseHistory"
              >
                清空历史
              </el-button>
            </div>
          </div>
          <div class="history-list" v-loading="loading">
            <div v-if="browseHistory.length === 0" class="empty-state">
              <div class="empty-icon">👁️</div>
              <div class="empty-text">暂无浏览记录</div>
              <button class="empty-btn" @click="goToVerifiedProducts">去逛逛</button>
            </div>
            <div v-else>
              <div 
                v-for="(item, index) in browseHistory" 
                :key="index"
                class="history-item"
                @click="goToProductDetail(item.productId)"
              >
                <img 
                  :src="item.image || defaultImage"
                  class="history-image"
                />
                <div class="history-info">
                  <div class="history-title">{{ item.title }}</div>
                  <div class="history-meta">
                    <span class="history-price">¥{{ item.price }}</span>
                    <span class="history-time">{{ formatBrowseTime(item.timestamp) }}</span>
                  </div>
                </div>
                <el-button 
                  class="history-remove"
                  size="small" 
                  text
                  @click.stop="removeHistoryItem(index)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 回收订单 -->
        <div class="content-section" v-if="activeMenu === 'recycle'">
          <div class="section-header">
            <h2 class="section-title">回收订单</h2>
            <el-button type="primary" @click="goToRecycle">创建回收订单</el-button>
          </div>
          <div class="recycle-orders-list" v-loading="loading">
            <div v-if="recycleOrders.length === 0" class="empty-state">
              <div class="empty-icon">♻️</div>
              <div class="empty-text">暂无回收订单</div>
              <button class="empty-btn" @click="goToRecycle">创建回收订单</button>
            </div>
            <div v-else>
              <div 
                v-for="order in recycleOrders" 
                :key="order.id"
                class="recycle-order-card"
              >
                <div class="recycle-header">
                  <div class="recycle-info">
                    <span class="recycle-id">回收单号：{{ order.id }}</span>
                    <span class="recycle-device">{{ order.brand }} {{ order.model }}</span>
                  </div>
                  <div class="recycle-status" :class="getRecycleStatusClass(order.status)">
                    {{ getRecycleStatusText(order.status) }}
                  </div>
                </div>
                <div class="recycle-body">
                  <div class="recycle-details">
                    <div class="detail-item">
                      <span class="detail-label">设备类型：</span>
                      <span class="detail-value">{{ order.device_type }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">存储容量：</span>
                      <span class="detail-value">{{ order.storage || '未指定' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">成色：</span>
                      <span class="detail-value">{{ getConditionText(order.condition) }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">预估价格：</span>
                      <span class="detail-value price">¥{{ order.estimated_price || '待评估' }}</span>
                    </div>
                  </div>
                </div>
                <div class="recycle-footer">
                  <div class="recycle-time">{{ formatDate(order.created_at) }}</div>
                  <div class="recycle-actions">
                    <el-button size="small" plain @click="viewRecycleDetail(order.id)">
                      查看详情
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 联系客服 -->
        <div class="content-section" v-if="activeMenu === 'service'">
          <div class="section-header">
            <h2 class="section-title">联系客服</h2>
          </div>
          <div class="service-content">
            <div class="service-intro">
              <div class="intro-icon">💬</div>
              <div class="intro-text">
                <h3>官方验货客服</h3>
                <p>专业客服团队，7×24小时在线服务</p>
              </div>
            </div>

            <div class="service-methods">
              <div class="method-card" @click="openOnlineChat">
                <div class="method-icon">💬</div>
                <div class="method-title">在线客服</div>
                <div class="method-desc">即时沟通，快速响应</div>
                <div class="method-status">在线</div>
              </div>
              <div class="method-card" @click="openPhoneService">
                <div class="method-icon">📞</div>
                <div class="method-title">电话客服</div>
                <div class="method-desc">400-888-8888</div>
                <div class="method-time">9:00-21:00</div>
              </div>
              <div class="method-card" @click="openEmailService">
                <div class="method-icon">📧</div>
                <div class="method-title">邮件咨询</div>
                <div class="method-desc">service@verified.com</div>
                <div class="method-time">24小时内回复</div>
              </div>
            </div>

            <div class="service-faq">
              <h3 class="faq-title">常见问题</h3>
              <div class="faq-list">
                <div 
                  v-for="(faq, index) in faqList" 
                  :key="index"
                  class="faq-item"
                  @click="toggleFaq(index)"
                >
                  <div class="faq-question">
                    <span>{{ faq.question }}</span>
                    <span class="faq-arrow" :class="{ expanded: faq.expanded }">▼</span>
                  </div>
                  <div class="faq-answer" v-show="faq.expanded">
                    {{ faq.answer }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 账户设置 -->
        <div class="content-section" v-if="activeMenu === 'settings'">
          <div class="section-header">
            <h2 class="section-title">账户设置</h2>
          </div>
          <div class="settings-list">
            <div class="setting-item">
              <div class="setting-label">个人资料</div>
              <el-button text @click="goToMainProfile">前往易淘主站设置</el-button>
            </div>
            <div class="setting-item">
              <div class="setting-label">收货地址</div>
              <el-button text @click="goToMainProfile">前往易淘主站设置</el-button>
            </div>
            <div class="setting-item">
              <div class="setting-label">账号安全</div>
              <el-button text @click="goToMainProfile">前往易淘主站设置</el-button>
            </div>
            <div class="setting-item">
              <div class="setting-label">通知设置</div>
              <el-switch v-model="notificationSettings.order" />
            </div>
            <div class="setting-item">
              <div class="setting-label">订单通知</div>
              <el-switch v-model="notificationSettings.message" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = ref('home')
const loading = ref(false)
const currentOrderStatus = ref('all')
const orders = ref([])
const favorites = ref([])
const recycleOrders = ref([])
const browseHistory = ref([])
const notificationSettings = ref({
  order: true,
  message: true
})

const defaultImage = 'https://via.placeholder.com/200x200?text=No+Image'

const orderStatusTabs = [
  { label: '全部', value: 'all' },
  { label: '待付款', value: 'pending' },
  { label: '待发货', value: 'paid' },
  { label: '待收货', value: 'shipped' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' },
]

const faqList = ref([
  {
    question: '什么是官方验货？',
    answer: '官方验货是指我们平台对商品进行专业质检，确保商品成色、功能、真伪都符合描述。官方验货商品都有"✓ 官方验机"标识，品质有保障。',
    expanded: false
  },
  {
    question: '官方验货商品支持哪些成色？',
    answer: '官方验货商品仅包括全新、99成新、95成新三种成色，确保商品品质优良。',
    expanded: false
  },
  {
    question: '如何申请退款？',
    answer: '在订单详情页面可以申请退款，客服会在24小时内处理您的申请。',
    expanded: false
  },
  {
    question: '订单发货后多久能收到？',
    answer: '一般3-7个工作日可以收到，具体时间取决于您的收货地址。',
    expanded: false
  },
])

const orderStats = computed(() => {
  return {
    total: orders.value.length,
    pending: orders.value.filter(o => o.status === 'pending').length,
    paid: orders.value.filter(o => o.status === 'paid').length,
    shipped: orders.value.filter(o => o.status === 'shipped').length,
    completed: orders.value.filter(o => o.status === 'completed').length,
  }
})

const filteredOrders = computed(() => {
  if (currentOrderStatus.value === 'all') {
    return orders.value
  }
  return orders.value.filter(order => order.status === currentOrderStatus.value)
})

const recentOrders = computed(() => {
  return orders.value.slice().sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const getConditionText = (condition) => {
  const map = {
    'new': '全新',
    'like_new': '99成新',
    'good': '95成新',
    'fair': '9成新',
    'poor': '8成新',
  }
  return map[condition] || '未知'
}

const getStatusText = (status) => {
  const map = {
    'pending': '待付款',
    'paid': '待发货',
    'shipped': '待收货',
    'completed': '已完成',
    'cancelled': '已取消',
  }
  return map[status] || status
}

const getStatusBadgeText = (status) => {
  const map = {
    'pending': '等待买家付款',
    'paid': '等待卖家发货',
    'shipped': '等待买家收货',
    'completed': '交易已完成',
    'cancelled': '订单已取消',
  }
  return map[status] || status
}

const getStatusClass = (status) => {
  const map = {
    'pending': 'status-warning',
    'paid': 'status-info',
    'shipped': 'status-primary',
    'completed': 'status-success',
    'cancelled': 'status-danger',
  }
  return map[status] || ''
}

const getRecycleStatusText = (status) => {
  const map = {
    'pending': '待处理',
    'quoted': '已报价',
    'accepted': '已接受',
    'shipped': '已寄出',
    'completed': '已完成',
    'cancelled': '已取消',
  }
  return map[status] || status
}

const getRecycleStatusClass = (status) => {
  const map = {
    'pending': 'status-warning',
    'quoted': 'status-info',
    'accepted': 'status-primary',
    'shipped': 'status-primary',
    'completed': 'status-success',
    'cancelled': 'status-danger',
  }
  return map[status] || ''
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
}

const formatBrowseTime = (timestamp) => {
  if (!timestamp) return ''
  const now = Date.now()
  const diff = now - timestamp
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  const d = new Date(timestamp)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

const switchMenu = (menu) => {
  activeMenu.value = menu
  currentOrderStatus.value = 'all'
  loadContent(menu)
}

const filterOrdersByStatus = (status) => {
  currentOrderStatus.value = status
}

const loadContent = async (menu) => {
  loading.value = true
  try {
    switch(menu) {
      case 'orders':
        await loadOrders()
        break
      case 'favorites':
        await loadFavorites()
        break
      case 'history':
        loadBrowseHistory()
        break
      case 'recycle':
        await loadRecycleOrders()
        break
      case 'home':
        await Promise.all([loadOrders(), loadFavorites(), loadRecycleOrders()])
        loadBrowseHistory()
        break
    }
  } finally {
    loading.value = false
  }
}

const loadOrders = async () => {
  try {
    // 使用官方验货订单API
    const res = await api.get('/verified-orders/')
    // 后端已经只返回当前用户的官方验货订单
    orders.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载订单失败:', error)
    ElMessage.error('加载订单失败')
    orders.value = []
  }
}

const loadFavorites = async () => {
  try {
    // 使用官方验货收藏API
    const res = await api.get('/verified-favorites/')
    favorites.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载收藏失败:', error)
  }
}

const loadBrowseHistory = () => {
  // 从localStorage加载浏览历史
  const historyKey = `browse_history_${authStore.user?.id}`
  const stored = localStorage.getItem(historyKey)
  if (stored) {
    try {
      browseHistory.value = JSON.parse(stored).filter(item => {
        // 只显示官方验货商品的浏览记录
        return item.condition && ['new', 'like_new', 'good'].includes(item.condition)
      })
    } catch (e) {
      console.error('加载浏览历史失败:', e)
      browseHistory.value = []
    }
  } else {
    browseHistory.value = []
  }
}

const saveBrowseHistory = () => {
  const historyKey = `browse_history_${authStore.user?.id}`
  localStorage.setItem(historyKey, JSON.stringify(browseHistory.value))
}

const addToBrowseHistory = (product) => {
  if (!authStore.user || !product) return
  
  const historyItem = {
    productId: product.id,
    title: product.title,
    price: product.price,
    image: product.images?.length ? getImageUrl(product.images[0].image) : defaultImage,
    condition: product.condition,
    timestamp: Date.now()
  }
  
  // 移除重复项
  browseHistory.value = browseHistory.value.filter(item => item.productId !== product.id)
  // 添加到开头
  browseHistory.value.unshift(historyItem)
  // 最多保存50条
  if (browseHistory.value.length > 50) {
    browseHistory.value = browseHistory.value.slice(0, 50)
  }
  
  saveBrowseHistory()
}

const removeHistoryItem = (index) => {
  browseHistory.value.splice(index, 1)
  saveBrowseHistory()
  ElMessage.success('已删除')
}

const clearBrowseHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有浏览历史吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    browseHistory.value = []
    saveBrowseHistory()
    ElMessage.success('已清空')
  } catch {
    // 取消
  }
}

const loadRecycleOrders = async () => {
  try {
    const res = await api.get('/recycle-orders/')
    recycleOrders.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载回收订单失败:', error)
  }
}

const handlePay = (order) => {
  // TODO: 创建官方验货订单的支付页面
  ElMessage.info('支付功能开发中...')
}

const handleConfirmReceive = async (order) => {
  try {
    await api.patch(`/verified-orders/${order.id}/`, { status: 'completed' })
    ElMessage.success('确认收货成功')
    await loadOrders()
  } catch (error) {
    ElMessage.error('确认收货失败')
  }
}

const handleContactSeller = (order) => {
  const sellerId = typeof order.product?.seller === 'object' ? order.product.seller.id : order.product?.seller
  router.push(`/messages?user_id=${sellerId}&product_id=${order.product?.id}`)
}

const removeFavorite = async (fav) => {
  try {
    await api.delete(`/verified-favorites/${fav.id}/`)
    favorites.value = favorites.value.filter(f => f.id !== fav.id)
    ElMessage.success('已取消收藏')
  } catch (error) {
    ElMessage.error('取消收藏失败')
  }
}

const toggleFaq = (index) => {
  faqList.value[index].expanded = !faqList.value[index].expanded
}

const openOnlineChat = () => {
  ElMessage.info('在线客服功能开发中...')
  // TODO: 打开在线客服窗口
}

const openPhoneService = () => {
  ElMessage.info('客服电话：400-888-8888')
  // TODO: 拨打电话
}

const openEmailService = () => {
  window.location.href = 'mailto:service@verified.com'
}

const goToOrderDetail = (id) => {
  router.push(`/verified-order/${id}`)
}

const goToProductDetail = (id) => {
  if (id) {
    router.push(`/products/${id}`)
  }
}

const goToVerifiedProducts = () => {
  router.push('/verified-products')
}

const goToRecycle = () => {
  router.push('/recycle')
}

const goToMainProfile = () => {
  router.push('/profile')
}

const viewRecycleDetail = (id) => {
  router.push(`/recycle-order/${id}`)
}

// 监听路由参数，设置默认菜单
watch(() => route.query.menu, (val) => {
  if (val && ['home', 'orders', 'favorites', 'history', 'recycle', 'service', 'settings'].includes(val)) {
    activeMenu.value = val
    loadContent(val)
  }
}, { immediate: true })

onMounted(() => {
  // 如果路由中有menu参数，使用它；否则默认显示home
  const menuFromRoute = route.query.menu
  if (menuFromRoute && ['home', 'orders', 'favorites', 'history', 'recycle', 'service', 'settings'].includes(menuFromRoute)) {
    activeMenu.value = menuFromRoute
    loadContent(menuFromRoute)
  } else {
    loadContent('home')
  }
  
  // 监听商品浏览，添加到历史记录
  // 这个可以通过全局事件总线或路由守卫来实现
})
</script>

<style scoped>
.verified-profile-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f9ff 0%, #f5f5f5 100%);
}

.profile-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  gap: 20px;
}

/* 左侧边栏 */
.sidebar {
  width: 260px;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: fit-content;
  position: sticky;
  top: 100px;
}

.sidebar-header {
  text-align: center;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 24px;
}

.user-avatar-large {
  margin-bottom: 12px;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.verified-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.badge-icon {
  font-size: 14px;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: #666;
  position: relative;
}

.menu-item:hover {
  background: #f0f9ff;
  color: #1890ff;
}

.menu-item.active {
  background: linear-gradient(135deg, #e6f7ff, #bae7ff);
  color: #1890ff;
  font-weight: 600;
}

.menu-icon {
  font-size: 20px;
}

.menu-text {
  flex: 1;
  font-size: 14px;
}

.menu-badge {
  background: #ff4d4f;
  color: #fff;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.sidebar-footer {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.back-link:hover {
  background: #f5f5f5;
  color: #1890ff;
}

.link-icon {
  font-size: 16px;
}

/* 右侧主体内容 */
.main-content {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.content-section {
  min-height: 400px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.section-count {
  font-size: 14px;
  color: #999;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.section-stats {
  display: flex;
  gap: 16px;
}

.stat-card {
  text-align: center;
  padding: 16px 24px;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #bae7ff;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1890ff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

/* 快捷操作 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.action-card {
  padding: 24px;
  background: linear-gradient(135deg, #e6f7ff, #bae7ff);
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #91d5ff;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.2);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.action-text {
  font-size: 14px;
  color: #1890ff;
  font-weight: 600;
}

/* 最近订单 */
.recent-section {
  margin-top: 32px;
}

.recent-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.recent-orders {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-order-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.recent-order-item:hover {
  border-color: #1890ff;
  background: #f0f9ff;
}

.order-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
}

.order-info {
  flex: 1;
}

.order-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.order-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.order-price {
  font-size: 14px;
  font-weight: 600;
  color: #ff4d4f;
}

.empty-recent {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* 订单状态标签 */
.order-status-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
  flex-wrap: wrap;
}

.status-tab {
  padding: 8px 20px;
  border: none;
  background: transparent;
  border-bottom: 2px solid transparent;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.status-tab:hover {
  color: #1890ff;
}

.status-tab.active {
  color: #333;
  font-weight: 600;
  border-bottom-color: #333;
}

/* 订单列表 */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-card {
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
  background: #fff;
}

.order-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.order-info-left {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #666;
}

.order-status-text {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-warning {
  background: #fff7e6;
  color: #fa8c16;
}

.status-info {
  background: #e6f7ff;
  color: #1890ff;
}

.status-primary {
  background: #e6f7ff;
  color: #1890ff;
}

.status-success {
  background: #f6ffed;
  color: #52c41a;
}

.status-danger {
  background: #fff1f0;
  color: #ff4d4f;
}

.order-body {
  padding: 16px;
  cursor: pointer;
}

.seller-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.seller-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.seller-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.order-status-badge-top {
  font-size: 13px;
  color: #fa8c16;
  font-weight: 600;
}

.product-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.product-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.product-details {
  flex: 1;
  min-width: 0;
}

.product-description {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-title-collapsed {
  font-size: 12px;
  color: #999;
  margin-bottom: 12px;
}

.product-price-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.price-label {
  font-size: 14px;
  color: #ff4d4f;
  font-weight: 600;
}

.price-value {
  font-size: 20px;
  font-weight: 700;
  color: #ff4d4f;
}

.more-btn {
  flex-shrink: 0;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
}

.order-date {
  font-size: 13px;
  color: #999;
}

.order-actions {
  display: flex;
  gap: 8px;
}

/* 收藏网格 */
.favorites-grid {
  min-height: 200px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.product-card {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.product-card:hover {
  border-color: #1890ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.1);
}

.product-image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 100%;
  background: #f5f5f5;
  overflow: hidden;
}

.product-image-wrapper .product-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-image-wrapper .verified-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: #1890ff;
  color: #fff;
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.favorite-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.favorite-btn:hover {
  background: #fff;
  transform: scale(1.1);
}

.favorite-icon {
  font-size: 18px;
}

.product-info {
  padding: 12px;
}

.product-title {
  font-size: 13px;
  color: #333;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-price {
  font-size: 16px;
  font-weight: 700;
  color: #ff4d4f;
}

/* 历史浏览 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: #1890ff;
  background: #f0f9ff;
}

.history-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.history-price {
  font-size: 16px;
  font-weight: 700;
  color: #ff4d4f;
}

.history-time {
  font-size: 12px;
  color: #999;
}

.history-remove {
  flex-shrink: 0;
}

/* 回收订单 */
.recycle-orders-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recycle-order-card {
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  overflow: hidden;
}

.recycle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
}

.recycle-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recycle-id {
  font-size: 12px;
  color: #999;
}

.recycle-device {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.recycle-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.recycle-body {
  padding: 16px;
}

.recycle-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  display: flex;
  gap: 8px;
}

.detail-label {
  font-size: 13px;
  color: #666;
}

.detail-value {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.detail-value.price {
  color: #ff4d4f;
  font-weight: 700;
}

.recycle-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
}

.recycle-time {
  font-size: 12px;
  color: #999;
}

/* 联系客服 */
.service-content {
  max-width: 800px;
}

.service-intro {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: linear-gradient(135deg, #e6f7ff, #bae7ff);
  border-radius: 12px;
  margin-bottom: 24px;
}

.intro-icon {
  font-size: 48px;
}

.intro-text h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.intro-text p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.service-methods {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.method-card {
  padding: 24px;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.method-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.1);
  transform: translateY(-2px);
}

.method-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.method-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.method-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.method-status {
  font-size: 12px;
  color: #52c41a;
  font-weight: 600;
}

.method-time {
  font-size: 12px;
  color: #999;
}

.service-faq {
  margin-top: 32px;
}

.faq-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.faq-item {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
}

.faq-question:hover {
  background: #f0f9ff;
}

.faq-arrow {
  font-size: 12px;
  color: #999;
  transition: transform 0.2s;
}

.faq-arrow.expanded {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 16px;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  background: #fff;
}

/* 设置列表 */
.settings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
}

.setting-label {
  font-size: 14px;
  color: #333;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 16px;
  color: #666;
  margin-bottom: 24px;
}

.empty-btn {
  padding: 10px 24px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.empty-btn:hover {
  background: #40a9ff;
}

/* 响应式 */
@media (max-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .service-methods {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .profile-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    position: static;
  }
  
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .service-methods {
    grid-template-columns: 1fr;
  }
  
  .recycle-details {
    grid-template-columns: 1fr;
  }
  
  .order-status-tabs {
    overflow-x: auto;
    flex-wrap: nowrap;
  }
  
  .status-tab {
    flex-shrink: 0;
  }
}
</style>
