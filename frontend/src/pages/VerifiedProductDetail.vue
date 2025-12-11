<template>
  <div class="verified-detail-page">
    <div v-if="loading" class="loading">
      <el-skeleton :rows="8" animated />
    </div>

    <div v-else-if="error" class="error">
      <el-empty description="加载失败">
        <el-button type="primary" @click="loadProduct">重试</el-button>
      </el-empty>
    </div>

    <div v-else-if="product" class="detail-card">
      <div class="top">
        <div class="gallery">
          <el-image
            v-if="images.length"
            :src="images[currentImage]"
            :preview-src-list="images"
            :initial-index="currentImage"
            fit="contain"
            class="main-img"
          />
          <div v-else class="no-img">
            <el-icon><PictureFilled /></el-icon>
            <span>暂无图片</span>
          </div>
          <div v-if="images.length > 1" class="thumbs">
            <div
              v-for="(src, idx) in images"
              :key="idx"
              :class="['thumb', { active: currentImage === idx }]"
              @click="currentImage = idx"
            >
              <img :src="src" :alt="product.title" />
            </div>
          </div>
        </div>

        <div class="info">
          <div class="badges">
            <el-tag type="success" effect="plain">官方验</el-tag>
            <el-tag type="info" effect="plain">正品保障</el-tag>
            <el-tag type="warning" effect="plain">质检报告</el-tag>
          </div>
          <h1 class="title">{{ product.title }}</h1>
          <p class="sub">{{ product.brand }} {{ product.model }} {{ product.storage || '' }}</p>
          <div class="price-row">
            <span class="price">¥{{ product.price }}</span>
            <span v-if="product.original_price" class="orig">¥{{ product.original_price }}</span>
          </div>
          <div class="meta">库存：{{ product.stock ?? '—' }} · 所在地：{{ product.location || '官方仓' }}</div>
          <div class="attrs">
            <div>成色：{{ conditionText }}</div>
            <div v-if="product.category?.name">分类：{{ product.category.name }}</div>
            <div>保障：官方质检 · 7天无理由</div>
          </div>
          <div class="inspection" v-if="inspectionAvailable">
            <div class="ins-title">质检信息</div>
            <div class="ins-meta">
              <span>结果：{{ inspectionText }}</span>
              <span v-if="product.inspection_date"> · 日期：{{ product.inspection_date }}</span>
              <span v-if="product.inspection_staff"> · 质检员：{{ product.inspection_staff }}</span>
            </div>
            <div v-if="product.inspection_note" class="ins-note">说明：{{ product.inspection_note }}</div>
            <div v-if="reports.length" class="reports">
              <div
                v-for="(r, idx) in reports"
                :key="idx"
                class="report"
                @click="previewReport(r)"
              >
                <el-icon><Document /></el-icon>
                <span>{{ getReportName(r) }}</span>
              </div>
            </div>
            <div v-else class="empty">暂无质检报告</div>
          </div>
        </div>
      </div>

      <div class="detail-block" v-if="detailImages.length">
        <div class="block-title">商品详情图</div>
        <div class="detail-list">
          <el-image
            v-for="(src, idx) in detailImages"
            :key="idx"
            :src="src"
            :preview-src-list="detailImages"
            :initial-index="idx"
            fit="contain"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { PictureFilled, Document } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'

const route = useRoute()
const router = useRouter()

const product = ref(null)
const loading = ref(false)
const error = ref(null)
const currentImage = ref(0)

const conditionMap = {
  excellent: '九九新',
  good: '九成新',
  fair: '八五新',
  poor: '八成新',
  verified: '官方验'
}

const images = computed(() => {
  if (!product.value) return []
  const arr = product.value.images || []
  return arr.map(img => resolveImageField(img)).filter(Boolean)
})

const detailImages = computed(() => {
  if (!product.value) return []
  const arr = product.value.detail_images || product.value.images || []
  return arr.map(img => resolveImageField(img)).filter(Boolean)
})

const reports = computed(() => {
  if (!product.value) return []
  return (product.value.inspection_reports || []).map(normalizeFile).filter(Boolean)
})

const conditionText = computed(() => conditionMap[product.value?.condition] || '官方验')
const inspectionAvailable = computed(() => product.value && (product.value.inspection_result || reports.value.length))
const inspectionText = computed(() => product.value?.inspection_result || '已完成质检')

function resolveImageField(img) {
  if (!img) return null
  if (typeof img === 'string') return getImageUrl(img)
  if (img.url) return getImageUrl(img.url)
  if (img.image) return getImageUrl(img.image)
  if (img.image_url) return getImageUrl(img.image_url)
  if (img.imageUrl) return getImageUrl(img.imageUrl)
  return null
}

function normalizeFile(f) {
  if (!f) return null
  if (typeof f === 'string') return { url: getImageUrl(f) }
  if (f.url) return { ...f, url: getImageUrl(f.url) }
  if (f.image) return { ...f, url: getImageUrl(f.image) }
  return null
}

function getReportName(r) {
  if (!r?.url) return '查看报告'
  try {
    const u = new URL(r.url, window.location.origin)
    return decodeURIComponent(u.pathname.split('/').pop() || '报告')
  } catch {
    return '报告'
  }
}

function previewReport(r) {
  if (!r?.url) return
  window.open(r.url, '_blank')
}

function normalizeProduct(data) {
  const imgs = []
  if (Array.isArray(data.detail_images)) {
    data.detail_images.forEach(img => {
      const val = img?.image || img?.url || img
      if (val) imgs.push({ image: val })
    })
  }
  if (!imgs.length && data.cover_image) imgs.push({ image: data.cover_image })
  if (!imgs.length && Array.isArray(data.images)) {
    data.images.forEach(img => {
      const val = img?.image || img?.url || img
      if (val) imgs.push({ image: val })
    })
  }
  data.images = imgs
  if (!data.seller) data.seller = { username: '官方验' }
  return data
}

async function loadProduct() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(`/verified-products/${route.params.id}/`)
    product.value = normalizeProduct(res.data)
  } catch (err) {
    error.value = err
    ElMessage.error('商品加载失败')
    router.push('/verified-products')
  } finally {
    loading.value = false
  }
}

onMounted(loadProduct)
</script>

<style scoped>
.verified-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px 48px;
}
.detail-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  padding: 20px;
}
.top {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}
.gallery {
  width: 45%;
}
.main-img {
  width: 100%;
  height: 360px;
  border-radius: 10px;
  background: #fafafa;
}
.no-img {
  width: 100%;
  height: 360px;
  border-radius: 10px;
  background: #fafafa;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  gap: 6px;
}
.thumbs {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  overflow-x: auto;
}
.thumb {
  width: 70px;
  height: 70px;
  border: 1px solid #eee;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
}
.thumb.active {
  border-color: #409eff;
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.info {
  flex: 1;
}
.badges {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}
.title {
  font-size: 22px;
  font-weight: 700;
  margin: 4px 0;
}
.sub {
  color: #666;
  margin-bottom: 8px;
}
.price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin: 10px 0;
}
.price {
  color: #ff6a00;
  font-size: 26px;
  font-weight: 700;
}
.orig {
  text-decoration: line-through;
  color: #999;
}
.meta {
  color: #666;
  margin-bottom: 10px;
}
.attrs {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #444;
  margin-bottom: 12px;
}
.inspection {
  padding: 12px;
  background: #f9fbff;
  border: 1px solid #e6f2ff;
  border-radius: 8px;
}
.ins-title {
  font-weight: 600;
  margin-bottom: 6px;
}
.ins-meta {
  color: #555;
  margin-bottom: 6px;
}
.ins-note {
  color: #333;
  margin-bottom: 8px;
}
.reports {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.report {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #333;
}
.report:hover {
  color: #409eff;
}
.empty {
  color: #888;
}
.detail-block {
  margin-top: 24px;
}
.block-title {
  font-weight: 600;
  margin-bottom: 12px;
}
.detail-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}
.loading,
.error {
  padding: 40px 0;
}
@media (max-width: 960px) {
  .top {
    flex-direction: column;
  }
  .gallery {
    width: 100%;
  }
  .main-img,
  .no-img {
    height: 300px;
  }
}
</style>



