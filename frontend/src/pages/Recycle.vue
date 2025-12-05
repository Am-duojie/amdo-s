<template>
  <div class="recycle-page">
    
    
    <div class="recycle-container">
      <!-- 顶部横幅 -->
      <div class="recycle-banner">
        <div class="banner-content">
          <h1 class="banner-title">♻️ 极速回收</h1>
          <p class="banner-subtitle">上门回收秒拿钱</p>
        </div>
      </div>

      <!-- 搜索框 -->
      <div class="search-section">
        <div class="search-box">
          <input 
            v-model="searchKeyword" 
            placeholder="iPhone 13" 
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button class="search-btn" @click="handleSearch">🔍</button>
        </div>
      </div>

      <!-- 本机识别（如果支持） -->
      <div v-if="currentDevice" class="current-device-card">
        <div class="device-info">
          <div class="device-image">
            <span class="device-icon">📱</span>
          </div>
          <div class="device-details">
            <div class="device-name">本机: {{ currentDevice }}</div>
            <div class="device-price-info">
              <span class="price-label">近7日均价</span>
              <span class="price-value">¥{{ averagePrice }}</span>
              <span class="bonus-info">含加价¥{{ bonus }}</span>
            </div>
          </div>
          <button class="estimate-btn" @click="goToEstimate">精准估价</button>
        </div>
      </div>

      <!-- 优惠活动 -->
      <div class="promo-section">
        <div class="promo-card" @click="handlePromo('phone')">
          <div class="promo-content">
            <span class="promo-amount">¥500 最高</span>
            <span class="promo-desc">12月手机回收...</span>
          </div>
          <button class="promo-btn">去使用</button>
        </div>
        <div class="promo-card" @click="handlePromo('digital')">
          <div class="promo-content">
            <span class="promo-amount">¥500 最高</span>
            <span class="promo-desc">12月数码回收...</span>
          </div>
          <button class="promo-btn">去使用</button>
        </div>
      </div>

      <!-- 服务保障 -->
      <div class="guarantee-section">
        <div class="guarantee-item">
          <span class="guarantee-icon">✓</span>
          <span class="guarantee-text">超时赔</span>
        </div>
        <div class="guarantee-item">
          <span class="guarantee-icon">✓</span>
          <span class="guarantee-text">护隐私</span>
        </div>
        <div class="guarantee-item">
          <span class="guarantee-icon">✓</span>
          <span class="guarantee-text">丢损赔</span>
        </div>
        <div class="guarantee-item">
          <span class="guarantee-icon">✓</span>
          <span class="guarantee-text">可复检</span>
        </div>
      </div>

      <!-- 设备类型选择 -->
      <div class="device-type-section">
        <h2 class="section-title">
          手机数码
          <span class="section-subtitle">当面验机现场拿钱</span>
          <span class="hot-tag">12.1-12.15加价¥500</span>
        </h2>
        
        <div class="device-grid">
          <div 
            v-for="device in deviceTypes" 
            :key="device.type"
            class="device-item"
            @click="selectDevice(device)"
          >
            <div class="device-icon-large">{{ device.icon }}</div>
            <div class="device-label">{{ device.label }}</div>
            <div v-if="device.hot" class="hot-badge">热</div>
          </div>
        </div>
      </div>

      <!-- 估价表单 -->
      <div v-if="showEstimateForm" class="estimate-form-section">
        <h2 class="form-title">精准估价</h2>
        
        <div class="form-content">
          <div class="form-group">
            <label>设备类型</label>
            <select v-model="estimateForm.device_type" class="form-select">
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

          <button class="estimate-submit-btn" @click="submitEstimate" :disabled="!canEstimate">
            {{ estimating ? '估价中...' : '立即估价' }}
          </button>
        </div>

        <!-- 估价结果 -->
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

      <!-- 立即回收按钮 -->
      <div class="recycle-action">
        <button class="recycle-now-btn" @click="showEstimateForm = true">
          <span class="recycle-icon">♻️</span>
          立即回收
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()

const searchKeyword = ref('')
const currentDevice = ref(null) // 可以检测用户设备
const averagePrice = ref(1838)
const bonus = ref(150)
const showEstimateForm = ref(false)
const estimating = ref(false)
const estimateResult = ref(null)

const deviceTypes = [
  { type: 'phone', label: '苹果', icon: '🍎', hot: true },
  { type: 'phone', label: '华为', icon: '📱' },
  { type: 'phone', label: '小米', icon: '📱' },
  { type: 'phone', label: 'OPPO', icon: '📱' },
  { type: 'phone', label: 'VIVO', icon: '📱' },
  { type: 'laptop', label: '笔记本', icon: '💻' },
  { type: 'tablet', label: '平板', icon: '📱' },
  { type: 'headphone', label: '耳机', icon: '🎧' },
  { type: 'camera', label: '相机', icon: '📷' },
  { type: 'more', label: '更多', icon: '⋯' },
]

const estimateForm = ref({
  device_type: '',
  brand: '',
  model: '',
  storage: '',
  condition: 'good'
})

const conditions = [
  { value: 'new', label: '全新' },
  { value: 'like_new', label: '几乎全新' },
  { value: 'good', label: '良好' },
  { value: 'fair', label: '一般' },
  { value: 'poor', label: '较差' }
]

// 品牌和型号数据
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
  return estimateForm.value.device_type && 
         estimateForm.value.brand && 
         estimateForm.value.model && 
         estimateForm.value.storage &&
         estimateForm.value.condition
})

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    // 可以跳转到搜索结果或直接开始估价
    estimateForm.value.model = searchKeyword.value
    showEstimateForm.value = true
  }
}

const selectDevice = (device) => {
  if (device.type === 'phone') {
    estimateForm.value.device_type = '手机'
    estimateForm.value.brand = device.label === '苹果' ? '苹果' : device.label
    showEstimateForm.value = true
  } else if (device.type === 'laptop') {
    estimateForm.value.device_type = '笔记本'
    showEstimateForm.value = true
  } else if (device.type === 'tablet') {
    estimateForm.value.device_type = '平板'
    showEstimateForm.value = true
  }
}

const onBrandChange = () => {
  estimateForm.value.model = ''
  estimateForm.value.storage = ''
}

const onModelChange = () => {
  estimateForm.value.storage = ''
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

const goToEstimate = () => {
  showEstimateForm.value = true
}

const handlePromo = (type) => {
  ElMessage.info(`跳转到${type === 'phone' ? '手机' : '数码'}回收活动页面`)
}

onMounted(() => {
  // 可以尝试检测用户设备
  // currentDevice.value = detectDevice()
})
</script>

<style scoped>
.recycle-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #fff5e6 0%, #ffffff 100%);
}

.recycle-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 横幅 */
.recycle-banner {
  background: linear-gradient(135deg, #ff6600, #ff8833);
  border-radius: 16px;
  padding: 40px 30px;
  margin-bottom: 24px;
  color: #fff;
  text-align: center;
  box-shadow: 0 8px 24px rgba(255, 102, 0, 0.2);
}

.banner-title {
  font-size: 36px;
  font-weight: 900;
  margin-bottom: 8px;
}

.banner-subtitle {
  font-size: 18px;
  opacity: 0.95;
}

/* 搜索框 */
.search-section {
  margin-bottom: 24px;
}

.search-box {
  display: flex;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.search-input {
  flex: 1;
  padding: 16px 20px;
  border: none;
  font-size: 16px;
  outline: none;
}

.search-btn {
  padding: 16px 24px;
  background: linear-gradient(135deg, #ff6600, #ff8833);
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
}

/* 本机卡片 */
.current-device-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.device-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.device-image {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.device-icon {
  font-size: 40px;
}

.device-details {
  flex: 1;
}

.device-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.device-price-info {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.price-label {
  font-size: 14px;
  color: #999;
}

.price-value {
  font-size: 28px;
  font-weight: 900;
  color: #ff4444;
}

.bonus-info {
  font-size: 14px;
  color: #ff6600;
}

.estimate-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #ff6600, #ff8833);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

/* 优惠活动 */
.promo-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.promo-card {
  background: #fff;
  border: 2px solid #ff6600;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s;
}

.promo-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 102, 0, 0.2);
}

.promo-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.promo-amount {
  font-size: 20px;
  font-weight: 900;
  color: #ff4444;
}

.promo-desc {
  font-size: 14px;
  color: #666;
}

.promo-btn {
  padding: 8px 16px;
  background: #ff6600;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

/* 服务保障 */
.guarantee-section {
  display: flex;
  justify-content: space-around;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.guarantee-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.guarantee-icon {
  width: 32px;
  height: 32px;
  background: #4caf50;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
}

.guarantee-text {
  font-size: 14px;
  color: #666;
}

/* 设备类型 */
.device-type-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-subtitle {
  font-size: 14px;
  font-weight: 400;
  color: #666;
}

.hot-tag {
  background: #ff4444;
  color: #fff;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.device-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.device-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #f8f8f8;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.device-item:hover {
  background: #fff5e6;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(255, 102, 0, 0.15);
}

.device-icon-large {
  font-size: 40px;
  margin-bottom: 8px;
}

.device-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.hot-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #ff4444;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

/* 估价表单 */
.estimate-form-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.form-select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
}

.form-select:focus {
  border-color: #ff6600;
}

.condition-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.condition-option {
  flex: 1;
  min-width: 100px;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.condition-option.active {
  border-color: #ff6600;
  background: #fff5e6;
  color: #ff6600;
}

.condition-radio {
  display: none;
}

.estimate-submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #ff6600, #ff8833);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.estimate-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 102, 0, 0.3);
}

.estimate-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 估价结果 */
.estimate-result {
  margin-top: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #fff5e6, #fff);
  border-radius: 12px;
  border: 2px solid #ff6600;
}

.result-header h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 20px;
  color: #ff6600;
}

.result-content {
  margin-bottom: 24px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e0e0e0;
}

.result-item.total {
  border-bottom: none;
  border-top: 2px solid #ff6600;
  padding-top: 16px;
  margin-top: 8px;
}

.result-label {
  font-size: 16px;
  color: #666;
}

.result-value {
  font-size: 18px;
  font-weight: 600;
}

.result-value.price {
  color: #ff4444;
}

.result-value.bonus {
  color: #4caf50;
}

.result-value.total-price {
  font-size: 28px;
  font-weight: 900;
  color: #ff6600;
}

.create-order-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #ff6600, #ff8833);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.create-order-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 102, 0, 0.3);
}

/* 立即回收按钮 */
.recycle-action {
  text-align: center;
  margin-top: 32px;
  margin-bottom: 40px;
}

.recycle-now-btn {
  padding: 20px 60px;
  background: linear-gradient(135deg, #ff6600, #ff8833);
  color: #fff;
  border: none;
  border-radius: 50px;
  font-size: 20px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(255, 102, 0, 0.3);
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.recycle-now-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(255, 102, 0, 0.4);
}

.recycle-icon {
  font-size: 24px;
}

/* 响应式 */
@media (max-width: 768px) {
  .device-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .promo-section {
    grid-template-columns: 1fr;
  }
  
  .guarantee-section {
    flex-wrap: wrap;
    gap: 16px;
  }
}
</style>
