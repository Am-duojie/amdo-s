# 回收订单价格确认流程

## 概述

回收订单的价格确认流程确保用户在质检完成后有机会确认最终价格，只有在用户确认后订单才会进入打款阶段。

## 工作流程

### 1. 用户提交订单并填写物流信息

用户提交订单后：
1. 订单状态为 `pending`（待估价）
2. 用户在订单详情页填写物流信息（物流公司、运单号）
3. 提交物流信息后，订单状态自动变为 `shipped`（已寄出）

### 2. 管理员完成质检并设置最终价格

管理员在质检完成后：
1. 确认收货，订单状态变为 `received`（已收货）
2. 填写质检报告（66项检测）
3. 设置最终价格和加价（如有）
4. 订单状态变为 `inspected`（已检测）
5. `final_price_confirmed` 字段为 `false`

### 3. 用户确认价格

用户在订单详情页看到：
- 最终价格和加价金额
- "确认最终价格" 按钮
- "对最终价格有异议" 按钮

用户点击"确认最终价格"后：
1. 调用 API: `POST /api/recycle-orders/{id}/confirm_final_price/`
2. `final_price_confirmed` 字段变为 `true`
3. 订单状态自动变为 `completed`（已完成）
4. 订单进入打款阶段

### 4. 管理员打款

订单完成后，管理员可以：
1. 在订单详情页看到"打款给用户"按钮
2. 选择打款方式（支付宝转账/钱包）
3. 完成打款操作

## 状态流转

```
pending (待估价) - 用户提交订单
  ↓ 用户填写物流信息
  ↓
shipped (已寄出) - 自动变更
  ↓ 管理员确认收货
  ↓
received (已收货)
  ↓ 管理员完成质检并设置最终价格
  ↓
inspected (已检测)
  ↓ [等待用户确认价格]
  ↓ 用户点击"确认最终价格"
  ↓
completed (已完成) - 自动进入打款阶段
  ↓ 管理员打款
  ↓
paid (已打款)
```

## API 接口

### 用户确认最终价格

**端点**: `POST /api/recycle-orders/{id}/confirm_final_price/`

**权限**: 需要登录，且订单属于当前用户

**请求**: 无需请求体

**响应**:
```json
{
  "success": true,
  "message": "价格确认成功，订单已进入打款阶段",
  "order": {
    "id": 123,
    "status": "completed",
    "final_price_confirmed": true,
    ...
  }
}
```

**错误响应**:
- `403`: 无权访问此订单
- `400`: 订单状态不正确（只有 `inspected` 状态可以确认）
- `400`: 订单尚未设置最终价格
- `400`: 订单价格已确认，无需重复确认

## 数据模型

### RecycleOrder 字段

- `final_price`: 最终价格（管理员设置）
- `bonus`: 加价金额（管理员设置）
- `final_price_confirmed`: 用户是否确认最终价格（布尔值）
- `status`: 订单状态

## 前端实现

### 用户端 (RecycleOrderDetail.vue)

**已检测状态显示**:
```vue
<template v-if="order.status === 'inspected'">
  <el-button type="primary" size="large" @click="confirmFinalPrice">
    确认最终价格
  </el-button>
  <el-button type="warning" size="large" @click="showFinalDisputeDialog = true">
    对最终价格有异议
  </el-button>
</template>
```

**确认价格函数**:
```javascript
const confirmFinalPrice = async () => {
  const finalPrice = order.value.final_price
  const bonus = order.value.bonus || 0
  const totalPrice = (parseFloat(finalPrice) + parseFloat(bonus)).toFixed(2)
  
  await ElMessageBox.confirm(
    `确认接受最终价格 ¥${finalPrice}${bonus > 0 ? ` + 加价 ¥${bonus}` : ''} = ¥${totalPrice} 吗？确认后订单将进入打款阶段。`, 
    '确认最终价格'
  )

  await api.post(`/recycle-orders/${order.value.id}/confirm_final_price/`)
  ElMessage.success('已确认最终价格，订单已进入打款阶段')
  await loadOrderDetail()
}
```

### 管理端 (RecycleOrderDetail.vue)

**等待确认提示**:
```vue
<el-alert
  v-if="detail.status === 'inspected' && detail.final_price && !detail.final_price_confirmed"
  type="warning"
  :closable="false"
>
  <template #title>
    <div style="display: flex; align-items: center; gap: 8px;">
      <el-icon><Clock /></el-icon>
      <span>等待用户确认最终价格 ¥{{ detail.final_price }}</span>
    </div>
  </template>
  用户确认价格后，订单将自动进入打款阶段
</el-alert>
```

## 业务规则

1. **只有已检测状态可以确认**: 订单必须处于 `inspected` 状态
2. **必须有最终价格**: 管理员必须先设置 `final_price`
3. **不可重复确认**: `final_price_confirmed` 为 `true` 后不能再次确认
4. **自动完成订单**: 确认价格后订单自动变为 `completed` 状态
5. **价格异议**: 用户可以选择提出价格异议，订单保持 `inspected` 状态

## 注意事项

1. **向后兼容**: 旧订单（没有 `final_price_confirmed` 字段）默认为 `false`
2. **管理员操作**: 管理员不能代替用户确认价格
3. **打款前提**: 只有 `final_price_confirmed` 为 `true` 且状态为 `completed` 才能打款
4. **日志记录**: 用户确认价格的操作会记录在日志中

## 测试场景

### 正常流程
1. 管理员完成质检并设置最终价格 ¥1000
2. 用户看到最终价格 ¥1000
3. 用户点击"确认最终价格"
4. 订单状态变为 `completed`
5. 管理员可以打款

### 异议流程
1. 管理员完成质检并设置最终价格 ¥800
2. 用户认为价格过低
3. 用户点击"对最终价格有异议"
4. 填写异议原因
5. 订单保持 `inspected` 状态，`price_dispute` 为 `true`
6. 管理员重新评估并调整价格

### 错误场景
1. 用户尝试确认未检测的订单 → 400 错误
2. 用户尝试确认没有最终价格的订单 → 400 错误
3. 用户尝试重复确认 → 400 错误
4. 用户尝试确认他人订单 → 403 错误

## 相关文件

- **后端模型**: `backend/app/secondhand_app/models.py` - RecycleOrder
- **后端视图**: `backend/app/secondhand_app/views.py` - RecycleOrderViewSet.confirm_final_price
- **后端序列化器**: `backend/app/secondhand_app/serializers.py` - RecycleOrderSerializer
- **管理端视图**: `backend/app/admin_api/views.py` - InspectionOrderDetailView
- **用户端组件**: `frontend/src/pages/RecycleOrderDetail.vue`
- **管理端组件**: `frontend/src/admin/pages/components/RecycleOrderDetail.vue`
