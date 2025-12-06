import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAdminAuthStore } from '@/stores/adminAuth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    meta: { theme: 'yellow', hideSearch: false }
  },
  {
    path: '/original',
    name: 'OriginalHome',
    component: () => import('@/pages/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { hideSearch: true, theme: 'yellow' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue'),
    meta: { hideSearch: true, theme: 'yellow' }
  },
  {
    path: '/products',
    name: 'ProductList',
    component: () => import('@/pages/ProductList.vue'),
    meta: { theme: 'yellow', hideSearch: false }
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: () => import('@/pages/ProductDetail.vue'),
    meta: { theme: 'yellow', hideSearch: false }
  },
  {
    path: '/publish',
    name: 'PublishProduct',
    component: () => import('@/pages/EditProduct.vue'),
    meta: { requiresAuth: true, hideSearch: true, theme: 'yellow' }
  },
  {
    path: '/edit/:id',
    name: 'EditProduct',
    component: () => import('@/pages/EditProduct.vue'),
    meta: { requiresAuth: true, hideSearch: true, theme: 'yellow' }
  },
  {
    path: '/my-products',
    name: 'MyProducts',
    component: () => import('@/pages/MyProducts.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/order/:id',
    name: 'OrderDetail',
    component: () => import('@/pages/OrderDetail.vue'),
    meta: { requiresAuth: true, hideSearch: true, theme: 'yellow' }
  },
  {
    path: '/checkout/:id',
    name: 'Checkout',
    component: () => import('@/pages/Checkout.vue'),
    meta: { requiresAuth: true, hideSearch: true, theme: 'yellow' }
  },
  {
    path: '/my-favorites',
    name: 'MyFavorites',
    component: () => import('@/pages/MyFavorites.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('@/pages/Messages.vue'),
    meta: { requiresAuth: true, hideSearch: true, theme: 'yellow' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: true, hideSearch: false, theme: 'yellow' }
  },
  {
    path: '/recycle',
    name: 'Recycle',
    component: () => import('@/pages/Recycle.vue'),
    meta: { theme: 'yellow', hideSearch: false }
  },
  {
    path: '/my-recycle-orders',
    name: 'MyRecycleOrders',
    component: () => import('@/pages/MyRecycleOrders.vue'),
    meta: { requiresAuth: true, theme: 'yellow', hideSearch: false }
  },
  {
    path: '/recycle-order/:id',
    name: 'RecycleOrderDetail',
    component: () => import('@/pages/RecycleOrderDetail.vue'),
    meta: { requiresAuth: true, theme: 'yellow', hideSearch: false }
  },
  {
    path: '/verified-products',
    name: 'VerifiedProducts',
    component: () => import('@/pages/VerifiedProducts.vue'),
    meta: { theme: 'blue', hideSearch: false, verifiedMode: true }
  },
  {
    path: '/verified-profile',
    name: 'VerifiedProfile',
    component: () => import('@/pages/VerifiedProfile.vue'),
    meta: { requiresAuth: true, theme: 'blue', hideSearch: false, verifiedMode: true }
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/admin/pages/AdminLogin.vue'),
    meta: { hideSearch: true, adminPublic: true, admin: true }
  },
  {
    path: '/admin',
    component: () => import('@/admin/layout/AdminLayout.vue'),
    meta: { hideSearch: true, admin: true },
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/admin/pages/AdminDashboard.vue'), meta: { requiresAdminAuth: true, hideSearch: true } },
      // 回收业务
      { path: 'recycle-orders', name: 'RecycleOrderManagement', component: () => import('@/admin/pages/RecycleOrderManagement.vue'), meta: { requiresAdminAuth: true } },
      { path: 'inspection-orders', name: 'InspectionOrders', component: () => import('@/admin/pages/InspectionOrders.vue'), meta: { requiresAdminAuth: true } },
      { path: 'inspection-orders/:id', name: 'InspectionOrderDetail', component: () => import('@/admin/pages/InspectionOrderDetail.vue'), meta: { requiresAdminAuth: true } },
      // 官方验业务
      { path: 'verified-products', name: 'VerifiedProductManagement', component: () => import('@/admin/pages/VerifiedProductManagement.vue'), meta: { requiresAdminAuth: true } },
      { path: 'verified-orders', name: 'VerifiedOrderManagement', component: () => import('@/admin/pages/VerifiedOrderManagement.vue'), meta: { requiresAdminAuth: true } },
      // 兼容旧路由
      { path: 'recycled-products', name: 'RecycledProductsAdmin', component: () => import('@/admin/pages/RecycledProducts.vue'), meta: { requiresAdminAuth: true } },
      { path: 'verified-listings', name: 'VerifiedListingsAdmin', component: () => import('@/admin/pages/VerifiedListings.vue'), meta: { requiresAdminAuth: true } },
      { path: 'audit-queue', name: 'AuditQueueAdmin', component: () => import('@/admin/pages/AuditQueue.vue'), meta: { requiresAdminAuth: true } },
      { path: 'audit-logs', name: 'AuditLogsAdmin', component: () => import('@/admin/pages/AuditLogs.vue'), meta: { requiresAdminAuth: true } },
      { path: 'users', name: 'AdminUsers', component: () => import('@/admin/pages/Users.vue'), meta: { requiresAdminAuth: true } },
      { path: 'roles', name: 'AdminRoles', component: () => import('@/admin/pages/Roles.vue'), meta: { requiresAdminAuth: true } },
      // 易淘业务
      { path: 'secondhand-orders', name: 'SecondHandOrderManagement', component: () => import('@/admin/pages/SecondHandOrderManagement.vue'), meta: { requiresAdminAuth: true } },
      // 兼容旧路由
      { path: 'payments', name: 'AdminPayments', component: () => import('@/admin/pages/Payments.vue'), meta: { requiresAdminAuth: true } },
      { path: 'verified-orders-old', name: 'AdminVerifiedOrders', component: () => import('@/admin/pages/VerifiedOrdersAdmin.vue'), meta: { requiresAdminAuth: true } },
      { path: 'shops', name: 'AdminShops', component: () => import('@/admin/pages/Shops.vue'), meta: { requiresAdminAuth: true } },
      { path: 'categories', name: 'AdminCategories', component: () => import('@/admin/pages/Categories.vue'), meta: { requiresAdminAuth: true } },
      { path: 'products', name: 'AdminProducts', component: () => import('@/admin/pages/Products.vue'), meta: { requiresAdminAuth: true } },
      { path: 'frontend-users', name: 'AdminFrontendUsers', component: () => import('@/admin/pages/FrontendUsers.vue'), meta: { requiresAdminAuth: true } },
      { path: 'messages', name: 'AdminMessages', component: () => import('@/admin/pages/Messages.vue'), meta: { requiresAdminAuth: true } },
      { path: 'addresses', name: 'AdminAddresses', component: () => import('@/admin/pages/Addresses.vue'), meta: { requiresAdminAuth: true } },
    ]
  },
  {
    path: '/verified-order/:id',
    name: 'VerifiedOrderDetail',
    component: () => import('@/pages/VerifiedOrderDetail.vue'),
    meta: { requiresAuth: true, theme: 'blue', hideSearch: false, verifiedMode: true }
  },

]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { left: 0, top: 0 }
  }
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 等待认证状态初始化完成
  if (authStore.loading) {
    await new Promise(resolve => {
      const unwatch = authStore.$subscribe(() => {
        if (!authStore.loading) {
          unwatch()
          resolve()
        }
      })
      // 防止无限等待
      setTimeout(() => {
        unwatch()
        resolve()
      }, 1000)
    })
  }
  
  if (to.meta.requiresAuth && !authStore.user) {
    next({ name: 'Login' })
    return
  }
  
  if (to.matched.some(r => r.meta.requiresAdminAuth)) {
    const admin = useAdminAuthStore()
    
    // 等待后台认证状态初始化完成
    if (admin.loading) {
      await new Promise(resolve => {
        const unwatch = admin.$subscribe(() => {
          if (!admin.loading) {
            unwatch()
            resolve()
          }
        })
        // 防止无限等待
        setTimeout(() => {
          unwatch()
          resolve()
        }, 1000)
      })
    }
    
    // 检查登录状态
    const token = localStorage.getItem('ADMIN_TOKEN')
    const hasUser = !!admin.user
    
    if (!token || !hasUser) {
      // 如果是从登录页跳转过来的，且已经有token，再等一会儿
      if (from.name === 'AdminLogin' && token) {
        await new Promise(resolve => setTimeout(resolve, 200))
        // 再次检查
        if (admin.isAuthed) {
          next()
          return
        }
      }
      next({ name: 'AdminLogin' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router


