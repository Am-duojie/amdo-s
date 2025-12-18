# 回收主线：机器学习方案与落地一页说明

本页以“回收”为主线，基于当前项目已有数据结构（回收问卷模板、订单、质检报告、打款与异议字段），给出可用于答辩/演示的机器学习方向与工程落地路径。

## 1. 先确认：当前回收流程（以代码为准）

**核心状态（RecycleOrder.status）**：

`pending(待寄出) → shipped(已寄出) → received(已收货) → inspected(已检测) → completed(已完成) → cancelled(已取消)`

**资金状态（RecycleOrder.payment_status）**：

`pending(待打款) / paid(已打款) / failed(打款失败)`

**关键接口**（与流程节点对应）：

- 用户提交订单：`POST /api/recycle-orders/`（status=pending）
- 用户填写物流：`PATCH /api/recycle-orders/{id}/`（填写 carrier+tracking 后自动 pending→shipped）
- 管理员确认收货：`POST /admin-api/inspection-orders/{id}/received`（shipped→received）
- 管理员提交质检报告：`POST /admin-api/inspection-orders/{id}/report`（received/shipped→inspected，写入 AdminInspectionReport）
- 管理员设置最终价：`PUT /admin-api/inspection-orders/{id}/price`（更新 final_price/bonus，重置 final_price_confirmed=false）
- 用户确认最终价：`POST /api/recycle-orders/{id}/confirm_final_price/`（inspected→completed，final_price_confirmed=true）
- 管理员打款：`POST /admin-api/inspection-orders/{id}/payment`（payment_status=paid，status 仍为 completed）

> 文档对齐：`docs/40-dev-guide/recycle-order-complete-workflow.md` 已补充 “打款完成=payment_status=paid（status仍为completed）” 的说明，避免“paid是订单状态吗？”这类追问。

## 2. 回收主线最适合做的 3 个 ML 任务（论文/答辩友好）

1) **最终回收价预测（回归）**  
目标：在“用户问卷完成/或质检完成”时预测 `final_price`，给出“建议回收价区间”与“置信度/风险”。  
价值：减少人工定价波动，提高一致性；用于解释“为什么要调价”。

2) **价格异议/取消风险预测（分类）**  
目标：预测 `price_dispute`（价格异议）/ `cancelled`（取消）概率。  
价值：提前识别高风险订单，提示客服/运营介入；可在管理端做风控看板。

3) **质检结果与调价幅度预测（回归/分类）**  
目标：基于问卷与机型信息预测“质检后是否需要大幅调价（|final-estimated|阈值）”。  
价值：解释“估价与质检价差异”，提升估价可信度。

## 3. 特征工程：解决“不同品牌/机型问卷不一致”

你现在的问卷是 **模板驱动**（`RecycleDeviceTemplate` + `RecycleQuestionTemplate` + `RecycleQuestionOption`），选项带 `impact`（positive/minor/major/critical）。这对特征工程很友好：

- **通用结构化特征（跨机型稳定）**
  - 机型侧：device_type/brand/model/storage/condition、release_year（若有）
  - 问卷侧：impact 四档计数（如 `impact_critical_cnt`）、每一步是否缺失、回答数量
  - 质检侧：check_items 通过率（passed_cnt/failed_cnt）、overall_result、score（若有）
- **机型差异的处理**
  - 做“**两层模型**”：全局模型（学习通用规律）+ 机型/品牌分组校准（brand/model 的残差校正）
  - 或做“**模板ID embedding/one-hot**”：以 `template_id` 作为高层类别特征（低维处理即可）

这套表述在答辩时通常更容易被认可：既体现“数据科学的特征工程”，又解释了“问卷不一致”的工程解法。

## 4. 没有历史数据：怎么做训练数据（可落地/可答辩）

建议分三步，逐步替代“纯规则估价”：

1) **冷启动（弱监督/规则标签）**  
用现有估价逻辑生成标签：`estimated_price`（模板 base_prices/price_service/price_model），再结合 `impact` 做加减分，形成 `pseudo_final_price`（伪最终价）。  
优点：立刻可训练一个 baseline；答辩可解释“弱监督/规则蒸馏”。

2) **小样本人工标注**  
从管理端导出 50~200 条“质检后最终价”作为真实标签（可以自己扮演管理员标注），用于校正模型与评估（MAE/MAPE）。

3) **上线后持续学习**  
每次质检确认后沉淀一条训练样本（问卷+质检→final_price），定期离线重训并版本化。

## 5. 推荐算法（按“可实现/可解释/可答辩”优先）

- **价格回归（final_price）**：LightGBM/XGBoost（树模型，缺失值友好、可解释性强）或 Ridge/Lasso（线性，可解释更强）  
- **异议/取消风险**：Logistic Regression / XGBoost（二分类，输出概率，可做阈值策略）
- **评估指标**：
  - 回归：MAE、MAPE、分组 MAE（按品牌/机型/成色）
  - 分类：AUC、Precision/Recall（尤其关注高风险召回）

## 6. 工程落地（建议写在后端）

**推荐落地位置**：后端 Django（便于拿到 DB 数据、控制版本、写管理端接口）。

最小闭环（建议实现顺序）：

1) **数据集导出**：从 `RecycleOrder` + `AdminInspectionReport` 抽取特征与标签（CSV/Parquet）
2) **训练脚本/管理命令**：离线训练 → 产出模型文件（带版本号与训练参数）
3) **推理服务**：估价接口与管理端定价页调用推理，返回：
   - `suggested_final_price`（建议价）
   - `risk_score`（异议/取消风险）
   - `top_factors`（可解释：impact/质检失败项/机型衰减等）
4) **监控看板**（你已做的统计页可扩展）：
   - 估价误差分布（|final-estimated|）
   - 质检后调价率、异议率、打款失败率
   - 分品牌/机型 TopN（找“模型偏差最大”的分组）

## 7. 已实现的最小闭环（在线推理）

- 管理端回收订单详情接口会返回 `ml` 字段（建议价/风险/因素），用于“随时打开就能分析”：`GET /admin-api/inspection-orders/{id}`
- 也可单独调用预测接口：`GET /admin-api/recycle-ml/predict?order_id={id}`
- 管理端详情页已展示“智能分析（在线推理）”区块：`frontend/src/admin/pages/InspectionOrderDetail.vue`
- 数据看板增加“智能分析”入口页面：`/admin/intelligent-analysis`（`frontend/src/admin/pages/IntelligentAnalysis.vue`）

## 8. 无历史数据的演示：拟真造数 + 批量分析

- 拟真造数命令（生成回收订单+质检报告，便于演示分布与TopN）：`python backend/manage.py seed_recycle_orders --count 2000 --days 60 --ensure-templates`
- 如需重新生成“时间趋势”（不重造数据）：`python backend/manage.py seed_recycle_orders --retime-by-tag --tag FAKE_RECYCLE --days 60`
- 批量分析接口：
  - `GET /admin-api/recycle-ml/summary`（分布/TopN）
  - `GET /admin-api/recycle-ml/batch`（分页列表）
