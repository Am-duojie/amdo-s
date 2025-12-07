# 支付回调问题调试指南

## 问题：支付成功后没有反应

### 调试步骤

#### 1. 检查后端日志

支付成功后，查看后端日志，应该能看到以下信息：

```
========== 支付回调重定向页面 ==========
请求方法: GET
所有参数: {...}
支付宝返回参数: {...}
支付状态查询结果: status=success, message=支付成功！
```

**如果没有看到这些日志：**
- 支付宝可能没有跳转到回调地址
- 检查 `return_url` 配置是否正确

#### 2. 检查支付回调URL

在创建支付时，后端会记录使用的 `return_url`：
```
使用后端重定向页面（推荐，更稳定）: https://xxx.ngrok-free.dev/api/payment/redirect?order_id=xxx&order_type=normal
```

**确认：**
- 后端 ngrok 地址是否正确
- 支付宝沙箱环境能否访问该地址

#### 3. 手动测试回调地址

在浏览器中直接访问：
```
https://你的后端ngrok地址/api/payment/redirect?order_id=订单ID&order_type=normal
```

**应该看到：**
- 支付状态页面
- 自动跳转到本地前端（如果前端是 localhost）

#### 4. 检查前端服务

确保本地前端服务正在运行：
```bash
cd frontend
npm run dev
```

前端应该运行在：`http://localhost:5173`

#### 5. 检查浏览器控制台

打开浏览器开发者工具（F12），查看：
- Console 标签：是否有跳转相关的日志或错误
- Network 标签：是否有请求失败

#### 6. 常见问题

**问题1：支付宝没有跳转回来**
- 检查支付宝沙箱账号是否正常
- 检查支付是否真的成功（在支付宝沙箱中查看）

**问题2：后端页面显示但无法跳转到前端**
- 检查前端服务是否运行
- 检查浏览器是否阻止了跳转
- 手动点击"跳转到本地前端页面"按钮

**问题3：订单状态未更新**
- 检查异步通知是否到达（查看后端日志）
- 手动查询支付状态：`GET /api/payment/query/{order_id}/?order_type=normal`

### 测试命令

#### 查询支付状态
```bash
curl -X GET "http://127.0.0.1:8000/api/payment/query/订单ID/?order_type=normal" \
  -H "Authorization: Bearer 你的token"
```

#### 查看订单详情
```bash
curl -X GET "http://127.0.0.1:8000/api/orders/订单ID/" \
  -H "Authorization: Bearer 你的token"
```

### 日志位置

后端日志通常在：
- 控制台输出
- 如果配置了日志文件，查看 `debug.log`

### 联系支持

如果以上步骤都无法解决问题，请提供：
1. 后端日志（包含支付回调相关信息）
2. 浏览器控制台错误信息
3. 订单ID
4. 支付时间



