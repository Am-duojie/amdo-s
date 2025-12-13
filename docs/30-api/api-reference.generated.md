# API 参考（生成）

> 该文件由脚本生成：`python scripts/generate_api_reference.py`
> 请勿手工编辑。手工说明请写在 `docs/30-api/api-guide.md`。

- 生成日期：2025-12-13
- 占位符说明：`<id>` 表示资源主键（DRF 默认 pk）

## 用户端 API（/api）— 资源（DefaultRouter）

### `users` (ViewSet: `UserViewSet`)

标准路由：
- `GET` `/api/users/`
- `POST` `/api/users/`
- `GET` `/api/users/<id>/`
- `PUT` `/api/users/<id>/`
- `PATCH` `/api/users/<id>/`
- `DELETE` `/api/users/<id>/`

自定义 @action：
- `GET,PATCH` `/api/users/me/` — 获取或更新当前用户信息
- `POST` `/api/users/register/` — 用户注册
- `POST` `/api/users/upload_avatar/` — 上传头像
- `POST` `/api/users/login/` — 用户登录
- `GET` `/api/users/wallet/` — 获取当前用户钱包信息
- `POST` `/api/users/withdraw/` — 提现到支付宝

### `categories` (ViewSet: `CategoryViewSet`)

标准路由：
- `GET` `/api/categories/`
- `GET` `/api/categories/<id>/`

自定义 @action：
- （无）

### `products` (ViewSet: `ProductViewSet`)

标准路由：
- `GET` `/api/products/`
- `POST` `/api/products/`
- `GET` `/api/products/<id>/`
- `PUT` `/api/products/<id>/`
- `PATCH` `/api/products/<id>/`
- `DELETE` `/api/products/<id>/`

自定义 @action：
- `PATCH` `/api/products/<id>/update_status/` — 更新商品状态
- `POST` `/api/products/<id>/upload_images/` — 上传商品图片
- `POST` `/api/products/<id>/favorite/` — 收藏商品
- `POST` `/api/products/<id>/unfavorite/` — 取消收藏商品
- `GET` `/api/products/my_products/` — 获取当前用户发布的商品（包括所有状态）
- `GET` `/api/products/my_sales/` — 获取当前用户作为卖家的订单（含结算状态与账户）

### `orders` (ViewSet: `OrderViewSet`)

标准路由：
- `GET` `/api/orders/`
- `POST` `/api/orders/`
- `GET` `/api/orders/<id>/`
- `PUT` `/api/orders/<id>/`
- `PATCH` `/api/orders/<id>/`
- `DELETE` `/api/orders/<id>/`

自定义 @action：
- `PATCH` `/api/orders/<id>/update_status/` — 更新订单状态

### `messages` (ViewSet: `MessageViewSet`)

标准路由：
- `GET` `/api/messages/`
- `POST` `/api/messages/`
- `GET` `/api/messages/<id>/`
- `PUT` `/api/messages/<id>/`
- `PATCH` `/api/messages/<id>/`
- `DELETE` `/api/messages/<id>/`

自定义 @action：
- `GET` `/api/messages/conversations/` — 获取对话列表（与当前用户有过消息交流的用户）
- `GET` `/api/messages/with_user/` — 获取与指定用户的消息记录
- `POST` `/api/messages/read/` — 将与指定用户的消息标记为已读
- `POST` `/api/messages/<id>/recall/` — 撤回消息（仅限发送者且在可撤回时间内）
- `POST` `/api/messages/upload_image/` — 上传图片消息

### `favorites` (ViewSet: `FavoriteViewSet`)

标准路由：
- `GET` `/api/favorites/`
- `POST` `/api/favorites/`
- `GET` `/api/favorites/<id>/`
- `PUT` `/api/favorites/<id>/`
- `PATCH` `/api/favorites/<id>/`
- `DELETE` `/api/favorites/<id>/`

自定义 @action：
- `POST` `/api/favorites/remove/` — 取消收藏

### `addresses` (ViewSet: `AddressViewSet`)

标准路由：
- `GET` `/api/addresses/`
- `POST` `/api/addresses/`
- `GET` `/api/addresses/<id>/`
- `PUT` `/api/addresses/<id>/`
- `PATCH` `/api/addresses/<id>/`
- `DELETE` `/api/addresses/<id>/`

自定义 @action：
- （无）

### `recycle-orders` (ViewSet: `RecycleOrderViewSet`)

标准路由：
- `GET` `/api/recycle-orders/`
- `POST` `/api/recycle-orders/`
- `GET` `/api/recycle-orders/<id>/`
- `PUT` `/api/recycle-orders/<id>/`
- `PATCH` `/api/recycle-orders/<id>/`
- `DELETE` `/api/recycle-orders/<id>/`

自定义 @action：
- `GET` `/api/recycle-orders/<id>/inspection_report/` — 获取订单的质检报告
- `POST` `/api/recycle-orders/estimate/` — 估价接口 - 使用智能估价模型

### `verified-products` (ViewSet: `VerifiedProductViewSet`)

标准路由：
- `GET` `/api/verified-products/`
- `POST` `/api/verified-products/`
- `GET` `/api/verified-products/<id>/`
- `PUT` `/api/verified-products/<id>/`
- `PATCH` `/api/verified-products/<id>/`
- `DELETE` `/api/verified-products/<id>/`

自定义 @action：
- `POST` `/api/verified-products/<id>/upload_images/` — 上传商品图片
- `POST` `/api/verified-products/<id>/favorite/` — 收藏商品
- `POST` `/api/verified-products/<id>/unfavorite/` — 取消收藏商品
- `GET` `/api/verified-products/my_products/` — 获取当前用户发布的官方验货商品

### `verified-orders` (ViewSet: `VerifiedOrderViewSet`)

标准路由：
- `GET` `/api/verified-orders/`
- `POST` `/api/verified-orders/`
- `GET` `/api/verified-orders/<id>/`
- `PUT` `/api/verified-orders/<id>/`
- `PATCH` `/api/verified-orders/<id>/`
- `DELETE` `/api/verified-orders/<id>/`

自定义 @action：
- `PATCH` `/api/verified-orders/<id>/update_status/` — 更新订单状态

### `verified-favorites` (ViewSet: `VerifiedFavoriteViewSet`)

标准路由：
- `GET` `/api/verified-favorites/`
- `POST` `/api/verified-favorites/`
- `GET` `/api/verified-favorites/<id>/`
- `PUT` `/api/verified-favorites/<id>/`
- `PATCH` `/api/verified-favorites/<id>/`
- `DELETE` `/api/verified-favorites/<id>/`

自定义 @action：
- （无）

## 用户端 API（/api）— 显式接口（非 Router）
- `GET` `/api/recycle-catalog/`  (target: `views.RecycleCatalogView.as_view`)
- `(METHODS UNKNOWN)` `/api/recycle-templates/question-template/`  (target: `views.RecycleQuestionTemplateView.as_view`)
- `POST` `/api/auth/login/`  (target: `CustomTokenObtainPairView.as_view`)
- `POST` `/api/auth/refresh/`  (target: `TokenRefreshView.as_view`)
- `POST` `/api/payment/create/`  (target: `payment_views.create_payment`)
- `POST` `/api/payment/create-url/`  (target: `payment_views.create_payment_url`)
- `GET` `/api/payment/query/<int:order_id>/`  (target: `payment_views.query_payment`)
- `GET,POST` `/api/payment/redirect/`  (target: `payment_views.payment_redirect`)
- `GET,POST` `/api/payment/alipay/notify/`  (target: `payment_views.alipay_payment_notify`)

## 管理端 API（/admin-api）

### `addresses`
- `DELETE,GET` `/admin-api/addresses/<int:aid>`
- `DELETE,GET` `/admin-api/addresses`

### `audit`
- `GET,POST` `/admin-api/audit/queue/<int:qid>/decision`
- `GET,POST` `/admin-api/audit/queue`
- `GET` `/admin-api/audit/logs`

### `auth`
- `GET` `/admin-api/auth/me`
- `POST` `/admin-api/auth/change-password`
- `POST` `/admin-api/auth/login`
- `POST` `/admin-api/auth/logout`
- `POST` `/admin-api/auth/refresh`

### `categories`
- `DELETE,GET,POST,PUT` `/admin-api/categories/<int:cid>`
- `DELETE,GET,POST,PUT` `/admin-api/categories`

### `dashboard`
- `GET` `/admin-api/dashboard/metrics`

### `frontend-users`
- `DELETE,GET,POST` `/admin-api/frontend-users/<int:uid>`
- `DELETE,GET,POST` `/admin-api/frontend-users`

### `inspection-orders`
- `GET,POST,PUT` `/admin-api/inspection-orders/<int:order_id>/report`
- `GET,POST,PUT` `/admin-api/inspection-orders/<int:order_id>/status`
- `GET,POST,PUT` `/admin-api/inspection-orders/<int:order_id>`
- `GET` `/admin-api/inspection-orders`
- `POST` `/admin-api/inspection-orders/<int:order_id>/logistics`
- `POST` `/admin-api/inspection-orders/<int:order_id>/payment`
- `POST` `/admin-api/inspection-orders/<int:order_id>/publish-verified`
- `POST` `/admin-api/inspection-orders/<int:order_id>/received`
- `POST` `/admin-api/inspection-orders/batch-update`
- `PUT` `/admin-api/inspection-orders/<int:order_id>/price`

### `menus`
- `GET` `/admin-api/menus`

### `messages`
- `DELETE,GET` `/admin-api/messages/<int:mid>`
- `DELETE,GET` `/admin-api/messages`

### `payment`
- `GET,POST` `/admin-api/payment/order/<int:order_id>/settlement/<str:action>`
- `GET,POST` `/admin-api/payment/order/<int:order_id>/settlement`
- `GET` `/admin-api/payment/orders/<int:order_id>`
- `GET` `/admin-api/payment/orders`
- `GET` `/admin-api/payment/settlements/summary`
- `POST` `/admin-api/payment/order/<int:order_id>/<str:action>`

### `permissions`
- `GET` `/admin-api/permissions`

### `products`
- `DELETE,GET,POST` `/admin-api/products/<int:pid>/<str:action>`
- `DELETE,GET,POST` `/admin-api/products/<int:pid>`
- `DELETE,GET,POST` `/admin-api/products`

### `recycle-orders`
- `POST` `/admin-api/recycle-orders/<int:order_id>/create-verified-device/`

### `recycle-templates`
- `DELETE,GET,POST,PUT` `/admin-api/recycle-templates/<int:template_id>/questions/<int:question_id>/options/<int:option_id>`
- `DELETE,GET,POST,PUT` `/admin-api/recycle-templates/<int:template_id>/questions/<int:question_id>/options`
- `DELETE,GET,POST,PUT` `/admin-api/recycle-templates/<int:template_id>/questions/<int:question_id>`
- `DELETE,GET,POST,PUT` `/admin-api/recycle-templates/<int:template_id>/questions`
- `DELETE,GET,POST,PUT` `/admin-api/recycle-templates/<int:template_id>`
- `DELETE,GET,POST,PUT` `/admin-api/recycle-templates`
- `POST` `/admin-api/recycle-templates/import`

### `recycled-products`
- `GET,POST,PUT` `/admin-api/recycled-products/<int:item_id>/publish`
- `GET,POST,PUT` `/admin-api/recycled-products/<int:item_id>/stock`
- `GET,POST,PUT` `/admin-api/recycled-products`

### `roles`
- `GET,POST` `/admin-api/roles`

### `shops`
- `DELETE,GET,POST,PUT` `/admin-api/shops/<int:sid>`
- `DELETE,GET,POST,PUT` `/admin-api/shops`

### `statistics`
- `GET` `/admin-api/statistics`

### `uploads`
- `POST` `/admin-api/uploads/images/`
- `POST` `/admin-api/uploads/reports/`

### `users`
- `DELETE,GET,POST,PUT` `/admin-api/users/<int:uid>`
- `DELETE,GET,POST,PUT` `/admin-api/users`

### `verified-devices`
- `GET,PATCH` `/admin-api/verified-devices/<int:pk>/`
- `GET,POST` `/admin-api/verified-devices/`
- `POST` `/admin-api/verified-devices/<int:pk>/<str:action>/`
- `POST` `/admin-api/verified-devices/<int:pk>/list-product/`

### `verified-listings`
- `GET,POST` `/admin-api/verified-listings/<int:item_id>/<str:action>`
- `GET,POST` `/admin-api/verified-listings/<int:item_id>`
- `GET,POST` `/admin-api/verified-listings/`
- `GET,POST` `/admin-api/verified-listings`
- `GET,PUT` `/admin-api/verified-listings/<int:pk>/`
- `POST` `/admin-api/verified-listings/<int:pk>/publish/`
- `POST` `/admin-api/verified-listings/<int:pk>/unpublish/`

### `verified-orders`
- `GET,POST` `/admin-api/verified-orders/<int:oid>/<str:action>`
- `GET,POST` `/admin-api/verified-orders/<int:oid>`
- `GET,POST` `/admin-api/verified-orders`

## WebSocket
- `GET` `/ws/chat/?token=<jwt>`
