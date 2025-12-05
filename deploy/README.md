# 部署文件说明

本目录包含云服务器部署所需的配置文件和脚本。

## 📁 目录结构

```
deploy/
├── README.md                    # 本文件
├── nginx.conf.example          # Nginx 配置模板
├── scripts/                     # 部署脚本
│   ├── deploy.sh               # 一键部署脚本
│   └── backup.sh               # 备份脚本
└── systemd/                    # Systemd 服务文件
    └── secondhand-backend.service.example  # 后端服务配置
```

## 🚀 快速开始

### 1. 部署后端服务

```bash
# 复制 systemd 服务文件
sudo cp deploy/systemd/secondhand-backend.service.example /etc/systemd/system/secondhand-backend.service

# 编辑配置文件，修改用户名和路径
sudo vim /etc/systemd/system/secondhand-backend.service

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable secondhand-backend
sudo systemctl start secondhand-backend
```

### 2. 配置 Nginx

```bash
# 复制 Nginx 配置
sudo cp deploy/nginx.conf.example /etc/nginx/sites-available/secondhand

# 编辑配置，修改域名和路径
sudo vim /etc/nginx/sites-available/secondhand

# 启用配置
sudo ln -s /etc/nginx/sites-available/secondhand /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 3. 使用部署脚本

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/deploy.sh
chmod +x deploy/scripts/backup.sh

# 运行部署脚本
bash deploy/scripts/deploy.sh
```

### 4. 配置自动备份

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天凌晨2点备份）
0 2 * * * /var/www/secondhand/deploy/scripts/backup.sh >> /var/www/secondhand/backups/backup.log 2>&1
```

## 📝 配置文件说明

### Nginx 配置

`nginx.conf.example` 包含完整的 Nginx 配置：
- HTTP 和 HTTPS 支持
- 前端静态文件服务
- 后端 API 反向代理
- WebSocket 支持
- 静态文件和媒体文件配置

**使用方法**：
1. 复制文件到 `/etc/nginx/sites-available/secondhand`
2. 修改域名、路径等配置
3. 创建符号链接到 `sites-enabled`
4. 测试并重启 Nginx

### Systemd 服务配置

`secondhand-backend.service.example` 是后端服务的 systemd 配置：
- 使用 Daphne（支持 WebSocket）
- 自动重启
- 开机自启

**使用方法**：
1. 复制到 `/etc/systemd/system/secondhand-backend.service`
2. 修改用户、工作目录等配置
3. 重新加载 systemd 并启动服务

### 部署脚本

`deploy.sh` 一键部署脚本，自动执行：
1. 检查项目目录
2. 创建/激活虚拟环境
3. 安装依赖
4. 执行数据库迁移
5. 收集静态文件
6. 构建前端项目
7. 设置文件权限

### 备份脚本

`backup.sh` 自动备份脚本，备份：
1. 数据库（MySQL dump）
2. 媒体文件（上传的图片等）
3. 配置文件

自动清理7天前的旧备份。

## 🔧 配置要点

### 环境变量

创建 `backend/.env` 文件：

```env
DJANGO_SETTINGS_MODULE=core.settings_production
SECRET_KEY=你的密钥
DB_NAME=secondhand_platform
DB_USER=dbuser
DB_PASSWORD=数据库密码
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 前端环境变量

创建 `frontend/.env.production` 文件：

```env
VITE_API_URL=https://你的域名/api
```

### 文件权限

确保以下目录权限正确：

```bash
sudo chown -R www-data:www-data /var/www/secondhand/backend/static
sudo chown -R www-data:www-data /var/www/secondhand/backend/media
sudo chown -R www-data:www-data /var/www/secondhand/frontend/dist
```

## 📚 详细文档

更多部署细节请参考：
- 主文档：`云服务器部署完整指南.md`
- 快速指南：`快速部署指南.md`
- 本地部署：`本地部署外网访问指南.md`

## ⚠️ 注意事项

1. **安全性**：
   - 修改默认密码
   - 配置防火墙
   - 使用 HTTPS
   - 定期更新系统

2. **性能**：
   - 根据服务器配置调整 worker 数量
   - 配置数据库连接池
   - 启用静态文件缓存

3. **备份**：
   - 定期备份数据库和文件
   - 测试备份恢复流程
   - 保留多个备份版本

4. **监控**：
   - 监控服务器资源使用
   - 查看应用日志
   - 设置告警通知

## 🆘 问题排查

遇到问题？查看：
- `云服务器部署完整指南.md` 中的"常见问题"章节
- 服务日志：`sudo journalctl -u secondhand-backend -f`
- Nginx 日志：`/var/log/nginx/secondhand_error.log`
- Django 日志：`/var/www/secondhand/backend/logs/django.log`




