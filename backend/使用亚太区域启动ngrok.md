# 使用亚太区域启动 Ngrok（中国用户）

## 问题

ngrok 配置文件不支持在 YAML 中直接设置 `region` 字段，需要使用命令行参数。

## 解决方案

已修复配置文件，移除了不支持的 `region` 字段。现在需要使用命令行参数 `--region ap` 来指定区域。

## 启动方法

### 方法 1：使用启动脚本（推荐）

已更新启动脚本，会自动添加 `--region ap` 参数：

```powershell
# 启动后端
.\start_ngrok_backend.ps1

# 启动前端
.\start_ngrok_frontend.ps1
```

### 方法 2：手动使用命令行参数

```powershell
# 后端（亚太区域）
ngrok start --config ngrok-backend.yml --region ap backend

# 前端（亚太区域）
ngrok start --config ngrok-frontend.yml --region ap frontend
```

### 方法 3：直接启动（不使用配置文件）

```powershell
# 后端
ngrok http 8000 --region ap

# 前端
ngrok http 5173 --region ap
```

## 已修复的配置文件

### `ngrok-backend.yml`
```yaml
version: 3
agent:
  authtoken: 36TUDwWpJTqmuqX6TwUidfFZ8aL_3hNcLMa3t4T4dJgbrtcDq
tunnels:
  backend:
    addr: 8000
    proto: http
```

### `ngrok-frontend.yml`
```yaml
version: 3
agent:
  authtoken: 36WAP5OoDEykLUcZ4ENBqx9XHos_3gEc2P4eXSSSP9RYMEhB2
tunnels:
  frontend:
    addr: 5173
    proto: http
```

## 验证区域

启动后，在 ngrok 输出中应该能看到：

```
Region: Asia Pacific (ap)
```

或者在 ngrok Web 界面（`http://127.0.0.1:4040`）中查看区域信息。

## 支持的区域

- `us` - 美国
- `eu` - 欧洲
- `ap` - 亚太地区（**推荐中国用户使用**）
- `au` - 澳大利亚
- `sa` - 南美
- `in` - 印度
- `jp` - 日本

## 快速启动命令

```powershell
# 终端 1 - 后端（亚太区域）
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-backend.yml --region ap backend

# 终端 2 - 前端（亚太区域）
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-frontend.yml --region ap frontend
```

## 注意事项

1. **必须使用命令行参数**：`region` 不能在配置文件中设置
2. **每次启动都需要指定**：如果不指定，会使用默认区域（可能是 `jp`）
3. **使用启动脚本**：已更新的脚本会自动添加 `--region ap` 参数

现在可以正常启动 ngrok 了！




