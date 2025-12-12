<template>
  <div class="recycle-page">
    <div class="mobile-shell">
      <div class="content-viewport">
        <div class="content-grid">
          <div class="main-column">
            <header class="top-bar">
              <button class="icon-btn" @click="router.back()">←</button>
              <div class="top-title">产品列表</div>
              <div class="top-actions">
                <button class="icon-btn">⋯</button>
                <button class="icon-btn">⚙️</button>
              </div>
            </header>

            <section class="search-row">
              <div class="search-box">
                <span class="search-icon">🔍</span>
                <input
                  v-model="searchKeyword"
                  placeholder="搜索商品 寄售估价"
                  class="search-input"
                />
              </div>
              <button class="cart-btn">🛒</button>
            </section>

            <section class="chip-row">
              <button
                v-for="item in categoryList"
                :key="item.label"
                class="chip"
                :class="{ active: selectedCategory?.label === item.label }"
                @click="selectCategory(item)"
              >
                {{ item.label }}
              </button>
            </section>

            <section class="category-browser">
              <div class="brand-nav">
                <button
                  v-for="brand in brandList"
                  :key="brand"
                  class="brand-item"
                  :class="{ active: brand === selectedBrand }"
                  @click="selectBrand(brand)"
                >
                  {{ brand }}
                </button>
              </div>
              <div class="product-pane" ref="categoryPaneRef">
                <div
                  v-for="model in modelList"
                  :key="model"
                  class="product-row"
                  @click="openEstimator({
                    device_type: selectedCategory.device_type,
                    brand: selectedBrand,
                    model,
                    storage: currentStorage
                  })"
                >
                  <div class="product-thumb">📱</div>
                  <div class="product-info">
                    <div class="product-name">{{ selectedBrand }} {{ model }}</div>
                    <div class="product-sub">含寄售估价 / 透明质检</div>
                  </div>
                  <div class="product-price">估价</div>
                </div>
              </div>
            </section>
          </div>

        <transition name="sheet">
          <div class="estimate-sheet" v-if="sheetVisible" :class="{ desktop: isDesktop }">
            <div class="sheet-mask" v-if="!isDesktop" @click="closeSheet"></div>
            <div class="sheet-panel">
              <div class="sheet-header">
                <div>
                  <div class="sheet-title">在线估价</div>
                  <div class="sheet-sub">填写品牌型号即可立即估价</div>
                </div>
                <button class="close-btn" v-if="!isDesktop" @click="closeSheet">✕</button>
              </div>

            <div class="form-group">
              <label>设备类型</label>
              <select v-model="estimateForm.device_type" class="form-select" @change="onBrandChange">
                <option value="">请选择</option>
                <option value="手机">手机</option>
                <option value="平板">平板</option>
                <option value="笔记本">笔记本</option>
              </select>
            </div>

            <div class="form-group">
              <label>品牌</label>
              <select v-model="estimateForm.brand" class="form-select" @change="onBrandChange">
                <option value="">请选择</option>
                <option v-for="brand in availableBrands" :key="brand" :value="brand">{{ brand }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>型号</label>
              <select v-model="estimateForm.model" class="form-select" @change="onModelChange">
                <option value="">请选择</option>
                <option v-for="model in availableModels" :key="model" :value="model">{{ model }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>存储容量</label>
              <select v-model="estimateForm.storage" class="form-select">
                <option value="">请选择</option>
                <option v-for="storage in availableStorage" :key="storage" :value="storage">{{ storage }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>成色</label>
              <div class="condition-options">
                <label
                  v-for="cond in conditions"
                  :key="cond.value"
                  class="condition-option"
                  :class="{ active: estimateForm.condition === cond.value }"
                >
                  <input
                    type="radio"
                    :value="cond.value"
                    v-model="estimateForm.condition"
                    class="condition-radio"
                  />
                  <span>{{ cond.label }}</span>
                </label>
              </div>
            </div>

            <button class="estimate-submit-btn" @click="submitEstimate" :disabled="!canEstimate || estimating">
              {{ estimating ? '估价中...' : '立即估价' }}
            </button>

            <div v-if="estimateResult" class="estimate-result">
              <div class="result-header">
                <h3>估价结果</h3>
              </div>
              <div class="result-content">
                <div class="result-item">
                  <span class="result-label">预估价格：</span>
                  <span class="result-value price">¥{{ estimateResult.estimated_price }}</span>
                </div>
                <div class="result-item">
                  <span class="result-label">活动加价：</span>
                  <span class="result-value bonus">+¥{{ estimateResult.bonus }}</span>
                </div>
                <div class="result-item total">
                  <span class="result-label">最终价格：</span>
                  <span class="result-value total-price">¥{{ estimateResult.total_price }}</span>
                </div>
              </div>
              <button class="create-order-btn" @click="createRecycleOrder">提交回收订单</button>
            </div>
          </div>
        </div>
      </transition>
        </div>
      </div>

      <nav class="bottom-nav" v-if="!isDesktop">
        <button class="nav-item active" @click="router.push('/')">
          <span class="nav-icon">🏠</span>
          <span>首页</span>
        </button>
        <button class="nav-item" @click="showEstimateForm = true">
          <span class="nav-icon">⚡</span>
          <span>估价</span>
        </button>
        <button class="nav-item" @click="goToOrders">
          <span class="nav-icon">📦</span>
          <span>回收车</span>
        </button>
        <button class="nav-item" @click="goMine">
          <span class="nav-icon">👤</span>
          <span>我的</span>
        </button>
        <button class="nav-item" @click="showEstimateForm = true">
          <span class="nav-icon">🔍</span>
          <span>搜索</span>
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()

const searchKeyword = ref('')
const currentDevice = ref(null)
const averagePrice = ref(1605)
const bonus = ref(150)
const showEstimateForm = ref(false)
const estimating = ref(false)
const estimateResult = ref(null)
const isDesktop = ref(false)
const sheetVisible = computed(() => showEstimateForm.value || isDesktop.value)

const categoryList = [
  { label: '手机', icon: '📱', device_type: '手机', brand: '苹果' },
  { label: '平板', icon: '💫', device_type: '平板', brand: '苹果' },
  { label: '笔记本', icon: '💻', device_type: '笔记本', brand: '苹果' },
  { label: '耳机', icon: '🎧', device_type: '手机', brand: '苹果' },
  { label: '游戏机', icon: '🎮', device_type: '手机', brand: '苹果' },
  { label: '无人机', icon: '🛸', device_type: '手机', brand: '苹果' },
  { label: '商城', icon: '🛒', action: 'mall' },
  { label: '更多', icon: '⋯', action: 'more' }
]

const hotItem = {
  name: '苹果 iPhone 13',
  device_type: '手机',
  brand: '苹果',
  model: 'iPhone 13',
  storage: '128GB',
  condition: 'good',
  price: 1605
}

const estimateForm = ref({
  device_type: hotItem.device_type,
  brand: hotItem.brand,
  model: hotItem.model,
  storage: hotItem.storage,
  condition: hotItem.condition
})

const conditions = [
  { value: 'new', label: '全新' },
  { value: 'like_new', label: '几乎全新' },
  { value: 'good', label: '良好' },
  { value: 'fair', label: '一般' },
  { value: 'poor', label: '较差' }
]

const deviceData = {
  手机: {
    苹果: {
      models: ['iPhone 15 Pro Max', 'iPhone 15 Pro', 'iPhone 15', 'iPhone 14 Pro Max', 'iPhone 14 Pro', 'iPhone 14', 'iPhone 13 Pro Max', 'iPhone 13 Pro', 'iPhone 13'],
      storage: ['128GB', '256GB', '512GB', '1TB']
    },
    华为: {
      models: ['Mate 60 Pro', 'Mate 60', 'P60 Pro', 'P60'],
      storage: ['128GB', '256GB', '512GB', '1TB']
    },
    小米: {
      models: ['小米14 Pro', '小米14', '小米13 Ultra', '小米13'],
      storage: ['128GB', '256GB', '512GB', '1TB']
    },
    vivo: {
      models: ['X100 Pro', 'X100'],
      storage: ['256GB', '512GB']
    },
    OPPO: {
      models: ['Find X6 Pro', 'Find X6'],
      storage: ['256GB', '512GB']
    }
  },
  平板: {
    苹果: {
      models: ['iPad Pro 12.9', 'iPad Pro 11', 'iPad Air', 'iPad'],
      storage: ['64GB', '128GB', '256GB', '512GB', '1TB']
    },
    华为: {
      models: ['MatePad Pro', 'MatePad'],
      storage: ['64GB', '128GB', '256GB']
    }
  },
  笔记本: {
    苹果: {
      models: ['MacBook Pro 16', 'MacBook Pro 14', 'MacBook Air'],
      storage: ['256GB', '512GB', '1TB', '2TB']
    },
    联想: {
      models: ['ThinkPad X1', '小新16'],
      storage: ['512GB', '1TB']
    }
  }
}

const selectedCategory = ref(null)
const categoryPaneRef = ref(null)
const selectedBrand = ref('')
const currentStorage = computed(() => {
  if (!selectedCategory.value?.device_type || !selectedBrand.value) return ''
  const storageList = deviceData[selectedCategory.value.device_type]?.[selectedBrand.value]?.storage
  return storageList?.[0] || ''
})

const categoryBrands = computed(() => {
  if (!selectedCategory.value?.device_type) return {}
  return deviceData[selectedCategory.value.device_type] || {}
})

const brandList = computed(() => Object.keys(categoryBrands.value))
const modelList = computed(() => {
  if (!selectedBrand.value) return []
  return categoryBrands.value[selectedBrand.value]?.models || []
})

const availableBrands = computed(() => {
  if (!estimateForm.value.device_type) return []
  return Object.keys(deviceData[estimateForm.value.device_type] || {})
})

const availableModels = computed(() => {
  if (!estimateForm.value.device_type || !estimateForm.value.brand) return []
  return deviceData[estimateForm.value.device_type]?.[estimateForm.value.brand]?.models || []
})

const availableStorage = computed(() => {
  if (!estimateForm.value.device_type || !estimateForm.value.brand) return []
  return deviceData[estimateForm.value.device_type]?.[estimateForm.value.brand]?.storage || []
})

const canEstimate = computed(() => {
  return (
    estimateForm.value.device_type &&
    estimateForm.value.brand &&
    estimateForm.value.model &&
    estimateForm.value.storage &&
    estimateForm.value.condition
  )
})

const onBrandChange = () => {
  estimateForm.value.model = ''
  estimateForm.value.storage = ''
}

const onModelChange = () => {
  estimateForm.value.storage = ''
}

const openEstimator = (preset) => {
  if (preset) {
    estimateForm.value.device_type = preset.device_type || estimateForm.value.device_type
    estimateForm.value.brand = preset.brand || estimateForm.value.brand
    estimateForm.value.model = preset.model || ''
    estimateForm.value.storage = preset.storage || ''
    estimateForm.value.condition = preset.condition || 'good'
  }
  showEstimateForm.value = true
}

const selectCategory = (item) => {
  if (item.action === 'mall') {
    router.push('/products')
    return
  }
  selectedCategory.value = item
  selectedBrand.value = brandList.value[0] || ''
  if (categoryPaneRef.value) {
    categoryPaneRef.value.scrollTop = 0
  }
}

const handleCategoryClick = selectCategory

const selectBrand = (brand) => {
  selectedBrand.value = brand
  if (categoryPaneRef.value) {
    categoryPaneRef.value.scrollTop = 0
  }
}

const submitEstimate = async () => {
  if (!canEstimate.value) {
    ElMessage.warning('请填写完整的设备信息')
    return
  }

  estimating.value = true
  try {
    const res = await api.post('/recycle-orders/estimate/', estimateForm.value)
    estimateResult.value = res.data
    ElMessage.success('估价成功！')
  } catch (error) {
    console.error('估价失败:', error)
    ElMessage.error('估价失败，请稍后重试')
  } finally {
    estimating.value = false
  }
}

const createRecycleOrder = async () => {
  if (!estimateResult.value) {
    ElMessage.warning('请先进行估价')
    return
  }

  try {
    const orderData = {
      ...estimateForm.value,
      estimated_price: estimateResult.value.estimated_price,
      bonus: estimateResult.value.bonus,
      contact_name: '待填写',
      contact_phone: '待填写',
      address: '待填写'
    }

    const res = await api.post('/recycle-orders/', orderData)
    ElMessage.success('回收订单创建成功！')
    router.push(`/recycle-order/${res.data.id}`)
  } catch (error) {
    console.error('创建订单失败:', error)
    ElMessage.error('创建订单失败，请稍后重试')
  }
}

const closeSheet = () => {
  showEstimateForm.value = false
}

const goToOrders = () => {
  router.push('/my-recycle-orders')
}

const goMine = () => {
  router.push('/profile')
}

onMounted(() => {
  // 可根据需要接入设备识别
  // currentDevice.value = detectDevice()
  const onResize = () => {
    isDesktop.value = window.innerWidth >= 960
  }
  onResize()
  window.addEventListener('resize', onResize)
  onUnmounted(() => window.removeEventListener('resize', onResize))
  if (!selectedCategory.value && categoryList.length) {
    selectedCategory.value = categoryList[0]
    selectedBrand.value = brandList.value[0] || ''
  }
})
</script>

<style scoped>
.recycle-page {
  min-height: 100vh;
  height: 100vh;
  background: #f7f8fb;
  overflow: hidden;
}

.mobile-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 16px 96px;
  height: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.content-viewport {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}

.main-column {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  padding: 10px 12px;
  border-radius: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
}

.top-title {
  font-weight: 800;
  font-size: 16px;
  color: #111;
}

.icon-btn {
  border: none;
  background: #f3f4f6;
  border-radius: 10px;
  padding: 6px 10px;
  cursor: pointer;
}

.top-actions {
  display: flex;
  gap: 8px;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
}

.cart-btn {
  border: none;
  background: #fff;
  border-radius: 12px;
  padding: 10px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.chip-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
}

.chip {
  padding: 8px 14px;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  background: #f8fafc;
  cursor: pointer;
  white-space: nowrap;
}

.chip.active {
  border-color: #111;
  background: #eef2ff;
  color: #111;
  font-weight: 700;
}

.category-browser {
  display: grid;
  grid-template-columns: 0.9fr 2.1fr;
  gap: 12px;
  background: #fff;
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
  min-height: 480px;
}

.brand-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.brand-item {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #f8fafc;
  cursor: pointer;
  text-align: left;
}

.brand-item.active {
  border-color: #111;
  background: #eef2ff;
  font-weight: 700;
  color: #111;
}

.product-pane {
  background: #f9fafb;
  border: 1px solid #eef1f4;
  border-radius: 12px;
  padding: 8px;
  max-height: 520px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.product-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  border-radius: 12px;
  padding: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
  cursor: pointer;
  border: 1px solid #f1f2f5;
}

.product-thumb {
  width: 40px;
  height: 40px;
  background: #f3f4f6;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-info {
  flex: 1;
}

.product-name {
  font-weight: 700;
  color: #111;
}

.product-sub {
  font-size: 12px;
  color: #777;
}

.product-price {
  font-weight: 700;
  color: #111;
}

.hot-section {
  margin-top: 14px;
}

.hot-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px 8px;
}

.hot-title {
  font-weight: 800;
  color: #111;
}

.hot-more {
  border: none;
  background: transparent;
  color: #777;
  font-size: 13px;
  cursor: pointer;
}

.hot-card {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 12px;
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.06);
}

.hot-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.hot-name {
  font-size: 15px;
  font-weight: 700;
  color: #111;
}

.hot-price {
  font-size: 20px;
  font-weight: 800;
  color: #111;
}

.hot-sub {
  font-size: 12px;
  color: #777;
}

.hot-cta {
  margin-top: 6px;
  padding: 10px 12px;
  background: linear-gradient(135deg, #111, #1f2937);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.hot-img {
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border-radius: 12px;
  min-height: 90px;
}

.quick-stats {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  align-items: stretch;
}

.stat {
  background: #fff;
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.04);
}

.stat-label {
  font-size: 12px;
  color: #888;
}

.stat-value {
  margin-top: 6px;
  font-size: 16px;
  font-weight: 800;
  color: #111;
}

.primary-btn {
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #111, #1f2937);
  color: #fff;
  font-weight: 800;
  font-size: 15px;
  cursor: pointer;
  box-shadow: 0 12px 24px rgba(17, 24, 39, 0.2);
}

.floating-result {
  margin-top: 14px;
  background: #fff;
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.04);
}

.result-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-tag {
  padding: 4px 8px;
  background: #111;
  color: #fff;
  border-radius: 8px;
  font-size: 12px;
}

.result-price {
  font-size: 20px;
  font-weight: 800;
  color: #111;
}

.result-source {
  font-size: 12px;
  color: #777;
}

.primary-outline {
  margin-top: 10px;
  width: 100%;
  border: 1px solid #111;
  background: transparent;
  color: #111;
  border-radius: 12px;
  padding: 10px 0;
  font-weight: 700;
  cursor: pointer;
}

.estimate-sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  top: 0;
  display: flex;
  align-items: flex-end;
  z-index: 999;
}

.estimate-sheet.desktop {
  position: static;
  display: block;
  z-index: 1;
  align-items: stretch;
}

.estimate-sheet.desktop .sheet-mask {
  display: none;
}

.estimate-sheet.desktop .sheet-panel {
  border-radius: 16px;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.06);
  max-height: none;
  position: sticky;
  top: 8px;
}

.sheet-mask {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
}

.sheet-panel {
  position: relative;
  background: #fff;
  width: 100%;
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
  padding: 16px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 -10px 24px rgba(0, 0, 0, 0.08);
}

.sheet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.sheet-title {
  font-size: 18px;
  font-weight: 800;
  color: #111;
}

.sheet-sub {
  font-size: 12px;
  color: #777;
}

.close-btn {
  border: none;
  background: #f5f5f5;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 700;
  color: #222;
  font-size: 14px;
}

.form-select {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  background: #f8fafc;
}

.condition-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.condition-option {
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  text-align: center;
  cursor: pointer;
  background: #f8fafc;
}

.condition-option.active {
  border-color: #111;
  background: #eef2ff;
  color: #111;
}

.condition-radio {
  display: none;
}

.estimate-submit-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #111, #1f2937);
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  margin-top: 4px;
}

.estimate-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.estimate-result {
  margin-top: 16px;
  padding: 12px;
  border-radius: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.result-header h3 {
  margin: 0 0 10px;
  font-weight: 800;
  color: #111;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #444;
}

.result-item.total {
  border-top: 1px dashed #e5e7eb;
  padding-top: 8px;
}

.result-value.price {
  color: #111;
  font-weight: 700;
}

.result-value.bonus {
  color: #16a34a;
  font-weight: 700;
}

.result-value.total-price {
  font-size: 18px;
  font-weight: 800;
  color: #111;
}

.create-order-btn {
  width: 100%;
  margin-top: 10px;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #111, #1f2937);
  color: #fff;
  font-weight: 800;
  cursor: pointer;
}

.sheet-enter-active,
.sheet-leave-active {
  transition: all 0.25s ease;
}

.sheet-enter-from .sheet-panel,
.sheet-leave-to .sheet-panel {
  transform: translateY(100%);
}

.sheet-enter-from .sheet-mask,
.sheet-leave-to .sheet-mask {
  opacity: 0;
}

.bottom-nav {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 64px;
  background: #fff;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  border-top: 1px solid #eee;
  z-index: 998;
}

.nav-item {
  border: none;
  background: transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #555;
  cursor: pointer;
}

.nav-item.active {
  color: #111;
  font-weight: 800;
}

.nav-icon {
  font-size: 18px;
  line-height: 1;
}

.category-browser {
  display: grid;
  grid-template-columns: 0.9fr 2.1fr;
  gap: 12px;
  background: #fff;
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
  min-height: 340px;
}

.category-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #f8fafc;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.category-nav-item.active {
  border-color: #111;
  background: #eef2ff;
  color: #111;
  font-weight: 700;
}

.category-pane {
  background: #f9fafb;
  border: 1px solid #eef1f4;
  border-radius: 12px;
  padding: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.pane-brand {
  border-bottom: 1px solid #eef1f4;
  padding: 8px 0;
}

.pane-brand:last-child {
  border-bottom: none;
}

.pane-brand-name {
  font-weight: 700;
  margin-bottom: 6px;
  color: #111;
}

.pane-models {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.model-pill {
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #f8fafc;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.model-pill:hover {
  border-color: #111;
  background: #eef2ff;
  color: #111;
}

@media (min-width: 960px) {
  .content-grid {
    display: grid;
    grid-template-columns: 1.8fr 1fr;
    align-items: start;
    overflow: visible;
  }

  .mobile-shell {
    padding: 20px 20px 32px;
  }

  .hero-card {
    min-height: 160px;
  }

  .feature-row {
    grid-template-columns: repeat(4, 1fr);
  }

  .category-grid {
    grid-template-columns: repeat(5, 1fr);
  }

  .quick-stats {
    grid-template-columns: repeat(3, 1fr);
  }

  .estimate-sheet.desktop {
    position: sticky;
    top: 20px;
  }

  .sheet-panel {
    border-radius: 16px;
  }
}

@media (max-width: 360px) {
  .category-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
