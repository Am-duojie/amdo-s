# ???????????????Changelog???

## 2025-12-15

- **Documentation: add Amdo test note**
  - Added placeholder doc `docs/Amdo.md` to validate documentation sync.
  - Verification: open the new doc and confirm placeholder text renders.
- **Documentation: add amdo_1 test note**
  - Added placeholder doc `docs/amdo_1.md` for additional documentation sync testing.
  - Verification: open the new doc and confirm placeholder text renders.

## 2025-12-18

- **Documentation: add admin statistics onepager**
  - Added one-page brief for admin analytics dashboard: `docs/00-overview/admin-statistics-dashboard-onepager.md`
  - Verification: open the doc and confirm it describes metrics, methodology, and data flow.
- **Documentation: add recycle ML onepager + align workflow doc**
  - Added ML plan onepager: `docs/00-overview/recycle-ml-mainline-onepager.md`
  - Aligned recycle workflow doc with implementation (`payment_status=paid` vs `status`): `docs/40-dev-guide/recycle-order-complete-workflow.md`
  - Verification: open both docs and confirm wording matches current API and state fields.
- **Feature: add recycle online inference to admin**
  - Added baseline online inference (suggested price + dispute/cancel risk) and surfaced it in admin recycle order detail: `GET /admin-api/inspection-orders/{id}`
  - Added prediction endpoint: `GET /admin-api/recycle-ml/predict?order_id={id}`
  - Added dashboard entry page: `/admin/intelligent-analysis`
  - Verification: open admin “数据看板 > 智能分析” and confirm results load.
- **Feature: add fake data seeding + batch ML analysis**
  - Added seeding command for realistic recycle orders and inspection reports: `python backend/manage.py seed_recycle_orders --count 2000 --days 60 --ensure-templates`
  - Added batch endpoints: `GET /admin-api/recycle-ml/summary` and `GET /admin-api/recycle-ml/batch`
  - Verification: open admin “数据看板 > 智能分析” → “批量分析” and confirm charts/tables render.

- **Feature: import recycle device templates from JSON**
  - Added JSON import command: `python backend/manage.py import_recycle_templates_json --file <path> --ensure-questions`
  - Added sample template data file: `backend/data/recycle_templates_user.json`
  - Verification: import and confirm new templates appear in admin.

- **Feature: reset recycle + official-verified dataset**
  - Added reset command to clear recycle orders + official verified products/orders: `python backend/manage.py reset_recycle_official_data --yes`
  - Verification: run `--dry-run` then `--yes` and confirm counts drop to 0; re-import templates with `--templates-file`.

- **Feature: unify recycle functional questionnaire**
  - Updated the shared functional question to include “全部正常” and remove unused items; synced via `python backend/manage.py sync_recycle_functional_question`
  - Verification: open recycle wizard step 13 and confirm selection logic.

## 2025-12-14

- **功能完善：官方验商品规格字段扩展** ✅ 已完成
  - 后端模型新增字段：运行内存(ram)、版本(version)、拆修和功能(repair_status)
  - 后端序列化器已添加这三个字段到 VerifiedProductSerializer
  - 数据库迁移已成功执行（migration 0023）
  - 管理端表单已添加这些字段的编辑功能
  - 前端展示页面从后端动态获取所有规格数据，不再写死
  - 主要规格包括：品牌、型号、存储容量、运行内存、版本、成色、拆修和功能
  - 所有前端展示的数据都可以在管理系统中编辑
  - 文件：
    - `backend/app/secondhand_app/models.py` - 添加 ram, version, repair_status 字段
    - `backend/app/secondhand_app/serializers.py` - 在 VerifiedProductSerializer 的 fields 列表中添加 ram, version, repair_status
    - `backend/app/secondhand_app/migrations/0023_add_verified_product_specs.py` - 数据库迁移（已执行）
    - `frontend/src/admin/pages/components/VerifiedProductForm.vue` - 添加字段编辑功能
    - `frontend/src/pages/VerifiedProductDetail.vue` - 从后端动态获取数据
  - 验证方式：在管理端编辑官方验商品，填写运行内存、版本、拆修和功能；保存后在前端查看商品详情，检查这些字段是否正确显示

- **UI优化：官方验商品详情页设备规格模块**
  - 将原有的简单质检信息模块替换为更详细的设备规格模块
  - 关键规格始终显示：外观、电池健康度、屏幕尺寸
  - 详细规格可折叠展开：存储容量、充电方式、质检日期、质检员、质检结果
  - 使用图标和卡片式设计，提升视觉效果
  - 支持展开/收起功能，优化信息展示层次
  - 文件：
    - `frontend/src/pages/VerifiedProductDetail.vue` - 替换质检信息模块为设备规格模块
    - `docs/70-ui/verified-product-detail-optimization.md` - 详细的优化建议文档
  - 验证方式：访问官方验商品详情页，查看设备规格模块是否正确显示；点击"展开更多"按钮，检查详细规格是否正确展开/收起

## 2025-12-14

- **流程优化：回收订单提交流程改进**
  - 用户完成估价问卷后，跳转到估价详情页（`RecycleCheckout.vue`）查看预估价格和详细信息
  - 用户点击"提交订单"后，订单状态为 `pending`（待寄出），并自动跳转到订单详情页
  - 用户在订单详情页填写物流信息（物流公司、运单号）后，订单自动变为 `shipped`（已寄出）
  - 后端自动检测：当用户填写物流信息时，订单状态从 `pending` 自动变为 `shipped`，并设置寄出时间
  - 完整流程：估价问卷 → 估价详情页 → 提交订单（pending）→ 填写物流（shipped）→ 平台收货（received）→ 质检（inspected）→ 确认价格（completed）→ 打款
  - 文件：
    - `backend/app/secondhand_app/serializers.py` - 修改订单创建逻辑，初始状态为 `pending`；在 update 方法中添加自动状态转换逻辑
    - `frontend/src/pages/RecycleCheckout.vue` - 更新页面标题为"估价详情"；提交订单后跳转到订单详情页而不是订单列表
    - `frontend/src/pages/RecycleOrderDetail.vue` - 在 `pending` 状态显示"填写物流信息"按钮；简化物流信息提交逻辑
  - 验证方式：完成估价问卷 → 查看估价详情 → 提交订单 → 自动跳转到订单详情页 → 填写物流信息 → 检查状态是否自动变为"已寄出"

- **功能新增：回收订单价格确认流程**
  - 管理员完成质检并设置最终价格后，用户需要确认价格才能进入打款阶段
  - 新增用户端价格确认API端点：`POST /api/recycle-orders/{id}/confirm_final_price/`
  - 管理端显示"等待用户确认价格"提示，用户确认后订单自动变为"已完成"状态
  - 用户端显示最终价格和加价金额，提供"确认最终价格"和"对最终价格有异议"两个选项
  - 确认价格后 `final_price_confirmed` 字段变为 `true`，订单状态自动变为 `completed`
  - 完整流程：pending（用户填写物流）→ shipped（管理员收货）→ received（管理员质检）→ inspected（用户确认价格）→ completed（管理员打款）
  - 文件：
    - `backend/app/secondhand_app/views.py` - 新增 `confirm_final_price` action
    - `backend/app/admin_api/views.py` - 在订单详情响应中添加 `final_price_confirmed` 字段
    - `frontend/src/pages/RecycleOrderDetail.vue` - 更新价格确认UI和逻辑，添加物流信息填写功能
    - `frontend/src/admin/pages/components/RecycleOrderDetail.vue` - 添加等待确认提示
    - `docs/40-dev-guide/recycle-order-price-confirmation.md` - 详细技术文档
    - `docs/QUICK-START-PRICE-CONFIRMATION.md` - 快速开始指南
  - 验证方式：提交订单→填写物流信息→管理员收货质检→用户确认价格→管理员打款，检查每个环节的状态流转是否正确

## 2025-12-13

> 📋 **变更单**: [2025-12-13-admin-ui-fixes.md](../maintenance/changes/2025-12-13-admin-ui-fixes.md)

- **流程优化：简化回收订单状态流程**
  - 去掉"已估价"（quoted）和"已确认"（confirmed）状态
  - 用户提交订单后直接进入"已寄出"（shipped）状态
  - 新增"已收货"（received）状态，用于平台确认收货
  - 简化后的状态流程：pending -> shipped -> received -> inspected -> completed
  - 管理端添加"确认收货"功能，可将订单从"已寄出"更新为"已收货"
  - **修复流程进度显示逻辑**：修正流程步骤顺序（已寄出应在已收货之前），修正完成判断逻辑（根据实际状态判断，而不是索引比较），确保"已收货"只在状态为 received 或之后才显示为已完成
    - 修复 `isStepCompleted` 函数：从基于索引的比较改为基于实际状态的判断
    - 确保当订单状态为 `shipped` 时，"已收货"步骤不会显示为已完成
    - 只有当订单状态为 `received`、`inspected` 或 `completed` 时，"已收货"步骤才显示为已完成
  - 文件：
    - `backend/app/secondhand_app/models.py` - 更新 STATUS_CHOICES，去掉 quoted 和 confirmed，添加 received
    - `backend/app/secondhand_app/serializers.py` - 修改创建订单时的初始状态为 shipped，简化状态流转规则
    - `backend/app/admin_api/views.py` - 更新确认收货逻辑，支持从 shipped 到 received 的状态转换
    - `backend/app/secondhand_app/migrations/0022_*.py` - 数据库迁移
    - `frontend/src/admin/pages/InspectionOrders.vue` - 更新状态筛选和显示
    - `frontend/src/admin/pages/components/RecycleOrderDetail.vue` - 更新状态显示和操作按钮
    - `frontend/src/admin/pages/InspectionOrderDetail.vue` - 更新状态步骤显示
    - `frontend/src/admin/pages/RecycleOrderManagement.vue` - 更新状态筛选和显示，修复流程进度判断逻辑
    - `frontend/src/pages/RecycleOrderDetail.vue` - 更新用户端状态显示
    - `frontend/src/pages/MyRecycleOrders.vue` - 更新状态筛选
  - 验证方式：提交回收订单，检查状态是否为"已寄出"，流程进度中"已收货"不应显示为已完成；在管理端点击"确认收货"，检查状态是否更新为"已收货"，流程进度中"已收货"应显示为已完成；检查前端所有状态显示是否正确

- **功能实现：回收订单提交功能**
  - 实现提交订单API调用，创建回收订单
  - 添加订单数据验证（设备信息、存储容量、价格等）
  - 使用收款账户信息作为联系人信息（后续可优化为从用户资料获取）
  - 添加详细的错误处理和用户提示
  - 后端允许在创建订单时设置 `estimated_price`，并将订单状态初始化为 `shipped`（已寄出）
  - 文件：
    - `frontend/src/api/recycle.ts` - 添加 `createRecycleOrder` API函数和类型定义
    - `frontend/src/pages/RecycleCheckout.vue` - 实现 `handleSubmit` 函数，调用API创建订单
    - `backend/app/secondhand_app/serializers.py` - 修改 `RecycleOrderSerializer.create`，允许设置 `estimated_price` 和初始状态
  - 验证方式：完成问卷后进入提交订单页面，填写必要信息，点击"提交订单"，检查是否成功创建订单并跳转到"我的回收订单"页面；检查订单状态是否为"已估价"

- **Bug修复：提交订单页面价格显示问题**
  - 修复提交订单页面"预计到手价"显示为"--"的问题
  - 改进价格检查逻辑：检查价格是否为 null、undefined 或 0，而不仅仅是 null
  - 改进 onMounted 中的估价触发条件，放宽检查逻辑，确保有基本信息时就能触发估价
  - 添加详细的调试日志，便于排查问题
  - 在估价函数中添加价格有效性验证（必须大于0）
  - 文件：
    - `frontend/src/pages/RecycleCheckout.vue` - 改进 onMounted 逻辑，添加调试日志，改进价格显示判断
    - `frontend/src/pages/RecycleEstimateWizard.vue` - 改进估价函数，添加价格验证和调试日志
  - 验证方式：完成问卷后点击"提交订单"，检查价格是否正确显示；打开浏览器控制台查看调试日志；直接访问提交订单页面，检查是否自动触发估价并显示价格

- **功能完善：机型模板支持基础价格配置**
  - 在 `RecycleDeviceTemplate` 模型中添加 `base_prices` 字段（JSON格式），按存储容量存储基础价格
  - 估价API优先从机型模板获取基础价格，然后根据成色调整
  - 导入命令自动从 `LOCAL_PRICE_TABLE` 提取基础价格并写入模板
  - 前端显示报价明细：基础价格、成色调整、额外加价
  - **管理端支持编辑基础价格**：在机型模板编辑对话框中，可以为每个存储容量设置基础价格
  - 文件：
    - `backend/app/admin_api/models.py` - 添加 base_prices 字段
    - `backend/app/admin_api/serializers.py` - 更新序列化器包含 base_prices
    - `backend/app/admin_api/migrations/0005_*.py` - 数据库迁移
    - `backend/app/secondhand_app/views.py` - 修改估价API，优先使用模板基础价格
    - `backend/app/admin_api/management/commands/import_recycle_templates.py` - 导入时提取基础价格
    - `frontend/src/stores/recycleDraft.ts` - 添加 base_price 字段
    - `frontend/src/api/recycle.ts` - 更新API类型定义
    - `frontend/src/pages/RecycleEstimateWizard.vue` - 保存 base_price
    - `frontend/src/pages/RecycleCheckout.vue` - 显示报价明细
    - `frontend/src/admin/pages/RecycleTemplates.vue` - 添加基础价格编辑功能，表格显示基础价格
  - 验证方式：运行迁移，重新导入模板数据，检查模板是否包含基础价格；在管理端编辑机型模板，设置基础价格并保存；估价时检查是否优先使用模板价格；提交订单页面检查是否显示报价明细

- **UI优化：重新设计回收提交订单页面**
  - 删除产品图标表情符号
  - 删除拆机相关选项和说明（同意拆机复选框、拆机前需确认标签、拆机检测说明）
  - 删除价格反馈链接
  - 删除"无额外加价"提示（仅在有额外加价时显示）
  - 删除"顺丰上门"和"京东上门"邮寄方式，仅保留"自行邮寄"选项
  - 自行邮寄直接显示平台收件信息（收件人、收件地址），支持一键复制
  - 文件：
    - `frontend/src/pages/RecycleCheckout.vue` - 删除拆机相关代码，删除价格反馈和无额外加价提示，删除上门取件选项，简化邮寄方式显示
  - 验证方式：进入提交订单页面，检查拆机部分已删除，价格区域不显示反馈链接和无额外加价提示，邮寄方式仅显示平台收件信息

- **UI优化：重新设计回收提交订单页面（初始版本）**
  - 按照参考设计重新布局，主要显示订单信息、邮寄方式和收款信息
  - 订单信息区域：显示产品信息、预计到手价、价格反馈、拆机确认选项
  - 邮寄方式区域：提供顺丰上门、京东上门、自行邮寄三种选项，支持选择取件地址和时间
  - 收款信息区域：显示收款方式和账户信息，支持修改收款信息
  - 新增平台回收承担快递费用概览表格
  - 文件：
    - `frontend/src/pages/RecycleCheckout.vue` - 完全重写，采用新的布局和交互设计
  - 验证方式：进入回收提交订单页面，检查订单信息、邮寄方式选择、收款信息显示是否正常

- **修复：回收估价页面预计到手价显示时机**
  - 预计到手价卡片现在只在完成所有必填问题后才显示
  - 修复了在步骤1/13时就显示价格的问题
  - 文件：
    - `frontend/src/pages/RecycleEstimateWizard.vue` - 修改价格卡片显示条件为 `canCheckout && estimatedPriceText !== '--'`
  - 验证方式：进入回收估价页面，在未完成所有必填问题前，不应该显示预计到手价卡片

- **修复：管理端多标签页空白页面问题**
  - 添加 ErrorBoundary 组件，捕获组件渲染错误并显示友好的错误提示
  - 在 AppMain 中添加 Suspense 处理异步组件加载，显示加载骨架屏
  - 优化 keep-alive 配置，默认不缓存页面，避免多标签页切换时的状态混乱
  - 添加错误重试机制和返回首页功能
  - 文件：
    - `frontend/src/admin/layout/components/ErrorBoundary.vue` - 新增错误边界组件
    - `frontend/src/admin/layout/components/AppMain.vue` - 添加错误处理和加载状态
  - 验证方式：打开多个管理页面，切换标签页，应该不再出现空白页面；如果组件加载失败，会显示错误提示和重试按钮

- **UI优化：统一修复后台管理页面操作按钮布局**  
  > 详见变更单：影响13个管理页面
  - 所有表格的"操作"列按钮统一使用 `el-space wrap` 组件包装，确保按钮正确排列和自动换行
  - 修复了按钮重叠、挤压、布局混乱的问题
  - 调整了部分操作列的宽度以适应新的布局
  - 涉及页面：
    - `RecycleTemplates.vue` - 主表格、问卷表格、选项表格（3处）
    - `Shops.vue`, `Products.vue`, `Payments.vue`, `Categories.vue`
    - `FrontendUsers.vue`, `Users.vue`, `VerifiedOrdersAdmin.vue`
    - `VerifiedListings.vue`, `RecycledProducts.vue`, `AuditQueue.vue`
  - 验证方式：刷新后台管理页面，检查所有表格的操作列按钮是否整齐排列

- **修复：初始化机型模板数据**
  - 运行 `python manage.py import_recycle_templates` 从 `LOCAL_PRICE_TABLE` 导入所有机型数据
  - 成功导入 83 个机型模板、1008 个问卷问题、4332 个问卷选项
  - 删除前端硬编码的 `deviceCatalog.ts` 文件，所有数据现在完全来自后端
  - 文件：
    - `backend/app/admin_api/management/commands/import_recycle_templates.py` - 修复 Unicode 编码问题
    - `frontend/src/data/deviceCatalog.ts` - 已删除（不再使用）
  - 验证方式：刷新后台管理页面，应该能看到 83 个机型模板

- **功能优化：简化机型模板导入流程**
  - 新增"导出完整模板"功能，一键导出所有现有机型及其完整问卷配置
  - 简化导入逻辑：问卷配置按机型精确匹配（设备类型+品牌+型号），不再支持复杂的匹配优先级
  - 推荐流程：导出完整模板 → 在Excel中修改 → 重新导入，无需手动填写复杂的问卷配置
  - 文件：
    - `backend/app/admin_api/views.py` - 优化下载模板逻辑，支持导出现有机型；简化导入匹配逻辑
    - `frontend/src/admin/pages/RecycleTemplates.vue` - 新增"导出完整模板"按钮
    - `docs/40-dev-guide/recycle-template-management.md` - 更新使用说明，推荐导出→修改→导入流程
  - 验证方式：点击"导出完整模板"下载文件，修改后重新导入测试

- **功能增强：机型模板完整配置导入**
  - 扩展Excel模板格式，支持包含完整问卷配置的机型模板
  - Excel文件现在包含4个工作表：机型模板、问卷步骤、问卷选项、填写说明
  - 支持自定义问卷配置：如果提供了问卷步骤和选项工作表，会使用自定义配置创建完整问卷
  - 如果没有提供问卷配置，会使用默认13步问卷（向后兼容）
  - 导入时会为每个机型创建完整的问卷结构，包括所有问题和选项
  - 文件：
    - `backend/app/admin_api/views.py` - 更新下载模板和导入逻辑，支持多工作表解析
    - `docs/40-dev-guide/recycle-template-management.md` - 更新导入方式说明
  - 验证方式：下载模板，填写机型信息和问卷配置，上传测试完整导入功能

- **功能改进：机型模板导入方式优化**
  - 将"从价目表导入"改为"上传导入"功能，支持用户下载模板文件、编辑后上传批量导入
  - 新增下载模板API，生成Excel格式的模板文件（包含示例数据和填写说明）
  - 新增文件上传解析API，支持Excel(.xlsx/.xls)和CSV格式文件
  - 上传文件会自动解析并批量导入机型，为每个机型创建默认13步问卷
  - 文件：
    - `backend/app/admin_api/views.py` - 新增 `RecycleTemplateDownloadView` 和更新 `RecycleTemplateImportView`
    - `backend/app/admin_api/urls.py` - 添加下载模板路由
    - `frontend/src/admin/pages/RecycleTemplates.vue` - 更新UI，添加下载模板和上传导入按钮
    - `docs/40-dev-guide/recycle-template-management.md` - 更新导入方式说明
  - 验证方式：点击"下载模板"下载文件，编辑后点击"上传导入"测试批量导入功能

- **Bug修复：回收机型模板权限错误提示优化**
  - 优化权限检查错误提示，区分"未登录"（401）和"无权限"（403）两种情况
  - 更新权限文档，添加 `recycle_template` 相关权限说明
  - 所有回收模板相关接口现在会返回更清晰的错误信息
  - 文件：
    - `backend/app/admin_api/views.py` - 优化所有回收模板视图的权限检查
    - `docs/10-product/roles-permissions.md` - 添加回收模板权限说明
  - 验证方式：未登录时访问管理端应提示"未登录"，已登录但无权限时应提示具体需要的权限

## 2025-01-XX
- **Bug修复：回收机型模板管理功能修复**
  - 修复序列化器中 `queryset=None` 导致的 AssertionError，改为使用 `extra_kwargs` 和动态设置
  - 修复 `_build_catalog` 方法被错误放置在 `RecycleQuestionTemplateView` 类中的问题，导致 `/api/recycle-catalog/` 接口500错误
  - 修复创建问卷问题和选项时无法保存的问题，在视图中显式传递关联对象
  - 文件：
    - `backend/app/admin_api/serializers.py` - 修复序列化器字段定义
    - `backend/app/admin_api/views.py` - 修复保存逻辑
    - `backend/app/secondhand_app/views.py` - 修复方法位置
  - 验证方式：重启后端服务，测试创建问卷问题、选项功能，测试回收页面机型选择加载

## 2025-01-XX
- **功能验证：前端问卷内容加载机制检查**
  - 添加调试日志，检查问卷内容是否从后端加载
  - 修复 TypeScript 类型定义，添加 `storages` 字段
  - 优化错误处理，移除 TypeScript 类型注解（文件未启用 TypeScript）
  - 文件：
    - `frontend/src/pages/RecycleEstimateWizard.vue` - 添加调试日志
    - `frontend/src/api/recycle.ts` - 修复类型定义
  - 验证方式：打开浏览器控制台，访问回收问卷页面，查看日志确认数据来源

## 2025-01-XX
- **功能重构：回收机型目录和问卷改为从模板系统加载**
  - 修改 `/api/recycle-catalog/` 接口，优先从模板系统加载机型目录，无模板时从价目表加载（向后兼容）
  - 创建数据导入命令 `python manage.py import_recycle_templates`，从 LOCAL_PRICE_TABLE 导入所有机型数据
  - 导入命令自动为每个机型创建默认13步问卷（包含所有问题和选项）
  - 管理端添加"从价目表导入"按钮，支持通过API调用导入命令
  - 文件：
    - `backend/app/secondhand_app/views.py` - 修改 RecycleCatalogView，支持从模板加载
    - `backend/app/admin_api/management/commands/import_recycle_templates.py` - 新建导入命令
    - `backend/app/admin_api/views.py` - 新增导入API接口
    - `backend/app/admin_api/urls.py` - 添加导入路由
    - `frontend/src/admin/pages/RecycleTemplates.vue` - 添加导入按钮
  - 验证方式：
    1. 运行 `python manage.py import_recycle_templates` 导入数据
    2. 访问回收页面，检查机型选择是否正常加载
    3. 选择机型进入问卷，检查问卷内容是否正确
    4. 在管理端点击"从价目表导入"按钮测试导入功能

## 2025-01-XX
- **新功能：回收机型模板管理系统**
  - 后端：创建回收机型模板、问卷步骤、选项数据模型
  - 后端：创建管理端API接口（CRUD操作）
  - 后端：创建公开接口，根据机型获取问卷模板
  - 前端管理端：创建机型模板管理页面，支持新增/编辑机型、管理问卷步骤和选项
  - 前端用户端：修改问卷页面，优先从后端加载问卷内容，无模板时使用前端默认步骤
  - 文件：
    - `backend/app/admin_api/models.py` - 新增3个模型
    - `backend/app/admin_api/serializers.py` - 新增序列化器
    - `backend/app/admin_api/views.py` - 新增API视图
    - `backend/app/admin_api/urls.py` - 新增路由
    - `backend/app/secondhand_app/views.py` - 新增公开接口
    - `backend/core/urls.py` - 注册公开接口
    - `frontend/src/admin/pages/RecycleTemplates.vue` - 管理页面
    - `frontend/src/router/index.js` - 添加路由
    - `frontend/src/api/recycle.ts` - 新增API函数
    - `frontend/src/pages/RecycleEstimateWizard.vue` - 修改为从后端加载
  - 验证方式：
    1. 访问管理端 `/admin/recycle-templates`，创建机型模板和问卷
    2. 访问用户端回收问卷，检查是否从后端加载问卷内容
    3. 测试无模板时的fallback机制

## 2025-01-XX
- **功能优化：回收估价问卷交互改进**
  - 选择答案后自动跳转到下一个问题（单选问题）
  - 已回答的问题自动收起，显示问题和已选答案
  - 收起的问题显示"修改"按钮，点击可展开编辑
  - 展开已回答的问题时，不影响后面已回答的问题（它们保持收起状态）
  - 优化问题展示布局，提升用户体验
  - 文件：`frontend/src/pages/RecycleEstimateWizard.vue`
  - 验证方式：访问回收估价问卷，选择答案后检查是否自动跳转，已回答问题是否收起并显示修改按钮，展开已回答问题时检查后续已回答问题是否保持收起状态

## 2024-12-13
- 初始化：重建 docs/ 文档体系（以代码为准，建立变更流程与 API 参考）
