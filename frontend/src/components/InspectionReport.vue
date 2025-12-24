<template>
  <div class="inspection-report" :class="{ compact }">
    <template v-if="!compact && showSidebar">
      <aside class="sidebar">
        <div class="summary-card">
          <div class="cover-img">
            <img v-if="baseInfo.coverImage" :src="baseInfo.coverImage" alt="商品图片" />
            <span v-else>{{ baseInfo.model }} 示意图</span>
          </div>
          <h2 class="product-title">{{ baseInfo.model }}</h2>
          <div class="tags-row">
            <span class="tag highlight">{{ baseInfo.level }}</span>
            <span class="tag" v-if="baseInfo.spec">{{ baseInfo.spec }}</span>
            <span class="tag" v-if="baseInfo.color">{{ baseInfo.color }}</span>
          </div>
          <div class="price-section" v-if="baseInfo.price">
            <div class="price-label">预估回收价</div>
            <div class="price-val">¥{{ baseInfo.price }}</div>
          </div>
        </div>
      </aside>
    </template>

    <main class="content">
      <div class="section-header" :class="{ compact }">
        <div class="section-title">检测详情</div>
        <div class="toggle-btn" @click="toggleAll">
          {{ isAllExpanded ? '全部收起' : '全部展开' }}
        </div>
      </div>

      <div v-if="compact && showCompactSummary" class="compact-summary">
        <div class="tag-row">
          <el-tag size="small" type="success">{{ baseInfo.level }}</el-tag>
          <el-tag size="small" type="info" v-if="baseInfo.spec">{{ baseInfo.spec }}</el-tag>
          <el-tag size="small" v-if="baseInfo.color">{{ baseInfo.color }}</el-tag>
        </div>
        <div class="meta-row">
          <span v-if="baseInfo.model">{{ baseInfo.model }}</span>
          <span v-if="baseInfo.price">· 预估价：¥{{ baseInfo.price }}</span>
        </div>
      </div>

      <div
        class="check-card"
        :class="{ compact }"
        v-for="(cat, cIdx) in reportData"
        :key="cIdx"
      >
        <div
          class="card-head"
          :class="{ active: cat.expanded }"
          @click="cat.expanded = !cat.expanded"
        >
          <span class="head-title">{{ cat.title }}</span>
          <div class="head-status">
            <span :class="cat.hasIssues ? 'status-text-red' : 'status-text-green'">
              <span style="font-size:16px; margin-right:4px;">
                {{ cat.hasIssues ? '⚠' : '✔' }}
              </span>
              {{ cat.hasIssues ? `${cat.issueCount}项异常` : `${cat.totalCount}项全部通过` }}
            </span>
            <span class="arrow" :class="{ down: cat.expanded }">▾</span>
          </div>
        </div>

        <div class="card-body" v-show="cat.expanded">
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
                  <span v-if="item.pass" class="icon-check">✔</span>
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

          <div class="footer-note" v-if="cat.footer">
            <span class="note-label">{{ cat.footer.label }}</span>
            <span class="note-val">{{ cat.footer.value }}</span>
          </div>
        </div>
      </div>
    </main>

    <el-image-viewer
      v-if="imageViewerVisible"
      :url-list="[currentImage]"
      :initial-index="0"
      teleported
      show-progress
      @close="imageViewerVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  productId: {
    type: [String, Number],
    required: true
  },
  reportDataProp: {
    type: Object,
    default: null
  },
  compact: {
    type: Boolean,
    default: false
  },
  defaultExpanded: {
    type: Boolean,
    default: true
  },
  showCompactSummary: {
    type: Boolean,
    default: true
  },
  showSidebar: {
    type: Boolean,
    default: false
  }
})

const baseInfo = ref({
  model: '',
  level: '',
  spec: '',
  color: '',
  price: '',
  coverImage: ''
})

const reportData = ref([])
const isAllExpanded = ref(props.defaultExpanded)
const imageViewerVisible = ref(false)
const currentImage = ref('')

const isLightText = (text) => {
  return text && (text.includes('几乎不可见') || text.includes('无'))
}

const toggleAll = () => {
  isAllExpanded.value = !isAllExpanded.value
  reportData.value.forEach(cat => {
    cat.expanded = isAllExpanded.value
  })
}

const openImageViewer = (img) => {
  currentImage.value = img
  imageViewerVisible.value = true
}

const processReportData = (categories = [], expanded = true) => {
  return categories.map(cat => {
    const groups = cat.groups || []
    const items = groups.flatMap(g => g.items || [])
    const totalCount = items.length
    const issueCount = items.filter(i => i.pass === false || i.pass === 'fail' || i.value === 'fail').length
    return {
      ...cat,
      groups,
      expanded,
      totalCount,
      issueCount,
      hasIssues: issueCount > 0
    }
  })
}

const fetchInspectionReport = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/verified-products/${props.productId}/inspection_report/`)
    if (!response.ok) throw new Error('Failed to fetch inspection report')
    return await response.json()
  } catch (error) {
    console.error('Error fetching inspection report:', error)
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

onMounted(async () => {
  if (props.reportDataProp) {
    baseInfo.value = props.reportDataProp.baseInfo || baseInfo.value
    reportData.value = processReportData(props.reportDataProp.categories || [], props.defaultExpanded)
  } else {
    const data = await fetchInspectionReport()
    baseInfo.value = data.baseInfo || baseInfo.value
    reportData.value = processReportData(data.categories || [], props.defaultExpanded)
  }
})
</script>

<style scoped>
:root {
  --primary-color: #52c41a;
  --danger-color: #ff4d4f;
  --text-main: #262626;
  --text-normal: #595959;
  --text-light: #8c8c8c;
  --bg-body: #f5f7fa;
  --border-light: #f0f0f0;
}

.inspection-report {
  display: flex;
  gap: 30px;
  align-items: flex-start;
  padding: 20px 0;
}

.inspection-report.compact {
  display: block;
  padding: 0;
}

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

.summary-card:hover { transform: translateY(-2px); }

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

.cover-img img { width: 100%; height: 100%; object-fit: cover; }

.product-title {
  font-size: 24px;
  margin: 0 0 16px 0;
  color: var(--text-main);
  font-weight: 700;
  letter-spacing: -0.5px;
}

.tags-row { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }

.tag {
  background: #f5f5f5;
  color: var(--text-normal);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
}

.tag.highlight { background: #e8f7e6; color: #2b9c2f; }

.price-section { display: flex; justify-content: space-between; align-items: center; }
.price-label { color: var(--text-light); font-size: 12px; }
.price-val { color: #ff4d4f; font-size: 22px; font-weight: 700; }

.content { flex: 1; }

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header.compact { margin-bottom: 12px; }

.section-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-main);
}

.toggle-btn {
  font-size: 13px;
  color: var(--link-color);
  cursor: pointer;
}

.compact-summary {
  margin-bottom: 12px;
  padding: 10px 12px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.compact-summary .tag-row { display: flex; gap: 8px; margin-bottom: 6px; }
.compact-summary .meta-row { color: var(--text-light); font-size: 13px; }

.check-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  margin-bottom: 16px;
  overflow: hidden;
  box-shadow: 0 6px 18px rgba(0,0,0,0.03);
}

.check-card.compact { box-shadow: none; border-color: #f3f3f3; }

.card-head {
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  background: #fafafa;
}

.card-head.active { background: #f3f8ff; }

.head-title { font-weight: 600; color: var(--text-main); }

.head-status { display: flex; align-items: center; gap: 10px; color: var(--text-light); }

.status-text-green { color: #52c41a; font-weight: 600; }
.status-text-red { color: #ff4d4f; font-weight: 600; }
.arrow { transition: transform 0.2s; display: inline-block; }
.arrow.down { transform: rotate(180deg); }

.card-body { padding: 12px 16px 18px; }

.gallery-box { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }
.thumb {
  width: 120px;
  height: 120px;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #f0f0f0;
}
.thumb img { width: 100%; height: 100%; object-fit: cover; }

.group-container { margin-bottom: 12px; }
.group-title { font-weight: 600; margin-bottom: 6px; color: var(--text-normal); }

.items-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 8px 16px; }
.inspection-report.compact .items-grid { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }

.item-row { display: flex; align-items: center; gap: 6px; color: var(--text-normal); font-size: 13px; }
.label { flex: 0 0 auto; }
.dots { flex: 1; border-bottom: 1px dashed #e5e5e5; }
.value { flex: 0 0 auto; min-width: 80px; text-align: right; }
.value.light { color: var(--text-light); }
.value.error { color: #ff4d4f; font-weight: 600; }
.icon-check { margin-left: 4px; color: #67c23a; }

.view-image-btn {
  margin-left: 6px;
  border: 1px solid #f0f0f0;
  padding: 2px 6px;
  border-radius: 6px;
  background: #fff7e6;
  color: #fa8c16;
  cursor: pointer;
}

.footer-note {
  margin-top: 10px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 8px;
  color: var(--text-light);
  font-size: 13px;
}

.note-label { margin-right: 8px; color: var(--text-normal); }

</style>
