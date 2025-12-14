# 回收订单系统完整总结

## 系统概述

回收订单系统是一个完整的二手设备回收流程管理系统，涵盖从用户估价、订单提交、物流管理、质检评估、价格确认到最终打款的全流程。

## 核心功能

### 1. 估价系统
- 多维度估价：设备类型、品牌、型号、存储容量、成色
- 智能定价：基于模板价格、API价格、本地模型
- 价格明细：基础价格、成色调整、活动加价

### 2. 订单管理
- 订单创建：用户提交订单，状态为"待寄出"
- 物流管理：用户填写物流信息，自动变为"已寄出"
- 状态流转：pending → shipped → received → inspected → completed

### 3. 质检系统
- 66项检测：外观(15项)、屏幕(12项)、功能(30项)、维修记录(9项)
- 异常标记：不通过项目可上传图片
- 价格设定：管理员设置最终价格和加价

### 4. 价格确认
- 用户确认：用户必须确认最终价格才能进入打款阶段
- 价格异议：用户可对价格提出异议，管理员重新评估
- 自动流转：确认后订单自动变为"已完成"

### 5. 打款系统
- 多种方式：支付宝转账、平台钱包
- 打款记录：记录打款时间、方式、账户
- 交易记录：钱包交易记录可查询

## 技术架构

### 后端技术栈
- **框架**: Django + Django REST Framework
- **数据库**: PostgreSQL/MySQL
- **认证**: Token Authentication
- **权限**: 基于角色的权限控制

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router

### 核心模型

#### RecycleOrder（回收订单）
```python
class RecycleOrder(models.Model):
    # 基本信息
    user = ForeignKey(User)
    device_type = CharField()  # 设备类型
    brand = CharField()  # 品牌
    model = CharField()  # 型号
    storage = CharField()  # 存储容量
    condition = CharField()  # 成色
    
    # 价格信息
    estimated_price = DecimalField()  # 预估价格
    final_price = DecimalField()  # 最终价格
    bonus = DecimalField()  # 加价
    final_price_confirmed = BooleanField()  # 价格已确认
    
    # 状态信息
    status = CharField()  # 订单状态
    payment_status = CharField()  # 打款状态
    price_dispute = BooleanField()  # 价格异议
    
    # 物流信息
    shipping_carrier = CharField()  # 物流公司
    tracking_number = CharField()  # 运单号
    shipped_at = DateTimeField()  # 寄出时间
    received_at = DateTimeField()  # 收货时间
    
    # 质检信息
    inspected_at = DateTimeField()  # 质检时间
    
    # 打款信息
    payment_method = CharField()  # 打款方式
    payment_account = CharField()  # 打款账户
    paid_at = DateTimeField()  # 打款时间
```

#### AdminInspectionReport（质检报告）
```python
class AdminInspectionReport(models.Model):
    order = ForeignKey(RecycleOrder)
    check_items = JSONField()  # 66项检测结果
    remarks = TextField()  # 质检备注
    evidence = JSONField()  # 证据图片
    overall_result = CharField()  # 总体结果
    recommend_price = DecimalField()  # 推荐价格
    score = DecimalField()  # 评分
    template_name = CharField()  # 模板名称
    template_version = CharField()  # 模板版本
```

## 完整流程

### 用户端流程

```
1. 估价问卷
   ↓
2. 估价详情页
   - 查看预估价格
   - 查看价格明细
   - 确认收款信息
   ↓
3. 提交订单 (pending)
   - 订单创建
   - 跳转到订单详情
   ↓
4. 填写物流信息
   - 选择物流公司
   - 填写运单号
   - 自动变为 shipped
   ↓
5. 寄出设备
   - 按物流信息寄出
   - 等待平台收货
   ↓
6. 等待质检
   - 平台收货 (received)
   - 管理员质检 (inspected)
   ↓
7. 确认价格
   - 查看质检报告
   - 查看最终价格
   - 确认或提出异议
   ↓
8. 等待打款 (completed)
   - 管理员打款
   - 查看打款记录
```

### 管理端流程

```
1. 查看订单列表
   - 筛选状态
   - 搜索订单
   ↓
2. 确认收货 (shipped → received)
   - 点击"确认收到设备"
   ↓
3. 质检设备 (received → inspected)
   - 填写66项检测
   - 标记异常项目
   - 上传异常图片
   - 设置最终价格
   - 设置加价
   - 保存质检报告
   ↓
4. 等待用户确认
   - 显示"等待用户确认价格"
   - 用户确认后自动变为 completed
   ↓
5. 打款 (completed → paid)
   - 选择打款方式
   - 确认打款金额
   - 完成打款
```

## 状态机

```
┌─────────┐
│ pending │ 待寄出
└────┬────┘
     │ 用户填写物流信息
     ↓
┌─────────┐
│ shipped │ 已寄出
└────┬────┘
     │ 管理员确认收货
     ↓
┌──────────┐
│ received │ 已收货
└────┬─────┘
     │ 管理员质检并设置价格
     ↓
┌───────────┐
│ inspected │ 已检测
└────┬──────┘
     │ 用户确认价格
     ↓
┌───────────┐
│ completed │ 已完成
└────┬──────┘
     │ 管理员打款
     ↓
┌──────┐
│ paid │ 已打款
└──────┘
```

## API 端点

### 用户端 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/recycle-orders/estimate/` | POST | 估价接口 |
| `/api/recycle-orders/` | POST | 创建订单 |
| `/api/recycle-orders/` | GET | 获取订单列表 |
| `/api/recycle-orders/{id}/` | GET | 获取订单详情 |
| `/api/recycle-orders/{id}/` | PATCH | 更新订单（填写物流） |
| `/api/recycle-orders/{id}/inspection_report/` | GET | 获取质检报告 |
| `/api/recycle-orders/{id}/confirm_final_price/` | POST | 确认最终价格 |

### 管理端 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/admin-api/inspection-orders/` | GET | 获取订单列表 |
| `/admin-api/inspection-orders/{id}/` | GET | 获取订单详情 |
| `/admin-api/inspection-orders/{id}/` | PUT | 更新订单状态 |
| `/admin-api/inspection-orders/{id}/logistics/received` | POST | 确认收货 |
| `/admin-api/inspection-orders/{id}/report` | POST | 提交质检报告 |
| `/admin-api/inspection-orders/{id}/payment` | POST | 打款 |

## 关键特性

### 1. 自动状态流转
- 填写物流信息 → 自动变为"已寄出"
- 确认价格 → 自动变为"已完成"

### 2. 价格透明
- 显示基础价格、成色调整、加价
- 显示最终价格和实付金额

### 3. 用户权益保护
- 用户必须确认价格才能打款
- 用户可以对价格提出异议

### 4. 完整的质检系统
- 66项标准化检测
- 异常项目可上传图片
- 质检报告可查询

### 5. 灵活的打款方式
- 支持支付宝转账
- 支持平台钱包充值

## 权限控制

### 用户端权限
- 查看自己的订单：需要登录
- 填写物流信息：需要登录，订单属于当前用户
- 确认价格：需要登录，订单属于当前用户

### 管理端权限
- 查看订单：`inspection:view`
- 确认收货：`inspection:write`
- 质检并设置价格：`inspection:write`, `inspection:price`
- 打款：`inspection:payment`

## 数据安全

### 1. 认证机制
- 用户端：Token Authentication
- 管理端：JWT Authentication

### 2. 权限验证
- 用户只能操作自己的订单
- 管理员需要相应权限才能操作

### 3. 数据验证
- 前端表单验证
- 后端数据验证
- 状态流转验证

### 4. 审计日志
- 记录所有关键操作
- 包括操作人、操作时间、操作内容

## 性能优化

### 1. 数据库优化
- 使用 select_related 减少查询
- 使用 prefetch_related 优化关联查询
- 添加索引提高查询速度

### 2. 前端优化
- 组件懒加载
- 图片懒加载
- 分页加载

### 3. 缓存策略
- 价格模板缓存
- 用户信息缓存

## 扩展性

### 1. 支持多种设备类型
- 手机、平板、笔记本
- 可扩展到其他电子产品

### 2. 灵活的质检模板
- 支持自定义质检项目
- 支持多版本模板

### 3. 多种打款方式
- 支付宝转账
- 平台钱包
- 可扩展到微信、银行卡等

## 文档体系

### 用户文档
- `docs/USER-GUIDE-RECYCLE-ORDER.md` - 用户操作指南
- `docs/QUICK-START-PRICE-CONFIRMATION.md` - 快速开始指南

### 开发文档
- `docs/40-dev-guide/recycle-order-complete-workflow.md` - 完整工作流程
- `docs/40-dev-guide/recycle-order-price-confirmation.md` - 价格确认详细文档
- `docs/40-dev-guide/inspection-report-data-format.md` - 质检报告数据格式
- `docs/40-dev-guide/admin-inspection-report-editor.md` - 管理端质检编辑器

### API 文档
- `docs/30-api/inspection-report-api.md` - 质检报告 API

### 变更记录
- `docs/changelog.md` - 系统变更记录

## 测试建议

### 1. 功能测试
- 完整流程测试：从估价到打款
- 异常流程测试：价格异议、订单取消
- 边界条件测试：价格为0、物流信息缺失

### 2. 性能测试
- 并发订单创建
- 大量订单查询
- 质检报告加载

### 3. 安全测试
- 权限验证测试
- 数据验证测试
- SQL注入测试

## 未来规划

### 1. 功能增强
- 支持批量回收
- 支持上门取件
- 支持视频质检

### 2. 用户体验
- 实时物流跟踪
- 质检进度通知
- 打款到账通知

### 3. 数据分析
- 回收趋势分析
- 价格波动分析
- 用户行为分析

## 总结

回收订单系统是一个功能完整、流程清晰、安全可靠的二手设备回收管理系统。通过标准化的质检流程、透明的价格机制和灵活的打款方式，为用户提供了优质的回收体验，同时为管理员提供了高效的管理工具。

系统采用前后端分离架构，具有良好的扩展性和维护性，可以根据业务需求灵活调整和扩展功能。
