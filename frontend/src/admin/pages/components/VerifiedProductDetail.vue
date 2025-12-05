<template>
  <div class="verified-product-detail" v-loading="loading">
    <el-descriptions :column="2" border>
      <el-descriptions-item label="商品ID">{{ detail.id }}</el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="getStatusType(detail.status)">{{ getStatusText(detail.status) }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="标题" :span="2">{{ detail.title }}</el-descriptions-item>
      <el-descriptions-item label="品牌">{{ detail.brand }}</el-descriptions-item>
      <el-descriptions-item label="型号">{{ detail.model }}</el-descriptions-item>
      <el-descriptions-item label="存储">{{ detail.storage }}</el-descriptions-item>
      <el-descriptions-item label="成色">{{ getConditionText(detail.condition) }}</el-descriptions-item>
      <el-descriptions-item label="价格">¥{{ detail.price }}</el-descriptions-item>
      <el-descriptions-item label="原价">¥{{ detail.original_price || '-' }}</el-descriptions-item>
      <el-descriptions-item label="销量">{{ detail.sales_count || 0 }}</el-descriptions-item>
      <el-descriptions-item label="浏览量">{{ detail.view_count || 0 }}</el-descriptions-item>
      <el-descriptions-item label="描述" :span="2">{{ detail.description }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
      <el-descriptions-item label="更新时间">{{ formatTime(detail.updated_at) }}</el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'

const props = defineProps({
  productId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['updated'])

const loading = ref(false)
const detail = ref({})

const statusMap = {
  pending: { text: '待审核', type: 'warning' },
  active: { text: '在售', type: 'success' },
  sold: { text: '已售出', type: 'info' },
  removed: { text: '已下架', type: 'info' }
}

const conditionMap = {
  new: '全新',
  like_new: '99成新',
  good: '95成新'
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'
const getConditionText = (condition) => conditionMap[condition] || condition

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await adminApi.get(`/verified-listings/${props.productId}`)
    detail.value = res.data || {}
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.verified-product-detail {
  padding: 0;
}
</style>

