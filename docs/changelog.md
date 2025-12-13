# 变更记录（Changelog）

## 2025-12-13

> 📋 **变更单**: [2025-12-13-admin-ui-fixes.md](../maintenance/changes/2025-12-13-admin-ui-fixes.md)

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
