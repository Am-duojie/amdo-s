<template>
  <div class="my-products-page">
    
    <div class="products-container">
      <el-card header="我的商品" class="products-card">
        <template #header>
          <div class="card-header">
            <span class="header-title">我的商品</span>
            <el-button type="primary" :icon="Plus" @click="$router.push('/publish')">发布商品</el-button>
          </div>
        </template>
        <el-loading v-loading="loading">
          <el-empty v-if="!loading && products.length === 0" description="还没有发布商品，快去发布第一个吧！">
            <el-button type="primary" @click="$router.push('/publish')">发布商品</el-button>
          </el-empty>
          <div v-else class="products-grid">
            <div
              v-for="product in products"
              :key="product.id"
              class="product-card"
            >
              <div class="product-image" @click="$router.push(`/products/${product.id}`)">
                <img
                  v-if="product.images && product.images.length > 0"
                  :src="getImageUrl(product.images[0].image)"
                  alt="商品"
                />
                <div v-else class="no-image">
                  <el-icon><PictureFilled /></el-icon>
                </div>
                <div class="status-badge">
                  <el-tag :type="getStatusType(product.status)" size="small">
                    {{ getStatusText(product.status) }}
                  </el-tag>
                </div>
              </div>
              <div class="product-info">
                <div class="product-title" @click="$router.push(`/products/${product.id}`)">
                  {{ product.title }}
                </div>
                <div class="product-price">¥{{ product.price }}</div>
                <div class="product-meta">
                  <span class="meta-item">{{ product.view_count }}浏览</span>
                  <span class="meta-item">{{ formatDate(product.created_at) }}</span>
                </div>
                <div class="product-actions">
                  <el-button size="small" @click="$router.push(`/products/${product.id}`)">查看</el-button>
                  <el-button size="small" type="primary" @click="$router.push(`/edit/${product.id}`)">编辑</el-button>
                  <el-button
                    v-if="product.status === 'active'"
                    size="small"
                    type="warning"
                    @click="handleStatusUpdate(product.id, 'removed')"
                  >
                    下架
                  </el-button>
                  <el-button
                    v-if="product.status === 'removed'"
                    size="small"
                    type="success"
                    @click="handleStatusUpdate(product.id, 'active')"
                  >
                    重新上架
                  </el-button>
                  <el-button size="small" type="danger" @click="handleDelete(product.id)">删除</el-button>
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
import { ElMessageBox } from 'element-plus'
import { Plus, PictureFilled } from '@element-plus/icons-vue'
import api from '@/utils/api'
import ErrorHandler from '@/utils/errorHandler'
import { getImageUrl } from '@/utils/image'

const products = ref([])
const loading = ref(false)

onMounted(() => {
  loadProducts()
})

const loadProducts = async () => {
  loading.value = true
  try {
    // 使用后端已有的 my_products 接口
    const res = await api.get('/products/my_products/')
    products.value = res.data
  } catch (error) {
    ErrorHandler.show(error, '加载商品失败')
  } finally {
    loading.value = false
  }
}

const handleStatusUpdate = async (productId, newStatus) => {
  try {
    // 直接对商品做部分更新，修改状态
    await api.patch(`/products/${productId}/`, { status: newStatus })
    ErrorHandler.showSuccess('状态更新成功')
    loadProducts()
  } catch (error) {
    ErrorHandler.show(error, '更新失败')
  }
}

const handleDelete = async (productId) => {
  try {
    await ElMessageBox.confirm('确定要删除此商品吗？删除后无法恢复', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await api.delete(`/products/${productId}/`)
    ErrorHandler.showSuccess('删除成功')
    loadProducts()
  } catch (error) {
    if (error !== 'cancel') {
      ErrorHandler.show(error, '删除失败')
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
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.my-products-page {
  background: #f5f7f9;
  min-height: 100vh;
  padding: 0;
}

.products-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px;
}

.products-card {
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

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.product-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
  transition: all 0.3s;
}

.product-card:hover {
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

.product-card:hover .product-image img {
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

.meta-item {
  flex: 1;
}

.product-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }
}
</style>
