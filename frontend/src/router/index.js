import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue')
  },
  {
    path: '/original',
    name: 'OriginalHome',
    component: () => import('@/pages/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue')
  },
  {
    path: '/products',
    name: 'ProductList',
    component: () => import('@/pages/ProductList.vue')
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: () => import('@/pages/ProductDetail.vue')
  },
  {
    path: '/publish',
    name: 'PublishProduct',
    component: () => import('@/pages/EditProduct.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/edit/:id',
    name: 'EditProduct',
    component: () => import('@/pages/EditProduct.vue'),
    meta: { requiresAuth: true }
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
    meta: { requiresAuth: true }
  },
  {
    path: '/checkout/:id',
    name: 'Checkout',
    component: () => import('@/pages/Checkout.vue'),
    meta: { requiresAuth: true }
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
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/recycle',
    name: 'Recycle',
    component: () => import('@/pages/Recycle.vue')
  },
  {
    path: '/verified-products',
    name: 'VerifiedProducts',
    component: () => import('@/pages/VerifiedProducts.vue')
  },
  {
    path: '/verified-profile',
    name: 'VerifiedProfile',
    component: () => import('@/pages/VerifiedProfile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/verified-order/:id',
    name: 'VerifiedOrderDetail',
    component: () => import('@/pages/VerifiedOrderDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/verified-products/:id',
    name: 'VerifiedProductDetail',
    component: () => import('@/pages/VerifiedProductDetail.vue')
  },

]

const router = createRouter({
  history: createWebHistory(),
  routes
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








