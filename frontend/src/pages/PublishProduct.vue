<template>
  <div class="publish-page xy-theme">
    <div class="recycle-entry-banner" @click="$router.push('/recycle')">
      <div class="banner-left">
        <span class="recycle-icon">♻️</span>
        <span class="recycle-title">官方质检回收</span>
      </div>
      <div class="banner-right">
        <span class="banner-desc">专业质检 · 极速打款 · 安心回收</span>
        <el-button type="primary" size="small">去回收</el-button>
      </div>
    </div>
    <div class="publish-container">
      <el-card class="publish-card">
        <template #header>
          <div class="card-header">
            <h2>发布商品</h2>
            <p>建议包含品牌、型号、容量/配置等关键信息，清晰图片更容易卖出</p>
          </div>
        </template>
        
        <el-form :model="form" label-width="120px" class="publish-form">
          <el-divider content-position="left">基本信息</el-divider>
          <el-form-item label="商品标题" required>
            <el-input 
              v-model="form.title" 
              placeholder="如：iPhone 15 128G 蓝色 国行 一口价"
              maxlength="50" show-word-limit/>
          </el-form-item>

          <el-form-item label="商品描述" required>
            <el-input v-model="form.description" type="textarea" :rows="8" placeholder="如：购买时间/使用时长/电池健康/是否维修/配件清单/交易方式等" maxlength="800" show-word-limit/>
          </el-form-item>

          <el-divider content-position="left">分类与成色</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="分类">
                <el-select v-model="form.category_id" placeholder="选择分类" clearable style="width: 100%">
                  <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id"/>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="成色" required>
                <el-select v-model="form.condition" style="width: 100%">
                  <el-option label="全新" value="new"/>
                  <el-option label="几乎全新" value="like_new"/>
                  <el-option label="良好" value="good"/>
                  <el-option label="一般" value="fair"/>
                  <el-option label="较差" value="poor"/>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">价格与地点</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="价格" required>
                <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" prefix="¥" placeholder="请输入价格"/>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="原价（可选）">
                <el-input-number v-model="form.original_price" :min="0" :precision="2" style="width: 100%" prefix="¥" placeholder="原价"/>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="所在地" required>
            <el-input v-model="form.location" placeholder="如：北京市朝阳区"/>
          </el-form-item>

          <el-divider content-position="left">联系方式</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="联系电话">
                <el-input v-model="form.contact_phone" placeholder="选填，方便买家联系"/>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="微信">
                <el-input v-model="form.contact_wechat" placeholder="选填"/>
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">商品图片</el-divider>
          <el-form-item label="图片上传" required>
            <div class="upload-tips">
              <el-icon><InfoFilled/></el-icon>
              <span>最多 5 张，第一张为主图；建议 1:1 或 4:3，确保清晰、正面、配件合照</span>
            </div>
            <el-upload v-model:file-list="fileList" action="#" list-type="picture-card" :auto-upload="false" :limit="5" accept="image/*" :on-preview="handlePreview" :on-remove="handleRemove">
              <el-icon><Plus/></el-icon>
            </el-upload>
          </el-form-item>

          <div class="form-actions">
            <el-button type="primary" @click="handleSubmit" :loading="loading" size="large" class="submit-btn">发布商品</el-button>
            <el-button @click="$router.back()" size="large">取消</el-button>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()

const categories = ref([])
const fileList = ref([])
const loading = ref(false)
const form = ref({
  title: '',
  description: '',
  category_id: null,
  price: null,
  original_price: null,
  condition: 'good',
  location: '',
  contact_phone: '',
  contact_wechat: '',
})

onMounted(() => {
  console.log('PublishProduct页面加载')
  
  // 检查登录状态
  const token = localStorage.getItem('token')
  console.log('Token:', token ? '存在' : '不存在')
  
  if (!token) {
    ElMessage.warning('请先登录后发布商品')
    router.push('/login')
    return
  }
  
  // 加载分类
  loadCategories()
})

const loadCategories = async () => {
  try {
    console.log('开始加载分类...')
    const res = await api.get('/categories/')
    console.log('分类API响应:', res.data)
    // 处理可能的分页格式，并过滤掉"数码产品"分类
    const allCategories = res.data?.results || res.data || []
    categories.value = allCategories.filter(cat => cat.name !== '数码产品')
    console.log('分类数据:', categories.value)
    
    if (categories.value.length === 0) {
      console.warn('没有分类数据，可能需要在后台添加分类')
    }
  } catch (error) {
    console.error('加载分类失败:', error)
    ElMessage.error('加载分类失败')
  }
}

const handlePreview = (file) => {
  // 预览图片
}

const handleRemove = (file) => {
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

const handleSubmit = async () => {
  if (!form.value.title || !form.value.description || !form.value.price) {
    ElMessage.warning('请填写必填信息')
    return
  }

  if (fileList.value.length === 0) {
    ElMessage.warning('请至少上传一张商品图片')
    return
  }

  loading.value = true
  try {
    const productData = { ...form.value }
    const productRes = await api.post('/products/', productData)
    const productId = productRes.data.id

    const formData = new FormData()
    fileList.value.forEach((file, index) => {
      formData.append('images', file.raw)
      if (index === 0) {
        formData.append('is_primary', 'true')
      }
    })

    await api.post(`/products/${productId}/upload_images/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    ElMessage.success('商品发布成功')
    router.push(`/products/${productId}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '发布失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.recycle-entry-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 16px auto 8px;
  padding: 12px 16px;
  max-width: 1200px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ff6600, #ff8833);
  color: #fff;
  box-shadow: 0 4px 16px rgba(255, 102, 0, 0.25);
}
.recycle-entry-banner .banner-left { display: flex; align-items: center; gap: 8px; }
.recycle-entry-banner .recycle-icon { font-size: 20px; }
.recycle-entry-banner .recycle-title { font-weight: 700; font-size: 15px; }
.recycle-entry-banner .banner-right { display: flex; align-items: center; gap: 10px; }
.recycle-entry-banner .banner-desc { opacity: 0.9; font-size: 13px; }
.recycle-entry-banner:hover { filter: brightness(1.02); }
.publish-page {
  background: #f5f7f9;
  min-height: 100vh;
  padding: 0;
}

.publish-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px 20px;
}

.publish-card {
  border-radius: 8px;
}

.publish-form {
  padding: 20px 0;
}

.upload-tips {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #999;
  font-size: 12px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.submit-btn {
  background: #ff6a00;
  border-color: #ff6a00;
  padding: 0 40px;
}

.submit-btn:hover {
  background: #ff8533;
  border-color: #ff8533;
}
</style>
