<template>
  <div class="profile-page xianyu-style">
    
    <div class="profile-container">
      <!-- 左侧边栏 -->
      <div class="sidebar">
        <div class="sidebar-menu">
          <!-- 我的易淘 -->
          <div class="menu-item" :class="{ active: activeMenu === 'home' }" @click="switchMenu('home')">
            <el-icon><User /></el-icon>
            <span>我的易淘</span>
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
              <div class="submenu-item" :class="{ active: activeMenu === 'wallet' }" @click="switchMenu('wallet')">
                钱包余额
              </div>
              <div class="submenu-item" :class="{ active: activeMenu === 'wallet-transactions' }" @click="switchMenu('wallet-transactions')">
                交易记录
              </div>
              <div class="submenu-item" :class="{ active: activeMenu === 'wallet-withdraw' }" @click="switchMenu('wallet-withdraw')">
                提现
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
            <span class="section-count">共 {{ products.length }} 件</span>
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
                <div v-if="product.status === 'sold'" class="sold-badge"><span>卖掉了</span></div>
              </div>
              <div class="product-info">
                <div class="product-title">{{ product.title }}</div>
                <div class="product-price">¥{{ product.price }}</div>
              </div>
            </div>
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
              <el-input v-model="editForm.location" placeholder="如：广东省 深圳市" />
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
        <div class="content-section wallet-section" v-if="activeMenu === 'wallet'">
          <div class="section-header">
            <h2 class="section-title">钱包余额</h2>
          </div>
          <div v-if="loading" class="loading-wrapper">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else class="wallet-balance-card">
            <div class="balance-display">
              <div class="balance-label">钱包余额</div>
              <div class="balance-amount">¥{{ walletInfo.balance || '0.00' }}</div>
              <div class="balance-frozen" v-if="walletInfo.frozen_balance > 0">
                冻结余额: ¥{{ walletInfo.frozen_balance }}
              </div>
              <div style="margin-top: 12px; font-size: 12px">
                <el-tag v-if="bindForm.alipay_login_id" type="success" size="small">已绑定：{{ bindForm.alipay_login_id }}</el-tag>
                <el-tag v-else type="warning" size="small">未绑定支付宝账户</el-tag>
              </div>
            </div>
            <div class="balance-actions">
              <el-button type="primary" @click="switchMenu('wallet-withdraw')" :disabled="!walletInfo.balance || walletInfo.balance <= 0">
                提现
              </el-button>
              <el-button @click="switchMenu('wallet-transactions')">查看交易记录</el-button>
              <el-button @click="switchMenu('wallet-bind')">绑定支付宝</el-button>
            </div>
          </div>
        </div>

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
                    {{ row.transaction_type_display }}
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
              <el-table-column prop="balance_after" label="余额" width="120">
                <template #default="{ row }">
                  ¥{{ row.balance_after }}
                </template>
              </el-table-column>
              <el-table-column prop="note" label="备注" min-width="200">
                <template #default="{ row }">
                  {{ row.note || '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="withdraw_status_display" label="提现状态" width="120" v-if="hasWithdrawStatus">
                <template #default="{ row }">
                  <el-tag v-if="row.withdraw_status" :type="getWithdrawStatusType(row.withdraw_status)" size="small">
                    {{ row.withdraw_status_display }}
                  </el-tag>
                  <span v-else>-</span>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="walletTransactionsTotal > walletTransactions.length" style="text-align: center; margin-top: 16px">
              <el-button @click="loadMoreTransactions">加载更多</el-button>
            </div>
          </div>
        </div>

        <!-- 提现 -->
        <div class="content-section wallet-withdraw-section" v-if="activeMenu === 'wallet-withdraw'">
          <div class="section-header">
            <h2 class="section-title">提现</h2>
          </div>
          <el-card class="withdraw-card">
            <el-alert
              type="info"
              :closable="false"
              style="margin-bottom: 20px"
            >
              <template #title>
                <div>提现将转账到您的支付宝账户（支持沙箱环境）</div>
              </template>
            </el-alert>
            <el-form :model="withdrawForm" label-width="100px">
              <el-form-item label="可提现金额">
                <div style="font-size: 24px; color: #ff2442; font-weight: bold">
                  ¥{{ walletInfo.balance || '0.00' }}
                </div>
              </el-form-item>
              <el-form-item label="提现金额" required>
                <el-input-number
                  v-model="withdrawForm.amount"
                  :precision="2"
                  :min="0.01"
                  :max="walletInfo.balance && walletInfo.balance > 0.01 ? walletInfo.balance : 0.01"
                  :step="100"
                  :disabled="!walletInfo.balance || walletInfo.balance <= 0"
                  style="width: 100%"
                  placeholder="请输入提现金额"
                />
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  可提现金额: ¥{{ walletInfo.balance || '0.00' }}
                </div>
              </el-form-item>
              <el-form-item label="支付宝账号" required>
                <el-input
                  v-model="withdrawForm.alipay_account"
                  placeholder="请输入支付宝账号（手机号或邮箱）"
                />
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  支持沙箱环境测试账号。如果已绑定支付宝账户，将自动填充
                </div>
              </el-form-item>
              <el-form-item label="支付宝姓名">
                <el-input
                  v-model="withdrawForm.alipay_name"
                  placeholder="请输入支付宝真实姓名（可选，建议填写）"
                />
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  填写真实姓名可提高提现成功率
                </div>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="withdrawing" @click="handleWithdraw" :disabled="!walletInfo.balance || walletInfo.balance <= 0">确认提现</el-button>
                <el-button @click="resetWithdrawForm">重置</el-button>
                <el-button @click="switchMenu('wallet')">返回</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

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
          <el-input v-model="editForm.location" placeholder="如：广东省 深圳市" />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, ShoppingBag, Star, Setting, ArrowDown, Location, PictureFilled, Wallet } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 菜单状态
const activeMenu = ref('home')
const expandedMenus = reactive({
  trade: true,
  wallet: true,
  settings: true
})

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

// 数据
const loading = ref(false)
const products = ref([])
const allOrders = ref([])
const favorites = ref([])
const addresses = ref([])
const userLocation = ref('未设置')

// 钱包相关数据
const walletInfo = ref({ balance: 0, frozen_balance: 0 })
const walletTransactions = ref([])
const walletTransactionsTotal = ref(0)
const walletTransactionsPage = ref(1)
const walletTransactionsPageSize = ref(20)
const withdrawing = ref(false)
const binding = ref(false)
const withdrawForm = reactive({
  amount: null,
  alipay_account: '',
  alipay_name: ''
})
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
const loadWalletInfo = async () => {
  try {
    const res = await api.get('/users/wallet/', {
      params: {
        page: 1,
        page_size: 1
      }
    })
    walletInfo.value = {
      balance: res.data.balance || 0,
      frozen_balance: res.data.frozen_balance || 0
    }
  } catch (error) {
    console.error('加载钱包信息失败:', error)
  }
}

const loadWalletTransactions = async () => {
  loading.value = true
  try {
    const res = await api.get('/users/wallet/', {
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
    walletInfo.value = {
      balance: res.data.balance || 0,
      frozen_balance: res.data.frozen_balance || 0
    }
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

const resetWithdrawForm = () => {
  withdrawForm.amount = null
  withdrawForm.alipay_account = bindForm.alipay_login_id || ''
  withdrawForm.alipay_name = bindForm.alipay_real_name || ''
}

const handleWithdraw = async () => {
  if (!withdrawForm.amount || withdrawForm.amount <= 0) {
    ElMessage.warning('请输入提现金额')
    return
  }
  if (withdrawForm.amount > walletInfo.value.balance) {
    ElMessage.warning('提现金额不能超过余额')
    return
  }
  if (!withdrawForm.alipay_account) {
    ElMessage.warning('请输入支付宝账号')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认提现 ¥${withdrawForm.amount} 到支付宝账号 ${withdrawForm.alipay_account}？`,
      '确认提现',
      { type: 'warning' }
    )
    
    withdrawing.value = true
    const res = await api.post('/users/withdraw/', {
      amount: withdrawForm.amount,
      alipay_account: withdrawForm.alipay_account,
      alipay_name: withdrawForm.alipay_name
    })
    
    if (res.data.success) {
      ElMessage.success(res.data.message || '提现成功')
      resetWithdrawForm()
      await loadWalletInfo()
      await loadWalletTransactions()
      switchMenu('wallet-transactions')
    } else {
      ElMessage.error(res.data.detail || '提现失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      const errorDetail = error.response?.data?.detail || '提现失败'
      ElMessage.error(errorDetail)
    }
  } finally {
    withdrawing.value = false
  }
}

const loadUserInfo = async () => {
  try {
    const res = await api.get('/users/me/')
    bindForm.alipay_login_id = res.data?.alipay_login_id || ''
    bindForm.alipay_real_name = res.data?.alipay_real_name || ''
    // 如果已绑定支付宝，自动填充到提现表单
    if (bindForm.alipay_login_id && !withdrawForm.alipay_account) {
      withdrawForm.alipay_account = bindForm.alipay_login_id
    }
    if (bindForm.alipay_real_name && !withdrawForm.alipay_name) {
      withdrawForm.alipay_name = bindForm.alipay_real_name
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

const handleBindAlipay = async () => {
  if (!bindForm.alipay_login_id) {
    ElMessage.warning('请输入支付宝登录账号')
    return
  }
  try {
    binding.value = true
    const res = await api.patch('/users/me/', {
      alipay_login_id: bindForm.alipay_login_id,
      alipay_real_name: bindForm.alipay_real_name
    })
    ElMessage.success('绑定成功')
    // 更新绑定表单
    if (res.data) {
      bindForm.alipay_login_id = res.data.alipay_login_id || bindForm.alipay_login_id
      bindForm.alipay_real_name = res.data.alipay_real_name || bindForm.alipay_real_name
    }
    // 同时更新 authStore 中的用户信息
    if (authStore.user) {
      authStore.user.alipay_login_id = res.data?.alipay_login_id || ''
      authStore.user.alipay_real_name = res.data?.alipay_real_name || ''
      localStorage.setItem('user', JSON.stringify(authStore.user))
    }
    // 如果提现表单中的账号为空，自动填充
    if (!withdrawForm.alipay_account && bindForm.alipay_login_id) {
      withdrawForm.alipay_account = bindForm.alipay_login_id
    }
    if (!withdrawForm.alipay_name && bindForm.alipay_real_name) {
      withdrawForm.alipay_name = bindForm.alipay_real_name
    }
  } catch (error) {
    const detail = error.response?.data?.detail || '绑定失败'
    ElMessage.error(detail)
  } finally {
    binding.value = false
  }
}

const getTransactionType = (type) => {
  const typeMap = {
    income: 'success',
    expense: 'danger',
    withdraw: 'warning',
    refund: 'info'
  }
  return typeMap[type] || 'info'
}

const hasWithdrawStatus = computed(() => {
  return walletTransactions.value.some(t => t.withdraw_status)
})

const getWithdrawStatusType = (status) => {
  const statusMap = {
    pending: 'warning',
    processing: 'primary',
    success: 'success',
    failed: 'danger'
  }
  return statusMap[status] || 'info'
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
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
      case 'wallet':
        await loadWalletInfo()
        await loadUserInfo()
        break
      case 'wallet-transactions':
        walletTransactionsPage.value = 1
        await loadWalletTransactions()
        break
      case 'wallet-withdraw':
        await loadWalletInfo()
        await loadUserInfo()
        // 如果已绑定支付宝，自动填充到提现表单
        if (bindForm.alipay_login_id && !withdrawForm.alipay_account) {
          withdrawForm.alipay_account = bindForm.alipay_login_id
        }
        if (bindForm.alipay_real_name && !withdrawForm.alipay_name) {
          withdrawForm.alipay_name = bindForm.alipay_real_name
        }
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
    const res = await api.get('/products/my_products/')
    products.value = res.data || []
    stats.products = products.value.length
  } catch (error) {
    console.error('加载商品失败:', error)
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

const loadFavorites = async () => {
  try {
    const res = await api.get('/favorites/')
    favorites.value = res.data?.results || res.data || []
    stats.favorites = favorites.value.length
  } catch (error) {
    console.error('加载收藏失败:', error)
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
    shipped: '等待见面交易',
    completed: '交易完成',
    cancelled: '交易关闭'
  }
  return labels[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
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

onMounted(async () => {
  if (!authStore.user) {
    await authStore.init()
  }
  
  if (!authStore.user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  // 检查URL参数，决定显示哪个菜单
  const tab = route.query.tab
  if (tab === 'sold') {
    activeMenu.value = 'sold'
    expandedMenus.trade = true
    loadOrders()
  } else if (tab === 'bought') {
    activeMenu.value = 'bought'
    expandedMenus.trade = true
    loadOrders()
  } else if (tab === 'favorites') {
    activeMenu.value = 'favorites'
    loadFavorites()
  } else if (tab === 'address') {
    activeMenu.value = 'address'
    loadAddresses()
  } else {
    loadProducts()
  }
  
  initEditForm()
  userLocation.value = localStorage.getItem('user_location') || '未设置'
  // 初始化绑定表单数据
  loadUserInfo()
})
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

.section-title { font-size: 18px; font-weight: 600; color: var(--text-primary); margin: 0; }
.section-count { font-size: 14px; color: var(--text-muted); }

.loading-wrapper, .empty-wrapper { padding: 60px 0; }

/* 商品网格 */
.products-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }

.product-card { cursor: pointer; transition: all 0.2s; border-radius: 8px; overflow: hidden; background: #fafafa; }
.product-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

.product-image { position: relative; width: 100%; aspect-ratio: 1; background: #f5f5f5; }
.product-image img { width: 100%; height: 100%; object-fit: cover; }
.product-image .no-image { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 48px; color: #ddd; }

.sold-badge {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sold-badge span {
  background: #ff6a00;
  color: #fff;
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  transform: rotate(-15deg);
}

.product-info { padding: 12px; }
.product-title { font-size: 14px; color: var(--text-primary); line-height: 1.4; height: 40px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; margin-bottom: 8px; }
.product-price { font-size: 18px; font-weight: 600; color: var(--price-color); }

/* 订单状态标签 */
.order-status-tabs {
  display: flex;
  gap: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
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
.wallet-balance-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 40px;
  color: white;
  text-align: center;
}

.balance-display {
  margin-bottom: 24px;
}

.balance-label {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 16px;
}

.balance-amount {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 8px;
}

.balance-frozen {
  font-size: 14px;
  opacity: 0.8;
}

.balance-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

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

.withdraw-card {
  max-width: 600px;
}
</style>
