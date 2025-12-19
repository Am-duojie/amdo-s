# 2025-12-18 - 回收问卷：功能性问题（公共模板）

## 变更内容

- 将问卷最后一步统一为“功能性问题（非必选，可多选）”
  - 新增“全部正常”选项（与其它异常项互斥）。
  - 移除“无法连接电脑”等不需要项。
- 作为公共默认模板应用到所有机型：
  - 默认问卷来源更新：`backend/app/admin_api/management/commands/import_recycle_templates.py`
  - 提供同步命令：`python backend/manage.py sync_recycle_functional_question`
- 前端交互优化：
  - 在多选时选择“全部正常”会清空其它选项；选择其它选项会移除“全部正常”。

## 相关文件

- `backend/app/admin_api/management/commands/import_recycle_templates.py`
- `backend/app/admin_api/management/commands/sync_recycle_functional_question.py`
- `backend/app/secondhand_app/management/commands/seed_recycle_orders.py`
- `frontend/src/pages/RecycleEstimateWizard.vue`

## 验证方式

- 同步模板：
  - `python backend/manage.py sync_recycle_functional_question --dry-run`
  - `python backend/manage.py sync_recycle_functional_question`
- 打开回收估价问卷，进入最后一步，确认选项与交互符合预期。

