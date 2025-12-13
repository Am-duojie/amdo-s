# 系统架构与模块划分

## 总体架构
- 前端：Vue3 + Element Plus（用户端与管理端共用一个前端工程，路由区分）
- 后端：Django + DRF（REST API），Channels（WebSocket 聊天）
- 数据：MySQL
- 第三方：支付宝（支付/回调/查询），ngrok 用于回调调试（开发环境）

## 后端模块（以代码路径为准）
- 路由聚合：`backend/core/urls.py`
- 用户端业务：`backend/app/secondhand_app/`
- 管理端业务：`backend/app/admin_api/`
- WebSocket：`backend/app/consumers.py`、`backend/app/routing.py`
- 支付：`backend/app/secondhand_app/payment_views.py`

## 前端模块（以代码路径为准）
- 用户端页面：`frontend/src/pages/`
- 管理端页面：`frontend/src/admin/pages/`
- API：`frontend/src/api/`
- 路由：`frontend/src/router/index.js`
- 状态：`frontend/src/stores/`

## 关键设计点
- HTTP 认证：JWT
- WebSocket：querystring token（存在泄露风险，建议说明改进：Header/子协议）
- 支付：回调验签 + 幂等 + 状态一致性（建议在测试/运维章节说明）
- 回收：流程状态与打款状态分离，便于运营与审计
