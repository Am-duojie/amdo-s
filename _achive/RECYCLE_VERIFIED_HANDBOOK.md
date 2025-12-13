回收-官方验-上架全链路梳理（前后端与接口）
=========================================

更新时间：2025-12-12

## 1. 范围与目标
- 覆盖回收下单 → 质检 → 官方验库存（SN 级）→ 一键上架 → 销售/锁控的主要代码与接口。
- 便于新同学快速理解现状、联调，以及定位“回收完成后未联动官方验管理”的问题。

## 2. 业务主线（概要）
1) 用户发起回收：填写设备信息 → 估价 → 创建回收单。  
2) 后台质检：收货 → 录入质检报告 → 确认最终价 → 完结回收单。  
3) 自动/手动生成官方验库存：回收单到达 inspected/completed 时创建 `VerifiedDevice`；或后台按钮手动触发。  
4) SN 级库存管理：搜索、批量操作（锁/解锁/售出/移除/送修等）、打印条码。  
5) 一键上架：从库存生成 `VerifiedProduct`，并更新设备状态（通常锁定或售出）。  
6) 销售锁控：下单前锁定设备，支付成功标售出，取消/失败解锁，避免超卖。

## 3. 后端关键点
### 3.1 模型（`backend/app/secondhand_app/models.py`）
- `RecycleOrder`
  - 状态：pending / quoted / confirmed / shipped / inspected / completed / cancelled
  - 新字段：`final_price_confirmed`(bool, default False)，`payment_retry_count`(int, default 0)
  - 价格：`estimated_price`、`final_price`、`bonus`
  - 支付：`payment_status`、`payment_method`、`payment_account`、`payment_note`
- `VerifiedDevice`（官方验库存，SN 级）
  - 关键：`sn` 唯一（缺省自动占位 `AUTO-XXXXXXXX`）、`brand`/`model`/`storage`/`condition`
  - 状态：ready / locked / sold / repair / removed 等
  - 位置：`location`，成本/建议价：`cost_price`、`suggested_price`
  - 关联：`recycle_order`、`seller`(回收用户)
- `VerifiedProduct`（官方验商品，用于前台售卖）
  - 关联 `verified_device`（一键上架时使用），含价格/成色/封面/图片/库存等字段。

### 3.2 关键函数
- `create_verified_device_from_recycle_order(order, status='ready', location='官方仓')`
  - 幂等：若回收单已有关联设备直接返回。
  - 无 SN 自动生成 `AUTO-XXXXXXXX`。
  - 字段取值：brand/model/storage/condition/price/inspection_note 来源于回收单；`seller=order.user`。
  - 作用：自动/手动打通回收 → 官方验库存。

### 3.3 序列化器（`backend/app/secondhand_app/serializers.py`）
- `RecycleOrderSerializer`
  - 暴露新字段：`final_price_confirmed`、`payment_retry_count`。
  - 状态校验：仅允许用户态流转 quoted→confirmed/shipped；confirmed→shipped；inspected→completed；pending/quoted/confirmed→cancelled。
  - 当状态变为 inspected/completed 时，尝试调用 `create_verified_device_from_recycle_order`（异常吞掉，避免影响主流程）。
- `VerifiedDeviceSerializer`
  - `create` 时未传 `sn` 则自动生成占位 SN。

### 3.4 管理端视图与路由（`backend/app/admin_api`）
- `urls.py`：新增 `POST /admin-api/recycle-orders/<id>/create-verified-device/`（手动生成库存）。
- `InspectionOrderDetailView`
  - `post/put`：提交报告或完成时，当回收单状态进入 inspected/completed 触发自动生成库存。
- `CreateVerifiedDeviceFromRecycleOrderView`
  - 手动触发从回收单生成 `VerifiedDevice`（后台按钮）。
- `AdminVerifiedDeviceView` / `AdminVerifiedDeviceDetailView`
  - 库存列表与 CRUD。
- `AdminVerifiedDeviceActionView`
  - 批量/单条状态操作：lock/unlock/sold/remove/ready/repair 等。
- `AdminVerifiedDeviceListProductView`
  - 一键上架：从 `VerifiedDevice` 创建 `VerifiedProduct`，并更新设备状态。
- 其他：官方验商品上下架、编辑在 AdminVerifiedProduct* 相关视图中。

### 3.5 用户端主要接口（只列与本链路相关）
- `POST /api/recycle-orders/estimate/` 估价
- `POST /api/recycle-orders/` 创建回收单
- `GET /api/recycle-orders/` & `/api/recycle-orders/{id}/`
- `PATCH /api/recycle-orders/{id}/` 用户态状态更新（确认估价/提交物流/异议/确认最终价/取消等）
- `GET /api/recycle-orders/{id}/inspection-report/`
- `GET /api/verified-products/` 列表（官方验）
- `GET /api/verified-products/{id}/` 详情

### 3.6 状态/枚举对齐（建议表）
- 回收单状态：pending / quoted / confirmed / shipped / inspected / completed / cancelled
- 支付状态：pending / paid / failed
- 设备状态：ready / locked / sold / repair / removed（可按需扩展）
- 成色：new / like_new / good / fair / poor（前后端统一）
- 价格类型（质检定价接口）：`price_type` = estimated | final

## 4. 前端用户端（Vue3 + Element Plus）
- `src/pages/Recycle.vue`：设备信息表单 → 估价 → 创建回收单（当前联系人/地址为占位，建议必填化）。
- `src/pages/MyRecycleOrders.vue`：当前用户回收单列表，状态筛选，跳转详情。
- `src/pages/RecycleOrderDetail.vue`：回收单详情与操作（确认估价、提交物流、异议、确认最终价、取消）；加载质检报告；展示价格/打款信息。
- `src/pages/VerifiedProducts.vue`：官方验商品列表，筛选条件（分类/品牌/成色/搜索），分页。
- `src/pages/VerifiedProductDetail.vue`：官方验商品详情、质检信息、报告与详情图；成色映射需对齐后端枚举。

## 5. 前端管理端
- `src/admin/pages/RecycleOrderManagement.vue`：回收单列表/筛选，进度条高亮修正（completed 显示为完成）。
- `src/admin/pages/components/RecycleOrderDetail.vue`：后台回收单详情；收货、提交质检报告、设置最终价、更新状态；按钮“生成官方验库存”调用 `/admin-api/recycle-orders/{id}/create-verified-device/`。
- `src/admin/pages/VerifiedDeviceInventory.vue`：官方验库存（SN 级）列表；搜索/筛选；批量锁/解锁/售出/移除/送修；单条操作；打印条码。
- `src/admin/pages/VerifiedProductManagement.vue`：官方验商品列表；“新增设备”支持演示模式自动生成 SN/IMEI；支持一键上架。
- `src/admin/pages/components/VerifiedProductForm.vue`：官方验商品表单（新增/编辑）；一键上架可带入库存设备信息预填。

## 6. 状态机与锁控
- 回收单（用户态允许）：quoted→confirmed/shipped；confirmed→shipped；inspected→completed；pending/quoted/confirmed→cancelled。
- 设备状态：ready（可售）/ locked（锁定防超卖）/ sold / repair / removed 等。
- 锁控策略：下单前锁设备，支付成功标售出；取消/失败解锁。批量与单条动作由 `AdminVerifiedDeviceActionView` 提供。

## 7. 已知问题与建议
- 成色枚举对齐：后端为 new/like_new/good/fair/poor，前端映射需同步，避免 fallback。
- 品牌/分类硬编码：官方验列表/管理端建议改为后端数据驱动。
- 联系方式：回收下单页应强制填写联系人/电话/地址，避免占位“待填写”。
- 打印条码：前后端统一使用 SN（或 IMEI）作为打印值。
- 自动生成库存的异常当前被吞掉，排查需看后台日志。

## 8. 自测建议（示例流）
1) 用户登录，调用 `/api/recycle-orders/estimate/` 使用有价格数据的组合（如：device_type=手机、brand=苹果、model=iPhone 15 Pro Max、storage=256GB、condition=good）。  
2) 创建回收单 `/api/recycle-orders/`（填 estimated_price/bonus/联系人/电话/地址）。  
3) 管理端登录后：收货 `POST /admin-api/inspection-orders/{id}/received` → 提交质检报告 `POST /admin-api/inspection-orders/{id}` → 设置最终价 `PUT /admin-api/inspection-orders/{id}/price` → 完成 `PUT /admin-api/inspection-orders/{id}` status=completed。  
4) 检查自动生成 `VerifiedDevice`（也可手动 `POST /admin-api/recycle-orders/{id}/create-verified-device/`）。  
5) 在库存页执行一键上架，生成 `VerifiedProduct`；确认设备状态随之更新（锁/售出）。  
6) 前台 `GET /api/verified-products/` 能看到上架商品，详情页展示质检/图片。

## 9. 现有文档/参考
- 代码内相关文件：`backend/app/secondhand_app/models.py`、`serializers.py`、`admin_api/views.py|urls.py`；前端 `src/pages` 与 `src/admin/pages` 下对应 Vue 组件。
- 既有业务文档：`RECYCLE_BUSINESS_FLOW.md`、`RECYCLE_BUSINESS_PROCESS.md`、`BUSINESS_FLOW_COMPLETE.md` 等。

## 10. 本次对话摘要（Cursor 会话）
- 用户需求：将回收→官方验→上架的学习与代码梳理落库成文档，便于后续对齐与排查“回收完成后官方验未联动”问题。
- 产出：本文件 `RECYCLE_VERIFIED_HANDBOOK.md`，覆盖业务链路、后端模型/接口、前端用户端与管理端页面、状态机/锁控、已知问题和自测流程。
- 重点提醒：成色枚举对齐（new/like_new/good/fair/poor）；回收单必填联系人/电话/地址；品牌/分类建议后端驱动；库存锁控需落地在下单/取消/支付回调；自动生成库存异常需查日志。

## 11. 待完善/风险点清单
- 成色映射：前端所有成色展示/筛选统一为 new/like_new/good/fair/poor。
- 品牌/分类：列表筛选改为后端返回（避免硬编码）；官方验商品的分类与设备品牌对齐。
- 联系方式必填：回收下单必须提供联系人/电话/地址，避免占位“待填写”写入库。
- 锁控落地：下单锁设备、取消/支付失败解锁、支付成功标售出；批量动作与订单状态保持一致。
- 支付/钱包：确认官方验下单与库存状态同步（避免已售商品仍可下单）。
- 质检报告规范：检查 `check_items`/`overall_result`/`score` 的字段要求与前端表单一致性。
- 条码打印：统一使用 SN 或 IMEI，前后端一致。
- 事务/幂等：回收单完成→生成库存需包裹在事务中；手动生成接口保持幂等。
- 日志与报警：自动生成库存失败需在日志可见；考虑增加告警。
- 测试脚本：建议保留一份可跑通的示例（后端 Python client 或 Postman collection），使用有价格数据的机型组合。

## 12. 简易接口示例（便于校验）
- 估价：`POST /api/recycle-orders/estimate/`  
  ```json
  {"device_type":"手机","brand":"苹果","model":"iPhone 15 Pro Max","storage":"256GB","condition":"good"}
  ```
- 创建回收单：`POST /api/recycle-orders/`  
  ```json
  {"device_type":"手机","brand":"苹果","model":"iPhone 15 Pro Max","storage":"256GB","condition":"good","estimated_price":7200,"bonus":100,"contact_name":"张三","contact_phone":"13800000000","address":"上海市..."}
  ```
- 质检报告：`POST /admin-api/inspection-orders/{id}`  
  ```json
  {"remarks":"自动测试质检","check_items":{"screen":"ok","battery":"88%"},"overall_result":"passed","recommend_price":7200,"score":90,"evidence":[]}
  ```
- 设置最终价：`PUT /admin-api/inspection-orders/{id}/price`  
  ```json
  {"price_type":"final","final_price":7200,"bonus":100}
  ```
- 完成并尝试生成库存：`PUT /admin-api/inspection-orders/{id}` with `{"status":"completed"}`  
- 手动生成库存：`POST /admin-api/recycle-orders/{id}/create-verified-device/`
- 一键上架：`POST /admin-api/verified-devices/{id}/list-product`（若接口路由为 AdminVerifiedDeviceListProductView）
- 库存批量操作：`POST /admin-api/verified-devices/actions/`  
  ```json
  {"action":"lock","ids":[1,2,3]}
  ```

## 13. 其他业务概览（待按需深挖）
- C2C/商城交易：商品（Product）、订单（Order）、支付回调、物流/收货，详见 `COMPLETE_FEATURES_SUMMARY.md`、`BUSINESS_FLOW_COMPLETE.md`。
- 官方验售卖端：`VerifiedOrder` 下单/支付/取消/售后等流程，需与设备锁定/解锁联动（支付成功标 sold，取消/失败解锁）。
- 支付/结算：支付宝支付、分账、回调与重试，详见 `PAYMENT_FLOW_COMPLETE.md`、`PAYMENT_CALLBACK_IMPLEMENTATION.md`、`ALIPAY_*` 系列文档。
- 钱包/流水：`Wallet`、`WalletTransaction` 记录充值/退款/提现/商品结算，回收打款也需同步流水；参考 `PAYMENT_*`、`ROYALTY_FIX_SUMMARY.md`。
- 通知/实时：Channels/WebSocket 推送订单/支付/消息（若开启聊天或状态通知），参考 `consumers.py` / `routing.py`。
- 数据修复与脚本：`cleanup_verified.py`、`verify_*`、`check_*`、`export_*` 等辅助脚本，用于数据导出、校验与修复。

## 14. 后续可补充的细化方向
- 逐模块字段级说明：`VerifiedOrder`、`Wallet*`、`Order`（C2C）、支付回调参数与签名校验。
- 前端商城侧：商品列表/详情/下单/支付/订单列表与售后页面的接口对照。
- 运维与排障：ngrok 使用、支付回调环境、常见错误码与修复手册。
- 测试资产：统一的 Postman / Python client 脚本集合，覆盖回收、官方验、支付与退款路径。

## 15. 详细字段与状态对照（当前代码可见范围）
- RecycleOrder（回收单，`secondhand_app/models.py`）
  - 核心：user、device_type、brand、model、storage、condition、note、estimated_price、final_price、bonus、status、payment_status、payment_method、payment_account、payment_note、shipped_at、final_price_confirmed、payment_retry_count、created_at、updated_at。
  - 状态机（用户态允许）：quoted→confirmed/shipped；confirmed→shipped；inspected→completed；pending/quoted/confirmed→cancelled。
- VerifiedDevice（官方验库存，SN 级）
  - 核心：sn（唯一，缺省 AUTO-XXXXXXXX）、brand、model、storage、condition、status、location、suggested_price、cost_price、inspection_note、recycle_order、seller、created_at、updated_at。
  - 状态：ready / locked / sold / repair / removed（可扩展）。
- VerifiedProduct（官方验商品）
  - 核心：verified_device、title/subtitle、price、original_price、condition、category、cover_image、images/detail_images、stock、status（active/inactive）、location、description、created_at、updated_at。
- VerifiedOrder（官方验订单，未在本链路详述）
  - 需与设备锁控联动：下单锁定、支付成功售出、取消/支付失败解锁。
- Wallet / WalletTransaction
  - 记录充值/退款/提现/结算与回收打款，确保与订单/设备状态一致。

## 16. 前后端动作映射（关键页面/接口）
- 用户端
  - 回收估价：Recycle.vue → `POST /api/recycle-orders/estimate/`
  - 创建回收单：Recycle.vue → `POST /api/recycle-orders/`
  - 回收单列表：MyRecycleOrders.vue → `GET /api/recycle-orders/`
  - 回收单详情/操作：RecycleOrderDetail.vue → `GET /api/recycle-orders/{id}/`，`PATCH /api/recycle-orders/{id}/`（确认估价/物流/异议/确认最终价/取消），`GET /api/recycle-orders/{id}/inspection-report/`
  - 官方验列表：VerifiedProducts.vue → `GET /api/verified-products/`
  - 官方验详情：VerifiedProductDetail.vue → `GET /api/verified-products/{id}/`
- 管理端
  - 回收单列表：RecycleOrderManagement.vue → `GET /admin-api/inspection-orders/`
  - 质检收货：RecycleOrderDetail.vue → `POST /admin-api/inspection-orders/{id}/received`
  - 提交质检报告：RecycleOrderDetail.vue → `POST /admin-api/inspection-orders/{id}`
  - 设置最终价：RecycleOrderDetail.vue → `PUT /admin-api/inspection-orders/{id}/price`
  - 完成回收单：RecycleOrderDetail.vue → `PUT /admin-api/inspection-orders/{id}`（status=completed）
  - 手动生成库存：RecycleOrderDetail.vue → `POST /admin-api/recycle-orders/{id}/create-verified-device/`
  - 库存列表/操作：VerifiedDeviceInventory.vue → `GET /admin-api/verified-devices/`；动作 `POST /admin-api/verified-devices/actions/`
  - 库存单条操作：VerifiedDeviceInventory.vue → `POST /admin-api/verified-devices/{id}/actions/`（若后端支持）
  - 一键上架：VerifiedDeviceInventory.vue 或 VerifiedProductManagement.vue → `POST /admin-api/verified-devices/{id}/list-product`
  - 官方验商品管理：VerifiedProductManagement.vue / VerifiedProductForm.vue → `GET/POST/PUT /admin-api/verified-products/`，下架/删除等视后端路由。

## 17. 锁控与事务建议（避免超卖）
- 下单前：检查设备状态=ready；下单即锁定（locked）。
- 支付成功：设备标 sold；商品库存减一。
- 取消/支付失败：解锁设备（回到 ready）并恢复库存。
- 一键上架：同步更新设备状态（通常锁定/售出）与商品状态。
- 推荐：相关接口使用数据库事务包裹，并对重复请求做幂等（避免并发下单）。

## 18. 日志与监控建议
- 自动生成库存失败：记录异常与回收单 ID，便于人工补单或重试。
- 设备锁控：记录锁/解锁/售出操作的请求来源（订单号、用户、时间）。
- 支付回调：记录第三方流水号、签名校验结果、状态变更结果。
- 质检与定价：记录操作人、请求体、结果价格，便于纠纷追溯。

## 19. 数据校验与一致性
- 成色/状态/分类：前后端统一枚举，禁止硬编码偏差。
- 联系方式：回收单创建时强制校验联系人/电话/地址。
- 质检报告：`check_items`/`overall_result`/`score` 的必填与格式需前后端一致。
- 图片字段：cover / images / detail_images / inspection_reports 的兜底与去重。
- 价格字段：estimated_price/final_price/bonus 不为空且类型正确；价格类型 `price_type`=estimated|final。

## 20. 测试与脚本
- 建议保留可执行示例（Python client 或 Postman）覆盖：估价→创建回收单→收货→质检报告→定价→完成→自动生成库存→手动生成库存→一键上架→前台列表/详情校验。
- 使用已知有价格数据的机型组合（例如：手机/苹果/iPhone 15 Pro Max/256GB/condition=good）。

## 21. 运维与排障（提纲）
- ngrok/内网穿透：参见 `NGROK_USAGE.md`、`INTRANET_PENETRATION_GUIDE.md`。
- 支付回调常见问题：签名失败、回调地址错误、分账失败重试，参见 `PAYMENT_*`、`ALIPAY_*` 文档。
- 数据修复：`cleanup_verified.py`、`verify_*`、`check_*` 脚本在异常数据（缺字段/状态错位）时可用。

## 22. 后端模块与接口（更细粒度）
- models（`secondhand_app/models.py`）
  - RecycleOrder：上文字段；`shipped_at` 若状态改 shipped 且未填，会在 serializer 中自动补当前时间。
  - VerifiedDevice：SN 唯一；关联回收单/卖家；状态机不在模型内，动作由视图/批量接口控制。
  - VerifiedProduct：关联库存设备；价格/原价/库存/图片/成色/分类/地点；状态 active/inactive。
  - VerifiedOrder：官方验订单，需与设备锁定联动（建议补全字段说明与状态机）。
  - Wallet / WalletTransaction：钱包及流水，记录充值/退款/提现/结算/回收打款。
- serializers（`secondhand_app/serializers.py`）
  - RecycleOrderSerializer：状态校验；inspected/completed 自动尝试生成 VerifiedDevice；暴露新增字段 final_price_confirmed/payment_retry_count。
  - VerifiedDeviceSerializer：create 缺 sn 时自动生成 AUTO-XXXXXXXX。
  - VerifiedProduct/VerifiedOrder 等序列化器（未全文列出）建议后续补字段对照。
- admin 视图（`admin_api/views.py`）
  - InspectionOrderDetailView：收货/质检报告/定价/完成时调用创建库存；更新回收状态。
  - CreateVerifiedDeviceFromRecycleOrderView：手动生成库存。
  - AdminVerifiedDeviceView/Detail：库存列表与 CRUD。
  - AdminVerifiedDeviceActionView：批量/单条动作 lock/unlock/sold/remove/ready/repair。
  - AdminVerifiedDeviceListProductView：一键上架，生成 VerifiedProduct 并更新设备状态。
  - AdminVerifiedProduct*：商品列表/创建/更新/下架/删除等（需确认路由）。
- 用户接口（`secondhand_app/views.py`）
  - RecycleOrderViewSet：estimate、list、retrieve、partial_update（用户态状态机）、inspection_report。
  - VerifiedProductViewSet：列表/详情（官方验商品用户端）。
  - VerifiedOrderViewSet：下单/支付/取消等（未详述，待补字段与锁控）。

## 23. 前端页面与数据流（更细粒度）
- 用户端
  - Recycle.vue：表单 `device_type/brand/model/storage/condition`；`submitEstimate` → `/api/recycle-orders/estimate/`；`createRecycleOrder` → `/api/recycle-orders/`（需补联系人/电话/地址必填）。
  - MyRecycleOrders.vue：`GET /api/recycle-orders/`（status 分页）；展示支付 tag；点击跳转详情。
  - RecycleOrderDetail.vue：`loadOrderDetail` + `loadInspectionReport`；动作 `PATCH /api/recycle-orders/{id}/`（confirm/shipping/dispute/final/cancel）；`GET /inspection-report/`；质检报告展示 check_items/score/备注。
  - VerifiedProducts.vue：筛选条件（category/brand/condition/search）；`GET /api/verified-products/`（status=active，ordering=-created_at）；分页。
  - VerifiedProductDetail.vue：`GET /api/verified-products/{id}/`；图片兜底（cover/detail/images）；质检信息/报告列表；成色映射需对齐 new/like_new/good/fair/poor。
- 管理端
  - RecycleOrderManagement.vue：列表筛选；进度条 active/completed 逻辑；`GET /admin-api/inspection-orders/`。
  - RecycleOrderDetail.vue（admin 组件）：`GET /admin-api/inspection-orders/{id}`；收货 `POST .../received`；质检报告 `POST .../{id}`；定价 `PUT .../{id}/price`；完成 `PUT .../{id}` status=completed；手动生成库存 `POST /admin-api/recycle-orders/{id}/create-verified-device/`。
  - VerifiedDeviceInventory.vue：`GET /admin-api/verified-devices/`；批量动作 `POST /admin-api/verified-devices/actions/`（lock/unlock/sold/remove/ready/repair）；单条动作同接口（或 detail/actions）；打印条码。
  - VerifiedProductManagement.vue：官方验商品列表；新增设备（演示模式自动生成 SN/IMEI）；一键上架入口调用 `list-product`；下架/删除等操作。
  - VerifiedProductForm.vue：商品表单（标题/价格/原价/成色/分类/描述/封面/图片/库存/关联设备）；一键上架预填库存信息。

## 24. 建议的补充与校验清单（前后端联合）
- 确认 VerifiedOrder 全流程：下单→支付→取消/退款，对设备锁定的影响（需与 AdminVerifiedDeviceAction/商品库存协同）。
- 补齐支付回调与钱包流水的状态映射：订单状态变化 ↔ 钱包/流水记录 ↔ 设备状态。
- 前端成色、状态、分类枚举统一由后端接口下发或集中常量，避免硬编码。
- 商品/库存图片字段统一：cover/ images/ detail_images/ inspection_reports 的兜底与顺序。
- 文档化批量动作的返回格式与错误处理（例如部分成功、已售无法操作等）。
- 增加幂等键（如订单号/请求号）以防重复扣减或重复上架。
- 集中一份 Postman/脚本覆盖：回收端全链路 + 官方验库存/上架 + 官方验下单/支付/取消 + 设备锁控验证。

## 25. 官方验订单 VerifiedOrder（建议补充字段/状态机）
- 字段建议：user、verified_product、verified_device、order_no（幂等）、amount_payable、amount_paid、payment_method、payment_status、status、address/receiver/phone、remark、paid_at、cancelled_at、refunded_at、created_at、updated_at。
- 状态机示例：created → pending_payment → paid → (shipped?) → completed；可取消：pending_payment→cancelled；退款：paid/completed→refunding→refunded。
- 设备锁映射：created/待支付时锁定设备；支付成功标 sold；取消/支付失败解锁；退款成功可按策略回退库存（视业务规则）。
- 接口（待在后端确认/补齐）：下单 `POST /api/verified-orders/`，支付 `POST /api/verified-orders/{id}/pay`，取消 `POST /api/verified-orders/{id}/cancel`，退款 `POST /api/verified-orders/{id}/refund`。
- 建议：所有支付/取消/退款接口使用幂等号（order_no 或 request_id）避免重复扣减；在交易逻辑内做事务。

## 26. 支付回调与分账（建议补充）
- 回调参数：第三方交易号、商户订单号、金额、签名、支付状态、时间戳等；需校验签名与金额。
- 回调流程：验签→查单→幂等判断→更新订单支付状态→更新设备/库存→记 Wallet 流水→返回成功。
- 分账/结算：若有分账，记录分账单号与状态；失败时入重试队列或人工核对。参考 `ALIPAY_*`、`PAYMENT_CALLBACK_IMPLEMENTATION.md`。
- 常见错误：签名失败（公钥/编码问题）、金额不符（精度/币种）、重复回调（需幂等）、分账失败（账户/额度/限频）。

## 27. 钱包与流水（Wallet/WalletTransaction）
- 字段建议：wallet（用户）、type（recharge/withdraw/settle/refund/payout 等）、amount、direction（in/out）、currency、related_order_id、related_order_type（RecycleOrder/VerifiedOrder/C2C Order）、method（alipay/balance）、status、remark、created_at、updated_at。
- 约束：金额精度一致；所有订单/支付变更必须写流水；流水与订单/设备状态一致性需事务。
- 回收打款：RecycleOrder 完成后打款记一条入账流水；支付失败/重试计数 `payment_retry_count`。
- 官方验支付：支付成功记入账，退款记出账；与设备 sold/解锁同步。

## 28. C2C/商城商品与订单（概要，待深挖）
- Product：标题、价格、原价、库存、封面/图片、分类、成色、状态（上架/下架）、卖家。
- Order（C2C）：买家/卖家、商品、数量、价格、支付状态、物流状态（待发货/已发货/已收货）、售后/退款状态。
- 物流/收货：收货地址、快递单号/公司、发货/收货时间；状态更新接口需与支付/售后联动。
- 前端商城侧：商品列表/详情/下单/支付/订单列表/售后，对应 API 需与状态机对齐。

## 29. 前端枚举与配置统一
- 成色：统一 new/like_new/good/fair/poor；组件、筛选、后端枚举一致。
- 状态：回收单/设备/订单/支付状态集中定义；避免多处硬编码。
- 分类/品牌：尽量由后端下发；若本地常量，集中单处维护。
- 图片/文件：cover/images/detail_images/inspection_reports 的兜底与顺序统一，上传组件与后端字段一致。
- 错误提示与拦截器：前端统一处理 401/403/422/500；JWT 过期刷新或重登策略。

## 30. 权限与认证（简述）
- 管理端：若有角色权限，需确认 admin_api 是否做了权限校验（视 settings/DRF 配置）；前端根据角色隐藏/禁用按钮。
- JWT：前后端统一使用 Authorization: Bearer；刷新/过期处理，前端拦截器重试或跳转登录。

## 31. 运行/部署与环境要点
- 环境变量：数据库、Redis、JWT 密钥、第三方支付、公私钥、媒体路径、回调/前端地址等。
- 媒体/上传：确保 media 路径可写；大文件/图片压缩策略。
- ngrok/内网穿透：回调地址需可达；参考 `NGROK_USAGE.md`、`INTRANET_PENETRATION_GUIDE.md`。
- 并发与锁：下单/库存操作需事务与幂等，避免超卖。

## 32. 测试资产与覆盖建议
- 提供 Postman/Python 脚本集合，覆盖：回收估价→下单→质检→定价→完成→自动/手动生成库存→一键上架→官方验下单→支付→取消/退款→锁控验证。
- 使用有价格数据的机型（如 iPhone 15 Pro Max 256GB condition=good）作为基线用例。
- 增加异常用例：重复回调、支付金额不符、设备已锁/已售再下单、批量动作部分失败等。

## 33. VerifiedOrder 字段与状态（表格化草案）
- 关键字段（建议对照后端实际）：
  - order_no（唯一幂等号）、user、verified_product、verified_device
  - amount_payable、amount_paid、currency
  - payment_method（alipay/balance/其他）、payment_status（pending/paid/failed/refunding/refunded）
  - status（created/pending_payment/paid/shipped/completed/cancelled/refunded）
  - address / receiver / phone
  - remark、paid_at、cancelled_at、refunded_at、created_at、updated_at
- 状态机示例：
  - created → pending_payment → paid → (shipped) → completed
  - 取消：pending_payment → cancelled
  - 退款：paid/completed → refunding → refunded（可选回退库存策略）
- 设备锁映射：
  - 创建/待支付：锁定设备（status=locked）
  - 支付成功：设备标 sold
  - 取消/支付失败：解锁设备（回到 ready）
  - 退款成功：按业务决定是否回退库存/解锁
- 接口示例（需与后端路由对齐）：
  - 下单：`POST /api/verified-orders/`
  - 支付：`POST /api/verified-orders/{id}/pay`（带 payment_method）
  - 取消：`POST /api/verified-orders/{id}/cancel`
  - 退款：`POST /api/verified-orders/{id}/refund`
  - 详情/列表：`GET /api/verified-orders/`、`GET /api/verified-orders/{id}/`
- 幂等建议：所有支付/取消/退款接口带 request_id 或使用 order_no 做幂等；接口内部加数据库唯一幂等表或乐观锁。

## 34. Wallet / WalletTransaction 字段与场景
- WalletTransaction 字段（建议对照后端实际）：
  - user/wallet、type（recharge/withdraw/settle/refund/payout）、direction（in/out）
  - amount、currency、balance_before/after（可选）、status（pending/success/failed）
  - method（alipay/balance/other）、related_order_id、related_order_type（RecycleOrder/VerifiedOrder/C2C）
  - remark、request_id（幂等）、created_at、updated_at
- 典型场景对照：
  - 回收打款：RecycleOrder 完成 → payout 入账流水；失败重试累计 payment_retry_count。
  - 官方验支付：支付成功 → in 流水；退款 → out 流水；与设备 sold/解锁同步。
  - C2C 结算/分账：买家支付成功 → 卖家结算入账；平台分账/佣金。
  - 提现/充值：withdraw/out；recharge/in。
- 一致性要求：订单状态变更、设备锁控、钱包流水写入需在事务内完成；同一 request_id 需幂等。

## 35. 支付回调/分账参数与处理（示例）
- 回调典型参数：out_trade_no（商户单号）、trade_no（第三方流水）、total_amount、seller_id/app_id、trade_status、timestamp、sign、buyer_id 等。
- 处理流程：
  1) 验签（公钥、字符集、签名算法）；
  2) 校验金额/订单号存在性；
  3) 幂等判断（根据 order_no + trade_no 记录）；
  4) 更新订单支付状态、写 Wallet 流水、更新设备锁控；
  5) 分账（如有）：记录分账单号/状态，失败入重试队列；
  6) 返回成功应答给支付平台。
- 常见错误与重试：
  - 签名失败：检查公钥/编码/参与签名字段顺序。
  - 金额不符：精度/币种/小数位处理。
  - 重复回调：需幂等直接返回成功。
  - 分账失败：账户未配置/额度/限频，需重试或人工处理。
- 日志建议：记录回调原文、验签结果、订单号、trade_no、处理结果；异常报警。

## 36. “易淘”商城/C2C 业务流程（概要补充）
- 用户侧主链路
  1) 浏览商品列表/详情（Product）→ 加入购物车或直接下单（若有购物车模块）。  
  2) 下单：选择地址/支付方式，生成 Order（商户单号）。  
  3) 支付：调用支付渠道，成功后 Order 支付状态更新（pending→paid），写 WalletTransaction（in），若为官方验/自营商品需锁/扣库存。  
  4) 发货：商家/平台填写物流公司与单号，订单物流状态更新（pending_ship→shipped）。  
  5) 收货：买家确认收货（shipped→completed）；若超时可自动收货（视业务配置）。  
  6) 售后/退款：paid/completed 状态可发起退款/退货退款，进入 refunding→refunded，需与库存/结算同步。  
  7) 评价（若有）：完成后可评价商品/店铺。  
- 卖家/管理侧
  - 商品管理：上/下架、价格/库存维护、图片/分类/品牌。  
  - 订单管理：查看订单、发货、同意/拒绝售后、退款处理。  
  - 结算/分账：买家支付成功后，按规则将货款结算到卖家钱包，平台抽佣；失败需重试/人工。  
  - 风控/纠纷：异常订单、拒收、未发货超时等处理策略。  
- 模型与状态（建议对照实际实现）
  - Product：title/price/original_price/stock/status(category/brand/condition/cover/images)。  
  - Order：买家/卖家、商品/数量、amount、payment_status(pending/paid/failed/refunding/refunded)、status(pending_payment/pending_ship/shipped/completed/cancelled)、logistics_company/tracking_no、address/receiver/phone、remark、timestamps。  
  - 售后：退款单（可单独表），关联订单/商品、原因、金额、状态（pending/refunding/refunded/rejected）。  
  - 结算/分账：与 WalletTransaction 关联，记录平台佣金、卖家入账。  
- 接口（需与实际路由确认）
  - 商品：`GET /api/products/`、`GET /api/products/{id}/`、`POST/PUT /admin-api/products/` 上下架、删除。  
  - 订单：`POST /api/orders/` 下单，`POST /api/orders/{id}/pay`，`POST /api/orders/{id}/cancel`，`POST /api/orders/{id}/confirm-receipt`，`POST /api/orders/{id}/refund`，`GET /api/orders/` 列表。  
  - 售后：`POST /api/refunds/`、`GET /api/refunds/`、`POST /api/refunds/{id}/agree|reject`（管理/卖家侧）。  
  - 物流：`POST /admin-api/orders/{id}/ship`（填写快递）。  
- 联动要点
  - 库存：下单锁库存，支付成功扣减；取消/支付失败解锁；退款可选回补。  
  - 钱包/分账：支付成功→平台/卖家分账入账；退款→对应出账；全部需幂等与事务。  
  - 状态机：支付/物流/售后状态应分离但一致性校验，避免互相覆盖。  

## 37. 关键模型字段清单（精细版，按当前代码惯例）
- RecycleOrder
  - 基本：id, user, device_type(str), brand(str), model(str), storage(str), condition(str), note(text)
  - 价格：estimated_price(decimal), final_price(decimal), bonus(decimal, 可空)
  - 状态：status(enum: pending/quoted/confirmed/shipped/inspected/completed/cancelled)
  - 支付：payment_status(enum pending/paid/failed), payment_method(str), payment_account(str), payment_note(text), payment_retry_count(int, default 0), final_price_confirmed(bool, default False)
  - 物流：shipped_at(datetime, serializer 自动补), tracking_number/express_company(若有)
  - 时间：created_at, updated_at
- VerifiedDevice
  - 标识：id, sn(unique, auto fallback AUTO-XXXXXXXX), imei(若有)
  - 关联：recycle_order(FK), seller(FK user)
  - 规格：brand, model, storage, condition(enum new/like_new/good/fair/poor)
  - 状态：status(enum ready/locked/sold/repair/removed...), location(str)
  - 价格：suggested_price, cost_price
  - 质检：inspection_note(text)
  - 时间：created_at, updated_at
- VerifiedProduct
  - 关联：verified_device(FK 可空), seller(若有 C2C 场景), category, brand, model, storage, condition
  - 展示：title, subtitle, description, cover_image, images[], detail_images[]
  - 价格与库存：price, original_price, stock, status(active/inactive), location
  - 时间：created_at, updated_at
- VerifiedOrder（建议落地时核对）
  - 关联：user, verified_product, verified_device, address/receiver/phone
  - 金额：amount_payable, amount_paid, currency
  - 状态：status(created/pending_payment/paid/shipped/completed/cancelled/refunded), payment_status(pending/paid/failed/refunding/refunded)
  - 支付：payment_method, order_no(幂等), paid_at, cancelled_at, refunded_at
  - 物流：logistics_company, tracking_no, shipped_at, delivered_at（若有）
  - 时间：created_at, updated_at
- WalletTransaction
  - 关联：user/wallet, related_order_id, related_order_type(RecycleOrder/VerifiedOrder/C2C)
  - 金额：amount, currency, direction(in/out), type(recharge/withdraw/settle/refund/payout)
  - 支付方式：method(alipay/balance/other)
  - 状态：pending/success/failed
  - 幂等：request_id
  - 备注/时间：remark, created_at, updated_at

## 38. 状态机与动作示例（更细）
- RecycleOrder（用户态）
  - quoted→confirmed：确认估价
  - quoted/confirmed→shipped：提交物流（自动补 shipped_at）
  - inspected→completed：确认最终价
  - pending/quoted/confirmed→cancelled：取消
- VerifiedDevice
  - ready→locked：下单锁定/批量锁
  - locked→ready：取消/支付失败解锁
  - locked→sold：支付成功或一键上架售出
  - 任意→repair/remove：维护/移除
- VerifiedOrder（示例）
  - created/pending_payment→paid：支付成功
  - pending_payment→cancelled：用户取消/超时取消
  - paid→refunding→refunded：退款
  - paid→completed：收货/自动收货
- C2C Order（示例）
  - pending_payment→paid → pending_ship → shipped → completed
  - pending_payment→cancelled；paid→refunding→refunded

## 39. 接口示例（补充 JSON 样例）
- 官方验下单（示例） `POST /api/verified-orders/`
  ```json
  {"verified_product":123,"address":"上海市...","receiver":"李四","phone":"13800000000","payment_method":"alipay"}
  ```
- 官方验支付 `POST /api/verified-orders/{id}/pay`
  ```json
  {"payment_method":"alipay","request_id":"pay-uuid-1"}
  ```
- 官方验取消 `POST /api/verified-orders/{id}/cancel`
  ```json
  {"reason":"买家取消","request_id":"cancel-uuid-1"}
  ```
- 支付回调（示例载荷）
  ```json
  {"out_trade_no":"ORDER123","trade_no":"ALI456","total_amount":"7200.00","trade_status":"SUCCESS","sign":"...","timestamp":"2025-12-12 12:00:00"}
  ```
- 钱包流水记录（示例）
  ```json
  {"user":1,"type":"payout","direction":"in","amount":"7200.00","currency":"CNY","related_order_type":"RecycleOrder","related_order_id":99,"method":"alipay","request_id":"payout-uuid-1","status":"success"}
  ```

## 40. 进一步待核对/落地项
- VerifiedOrder/WalletTransaction 的实际模型字段与上表一致性；若缺失需补充迁移。
- 支付/退款/分账接口的实际路由与参数，需在代码中确认并补示例。
- 前端对官方验下单/支付/取消/退款的页面与接口对照（当前文档未展开 UI 层细节）。
- C2C 购物车（若有）与订单接口实际路由/请求体需对齐并文档化。

## 41. 实际模型字段摘要（基于 `secondhand_app/models.py` 现有代码）
- VerifiedDevice 状态枚举：pending / repairing / ready / listed / locked / sold / removed；成色枚举：new/like_new/good/fair/poor。
- VerifiedDevice 字段：recycle_order(FK)、seller(FK User)、category(FK Category)、sn(unique)、imei、brand/model/storage、condition、status、location、barcode、cost_price、suggested_price、cover_image、detail_images(JSON)、inspection_reports(JSON)、inspection_result(pass/warn/fail)、inspection_date、inspection_staff、inspection_note、battery_health、screen_condition、repair_history、linked_product(FK VerifiedProduct)、created_at、updated_at。
- VerifiedProduct 状态：pending/active/sold/removed/draft；成色枚举同上。字段：seller、shop、category、title、description、price、original_price、condition、location、contact_phone/wechat、brand/model/storage/screen_size/battery_health/charging_type、verified_at/by、cover_image、detail_images、inspection_reports、inspection_result/date/staff/note、stock、tags(JSON)、published_at、removed_reason、view_count、sales_count、created_at/updated_at。
- RecycleOrder：状态 pending/quoted/confirmed/shipped/inspected/completed/cancelled；payment_status pending/paid/failed；含 device_type/brand/model/storage/condition/note/estimated_price/final_price/bonus/final_price_confirmed/payment_retry_count/contact_name/phone/address/shipping_carrier/tracking_number/shipped_at/received_at/inspected_at/payment_method/account/paid_at/payment_note/price_dispute/price_dispute_reason/reject_reason/created_at/updated_at。
- Wallet：user(one-to-one)、balance、frozen_balance、created_at、updated_at。
- WalletTransaction：transaction_type(income/expense/withdraw/refund)、amount、balance_after、related_order(RecycleOrder)、related_market_order(Order)、note、withdraw_status(pending/processing/success/failed)、alipay_account/name/order_id、created_at。
- Product（C2C）：seller、shop、category、title、description、price、original_price、condition(new/like_new/good/fair/poor)、status(pending/active/sold/removed)、location、contact_phone/wechat、view_count、created_at/updated_at。
- Order（C2C）：buyer、product、total_price、status(pending/paid/shipped/completed/cancelled)、shipping_address/name/phone、carrier、tracking_number、shipped_at、delivered_at、note、created_at/updated_at；支付/分账字段：alipay_trade_no、settlement_status(pending/settled/failed)、settled_at、settle_request_no、seller_settle_amount、platform_commission_amount、settlement_method、transfer_order_id。
- VerifiedOrder（官方验订单）：buyer、product、total_price、status(pending/paid/shipped/completed/cancelled)、shipping_address/name/phone、carrier、tracking_number、shipped_at、delivered_at、note、created_at/updated_at。
- Category/Shop/UserProfile/Message/Favorite/Address 也在该文件，若需可再表格化补充。

## 42. 逐字段表格（依据 `secondhand_app/models.py` 现有定义）
> 若后续迁移有变，请以最新模型为准；choices 写出主要枚举。

### 42.1 RecycleOrder
| 字段 | 类型 | 必填 | 默认/choices | 说明 |
| --- | --- | --- | --- | --- |
| user | FK User | 是 |  | 回收发起人 |
| device_type | Char | 是 |  | 设备类型，估价入参 |
| brand/model/storage | Char | 是 |  | 品牌/型号/存储 |
| condition | Char | 是 | new/like_new/good/fair/poor | 成色 |
| note | Text | 否 |  | 用户备注 |
| estimated_price | Decimal | 否 |  | 估价结果 |
| final_price | Decimal | 否 |  | 最终价 |
| bonus | Decimal | 否 |  | 额外补贴 |
| status | Char | 是 | pending/quoted/confirmed/shipped/inspected/completed/cancelled | 回收单状态 |
| payment_status | Char | 是 | pending/paid/failed | 打款状态 |
| payment_method/account/note | Char/Text | 否 |  | 打款信息 |
| payment_retry_count | Int | 否 | 0 | 打款重试计数 |
| final_price_confirmed | Bool | 否 | False | 用户是否确认最终价 |
| shipping_carrier/tracking_number | Char | 否 |  | 物流公司/单号 |
| shipped_at | DateTime | 否 |  | serializer 在 shipped 时可自动补 |
| received_at/inspected_at/paid_at | DateTime | 否 |  | 流程节点时间 |
| price_dispute / price_dispute_reason / reject_reason | Text | 否 |  | 异议/拒绝原因 |
| contact_name/phone/address | Char | 否 |  | 当前占位，建议改必填 |
| created_at/updated_at | DateTime | 是 | auto |  |

### 42.2 VerifiedDevice（官方验库存）
| 字段 | 类型 | 必填 | 默认/choices | 说明 |
| --- | --- | --- | --- | --- |
| recycle_order | FK RecycleOrder | 否 |  | 由回收单生成 |
| seller | FK User | 否 |  | 默认回收用户 |
| category | FK Category | 否 |  | 若有品类分类 |
| sn | Char unique | 否 | AUTO-XXXXXXXX | 未传自动占位 |
| imei | Char | 否 |  | 可空 |
| brand/model/storage | Char | 是 |  | 规格 |
| condition | Char | 是 | new/like_new/good/fair/poor | 成色 |
| status | Char | 是 | pending/repairing/ready/listed/locked/sold/removed | 真实代码枚举 |
| location | Char | 否 |  | 仓库/库位 |
| barcode | Char | 否 |  | 若打印用 |
| cost_price | Decimal | 否 |  | 成本（回收最终价） |
| suggested_price | Decimal | 否 |  | 建议售卖价 |
| cover_image | Image | 否 |  | 封面 |
| detail_images | JSON | 否 | [] | 详情图 |
| inspection_reports | JSON | 否 | [] | 报告列表 |
| inspection_result | Char | 否 | pass/warn/fail | 质检结果枚举 |
| inspection_date/staff | DateTime/Char | 否 |  | 质检时间/人员 |
| inspection_note | Text | 否 |  | 质检备注 |
| battery_health/screen_condition/repair_history | Char/Text | 否 |  | 额外质检信息 |
| linked_product | FK VerifiedProduct | 否 |  | 上架后回填 |
| created_at/updated_at | DateTime | 是 |  |  |

### 42.3 VerifiedProduct（官方验商品）
| 字段 | 类型 | 必填 | 默认/choices | 说明 |
| --- | --- | --- | --- | --- |
| verified_device | FK VerifiedDevice | 否 |  | 一键上架关联 |
| seller/shop | FK | 否 |  | 若有店铺/卖家 |
| category | FK Category | 否 |  | 分类 |
| title/subtitle/description | Char/Text | 是/否 |  | 展示信息 |
| price | Decimal | 是 |  | 售价 |
| original_price | Decimal | 否 |  | 原价/参考价 |
| condition | Char | 是 | new/like_new/good/fair/poor | 成色 |
| location | Char | 否 |  | 仓库/城市 |
| contact_phone/wechat | Char | 否 |  | 联系方式 |
| brand/model/storage/screen_size/charging_type/battery_health | Char | 否 |  | 规格补充 |
| verified_at/by | DateTime/Char | 否 |  | 官方验时间/人 |
| cover_image | Image | 否 |  | 封面 |
| detail_images | JSON | 否 | [] | 详情图 |
| inspection_reports/result/date/staff/note | JSON/Char/DateTime | 否 |  | 质检信息透传 |
| stock | Int | 是 |  | 库存 |
| tags | JSON | 否 | [] | 标签 |
| status | Char | 是 | pending/active/sold/removed/draft | 商品状态 |
| published_at/removed_reason | DateTime/Text | 否 |  | 上/下架信息 |
| view_count/sales_count | Int | 否 | 0 | 浏览/销量 |
| created_at/updated_at | DateTime | 是 |  |  |

### 42.4 VerifiedOrder（官方验订单）
| 字段 | 类型 | 必填 | 默认/choices | 说明 |
| --- | --- | --- | --- | --- |
| buyer | FK User | 是 |  | 下单人 |
| product | FK VerifiedProduct | 是 |  | 购买商品 |
| verified_device | FK VerifiedDevice | 否 |  | 对应设备 |
| total_price | Decimal | 是 |  | 应付 |
| status | Char | 是 | pending/paid/shipped/completed/cancelled | 实际枚举 |
| payment_status | Char | 是 | pending/paid/failed/refunding/refunded | 支付状态 |
| payment_method | Char | 否 |  | alipay/balance |
| order_no | Char | 否 |  | 幂等号 |
| shipping_address/name/phone | Char | 是 |  | 收件信息 |
| carrier/tracking_number | Char | 否 |  | 物流 |
| shipped_at/delivered_at | DateTime | 否 |  | 发货/收货 |
| note | Text | 否 |  | 备注 |
| created_at/updated_at | DateTime | 是 |  |  |

### 42.5 Wallet 与 WalletTransaction
| 字段 | 类型 | 必填 | 默认/choices | 说明 |
| --- | --- | --- | --- | --- |
| wallet.user | OneToOne User | 是 |  | |
| wallet.balance | Decimal | 是 | 0 | 可用余额 |
| wallet.frozen_balance | Decimal | 是 | 0 | 冻结 |
| WalletTransaction.transaction_type | Char | 是 | income/expense/withdraw/refund | 真实枚举 |
| amount | Decimal | 是 |  | 金额 |
| balance_after | Decimal | 否 |  | 余额快照 |
| related_order | FK RecycleOrder | 否 |  | 回收关联 |
| related_market_order | FK Order | 否 |  | C2C 订单 |
| note | Text | 否 |  | 备注 |
| withdraw_status | Char | 否 | pending/processing/success/failed | 体现状态 |
| alipay_account/name/order_id | Char | 否 |  | 支付宝提现信息 |
| created_at | DateTime | 是 |  |  |

### 42.6 Product（C2C）
| 字段 | 类型 | 必填 | 默认/choices | 说明 |
| --- | --- | --- | --- | --- |
| seller/shop/category | FK | 是 |  | 卖家/店铺/分类 |
| title/description | Char/Text | 是 |  | |
| price/original_price | Decimal | 是/否 |  | 售价/原价 |
| condition | Char | 是 | new/like_new/good/fair/poor | 成色 |
| status | Char | 是 | pending/active/sold/removed | 商品状态 |
| location | Char | 否 |  | 城市 |
| contact_phone/wechat | Char | 否 |  | |
| view_count | Int | 否 | 0 | 浏览 |
| created_at/updated_at | DateTime | 是 |  |  |

### 42.7 Order（C2C）
| 字段 | 类型 | 必填 | 默认/choices | 说明 |
| --- | --- | --- | --- | --- |
| buyer | FK User | 是 |  | 买家 |
| product | FK Product | 是 |  | 商品 |
| total_price | Decimal | 是 |  | 支付金额 |
| status | Char | 是 | pending/paid/shipped/completed/cancelled | 订单状态 |
| alipay_trade_no | Char | 否 |  | 支付宝交易号 |
| settlement_status | Char | 否 | pending/settled/failed | 结算状态 |
| settle_request_no | Char | 否 |  | 结算请求号 |
| seller_settle_amount / platform_commission_amount | Decimal | 否 |  | 分账金额 |
| settlement_method | Char | 否 |  | 分账方式 |
| transfer_order_id | Char | 否 |  | 转账单号 |
| shipping_address/name/phone | Char | 是 |  | 收件信息 |
| carrier/tracking_number | Char | 否 |  | 物流 |
| shipped_at/delivered_at | DateTime | 否 |  | 发货/收货 |
| note | Text | 否 |  | 备注 |
| created_at/updated_at | DateTime | 是 |  |  |

## 43. 路由与前端组件对照（官方验 + 易淘）
- 官方验（B2C）
  - 列表/详情：`GET /api/verified-products/` / `{id}` ↔ `VerifiedProducts.vue` / `VerifiedProductDetail.vue`
  - 下单：`POST /api/verified-orders/` ↔ 待确认页面（若未实现需补）
  - 支付：`POST /api/verified-orders/{id}/pay` ↔ 支付弹窗/按钮
  - 取消/退款：`POST /api/verified-orders/{id}/cancel|refund` ↔ 订单详情页动作
  - 管理：`/admin-api/verified-devices/`、`/actions/`、`/list-product` ↔ `VerifiedDeviceInventory.vue`、`VerifiedProductManagement.vue`
- 易淘（C2C/商城）
  - 商品：`GET /api/products/` / `{id}` ↔ 商品列表/详情页
  - 下单：`POST /api/orders/` ↔ 订单确认页
  - 支付：`POST /api/orders/{id}/pay` ↔ 支付按钮
  - 取消：`POST /api/orders/{id}/cancel` ↔ 订单详情
  - 发货：`POST /admin-api/orders/{id}/ship` ↔ 卖家/管理端发货页
  - 收货：`POST /api/orders/{id}/confirm-receipt`
  - 退款：`POST /api/orders/{id}/refund`、`/api/refunds/{id}/agree|reject` ↔ 售后页

## 44. 典型请求/回调 JSON（补充）
- 回收取消（用户） `PATCH /api/recycle-orders/{id}/`
  ```json
  {"status":"cancelled"}
  ```
- 回收确认物流
  ```json
  {"status":"shipped","shipping_carrier":"顺丰","tracking_number":"SF123"}
  ```
- 库存批量锁定
  ```json
  {"action":"lock","ids":[10,11,12]}
  ```
- 官方验退款
  ```json
  {"reason":"七天无理由","request_id":"refund-uuid-1"}
  ```
- 支付回调（含分账扩展示例）
  ```json
  {"out_trade_no":"ORDER123","trade_no":"ALI456","total_amount":"7200.00","trade_status":"SUCCESS","sign":"...","timestamp":"2025-12-12 12:00:00","royalty":{"status":"SUCCESS","detail":"xxx"}}
  ```

## 45. 校验清单（落地执行版）
- 枚举统一：成色 new/like_new/good/fair/poor；设备状态 pending/repairing/ready/listed/locked/sold/removed；商品状态 pending/active/sold/removed/draft。
- 路由核对：`list-product`、`actions`、官方验订单支付/取消/退款接口是否已实现并在前端调用。
- 锁控落地：下单锁、支付成功 sold、取消/失败解锁；退款策略明确。
- 钱包流水：回收打款/官方验支付/退款/C2C 分账全部写流水，幂等使用 request_id。
- 前端必填：回收联系人/电话/地址改为必填校验；成色/状态显示与后端一致。
- 日志与报警：生成库存失败、支付回调验签失败、分账失败均需日志+告警。
- 测试用例：正常流 + 重复回调 + 已售再下单 + 批量动作部分失败 + 退款回退库存策略。

## 46. 后续行动建议
- 若 VerifiedOrder/WalletTransaction 字段与上表不符，补迁移与序列化器，并在前后端接入支付/取消/退款流程。
- 为官方验下单/支付/取消/退款补前端页面与接口调用，复用锁控逻辑。
- 整理一份 Postman/py 脚本集，按“回收→库存→上架→官方验下单→支付→取消/退款”全链路覆盖，并包含异常回调与幂等校验。
- 将枚举/分类/品牌由后端接口下发或集中常量，移除散落的硬编码。
