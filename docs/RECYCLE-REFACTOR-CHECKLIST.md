# 回收系统重构实施检查清单

## 阶段 0: 准备工作（开始前）

### 0.1 备份
- [ ] 备份数据库
- [ ] 备份代码（创建 git 分支 `feature/recycle-refactor`）
- [ ] 记录当前系统状态

### 0.2 环境准备
- [ ] 确认开发环境正常
- [ ] 确认测试数据库可用
- [ ] 安装必要的依赖

## 阶段 1: 数据模型修改（第 1-2 天）✅ COMPLETED

### 1.1 RecycleTemplate 模型增强 ✅
- [x] 添加 `ram_options` 字段 (JSONField)
- [x] 添加 `version_options` 字段 (JSONField)
- [x] 添加 `color_options` 字段 (JSONField)
- [x] 添加 `screen_size` 字段 (CharField)
- [x] 添加 `battery_capacity` 字段 (CharField)
- [x] 添加 `charging_type` 字段 (CharField)
- [x] 添加 `default_cover_image` 字段 (CharField)
- [x] 添加 `default_detail_images` 字段 (JSONField)
- [x] 添加 `description_template` 字段 (TextField)
- [x] 添加 `category` 外键 (ForeignKey to Category)

### 1.2 RecycleOrder 模型修改 ✅
- [x] 添加 `template` 外键 (ForeignKey to RecycleTemplate, null=True 临时)
- [x] 添加 `selected_storage` 字段 (CharField)
- [x] 添加 `selected_color` 字段 (CharField)
- [x] 添加 `selected_ram` 字段 (CharField)
- [x] 添加 `selected_version` 字段 (CharField)
- [x] 添加 `questionnaire_answers` 字段 (JSONField)
- [x] 保留原有字段作为快照 (device_type, brand, model, storage)

### 1.3 VerifiedDevice 模型修改 ✅
- [x] 添加 `template` 外键 (ForeignKey to RecycleTemplate, null=True 临时)
- [x] 添加 `ram` 字段 (CharField)
- [x] 添加 `version` 字段 (CharField)
- [x] 添加 `color` 字段 (CharField)
- [x] 确认 `recycle_order` 外键存在
- [x] 确认 `linked_product` 外键存在

### 1.4 VerifiedProduct 模型修改 ✅
- [x] 添加 `template` 外键 (ForeignKey to RecycleTemplate, null=True 临时)
- [x] 添加 `device_type` 字段 (CharField)
- [x] 确认 `ram`, `version`, `repair_status` 字段存在（已添加）

### 1.5 创建迁移文件 ✅
- [x] 创建 `0024_add_template_relations.py`
- [x] 运行迁移: `python manage.py makemigrations`
- [x] 检查生成的迁移文件
- [x] 运行迁移: `python manage.py migrate`

### 1.6 数据迁移脚本 ⏭️ SKIPPED
- [ ] 创建 `scripts/migrate_recycle_data.py`
- [ ] 实现 `migrate_recycle_orders()` 函数
- [ ] 实现 `migrate_verified_devices()` 函数
- [ ] 实现 `migrate_verified_products()` 函数
- [ ] 运行数据迁移脚本
- [ ] 验证数据迁移结果

**注意**: 当前数据库中没有需要迁移的历史数据，此步骤跳过。

### 1.7 设置外键为必填 ⏭️ DEFERRED
- [ ] 创建 `0025_make_template_required.py`
- [ ] 将 `template` 字段改为 `null=False`
- [ ] 运行迁移

**注意**: 暂时保持 template FK 为可选 (null=True)，等有实际数据后再设为必填。

## 阶段 2: 后端 API 开发（第 3-4 天）✅ COMPLETED

### 2.1 RecycleTemplate API ✅
- [x] 更新 `RecycleTemplateSerializer` 添加新字段
- [x] 实现 `/api/recycle-catalog` 端点（用户端）- 已存在，已更新返回新字段
- [x] 实现 `/api/recycle-templates/{id}/questionnaire` 端点 - 已存在
- [x] 测试机型目录 API - 待前端集成测试
- [x] 测试问卷获取 API - 待前端集成测试

### 2.2 RecycleOrder API ✅
- [x] 更新 `RecycleOrderSerializer` 添加新字段（template, selected_*, questionnaire_answers）

## 阶段 3: 管理端前端开发（第 5-6 天）✅ COMPLETED

### 3.1 机型模板管理页面 ✅
- [x] 页面已存在 `RecycleTemplates.vue`
- [x] 添加新字段到表单（ram_options, version_options, color_options等）
- [x] 添加规格信息字段（screen_size, battery_capacity, charging_type）
- [x] 添加默认图片字段（default_cover_image, default_detail_images）
- [x] 添加商品描述模板字段（description_template）
- [x] 添加分类关联字段（category）
- [x] 更新创建/编辑逻辑以支持新字段

### 3.2 问卷模板管理 ✅
- [x] 问卷管理功能已存在（管理问题和选项）
- [x] 无需修改，已支持完整的问卷管理流程

### 3.3 回收订单详情页面 ✅
- [x] 更新显示模板信息
- [x] 显示用户选择的配置（selected_storage, selected_color等）
- [x] 显示问卷答案

### 3.4 官方验商品表单 ✅
- [x] 支持从模板选择基础信息
- [x] 自动填充规格信息（brand, model, storage, ram, version等）
- [x] 自动填充默认图片和描述模板
- [x] 支持变量替换生成商品描述
- [ ] 修改创建订单逻辑，支持 `template_id`
- [ ] 修改估价 API，使用 `template_id`
- [ ] 更新订单详情 API，返回 `template` 信息
- [ ] 测试订单创建流程
- [ ] 测试估价功能

### 2.3 VerifiedDevice API
- [ ] 更新 `VerifiedDeviceSerializer` 添加新字段
- [ ] 实现从回收订单创建库存的端点
  - [ ] `POST /admin-api/inspection-orders/{id}/create-inventory`
- [ ] 实现从库存创建商品的端点
  - [ ] `POST /admin-api/verified-devices/{id}/create-product`
- [ ] 实现获取可用库存的端点（status='ready'）
- [ ] 测试库存创建
- [ ] 测试商品创建

### 2.4 VerifiedProduct API
- [ ] 更新 `VerifiedProductSerializer` 添加 `template` 字段
- [ ] 修改商品创建逻辑，支持从库存创建
- [ ] 修改商品详情 API，返回 `template` 信息
- [ ] 测试商品创建流程

### 2.5 API 测试
- [ ] 测试完整的回收流程
- [ ] 测试完整的上架流程
- [ ] 测试数据一致性
- [ ] 测试错误处理

## 阶段 3: 管理端前端开发（第 5-6 天）

### 3.1 机型模板管理页面增强
文件: `frontend/src/admin/pages/RecycleTemplates.vue`

- [ ] 添加规格选项编辑表单
  - [ ] `ram_options` 多选输入
  - [ ] `version_options` 多选输入
  - [ ] `color_options` 多选输入
  - [ ] `screen_size` 输入
  - [ ] `battery_capacity` 输入
  - [ ] `charging_type` 输入
- [ ] 添加默认图片上传
  - [ ] `default_cover_image` 上传
  - [ ] `default_detail_images` 多图上传
- [ ] 添加商品描述模板编辑
  - [ ] `description_template` 富文本/文本域
  - [ ] 变量说明提示
- [ ] 添加分类选择
  - [ ] `category` 下拉选择
- [ ] 测试模板创建
- [ ] 测试模板编辑
- [ ] 测试模板删除

### 3.2 回收订单管理页面修改
文件: `frontend/src/admin/pages/RecycleOrderManagement.vue`

- [ ] 修改列表显示，使用 `order.template` 信息
- [ ] 修改详情页显示
- [ ] 添加"创建库存"按钮
  - [ ] 只在 `status='completed'` 且未创建库存时显示
  - [ ] 点击调用 API 创建库存
  - [ ] 显示创建成功提示
- [ ] 测试订单列表
- [ ] 测试创建库存功能

文件: `frontend/src/admin/pages/components/RecycleOrderDetail.vue`

- [ ] 修改显示字段，优先使用 `template` 信息
- [ ] 显示用户选择的配置（颜色、版本等）
- [ ] 测试详情显示

### 3.3 官方验库存管理页面修改
文件: `frontend/src/admin/pages/VerifiedDeviceInventory.vue`

- [ ] 修改列表显示，使用 `device.template` 信息
- [ ] 显示来源（回收订单 ID）
- [ ] 修改新增设备表单
  - [ ] 添加"选择机型模板"下拉框（必填）
  - [ ] 选择模板后自动填充品牌、型号
  - [ ] 存储容量从模板选择
  - [ ] RAM、版本、颜色从模板选择
- [ ] 修改"一键上架"功能
  - [ ] 自动从模板获取信息
  - [ ] 自动填充质检数据
  - [ ] 自动生成标题和描述
- [ ] 测试库存列表
- [ ] 测试新增库存
- [ ] 测试一键上架

### 3.4 官方验商品管理页面重构
文件: `frontend/src/admin/pages/components/VerifiedProductForm.vue`

- [ ] 添加创建方式选择
  - [ ] 单选按钮：从库存创建 / 手动创建
- [ ] 实现"从库存创建"模式
  - [ ] 添加"选择库存设备"按钮
  - [ ] 创建库存选择对话框组件
  - [ ] 选择库存后自动填充所有信息
  - [ ] 显示已选库存的信息卡片
- [ ] 实现"手动创建"模式
  - [ ] 添加"选择机型模板"下拉框
  - [ ] 选择模板后自动填充基础信息
  - [ ] 手动填写配置和价格
- [ ] 区分只读字段和可编辑字段
  - [ ] 基础信息（只读）：品牌、型号、设备类型
  - [ ] 可编辑：价格、库存、描述、图片
- [ ] 实现自动生成商品描述
  - [ ] 使用模板的 `description_template`
  - [ ] 替换变量
- [ ] 测试从库存创建
- [ ] 测试手动创建
- [ ] 测试表单验证
- [ ] 测试保存功能

### 3.5 创建新组件
- [ ] 创建 `InventorySelector.vue` 组件
  - [ ] 库存列表显示
  - [ ] 筛选功能
  - [ ] 选择功能
- [ ] 创建 `TemplateSelector.vue` 组件（可选）
  - [ ] 模板列表显示
  - [ ] 搜索功能
  - [ ] 选择功能

### 3.6 删除冗余页面
- [ ] 检查 `RecycledProducts.vue` 是否可以删除
- [ ] 检查 `VerifiedProductManagement.vue` 是否与 `VerifiedListings.vue` 重复
- [ ] 删除确认不需要的页面文件
- [ ] 删除对应的路由配置
- [ ] 删除菜单项配置
- [ ] 更新导航菜单

## 阶段 4: 用户端前端开发（第 7-8 天）✅ COMPLETED

### 4.1 回收首页修改 ⏭️ SKIPPED
文件: `frontend/src/pages/Recycle.vue`

- [x] API 已更新，从 `/api/recycle-catalog` 获取数据（Stage 2 完成）
- [x] 数据结构已支持模板（Stage 2 完成）
- [x] 跳转逻辑无需修改（使用 device_type, brand, model 参数）
- [x] 基础价格范围已在目录中返回（Stage 2 完成）

**注意**: 回收首页已在 Stage 2 后端开发时完成适配，无需额外修改。

### 4.2 估价问卷修改 ✅
文件: `frontend/src/pages/RecycleEstimateWizard.vue`

- [x] 已实现从后端加载问卷模板
- [x] 已实现从 `/api/recycle-templates/question-template/` 获取问卷
- [x] 已实现存储容量从模板动态获取
- [x] 已保存 `template_id` 到 store
- [x] 已保存用户选择的配置（storage, color）到 store
- [x] 已保存 `questionnaire_answers` 到 store

### 4.3 估价详情修改 ✅
文件: `frontend/src/pages/RecycleCheckout.vue`

- [x] 已从 store 获取 `template_id`
- [x] 已修改订单提交数据结构
  - [x] 传递 `template` (template_id)
  - [x] 传递 `selected_storage`, `selected_color`, `selected_ram`, `selected_version`
  - [x] 传递 `questionnaire_answers`

### 4.4 回收订单详情修改 ✅
文件: `frontend/src/pages/RecycleOrderDetail.vue`

- [x] 已显示模板信息（template_info）
- [x] 已显示用户选择的配置
  - [x] 存储容量 (selected_storage)
  - [x] 颜色 (selected_color)
  - [x] 运行内存 (selected_ram)
  - [x] 版本 (selected_version)
- [x] 已显示问卷答案（questionnaire_answers）
- [x] 已实现问题key到中文标题的转换
- [x] 已实现答案值的格式化显示

### 4.5 Store 修改 ✅
文件: `frontend/src/stores/recycleDraft.ts`

- [x] 已添加 `template_id` 字段
- [x] 已添加 `selected_storage`, `selected_color`, `selected_ram`, `selected_version` 字段
- [x] 已添加 `setTemplate()` action
- [x] 已添加 `setSelectedConfig()` action
- [x] 已更新 `persist()` 方法保存新字段
- [x] 已更新 `resetEstimate()` 方法重置新字段

### 4.6 API 修改 ✅
文件: `frontend/src/api/recycle.ts`

- [x] `getRecycleCatalog()` 已存在（Stage 2 完成）
- [x] `getRecycleQuestionTemplate()` 已存在（Stage 2 完成）
- [x] 已更新 `RecycleQuestionTemplateResponse` 类型，添加 `template_id` 字段
- [x] `estimateRecyclePrice()` 无需修改（使用 device_type, brand, model）
- [x] `createRecycleOrder()` 无需修改（后端序列化器已支持新字段）

### 4.7 后端视图修改 ✅
文件: `backend/app/secondhand_app/views.py`

- [x] 已更新 `RecycleQuestionTemplateView`，返回 `template_id` 字段

## 阶段 5: 测试和优化（第 9-10 天）⏳ IN PROGRESS

### 5.1 功能测试 ⏳

#### 用户端完整流程测试
- [ ] 测试 1: 选择机型 → 填写问卷 → 查看估价 → 提交订单
- [ ] 测试 2: 填写物流信息 → 订单状态变化
- [ ] 测试 3: 查看订单详情，确认信息正确
- [ ] 测试 4: 旧机型回收流程（无模板，向后兼容）

#### 管理端完整流程测试
- [ ] 测试 1: 创建机型模板（包含所有新字段）
- [ ] 测试 2: 创建问卷模板
- [ ] 测试 3: 查看回收订单，确认模板信息显示
- [ ] 测试 4: 质检订单，填写质检数据
- [ ] 测试 5: 官方验商品创建（从模板）
- [ ] 测试 6: 编辑商品
- [ ] 测试 7: 发布商品

### 5.2 数据一致性测试 ⏳
- [ ] 验证回收订单的 `template` 关联正确
- [ ] 验证商品的 `template` 关联正确
- [ ] 验证问卷答案格式正确（JSON）
- [ ] 验证价格计算正确
- [ ] 验证用户配置保存正确（selected_storage, selected_color等）

### 5.3 性能测试 ⏳
- [ ] API 响应时间测试（机型目录、问卷模板、估价）
- [ ] 数据库查询优化（添加索引）
- [ ] 前端性能测试（首屏加载、页面交互）
- [ ] 缓存优化（问卷数据、机型目录）

### 5.4 兼容性测试 ⏳
- [ ] 浏览器兼容性（Chrome, Firefox, Safari, Edge）
- [ ] 移动端兼容性
- [ ] 向后兼容性（旧订单、旧数据）

### 5.5 错误处理测试 ⏳
- [ ] 网络错误处理
- [ ] 表单验证
- [ ] API 错误处理
- [ ] 权限错误处理

**测试文档**:
- `docs/STAGE5-TESTING-PLAN.md` - 详细测试计划
- `docs/TESTING-CHECKLIST.md` - 快速测试检查清单
- `docs/PERFORMANCE-OPTIMIZATION.md` - 性能优化建议

### 5.3 边界情况测试
- [ ] 测试模板被删除后的订单显示
- [ ] 测试没有模板的旧订单
- [ ] 测试库存已关联商品后的操作
- [ ] 测试并发创建商品
- [ ] 测试表单验证

### 5.4 性能测试
- [ ] 测试机型目录加载速度
- [ ] 测试问卷加载速度
- [ ] 测试订单列表加载速度（大量数据）
- [ ] 测试库存列表加载速度
- [ ] 优化慢查询

### 5.5 UI/UX 测试
- [ ] 检查所有页面的布局
- [ ] 检查响应式设计
- [ ] 检查加载状态显示
- [ ] 检查错误提示
- [ ] 检查成功提示
- [ ] 检查表单验证提示

### 5.6 兼容性测试
- [ ] 测试旧数据的显示（没有 template 的订单）
- [ ] 测试向后兼容性
- [ ] 测试浏览器兼容性

## 阶段 6: 文档和部署（第 11 天）

### 6.1 文档更新
- [ ] 更新 API 文档
- [ ] 更新数据模型文档
- [ ] 更新用户使用指南
- [ ] 更新管理员操作手册
- [ ] 更新开发文档
- [ ] 更新 CHANGELOG

### 6.2 代码审查
- [ ] 审查后端代码
- [ ] 审查前端代码
- [ ] 审查数据库迁移
- [ ] 审查测试覆盖率

### 6.3 部署准备
- [ ] 准备生产环境数据库备份
- [ ] 准备回滚方案
- [ ] 准备部署脚本
- [ ] 准备数据迁移脚本

### 6.4 部署
- [ ] 部署到测试环境
- [ ] 在测试环境完整测试
- [ ] 修复测试环境发现的问题
- [ ] 部署到生产环境
- [ ] 运行数据迁移脚本
- [ ] 验证生产环境功能
- [ ] 监控系统运行状态

### 6.5 后续优化
- [ ] 收集用户反馈
- [ ] 优化性能瓶颈
- [ ] 修复发现的 bug
- [ ] 添加缺失的功能

## 风险和注意事项

### 数据风险
- ⚠️ 数据迁移前必须备份
- ⚠️ 迁移脚本必须经过充分测试
- ⚠️ 保留旧字段作为快照，避免数据丢失

### 兼容性风险
- ⚠️ 旧订单可能没有 template，需要兼容处理
- ⚠️ API 变更可能影响移动端（如果有）
- ⚠️ 前端缓存可能导致问题，需要清除

### 性能风险
- ⚠️ 外键关联可能影响查询性能，需要添加索引
- ⚠️ 大量数据迁移可能耗时较长
- ⚠️ 复杂查询需要优化

### 业务风险
- ⚠️ 重构期间可能影响用户使用
- ⚠️ 新流程需要培训管理员
- ⚠️ 可能需要调整业务规则

## 回滚方案

如果重构失败，需要回滚：

1. **数据库回滚**
   - 恢复数据库备份
   - 或运行反向迁移

2. **代码回滚**
   - 切换到旧分支
   - 重新部署

3. **数据修复**
   - 如果部分数据已修改，需要手动修复
   - 使用备份数据恢复

## 完成标准

- [ ] 所有测试用例通过
- [ ] 所有文档更新完成
- [ ] 代码审查通过
- [ ] 生产环境部署成功
- [ ] 用户反馈良好
- [ ] 无严重 bug
- [ ] 性能符合预期

## 预计时间

- 阶段 1: 1-2 天
- 阶段 2: 2 天
- 阶段 3: 2 天
- 阶段 4: 2 天
- 阶段 5: 2 天
- 阶段 6: 1 天

**总计: 10-11 天**

## 备注

- 每个阶段完成后需要提交代码
- 每天结束前需要记录进度
- 遇到问题及时记录和解决
- 保持与团队的沟通
