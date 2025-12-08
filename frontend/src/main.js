import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { useAdminAuthStore } from './stores/adminAuth'
import './index.css'
import './styles/theme.css'
import './styles/xianyu.css'
import './styles/admin-theme.css'
import './styles/admin-vea.css'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 设置Element Plus主题色
app.use(ElementPlus, { 
  locale: zhCn,
  size: 'default'
})

app.use(pinia)
app.use(router)

// 初始化认证状态
const authStore = useAuthStore()
authStore.init()

// 初始化后台管理认证状态
const adminAuthStore = useAdminAuthStore()
adminAuthStore.init()

app.mount('#app')

