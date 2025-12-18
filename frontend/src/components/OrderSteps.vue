<template>
  <el-steps 
    :active="activeStep" 
    finish-status="success" 
    align-center
    class="order-steps"
  >
    <el-step
      v-for="(step, index) in stepList"
      :key="index"
      :title="step.title"
    >
      <template #description>
        <div class="step-time">{{ step.time || '-' }}</div>
      </template>
      <template #icon v-if="step.loading">
        <el-icon class="is-loading">
          <Loading />
        </el-icon>
      </template>
    </el-step>
  </el-steps>
</template>

<script setup>
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { getRecycleProcessSteps, getRecycleStageIndex } from '@/utils/recycleFlow'

const props = defineProps({
  // 订单数据
  order: {
    type: Object,
    required: true
  },
  // 步骤类型：'recycle' | 'trade' | 'verified'
  type: {
    type: String,
    default: 'recycle',
    validator: (v) => ['recycle', 'trade', 'verified'].includes(v)
  }
})

// 格式化时间
const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '/')
}

// 回收订单步骤配置
const recycleSteps = computed(() => {
  const order = props.order
  const steps = getRecycleProcessSteps(order)
  return steps.map(s => {
    if (s.value === 'pending') {
      return { title: s.label, time: formatTime(order.created_at), status: s.value }
    }
    if (s.value === 'shipped') {
      return {
        title: s.label,
        time: order.shipped_at ? formatTime(order.shipped_at) : '',
        status: s.value,
        loading: order.status === 'shipped' && !order.received_at
      }
    }
    if (s.value === 'received') {
      return { title: s.label, time: order.received_at ? formatTime(order.received_at) : '', status: s.value }
    }
    if (s.value === 'inspected') {
      return {
        title: s.label,
        time: order.inspected_at ? formatTime(order.inspected_at) : '',
        status: s.value,
        loading:
          ['inspected', 'completed'].includes(order.status) &&
          !!order.final_price &&
          !order.final_price_confirmed &&
          !order.price_dispute
      }
    }
    if (s.value === 'completed') {
      return { title: s.label, time: order.completed_at ? formatTime(order.completed_at) : '', status: s.value }
    }
    if (s.value === 'paid') {
      return { title: s.label, time: order.paid_at ? formatTime(order.paid_at) : '', status: s.value }
    }
    return { title: s.label, time: '', status: s.value }
  })
})

// 二手交易订单步骤配置
const tradeSteps = computed(() => {
  const order = props.order
  return [
    {
      title: '下单',
      time: formatTime(order.created_at),
      status: 'pending'
    },
    {
      title: '付款',
      time: order.paid_at ? formatTime(order.paid_at) : '',
      status: 'paid',
      loading: order.status === 'paid' && !order.shipped_at
    },
    {
      title: '发货',
      time: order.shipped_at ? formatTime(order.shipped_at) : '',
      status: 'shipped',
      loading: order.status === 'shipped' && !order.completed_at
    },
    {
      title: '完成',
      time: order.completed_at ? formatTime(order.completed_at) : '',
      status: 'completed'
    }
  ]
})

// 官翻商品订单步骤配置
const verifiedSteps = computed(() => {
  const order = props.order
  return [
    {
      title: '下单',
      time: formatTime(order.created_at),
      status: 'pending'
    },
    {
      title: '付款',
      time: order.paid_at ? formatTime(order.paid_at) : '',
      status: 'paid',
      loading: order.status === 'paid' && !order.shipped_at
    },
    {
      title: '发货',
      time: order.shipped_at ? formatTime(order.shipped_at) : '',
      status: 'shipped',
      loading: order.status === 'shipped' && !order.completed_at
    },
    {
      title: '完成',
      time: order.completed_at ? formatTime(order.completed_at) : '',
      status: 'completed'
    }
  ]
})

// 根据类型选择步骤配置
const stepList = computed(() => {
  switch (props.type) {
    case 'recycle':
      return recycleSteps.value
    case 'trade':
      return tradeSteps.value
    case 'verified':
      return verifiedSteps.value
    default:
      return recycleSteps.value
  }
})

// 计算当前激活的步骤索引
const activeStep = computed(() => {
  const order = props.order
  const status = order.status
  
  if (props.type === 'recycle') {
    return getRecycleStageIndex(order) + 1
  } else {
    // 二手交易和官翻商品订单状态映射
    const statusMap = {
      'pending': 0,      // 下单
      'paid': 1,         // 付款（进行中）
      'shipped': 2,      // 发货（进行中）
      'completed': 3,    // 完成
      'cancelled': 0     // 已取消
    }
    
    return statusMap[status] ?? 0
  }
})
</script>

<style scoped>
.order-steps {
  padding: 20px 0;
}

/* 时间样式 */
.step-time {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  white-space: nowrap;
  line-height: 1.4;
}

/* 加载图标动画 */
.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 响应式：移动端调整 */
@media (max-width: 768px) {
  .order-steps {
    padding: 16px 0;
  }
  
  .step-time {
    font-size: 11px;
  }
  
  /* 移动端步骤标题可能需要换行 */
  .order-steps :deep(.el-step__title) {
    font-size: 13px;
    line-height: 1.3;
  }
}

/* 优化步骤条样式 */
.order-steps :deep(.el-step__head) {
  border-color: var(--border-default, #e6e8ee);
}

.order-steps :deep(.el-step__title) {
  font-weight: 600;
  color: var(--text-primary, #111827);
}

.order-steps :deep(.el-step__title.is-wait) {
  color: var(--text-tertiary, #9ca3af);
}

.order-steps :deep(.el-step__title.is-process) {
  color: var(--color-primary, #ff6a00);
  font-weight: 700;
}

.order-steps :deep(.el-step__title.is-finish) {
  color: var(--color-success, #10b981);
}

/* 步骤图标样式优化 */
.order-steps :deep(.el-step__icon) {
  width: 32px;
  height: 32px;
  font-size: 16px;
}

.order-steps :deep(.el-step__icon.is-text) {
  border-width: 2px;
}

.order-steps :deep(.el-step__line) {
  background-color: var(--border-light, #f0f0f0);
}

.order-steps :deep(.el-step__line-inner) {
  border-width: 2px;
}
</style>
