<template>
  <div class="edit-product-page">
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
    <div class="container">
      <el-card class="edit-card">
        <template #header>
          <div class="card-header">
            <span>{{ isEditing ? '编辑商品' : '发布商品' }}</span>
            <el-button @click="$router.go(-1)">返回</el-button>
          </div>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          label-position="left"
          class="product-form"
        >
          <el-form-item label="商品标题" prop="title">
            <el-input
              v-model="form.title"
              placeholder="请输入商品标题"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="商品分类" prop="category_id">
            <el-select
              v-model="form.category_id"
              placeholder="请选择分类"
              style="width: 100%"
            >
              <el-option
                v-for="category in categories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="商品价格" prop="price">
            <el-input-number
              v-model="form.price"
              :min="0.01"
              :max="999999.99"
              :precision="2"
              :step="0.01"
              style="width: 200px"
            />
            <span class="price-unit">元</span>
          </el-form-item>

          <el-form-item label="原价" prop="original_price">
            <el-input-number
              v-model="form.original_price"
              :min="0"
              :max="999999.99"
              :precision="2"
              :step="0.01"
              placeholder="可选"
              style="width: 200px"
            />
            <span class="price-unit">元</span>
          </el-form-item>

          <el-form-item label="成色" prop="condition">
            <el-select v-model="form.condition" style="width: 100%">
              <el-option label="全新" value="new" />
              <el-option label="几乎全新" value="like_new" />
              <el-option label="良好" value="good" />
              <el-option label="一般" value="fair" />
              <el-option label="较差" value="poor" />
            </el-select>
          </el-form-item>

          <el-form-item label="商品描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="6"
              placeholder="请详细描述商品的状况、购买时间、使用情况等"
              maxlength="2000"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="交易地点" prop="location">
            <el-input
              v-model="form.location"
              placeholder="请输入交易地点，如：XX大学、XX地铁站等"
            />
          </el-form-item>

          <el-form-item label="联系电话">
            <el-input
              v-model="form.contact_phone"
              placeholder="可选，方便买家联系"
            />
          </el-form-item>

          <el-form-item label="微信">
            <el-input
              v-model="form.contact_wechat"
              placeholder="可选，方便买家联系"
            />
          </el-form-item>

          <el-form-item label="商品图片">
            <div class="image-upload">
              <el-upload
                ref="uploadRef"
                action=""
                :auto-upload="false"
                :on-change="handleImageChange"
                :on-remove="handleImageRemove"
                :limit="9"
                :file-list="imageFiles"
                list-type="picture-card"
                accept="image/*"
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">
                最多上传9张图片，支持jpg、png格式，每张不超过5MB
              </div>
            </div>
          </el-form-item>

          <el-form-item>
            <div class="form-actions">
              <el-button size="large" @click="$router.go(-1)">取消</el-button>
              <el-button
                type="primary"
                size="large"
                :loading="submitting"
                @click="handleSubmit"
              >
                {{ isEditing ? '保存修改' : '发布商品' }}
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()

const formRef = ref()
const uploadRef = ref()
const submitting = ref(false)
const categories = ref([])
const imageFiles = ref([])

const productId = computed(() => route.params.id)
const isEditing = computed(() => !!productId.value)

const form = ref({
  title: '',
  category_id: null,
  price: 0,
  original_price: null,
  condition: 'good',
  description: '',
  location: '',
  contact_phone: '',
  contact_wechat: '',
})

const rules = {
  title: [
    { required: true, message: '请输入商品标题', trigger: 'blur' },
    { min: 5, max: 200, message: '标题长度在 5 到 200 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择商品分类', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入商品价格', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '价格必须大于0', trigger: 'blur' }
  ],
  condition: [
    { required: true, message: '请选择商品成色', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入商品描述', trigger: 'blur' },
    { min: 10, max: 2000, message: '描述长度在 10 到 2000 个字符', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入交易地点', trigger: 'blur' }
  ]
}

onMounted(() => {
  loadCategories()
  if (isEditing.value) {
    loadProduct()
  }
})

const loadCategories = async () => {
  try {
    const res = await api.get('/categories/')
    const data = res.data?.results || res.data || []
    // 过滤掉可能的null值和"数码产品"分类
    categories.value = Array.isArray(data) ? data.filter(c => c && c.id && c.name !== '数码产品') : []
  } catch (error) {
    ElMessage.error('加载分类失败')
  }
}

const loadProduct = async () => {
  try {
    const res = await api.get(`/products/${productId.value}/`)
    const product = res.data
    
    form.value = {
      title: product.title,
      category_id: product.category?.id,
      price: product.price,
      original_price: product.original_price,
      condition: product.condition,
      description: product.description,
      location: product.location,
      contact_phone: product.contact_phone,
      contact_wechat: product.contact_wechat,
    }

    // 加载现有图片
    if (product.images && product.images.length > 0) {
      imageFiles.value = product.images.map(img => ({
        uid: img.id,
        name: img.image.split('/').pop(),
        url: img.image,
        status: 'success'
      }))
    }
  } catch (error) {
    ElMessage.error('加载商品信息失败')
    router.go(-1)
  }
}

const handleImageChange = (file, fileList) => {
  // 检查文件大小
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过5MB')
    return false
  }
  imageFiles.value = fileList
}

const handleImageRemove = (file, fileList) => {
  imageFiles.value = fileList
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    let productData = { ...form.value }
    
    if (isEditing.value) {
      // 更新商品
      await api.patch(`/products/${productId.value}/`, productData)
      
      // 上传新图片
      const newImages = imageFiles.value.filter(file => !file.url)
      if (newImages.length > 0) {
        const formData = new FormData()
        newImages.forEach(file => {
          formData.append('images', file.raw)
        })
        
        await api.post(`/products/${productId.value}/upload_images/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
      }
      
      ElMessage.success('商品修改成功')
    } else {
      // 创建商品
      const res = await api.post('/products/', productData)
      const newProductId = res.data.id
      
      // 上传图片
      if (imageFiles.value.length > 0) {
        const formData = new FormData()
        imageFiles.value.forEach(file => {
          if (file.raw) {
            formData.append('images', file.raw)
          }
        })
        
        await api.post(`/products/${newProductId}/upload_images/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
      }
      
      ElMessage.success('商品发布成功')
    }
    
    router.push('/my-products')
  } catch (error) {
    if (error.response?.data) {
      const errors = Object.values(error.response.data).flat()
      ElMessage.error(errors.join(', '))
    } else {
      ElMessage.error(isEditing.value ? '修改失败' : '发布失败')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.recycle-entry-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 16px auto 0;
  padding: 12px 16px;
  max-width: 800px;
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
.edit-product-page {
  background: #f5f7f9;
  min-height: 100vh;
  padding: 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 20px;
}

.edit-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.product-form {
  padding: 20px 0;
}

.price-unit {
  margin-left: 10px;
  color: #999;
}

.image-upload {
  width: 100%;
}

.upload-tip {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.form-actions .el-button {
  width: 150px;
}

:deep(.el-upload--picture-card) {
  width: 120px;
  height: 120px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 120px;
  height: 120px;
}

@media (max-width: 768px) {
  .container {
    padding: 20px 10px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .form-actions .el-button {
    width: 100%;
  }
}
</style>
