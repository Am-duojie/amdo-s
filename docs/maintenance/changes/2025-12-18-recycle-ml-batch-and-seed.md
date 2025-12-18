# 2025-12-18 - 回收拟真造数 + 批量智能分析（分布/TopN/分页）

## 变更内容

### 1) 拟真数据生成（用于无历史数据的演示/分析）

- 新增管理命令：`backend/app/secondhand_app/management/commands/seed_recycle_orders.py`
  - 生成回收订单 `RecycleOrder`（含问卷答案、状态流转时间、预估价/最终价、异议/取消、打款状态等）
  - 生成质检报告 `AdminInspectionReport`（66项 check_items，pass/fail 分布与问卷严重度相关）
  - 写入 `note` 标记（默认 `FAKE_RECYCLE`），便于回滚删除
  - 自动修正时间字段：为 BI 趋势分析生成合理的 `created_at/updated_at`（避免 auto_now(_add) 导致时间集中在导入时刻）

### 2) 批量在线推理接口（后端）

- 新增接口：
  - `GET /admin-api/recycle-ml/batch`：分页返回订单 + 在线推理结果（含 `gap_ratio`）
  - `GET /admin-api/recycle-ml/summary`：聚合统计（状态分布、风险分布、偏离分布、TopN）

### 3) 数据看板批量分析页（前端）

- `数据看板 > 智能分析` 增加“批量分析”Tab：
  - 风险分布图（异议风险）
  - 偏离分布图（|建议-预估|/预估）
  - 高风险 Top10、品牌 Top10
  - 分页列表（可按日期/状态过滤）

相关文件：
- `frontend/src/admin/pages/IntelligentAnalysis.vue`
- `backend/app/admin_api/views.py`
- `backend/app/admin_api/urls.py`

## 验证方式

### 造数

在已完成迁移并可连接数据库的环境中执行：

- 生成 2000 条（过去60天，自动补模板）：  
  `python backend/manage.py seed_recycle_orders --count 2000 --days 60 --ensure-templates`
- 删除造数（按 tag 回滚）：  
  `python backend/manage.py seed_recycle_orders --delete-by-tag --tag FAKE_RECYCLE`
- 仅重置时间分布（不重新造数）：  
  `python backend/manage.py seed_recycle_orders --retime-by-tag --tag FAKE_RECYCLE --days 60`

### 分析页

- 登录管理端，进入：`数据看板 > 智能分析`
  - “批量分析”Tab：应能看到分布图/TopN/分页列表
  - “单条分析”Tab：仍可按订单 ID 查询并手动“重新计算”
