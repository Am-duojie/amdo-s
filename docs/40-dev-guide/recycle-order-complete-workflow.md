# 回收订单完整工作流程

## 流程概览

回收订单从用户提交到最终打款完成，经历以下5个主要阶段：

```
1. 用户提交订单 (pending)
   ↓
2. 用户填写物流并寄出 (shipped)
   ↓
3. 管理员收货并质检 (received → inspected)
   ↓
4. 用户确认价格 (completed)
   ↓
5. 管理员打款（payment_status=paid）
```

## 详细流程

### 阶段 1: 用户提交订单

**操作者**: 用户

**步骤**:
1. 用户在前端完成设备估价问卷（`RecycleEstimateWizard.vue`）
2. 填写设备信息（品牌、型号、存储容量、成色等）
3. 系统自动估价，显示预估价格
4. 跳转到估价详情页（`RecycleCheckout.vue`）
5. 用户查看估价详情：
   - 预估价格
   - 价格明细（基础价格、成色调整、加价）
   - 平台收件地址
   - 收款信息
6. 用户点击"提交订单"按钮
7. 确认提交
8. 订单创建成功，跳转到订单详情页

**状态变化**:
- 订单创建，状态为 `pending`（待寄出）
- `estimated_price` 字段保存预估价格

**数据库操作**:
```python
RecycleOrder.objects.create(
    user=current_user,
    device_type='手机',
    brand='苹果',
    model='iPhone 13',
    storage='128GB',
    condition='good',
    estimated_price=3200.00,
    status='pending',
    contact_name='张三',
    contact_phone='13800138000',
    address='平台收件地址'
)
```

**前端页面**: 
- 估价问卷：`RecycleEstimateWizard.vue`
- 估价详情：`RecycleCheckout.vue`
- 订单详情：`RecycleOrderDetail.vue`

**API端点**: `POST /api/recycle-orders/`

---

### 阶段 2: 用户填写物流信息

**操作者**: 用户

**步骤**:
1. 用户进入"我的回收订单"
2. 点击订单查看详情
3. 点击"填写物流信息"按钮
4. 选择物流公司（顺丰、圆通等）
5. 填写运单号
6. 提交物流信息
7. 用户按照物流信息寄出设备

**状态变化**: 
- 订单状态从 `pending` 自动变为 `shipped`（已寄出）
- `shipping_carrier` 和 `tracking_number` 字段被填充
- `shipped_at` 字段设置为当前时间

**后端逻辑**:
```python
# 在 RecycleOrderSerializer.update 中
if current_status == 'pending' and 'shipping_carrier' in validated_data and 'tracking_number' in validated_data:
    if validated_data.get('shipping_carrier') and validated_data.get('tracking_number'):
        validated_data['status'] = 'shipped'
        validated_data['shipped_at'] = timezone.now()
```

**前端页面**: `RecycleOrderDetail.vue`

**API端点**: `PATCH /api/recycle-orders/{id}/`

**请求体**:
```json
{
  "shipping_carrier": "顺丰速运",
  "tracking_number": "SF1234567890"
}
```

---

### 阶段 3: 管理员收货并质检

**操作者**: 管理员

#### 3.1 确认收货

**步骤**:
1. 管理员在后台查看"已寄出"的订单
2. 实际收到设备后，点击"确认收到设备"按钮

**状态变化**: 
- 订单状态从 `shipped` 变为 `received`（已收货）
- `received_at` 字段设置为当前时间

**API端点**: `POST /admin-api/inspection-orders/{id}/received`

#### 3.2 质检并设置价格

**步骤**:
1. 点击"开始质检"按钮
2. 填写66项质检报告：
   - 外观检测（15项）
   - 屏幕检测（12项）
   - 功能检测（30项）
   - 维修记录（9项）
3. 对于有问题的项目，标记为"不通过"并上传异常图片
4. 填写质检备注
5. 设置最终价格（可以与预估价格不同）
6. 设置加价金额（如有活动）
7. 保存质检报告

**状态变化**: 
- 订单状态从 `received` 变为 `inspected`（已检测）
- `inspected_at` 字段设置为当前时间
- `final_price` 字段设置为管理员确定的价格
- `bonus` 字段设置为加价金额
- `final_price_confirmed` 字段为 `false`（等待用户确认）
- 创建 `AdminInspectionReport` 记录

**API端点**: `POST /admin-api/inspection-orders/{id}/report`

**请求体**:
```json
{
  "check_items": [
    {
      "category": "外观检测",
      "label": "机身外观",
      "result": "轻微划痕",
      "pass": false,
      "image": "https://example.com/scratch.jpg"
    },
    // ... 其他65项
  ],
  "remarks": "设备整体状况良好，仅有轻微使用痕迹",
  "final_price": 3000.00,
  "bonus": 50.00
}
```

**前端页面**: `RecycleOrderDetail.vue` (管理端)

---

### 阶段 4: 用户确认价格

**操作者**: 用户

**步骤**:
1. 用户收到质检完成通知（可选）
2. 进入订单详情页
3. 查看质检报告和最终价格
4. 查看价格明细：
   - 最终价格: ¥3000
   - 加价: ¥50
   - 实付金额: ¥3050
5. 选择操作：
   - **确认价格**: 点击"确认最终价格"按钮
   - **提出异议**: 点击"对最终价格有异议"按钮

#### 4.1 确认价格

**步骤**:
1. 点击"确认最终价格"
2. 在确认对话框中再次查看价格
3. 点击"确认"

**状态变化**: 
- `final_price_confirmed` 字段变为 `true`
- 订单状态从 `inspected` 自动变为 `completed`（已完成）

**API端点**: `POST /api/recycle-orders/{id}/confirm_final_price/`

**响应**:
```json
{
  "success": true,
  "message": "价格确认成功，订单已进入打款阶段",
  "order": {
    "id": 123,
    "status": "completed",
    "final_price_confirmed": true,
    "final_price": "3000.00",
    "bonus": "50.00"
  }
}
```

#### 4.2 提出价格异议

**步骤**:
1. 点击"对最终价格有异议"
2. 填写异议原因
3. 提交异议

**状态变化**: 
- `price_dispute` 字段变为 `true`
- `price_dispute_reason` 字段保存异议原因
- 订单保持 `inspected` 状态
- 管理员需要重新评估并调整价格

**API端点**: `PATCH /api/recycle-orders/{id}/`

**请求体**:
```json
{
  "price_dispute": true,
  "price_dispute_reason": "设备实际成色比质检报告描述的要好，价格应该更高"
}
```

**前端页面**: `RecycleOrderDetail.vue`

---

### 阶段 5: 管理员打款

**操作者**: 管理员

**前提条件**:
- 订单状态为 `completed`
- `final_price_confirmed` 为 `true`
- 用户已绑定支付宝账号（如果使用支付宝转账）

**步骤**:
1. 在订单详情页点击"打款给用户"按钮
2. 选择打款方式：
   - **支付宝转账**: 直接转账到用户支付宝账号
   - **钱包**: 将金额充值到用户平台钱包
3. 确认打款金额（最终价格 + 加价）
4. 填写打款备注（可选）
5. 确认打款

**状态变化**:
- `payment_status` 从 `pending` 变为 `paid`（已打款）
- `paid_at` 字段设置为当前时间
- `payment_method` 字段保存打款方式
- `payment_account` 字段保存打款账户
- 如果使用钱包方式，创建 `WalletTransaction` 记录

**API端点**: `POST /admin-api/inspection-orders/{id}/payment`

**请求体**:
```json
{
  "payment_method": "transfer",
  "payment_account": "user@alipay.com",
  "payment_note": "回收订单#123打款"
}
```

**前端页面**: `RecycleOrderDetail.vue` (管理端)

---

## 状态机图

```
┌─────────┐
│ pending │ 用户提交订单
└────┬────┘
     │ 用户填写物流信息
     ↓
┌─────────┐
│ shipped │ 设备已寄出
└────┬────┘
     │ 管理员确认收货
     ↓
┌──────────┐
│ received │ 平台已收货
└────┬─────┘
     │ 管理员质检并设置价格
     ↓
┌───────────┐
│ inspected │ 质检完成，等待用户确认
└────┬──────┘
     │ 用户确认价格
     ↓
┌───────────┐
│ completed │ 订单完成，等待打款
└────┬──────┘
      │ 管理员打款
      ↓
payment_status = paid（打款完成）
```

> 说明：当前实现里，“打款完成”通过字段 `payment_status=paid` 表示，订单 `status` 仍保持为 `completed`（便于区分“业务流程完成”和“资金处理完成”两层状态）。

## 异常流程

### 用户取消订单

**时机**: 订单状态为 `pending` 或 `shipped` 时

**操作**: 
- 用户或管理员可以取消订单
- 订单状态变为 `cancelled`
- 填写取消原因

### 价格异议处理

**时机**: 订单状态为 `inspected` 时

**流程**:
1. 用户提出价格异议
2. `price_dispute` 变为 `true`
3. 管理员查看异议原因
4. 管理员重新评估并调整价格
5. 保存新的最终价格
6. 用户重新确认价格

### 打款失败

**时机**: 管理员打款时

**处理**:
- `payment_status` 变为 `failed`
- 记录失败原因
- 管理员可以重试打款
- `payment_retry_count` 字段记录重试次数

## 关键字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 订单状态 |
| estimated_price | decimal | 预估价格（用户提交时） |
| final_price | decimal | 最终价格（管理员设置） |
| bonus | decimal | 加价金额 |
| final_price_confirmed | boolean | 用户是否确认最终价格 |
| payment_status | string | 打款状态 |
| price_dispute | boolean | 是否有价格异议 |
| shipping_carrier | string | 物流公司 |
| tracking_number | string | 运单号 |
| shipped_at | datetime | 寄出时间 |
| received_at | datetime | 收货时间 |
| inspected_at | datetime | 质检时间 |
| paid_at | datetime | 打款时间 |

## 权限要求

### 用户端
- 查看自己的订单: 需要登录
- 填写物流信息: 需要登录，订单属于当前用户
- 确认价格: 需要登录，订单属于当前用户

### 管理端
- 查看订单: `inspection:view`
- 确认收货: `inspection:write`
- 质检并设置价格: `inspection:write`, `inspection:price`
- 打款: `inspection:payment`

## 相关文件

### 后端
- `backend/app/secondhand_app/models.py` - RecycleOrder 模型
- `backend/app/secondhand_app/views.py` - 用户端 API
- `backend/app/secondhand_app/serializers.py` - 序列化器
- `backend/app/admin_api/views.py` - 管理端 API
- `backend/app/admin_api/models.py` - AdminInspectionReport 模型

### 前端
- `frontend/src/pages/RecycleOrderDetail.vue` - 用户端订单详情
- `frontend/src/admin/pages/components/RecycleOrderDetail.vue` - 管理端订单详情
- `frontend/src/pages/RecycleCheckout.vue` - 订单提交页面

### 文档
- `docs/40-dev-guide/recycle-order-price-confirmation.md` - 价格确认详细文档
- `docs/QUICK-START-PRICE-CONFIRMATION.md` - 快速开始指南
- `docs/40-dev-guide/inspection-report-data-format.md` - 质检报告数据格式
