#!/bin/bash
# 数据库和文件备份脚本
# 使用方法: bash backup.sh
# 建议添加到 crontab: 0 2 * * * /var/www/secondhand/deploy/scripts/backup.sh

set -e

# 配置变量
BACKUP_DIR="/var/www/secondhand/backups"
PROJECT_DIR="/var/www/secondhand"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7  # 保留7天的备份

# 从环境变量或配置文件读取数据库密码
# 建议在 .env 文件中配置
DB_USER="${DB_USER:-dbuser}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-secondhand_platform}"

echo "=========================================="
echo "开始备份"
echo "日期: $(date)"
echo "=========================================="

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库
echo "[1/3] 备份数据库..."
if [ -z "$DB_PASSWORD" ]; then
    mysqldump -u "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/db_$DATE.sql"
else
    mysqldump -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" > "$BACKUP_DIR/db_$DATE.sql"
fi

# 压缩数据库备份
gzip "$BACKUP_DIR/db_$DATE.sql"
echo "✓ 数据库备份完成: db_$DATE.sql.gz"

# 备份媒体文件
echo "[2/3] 备份媒体文件..."
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" -C "$PROJECT_DIR/backend" media
echo "✓ 媒体文件备份完成: media_$DATE.tar.gz"

# 备份配置文件
echo "[3/3] 备份配置文件..."
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    -C "$PROJECT_DIR/backend" \
    core/settings_production.py \
    .env 2>/dev/null || true
echo "✓ 配置文件备份完成: config_$DATE.tar.gz"

# 删除旧备份
echo "清理 $KEEP_DAYS 天前的备份..."
find "$BACKUP_DIR" -name "*.gz" -type f -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$KEEP_DAYS -delete

echo ""
echo "=========================================="
echo "备份完成！"
echo "备份目录: $BACKUP_DIR"
echo "=========================================="
echo ""
ls -lh "$BACKUP_DIR"




