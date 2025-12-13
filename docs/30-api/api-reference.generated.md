# API 参考（生成）

> 该文件由脚本生成：`python scripts/generate_api_reference.py`
> 请勿手工编辑。手工说明请写在 `docs/30-api/api-guide.md`。

- 生成日期：2025-12-13

## 用户端 API（/api）
- `/api/users/`  (ViewSet: `views`)
- `/api/categories/`  (ViewSet: `views`)
- `/api/products/`  (ViewSet: `views`)
- `/api/orders/`  (ViewSet: `views`)
- `/api/messages/`  (ViewSet: `views`)
- `/api/favorites/`  (ViewSet: `views`)
- `/api/addresses/`  (ViewSet: `views`)
- `/api/recycle-orders/`  (ViewSet: `views`)
- `/api/verified-products/`  (ViewSet: `views`)
- `/api/verified-orders/`  (ViewSet: `views`)
- `/api/verified-favorites/`  (ViewSet: `views`)
- `/api/payment/*`  (支付相关：create/query/notify 等，详见后端 urls 聚合)

## 管理端 API（/admin-api）
- `/admin-api/*`（建议：在此补充管理端关键入口，或增强脚本解析 admin_api 路由）

## WebSocket
- `/ws/chat/?token=<jwt>`
