# 2025-12-18 - 清空回收/官方验订单与商品数据（重置数据集）

## 变更内容

- 新增管理命令：`backend/app/secondhand_app/management/commands/reset_recycle_official_data.py`
  - 用于一次性清空“回收订单 + 官方验商品/订单 + 相关审核/质检数据”。
  - 支持 `--dry-run` 预览删除数量，避免误删。
  - 可选：清空并从 JSON 重新导入机型模板（配套补默认问卷）。
  - 可选：清空后重新造数（回收订单）。

## 使用方式

- 仅预览（不删除）：
  - `python backend/manage.py reset_recycle_official_data --dry-run`
- 确认清空并从 JSON 重导机型模板：
  - `python backend/manage.py reset_recycle_official_data --yes --templates-file backend/data/recycle_templates_user.json`
- 清空后重新造数（示例：2000 条 / 60 天）：
  - `python backend/manage.py reset_recycle_official_data --yes --templates-file backend/data/recycle_templates_user.json --seed-recycle-count 2000 --seed-days 60 --seed-tag FAKE_RECYCLE`

