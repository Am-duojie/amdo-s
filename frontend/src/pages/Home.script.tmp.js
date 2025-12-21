
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Document, List, Star, ChatDotRound, User, SwitchButton, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import { useAuthStore } from '@/stores/auth'
import { getResults } from '@/utils/responseGuard'

const router = useRouter()
const authStore = useAuthStore()

// 状态
const activeCategory = ref(null)
const activeTab = ref('recommend')
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)
const products = ref([])
const pageIndex = ref(1)


// 鏁扮爜鍒嗙被
const categories = ref([])
const catIcons = ['手机','相机','电脑','图书','耳机','游戏','配件','手表']

// 鍒嗙被鍟嗗搧鏁版嵁
const phoneProducts = ref([])
const cameraProducts = ref([])
const computerProducts = ref([])
const tabletProducts = ref([])
const verifiedProducts = ref([])

// 鏍规嵁鍒嗙被鍚嶇О鍔犺浇鍟嗗搧
const loadCategoryProducts = async () => {
  try {
    // 鑾峰彇鎵€鏈夊晢鍝?    const res = await api.get('/products/', { params: { status: 'active', page_size: 50 } })
    const allProducts = res.data.results || res.data || []
    
    // 鎸夋爣棰樺叧閿瘝鍒嗙被
    phoneProducts.value = allProducts.filter(p => 
      /手机|iPhone|华为|小米|OPPO|vivo|三星|荣耀/i.test(p.title)
    ).slice(0, 4)
    
    cameraProducts.value = allProducts.filter(p => 
      /相机|摄像|镜头|佳能|尼康|索尼|富士|单反|微单/i.test(p.title)
    ).slice(0, 4)
    
    computerProducts.value = allProducts.filter(p => 
      /电脑|笔记本|台式|MacBook|ThinkPad|联想|戴尔|华硕|显卡|CPU/i.test(p.title)
    ).slice(0, 4)
    
    tabletProducts.value = allProducts.filter(p => 
      /平板|iPad|Pro|Air|安卓平板|华为平板|小米平板/i.test(p.title)
    ).slice(0, 4)

    // 鍔犺浇瀹樻柟楠岃揣鍟嗗搧
    try {
      const verifiedRes = await api.get('/verified-products/', { params: { page_size: 3 } })
      verifiedProducts.value = verifiedRes.data?.results || verifiedRes.data || []
    } catch (err) {
      console.error('加载官方验货商品失败:', err)
      verifiedProducts.value = []
    }
    // 如果某分类商品不足，用其他商品填充
    const fillProducts = allProducts.filter(p =>
      !phoneProducts.value.includes(p) && 
      !cameraProducts.value.includes(p) && 
      !computerProducts.value.includes(p) && 
      !tabletProducts.value.includes(p)
    )
    
    if (phoneProducts.value.length < 3) {
      phoneProducts.value = [...phoneProducts.value, ...fillProducts.slice(0, 3 - phoneProducts.value.length)]
    }
    if (cameraProducts.value.length < 3) {
      cameraProducts.value = [...cameraProducts.value, ...fillProducts.slice(0, 3 - cameraProducts.value.length)]
    }
    if (computerProducts.value.length < 3) {
      computerProducts.value = [...computerProducts.value, ...fillProducts.slice(0, 3 - computerProducts.value.length)]
    }
    if (tabletProducts.value.length < 3) {
      tabletProducts.value = [...tabletProducts.value, ...fillProducts.slice(0, 3 - tabletProducts.value.length)]
    }
  } catch (err) {
    console.error('加载分类商品失败:', err)
  }
}

// 鏍规嵁鍒嗙被鍚嶇О璺宠浆
const goToCategoryByName = (name) => {
  router.push({ path: '/products', query: { search: name } })
}

// 鏍囩
const tabs = ref([
  { id: 'recommend', name: '猜你喜欢', desc: '为你推荐' },
  { id: 'fresh', name: '最新发布', desc: '刚刚上架' },
  { id: 'nearby', name: '同城好物', desc: '就在身边' },
  { id: 'low_price', name: '捡漏专区', desc: '超低价格' },
])
// 宸ュ叿鏂规硶
const formatPriceInt = (price) => Math.floor(price).toLocaleString()
const formatPriceDecimal = (price) => {
  const decimal = price.toString().split('.')[1]
  return decimal ? `.${decimal}` : ''
}

const resolveVerifiedThumb = (p) => {
  // 浼樺厛 detail_images / images / cover_image / image_url
  const fallback = 'https://via.placeholder.com/80'
  if (!p) return fallback
  const pick = (img) => {
    if (!img) return null
    if (typeof img === 'string') return getImageUrl(img)
    if (img.image) return getImageUrl(img.image)
    if (img.url) return getImageUrl(img.url)
    if (img.image_url) return getImageUrl(img.image_url)
    if (img.imageUrl) return getImageUrl(img.imageUrl)
    return null
  }
  if (Array.isArray(p.detail_images) && p.detail_images.length) {
    const src = pick(p.detail_images[0])
    if (src) return src
  }
  if (Array.isArray(p.images) && p.images.length) {
    const src = pick(p.images[0])
    if (src) return src
  }
  if (p.cover_image) {
    const src = pick(p.cover_image)
    if (src) return src
  }
  return fallback
}


const switchTab = (id) => {
  activeTab.value = id
  products.value = []
  pageIndex.value = 1
  loadProducts()
}

const goToPublish = () => router.push('/publish')
const goToDetail = (id) => router.push(`/products/${id}`)
const goToProfile = () => router.push('/profile')
const goToVerifiedProducts = () => router.push('/verified-products')
const goToVerifiedDetail = (id) => router.push(`/verified-products/${id}`)
const goToRecycle = () => router.push('/recycle')

// 澶勭悊鐢ㄦ埛鑿滃崟鍛戒护
const handleUserMenuCommand = async (command) => {
  switch (command) {
    case 'trade':
      router.push('/profile?tab=bought')  // 璺宠浆鍒版垜鐨勪氦鏄擄紙榛樿鏄剧ず鎴戜拱鍒扮殑锛?      break
    case 'favorites':
      router.push('/profile?tab=favorites')  // 璺宠浆鍒版垜鐨勬敹钘?      break
    case 'settings':
      router.push('/profile?tab=address')  // 璺宠浆鍒拌处鎴疯缃紙榛樿鏄剧ず鏀惰揣鍦板潃锛?      break
    case 'products':
      router.push('/profile')  // 璺宠浆鍒颁釜浜轰腑蹇?      break
    case 'orders':
      router.push('/profile?tab=bought')  // 璺宠浆鍒颁釜浜轰腑蹇冪殑"鎴戜拱鍒扮殑"
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
        // 鍙栨秷閫€鍑?      }
      break
  }
}

// 加载分类（从后端）
const loadCategories = async () => {
  try {
    const res = await api.get('/categories/')
    let allCategories = getResults(res.data)
    // 按数码产品重要性排序
    const categoryOrder = ['手机','平板','笔记本电脑','台式电脑','摄影摄像','智能手表','耳机音响','游戏设备','数码配件','其他数码']
    allCategories.sort((a, b) => {
      const indexA = categoryOrder.indexOf(a.name)
      const indexB = categoryOrder.indexOf(b.name)
      return indexA - indexB
    })
    
    categories.value = allCategories
  } catch (err) {
    console.error('加载分类失败:', err)
    categories.value = []
  }
}

// 点击分类，跳到商品列表并带上分类筛选
const goToCategory = (categoryId) => {
  if (!categoryId) return
  router.push({ path: '/products', query: { category: categoryId } })
}

// 鍔犺浇鍟嗗搧
const loadProducts = async (append = false) => {
  if (!append) loading.value = true
  else loadingMore.value = true

  try {
    const locationKey = (() => {
      const raw = authStore.user?.location || ''
      if (!raw) return ''
      if (raw.includes('市')) {
        return raw.split('市')[0].slice(-2) + '市'
      }
      if (raw.includes('省')) {
        const parts = raw.split('省')
        return parts[1] ? parts[1].slice(0, 2) : parts[0].slice(-2)
      }
      return raw.slice(0, 3)
    })()

    let ordering = '-created_at'
    if (activeTab.value === 'recommend') {
      ordering = '-view_count'
    } else if (activeTab.value === 'fresh') {
      ordering = '-created_at'
    } else if (activeTab.value === 'low_price') {
      ordering = 'price'
    } else if (activeTab.value === 'nearby') {
      ordering = '-created_at'
    }

    const params = {
      status: 'active',
      page: append ? pageIndex.value + 1 : 1,
      page_size: 30,
      ordering,
    }

    const res = await api.get('/products/', { params })
    let newProducts = getResults(res.data)

    if (activeTab.value === 'nearby' && locationKey) {
      const nearbyProducts = newProducts.filter(p => {
        const loc = (p.location || '').toLowerCase()
        return loc.includes(locationKey.toLowerCase())
      })
      newProducts = nearbyProducts.length > 0 ? nearbyProducts : newProducts
    }

    if (activeTab.value === 'recommend') {
      newProducts = newProducts
        .map(p => ({ p, sort: Math.random() }))
        .sort((a, b) => a.sort - b.sort)
        .map(item => item.p)
    }

    if (append) products.value.push(...newProducts)
    else products.value = newProducts

    hasMore.value = !!res.data.next
    if (append) {
      pageIndex.value += 1
    } else {
      pageIndex.value = 1
    }
  } catch (error) {
    console.error('加载商品失败:', error)
    ElMessage.error('加载商品失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => loadProducts(true)

onMounted(async () => {
  if (!authStore.user && !authStore.loading) {
    await authStore.init()
  }
  loadCategories()
  loadProducts()
  loadCategoryProducts()
  const onScrollLoadMore = () => {
    if (loadingMore.value || loading.value || !hasMore.value) return
    const scrollBottom = window.innerHeight + window.scrollY
    const docHeight = document.documentElement.scrollHeight || document.body.scrollHeight
    if (scrollBottom >= docHeight - 200) loadMore()
  }
  window.addEventListener('scroll', onScrollLoadMore, { passive: true })
  onBeforeUnmount(() => {
    window.removeEventListener('scroll', onScrollLoadMore)
  })
})
