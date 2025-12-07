# 启动 Ngrok 正确方法

## 问题

如果出现错误：
```
ERROR: Error reading configuration file 'ngrok-backend.yml': open C:\Users\an344\ngrok-backend.yml: The system cannot find the file specified.
```

说明 ngrok 在错误的目录查找配置文件。

## 解决方案

### 方法 1：切换到项目目录再启动（推荐）

```powershell
# 切换到 backend 目录
cd D:\AAA\毕业设计\backend

# 启动后端 ngrok
ngrok start --config ngrok-backend.yml backend

# 启动前端 ngrok（在另一个终端）
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-frontend.yml frontend
```

### 方法 2：使用完整路径

```powershell
# 启动后端
ngrok start --config "D:\AAA\毕业设计\backend\ngrok-backend.yml" backend

# 启动前端
ngrok start --config "D:\AAA\毕业设计\backend\ngrok-frontend.yml" frontend
```

### 方法 3：使用相对路径（如果当前在 backend 目录）

```powershell
# 确保当前目录是 backend
cd D:\AAA\毕业设计\backend

# 使用相对路径
ngrok start --config .\ngrok-backend.yml backend
ngrok start --config .\ngrok-frontend.yml frontend
```

## 完整启动流程

### 终端 1 - Django 后端
```powershell
cd D:\AAA\毕业设计\backend
python manage.py runserver
```

### 终端 2 - 前端服务
```powershell
cd D:\AAA\毕业设计\frontend
npm run dev
```

### 终端 3 - 后端 ngrok
```powershell
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-backend.yml backend
```

### 终端 4 - 前端 ngrok
```powershell
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-frontend.yml frontend
```

## 验证配置文件位置

运行以下命令确认配置文件存在：

```powershell
cd D:\AAA\毕业设计\backend
Get-ChildItem ngrok-*.yml
```

应该看到：
- `ngrok-backend.yml`
- `ngrok-frontend.yml`

## 快速启动脚本

也可以使用我创建的 PowerShell 脚本：

```powershell
cd D:\AAA\毕业设计\backend
.\start_ngrok_backend.ps1
.\start_ngrok_frontend.ps1
```

这些脚本会自动切换到正确的目录。


