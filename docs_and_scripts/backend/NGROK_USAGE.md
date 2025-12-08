# ngrok 当前使用说明

本文件替代此前所有重复的 ngrok 相关文档，保持与现有代码配置一致。

## 当前配置快照
- 配置文件：`backend/ngrok.yml`（同时定义 8000 后端和 5173 前端隧道）
- 后端地址：`BACKEND_URL = https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev`（见 `backend/core/settings.py`）
- 前端地址：`FRONTEND_URL = http://localhost:5173`（如需公网访问前端，再改为前端 ngrok 地址）

> 免费版 ngrok 地址会变动，变动后只需按下述步骤更新即可，无需再创建额外文档。

## 启动流程
1. 后端服务  
   ```powershell
   cd backend
   # 如需虚拟环境：.\venv\Scripts\activate
   python manage.py runserver 0.0.0.0:8000
   ```
2. 开启 ngrok 隧道  
   ```powershell
   # 同时映射后端(8000)和前端(5173)
   ngrok start --all --config ngrok.yml
   # 仅后端时可用
   # ngrok start backend --config ngrok.yml
   ```
   记录 ngrok 输出中的 HTTPS 地址，后续写入配置。
3. 前端开发服 务  
   ```powershell
   cd frontend
   npm run dev
   ```

## 地址变更时的更新
1. 在 `backend/core/settings.py` 中同步新的地址：
   ```python
   FRONTEND_URL = 'http://localhost:5173'  # 如前端也走 ngrok，则改为新的前端 https 地址
   BACKEND_URL = 'https://<新的后端 ngrok 域名>'
   ```
2. 在前端根目录创建/更新 `.env`（推荐持久化）：  
   ```env
   VITE_BACKEND_NGROK_URL=https://<新的后端 ngrok 域名>
   # 如管理后台也需外网访问，可同步指定
   VITE_ADMIN_API_URL=https://<新的后端 ngrok 域名>/admin-api
   ```
   保存后重启前端 `npm run dev`。临时方案仍可在浏览器控制台设置：
   ```javascript
   localStorage.setItem('BACKEND_NGROK_URL', 'https://<新的后端 ngrok 域名>')
   location.reload()
   ```

## 验证清单
- 访问 `<后端地址>/api/` 返回 Django API 列表即可。
- 前端页面能正常拉取数据；若报错，检查 `.env` 中的 `VITE_BACKEND_NGROK_URL`。
- 支付回调：回调地址自动拼成 `<后端地址>/api/payment/alipay/notify/`，确保 ngrok 仍在线。

## 其他注意
- WebSocket 目前写死为 `ws://127.0.0.1:8000/ws/chat/?token=...`（`frontend/src/utils/websocket.js`），如需公网聊天，需同步改为基于 `BACKEND_URL` 的 `wss://` 地址。
- 免费版隧道会过期或切换域名，请在每次重启 ngrok 后按“地址变更”步骤更新配置。


