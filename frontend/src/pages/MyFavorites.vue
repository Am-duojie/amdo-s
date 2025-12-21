<template>
  <div class="my-favorites-page">
    
    <div class="container">
      <el-card class="favorites-card">
        <template #header>
          <div class="card-header">
            <span class="header-title">我的收藏</span>
            <span class="count">共 {{ favorites.length }} 件商品</span>
          </div>
        </template>

        <el-loading v-loading="loading">
          <el-empty v-if="!loading && favorites.length === 0" description="还没有收藏任何商品，快去发现好物吧！">
            <el-button type="primary" @click="$router.push('/')">去逛逛</el-button>
          </el-empty>
          <div v-else class="favorites-grid">
            <div
              v-for="favorite in favorites"
              :key="favorite.id"
              class="favorite-card"
            >
              <div class="product-image" @click="$router.push(`/products/${favorite.product.id}`)">
                <img
                  v-if="favorite.product.images && favorite.product.images.length > 0"
                  :src="getImageUrl(favorite.product.images[0].image)"
                  :alt="favorite.product.title"
                />
                <div v-else class="no-image">
                  <el-icon><PictureFilled /></el-icon>
                </div>
                <div class="status-badge">
                  <el-tag :type="getStatusType(favorite.product.status)" size="small">
                    {{ getStatusText(favorite.product.status) }}
                  </el-tag>
                </div>
              </div>
              <div class="product-info">
                <div class="product-title" @click="$router.push(`/products/${favorite.product.id}`)">
                  {{ favorite.product.title }}
                </div>
                <div class="product-price">¥{{ favorite.product.price }}</div>
                <div class="product-meta">
                  <span class="product-location">{{ favorite.product.location }}</span>
                  <span class="favorite-time">收藏于 {{ formatDate(favorite.created_at) }}</span>
                </div>
                <div class="product-actions">
                  <el-button size="small" @click="$router.push(`/products/${favorite.product.id}`)">查看</el-button>
                  <el-button size="small" type="danger" @click="handleRemove(favorite.product.id)">取消收藏</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-loading>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { PictureFilled } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'

const favorites = ref([])
const loading = ref(false)

onMounted(() => {
  loadFavorites()
})

const loadFavorites = async () => {
  loading.value = true
  try {
    const res = await api.get('/favorites/')
    favorites.value = res.data.results || res.data
  } catch (error) {
    ElMessage.error('加载收藏失败')
  } finally {
    loading.value = false
  }
}

const handleRemove = async (productId) => {
  try {
    await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await api.post('/favorites/remove/', { product_id: productId })
    ElMessage.success('已取消收藏')
    loadFavorites()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消收藏失败')
    }
  }
}

const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    active: 'success',
    sold: 'info',
    removed: 'info',
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待审核',
    active: '在售',
    sold: '已售出',
    removed: '已下架',
  }
  return map[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.my-favorites-page {
  background: #f5f7f9;
  min-height: 100vh;
  padding: 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px;
}

.favorites-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.count {
  color: #666;
  font-size: 14px;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.favorite-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
  transition: all 0.3s;
}

.favorite-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.product-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f5f5f5;
  position: relative;
  cursor: pointer;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.favorite-card:hover .product-image img {
  transform: scale(1.05);
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
  font-size: 48px;
}

.status-badge {
  position: absolute;
  top: 8px;
  right: 8px;
}

.product-info {
  padding: 12px;
}

.product-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
  min-height: 40px;
  cursor: pointer;
}

.product-title:hover {
  color: #ff6a00;
}

.product-price {
  font-size: 20px;
  font-weight: bold;
  color: #ff6a00;
  margin-bottom: 8px;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-bottom: 12px;
}

.product-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .favorites-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }
  
  .product-image {
    height: 150px;
  }
}
</style>

















