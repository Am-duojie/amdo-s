# 角色与权限（管理端）

## 权威来源（SSOT）
- `backend/app/admin_api/models.py`：`AdminUser`、`AdminRole`（含 `permissions` JSON 列表）

## 当前实现特征
- 管理端使用独立账户体系（AdminUser），与前台用户分离。
- 角色权限以 JSON 列表保存（例如 `["inspection:read", "inspection:write"]`）。

## 权限点清单（基于代码实现）

### 回收订单/质检（inspection）
- `inspection:view`：查看回收订单列表和详情
- `inspection:write`：更新订单状态、创建质检报告、录入物流信息、定价、完成订单
- `inspection:payment`：打款操作（前端使用，后端实际检查 `inspection:write`）
- `inspection:price`：估价和定价操作（前端使用）

### 官方验（verified）
- `verified:view`：查看官方验商品、订单列表
- `verified:read`：读取官方验详情（部分接口使用）
- `verified:write`：创建/更新/发布/下架官方验商品，更新官方验订单状态

### 回收商品发布（recycled）
- `recycled:view`：查看已回收商品列表
- `recycled:write`：将回收订单发布为官方验商品，管理回收商品上下架

### 支付/订单（payment）
- `payment:view`：查看支付记录、分账详情
- `payment:write`：退款、重试分账
- `order:ship`：发货操作（普通订单）

### 用户管理（user）
- `user:view`：查看前台用户列表
- `user:write`：编辑用户信息
- `user:delete`：删除用户

### 商品管理（product）
- `product:view`：查看普通商品列表
- `product:write`：发布/下架/标记已售商品
- `product:delete`：删除商品

### 分类管理（category）
- `category:view`：查看分类列表
- `category:write`：创建/编辑分类
- `category:delete`：删除分类

### 店铺管理（shop）
- `shop:view`：查看店铺列表
- `shop:write`：创建/编辑店铺
- `shop:delete`：删除店铺

### 消息管理（message）
- `message:view`：查看消息列表
- `message:delete`：删除消息

### 地址管理（address）
- `address:view`：查看地址列表
- `address:delete`：删除地址

### 审核队列（audit）
- `audit:view`：查看审核队列
- `audit:write`：审核通过/驳回操作

### 审计日志（audit_log）
- `audit_log:view`：查看操作审计日志

### 管理员/角色（admin_user, role）
- `admin_user:view`：查看管理员列表
- `admin_user:write`：创建/编辑管理员
- `role:view`：查看角色列表
- `role:write`：创建/编辑角色

### 仪表盘（dashboard）
- `dashboard:view`：查看仪表盘统计数据

### 特殊权限
- `*`：通配符，表示拥有所有权限（超级管理员）

## 权限检查机制
- 后端：`backend/app/admin_api/views.py` 中的 `has_perms(admin, perms_list)` 函数
- 前端：`frontend/src/stores/adminAuth.js` 中的 `hasPerm(code)` 方法
- 权限存储在 `AdminRole.permissions` JSON 字段中，支持字符串数组
- 权限检查支持通配符 `*`，拥有该权限的管理员可访问所有功能

> 权限点来源：`backend/app/admin_api/views.py`（各视图的 `has_perms` 调用）和 `backend/app/admin_api/management/commands/seed_admin.py`（初始权限配置）
