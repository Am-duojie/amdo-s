## 聊天功能设计与实现（当前状态）

### 目标
- WebSocket 实时消息收发，单实例、自动重连。
- 当前会话内自动已读：只要在聊天页、页面可见且 WS 已连，收到消息立即标记已读并清零未读。
- 未读角标同步：通过 `refresh-unread` 事件或单次拉取 `/messages/conversations/` 更新，无持续轮询。

### 前端实现
#### 1) WebSocket（`src/utils/websocket.js`）
- 单例服务，地址由 `VITE_WS_BASE` 配置。
- 自动重连、自检；connected/disconnected/message/error 事件可订阅。

#### 2) 聊天页（`src/pages/Messages.vue`）
- 状态：`isPageVisible`、`wsConnected`、`isOnMessagesPage`。
- 收到 `new_message`：
  - 若当前会话、我是接收方、WS 已连、页面可见：调用 `markAsRead`，本地设已读、清零未读。
  - 其他：接收方不满足条件则累加未读；发送方仅清零对方未读。
- 收到 `read_ack`：
  - 将我发给对方的消息设为已读，清零对应会话未读，刷新对话列表并触发 `refresh-unread`。
- `markAsRead(peerId)`：
  - 调用 `/messages/read/`，本地设已读、清零未读，触发 `refresh-unread`。
- 进入对话 `handleSelectUser`：
  - 选中用户，清零未读，标记本地已读，调用 `/messages/read/`，触发 `refresh-unread`。
- 放宽自动已读：不再要求窗口聚焦，只要页面可见、当前对话即可自动已读。

#### 3) 未读角标（`src/components/SidebarQuickActions.vue`）
- `loadUnread`：单次 GET `/messages/conversations/`，初始化或收到 `refresh-unread` 时刷新，不循环轮询。
- 无 token 不请求。

### 后端要点
- Django + Channels，`/ws/chat/` 基于 token 鉴权。
- 消息模型：`message_type/payload/recalled/recallable_until/is_read` 等。
- `/messages/read/`：标记对端消息为已读，并通过 WS 推送 `read_ack`。
- `/messages/conversations/`：返回各会话 `unread_count`，供角标刷新。

### 当前行为
- 聊天页可见时，收到消息自动已读、未读清零，对方收到 `read_ack` 后气泡即时已读。
- 非当前页/不可见时仅累加未读，进入对话后再标记已读。
- 未读角标通过事件或单次拉取刷新，无持续轮询。

### 可选后续
- 增加“正在输入”“送达”状态。
- 对未读刷新可加防抖/节流或合并多个 `refresh-unread`。
- 生产环境使用 wss 并确保同源配置。








