# Vite 配置 ngrok 访问说明

## 问题

当通过 ngrok 访问前端时，Vite 会检查 Host 头，如果 Host 不在允许列表中，会显示错误：

```
请求被阻止。此主机（"xxx.ngrok-free.dev"）未被允许。
```

## 解决方案

已在 `vite.config.js` 中添加 `allowedHosts` 配置，允许以下域名访问：

- `localhost` - 本地访问
- `.ngrok-free.dev` - ngrok 免费版域名
- `.ngrok.io` - ngrok 旧版域名
- `.ngrok.app` - ngrok 新版域名

## 配置说明

```javascript
server: {
  host: '0.0.0.0',
  port: 5173,
  allowedHosts: [
    'localhost',
    '.ngrok-free.dev',
    '.ngrok.io',
    '.ngrok.app'
  ],
  // ...
}
```

**注意**：使用通配符（如 `.ngrok-free.dev`）可以匹配所有 ngrok 子域名，这样即使 ngrok 地址变化也不需要修改配置。

## 重启前端服务

修改配置后，需要重启前端开发服务器：

1. 停止当前前端服务（在运行 `npm run dev` 的终端按 `Ctrl+C`）
2. 重新启动：
   ```powershell
   npm run dev
   ```

## 验证

重启后，通过 ngrok 地址访问前端应该可以正常工作：

```
https://您的-前端-ngrok-地址.ngrok-free.dev
```

## 安全说明

`allowedHosts` 配置仅在开发环境中使用。生产环境构建后（`npm run build`），这个配置不会影响生产构建。

## 如果仍然遇到问题

1. **确认配置已保存**：检查 `vite.config.js` 文件
2. **确认已重启**：完全停止并重新启动前端服务
3. **检查 ngrok 地址**：确认访问的地址确实是 ngrok 地址
4. **查看 Vite 日志**：在终端中查看是否有其他错误信息




