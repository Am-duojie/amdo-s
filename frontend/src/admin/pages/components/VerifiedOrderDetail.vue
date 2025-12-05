<template>
  <div class="verified-order-detail" v-loading="loading">
    <el-descriptions :column="2" border>
      <el-descriptions-item label="订单号">{{ detail.id }}</el-descriptions-item>
      <el-descriptions-item label="订单状态">
        <el-tag :type="getStatusType(detail.status)">{{ getStatusText(detail.status) }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="商品">{{ detail.product?.title || '-' }}</el-descriptions-item>
      <el-descriptions-item label="价格">¥{{ detail.total_price }}</el-descriptions-item>
      <el-descriptions-item label="买家">{{ detail.buyer?.username || '-' }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
      <el-descriptions-item label="收货人">{{ detail.shipping_name }}</el-descriptions-item>
      <el-descriptions-item label="收货电话">{{ detail.shipping_phone }}</el-descriptions-item>
      <el-descriptions-item label="收货地址" :span="2">{{ detail.shipping_address }}</el-descriptions-item>
      <el-descriptions-item v-if="detail.carrier" label="物流公司">{{ detail.carrier }}</el-descriptions-item>
      <el-descriptions-item v-if="detail.tracking_number" label="运单号">{{ detail.tracking_number }}</el-descriptions-item>
      <el-descriptions-item v-if="detail.shipped_at" label="发货时间">{{ formatTime(detail.shipped_at) }}</el-descriptions-item>
      <el-descriptions-item v-if="detail.delivered_at" label="签收时间">{{ formatTime(detail.delivered_at) }}</el-descriptions-item>
      <el-descriptions-item label="备注" :span="2">{{ detail.note || '-' }}</el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'

const props = defineProps({
  orderId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['updated'])

const loading = ref(false)
const detail = ref({})

const statusMap = {
  pending: { text: '待付款', type: 'warning' },
  paid: { text: '已付款', type: 'success' },
  shipped: { text: '已发货', type: 'primary' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'info' }
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await adminApi.get(`/verified-orders/${props.orderId}`)
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
.verified-order-detail {
  padding: 0;
}
</style>

