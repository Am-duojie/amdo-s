<template>
  <div class="verified-product-detail" v-loading="loading">
    <el-descriptions :column="2" border>
      <el-descriptions-item label="品牌">{{ detail.brand }}</el-descriptions-item>
      <el-descriptions-item label="型号">{{ detail.model }}</el-descriptions-item>
      <el-descriptions-item label="存储容量">{{ detail.storage }}</el-descriptions-item>
      <el-descriptions-item label="运行内存">{{ detail.ram || '-' }}</el-descriptions-item>
      <el-descriptions-item label="版本">{{ detail.version || '-' }}</el-descriptions-item>
      <el-descriptions-item label="成色">{{ getConditionText(detail.condition) }}</el-descriptions-item>
      <el-descriptions-item label="拆修和功能">{{ detail.repair_status || '-' }}</el-descriptions-item>
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

const loading = ref(false)
const detail = ref({})

const conditionMap = {
  new: '全新',
  like_new: '99成新',
  good: '95成新'
}

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

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.verified-product-detail {
  padding: 0;
}
</style>
