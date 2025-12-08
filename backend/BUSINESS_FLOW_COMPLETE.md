# 完整业务流程文档

## 回收业务流程

### 订单状态流转
```
pending (待估价) 
  ↓ [管理员给出预估价格]
quoted (已估价) 
  ↓ [用户确认]
confirmed (已确认) 
  ↓ [用户寄出设备，填写物流信息]
shipped (已寄出) 
  ↓ [平台收到设备]
inspected (已检测) 
  ↓ [管理员设置最终价格]
completed (已完成) 
  ↓ [管理员执行打款]
paid (已打款) → 钱存入用户钱包
```

### 关键操作点

1. **估价阶段**：管理员在订单详情页给出预估价格
2. **确认阶段**：用户在前端确认价格
3. **物流阶段**：用户填写物流信息，平台确认收到
4. **质检阶段**：平台创建质检报告，设置最终价格
5. **完成阶段**：订单状态变为已完成
6. **打款阶段**：
   - 管理员在订单详情页点击"执行打款"
   - 系统将钱存入用户钱包
   - 更新订单打款状态为"已打款"

## 钱包和提现流程

### 钱包功能
- **余额查询**：`GET /api/users/wallet/`
- **交易记录**：支持分页查询
- **提现功能**：`POST /api/users/withdraw/`

### 提现流程
1. 用户进入钱包页面
2. 点击"提现"按钮
3. 填写提现金额、支付宝账号、姓名（可选）
4. 系统调用支付宝转账接口（支持沙箱环境）
5. 提现成功/失败处理
6. 更新钱包余额和交易记录

### 提现支持
- ✅ 支持沙箱环境测试
- ✅ 支持生产环境
- ✅ 自动退回失败金额
- ✅ 完整的错误处理和日志记录

## 官方验货流程

### 发布为官方验商品
1. 回收订单完成后（inspected 或 completed 状态）
2. 管理员在订单详情页点击"发布为官方验商品"
3. 系统自动创建官方验商品
4. 商品自动上架到官方验货专区

### 官方验商品特点
- 来自回收订单，已完成质检
- 价格自动设置为回收价格的1.3倍
- 自动关联原回收订单信息
- 状态自动设为"active"（在售）

## 前端页面

### 用户端
- `/wallet` - 钱包页面（余额、交易记录、提现）
- `/profile` - 个人中心（包含钱包入口）
- `/my-recycle-orders` - 我的回收订单
- `/recycle-order/:id` - 回收订单详情

### 管理端
- `/admin/inspection-orders` - 回收订单列表
- `/admin/inspection-orders/:id` - 回收订单详情（包含打款功能）
- `/admin/verified-products` - 官方验商品管理

## API端点

### 钱包相关
- `GET /api/users/wallet/` - 获取钱包信息和交易记录
- `POST /api/users/withdraw/` - 提现到支付宝

### 回收订单相关
- `GET /api/recycle-orders/` - 获取回收订单列表
- `GET /api/recycle-orders/:id/` - 获取订单详情
- `POST /api/admin-api/inspection-orders/:id/payment` - 执行打款

### 官方验货相关
- `POST /api/admin-api/inspection-orders/:id/publish-verified` - 发布为官方验商品

## 配置说明

### 支付宝配置
- 当前使用沙箱环境：`https://openapi-sandbox.dl.alipaydev.com/gateway.do`
- 支持提现到沙箱支付宝账户
- 生产环境需要修改 `ALIPAY_GATEWAY_URL` 为生产地址

### 内网穿透
- 使用 ngrok 进行内网穿透
- 配置在 `BACKEND_URL` 中
- 用于支付宝回调通知










