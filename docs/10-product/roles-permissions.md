# 角色与权限（管理端）

## 权威来源（SSOT）
- `backend/app/admin_api/models.py`：`AdminUser`、`AdminRole`（含 `permissions` JSON 列表）

## 当前实现特征
- 管理端使用独立账户体系（AdminUser），与前台用户分离。
- 角色权限以 JSON 列表保存（例如 `["inspection:read", "inspection:write"]`）。

## 建议的权限点分组（毕业设计可用）
- inspection:*（回收订单/质检）
- verified:*（官方验库存/上架）
- payment:*（支付订单/结算）
- users:*（用户管理）
- catalog:*（分类/商品）

TODO: needs confirmation（请根据实际鉴权逻辑补齐权限点清单与映射关系）
