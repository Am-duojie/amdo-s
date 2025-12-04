<template>
  <div class="product-detail-page xianyu-style">
    <!-- 1) 顶部导航 - 易淘风格 -->
    <header class="header-sticky">
      <div class="header-content">
        <!-- Logo -->
        <div class="brand-logo" @click="router.push('/')">
          <span class="logo-icon">🛒</span>
          <span class="logo-text">易淘</span>
        </div>

        <!-- 搜索区 - 使用Element Plus组件 -->
        <div class="search-section">
          <el-input
            v-model="searchKeyword"
            :placeholder="searchPlaceholder"
            size="large"
            class="custom-search-input"
            @keyup.enter="handleSearchKeyword"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button 
                @click="handleSearchKeyword"
                :icon="Search"
                type="primary"
              >
                搜索
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- 右侧用户区 -->
        <div class="user-section">
          <template v-if="authStore.user">
            <div class="user-dropdown">
              <div
                class="user-info"
                role="button"
                aria-haspopup="true"
                aria-expanded="false"
              >
                <div class="user-avatar-block">
                  <img
                    v-if="authStore.user.avatar"
                    :src="authStore.user.avatar"
                    class="user-avatar"
                    alt="用户头像"
                  />
                  <div v-else class="user-avatar-default">{{ userInitial }}</div>
                </div>
                <div class="user-meta">
                  <span class="user-meta-name">{{ userDisplayName }}</span>
                  <span class="user-meta-desc">个人中心</span>
                </div>
                <span class="dropdown-arrow" aria-hidden="true">▼</span>
              </div>
              <div class="custom-dropdown">
                <div class="user-profile-card">
                  <div class="profile-header">
                    <img v-if="authStore.user.avatar" :src="authStore.user.avatar" class="profile-avatar" />
                    <div v-else class="profile-avatar-default">{{ userInitial }}</div>
                    <div class="profile-info">
                      <div class="profile-name">{{ authStore.user.username }}</div>
                      <div class="profile-stats">
                        <span class="stat-item">0 粉丝</span>
                        <span class="stat-divider">|</span>
                        <span class="stat-item">0 关注</span>
                      </div>
                    </div>
                  </div>
                  <div class="profile-menu">
                    <div class="profile-menu-item" @click="handleUserMenuCommand('orders')">
                      <span class="menu-text">我买到的</span>
                      <span class="menu-arrow">›</span>
                    </div>
                    <div class="profile-menu-item" @click="handleUserMenuCommand('products')">
                      <span class="menu-text">我卖出的</span>
                      <span class="menu-arrow">›</span>
                    </div>
                    <div class="profile-menu-item" @click="handleUserMenuCommand('favorites')">
                      <span class="menu-text">我的收藏</span>
                      <span class="menu-arrow">›</span>
                    </div>
                    <div class="profile-menu-item" @click="handleUserMenuCommand('messages')">
                      <span class="menu-text">消息中心</span>
                      <span class="menu-arrow">›</span>
                    </div>
                    <div class="profile-menu-item" @click="handleUserMenuCommand('profile')">
                      <span class="menu-text">个人中心</span>
                      <span class="menu-arrow">›</span>
                    </div>
                  </div>
                  <div class="logout-item" @click="handleUserMenuCommand('logout')">
                    <span class="logout-text">退出登录</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="order-link" @click="router.push('/profile?tab=bought')">
              <span class="order-icon">📋</span>
              <span>订单</span>
            </div>
          </template>
          <template v-else>
            <div class="login-btn" @click="goToLogin">登录/注册</div>
          </template>
        </div>
      </div>
    </header>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="product" class="detail-container">
      <!-- 卖家信息栏 -->
      <div class="seller-header">
        <div class="seller-left">
          <el-avatar :size="48" class="seller-avatar">
            {{ product.seller?.username?.[0] || '卖' }}
          </el-avatar>
          <div class="seller-info">
            <div class="seller-name">{{ product.seller?.username }}</div>
            <div class="seller-stats">
              <span class="stat-item">
                <el-icon><Location /></el-icon>
                {{ product.location || '未知' }}
              </span>
              <span class="stat-item">发布于 {{ formatTimeAgo(product.created_at) }}</span>
            </div>
          </div>
        </div>
        <div class="seller-right">
          <el-button 
            class="shop-btn"
            @click="handleViewSeller"
          >
            <el-icon><Shop /></el-icon>
            TA的小店
          </el-button>
        </div>
      </div>

      <!-- 主体内容 -->
      <div class="main-content">
        <!-- 左侧：图片展示区 -->
        <div class="image-section">
          <!-- 缩略图列表（左侧） -->
          <div v-if="product.images && product.images.length > 1" class="thumbnail-list">
            <div
              v-for="(img, index) in product.images"
              :key="index"
              class="thumbnail-item"
              :class="{ active: currentImage === index }"
              @click="currentImage = index"
              @mouseenter="currentImage = index"
            >
              <img :src="getImageUrl(img.image)" :alt="product.title" />
            </div>
          </div>
          
          <!-- 主图 -->
          <div class="main-image-wrapper">
            <el-image
              v-if="product.images && product.images.length > 0"
              :src="getImageUrl(product.images[currentImage]?.image)"
              :alt="product.title"
              fit="contain"
              class="main-image"
              :preview-src-list="product.images.map(img => getImageUrl(img.image))"
              :initial-index="currentImage"
            />
            <div v-else class="no-image">
              <el-icon><PictureFilled /></el-icon>
              <p>暂无图片</p>
            </div>
          </div>
        </div>

        <!-- 右侧：商品信息区 -->
        <div class="info-section">
          <!-- 价格区 -->
          <div class="price-area">
            <div class="price-row">
              <span class="currency">¥</span>
              <span class="price-value">{{ product.price }}</span>
              <span v-if="product.original_price" class="original-price">¥{{ product.original_price }}</span>
              <span class="shipping-tag">包邮</span>
            </div>
            <div class="condition-badge" :class="getConditionClass(product.condition)">
              {{ conditionMap[product.condition] || '未知成色' }}
            </div>
          </div>

          <!-- 统计信息 -->
          <div class="stats-row">
            <span class="stat">{{ product.favorite_count || 0 }}人想要</span>
            <span class="stat-divider">|</span>
            <span class="stat">{{ product.view_count || 0 }}浏览</span>
          </div>

          <!-- 商品描述 -->
          <div class="description-area">
            <div class="product-title">{{ product.title }}</div>
            <div class="product-desc">{{ product.description }}</div>
          </div>

          <!-- 商品属性 -->
          <div class="attributes-area">
            <div class="attr-row">
              <span class="attr-label">分类：</span>
              <span class="attr-value">{{ product.category?.name || '其他' }}</span>
            </div>
            <div class="attr-row" v-if="product.condition">
              <span class="attr-label">成色：</span>
              <span class="attr-value">{{ conditionMap[product.condition] }}</span>
            </div>
            <div class="attr-row" v-if="product.location">
              <span class="attr-label">所在地：</span>
              <span class="attr-value">{{ product.location }}</span>
            </div>
          </div>

          <!-- 操作按钮区 -->
          <div class="action-area">
            <el-button 
              class="action-btn chat-btn"
              size="large"
              @click="handleMessage"
              :disabled="authStore.user && authStore.user.id === product.seller?.id"
            >
              <el-icon><ChatDotRound /></el-icon>
              聊一聊
            </el-button>
            
            <el-button
              v-if="product.status === 'active'"
              class="action-btn buy-btn"
              size="large"
              @click="handleBuy"
              :disabled="!authStore.user || (authStore.user && authStore.user.id === product.seller?.id)"
            >
              立即购买
            </el-button>
            <el-button v-else class="action-btn disabled-btn" size="large" disabled>
              {{ product.status === 'sold' ? '已售出' : '已下架' }}
            </el-button>
            
            <el-button 
              class="action-btn favorite-btn"
              size="large"
              @click="handleFavorite"
              :disabled="!authStore.user"
            >
              <el-icon>
                <StarFilled v-if="product.is_favorited" />
                <Star v-else />
              </el-icon>
              {{ product.is_favorited ? '已收藏' : '收藏' }}
            </el-button>
          </div>

          <!-- 底部链接 -->
          <div class="footer-links">
            <span class="link-item">
              <el-icon><CircleCheck /></el-icon>
              担保交易
            </span>
            <span class="link-item" @click="handleShare">
              <el-icon><Share /></el-icon>
              分享
            </span>
          </div>
        </div>
      </div>

      <!-- 相似商品推荐 -->
      <div class="related-section" v-if="relatedProducts.length > 0">
        <div class="section-title">
          <span>相似商品推荐</span>
        </div>
        <div class="related-grid">
          <div 
            v-for="item in relatedProducts" 
            :key="item.id" 
            class="related-card"
            @click="$router.push(`/products/${item.id}`)"
          >
            <div class="related-image">
              <img v-if="item.images && item.images.length > 0" :src="getImageUrl(item.images[0].image)" :alt="item.title" />
              <div v-else class="no-image-small">
                <el-icon><PictureFilled /></el-icon>
              </div>
            </div>
            <div class="related-info">
              <div class="related-title">{{ item.title }}</div>
              <div class="related-price">¥{{ item.price }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 下单对话框 -->
    <el-dialog v-model="showOrderDialog" title="确认购买" width="480px" @close="resetOrderForm" class="order-dialog">
      <div v-if="product" class="order-product-preview">
        <div class="preview-image">
          <img v-if="product.images?.length" :src="getImageUrl(product.images[0].image)" />
          <el-icon v-else><PictureFilled /></el-icon>
        </div>
        <div class="preview-info">
          <div class="preview-title">{{ product.title }}</div>
          <div class="preview-price">¥{{ product.price }}</div>
        </div>
      </div>
      
      <el-divider />
      
      <el-form :model="orderForm" label-width="90px" class="order-form">
        <el-form-item label="收货人" required>
          <el-input v-model="orderForm.shipping_name" placeholder="请输入收货人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" required>
          <el-input v-model="orderForm.shipping_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="收货地址" required>
          <el-input v-model="orderForm.shipping_address" type="textarea" :rows="2" placeholder="请输入详细收货地址" />
        </el-form-item>
        <el-form-item label="留言">
          <el-input v-model="orderForm.note" type="textarea" :rows="2" placeholder="选填，可填写特殊要求" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showOrderDialog = false">取消</el-button>
        <el-button type="warning" @click="handleOrderSubmit" :loading="orderLoading" class="submit-btn">
          确认购买 ¥{{ product?.price }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 支付对话框 -->
    <el-dialog
      v-model="paymentDialogVisible"
      title="选择支付方式"
      width="460px"
      :close-on-click-modal="false"
      class="payment-dialog"
    >
      <div class="payment-options">
        <div 
          class="payment-option"
          :class="{ active: paymentType === 'alipay' }"
          @click="paymentType = 'alipay'"
        >
          <div class="option-icon alipay">
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%231677ff' d='M21.422 15.358c-3.06-1.064-5.094-1.917-6.308-2.553.488-1.122.849-2.363 1.033-3.674h-4.15V7.995h4.98V6.948h-4.98V4.468h-2.047c-.2 0-.363.163-.363.363v2.117H5.07v1.047h4.517v1.136H5.87v.947h7.855c-.156.93-.413 1.795-.76 2.574-2.75-.885-5.694-1.2-5.694 1.38 0 1.67 1.463 2.706 3.803 2.706 2.232 0 3.803-.787 4.706-2.363.92.42 2.016.91 3.28 1.474.18.08.374.15.583.214v3.24c0 .66-.537 1.197-1.197 1.197H5.554c-.66 0-1.197-.537-1.197-1.197V5.554c0-.66.537-1.197 1.197-1.197h12.892c.66 0 1.197.537 1.197 1.197v9.804h1.78zm-10.27 2.29c-1.6 0-2.293-.41-2.293-1.094 0-.916 1.15-.916 2.1-.916.87 0 1.735.08 2.542.253-.61 1.184-1.461 1.757-2.35 1.757z'/%3E%3C/svg%3E" alt="支付宝" />
          </div>
          <span class="option-name">支付宝</span>
        </div>
        <div 
          class="payment-option"
          :class="{ active: paymentType === 'wxpay' }"
          @click="paymentType = 'wxpay'"
        >
          <div class="option-icon wechat">
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2307c160' d='M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088-.181-.012-.363-.022-.545-.033h-.061zm-2.89 3.217c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.97-.982zm4.844 0c.536 0 .97.44.97.982a.976.976 0 0 1-.97.983.976.976 0 0 1-.969-.983c0-.542.433-.982.97-.982z'/%3E%3C/svg%3E" alt="微信" />
          </div>
          <span class="option-name">微信支付</span>
        </div>
      </div>
      
      <div class="payment-amount">
        <span>支付金额</span>
        <span class="amount">¥{{ product?.price }}</span>
      </div>
      
      <!-- 支付二维码 -->
      <div v-if="qrcodeUrl" class="qrcode-container">
        <el-image :src="qrcodeUrl" fit="contain" class="qrcode-img" />
        <p class="qrcode-tip">请使用{{ paymentType === 'alipay' ? '支付宝' : '微信' }}扫码支付</p>
        <el-alert 
          title="演示模式：可点击下方【模拟完成支付】进行测试" 
          type="info" 
          :closable="false"
          show-icon
          style="margin-top: 12px;"
        />
      </div>
      
      <template #footer>
        <el-button @click="closePaymentDialog">取消</el-button>
        <el-button 
          v-if="!qrcodeUrl" 
          type="warning" 
          @click="createPayment"
          :loading="paymentLoading"
        >
          确认支付
        </el-button>
        <template v-else>
          <el-button 
            type="primary" 
            @click="demoCompletePayment"
            :loading="checkingPayment"
          >
            🎭 模拟完成支付
          </el-button>
          <el-button 
            type="success" 
            @click="checkPaymentStatus"
            :loading="checkingPayment"
          >
            我已支付完成
          </el-button>
        </template>
      </template>
    </el-dialog>

    <!-- 移动端底部操作条 -->
    <div class="mobile-action-bar" v-if="product && !loading">
      <div class="mobile-left">
        <div class="mobile-btn" @click="handleMessage">
          <el-icon><ChatDotRound /></el-icon>
          <span>聊一聊</span>
        </div>
        <div class="mobile-btn" @click="handleFavorite">
          <el-icon>
            <StarFilled v-if="product.is_favorited" />
            <Star v-else />
          </el-icon>
          <span>{{ product.is_favorited ? '已收藏' : '收藏' }}</span>
        </div>
      </div>
      <el-button 
        v-if="product.status === 'active'"
        class="mobile-buy-btn"
        @click="handleBuy"
        :disabled="!authStore.user || (authStore.user && authStore.user.id === product.seller?.id)"
      >
        ¥{{ product.price }} 立即购买
      </el-button>
      <el-button v-else class="mobile-buy-btn disabled" disabled>
        {{ product.status === 'sold' ? '已售出' : '已下架' }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Star, StarFilled, ChatDotRound, PictureFilled, Share, CircleCheck, Location, Shop, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import { getImageUrl } from '@/utils/image'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userDisplayName = computed(() => authStore.user?.nickname || authStore.user?.username || '易淘用户')
const userInitial = computed(() => authStore.user?.username?.charAt(0)?.toUpperCase() || 'U')

const product = ref(null)
const relatedProducts = ref([])
const loading = ref(true)
const showOrderDialog = ref(false)
const orderLoading = ref(false)
const currentImage = ref(0)
const orderForm = ref({
  shipping_name: '',
  shipping_phone: '',
  shipping_address: '',
  note: ''
})

// 支付相关
const paymentDialogVisible = ref(false)
const paymentType = ref('alipay')
const paymentLoading = ref(false)
const qrcodeUrl = ref('')
const checkingPayment = ref(false)
const currentOrderId = ref(null)
let paymentCheckTimer = null

// 搜索相关
const searchKeyword = ref('')
const hotWords = ref([])

// 动态搜索提示
const searchPlaceholder = computed(() => {
  if (hotWords.value.length >= 3) {
    const samples = hotWords.value.slice(0, 3)
    return `搜索好物，例如 ${samples.join(' / ')}`
  }
  return '搜索二手好物'
})

const conditionMap = { 
  new: '全新', 
  like_new: '几乎全新', 
  good: '成色良好', 
  fair: '有使用痕迹', 
  poor: '成色较旧' 
}

// 加载热词
const loadHotWords = async () => {
  try {
    const res = await api.get('/products/', { 
      params: { status: 'active', page_size: 30 } 
    })
    const productList = res.data.results || res.data
    
    if (!productList || productList.length === 0) return
    
    // 从商品标题中提取关键词
    const words = []
    productList.forEach(product => {
      if (product.title) {
        const title = product.title.trim()
        const keyword = title.length > 12 ? title.substring(0, 8) : title
        if (keyword.length >= 2 && !words.includes(keyword)) {
          words.push(keyword)
        }
      }
    })
    
    hotWords.value = words.slice(0, 10)
  } catch (err) {
    console.error('加载热词失败:', err)
  }
}

// 搜索处理
const handleSearchKeyword = () => {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/products', query: { search: searchKeyword.value } })
  } else {
    router.push('/products')
  }
}

// 用户菜单处理
const handleUserMenuCommand = async (command) => {
  switch (command) {
    case 'products':
      router.push('/profile')
      break
    case 'orders':
      router.push('/profile?tab=bought')
      break
    case 'favorites':
      router.push('/profile?tab=favorites')
      break
    case 'messages':
      router.push('/messages')
      break
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        authStore.logout()
        ElMessage.success('已退出登录')
        router.push('/')
      } catch {
        // 取消退出
      }
      break
  }
}

const goToLogin = () => router.push('/login')

onMounted(() => { 
  loadProduct()
  loadHotWords()
  if (!authStore.user) {
    authStore.init()
  }
})

onBeforeUnmount(() => {
  if (paymentCheckTimer) {
    clearInterval(paymentCheckTimer)
  }
})

const getConditionClass = (condition) => {
  const classMap = {
    new: 'condition-new',
    like_new: 'condition-like-new',
    good: 'condition-good',
    fair: 'condition-fair',
    poor: 'condition-poor'
  }
  return classMap[condition] || 'condition-default'
}

const formatTimeAgo = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  return date.toLocaleDateString('zh-CN')
}

const loadProduct = async () => {
  try {
    const res = await api.get(`/products/${route.params.id}/`)
    product.value = res.data
    loadRelatedProducts()
  } catch (error) {
    ElMessage.error('商品加载失败')
    router.push('/products')
  } finally { 
    loading.value = false 
  }
}

const loadRelatedProducts = async () => {
  try {
    const params = { status: 'active', category: product.value?.category?.id, page_size: 6 }
    const res = await api.get('/products/', { params })
    const allProducts = res.data.results || res.data
    relatedProducts.value = allProducts.filter(p => p.id !== product.value?.id).slice(0, 6)
  } catch (error) { 
    console.error('加载相似商品失败:', error) 
  }
}

const handleFavorite = async () => {
  if (!authStore.user) { 
    ElMessage.warning('请先登录')
    router.push('/login')
    return 
  }
  try {
    if (product.value.is_favorited) {
      await api.delete('/favorites/remove/', { params: { product_id: route.params.id } })
      ElMessage.success('已取消收藏')
    } else {
      await api.post('/favorites/', { product_id: route.params.id })
      ElMessage.success('已收藏')
    }
    loadProduct()
  } catch (error) { 
    ElMessage.error('操作失败') 
  }
}

const handleMessage = () => {
  if (!authStore.user) { 
    ElMessage.warning('请先登录')
    router.push('/login')
    return 
  }
  if (authStore.user.id === product.value.seller.id) { 
    ElMessage.warning('不能联系自己')
    return 
  }
  router.push(`/messages?user_id=${product.value.seller.id}&product_id=${route.params.id}`)
}

const handleBuy = () => {
  if (!authStore.user) { 
    ElMessage.warning('请先登录')
    router.push('/login')
    return 
  }
  if (authStore.user.id === product.value.seller.id) { 
    ElMessage.warning('不能购买自己的商品')
    return 
  }
  if (product.value.status !== 'active') { 
    ElMessage.warning('商品已下架或已售出')
    return 
  }
  // 跳转到订单确认页面
  router.push(`/checkout/${route.params.id}`)
}

const handleViewSeller = () => { 
  router.push(`/products?seller=${product.value.seller.id}`) 
}

const handleOrderSubmit = async () => {
  if (!orderForm.value.shipping_name || !orderForm.value.shipping_phone || !orderForm.value.shipping_address) {
    ElMessage.warning('请填写完整信息')
    return 
  }
  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(orderForm.value.shipping_phone)) { 
    ElMessage.warning('请输入正确的手机号码')
    return 
  }
  orderLoading.value = true
  try {
    const resp = await api.post('/orders/', { product_id: route.params.id, ...orderForm.value })
    ElMessage.success('订单创建成功！')
    showOrderDialog.value = false
    resetOrderForm()
    currentOrderId.value = resp.data.id
    paymentDialogVisible.value = true
    paymentType.value = 'alipay'
    qrcodeUrl.value = ''
  } catch (error) {
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || '创建订单失败'
    ElMessage.error(errorMsg)
  } finally { 
    orderLoading.value = false 
  }
}

const closePaymentDialog = () => {
  paymentDialogVisible.value = false
  qrcodeUrl.value = ''
  if (paymentCheckTimer) {
    clearInterval(paymentCheckTimer)
    paymentCheckTimer = null
  }
  if (currentOrderId.value) {
    router.push(`/order/${currentOrderId.value}`)
  }
}

const createPayment = async () => {
  paymentLoading.value = true
  try {
    const res = await api.post('/payment/create/', {
      order_id: currentOrderId.value,
      pay_type: paymentType.value
    })
    
    if (res.data.success) {
      qrcodeUrl.value = res.data.qrcode
      ElMessage.success('支付二维码已生成')
      startPaymentCheck()
    } else {
      ElMessage.error(res.data.error || '创建支付失败')
    }
  } catch (error) {
    console.error('创建支付错误:', error)
    ElMessage.error(error.response?.data?.error || '创建支付失败')
  } finally {
    paymentLoading.value = false
  }
}

const startPaymentCheck = () => {
  paymentCheckTimer = setInterval(async () => {
    await checkPaymentStatus(true)
  }, 3000)
}

const checkPaymentStatus = async (isAutoCheck = false) => {
  if (!isAutoCheck) {
    checkingPayment.value = true
  }
  
  try {
    const res = await api.get(`/payment/query/${currentOrderId.value}/`)
    
    if (res.data.success && res.data.status === 1) {
      ElMessage.success('支付成功！')
      closePaymentDialog()
      router.push(`/order/${currentOrderId.value}`)
    } else if (!isAutoCheck) {
      ElMessage.warning('尚未检测到支付，请完成支付后再试')
    }
  } catch (error) {
    if (!isAutoCheck) {
      console.error('查询支付状态错误:', error)
      ElMessage.error('查询支付状态失败')
    }
  } finally {
    checkingPayment.value = false
  }
}

const demoCompletePayment = async () => {
  checkingPayment.value = true
  try {
    const res = await api.post(`/payment/demo-complete/${currentOrderId.value}/`)
    
    if (res.data.success) {
      ElMessage.success('演示模式：支付已完成！')
      closePaymentDialog()
      router.push(`/order/${currentOrderId.value}`)
    } else {
      ElMessage.error(res.data.error || '操作失败')
    }
  } catch (error) {
    console.error('模拟支付错误:', error)
    ElMessage.error(error.response?.data?.error || '演示模式不可用')
  } finally {
    checkingPayment.value = false
  }
}

const resetOrderForm = () => { 
  orderForm.value = { shipping_name: '', shipping_phone: '', shipping_address: '', note: '' } 
}

const handleShare = () => {
  const shareUrl = `${window.location.origin}/products/${route.params.id}`
  const title = product.value?.title || '查看这个商品'
  if (navigator.share) { 
    navigator.share({ title, text: title, url: shareUrl }).catch(()=>{}) 
  } else { 
    navigator.clipboard.writeText(shareUrl)
      .then(() => ElMessage.success('链接已复制'))
      .catch(() => ElMessage.error('复制失败')) 
  }
}
</script>

<style scoped>
.xianyu-style {
  --brand: #ffe400;
  --brand-orange: #ff6600;
  --primary: #ffe400;
  --primary-dark: #ffd600;
  --price-color: #ff2442;
  --text-primary: #222;
  --text-secondary: #666;
  --text-muted: #999;
  --text-light: #999;
  --border-color: #f0f0f0;
  --bg-page: #f5f5f5;
  --bg-white: #fff;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 50px;
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
}

.product-detail-page {
  background: var(--bg-page);
  min-height: 100vh;
  padding-bottom: 80px;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", "Microsoft YaHei", sans-serif;
  margin: 0;
  padding-top: 0;
  padding-left: 0;
  padding-right: 0;
  width: 100%;
}

/* ==================== 顶部导航 ==================== */
.header-sticky {
  background: linear-gradient(135deg, #ffe400 0%, #ffd000 50%, #ffe400 100%);
  background-size: 200% 200%;
  animation: gradientShift 10s ease infinite;
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 16px 0;
  margin: 0;
  box-shadow: 0 4px 24px rgba(0,0,0,0.1);
  border-bottom: 2px solid rgba(255,255,255,0.3);
  width: 100%;
  left: 0;
  right: 0;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 40px;
  padding: 0 20px;
}

/* Logo */
.brand-logo { 
  cursor: pointer; 
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.6));
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.brand-logo:hover { 
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.12);
  background: linear-gradient(135deg, rgba(255,255,255,1), rgba(255,255,255,0.8));
}
.logo-icon {
  font-size: 32px;
  line-height: 1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
  animation: bounce 2s ease-in-out infinite;
}
.logo-text { 
  font-size: 36px; 
  font-weight: 900; 
  background: linear-gradient(135deg, #ff6600, #ff8833);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  letter-spacing: -1px;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-4px) scale(1.05); }
}

/* 搜索区域 - Element Plus样式 */
.search-section { 
  flex: 1;
  max-width: 580px;
}

.custom-search-input {
  height: 44px;
}

.custom-search-input :deep(.el-input__wrapper) {
  border-radius: 22px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  padding-left: 16px;
}

.custom-search-input :deep(.el-input__prefix) {
  color: var(--text-light);
}

.custom-search-input :deep(.el-input-group__append) {
  border-radius: 0 22px 22px 0;
  border: none;
  box-shadow: none;
}

.custom-search-input :deep(.el-input-group__append .el-button) {
  border-radius: 0 22px 22px 0;
  height: 44px;
  padding: 0 24px;
}

/* 用户区域 */
.user-section {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
  margin-left: auto;
  justify-content: flex-end;
}

.user-dropdown {
  position: relative;
  display: inline-block;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 10px 16px;
  border-radius: 14px;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(10px);
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid rgba(255,255,255,0.4);
}
.dropdown-arrow {
  font-size: 12px;
  color: #666;
  margin-left: 2px;
  transition: transform 0.1s cubic-bezier(0.4, 0, 0.2, 1), color 0.1s linear;
}

.user-dropdown:hover .user-info { 
  background: #fff8e6;
  border-color: rgba(255,106,0,0.3);
  box-shadow: 0 6px 20px rgba(255,106,0,0.12);
}
.user-dropdown:hover .dropdown-arrow {
  color: var(--brand-orange);
  transform: rotate(180deg);
}

.user-avatar-block {
  width: 34px;
  height: 34px;
  border-radius: 50%;
}

.user-avatar, .user-avatar-default {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  flex-shrink: 0;
}
.user-avatar { 
  object-fit: cover; 
  border: 2px solid rgba(255,106,0,0.15);
  transition: all 0.25s ease;
}
.user-dropdown:hover .user-avatar {
  border-color: rgba(255,106,0,0.4);
}
.user-avatar-default {
  background: linear-gradient(135deg, #ff6600, #ff8833);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
  border: 2px solid rgba(255,106,0,0.15);
  transition: all 0.25s ease;
}
.user-dropdown:hover .user-avatar-default {
  border-color: rgba(255,106,0,0.4);
}
.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.user-meta-name {
  font-size: 14px;
  color: #222;
  font-weight: 600;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-dropdown:hover .user-meta-name {
  color: #ff6600;
}

.user-meta-desc {
  font-size: 11px;
  color: #999;
  letter-spacing: 0.2px;
}
.user-dropdown:hover .user-meta-desc {
  color: #ffb347;
}

.custom-dropdown {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 4px;
  min-width: 260px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.8);
  background: #fff;
  overflow: hidden;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transform: translateY(6px);
  transition: opacity 0.08s cubic-bezier(0.4, 0, 0.2, 1), transform 0.08s cubic-bezier(0.4, 0, 0.2, 1), visibility 0.08s linear;
}

.user-dropdown:hover .custom-dropdown {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.user-profile-card {
  width: 100%;
}

.profile-header {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.profile-avatar, .profile-avatar-default {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 12px;
}

.profile-avatar {
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.profile-avatar-default {
  background: linear-gradient(135deg, #ff6600, #ff8833);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.profile-stats {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
}

.stat-item {
  margin-right: 4px;
}

.stat-divider {
  margin: 0 6px;
  color: #e0e0e0;
}

.profile-menu {
  padding: 8px 0;
}

.profile-menu-item {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: background 0.2s ease;
}

.profile-menu-item:hover {
  background: #fafafa;
}

.menu-text {
  flex: 1;
}

.menu-arrow {
  font-size: 16px;
  color: #ccc;
}

.logout-item {
  padding: 12px 16px;
  font-size: 14px;
  color: #ff4444;
  text-align: center;
  border-top: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s ease;
}

.logout-item:hover {
  background: #fff2f2;
}

.order-link {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #222;
  cursor: pointer;
  padding: 10px 16px;
  border-radius: 12px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(8px);
  transition: all 0.25s ease;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,0.3);
}
.order-link:hover { 
  background: #fff8e6;
  border-color: rgba(255,106,0,0.2);
  color: #ff6600; 
}
.order-link .order-icon {
  font-size: 18px;
  line-height: 1;
}

.login-btn {
  font-size: 14px;
  color: #fff;
  cursor: pointer;
  padding: 10px 20px;
  background: linear-gradient(135deg, #ff6600, #ff8833);
  border-radius: 12px;
  font-weight: 500;
  border: 1px solid rgba(255,102,0,0.3);
  transition: all 0.25s ease;
}
.login-btn:hover { 
  background: linear-gradient(135deg, #ff7722, #ff9944);
  border-color: rgba(255,102,0,0.5);
  transform: translateY(-1px);
}

.loading-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 卖家信息栏 */
.seller-header {
  background: var(--bg-white);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.seller-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.seller-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: 600;
}

.seller-info .seller-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.seller-stats {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: var(--text-muted);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.shop-btn {
  border-radius: 20px;
  padding: 8px 20px;
}

/* 主体内容 */
.main-content {
  background: var(--bg-white);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  gap: 32px;
  margin-bottom: 16px;
}

/* 图片区域 */
.image-section {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.thumbnail-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 72px;
}

.thumbnail-item {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.thumbnail-item:hover,
.thumbnail-item.active {
  border-color: var(--primary);
}

.thumbnail-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.main-image-wrapper {
  width: 480px;
  height: 480px;
  border-radius: 12px;
  overflow: hidden;
  background: #fafafa;
}

.main-image {
  width: 100%;
  height: 100%;
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #ccc;
  font-size: 64px;
}

.no-image p {
  font-size: 14px;
  margin-top: 12px;
}

/* 信息区域 */
.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 价格区 */
.price-area {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.currency {
  font-size: 20px;
  color: var(--price-color);
  font-weight: 600;
}

.price-value {
  font-size: 36px;
  color: var(--price-color);
  font-weight: 700;
  line-height: 1;
}

.original-price {
  font-size: 14px;
  color: var(--text-muted);
  text-decoration: line-through;
  margin-left: 8px;
}

.shipping-tag {
  font-size: 12px;
  color: var(--text-muted);
  border: 1px solid var(--border-color);
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 8px;
}

.condition-badge {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
}

.condition-new { background: #fff3cd; color: #856404; }
.condition-like-new { background: #ffe400; color: #333; }
.condition-good { background: #d4edda; color: #155724; }
.condition-fair { background: #e2e3e5; color: #383d41; }
.condition-poor { background: #f8d7da; color: #721c24; }
.condition-default { background: #f0f0f0; color: #666; }

/* 统计信息 */
.stats-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.stat-divider {
  color: #ddd;
}

/* 商品描述 */
.description-area {
  margin-bottom: 20px;
}

.product-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.5;
  margin-bottom: 12px;
}

.product-desc {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.8;
  white-space: pre-wrap;
}

/* 商品属性 */
.attributes-area {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.attr-row {
  display: flex;
  margin-bottom: 8px;
}

.attr-row:last-child {
  margin-bottom: 0;
}

.attr-label {
  width: 70px;
  font-size: 14px;
  color: var(--text-muted);
}

.attr-value {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
}

/* 操作按钮区 */
.action-area {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.action-btn {
  height: 48px;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 500;
}

.chat-btn {
  flex: 0 0 140px;
  background: #fff;
  border: 1px solid #ddd;
  color: var(--text-primary);
}

.chat-btn:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

.buy-btn {
  flex: 1;
  background: var(--primary);
  border-color: var(--primary);
  color: #333;
}

.buy-btn:hover:not(:disabled) {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
}

.disabled-btn {
  flex: 1;
  background: #e0e0e0;
  border-color: #e0e0e0;
  color: #999;
}

.favorite-btn {
  flex: 0 0 100px;
  background: #fff;
  border: 1px solid #ddd;
  color: var(--text-primary);
}

.favorite-btn:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

/* 底部链接 */
.footer-links {
  display: flex;
  gap: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.link-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
}

.link-item:hover {
  color: var(--text-secondary);
}

/* 相似商品推荐 */
.related-section {
  background: var(--bg-white);
  border-radius: 12px;
  padding: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.related-card {
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  background: #fafafa;
  transition: all 0.2s;
}

.related-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.related-image {
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
}

.related-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image-small {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
  font-size: 32px;
}

.related-info {
  padding: 10px;
}

.related-title {
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-price {
  font-size: 15px;
  font-weight: 600;
  color: var(--price-color);
}

/* 订单对话框 */
.order-product-preview {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.preview-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.preview-title {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.preview-price {
  font-size: 20px;
  font-weight: 600;
  color: var(--price-color);
}

.submit-btn {
  background: var(--primary);
  border-color: var(--primary);
  color: #333;
  font-weight: 600;
}

.submit-btn:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
}

/* 支付对话框 */
.payment-options {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.payment-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-option:hover {
  border-color: #ccc;
}

.payment-option.active {
  border-color: var(--primary);
  background: #fffde7;
}

.option-icon {
  width: 48px;
  height: 48px;
}

.option-icon img {
  width: 100%;
  height: 100%;
}

.option-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.payment-amount {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.payment-amount .amount {
  font-size: 24px;
  font-weight: 700;
  color: var(--price-color);
}

.qrcode-container {
  text-align: center;
  padding: 24px;
  background: #fafafa;
  border-radius: 8px;
  margin-top: 16px;
}

.qrcode-img {
  width: 180px;
  height: 180px;
}

.qrcode-tip {
  margin-top: 12px;
  color: var(--text-muted);
  font-size: 14px;
}

/* 移动端底部操作条 */
.mobile-action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--bg-white);
  border-top: 1px solid var(--border-color);
  padding: 8px 12px;
  display: none;
  align-items: center;
  gap: 12px;
  z-index: 1000;
}

.mobile-left {
  display: flex;
  gap: 16px;
}

.mobile-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
}

.mobile-btn .el-icon {
  font-size: 20px;
}

.mobile-buy-btn {
  flex: 1;
  height: 44px;
  background: var(--primary);
  border-color: var(--primary);
  color: #333;
  font-size: 16px;
  font-weight: 600;
  border-radius: 22px;
}

.mobile-buy-btn.disabled {
  background: #e0e0e0;
  border-color: #e0e0e0;
  color: #999;
}

/* 响应式 */
@media (max-width: 1200px) {
  .related-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 992px) {
  .main-content {
    flex-direction: column;
    padding: 16px;
  }
  
  .image-section {
    flex-direction: column-reverse;
    gap: 12px;
  }
  
  .thumbnail-list {
    flex-direction: row;
    width: 100%;
    overflow-x: auto;
    padding-bottom: 4px;
  }
  
  .thumbnail-item {
    flex-shrink: 0;
    width: 64px;
    height: 64px;
  }
  
  .main-image-wrapper {
    width: 100%;
    height: auto;
    aspect-ratio: 1;
  }
  
  .action-area {
    flex-wrap: wrap;
  }
  
  .chat-btn {
    flex: 1 1 100%;
    order: 3;
  }
  
  .buy-btn,
  .disabled-btn {
    flex: 2;
  }
  
  .favorite-btn {
    flex: 1;
  }
  
  .related-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .product-detail-page {
    padding-bottom: 70px;
  }
  
  .detail-container {
    padding: 12px;
  }
  
  .seller-header {
    padding: 12px 16px;
  }
  
  .seller-stats {
    flex-direction: column;
    gap: 2px;
  }
  
  .shop-btn {
    display: none;
  }
  
  .price-value {
    font-size: 28px;
  }
  
  .condition-badge {
    font-size: 12px;
    padding: 4px 8px;
  }
  
  .action-area {
    display: none;
  }
  
  .footer-links {
    display: none;
  }
  
  .mobile-action-bar {
    display: flex;
  }
  
  .related-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
