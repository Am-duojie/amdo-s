# 2025-12-18 - 回收在线推理（建议价/风险）接入管理端

## 变更内容

- 后端新增回收在线推理模块（无第三方依赖）：`backend/app/secondhand_app/ml/recycle_online_inference.py`
  - 输出：建议回收价、建议区间、异议风险、取消风险、关键影响因素、模型版本
- 管理端接口支持“随时分析”
  - 新增预测接口：`GET /admin-api/recycle-ml/predict?order_id={id}`
  - 回收订单详情接口增加 `ml` 字段：`GET /admin-api/inspection-orders/{id}`
- 管理端页面展示预测结果（回收订单详情页）
  - `frontend/src/admin/pages/InspectionOrderDetail.vue`
  - `frontend/src/admin/pages/components/RecycleOrderDetail.vue`
- 数据看板增加入口（便于随时查看/演示）
  - 管理端菜单：数据看板 > 智能分析
  - 页面路由：`/admin/intelligent-analysis`（`frontend/src/router/index.js`）

## 说明

- 在线推理仅用于“决策辅助”，不会自动改价/自动打款；模型不可用时不影响原有流程（前端不展示或后端返回空）。
- 当前为无历史数据的 baseline 模型（线性回归/逻辑回归形式的权重基线），后续可用 `final_price`、`price_dispute`、`cancelled` 等真实标签离线训练更新权重。

## 验证方式

- 打开任意回收订单详情（管理端）：应出现“智能分析（在线推理）”区块，展示建议回收价/风险/关键因素。
- 直接请求预测接口：`GET /admin-api/recycle-ml/predict?order_id=1`（替换为存在的订单 ID），应返回 `ml.suggested_final_price`、`ml.risk_dispute` 等字段。
