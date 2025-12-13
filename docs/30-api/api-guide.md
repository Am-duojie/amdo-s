# API 使用说明

## 基础信息
- 用户端 API 前缀：`/api/`
- 管理端 API 前缀：`/admin-api/`
- 支付端点：`/api/payment/*`
- WebSocket：`/ws/chat/`

## 认证
- 用户端 HTTP：JWT（SimpleJWT）
- 管理端：独立登录体系（见 `/admin-api/auth/*`）

## WebSocket（聊天）
- 连接：`/ws/chat/?token=<jwt>`
- 发送消息（示例）：
```json
{
  "type": "chat_message",
  "receiver_id": 123,
  "product_id": 456,
  "message_type": "text",
  "content": "你好，这个还能便宜吗？",
  "payload": {}
}
```

## 支付（支付宝）
- `POST /api/payment/create/`：创建支付（body：order_id；可选 order_type=normal|verified）
- `POST /api/payment/create-url/`：创建支付 URL（如实现）
- `GET /api/payment/query/<order_id>/?order_type=normal|verified`：查询
- `GET /api/payment/redirect/`：跳转页
- `POST /api/payment/alipay/notify/`：回调通知（需验签与幂等）
