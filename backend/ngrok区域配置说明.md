# Ngrok 区域配置说明

## 中国用户区域选择

ngrok 官方**没有专门的中国区域**，但可以使用**亚太区域（ap）**，这对中国用户来说是最接近的选择。

## 已更新的配置

已将所有配置文件更新为使用 `ap`（亚太）区域：

### 后端配置 (`ngrok-backend.yml`)
```yaml
version: 3
agent:
  authtoken: 36TUDwWpJTqmuqX6TwUidfFZ8aL_3hNcLMa3t4T4dJgbrtcDq
  region: ap  # 亚太区域（适合中国用户）
tunnels:
  backend:
    addr: 8000
    proto: http
```

### 前端配置 (`ngrok-frontend.yml`)
```yaml
version: 3
agent:
  authtoken: 36WAP5OoDEykLUcZ4ENBqx9XHos_3gEc2P4eXSSSP9RYMEhB2
  region: ap  # 亚太区域（适合中国用户）
tunnels:
  frontend:
    addr: 5173
    proto: http
```

## Ngrok 支持的区域

- `us` - 美国
- `eu` - 欧洲
- `ap` - 亚太地区（**推荐中国用户使用**）
- `au` - 澳大利亚
- `sa` - 南美
- `in` - 印度
- `jp` - 日本

## 配置位置

`region` 字段应该放在 `agent` 级别，而不是 `tunnels` 级别：

```yaml
version: 3
agent:
  authtoken: YOUR_AUTHTOKEN
  region: ap  # 在这里配置区域
tunnels:
  # ...
```

## 使用效果

使用 `ap` 区域后：
- **延迟更低**：对于中国用户，连接到亚太服务器延迟更低
- **速度更快**：数据传输速度更快
- **稳定性更好**：网络连接更稳定

## 验证区域

启动 ngrok 后，在输出中可以看到区域信息：

```
Region: Asia Pacific (ap)
```

或者在 ngrok Web 界面（`http://127.0.0.1:4040`）中查看。

## 如果配置不生效

如果配置文件中的 `region` 字段不生效，可以在启动时使用命令行参数：

```powershell
# 后端
ngrok http 8000 --region ap

# 前端
ngrok http 5173 --region ap
```

或者使用配置文件并添加参数：

```powershell
ngrok start --config ngrok-backend.yml --region ap backend
```

## 国内替代方案

如果 ngrok 的亚太区域仍然不够快，可以考虑：

1. **国内 ngrok 服务商**：
   - Sunny-Ngrok: https://www.ngrok.cc
   - ITTUN: https://www.ittun.com

2. **自建 ngrok 服务器**：
   - 在中国境内部署自己的 ngrok 服务器
   - 完全控制，速度最快

## 当前配置状态

- ✅ `ngrok-backend.yml` - 已设置为 `ap` 区域
- ✅ `ngrok-frontend.yml` - 已设置为 `ap` 区域
- ✅ `ngrok.yml` - 已设置为 `ap` 区域

重启 ngrok 后，区域配置会生效。




