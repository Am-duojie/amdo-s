<template>
  <div class="verified-product-form">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" class="form-grid">
      <!-- 基础信息 -->
      <el-card shadow="never" class="card-block">
        <template #header>基础信息</template>
      <el-form-item label="商品标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入商品标题" />
      </el-form-item>
      <el-form-item label="品牌" prop="brand">
        <el-input v-model="form.brand" placeholder="如：苹果、华为" />
      </el-form-item>
      <el-form-item label="型号" prop="model">
        <el-input v-model="form.model" placeholder="如：iPhone 13" />
      </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类">
            <el-option label="手机数码" value="phone" />
            <el-option label="平板/笔记本" value="tablet" />
            <el-option label="电脑办公" value="computer" />
            <el-option label="智能穿戴" value="watch" />
            <el-option label="耳机音响" value="audio" />
          </el-select>
        </el-form-item>
      <el-form-item label="存储容量">
        <el-input v-model="form.storage" placeholder="如：128GB" />
      </el-form-item>
      <el-form-item label="成色" prop="condition">
        <el-select v-model="form.condition" style="width: 100%">
          <el-option label="全新" value="new" />
          <el-option label="99成新" value="like_new" />
          <el-option label="95成新" value="good" />
            <el-option label="9成新" value="fair" />
            <el-option label="8成新" value="poor" />
        </el-select>
      </el-form-item>
      <el-form-item label="价格" prop="price">
          <el-input-number v-model="form.price" :precision="2" :min="0.01" style="width: 100%" />
      </el-form-item>
      <el-form-item label="原价">
        <el-input-number v-model="form.original_price" :precision="2" :min="0" style="width: 100%" />
      </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="form.stock" :min="1" :max="9999" />
        </el-form-item>
        <el-form-item label="所在地" prop="location">
          <el-input v-model="form.location" placeholder="如：广东 深圳" />
        </el-form-item>
      <el-form-item label="商品描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入商品描述" />
      </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="form.tags" multiple filterable allow-create default-first-option placeholder="选择或输入标签">
            <el-option label="官方质检" value="官方质检" />
            <el-option label="正品保障" value="正品保障" />
            <el-option label="7天无理由" value="7天无理由" />
          </el-select>
        </el-form-item>
      </el-card>

      <!-- 媒体上传 -->
      <el-card shadow="never" class="card-block">
        <template #header>媒体上传</template>
        <el-form-item label="封面图" prop="cover_image">
          <el-upload
            class="upload-cover"
            :limit="1"
            accept="image/*"
            list-type="picture-card"
            :http-request="(options) => handleUpload(options, 'cover')"
            :file-list="coverFileList"
            :on-remove="() => (form.cover_image = '', coverFileList.splice(0))"
            :on-preview="handlePreview"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <el-form-item label="详情图(3~9)" prop="detail_images">
          <el-upload
            class="upload-detail"
            multiple
            list-type="picture-card"
            :limit="9"
            accept="image/*"
            :http-request="(options) => handleUpload(options, 'detail')"
            :file-list="detailFileList"
            :on-remove="handleDetailRemove"
            :on-preview="handlePreview"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <el-form-item label="质检报告(图片/PDF)" prop="inspection_reports">
          <el-upload
            class="upload-report"
            :limit="3"
            :http-request="(options) => handleUpload(options, 'report')"
            :file-list="reportFileList"
            :on-remove="handleReportRemove"
            accept="image/*,.pdf"
          >
            <el-button type="primary" text>上传质检报告</el-button>
            <template #tip>
              <div class="el-upload__tip">支持图片或PDF，最多3份</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-card>

      <!-- 质检信息 -->
      <el-card shadow="never" class="card-block">
        <template #header>质检信息</template>
        <el-form-item label="质检结果" prop="inspection_result">
          <el-select v-model="form.inspection_result" style="width: 100%">
            <el-option label="合格" value="pass" />
            <el-option label="警告" value="warn" />
            <el-option label="不合格" value="fail" />
          </el-select>
        </el-form-item>
        <el-form-item label="质检日期" prop="inspection_date">
          <el-date-picker v-model="form.inspection_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="质检员" prop="inspection_staff">
          <el-input v-model="form.inspection_staff" placeholder="质检员姓名/编号" />
        </el-form-item>
        <el-form-item label="质检说明">
          <el-input v-model="form.inspection_note" type="textarea" :rows="3" placeholder="可填写质检要点" />
        </el-form-item>
      </el-card>
    </el-form>

    <div class="actions">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button :loading="saving" @click="submit(false)">{{ isEdit ? '保存' : '创建' }}</el-button>
      <el-button type="primary" :loading="saving" @click="submit(true)">保存并上架</el-button>
      <el-button v-if="isEdit && form.status === 'active'" type="warning" plain :loading="saving" @click="unpublish">
        下架
      </el-button>
    </div>

    <el-image-viewer
      v-if="previewVisible"
      :url-list="previewImages"
      :initial-index="previewIndex"
      @close="previewVisible = false"
    />
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getImageUrl } from '@/utils/image'

const props = defineProps({
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['created', 'cancel', 'updated'])

const formRef = ref()
const saving = ref(false)
const coverFileList = ref([])
const detailFileList = ref([])
const reportFileList = ref([])
const previewVisible = ref(false)
const previewImages = ref([])
const previewIndex = ref(0)

const isEdit = computed(() => !!props.product?.id)

const form = reactive({
  title: '',
  brand: '',
  model: '',
  storage: '',
  condition: 'good',
  price: 0,
  original_price: 0,
  stock: 1,
  location: '',
  description: '',
  tags: [],
  cover_image: '',
  detail_images: [],
  inspection_reports: [],
  inspection_result: 'pass',
  inspection_date: '',
  inspection_staff: '',
  inspection_note: '',
  category: '',
  category_id: null,
  status: 'draft'
})

const rules = {
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  brand: [{ required: true, message: '请输入品牌', trigger: 'blur' }],
  model: [{ required: true, message: '请输入型号', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }],
  cover_image: [{ required: true, message: '请上传封面图', trigger: 'change' }],
  detail_images: [{ type: 'array', required: true, min: 1, message: '请至少上传1张详情图', trigger: 'change' }],
  inspection_result: [{ required: true, message: '请选择质检结果', trigger: 'change' }],
  inspection_date: [{ required: true, message: '请选择质检日期', trigger: 'change' }],
  inspection_staff: [{ required: true, message: '请输入质检员', trigger: 'blur' }],
  stock: [{ required: true, type: 'number', min: 1, message: '库存至少1', trigger: 'change' }],
  location: [{ required: true, message: '请输入所在地', trigger: 'blur' }],
}

// 上传接口：请根据后端实际路径修改。优先取环境变量 VITE_ADMIN_UPLOAD_URL
// 注意 adminApi 已带 baseURL=/admin-api，故这里默认用 /uploads/...，拼起来就是 /admin-api/uploads/...
const uploadEndpoint = import.meta.env.VITE_ADMIN_UPLOAD_URL || '/uploads/images/'
const reportEndpoint = import.meta.env.VITE_ADMIN_REPORT_UPLOAD_URL || '/uploads/reports/'

const handleUpload = async (options, type) => {
  const { file, onError, onSuccess } = options
  const formData = new FormData()
  formData.append('file', file)
  try {
    const endpoint = type === 'report' ? reportEndpoint : uploadEndpoint
    const res = await adminApi.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const url = res.data?.url || res.data?.image || res.data?.path
    if (!url) throw new Error('上传返回空URL')
    if (type === 'cover') {
      form.cover_image = url
      coverFileList.value = [{ name: file.name, url }]
    } else if (type === 'detail') {
      form.detail_images.push(url)
      detailFileList.value.push({ name: file.name, url })
    } else if (type === 'report') {
      form.inspection_reports.push(url)
      reportFileList.value.push({ name: file.name, url })
    }
    onSuccess(res.data)
  } catch (err) {
    ElMessage.error('上传失败')
    onError(err)
  }
}

const handleDetailRemove = (file) => {
  form.detail_images = form.detail_images.filter((u) => u !== file.url)
  detailFileList.value = detailFileList.value.filter((f) => f.url !== file.url)
}

const handlePreview = (file) => {
  const allImages = [
    ...coverFileList.value.map((f) => f.url),
    ...detailFileList.value.map((f) => f.url),
  ].filter(Boolean)
  const idx = allImages.findIndex((u) => u === file.url)
  if (allImages.length === 0) return
  previewImages.value = allImages
  previewIndex.value = idx >= 0 ? idx : 0
  previewVisible.value = true
}

const handleReportRemove = (file) => {
  form.inspection_reports = form.inspection_reports.filter((u) => u !== file.url)
  reportFileList.value = reportFileList.value.filter((f) => f.url !== file.url)
}

const normalizeToUrl = (url) => (url ? getImageUrl(url) || url : '')

const fillForm = (data = {}) => {
  form.title = data.title || ''
  form.brand = data.brand || ''
  form.model = data.model || ''
  form.storage = data.storage || ''
  form.condition = data.condition || 'good'
  form.price = Number(data.price || 0)
  form.original_price = Number(data.original_price || 0)
  form.stock = Number(data.stock || 1)
  form.location = data.location || ''
  form.description = data.description || ''
  form.tags = data.tags || []
  form.cover_image = data.cover_image || ''
  form.detail_images = data.detail_images || []
  form.inspection_reports = data.inspection_reports || []
  form.inspection_result = data.inspection_result || 'pass'
  form.inspection_date = data.inspection_date || ''
  form.inspection_staff = data.inspection_staff || ''
  form.inspection_note = data.inspection_note || ''
  form.category = data.category || ''
  form.category_id = (data.category && data.category.id) || data.category_id || null
  form.status = data.status || 'draft'

  coverFileList.value = form.cover_image
    ? [{ name: 'cover', url: normalizeToUrl(form.cover_image) }]
    : []
  detailFileList.value = (form.detail_images || []).map((u, idx) => ({
    name: `detail-${idx + 1}`,
    url: normalizeToUrl(u)
  }))
  reportFileList.value = (form.inspection_reports || []).map((u, idx) => ({
    name: `report-${idx + 1}`,
    url: normalizeToUrl(u)
  }))
}

watch(
  () => props.product,
  (val) => {
    if (val) fillForm(val)
  },
  { immediate: true, deep: true }
)

const submit = async (publishNow = false) => {
  try {
    await formRef.value.validate()
    saving.value = true
    // 组装 payload，去掉只读/无用字段
    const {
      category,
      tags,
      detail_images,
      inspection_reports,
      ...rest
    } = form
    const payload = {
      ...rest,
      price: Number(rest.price || 0),
      original_price: Number(rest.original_price || 0),
      stock: Number(rest.stock || 1),
      detail_images: Array.isArray(detail_images) ? [...detail_images] : [],
      inspection_reports: Array.isArray(inspection_reports) ? [...inspection_reports] : [],
    }
    // 日期格式化
    if (rest.inspection_date) {
      const d = rest.inspection_date
      const dateStr = d instanceof Date
        ? `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
        : rest.inspection_date
      payload.inspection_date = dateStr
    }
    if (Array.isArray(tags)) {
      payload.tags = [...tags]
    }
    // 处理分类：优先 category_id，没有则尝试 category（若是数字字符串）
    if (form.category_id) {
      payload.category_id = form.category_id
    } else if (form.category && !isNaN(Number(form.category))) {
      payload.category_id = Number(form.category)
    }
    let id = props.product?.id
    if (isEdit.value) {
      await adminApi.put(`/verified-listings/${id}/`, payload)
    } else {
      const res = await adminApi.post('/verified-listings/', payload)
      id = res.data?.id
    }
    if (publishNow && id) {
      await adminApi.post(`/verified-listings/${id}/publish/`)
      ElMessage.success('已发布')
    } else {
      ElMessage.success(isEdit.value ? '保存成功' : '创建成功')
    }
    emit(isEdit.value ? 'updated' : 'created')
  } catch (error) {
    if (error !== false) {
      ElMessage.error('提交失败')
    }
  } finally {
    saving.value = false
  }
}

const unpublish = async () => {
  if (!props.product?.id) return
  try {
    saving.value = true
    await adminApi.post(`/verified-listings/${props.product.id}/unpublish`)
    ElMessage.success('已下架')
    emit('updated')
  } catch (error) {
    ElMessage.error('下架失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.verified-product-form {
  padding: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 16px;
}

.card-block {
  width: 100%;
}

.actions {
  text-align: right;
  margin-top: 20px;
}

.upload-cover :deep(.el-upload) {
  width: 120px;
  height: 120px;
}

.upload-detail :deep(.el-upload) {
  width: 120px;
  height: 120px;
}

.upload-report :deep(.el-upload-list__item) {
  width: 240px;
}
</style>













