# OrderSteps 订单步骤条组件

## 概述

`OrderSteps` 是一个数据驱动的订单进度展示组件，基于 Element Plus 的 `el-steps` 封装，支持回收订单、二手交易订单和官翻商品订单三种类型。

## 特性

✅ **数据驱动** - 只需传入订单对象，自动计算步骤和进度
✅ **居中对齐** - 使用 `align-center` 属性，完美适配弹窗和卡片
✅ **时间显示** - 自动显示每个步骤的完成时间
✅ **加载状态** - 支持显示进行中的加载图标
✅ **多种类型** - 支持回收、交易、官翻三种订单类型
✅ **响应式** - 自动适配移动端和桌面端

## 使用方法

### 基础用法

```vue
<template>
  <OrderSteps :order="order" type="recycle" />
</template>

<script setup>
import OrderSteps from '@/components/OrderSteps.vue'
import { ref } from 'vue'

const order = ref({
  status: 'shipped',
  created_at: '2025-12-14T17:47:13',
  shipped_at: '2025-12-14T18:30:00',
  // ... 其他订单数据
})
</script>
```

### 在卡片中使用

```vue
<template>
  <BaseCard title="订单进度" shadow="sm">
    <OrderSteps :order="order" type="recycle" />
  </BaseCard>
</template>
```

### 在对话框中使用

```vue
<template>
  <el-dialog v-model="visible" title="订单详情" width="800px">
    <OrderSteps :order="order" type="trade" />
  </el-dialog>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| order | 订单对象（必填） | Object | - | - |
| type | 订单类型 | String | recycle / trade / verified | recycle |

## 订单对象字段

### 回收订单 (type="recycle")

```typescript
{
  status: string,           // 订单状态：pending/quoted/confirmed/shipped/received/inspected/completed/cancelled
  created_at: string,       // 创建时间
  shipped_at?: string,      // 寄出时间
  received_at?: string,     // 收货时间
  inspected_at?: string,    // 检测时间
  completed_at?: string,    // 完成时间
  paid_at?: string,         // 打款时间
  payment_status?: string   // 打款状态：pending/paid/failed
}
```

**步骤说明：**
1. 提交订单 - 显示 `created_at`
2. 已寄出 - 显示 `shipped_at`，进行中时显示加载图标
3. 已收货 - 显示 `received_at`
4. 已检测 - 显示 `inspected_at`，进行中时显示加载图标
5. 已完成 - 显示 `completed_at`
6. 已打款 - 显示 `paid_at`

### 二手交易订单 (type="trade")

```typescript
{
  status: string,        // 订单状态：pending/paid/shipped/completed/cancelled
  created_at: string,    // 创建时间
  paid_at?: string,      // 付款时间
  shipped_at?: string,   // 发货时间
  completed_at?: string  // 完成时间
}
```

**步骤说明：**
1. 下单 - 显示 `created_at`
2. 付款 - 显示 `paid_at`，进行中时显示加载图标
3. 发货 - 显示 `shipped_at`，进行中时显示加载图标
4. 完成 - 显示 `completed_at`

### 官翻商品订单 (type="verified")

与二手交易订单相同。

## 状态映射

### 回收订单状态

| 后端状态 | 步骤索引 | 显示效果 |
|---------|---------|---------|
| pending | 0 | 第1步完成 |
| quoted | 1 | 第2步完成 |
| confirmed | 1 | 第2步完成 |
| shipped | 2 | 第2步进行中（加载图标） |
| received | 3 | 第3步进行中 |
| inspected | 4 | 第4步进行中（加载图标） |
| completed | 5 | 第5步进行中 |
| paid | 6 | 全部完成 |

### 交易订单状态

| 后端状态 | 步骤索引 | 显示效果 |
|---------|---------|---------|
| pending | 0 | 第1步完成 |
| paid | 1 | 第1步进行中（加载图标） |
| shipped | 2 | 第2步进行中（加载图标） |
| completed | 3 | 全部完成 |

## 样式定制

组件已经集成了设计系统的颜色和样式，如需自定义：

```vue
<style scoped>
/* 修改步骤标题颜色 */
.order-steps :deep(.el-step__title.is-process) {
  color: #your-color;
}

/* 修改时间文字大小 */
.order-steps :deep(.step-time) {
  font-size: 13px;
}
</style>
```

## 完整示例

### 回收订单详情页

```vue
<template>
  <PageContainer title="回收订单详情">
    <!-- 订单信息 -->
    <BaseCard title="订单信息" class="mb-6">
      <div class="order-info">
        <div>订单号：#{{ order.id }}</div>
        <div>设备：{{ order.brand }} {{ order.model }}</div>
      </div>
    </BaseCard>

    <!-- 订单进度 -->
    <BaseCard title="订单进度" shadow="sm">
      <OrderSteps :order="order" type="recycle" />
    </BaseCard>

    <!-- 其他信息... -->
  </PageContainer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/utils/api'
import PageContainer from '@/components/PageContainer.vue'
import BaseCard from '@/components/BaseCard.vue'
import OrderSteps from '@/components/OrderSteps.vue'

const route = useRoute()
const order = ref(null)

onMounted(async () => {
  const res = await api.get(`/recycle-orders/${route.params.id}/`)
  order.value = res.data
})
</script>
```

### 订单列表弹窗

```vue
<template>
  <el-dialog v-model="visible" title="订单进度" width="700px">
    <OrderSteps :order="selectedOrder" type="trade" />
    
    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import OrderSteps from '@/components/OrderSteps.vue'

const visible = ref(false)
const selectedOrder = ref(null)

const showOrderProgress = (order) => {
  selectedOrder.value = order
  visible.value = true
}
</script>
```

## 与旧代码对比

### ❌ 旧代码（不推荐）

```vue
<el-steps :space="200" :active="getStepActive()" finish-status="success">
  <el-step title="提交订单" :description="formatDate(order.created_at)"></el-step>
  <el-step title="已寄出" :description="order.shipped_at ? formatDate(order.shipped_at) : '待寄出'"></el-step>
  <el-step title="已收货" :description="order.status === 'received' ? '平台已收货' : '待收货'"></el-step>
  <el-step title="已检测" :description="order.inspected_at ? formatDate(order.inspected_at) : '待检测'"></el-step>
  <el-step title="已完成" :description="order.status === 'completed' ? '订单完成' : '待完成'"></el-step>
</el-steps>

<script>
const getStepActive = () => {
  const stepMap = {
    pending: 0,
    quoted: 1,
    confirmed: 2,
    shipped: 3,
    inspected: 4,
    completed: 5
  }
  return stepMap[order.value?.status] ?? 0
}

const formatDate = (dateString) => {
  // ... 格式化逻辑
}
</script>
```

**问题：**
- `:space="200"` 固定宽度，在弹窗中可能被截断
- 步骤名和描述硬编码，难以维护
- 需要手动编写状态映射逻辑
- 需要自己实现时间格式化

### ✅ 新代码（推荐）

```vue
<OrderSteps :order="order" type="recycle" />
```

**优势：**
- 一行代码搞定
- 自动居中对齐，适配各种容器
- 数据驱动，自动计算进度
- 内置时间格式化
- 支持加载状态
- 统一的样式和交互

## 注意事项

1. **必须传入 order 对象** - 组件依赖订单数据计算进度
2. **时间字段可选** - 如果某个时间字段不存在，会显示 "-"
3. **状态值要匹配** - 确保后端返回的 status 值与组件定义的状态映射一致
4. **响应式布局** - 在窄屏幕下，步骤标题可能会换行，这是正常的

## 扩展

如果需要添加新的订单类型，可以在组件中添加新的步骤配置：

```javascript
// 在 OrderSteps.vue 中添加
const customSteps = computed(() => {
  const order = props.order
  return [
    { title: '步骤1', time: formatTime(order.step1_at), status: 'step1' },
    { title: '步骤2', time: formatTime(order.step2_at), status: 'step2' },
    // ...
  ]
})
```

然后在 `stepList` computed 中添加对应的 case。

## 相关组件

- [BaseCard](./ui-design-system.md#1-basecard---卡片组件) - 卡片容器
- [PageContainer](./ui-design-system.md#2-pagecontainer---页面容器) - 页面容器
- [Element Plus Steps](https://element-plus.org/zh-CN/component/steps.html) - 原始步骤条组件
