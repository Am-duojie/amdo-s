# 本地运行手册（开发者）

## 前端（Vue3 + Vite）
1. 安装依赖：`npm i`
2. 配置：`frontend/.env.example`
```dotenv
VITE_ADMIN_API_URL=http://127.0.0.1:8000/admin-api
VITE_API_URL=http://127.0.0.1:8000/api
VITE_API_DEBUG=false
```
3. 启动：`npm run dev`

## 后端（Django）
1. 创建虚拟环境并安装依赖：`pip install -r requirements.txt`
2. 迁移：`python manage.py migrate`
3. 启动：`python manage.py runserver`
4. WebSocket：按 ASGI 运行方式部署（见 `backend/core/asgi.py`）

## 内网穿透（支付回调调试）
仓库中包含 ngrok 配置（`backend/ngrok-*.yml`），建议仅用于开发环境。

## 重要：敏感配置管理（必须）
`backend/core/settings.py` 存在敏感配置硬编码风险（数据库口令/支付密钥等）。
建议立刻迁移到环境变量读取，并在仓库中只保留 `.env.example` 的“变量名 + 示例值”。

建议环境变量清单（示例）：
- `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD`
- `ALIPAY_APP_ID` / `ALIPAY_PRIVATE_KEY` / `ALIPAY_PUBLIC_KEY` / `ALIPAY_NOTIFY_URL` / `ALIPAY_RETURN_URL`
