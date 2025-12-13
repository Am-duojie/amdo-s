# 核心流程与状态机（权威）

> 字段与状态来源：`backend/app/secondhand_app/models.py`。

## 二手交易（普通商品）
### 用户端流程
浏览/搜索 → 商品详情 → 私信沟通 → 下单 → 状态流转 → 完成/取消

### 订单状态（Order.status）
- `pending`：待付款
- `paid`：已付款
- `shipped`：已发货
- `completed`：已完成
- `cancelled`：已取消

## 回收流程（RecycleOrder）
### 用户端流程
回收入口 → 估价问卷 → 提交回收订单 → 我的回收订单 → 详情/进度

### 管理端流程
回收订单列表 → 物流/收货 → 质检报告 → 定价 → 打款 →（可选）发布为官方验 → 完成

### 回收订单状态（RecycleOrder.status）
- `pending`：待估价
- `quoted`：已估价
- `confirmed`：已确认
- `shipped`：已寄出
- `inspected`：已检测
- `completed`：已完成
- `cancelled`：已取消

### 打款状态（RecycleOrder.payment_status，与 status 分离）
- `pending`：待打款
- `paid`：已打款
- `failed`：打款失败

### 关键约束
- `status` 代表业务流程，`payment_status` 代表打款结果；两者不能混用为同一筛选条件。
- 管理端页面应分别提供“流程状态”和“打款状态”筛选，并分别映射到后端参数。

## 官方验业务线

### 业务流程概述
回收质检合格设备生成库存（VerifiedDevice），再发布为官方验商品（VerifiedProduct），用户下单产生 VerifiedOrder（与普通 Order 分离）。

### 库存设备状态（VerifiedDevice.status）
- `pending`：待处理
- `repairing`：维修/翻新中
- `ready`：待上架
- `listed`：在售
- `locked`：已锁定
- `sold`：已售出
- `removed`：已下架

### 官方验商品状态（VerifiedProduct.status）
- `draft`：草稿
- `pending`：待审核
- `active`：在售
- `sold`：已售出
- `removed`：已下架

### 官方验订单状态（VerifiedOrder.status）
- `pending`：待付款
- `paid`：已付款
- `shipped`：已发货
- `completed`：已完成
- `cancelled`：已取消

### 管理端流程
1. **从回收订单创建库存**：回收订单质检通过（`inspected` 或 `completed`）后，可创建 VerifiedDevice（状态为 `ready`）
2. **库存处理**：设备进入 `repairing`（维修/翻新）或直接 `ready`（待上架）
3. **发布商品**：从 VerifiedDevice 创建或关联 VerifiedProduct，状态为 `draft` 或 `pending`
4. **审核上架**：管理端审核通过后，VerifiedProduct 状态变为 `active`
5. **订单处理**：用户下单后，VerifiedOrder 状态流转：`pending` → `paid` → `shipped` → `completed`

### 关键约束
- VerifiedDevice 与 RecycleOrder 通过 `recycle_order` 外键关联（可为空）
- VerifiedDevice 与 VerifiedProduct 通过 `linked_product` 外键关联（可为空）
- VerifiedProduct 的 `stock` 字段表示库存数量（默认 1）
- VerifiedOrder 与普通 Order 完全分离，使用独立的订单表

> 字段来源：`backend/app/secondhand_app/models.py`（VerifiedDevice、VerifiedProduct、VerifiedOrder 类定义）
