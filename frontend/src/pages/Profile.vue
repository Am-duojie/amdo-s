<template>
  <div class="profile-page xianyu-style">
    
    <div class="profile-container">
      <!-- 左侧边栏 -->
      <div class="sidebar">
        <div class="sidebar-menu">
          <template v-if="!isVerifiedZone">
            <!-- 我的易淘 -->
            <div class="menu-item" :class="{ active: activeMenu === 'home' }" @click="switchMenu('home')">
              <el-icon><User /></el-icon>
              <span>我的易淘</span>
            </div>

            <!-- 官方验入口（账号信息共享，订单独立） -->
            <div class="menu-item" @click="goToVerifiedProfile">
              <el-icon><DocumentChecked /></el-icon>
              <span>我的官方验</span>
            </div>

            <!-- 我的交易 -->
            <div class="menu-group">
              <div class="menu-header" @click="toggleMenu('trade')">
                <el-icon><ShoppingBag /></el-icon>
                <span>我的交易</span>
                <el-icon class="arrow" :class="{ expanded: expandedMenus.trade }"><ArrowDown /></el-icon>
              </div>
              <div class="submenu" v-show="expandedMenus.trade">
                <div class="submenu-item" :class="{ active: activeMenu === 'published' }" @click="switchMenu('published')">
                  我发布的
                </div>
                <div class="submenu-item" :class="{ active: activeMenu === 'sold' }" @click="switchMenu('sold')">
                  我卖出的
                </div>
                <div class="submenu-item" :class="{ active: activeMenu === 'bought' }" @click="switchMenu('bought')">
                  我买到的
                </div>
              </div>
            </div>

            <!-- 我的收藏 -->
            <div class="menu-item" :class="{ active: activeMenu === 'favorites' }" @click="switchMenu('favorites')">
              <el-icon><Star /></el-icon>
              <span>我的收藏</span>
            </div>

            <!-- 我的钱包 -->
            <div class="menu-group">
              <div class="menu-header" @click="toggleMenu('wallet')">
                <el-icon><Wallet /></el-icon>
                <span>我的钱包</span>
                <el-icon class="arrow" :class="{ expanded: expandedMenus.wallet }"><ArrowDown /></el-icon>
              </div>
              <div class="submenu" v-show="expandedMenus.wallet">
                <div class="submenu-item" :class="{ active: activeMenu === 'wallet-transactions' }" @click="switchMenu('wallet-transactions')">
                  交易记录
                </div>

                <div class="submenu-item" :class="{ active: activeMenu === 'wallet-bind' }" @click="switchMenu('wallet-bind')">
                  绑定支付宝
                </div>
              </div>
            </div>

            <!-- 账户设置 -->
            <div class="menu-group">
              <div class="menu-header" @click="toggleMenu('settings')">
                <el-icon><Setting /></el-icon>
                <span>账户设置</span>
                <el-icon class="arrow" :class="{ expanded: expandedMenus.settings }"><ArrowDown /></el-icon>
              </div>
              <div class="submenu" v-show="expandedMenus.settings">
                <div class="submenu-item" :class="{ active: activeMenu === 'profile' }" @click="switchMenu('profile')">
                  个人资料
                </div>
                <div class="submenu-item" :class="{ active: activeMenu === 'address' }" @click="switchMenu('address')">
                  收货地址
                </div>
                <div class="submenu-item" :class="{ active: activeMenu === 'security' }" @click="switchMenu('security')">
                  账号与安全
                </div>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="menu-item" @click="switchToSecondhandProfile">
              <el-icon><User /></el-icon>
              <span>返回易淘</span>
            </div>

            <div class="menu-item" :class="{ active: activeMenu === 'verified-orders' }" @click="switchMenu('verified-orders')">
              <el-icon><ShoppingCart /></el-icon>
              <span>官方验订单</span>
            </div>

            <div class="menu-item" :class="{ active: activeMenu === 'verified-favorites' }" @click="switchMenu('verified-favorites')">
              <el-icon><Star /></el-icon>
              <span>收藏/想要</span>
            </div>

            <div class="menu-item" :class="{ active: activeMenu === 'verified-history' }" @click="switchMenu('verified-history')">
              <el-icon><Clock /></el-icon>
              <span>浏览记录</span>
            </div>

            <div class="menu-item" :class="{ active: activeMenu === 'verified-recycle' }" @click="switchMenu('verified-recycle')">
              <el-icon><Tickets /></el-icon>
              <span>我的回收订单</span>
            </div>

            <div class="menu-item" :class="{ active: activeMenu === 'verified-service' }" @click="switchMenu('verified-service')">
              <el-icon><Headset /></el-icon>
              <span>联系客服</span>
            </div>
          </template>
        </div>
      </div>

      <!-- 右侧主体内容 -->
      <div class="main-content">
        <!-- 用户信息头部（仅在首页/发布显示） -->
        <div class="user-header" v-if="activeMenu === 'home' || activeMenu === 'published'">
          <div class="user-header-bg"></div>
          <div class="user-info-wrapper">
            <div class="user-avatar-section">
            <el-avatar :size="80" class="user-avatar" :src="authStore.user?.avatar">
              {{ authStore.user?.username?.[0]?.toUpperCase() || '用' }}
            </el-avatar>
          </div>
            <div class="user-details">
              <div class="user-name-row">
                <span class="user-name">{{ authStore.user?.username }}</span>
                <span class="user-badge seller">🏆 卖家信用优秀</span>
                <span class="user-badge buyer">⭐ 买家信用极好</span>
                <div class="edit-profile-btn">
                  <el-button @click="showEditModal = true" size="small" plain>编辑资料</el-button>
                </div>
              </div>
              <div class="user-stats">
                <span class="stat-item">
                  <el-icon><Location /></el-icon>
                  {{ userLocation || '未设置' }}
                </span>
                <span class="stat-divider">|</span>
                <span class="stat-item">{{ stats.followers || 0 }}粉丝</span>
                <span class="stat-divider">|</span>
                <span class="stat-item">{{ stats.following || 0 }}关注</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 我发布的 / 我的易淘 -->
        <div class="content-section" v-if="activeMenu === 'home' || activeMenu === 'published'">
          <div class="section-header">
            <h2 class="section-title">我发布的宝贝</h2>
            <span class="section-count">共 {{ productsTotal }} 件</span>
          </div>
          <div class="seller-toolbar">
            <div class="seller-tabs">
              <button
                class="tab-btn"
                :class="{ active: productsStatusFilter === 'all' }"
                @click="setProductsStatus('all')"
              >
                全部
              </button>
              <button
                class="tab-btn"
                :class="{ active: productsStatusFilter === 'active' }"
                @click="setProductsStatus('active')"
              >
                在售
              </button>
              <button
                class="tab-btn"
                :class="{ active: productsStatusFilter === 'pending' }"
                @click="setProductsStatus('pending')"
              >
                审核中
              </button>
              <button
                class="tab-btn"
                :class="{ active: productsStatusFilter === 'sold' }"
                @click="setProductsStatus('sold')"
              >
                已售
              </button>
              <button
                class="tab-btn"
                :class="{ active: productsStatusFilter === 'removed' }"
                @click="setProductsStatus('removed')"
              >
                已下架
              </button>
            </div>
          </div>
          <div v-if="loading" class="loading-wrapper">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="products.length === 0" class="empty-wrapper">
            <el-empty description="暂无发布的宝贝">
              <el-button type="warning" @click="$router.push('/publish')">去发布</el-button>
            </el-empty>
          </div>
          <div v-else class="products-grid">
            <div v-for="product in products" :key="product.id" class="product-card" @click="$router.push(`/products/${product.id}`)">
              <div class="product-image">
                <img v-if="product.images?.length" :src="getImageUrl(product.images[0].image)" :alt="product.title" />
                <el-icon v-else class="no-image"><PictureFilled /></el-icon>
                <div
                  v-if="product.status === 'sold' || product.status === 'removed' || product.status === 'pending'"
                  class="status-overlay"
                >
                  <span>
                    {{
                      product.status === 'sold'
                        ? '卖掉了'
                        : product.status === 'removed'
                          ? '已下架'
                          : '正在审核'
                    }}
                  </span>
                </div>
              </div>
              <div class="product-info">
                <div class="product-title">{{ product.title }}</div>
                <div class="product-price">¥{{ product.price }}</div>
                <div class="product-footer">
                  <span v-if="product.status === 'sold'" class="status-pill sold">已售</span>
                  <span v-else-if="product.status === 'pending'" class="status-pill pending">审核中</span>
                  <span v-else-if="product.status === 'removed'" class="status-pill removed">已下架</span>
                </div>
                <div v-if="product.status === 'removed' && product.removed_reason" class="removed-reason">
                  下架原因：{{ product.removed_reason }}
                </div>
              </div>
            </div>
          </div>
          <div v-if="productsTotal > productsPagination.pageSize" class="pagination-wrapper">
            <el-pagination
              v-model:current-page="productsPagination.current"
              :total="productsTotal"
              :page-size="productsPagination.pageSize"
              layout="prev, pager, next"
              background
              @current-change="handleProductsPageChange"
            />
          </div>
        </div>

        <!-- 我卖出的 / 我买到的 订单列表 -->
        <div class="orders-section" v-if="activeMenu === 'sold' || activeMenu === 'bought'">
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
          <div class="orders-list-wrapper">
            <div v-if="loading" class="loading-wrapper">
              <el-skeleton :rows="3" animated />
            </div>
            <div v-else-if="filteredOrders.length === 0" class="empty-wrapper">
              <el-empty :description="activeMenu === 'sold' ? '暂无卖出的订单' : '暂无购买记录'">
                <el-button v-if="activeMenu === 'bought'" type="warning" @click="$router.push('/')">去逛逛</el-button>
              </el-empty>
            </div>
            <div v-else class="orders-list">
              <div v-for="order in filteredOrders" :key="order.id" class="order-card-large">
                <!-- 订单头部：卖家/买家信息 + 状态 -->
                <div class="order-card-header">
                  <div class="seller-info">
                    <el-avatar :size="24">
                      {{ activeMenu === 'bought' ? order.product?.seller?.username?.[0] : order.buyer?.username?.[0] }}
                    </el-avatar>
                    <span class="seller-name">
                      {{ activeMenu === 'bought' ? order.product?.seller?.username : order.buyer?.username }}
                    </span>
                    <el-tag size="small" type="warning" v-if="order.product?.seller?.id === authStore.user?.id || order.buyer?.id === authStore.user?.id">
                      {{ activeMenu === 'bought' ? '卖家' : '买家' }}
                    </el-tag>
                  </div>
                  <div class="order-status-text" :class="getStatusClass(order.status)">
                    {{ getOrderStatusLabel(order.status) }}
                  </div>
                  <div v-if="activeMenu==='sold' && order.settlement_status" class="settlement-summary">
                    <el-tag :type="order.settlement_status==='settled'?'success':(order.settlement_status==='failed'?'danger':'warning')" size="small">
                      {{ order.settlement_status==='settled'?'已结算到账':(order.settlement_status==='failed'?'结算失败':'待结算') }}
                    </el-tag>
                    <el-tag v-if="order.settlement_method" :type="order.settlement_method==='TRANSFER'?'warning':'success'" size="small" style="margin-left:6px">
                      {{ order.settlement_method==='TRANSFER'?'转账代结算':'分账结算' }}
                    </el-tag>
                    <span v-if="order.settlement_account" class="settlement-account">到账：{{ order.settlement_account }}</span>
                  </div>
                </div>

                <!-- 订单内容：商品信息 -->
                <div class="order-card-body" @click="$router.push(`/order/${order.id}`)">
                  <div class="order-product-image">
                    <img v-if="order.product?.images?.length" :src="getImageUrl(order.product.images[0].image)" />
                    <el-icon v-else><PictureFilled /></el-icon>
                  </div>
                  <div class="order-product-info">
                    <div class="order-product-title">{{ order.product?.title }}</div>
                    <div class="order-product-desc">{{ order.product?.description?.slice(0, 50) }}...</div>
                    <div class="order-product-price">¥{{ order.product?.price }}</div>
                  </div>
                  <el-button class="more-btn" size="small" plain>更多</el-button>
                </div>

                <!-- 订单底部：操作按钮 -->
                <div class="order-card-footer">
                  <div class="order-time">{{ formatDate(order.created_at) }}</div>
                  <div class="order-actions">
                    <el-button size="small" plain @click.stop="handleContact(order)">
                      {{ activeMenu === 'bought' ? '联系卖家' : '联系买家' }}
                    </el-button>
                    
                    <!-- 买家操作 -->
                    <template v-if="activeMenu === 'bought'">
                      <el-button v-if="order.status === 'pending'" size="small" type="warning" @click.stop="handlePay(order)">
                        立即付款
                      </el-button>
                      <el-button v-if="order.status === 'shipped'" size="small" type="warning" @click.stop="handleConfirmReceive(order)">
                        确认收货
                      </el-button>
                      <el-button v-if="order.status === 'completed'" size="small" plain @click.stop="handleBuyAgain(order)">
                        再次购买
                      </el-button>
                    </template>
                    
                    <!-- 卖家操作 -->
                    <template v-if="activeMenu === 'sold'">
                      <el-button v-if="order.status === 'paid'" size="small" type="warning" @click.stop="handleShip(order)">
                        发货
                      </el-button>
                      <el-button size="small" plain @click.stop="$router.push(`/order/${order.id}`)">
                        查看详情
                      </el-button>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 官方验：订单 -->
        <div class="orders-section" v-if="activeMenu === 'verified-orders'">
          <div class="section-header">
            <h2 class="section-title">官方验订单</h2>
          </div>

          <div class="order-search-bar">
            <el-input
              v-model="verifiedOrderSearch"
              clearable
              placeholder="搜索订单号 / 商品标题 / 卖家"
            />
          </div>

          <div class="order-status-tabs">
            <div
              v-for="tab in orderStatusTabs"
              :key="tab.value"
              class="status-tab"
              :class="{ active: verifiedCurrentOrderStatus === tab.value }"
              @click="filterVerifiedOrdersByStatus(tab.value)"
            >
              {{ tab.label }}<span v-if="getVerifiedOrderStatusCount(tab.value) > 0">({{ getVerifiedOrderStatusCount(tab.value) }})</span>
            </div>
          </div>

          <div class="orders-list-wrapper">
            <div v-if="loading" class="loading-wrapper">
              <el-skeleton :rows="3" animated />
            </div>
            <div v-else-if="filteredVerifiedOrders.length === 0" class="empty-wrapper">
              <el-empty description="暂无官方验订单">
                <el-button type="primary" @click="openVerifiedProducts">去逛逛官方验</el-button>
              </el-empty>
            </div>
          <div v-else class="orders-list">
            <div v-for="order in filteredVerifiedOrders" :key="order.id" class="order-card-large">
                <div class="order-card-header">
                  <div class="seller-info">
                    <el-avatar :size="24" :src="order.product?.seller?.avatar">
                      {{ order.product?.seller?.username?.[0]?.toUpperCase() || 'X' }}
                    </el-avatar>
                    <span class="seller-name">{{ order.product?.seller?.username || '匿名用户' }}</span>
                    <el-tag size="small" type="warning">卖家</el-tag>
                  </div>
                  <div class="order-status-text" :class="getStatusClass(order.status)">
                    {{ getVerifiedOrderStatusLabel(order.status) }}
                  </div>
                </div>

                <div class="order-card-body" @click="goToVerifiedOrderDetail(order.id)">
                  <div class="order-product-image">
                    <img v-if="order.product?.images?.length" :src="getImageUrl(order.product.images[0].image)" />
                    <el-icon v-else><PictureFilled /></el-icon>
                  </div>
                  <div class="order-product-info">
                    <div class="order-product-title">{{ order.product?.title || '商品已下架' }}</div>
                    <div class="order-product-desc">{{ order.product?.description?.slice(0, 50) }}...</div>
                    <div class="order-product-price">￥{{ order.total_price }}</div>
                  </div>
                  <el-button class="more-btn" size="small" plain>更多</el-button>
                </div>

                <div class="order-card-footer">
                  <div class="order-time">{{ formatDate(order.created_at) }}</div>
                  <div class="order-actions">
                    <el-button size="small" plain @click.stop="handleContactVerifiedSeller(order)">联系卖家</el-button>
                    <el-button v-if="order.status === 'pending' || order.status === 'paid'" size="small" plain @click.stop="handleVerifiedCancel(order)">取消订单</el-button>
                    <el-button v-if="order.status === 'pending'" size="small" type="warning" @click.stop="handleVerifiedPay(order)">立即付款</el-button>
                    <el-button v-if="order.status === 'shipped'" size="small" type="warning" @click.stop="handleVerifiedConfirmReceive(order)">确认收货</el-button>
                    <el-button size="small" plain @click.stop="goToVerifiedOrderDetail(order.id)">查看详情</el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 官方验：收藏 -->
        <div class="content-section" v-if="activeMenu === 'verified-favorites'">
          <div class="section-header">
            <h2 class="section-title">官方验收藏</h2>
            <span class="section-count">共 {{ verifiedFavorites.length }} 件</span>
          </div>

          <div v-if="loading" class="loading-wrapper">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="verifiedFavorites.length === 0" class="empty-wrapper">
            <el-empty description="暂无收藏">
              <el-button type="primary" @click="openVerifiedProducts">去逛逛官方验</el-button>
            </el-empty>
          </div>
          <div v-else class="products-grid">
            <div
              v-for="fav in verifiedFavorites"
              :key="fav.id"
              class="product-card"
              @click="goToVerifiedProductDetail(fav.product?.id)"
            >
              <div class="product-image">
                <img v-if="fav.product?.images?.length" :src="getImageUrl(fav.product.images[0].image)" :alt="fav.product?.title" />
                <el-icon v-else class="no-image"><PictureFilled /></el-icon>
              </div>
              <div class="product-info">
                <div class="product-title">{{ fav.product?.title }}</div>
                <div class="product-price">￥{{ fav.product?.price }}</div>
                <div style="margin-top:8px;">
                  <el-button size="small" plain @click.stop="removeVerifiedFavorite(fav)">取消收藏</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 官方验：浏览记录 -->
        <div class="content-section" v-if="activeMenu === 'verified-history'">
          <div class="section-header">
            <h2 class="section-title">官方验浏览记录</h2>
            <div class="header-actions">
              <span class="section-count">共 {{ verifiedBrowseHistory.length }} 条</span>
              <el-button v-if="verifiedBrowseHistory.length > 0" size="small" text @click="clearVerifiedBrowseHistory">清空</el-button>
            </div>
          </div>

          <div v-if="verifiedBrowseHistory.length === 0" class="empty-wrapper">
            <el-empty description="暂无浏览记录">
              <el-button type="primary" @click="openVerifiedProducts">去逛逛官方验</el-button>
            </el-empty>
          </div>
          <div v-else class="history-list">
            <div
              v-for="(item, index) in verifiedBrowseHistory"
              :key="`${item.productId}_${item.timestamp}`"
              class="history-item"
              @click="goToVerifiedProductDetail(item.productId)"
            >
              <img :src="item.image || defaultImage" class="history-image" />
              <div class="history-info">
                <div class="history-title">{{ item.title }}</div>
                <div class="history-meta">
                  <span class="history-price">￥{{ item.price }}</span>
                  <span class="history-time">{{ formatBrowseTime(item.timestamp) }}</span>
                </div>
              </div>
              <el-button class="history-remove" size="small" text @click.stop="removeVerifiedHistoryItem(index)">删除</el-button>
            </div>
          </div>
        </div>

        <!-- 官方验：客服 -->
        <div class="content-section" v-if="activeMenu === 'verified-service'">
          <div class="section-header">
            <h2 class="section-title">联系客服</h2>
          </div>

          <el-card shadow="never" style="margin-bottom: 16px;">
            <div style="display:flex; gap:12px; flex-wrap: wrap; align-items:center;">
              <el-button type="primary" plain @click="openOnlineChat">在线客服</el-button>
              <el-button type="success" plain @click="openPhoneService">客服电话</el-button>
              <el-button type="info" plain @click="openEmailService">邮件支持</el-button>
              <span style="color:#999;">常见问题在下方</span>
            </div>
          </el-card>

          <el-card shadow="never">
            <div v-for="(faq, idx) in verifiedFaqList" :key="idx" class="faq-item">
              <div class="faq-q" @click="toggleVerifiedFaq(idx)">{{ faq.question }}</div>
              <div v-if="faq.expanded" class="faq-a">{{ faq.answer }}</div>
            </div>
          </el-card>
        </div>

        <!-- 官方验：回收订单（内嵌） -->
        <div class="orders-section" v-if="activeMenu === 'verified-recycle'">
          <div class="section-header">
            <h2 class="section-title">我的回收订单</h2>
          </div>

          <div class="order-search-bar">
            <el-input
              v-model="verifiedRecycleSearch"
              clearable
              placeholder="搜索订单号 / 品牌 / 机型"
            />
          </div>

          <div class="order-status-tabs">
            <div
              v-for="tab in verifiedRecycleStatusTabs"
              :key="tab.value"
              class="status-tab"
              :class="{ active: verifiedRecycleStatus === tab.value }"
              @click="filterVerifiedRecycleByStatus(tab.value)"
            >
              {{ tab.label }}<span v-if="getVerifiedRecycleStatusCount(tab.value) > 0">({{ getVerifiedRecycleStatusCount(tab.value) }})</span>
            </div>
          </div>

          <div class="orders-list-wrapper">
            <div v-if="loading" class="loading-wrapper">
              <el-skeleton :rows="3" animated />
            </div>
            <div v-else-if="filteredVerifiedRecycleOrders.length === 0" class="empty-wrapper">
              <el-empty description="暂无回收订单">
                <el-button type="warning" @click="$router.push('/recycle')">去回收</el-button>
              </el-empty>
            </div>
            <div v-else class="orders-list">
              <div
                v-for="order in filteredVerifiedRecycleOrders"
                :key="order.id"
                class="order-card-large"
                @click="$router.push(`/recycle-order/${order.id}`)"
              >
                <div class="order-card-header">
                  <div class="seller-info">
                    <span class="seller-name">回收单号：{{ order.id }}</span>
                  </div>
                  <div class="order-status-text" :class="getRecycleStatusClass(order)">
                    {{ getRecycleStatusText(order) }}
                  </div>
                </div>

                <div class="order-card-body">
                  <div class="order-product-info" style="padding: 8px 0;">
                    <div class="order-product-title">{{ order.brand }} {{ order.model }}</div>
                    <div class="order-product-desc">
                      {{ order.device_type }} · {{ getConditionText(order.condition) }}<span v-if="order.storage"> · {{ order.storage }}</span>
                    </div>
                    <div class="order-product-price">
                      <span v-if="order.final_price">￥{{ order.final_price }}</span>
                      <span v-else-if="order.estimated_price">￥{{ order.estimated_price }}</span>
                      <span v-else>—</span>
                    </div>
                  </div>
                </div>

                <div class="order-card-footer">
                  <div class="order-time">{{ formatDate(order.created_at) }}</div>
                  <div class="order-actions">
                    <el-button size="small" plain @click.stop="$router.push(`/recycle-order/${order.id}`)">查看详情</el-button>
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
          <div v-if="loading" class="loading-wrapper">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="favorites.length === 0" class="empty-wrapper">
            <el-empty description="暂无收藏">
              <el-button type="warning" @click="$router.push('/')">去逛逛</el-button>
            </el-empty>
          </div>
          <div v-else class="products-grid">
            <div v-for="fav in favorites" :key="fav.id" class="product-card" @click="$router.push(`/products/${fav.product?.id}`)">
              <div class="product-image">
                <img v-if="fav.product?.images?.length" :src="getImageUrl(fav.product.images[0].image)" :alt="fav.product?.title" />
                <el-icon v-else class="no-image"><PictureFilled /></el-icon>
              </div>
              <div class="product-info">
                <div class="product-title">{{ fav.product?.title }}</div>
                <div class="product-price">¥{{ fav.product?.price }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 个人资料 -->
        <div class="content-section profile-section" v-if="activeMenu === 'profile'">
          <div class="section-header">
            <h2 class="section-title">个人资料</h2>
          </div>
          <el-form :model="editForm" label-width="100px" class="profile-form">
            <el-form-item label="头像">
              <div class="avatar-upload">
                <el-avatar :size="64" :src="tempAvatarUrl || authStore.user?.avatar">
                  {{ authStore.user?.username?.[0]?.toUpperCase() || '用' }}
                </el-avatar>
                <input
                  type="file"
                  id="avatar-upload"
                  ref="avatarInput"
                  style="display: none"
                  accept="image/*"
                  @change="handleAvatarChange"
                >
                <el-button size="small" style="margin-left: 16px;" @click="triggerAvatarUpload">更换头像</el-button>
              </div>
            </el-form-item>
            <el-form-item label="用户名">
              <el-input v-model="editForm.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="editForm.email" type="email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="所在地">
              <div class="location-row">
                <el-cascader
                  v-model="locationValue"
                  :options="locationOptions"
                  :props="locationProps"
                  clearable
                  filterable
                  placeholder="请选择省/市/区"
                  class="location-cascader"
                />
                <el-button type="primary" plain :loading="locating" @click="handleLocate">自动获取</el-button>
              </div>
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input v-model="editForm.bio" type="textarea" :rows="3" placeholder="介绍一下自己吧~" :maxlength="200" show-word-limit />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" @click="handleUpdateProfile" :loading="updateLoading">保存修改</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 收货地址 -->
        <div class="content-section address-section" v-if="activeMenu === 'address'">
          <div class="section-header">
            <h2 class="section-title">收货地址</h2>
            <el-button type="primary" size="small" @click="openAddressModal('add')">新增地址</el-button>
          </div>
          
          <div v-if="loading" class="loading-wrapper">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="addresses.length === 0" class="empty-wrapper">
            <el-empty description="暂无收货地址" />
          </div>
          <div v-else class="address-list">
            <div v-for="addr in addresses" :key="addr.id" class="address-card">
              <div class="address-info">
                <div class="addr-row">
                  <span class="addr-name">{{ addr.name }}</span>
                  <span class="addr-phone">{{ addr.phone }}</span>
                  <el-tag v-if="addr.is_default" size="small" type="danger" effect="plain">默认</el-tag>
                </div>
                <div class="addr-detail">
                  {{ addr.province }} {{ addr.city }} {{ addr.district }} {{ addr.detail_address }}
                </div>
              </div>
              <div class="address-actions">
                <el-button type="primary" link @click="openAddressModal('edit', addr)">编辑</el-button>
                <el-button type="danger" link @click="handleDeleteAddress(addr.id)">删除</el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 账号与安全 -->
        <div class="content-section security-section" v-if="activeMenu === 'security'">
          <div class="section-header">
            <h2 class="section-title">账号与安全</h2>
          </div>
          <el-form :model="passwordForm" label-width="100px" class="security-form">
            <el-form-item label="原密码" required>
              <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入原密码" />
            </el-form-item>
            <el-form-item label="新密码" required>
              <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="请输入新密码（至少6位）" />
            </el-form-item>
            <el-form-item label="确认密码" required>
              <el-input v-model="passwordForm.new_password2" type="password" show-password placeholder="请再次输入新密码" />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" @click="handleChangePassword" :loading="passwordLoading">修改密码</el-button>
            </el-form-item>
          </el-form>
          <el-divider />
          <div class="logout-section">
            <el-button type="danger" @click="handleLogout">退出登录</el-button>
          </div>
        </div>

        <!-- 钱包余额 -->
        

        <!-- 交易记录 -->
        <div class="content-section wallet-transactions-section" v-if="activeMenu === 'wallet-transactions'">
          <div class="section-header">
            <h2 class="section-title">交易记录</h2>
            <el-button text @click="loadWalletTransactions">刷新</el-button>
          </div>
          <div v-if="loading" class="loading-wrapper">
            <el-skeleton :rows="5" animated />
          </div>
          <div v-else-if="walletTransactions.length === 0" class="empty-wrapper">
            <el-empty description="暂无交易记录" />
          </div>
          <div v-else>
            <el-table :data="walletTransactions" style="width: 100%">
              <el-table-column prop="created_at" label="时间" width="180">
                <template #default="{ row }">
                  {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="transaction_type_display" label="类型" width="120">
                <template #default="{ row }">
                  <el-tag :type="getTransactionType(row.transaction_type)">
                    {{ getTransactionTypeLabel(row) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="金额" width="120">
                <template #default="{ row }">
                  <span :class="row.amount >= 0 ? 'amount-income' : 'amount-expense'">
                    {{ row.amount >= 0 ? '+' : '' }}¥{{ Math.abs(row.amount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="note" label="备注" min-width="200">
                <template #default="{ row }">
                  {{ formatTransactionNote(row) }}
                </template>
              </el-table-column>
              
            </el-table>
            <div v-if="walletTransactionsTotal > walletTransactions.length" style="text-align: center; margin-top: 16px">
              <el-button @click="loadMoreTransactions">加载更多</el-button>
            </div>
          </div>
        </div>

        <!-- 提现 -->
        

        <!-- 绑定支付宝 -->
        <div class="content-section wallet-bind-section" v-if="activeMenu === 'wallet-bind'">
          <div class="section-header">
            <h2 class="section-title">绑定支付宝账户</h2>
            <el-button text @click="loadUserInfo">刷新</el-button>
          </div>
          <el-card class="bind-card">
            <el-alert
              type="info"
              :closable="false"
              style="margin-bottom: 20px"
            >
              <template #title>
                <div>绑定后，买家确认收货时的分账将直接打到该支付宝账户</div>
              </template>
            </el-alert>
            <el-form :model="bindForm" label-width="120px" style="max-width: 600px">
              <el-form-item label="支付宝登录账号" required>
                <el-input v-model="bindForm.alipay_login_id" placeholder="请输入支付宝登录账号（手机号或邮箱）" />
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  该账号用于分账收款，请确保为您的支付宝登录账号
                </div>
              </el-form-item>
              <el-form-item label="支付宝姓名">
                <el-input v-model="bindForm.alipay_real_name" placeholder="请输入支付宝真实姓名（可选，建议填写）" />
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  填写真实姓名有助于提高分账成功率
                </div>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="binding" @click="handleBindAlipay">保存绑定</el-button>
                <el-button @click="loadUserInfo">刷新</el-button>
              </el-form-item>
            </el-form>
            <div v-if="bindForm.alipay_login_id" style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 4px; border: 1px solid #b3d8ff">
              <div style="font-size: 14px; font-weight: 500; margin-bottom: 8px; color: #409eff">当前绑定信息</div>
              <div style="font-size: 13px; color: #606266">
                <div>支付宝账号：{{ bindForm.alipay_login_id }}</div>
                <div v-if="bindForm.alipay_real_name">支付宝姓名：{{ bindForm.alipay_real_name }}</div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 编辑资料对话框 -->
    <el-dialog v-model="showEditModal" title="编辑个人资料" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="头像">
          <div class="avatar-upload">
            <el-avatar :size="64" :src="tempAvatarUrl || authStore.user?.avatar">
              {{ authStore.user?.username?.[0]?.toUpperCase() || '用' }}
            </el-avatar>
            <input
              type="file"
              id="avatar-upload-dialog"
              ref="avatarInputDialog"
              style="display: none"
              accept="image/*"
              @change="handleAvatarChange"
            >
            <el-button size="small" style="margin-left: 16px;" @click="triggerAvatarUpload">更换头像</el-button>
          </div>
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="所在地">
          <div class="location-row">
            <el-cascader
              v-model="locationValue"
              :options="locationOptions"
              :props="locationProps"
              clearable
              filterable
              placeholder="请选择省/市/区"
              class="location-cascader"
            />
            <el-button type="primary" plain :loading="locating" @click="handleLocate">自动获取</el-button>
          </div>
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input v-model="editForm.bio" type="textarea" :rows="3" placeholder="介绍一下自己吧~" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditModal = false">取消</el-button>
        <el-button type="warning" @click="handleUpdateProfile" :loading="updateLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 地址编辑对话框 -->
    <el-dialog v-model="showAddressModal" :title="addressModalType === 'add' ? '新增收货地址' : '编辑收货地址'" width="500px">
      <el-form :model="addressForm" label-width="100px" ref="addressFormRef" :rules="addressRules">
        <el-form-item label="收货人" prop="name">
          <el-input v-model="addressForm.name" placeholder="请输入收货人姓名" />
        </el-form-item>
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="addressForm.phone" placeholder="请输入手机号码" />
        </el-form-item>
        <el-form-item label="所在地区" required>
          <div style="display: flex; gap: 10px;">
            <el-input v-model="addressForm.province" placeholder="省" />
            <el-input v-model="addressForm.city" placeholder="市" />
            <el-input v-model="addressForm.district" placeholder="区/县" />
          </div>
        </el-form-item>
        <el-form-item label="详细地址" prop="detail_address">
          <el-input v-model="addressForm.detail_address" type="textarea" placeholder="请输入详细地址" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="addressForm.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddressModal = false">取消</el-button>
        <el-button type="primary" @click="handleSaveAddress" :loading="addressLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, ShoppingBag, Star, Setting, ArrowDown, Location, PictureFilled, Wallet, DocumentChecked, ShoppingCart, Clock, Tickets, Headset } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import { getRecycleStatusTag } from '@/utils/recycleFlow'
import { getResults, getCount } from '@/utils/responseGuard'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

let suppressRouteSync = false

const isVerifiedZone = computed(() => route.query?.zone === 'verified' || String(route.query?.tab || '').startsWith('verified-'))
const defaultImage = 'https://via.placeholder.com/200x200?text=No+Image'

// 菜单状态
const activeMenu = ref('home')
const expandedMenus = reactive({
  trade: true,
  wallet: true,
  settings: true
})

const goToVerifiedProfile = () => {
  router.push('/profile?zone=verified&tab=verified-orders')
}

// 头像上传相关
const avatarInput = ref(null)
const avatarInputDialog = ref(null)
const tempAvatarFile = ref(null)
const tempAvatarUrl = ref(null)

// 订单状态筛选
const currentOrderStatus = ref('all')
const orderStatusTabs = [
  { label: '全部', value: 'all' },
  { label: '待付款', value: 'pending' },
  { label: '待发货', value: 'paid' },
  { label: '待收货', value: 'shipped' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
]

// 官方验（合并到个人中心内）
const verifiedCurrentOrderStatus = ref('all')
const verifiedOrderSearch = ref('')
const verifiedOrders = ref([])
const verifiedFavorites = ref([])
const verifiedBrowseHistory = ref([])

const verifiedRecycleStatus = ref('all')
const verifiedRecycleSearch = ref('')
const verifiedRecycleOrders = ref([])
const verifiedRecycleStatusTabs = [
  { label: '全部', value: 'all' },
  { label: '待寄出', value: 'to_ship' },
  { label: '待确认价格', value: 'price_confirm' },
  { label: '已完成', value: 'completed' }
]

const verifiedFaqList = ref([
  {
    question: '什么是官方验货？',
    answer: '官方验货是指平台对商品进行专业质检，确保成色、功能、真伪符合描述。',
    expanded: false
  },
  {
    question: '官方验货支持哪些成色？',
    answer: '通常为全新、99成新、95成新（以商品详情为准）。',
    expanded: false
  },
  {
    question: '如何申请售后/退款？',
    answer: '请在订单详情页发起申请，或联系在线客服协助处理。',
    expanded: false
  }
])

const verifiedOrderStats = computed(() => ({
  total: verifiedOrders.value.length,
  pending: verifiedOrders.value.filter(o => o.status === 'pending').length,
  paid: verifiedOrders.value.filter(o => o.status === 'paid').length,
  shipped: verifiedOrders.value.filter(o => o.status === 'shipped').length,
  completed: verifiedOrders.value.filter(o => o.status === 'completed').length,
  cancelled: verifiedOrders.value.filter(o => o.status === 'cancelled').length
}))

const getVerifiedOrderStatusCount = (status) => {
  if (status === 'all') return verifiedOrderStats.value.total
  return verifiedOrderStats.value[status] || 0
}

const verifiedRecycleStats = computed(() => ({
  total: verifiedRecycleOrders.value.length,
  to_ship: verifiedRecycleOrders.value.filter(o => o.status === 'pending').length,
  price_confirm: verifiedRecycleOrders.value.filter(o => Boolean(o.final_price) && !o.final_price_confirmed && o.status !== 'cancelled' && o.status !== 'completed').length,
  completed: verifiedRecycleOrders.value.filter(o => o.status === 'completed').length
}))

const getVerifiedRecycleStatusCount = (status) => {
  if (status === 'all') return verifiedRecycleStats.value.total
  return verifiedRecycleStats.value[status] || 0
}

const filteredVerifiedOrders = computed(() => {
  const kw = verifiedOrderSearch.value.trim().toLowerCase()
  const list = verifiedCurrentOrderStatus.value === 'all'
    ? verifiedOrders.value
    : verifiedOrders.value.filter(order => order.status === verifiedCurrentOrderStatus.value)

  if (!kw) return list
  return list.filter((order) => {
    const idText = String(order.id || '').toLowerCase()
    const titleText = String(order.product?.title || '').toLowerCase()
    const sellerText = String(order.product?.seller?.username || '').toLowerCase()
    return idText.includes(kw) || titleText.includes(kw) || sellerText.includes(kw)
  })
})

const filteredVerifiedRecycleOrders = computed(() => {
  const kw = verifiedRecycleSearch.value.trim().toLowerCase()

  const statusFiltered = (() => {
    switch (verifiedRecycleStatus.value) {
      case 'to_ship':
        return verifiedRecycleOrders.value.filter(order => order.status === 'pending')
      case 'price_confirm':
        return verifiedRecycleOrders.value.filter(order =>
          Boolean(order.final_price) &&
          !order.final_price_confirmed &&
          order.status !== 'cancelled' &&
          order.status !== 'completed'
        )
      case 'completed':
        return verifiedRecycleOrders.value.filter(order => order.status === 'completed')
      case 'all':
      default:
        return verifiedRecycleOrders.value
    }
  })()

  if (!kw) return statusFiltered
  return statusFiltered.filter((order) => {
    const idText = String(order.id || '').toLowerCase()
    const brandText = String(order.brand || '').toLowerCase()
    const modelText = String(order.model || '').toLowerCase()
    return idText.includes(kw) || brandText.includes(kw) || modelText.includes(kw)
  })
})

// 数据
const loading = ref(false)
const products = ref([])
const productsTotal = ref(0)
const productsStatusFilter = ref('all')
const productsStatusQuery = computed(() => {
  if (productsStatusFilter.value === 'all') return 'active,pending,sold,removed'
  return productsStatusFilter.value
})
const productsPagination = ref({
  current: 1,
  pageSize: 20,
  total: 0,
})
const allOrders = ref([])
const favorites = ref([])
const addresses = ref([])
const userLocation = ref('未设置')

// 钱包相关数据
const walletTransactions = ref([])
const walletTransactionsTotal = ref(0)
const walletTransactionsPage = ref(1)
const walletTransactionsPageSize = ref(20)
const binding = ref(false)
const bindForm = reactive({
  alipay_login_id: '',
  alipay_real_name: ''
})

const stats = reactive({
  products: 0,
  sold: 0,
  bought: 0,
  favorites: 0,
  followers: 0,
  following: 0
})

// 对话框
const showEditModal = ref(false)
const updateLoading = ref(false)
const passwordLoading = ref(false)

const editForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  location: '',
  bio: ''
})
const locating = ref(false)
const locationOptions = ref([])
const locationValue = ref([])

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  new_password2: ''
})

// 地址相关
const showAddressModal = ref(false)
const addressModalType = ref('add')
const addressLoading = ref(false)
const addressFormRef = ref(null)
const addressForm = reactive({
  id: null,
  name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detail_address: '',
  is_default: false
})

const addressRules = {
  name: [{ required: true, message: '请输入收货人姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号码', trigger: 'blur' }],
  detail_address: [{ required: true, message: '请输入详细地址', trigger: 'blur' }]
}

const locationProps = {
  lazy: true,
  lazyLoad: async (node, resolve) => {
    try {
      const keyword = node.level === 0 ? '中国' : node.value
      const res = await api.get('/geo/districts/', {
        params: { keywords: keyword, subdistrict: 1 }
      })
      const districts = res.data?.districts?.[0]?.districts || []
      const options = districts.map((d) => ({
        label: d.name,
        value: d.name,
        leaf: !d.districts || d.districts.length === 0,
      }))
      resolve(options)
    } catch (error) {
      resolve([])
    }
  },
}

const loadRootDistricts = async () => {
  try {
    const res = await api.get('/geo/districts/', {
      params: { keywords: '中国', subdistrict: 1 }
    })
    const districts = res.data?.districts?.[0]?.districts || []
    locationOptions.value = districts.map((d) => ({
      label: d.name,
      value: d.name,
      leaf: false,
    }))
  } catch (error) {
    locationOptions.value = []
  }
}

const parseLocationToArray = (value) => {
  if (!value) return []
  const parts = []
  const province = value.match(/([^\s省市区县]+省|[^\s省市区县]+自治区|[^\s省市区县]+特别行政区)/)
  const city = value.match(/([^\s省市区县]+市)/)
  const district = value.match(/([^\s省市区县]+区|[^\s省市区县]+县)/)
  if (province) parts.push(province[1])
  if (city) parts.push(city[1])
  if (district) parts.push(district[1])
  if (parts.length === 0) return [value]
  return parts
}

watch(locationValue, (val) => {
  editForm.location = Array.isArray(val) ? val.join('') : ''
})

const fetchIpLocation = async () => {
  const res = await api.get('/geo/ip/')
  const data = res.data || {}
  const parts = [data.province, data.city].filter(Boolean)
  return parts.join('')
}

const handleLocate = async () => {
  if (locating.value) return
  if (!navigator.geolocation) {
    ElMessage.warning('当前浏览器不支持定位')
    return
  }

  locating.value = true
  try {
    const ipLocation = await fetchIpLocation()
    if (ipLocation) {
      locationValue.value = parseLocationToArray(ipLocation)
      ElMessage.info('已使用网络定位，正在尝试精准定位...')
    }
  } catch (error) {
    // 忽略网络定位失败
  }

  try {
    const position = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 8000,
        maximumAge: 300000,
      })
    })

    const { latitude, longitude } = position.coords
    const url = new URL('https://nominatim.openstreetmap.org/reverse')
    url.searchParams.set('format', 'jsonv2')
    url.searchParams.set('lat', latitude)
    url.searchParams.set('lon', longitude)
    url.searchParams.set('accept-language', 'zh-CN')

    const res = await fetch(url.toString())
    if (!res.ok) throw new Error('reverse geocode failed')
    const data = await res.json()
    const address = data.address || {}

    const rawParts = [
      address.state,
      address.city || address.town || address.village,
      address.city_district || address.suburb || address.county,
    ]
    const parts = []
    rawParts.forEach((part) => {
      if (!part) return
      const value = String(part).trim()
      if (!value || parts.includes(value)) return
      parts.push(value)
    })

    if (parts.length > 0) {
      locationValue.value = parts
    }
  } catch (error) {
    if (error && error.code === 1) {
      ElMessage.warning('定位权限被拒绝')
    } else if (error && (error.code === 2 || error.code === 3)) {
      ElMessage.warning('定位超时或不可用，请手动修正')
    } else {
      ElMessage.error('定位失败')
    }
  } finally {
    locating.value = false
  }
}

// 计算属性：根据当前菜单和状态筛选订单
const filteredOrders = computed(() => {
  let orders = []
  
  if (activeMenu.value === 'sold') {
    // 我卖出的：我是卖家
    orders = allOrders.value.filter(order => order.product?.seller?.id === authStore.user?.id)
  } else if (activeMenu.value === 'bought') {
    // 我买到的：我是买家
    orders = allOrders.value.filter(order => order.buyer?.id === authStore.user?.id)
  }
  
  // 按状态筛选
  if (currentOrderStatus.value !== 'all') {
    orders = orders.filter(order => order.status === currentOrderStatus.value)
  }
  
  return orders
})

const toggleMenu = (menu) => {
  expandedMenus[menu] = !expandedMenus[menu]
}

// 钱包相关方法
const loadWalletTransactions = async () => {
  loading.value = true
  try {
    const res = await api.get('/users/transactions/', {
      params: {
        page: walletTransactionsPage.value,
        page_size: walletTransactionsPageSize.value
      }
    })
    if (walletTransactionsPage.value === 1) {
      walletTransactions.value = res.data.transactions || []
    } else {
      walletTransactions.value.push(...(res.data.transactions || []))
    }
    walletTransactionsTotal.value = res.data.total || 0
  } catch (error) {
    ElMessage.error('加载交易记录失败')
  } finally {
    loading.value = false
  }
}

const loadMoreTransactions = () => {
  walletTransactionsPage.value++
  loadWalletTransactions()
}

const loadUserInfo = async () => {
  try {
    const res = await api.get('/users/me/')
    bindForm.alipay_login_id = res.data?.alipay_login_id || ''
    bindForm.alipay_real_name = res.data?.alipay_real_name || ''
  } catch (error) {
    console.error('????????:', error)
  }
}

const handleBindAlipay = async () => {
  if (!bindForm.alipay_login_id) {
    ElMessage.warning('??????????')
    return
  }
  try {
    binding.value = true
    const res = await api.patch('/users/me/', {
      alipay_login_id: bindForm.alipay_login_id,
      alipay_real_name: bindForm.alipay_real_name
    })
    ElMessage.success('????')
    if (res.data) {
      bindForm.alipay_login_id = res.data.alipay_login_id || bindForm.alipay_login_id
      bindForm.alipay_real_name = res.data.alipay_real_name || bindForm.alipay_real_name
    }
    if (authStore.user) {
      authStore.user.alipay_login_id = res.data?.alipay_login_id || ''
      authStore.user.alipay_real_name = res.data?.alipay_real_name || ''
      localStorage.setItem('user', JSON.stringify(authStore.user))
    }
  } catch (error) {
    const detail = error.response?.data?.detail || '????'
    ElMessage.error(detail)
  } finally {
    binding.value = false
  }
}

const getTransactionType = (type) => {
  const typeMap = {
    income: 'success',
    expense: 'danger',
    refund: 'warning',
    recycle: 'success'
  }
  return typeMap[type] || 'info'
}

const getTransactionTypeLabel = (row) => {
  const labelMap = {
    income: '收入',
    expense: '支出',
    refund: '退款',
    recycle: '回收'
  }
  return labelMap[row.transaction_type] || row.transaction_type_display || row.transaction_type || '-'
}

const formatTransactionNote = (row) => {
  if (!row.note) return '-'
  return row.note
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const switchMenu = (menu) => {
  activeMenu.value = menu
  if (menu === 'verified-orders') {
    verifiedCurrentOrderStatus.value = 'all'
  } else {
    currentOrderStatus.value = 'all'
  }
  if (menu === 'home' || menu === 'published') {
    productsPagination.value.current = 1
  }

  // 同步 URL，避免从详情页返回时被旧的 query.tab 覆盖到“我买到的”
  const query = { ...route.query }
  if (menu.startsWith('verified-')) {
    query.zone = 'verified'
    query.tab = menu
  } else {
    delete query.zone
    if (menu === 'home') {
      delete query.tab
    } else {
      query.tab = menu
    }
  }
  suppressRouteSync = true
  router.replace({ path: '/profile', query }).finally(() => {
    suppressRouteSync = false
  })

  loadContent(menu)
}

const filterOrdersByStatus = (status) => {
  currentOrderStatus.value = status
}

const filterVerifiedOrdersByStatus = (status) => {
  verifiedCurrentOrderStatus.value = status
}

const loadContent = async (menu) => {
  loading.value = true
  try {
    switch(menu) {
      case 'verified-orders':
        await loadVerifiedOrders()
        break
      case 'verified-favorites':
        await loadVerifiedFavorites()
        break
      case 'verified-history':
        loadVerifiedBrowseHistory()
        break
      case 'verified-recycle':
        await loadVerifiedRecycleOrders()
        break
      case 'verified-service':
        break
      case 'home':
      case 'published':
        await loadProducts()
        break
      case 'sold':
      case 'bought':
        await loadOrders()
        break
      case 'favorites':
        await loadFavorites()
        break
      case 'address':
        await loadAddresses()
        break
      case 'wallet-transactions':
        walletTransactionsPage.value = 1
        await loadWalletTransactions()
        break
      case 'wallet-bind':
        await loadUserInfo()
        break
    }
  } finally {
    loading.value = false
  }
}

const loadProducts = async () => {
  try {
    const res = await api.get('/products/', {
      params: {
        seller: authStore.user?.id,
        status: productsStatusQuery.value,
        page: productsPagination.value.current,
        page_size: productsPagination.value.pageSize,
        ordering: '-created_at',
      },
    })
    products.value = getResults(res.data)
    productsTotal.value = getCount(res.data)
    productsPagination.value.total = productsTotal.value
  } catch (error) {
    console.error('加载商品失败:', error)
    ElMessage.error(error?.response?.data?.detail || '加载商品失败')
    products.value = []
    productsTotal.value = 0
  } finally {
    stats.products = productsTotal.value
  }
}

const setProductsStatus = (status) => {
  if (productsStatusFilter.value === status) return
  productsStatusFilter.value = status
  productsPagination.value.current = 1
  if (activeMenu.value === 'home' || activeMenu.value === 'published') {
    loading.value = true
    loadProducts().finally(() => {
      loading.value = false
    })
  }
}

const handleProductsPageChange = (page) => {
  productsPagination.value.current = page
  if (activeMenu.value === 'home' || activeMenu.value === 'published') {
    loading.value = true
    loadProducts()
      .finally(() => {
        loading.value = false
      })
      .then(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      })
  }
}

const loadOrders = async () => {
  try {
    const res = await api.get('/orders/')
    allOrders.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载订单失败:', error)
  }
}

const loadVerifiedOrders = async () => {
  try {
    const res = await api.get('/verified-orders/')
    verifiedOrders.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载官方验订单失败:', error)
    verifiedOrders.value = []
    ElMessage.error('加载官方验订单失败')
  }
}

const loadFavorites = async () => {
  try {
    const res = await api.get('/favorites/')
    favorites.value = res.data?.results || res.data || []
    stats.favorites = favorites.value.length
  } catch (error) {
    console.error('加载收藏失败:', error)
  }
}

const loadVerifiedFavorites = async () => {
  try {
    const res = await api.get('/verified-favorites/')
    verifiedFavorites.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载官方验收藏失败:', error)
    verifiedFavorites.value = []
  }
}

const removeVerifiedFavorite = async (fav) => {
  try {
    await api.delete(`/verified-favorites/${fav.id}/`)
    verifiedFavorites.value = verifiedFavorites.value.filter(f => f.id !== fav.id)
    ElMessage.success('已取消收藏')
  } catch (error) {
    ElMessage.error('取消收藏失败')
  }
}

const loadVerifiedRecycleOrders = async () => {
  try {
    const res = await api.get('/recycle-orders/')
    verifiedRecycleOrders.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载回收订单失败:', error)
    verifiedRecycleOrders.value = []
  }
}

const loadVerifiedBrowseHistory = () => {
  const historyKey = `browse_history_verified_${authStore.user?.id}`
  const stored = localStorage.getItem(historyKey)
  if (stored) {
    try {
      verifiedBrowseHistory.value = JSON.parse(stored) || []
    } catch (e) {
      console.error('加载浏览历史失败:', e)
      verifiedBrowseHistory.value = []
    }
  } else {
    verifiedBrowseHistory.value = []
  }
}

const saveVerifiedBrowseHistory = () => {
  const historyKey = `browse_history_verified_${authStore.user?.id}`
  localStorage.setItem(historyKey, JSON.stringify(verifiedBrowseHistory.value))
}

const removeVerifiedHistoryItem = (index) => {
  verifiedBrowseHistory.value.splice(index, 1)
  saveVerifiedBrowseHistory()
  ElMessage.success('已删除')
}

const clearVerifiedBrowseHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有浏览历史吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    verifiedBrowseHistory.value = []
    saveVerifiedBrowseHistory()
    ElMessage.success('已清空')
  } catch {
    // 取消
  }
}

const loadAddresses = async () => {
  try {
    const res = await api.get('/addresses/')
    addresses.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('加载地址失败:', error)
    ElMessage.error('加载收货地址失败')
  }
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'status-warning',
    paid: 'status-info',
    shipped: 'status-info',
    completed: 'status-success',
    cancelled: 'status-danger'
  }
  return classes[status] || ''
}

const getOrderStatusLabel = (status) => {
  const labels = {
    pending: '等待买家付款',
    paid: '买家已付款',
    shipped: '等待买家收货',
    completed: '交易完成',
    cancelled: '交易关闭'
  }
  return labels[status] || status
}

const getConditionText = (condition) => {
  const map = {
    new: '全新',
    like_new: '99成新',
    good: '95成新',
    fair: '9成新',
    poor: '8成新'
  }
  return map[condition] || condition || '-'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
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

const getVerifiedOrderStatusLabel = (status) => {
  const map = {
    pending: '待付款',
    paid: '待发货',
    shipped: '待收货',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

const openVerifiedProducts = () => {
  router.push('/verified-products')
}

const goToVerifiedOrderDetail = (id) => {
  router.push(`/verified-order/${id}`)
}

const goToVerifiedProductDetail = (id) => {
  if (!id) return
  router.push(`/verified-products/${id}`)
}

const handleContactVerifiedSeller = (order) => {
  const sellerId = typeof order.product?.seller === 'object' ? order.product.seller.id : order.product?.seller
  router.push(`/messages?user_id=${sellerId}&product_id=${order.product?.id}`)
}

const handleVerifiedPay = () => {
  ElMessage.info('支付功能开发中...')
}

const handleVerifiedConfirmReceive = async (order) => {
  try {
    await api.patch(`/verified-orders/${order.id}/update_status/`, { status: 'completed' })
    ElMessage.success('确认收货成功')
    await loadVerifiedOrders()
  } catch (error) {
    ElMessage.error('确认收货失败')
  }
}

const handleVerifiedCancel = async (order) => {
  try {
    await ElMessageBox.confirm('确认取消订单？', '确认操作', { type: 'warning' })
    await api.patch(`/verified-orders/${order.id}/update_status/`, { status: 'cancelled' })
    ElMessage.success('订单已取消')
    await loadVerifiedOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '取消失败')
    }
  }
}

const switchToSecondhandProfile = () => {
  router.push('/profile')
}

const toggleVerifiedFaq = (index) => {
  verifiedFaqList.value[index].expanded = !verifiedFaqList.value[index].expanded
}

const openOnlineChat = () => {
  ElMessage.info('在线客服功能开发中...')
}

const openPhoneService = () => {
  ElMessage.info('客服电话：400-888-8888')
}

const openEmailService = () => {
  window.location.href = 'mailto:service@verified.com'
}

const filterVerifiedRecycleByStatus = (status) => {
  verifiedRecycleStatus.value = status
}

const getRecycleStatusText = (order) => getRecycleStatusTag(order).text
const getRecycleStatusClass = (order) => {
  const type = getRecycleStatusTag(order).type
  const map = {
    success: 'status-success',
    warning: 'status-warning',
    danger: 'status-danger',
    primary: 'status-primary',
    info: 'status-info',
    '': 'status-info'
  }
  return map[type] || ''
}

// 操作处理
const handleContact = (order) => {
  const userId = activeMenu.value === 'bought' ? order.product?.seller?.id : order.buyer?.id
  router.push(`/messages?user_id=${userId}`)
}

const handlePay = (order) => {
  router.push(`/order/${order.id}`)
}

const handleConfirmReceive = async (order) => {
  try {
    await ElMessageBox.confirm('确认已收到商品？', '确认收货')
    await api.patch(`/orders/${order.id}/update_status/`, { status: 'completed' })
    ElMessage.success('确认收货成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleBuyAgain = (order) => {
  router.push(`/products/${order.product?.id}`)
}

const handleShip = async (order) => {
  try {
    await ElMessageBox.confirm('确认已发货？', '确认发货')
    await api.patch(`/orders/${order.id}/update_status/`, { status: 'shipped' })
    ElMessage.success('发货成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const initEditForm = () => {
  if (authStore.user) {
    editForm.username = authStore.user.username
    editForm.email = authStore.user.email || ''
    editForm.first_name = authStore.user.first_name || ''
    editForm.last_name = authStore.user.last_name || ''
    editForm.location = localStorage.getItem('user_location') || authStore.user.location || ''
    editForm.bio = localStorage.getItem('user_bio') || authStore.user.bio || ''
    locationValue.value = parseLocationToArray(editForm.location)
  }
}

const handleUpdateProfile = async () => {
  updateLoading.value = true
  try {
    // 创建FormData对象，支持文件上传
    const formData = new FormData()
    
    // 添加基本用户信息
    formData.append('username', editForm.username)
    formData.append('email', editForm.email)
    formData.append('first_name', editForm.first_name || '')
    formData.append('last_name', editForm.last_name || '')
    
    // 添加扩展信息
    formData.append('bio', editForm.bio)
    formData.append('location', editForm.location)
    
    // 添加头像文件（如果有）
    if (tempAvatarFile.value) {
      formData.append('avatar', tempAvatarFile.value)
    }
    
    // 发送PATCH请求，使用multipart/form-data格式
    const response = await api.patch('/users/me/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    // 更新authStore中的用户信息
    authStore.user = response.data
    
    // 更新本地存储
    localStorage.setItem('user_location', editForm.location)
    localStorage.setItem('user_bio', editForm.bio)
    userLocation.value = editForm.location
    
    // 清除临时头像
    clearTempAvatar()
    
    ElMessage.success('资料更新成功')
    showEditModal.value = false
  } catch (error) {
    console.error('更新资料失败:', error)
    let errorMessage = '更新失败'
    if (error.response?.data) {
      if (error.response.data.username) {
        errorMessage = error.response.data.username[0]
      } else if (error.response.data.email) {
        errorMessage = error.response.data.email[0]
      } else if (error.response.data.profile) {
        errorMessage = error.response.data.profile
      } else if (error.response.data.avatar) {
        errorMessage = error.response.data.avatar[0]
      } else {
        errorMessage = error.response.data.error || error.response.data.detail || '更新失败'
      }
    }
    ElMessage.error(errorMessage)
  } finally {
    updateLoading.value = false
  }
}

const handleChangePassword = async () => {
  if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.new_password2) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (passwordForm.new_password.length < 6) {
    ElMessage.warning('新密码至少6位')
    return
  }
  if (passwordForm.new_password !== passwordForm.new_password2) {
    ElMessage.warning('两次密码不一致')
    return
  }
  
  passwordLoading.value = true
  try {
    await api.post('/users/change_password/', {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    ElMessage.success('密码修改成功')
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.new_password2 = ''
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '修改失败')
  } finally {
    passwordLoading.value = false
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    authStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  }).catch(() => {})
}

// 地址相关操作
const openAddressModal = (type, data = null) => {
  addressModalType.value = type
  showAddressModal.value = true
  if (type === 'edit' && data) {
    Object.assign(addressForm, data)
  } else {
    // 重置表单
    Object.assign(addressForm, {
      id: null,
      name: '',
      phone: '',
      province: '',
      city: '',
      district: '',
      detail_address: '',
      is_default: false
    })
  }
}

const handleSaveAddress = async () => {
  if (!addressFormRef.value) return
  
  await addressFormRef.value.validate(async (valid) => {
    if (valid) {
      addressLoading.value = true
      try {
        if (addressModalType.value === 'add') {
          await api.post('/addresses/', addressForm)
          ElMessage.success('添加成功')
        } else {
          await api.patch(`/addresses/${addressForm.id}/`, addressForm)
          ElMessage.success('修改成功')
        }
        showAddressModal.value = false
        loadAddresses()
      } catch (error) {
        console.error('保存地址失败:', error)
        ElMessage.error('保存失败')
      } finally {
        addressLoading.value = false
      }
    }
  })
}

const handleDeleteAddress = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该地址吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/addresses/${id}/`)
    ElMessage.success('删除成功')
    loadAddresses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 头像上传方法
const triggerAvatarUpload = () => {
  // 触发文件选择对话框
  if (avatarInput.value) {
    avatarInput.value.click()
  } else if (avatarInputDialog.value) {
    avatarInputDialog.value.click()
  }
}

const handleAvatarChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  // 保存临时文件
  tempAvatarFile.value = file
  
  // 创建临时URL用于预览
  if (tempAvatarUrl.value) {
    URL.revokeObjectURL(tempAvatarUrl.value)
  }
  tempAvatarUrl.value = URL.createObjectURL(file)
  
  // 清空文件选择器，允许再次选择同一文件
  event.target.value = ''
}

const clearTempAvatar = () => {
  // 清除临时文件和URL
  tempAvatarFile.value = null
  if (tempAvatarUrl.value) {
    URL.revokeObjectURL(tempAvatarUrl.value)
    tempAvatarUrl.value = null
  }
}

const syncMenuFromRoute = async () => {
  if (!authStore.user) return

  const zone = route.query.zone
  const tab = route.query.tab
  const verifiedTabs = ['verified-orders', 'verified-favorites', 'verified-history', 'verified-recycle', 'verified-service']

  if (zone === 'verified' || verifiedTabs.includes(tab)) {
    const target = verifiedTabs.includes(tab) ? tab : 'verified-orders'
    activeMenu.value = target
    await loadContent(target)
    return
  }

  if (tab === 'sold') {
    activeMenu.value = 'sold'
    expandedMenus.trade = true
  } else if (tab === 'bought') {
    activeMenu.value = 'bought'
    expandedMenus.trade = true
  } else if (tab === 'published') {
    activeMenu.value = 'published'
    expandedMenus.trade = true
  } else if (tab === 'wallet-transactions') {
    activeMenu.value = 'wallet-transactions'
    expandedMenus.wallet = true
  } else if (tab === 'wallet-bind') {
    activeMenu.value = 'wallet-bind'
    expandedMenus.wallet = true
  } else if (tab === 'favorites') {
    activeMenu.value = 'favorites'
  } else if (tab === 'address') {
    activeMenu.value = 'address'
  } else {
    activeMenu.value = 'home'
  }

  await loadContent(activeMenu.value)
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.init()
  }
  
  if (!authStore.user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  await syncMenuFromRoute()
  
  initEditForm()
  userLocation.value = localStorage.getItem('user_location') || '未设置'
  loadRootDistricts()
  // 初始化绑定表单数据
  loadUserInfo()
})

watch(
  () => [route.query.zone, route.query.tab],
  async () => {
    if (suppressRouteSync) return
    await syncMenuFromRoute()
  }
)
</script>

<style scoped>
.xianyu-style {
  --primary: #ffe400;
  --primary-dark: #ffd600;
  --text-primary: #222;
  --text-secondary: #666;
  --text-muted: #999;
  --border-color: #f0f0f0;
  --bg-page: #f5f5f5;
  --bg-white: #fff;
  --price-color: #ff2442;
}

.profile-page { background: var(--bg-page); min-height: 100vh; }

.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  gap: 20px;
}

/* 左侧边栏 */
.sidebar { width: 200px; flex-shrink: 0; }

.sidebar-menu { background: var(--bg-white); border-radius: 12px; padding: 12px 0; }

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  cursor: pointer;
  color: var(--text-primary);
  font-size: 15px;
  transition: all 0.2s;
}

.menu-item:hover { background: #fafafa; }
.menu-item.active { background: #fff8e6; color: #ff6a00; font-weight: 500; }
.menu-item .el-icon { font-size: 18px; }

.menu-group { border-top: 1px solid var(--border-color); margin-top: 4px; padding-top: 4px; }

.menu-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  cursor: pointer;
  color: var(--text-primary);
  font-size: 15px;
}

.menu-header:hover { background: #fafafa; }
.menu-header .arrow { margin-left: auto; transition: transform 0.2s; }
.menu-header .arrow.expanded { transform: rotate(180deg); }

.submenu { background: #fafafa; }

.submenu-item {
  padding: 12px 20px 12px 48px;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 14px;
}

.submenu-item:hover { color: var(--text-primary); background: #f5f5f5; }
.submenu-item.active { color: #ff6a00; font-weight: 500; }

/* 右侧主体 */
.main-content { flex: 1; min-width: 0; }

/* 用户信息头部 */
.user-header {
  position: relative;
  background: var(--bg-white);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.user-header-bg { height: 80px; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }

.user-info-wrapper {
  display: flex;
  align-items: flex-end;
  padding: 0 24px 20px;
  margin-top: -40px;
  position: relative;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 28px;
  font-weight: 600;
  border: 4px solid #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.user-details { flex: 1; margin-left: 20px; padding-top: 44px; }
.user-name-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.user-name { font-size: 22px; font-weight: 600; color: var(--text-primary); }
.user-badge { padding: 4px 10px; border-radius: 12px; font-size: 12px; background: #fff3cd; color: #856404; }
.user-stats { display: flex; align-items: center; gap: 8px; color: var(--text-muted); font-size: 14px; }
.stat-item { display: flex; align-items: center; gap: 4px; }
.stat-divider { color: #ddd; }
.edit-profile-btn { margin-left: auto; }
.edit-profile-btn .el-button { border-radius: 20px; }

/* 内容区域 */
.content-section, .orders-section {
  background: var(--bg-white);
  border-radius: 12px;
  padding: 20px;
  min-height: 400px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.header-actions { margin-left: auto; display: flex; align-items: center; gap: 12px; }

.section-title { font-size: 18px; font-weight: 600; color: var(--text-primary); margin: 0; }
.section-count { font-size: 14px; color: var(--text-muted); }

.loading-wrapper, .empty-wrapper { padding: 60px 0; }

.location-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}
.location-cascader {
  flex: 1;
}

/* 商品网格 */
.products-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }

/* 我发布的：状态筛选 + 分页（样式对齐 SellerHome） */
.seller-toolbar { display: flex; align-items: center; justify-content: flex-start; margin-bottom: 16px; }
.seller-tabs { display: inline-flex; gap: 6px; padding: 4px; border-radius: 999px; background: #f6f7f9; }
.tab-btn {
  border: 0;
  background: transparent;
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}
.tab-btn:hover { color: var(--text-primary); }
.tab-btn.active { background: #fff; color: var(--text-primary); box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.pagination-wrapper { display: flex; justify-content: center; margin-top: 18px; }

.product-card { cursor: pointer; transition: all 0.2s; border-radius: 8px; overflow: hidden; background: #fafafa; }
.product-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

.product-image { position: relative; width: 100%; aspect-ratio: 1; background: #f5f5f5; }
.product-image img { width: 100%; height: 100%; object-fit: cover; }
.product-image .no-image { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 48px; color: #ddd; }

.status-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-overlay span {
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.35);
}

.product-info { padding: 12px; }
.product-title { font-size: 14px; color: var(--text-primary); line-height: 1.4; height: 40px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; margin-bottom: 8px; }
.product-price { font-size: 18px; font-weight: 600; color: var(--price-color); }
.product-footer { margin-top: 8px; display: flex; align-items: center; justify-content: space-between; }
.status-pill { display: inline-flex; align-items: center; height: 22px; padding: 0 10px; border-radius: 999px; font-size: 12px; }
.status-pill.sold { background: #ffe9ea; color: #ff4d4f; }
.status-pill.pending { background: #fff7e6; color: #d46b08; }
.status-pill.removed { background: #eef2f6; color: #64748b; }
.removed-reason {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 订单状态标签 */
.order-status-tabs {
  display: flex;
  gap: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.order-search-bar {
  margin-bottom: 12px;
}

.status-tab {
  font-size: 15px;
  color: var(--text-secondary);
  cursor: pointer;
  padding-bottom: 12px;
  border-bottom: 3px solid transparent;
  margin-bottom: -17px;
  transition: all 0.2s;
}

.status-tab:hover { color: var(--text-primary); }
.status-tab.active { color: var(--text-primary); font-weight: 600; border-bottom-color: #222; }

/* 订单卡片（大） */
.orders-list { display: flex; flex-direction: column; gap: 16px; }
.settlement-summary { margin-top: 6px; display: flex; align-items: center; gap: 6px; }
.settlement-account { margin-left: 6px; color: #606266; font-size: 12px; }

.order-card-large {
  background: var(--bg-white);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.order-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid var(--border-color);
}

.seller-info { display: flex; align-items: center; gap: 8px; }
.seller-name { font-size: 14px; color: var(--text-primary); font-weight: 500; }

.order-status-text { font-size: 14px; font-weight: 600; }
.status-warning { color: #ff9800; }
.status-info { color: #2196f3; }
.status-success { color: #4caf50; }
.status-danger { color: #f44336; }
.status-primary { color: #1890ff; }

.order-card-body {
  padding: 16px;
  display: flex;
  gap: 16px;
  cursor: pointer;
}

.order-product-image {
  width: 80px;
  height: 80px;
  background: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
}
.order-product-image img { width: 100%; height: 100%; object-fit: cover; }
.order-product-image .el-icon { width: 100%; height: 100%; font-size: 24px; color: #ddd; display: flex; align-items: center; justify-content: center; }

.order-product-info { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.order-product-title { font-size: 15px; color: var(--text-primary); margin-bottom: 6px; font-weight: 500; }
.order-product-desc { font-size: 13px; color: var(--text-muted); }
.order-product-price { font-size: 16px; color: var(--price-color); font-weight: 600; margin-top: 8px; }

.order-card-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-time { font-size: 12px; color: var(--text-muted); }
.order-actions { display: flex; gap: 12px; }

/* 官方验：浏览记录 */
.history-list { display: flex; flex-direction: column; gap: 12px; }
.history-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px 14px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-white);
  cursor: pointer;
}
.history-image { width: 64px; height: 64px; border-radius: 10px; object-fit: cover; background: #f2f2f2; flex-shrink: 0; }
.history-info { flex: 1; min-width: 0; }
.history-title { font-size: 14px; color: var(--text-primary); font-weight: 600; margin-bottom: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.history-meta { display: flex; gap: 10px; font-size: 12px; color: var(--text-muted); }
.history-price { color: var(--price-color); font-weight: 600; }
.history-remove { margin-left: auto; }

/* 官方验：客服 FAQ */
.faq-item { padding: 10px 0; border-bottom: 1px solid var(--border-color); }
.faq-item:last-child { border-bottom: none; }
.faq-q { font-weight: 700; color: var(--text-primary); cursor: pointer; }
.faq-a { margin-top: 8px; color: var(--text-secondary); line-height: 1.6; }

/* 个人资料表单 */
.profile-form, .security-form { max-width: 500px; margin-top: 20px; }
.avatar-upload { display: flex; align-items: center; }
.logout-section { margin-top: 30px; }

/* 收货地址列表 */
.address-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.address-card {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
  background: #fff;
}

.address-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border-color: #e0e0e0;
}

.addr-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.addr-name { font-size: 16px; font-weight: 600; color: #333; }
.addr-phone { font-size: 14px; color: #666; }
.addr-detail { font-size: 14px; color: #666; line-height: 1.5; margin-bottom: 12px; }

.address-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  border-top: 1px solid #f5f5f5;
  padding-top: 12px;
}

/* 钱包相关样式 */






.transactions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-white);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.transaction-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.transaction-detail {
  flex: 1;
}

.transaction-note {
  color: var(--text-primary);
  margin-bottom: 4px;
}

.transaction-time {
  font-size: 12px;
  color: var(--text-muted);
}

.transaction-amount {
  text-align: right;
}

.amount-income {
  color: #67c23a;
  font-weight: 500;
  font-size: 18px;
}

.amount-expense {
  color: #f56c6c;
  font-weight: 500;
  font-size: 18px;
}

.balance-after {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

</style>
