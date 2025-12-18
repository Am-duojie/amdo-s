# 2025-12-18 - 回收机型模板（JSON 导入）

## 变更内容

- 新增/完善 JSON 导入命令：`backend/app/admin_api/management/commands/import_recycle_templates_json.py`
  - 支持 `--dry-run` 校验、`--ensure-questions` 自动补默认问卷。
- 增加示例数据文件：`backend/data/recycle_templates_user.json`
  - 用于演示“机型模板”数据结构与批量导入流程（价格/参数可能为示例或中位数口径，答辩时建议说明来源与口径）。

## 使用方式

- 先校验（不写库）：
  - `python backend/manage.py import_recycle_templates_json --file backend/data/recycle_templates_user.json --dry-run`
- 正式导入并补齐默认问卷：
  - `python backend/manage.py import_recycle_templates_json --file backend/data/recycle_templates_user.json --ensure-questions`

## 验证方式

- 进入管理端“回收模板/机型模板”相关页面，确认新增机型可检索/可用于问卷。
- 或在后端 shell 中查看数量：
  - `python backend/manage.py shell -c "from app.admin_api.models import RecycleDeviceTemplate; print(RecycleDeviceTemplate.objects.count())"`

