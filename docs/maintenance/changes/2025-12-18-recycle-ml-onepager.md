# 2025-12-18 - 回收主线 ML 一页方案 + 流程文档对齐

## 变更内容

- 新增回收主线机器学习方案一页说明：`docs/00-overview/recycle-ml-mainline-onepager.md`
- 对齐回收流程文档与代码实现：`docs/40-dev-guide/recycle-order-complete-workflow.md`
  - 明确“打款完成”以 `payment_status=paid` 表示，订单 `status` 仍为 `completed`
  - 修正管理员确认收货接口路径为 `POST /admin-api/inspection-orders/{id}/received`
- 统一回收订单状态展示：`backend/app/secondhand_app/models.py` 将 `pending` 的中文显示更新为“待寄出”

## 验证方式

- 打开 `docs/00-overview/recycle-ml-mainline-onepager.md`，检查是否包含：流程核对、ML任务、特征工程、无历史数据的冷启动、落地路径。
- 打开 `docs/40-dev-guide/recycle-order-complete-workflow.md`，检查状态机图不再出现 `paid` 作为订单状态，并已标注 `payment_status=paid`。
- 在管理端任意回收订单详情页检查 `pending` 状态的中文显示为“待寄出”（如页面使用 `get_status_display()`）。

