#!/bin/bash
# 一键部署脚本
# 使用方法: bash deploy.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "开始部署二手交易平台"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 配置变量（根据实际情况修改）
PROJECT_DIR="/var/www/secondhand"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

# 检查是否以 root 用户运行
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}请不要使用 root 用户运行此脚本${NC}"
   exit 1
fi

echo -e "${YELLOW}[1/8] 检查项目目录...${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}错误: 项目目录不存在: $PROJECT_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 项目目录存在${NC}"

echo -e "${YELLOW}[2/8] 检查后端虚拟环境...${NC}"
cd "$BACKEND_DIR"
if [ ! -d "$VENV_DIR" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
echo -e "${GREEN}✓ 虚拟环境就绪${NC}"

echo -e "${YELLOW}[3/8] 安装后端依赖...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ 后端依赖安装完成${NC}"

echo -e "${YELLOW}[4/8] 检查环境变量文件...${NC}"
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}警告: .env 文件不存在，请创建并配置环境变量${NC}"
    echo "创建示例文件..."
    cat > "$BACKEND_DIR/.env.example" << EOF
DJANGO_SETTINGS_MODULE=core.settings_production
SECRET_KEY=你的密钥
DB_NAME=secondhand_platform
DB_USER=dbuser
DB_PASSWORD=你的数据库密码
DB_HOST=127.0.0.1
DB_PORT=3306
EOF
    echo -e "${YELLOW}请复制 .env.example 为 .env 并填写配置${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 环境变量文件存在${NC}"

echo -e "${YELLOW}[5/8] 执行数据库迁移...${NC}"
export DJANGO_SETTINGS_MODULE=core.settings_production
python manage.py makemigrations
python manage.py migrate
echo -e "${GREEN}✓ 数据库迁移完成${NC}"

echo -e "${YELLOW}[6/8] 收集静态文件...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ 静态文件收集完成${NC}"

echo -e "${YELLOW}[7/8] 构建前端项目...${NC}"
cd "$FRONTEND_DIR"
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}警告: .env.production 不存在，创建示例文件${NC}"
    echo "VITE_API_URL=https://你的域名/api" > .env.production
fi
npm install
npm run build
echo -e "${GREEN}✓ 前端构建完成${NC}"

echo -e "${YELLOW}[8/8] 设置文件权限...${NC}"
sudo chown -R www-data:www-data "$BACKEND_DIR/static"
sudo chown -R www-data:www-data "$BACKEND_DIR/media"
sudo chown -R www-data:www-data "$FRONTEND_DIR/dist"
echo -e "${GREEN}✓ 文件权限设置完成${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "部署完成！"
echo "==========================================${NC}"
echo ""
echo "下一步操作："
echo "1. 重启后端服务: sudo systemctl restart secondhand-backend"
echo "2. 重启 Nginx: sudo systemctl restart nginx"
echo "3. 查看服务状态: sudo systemctl status secondhand-backend"
echo ""




