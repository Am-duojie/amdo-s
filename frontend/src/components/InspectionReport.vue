<template>
  <div class="inspection-report">
    <!-- 左侧侧边栏 -->
    <aside class="sidebar">
      <div class="summary-card">
        <div class="cover-img">
          <img v-if="baseInfo.coverImage" :src="baseInfo.coverImage" alt="商品图片" />
          <span v-else>{{ baseInfo.model }} 实拍图</span>
        </div>
        <h2 class="product-title">{{ baseInfo.model }}</h2>
        <div class="tags-row">
          <span class="tag highlight">{{ baseInfo.level }}</span>
          <span class="tag">{{ baseInfo.spec }}</span>
          <span class="tag">{{ baseInfo.color }}</span>
        </div>
        <div class="price-section">
          <div class="price-label">预估回收价</div>
          <div class="price-val">¥{{ baseInfo.price }}</div>
        </div>
      </div>
    </aside>

    <!-- 右侧内容区 -->
    <main class="content">
      <div class="section-header">
        <div class="section-title">检测详情</div>
        <div class="toggle-btn" @click="toggleAll">
          {{ isAllExpanded ? '全部收起' : '全部展开' }}
        </div>
      </div>

      <!-- 检测项卡片 -->
      <div class="check-card" v-for="(cat, cIdx) in reportData" :key="cIdx">
        <div 
          class="card-head" 
          :class="{ active: cat.expanded }" 
          @click="cat.expanded = !cat.expanded"
        >
          <span class="head-title">{{ cat.title }}</span>
          <div class="head-status">
            <span 
              :class="cat.hasIssues ? 'status-text-red' : 'status-text-green'"
            >
              <span style="font-size:16px; margin-right:4px;">
                {{ cat.hasIssues ? '⚠' : '✓' }}
              </span>
              {{ cat.hasIssues ? `${cat.issueCount}项异常` : `${cat.totalCount}项全部通过` }}
            </span>
            <span class="arrow" :class="{ down: cat.expanded }">▼</span>
          </div>
        </div>

        <div class="card-body" v-show="cat.expanded">
          <!-- 图片画廊 -->
          <div class="gallery-box" v-if="cat.images && cat.images.length">
            <div 
              class="thumb" 
              v-for="(img, idx) in cat.images" 
              :key="idx"
              @click="openImageViewer(img)"
            >
              <img :src="img" :alt="`检测图${idx + 1}`" />
            </div>
          </div>

          <!-- 检测项分组 -->
          <div class="group-container" v-for="(group, gIdx) in cat.groups" :key="gIdx">
            <div class="group-title" v-if="group.name">{{ group.name }}</div>
            <div class="items-grid">
              <div class="item-row" v-for="(item, iIdx) in group.items" :key="iIdx">
                <span class="label">{{ item.label }}</span>
                <span class="dots"></span>
                <span 
                  class="value" 
                  :class="{ 
                    light: isLightText(item.value),
                    error: !item.pass 
                  }"
                >
                  {{ item.value }}
                  <span v-if="item.pass" class="icon-check">✓</span>
                  <button 
                    v-if="!item.pass && item.image" 
                    class="view-image-btn"
                    @click="openImageViewer(item.image)"
                  >
                    查看异常图
                  </button>
                </span>
              </div>
            </div>
          </div>

          <!-- 底部备注 -->
          <div class="footer-note" v-if="cat.footer">
            <span class="note-label">{{ cat.footer.label }}</span>
            <span class="note-val">{{ cat.footer.value }}</span>
          </div>
        </div>
      </div>
    </main>

    <!-- 图片查看器弹窗 -->
    <el-dialog
      v-model="imageViewerVisible"
      title="检测图片"
      width="800px"
      :close-on-click-modal="true"
      class="image-viewer-dialog"
    >
      <div class="image-viewer-content">
        <img :src="currentImage" alt="检测图片" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  // 商品基本信息
  productId: {
    type: [String, Number],
    required: true
  },
  // 可选：直接传入报告数据
  reportDataProp: {
    type: Object,
    default: null
  }
})

// 基本信息
const baseInfo = ref({
  model: '',
  level: '',
  spec: '',
  color: '',
  price: '',
  coverImage: ''
})

// 报告数据
const reportData = ref([])

// 展开/收起状态
const isAllExpanded = ref(true)

// 图片查看器
const imageViewerVisible = ref(false)
const currentImage = ref('')

// 判断是否为浅色文字
const isLightText = (text) => {
  return text && (text.includes('几乎不可见') || text.includes('无'))
}

// 切换全部展开/收起
const toggleAll = () => {
  isAllExpanded.value = !isAllExpanded.value
  reportData.value.forEach(cat => {
    cat.expanded = isAllExpanded.value
  })
}

// 打开图片查看器
const openImageViewer = (imageUrl) => {
  currentImage.value = imageUrl
  imageViewerVisible.value = true
}

// 处理后端数据，转换为组件需要的格式
const processReportData = (rawData) => {
  return rawData.map(category => {
    let totalCount = 0
    let issueCount = 0
    
    // 统计总数和异常数
    category.groups.forEach(group => {
      group.items.forEach(item => {
        totalCount++
        if (!item.pass) {
          issueCount++
        }
      })
    })

    return {
      ...category,
      expanded: true,
      totalCount,
      issueCount,
      hasIssues: issueCount > 0
    }
  })
}

// API 请求
const fetchInspectionReport = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/verified-products/${props.productId}/inspection_report/`)
    if (!response.ok) {
      throw new Error('Failed to fetch inspection report')
    }
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching inspection report:', error)
    // 返回空数据结构
    return {
      baseInfo: {
        model: '',
        level: '',
        spec: '',
        color: '',
        price: '',
        coverImage: ''
      },
      categories: []
    }
  }
}

// 初始化数据
onMounted(async () => {
  if (props.reportDataProp) {
    // 如果直接传入数据，使用传入的数据
    baseInfo.value = props.reportDataProp.baseInfo
    reportData.value = processReportData(props.reportDataProp.categories)
  } else {
    // 否则从 API 获取
    const data = await fetchInspectionReport()
    baseInfo.value = data.baseInfo
    reportData.value = processReportData(data.categories)
  }
})
</script>

<style scoped>
/* 全局变量 */
:root {
  --primary-color: #52c41a;
  --danger-color: #ff4d4f;
  --link-color: #1890ff;
  --text-main: #262626;
  --text-normal: #595959;
  --text-light: #8c8c8c;
  --bg-body: #f5f7fa;
  --border-light: #f0f0f0;
}

/* 主布局 */
.inspection-report {
  display: flex;
  gap: 30px;
  align-items: flex-start;
  padding: 20px 0;
}

/* 左侧侧边栏 */
.sidebar {
  width: 320px;
  flex-shrink: 0;
  position: sticky;
  top: 24px;
}

.summary-card {
  background: #fff;
  border-radius: 16px;
  padding: 30px 24px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.04);
  transition: transform 0.3s;
}

.summary-card:hover {
  transform: translateY(-2px);
}

.cover-img {
  width: 100%;
  height: 260px;
  background: linear-gradient(145deg, #f6f7f9 0%, #eaebef 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b0b0b0;
  font-size: 14px;
  margin-bottom: 24px;
  font-weight: 500;
  overflow: hidden;
}

.cover-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-title {
  font-size: 24px;
  margin: 0 0 16px 0;
  color: var(--text-main);
  font-weight: 700;
  letter-spacing: -0.5px;
}

.tags-row {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.tag {
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 12px;
  background: #f5f5f5;
  color: var(--text-normal);
  font-weight: 500;
}

.tag.highlight {
  background: #fff1f0;
  color: var(--danger-color);
  border: 1px solid #ffccc7;
  font-weight: 600;
}

.price-section {
  border-top: 1px dashed #e8e8e8;
  padding-top: 20px;
  margin-top: 10px;
}

.price-label {
  font-size: 13px;
  color: var(--text-light);
  margin-bottom: 4px;
}

.price-val {
  font-size: 36px;
  color: var(--danger-color);
  font-weight: 800;
  font-family: "DIN Alternate", "Roboto", sans-serif;
  letter-spacing: -1px;
}

/* 右侧内容区 */
.content {
  flex: 1;
  min-width: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-main);
  position: relative;
  padding-left: 16px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 4px;
  bottom: 4px;
  width: 4px;
  background: var(--primary-color);
  border-radius: 4px;
}

.toggle-btn {
  color: var(--link-color);
  font-size: 14px;
  cursor: pointer;
  user-select: none;
  transition: 0.2s;
  font-weight: 500;
}

.toggle-btn:hover {
  opacity: 0.8;
}

/* 检测项卡片 */
.check-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  margin-bottom: 20px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.02);
}

.card-head {
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  background: #fff;
  transition: background 0.2s;
}

.card-head:hover {
  background: #fafafa;
}

.card-head.active {
  border-bottom: 1px solid var(--border-light);
}

.head-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-main);
}

.head-status {
  font-size: 14px;
  color: var(--text-light);
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-text-green {
  color: var(--primary-color);
  font-weight: 500;
}

.status-text-red {
  color: var(--danger-color);
  font-weight: 500;
}

.arrow {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: #bfbfbf;
  font-size: 12px;
  margin-left: 8px;
}

.arrow.down {
  transform: rotate(180deg);
}

.card-body {
  padding: 10px 30px 30px 30px;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 图片画廊 */
.gallery-box {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  margin-bottom: 30px;
  padding: 20px 0 10px 0;
  scrollbar-width: none;
}

.gallery-box::-webkit-scrollbar {
  display: none;
}

.thumb {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  background: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #ccc;
  overflow: hidden;
  transition: all 0.2s;
  cursor: pointer;
}

.thumb:hover {
  border-color: var(--primary-color);
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 分组 */
.group-container {
  margin-bottom: 10px;
}

.group-title {
  font-size: 15px;
  color: var(--text-main);
  font-weight: 700;
  margin-bottom: 16px;
  margin-top: 24px;
}

.group-container:first-child .group-title {
  margin-top: 10px;
}

.items-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  column-gap: 60px;
  row-gap: 16px;
}

/* 检测项 */
.item-row {
  display: flex;
  align-items: center;
  font-size: 14px;
  height: 32px;
}

.label {
  color: var(--text-light);
  white-space: nowrap;
  font-size: 14px;
}

.dots {
  flex: 1;
  border-bottom: 1px dashed #e8e8e8;
  margin: 0 16px;
  position: relative;
  top: -4px;
}

.value {
  color: var(--text-main);
  font-weight: 500;
  display: flex;
  align-items: center;
  white-space: nowrap;
  gap: 8px;
}

.value.light {
  color: #b0b0b0;
  font-weight: 400;
}

.value.error {
  color: var(--danger-color);
  font-weight: 600;
}

.icon-check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  color: var(--primary-color);
  font-weight: bold;
  font-size: 14px;
}

/* 查看异常图按钮 */
.view-image-btn {
  padding: 2px 8px;
  background: var(--danger-color);
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.view-image-btn:hover {
  background: #ff7875;
  transform: translateY(-1px);
}

/* 底部备注 */
.footer-note {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  font-size: 15px;
  color: var(--text-main);
}

.note-label {
  font-weight: 600;
}

.note-val {
  color: var(--text-light);
}

/* 图片查看器弹窗 */
.image-viewer-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.image-viewer-content img {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 8px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .inspection-report {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    position: static;
  }

  .items-grid {
    grid-template-columns: 1fr;
    column-gap: 0;
  }
}
</style>
