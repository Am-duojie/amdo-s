import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.user) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router






