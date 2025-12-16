# 回收机型模板管理使用指南

## 概述

回收机型模板管理系统允许管理员在后台配置可回收的机型、品牌、问卷内容等，实现问卷内容的动态管理。

## 功能特性

1. **机型模板管理**
   - 新增/编辑/删除机型模板
   - 设置设备类型、品牌、型号、存储容量
   - 启用/禁用模板

2. **问卷步骤管理**
   - 为每个机型模板配置问卷步骤
   - 设置步骤顺序、问题标识、标题、类型（单选/多选）
   - 设置是否必填、是否启用

3. **问卷选项管理**
   - 为每个问题配置选项
   - 设置选项值、标签、描述
   - 设置对估价的影响（正面/轻微/重大/严重）
   - 设置选项顺序

## 数据模型

### RecycleDeviceTemplate（机型模板）
- `device_type`: 设备类型（手机、平板、笔记本等）
- `brand`: 品牌
- `model`: 型号
- `storages`: 存储容量列表（JSON数组）
- `series`: 系列（可选）
- `is_active`: 是否启用

### RecycleQuestionTemplate（问卷步骤模板）
- `device_template`: 关联的机型模板
- `step_order`: 步骤顺序（从1开始）
- `key`: 问题标识（唯一，如：channel, color, storage）
- `title`: 问题标题
- `helper`: 提示文本（可选）
- `question_type`: 问题类型（single/multi）
- `is_required`: 是否必填
- `is_active`: 是否启用

### RecycleQuestionOption（问卷选项）
- `question_template`: 关联的问题模板
- `value`: 选项值（唯一，如：official, black, 256GB）
- `label`: 选项标签（显示给用户）
- `desc`: 选项描述（可选）
- `impact`: 对估价的影响（positive/minor/major/critical）
- `option_order`: 选项顺序
- `is_active`: 是否启用

## API接口

### 管理端接口（需要管理员权限）

#### 机型模板
- `GET /admin-api/recycle-templates` - 获取模板列表
- `GET /admin-api/recycle-templates/<id>` - 获取模板详情
- `POST /admin-api/recycle-templates` - 创建模板
- `PUT /admin-api/recycle-templates/<id>` - 更新模板
- `DELETE /admin-api/recycle-templates/<id>` - 删除模板

#### 问卷步骤
- `GET /admin-api/recycle-templates/<template_id>/questions` - 获取问题列表
- `GET /admin-api/recycle-templates/<template_id>/questions/<question_id>` - 获取问题详情
- `POST /admin-api/recycle-templates/<template_id>/questions` - 创建问题
- `PUT /admin-api/recycle-templates/<template_id>/questions/<question_id>` - 更新问题
- `DELETE /admin-api/recycle-templates/<template_id>/questions/<question_id>` - 删除问题

#### 问卷选项
- `GET /admin-api/recycle-templates/<template_id>/questions/<question_id>/options` - 获取选项列表
- `GET /admin-api/recycle-templates/<template_id>/questions/<question_id>/options/<option_id>` - 获取选项详情
- `POST /admin-api/recycle-templates/<template_id>/questions/<question_id>/options` - 创建选项
- `PUT /admin-api/recycle-templates/<template_id>/questions/<question_id>/options/<option_id>` - 更新选项
- `DELETE /admin-api/recycle-templates/<template_id>/questions/<question_id>/options/<option_id>` - 删除选项

### 公开接口（用户端使用）

- `GET /api/recycle-templates/question-template/` - 根据机型获取问卷模板
  - 参数：`device_type`, `brand`, `model`
  - 返回：机型模板信息和完整的问卷步骤、选项

## 使用流程

### 1. 创建机型模板

1. 访问管理端：`/admin/recycle-templates`
2. 点击"新增模板"
3. 填写设备类型、品牌、型号、存储容量等信息
4. 保存

### 2. 配置问卷步骤

1. 在机型模板列表中，点击"管理问卷"
2. 点击"新增问题"
3. 设置步骤顺序、问题标识、标题、类型等
4. 保存

### 3. 配置问卷选项

1. 在问题列表中，点击"管理选项"
2. 点击"新增选项"
3. 设置选项值、标签、描述、影响等
4. 保存

### 4. 用户端使用

用户端问卷页面会自动：
1. 根据选择的机型，从后端加载对应的问卷模板
2. 如果后端有模板，使用后端数据
3. 如果后端没有模板，使用前端默认步骤（fallback机制）

## 字段说明（管理员必读）

### 问题标识（key）

**含义：** 系统内部识别问题的唯一代码，用于程序处理和数据分析。

**填写规范：**
- 使用英文小写字母
- 多个单词用下划线连接（推荐）或驼峰命名
- 建议使用有意义的英文单词

**示例：**
- `channel` - 购买渠道
- `color` - 颜色
- `storage` - 存储容量
- `screen_appearance` - 屏幕外观

**注意事项：**
- 同一机型模板内，问题标识必须唯一
- 建议使用标准的问题标识（如：channel, color, storage），便于系统识别和处理

### 选项值（value）

**含义：** 系统内部识别选项的唯一代码，用于程序处理和存储用户选择。

**填写规范：**
- 使用英文小写字母、数字
- 多个单词用下划线（`_`）或连字符（`-`）连接
- 对于存储容量，可以直接使用容量值（如：`256GB`）

**示例：**
- 购买渠道：`official`（官方/直营）、`operator`（运营商/合约）、`online`（第三方电商）
- 颜色：`black`（黑/深色）、`white`（白/浅色）、`blue`（蓝/紫/冷色）
- 存储容量：`256GB`、`512GB`、`1TB`（直接使用容量值）
- 使用情况：`unopened`（全新未拆封）、`light`（几乎全新）、`normal`（正常使用）

**注意事项：**
- 同一问题内，选项值必须唯一
- 建议保持一致性：如果"黑色"的选项值是`black`，其他机型也应该使用`black`
- 选项值会被存储到数据库，用于后续的数据分析和价格计算

### 选项标签（label）

**含义：** 显示给用户看的选项文本，用户友好、清晰易懂即可。

**填写规范：**
- 使用中文，清晰易懂
- 可以包含斜杠（`/`）表示多个含义
- 尽量简洁，避免过长

**示例：**
- "官方/直营"、"运营商/合约"
- "黑/深色"、"白/浅色"
- "256GB"、"512GB"
- "全新未拆封"、"几乎全新，使用很少"

### 对估价的影响（impact）

**含义：** 该选项对回收估价的影响程度，用于价格计算。

**选项说明：**
- **正面影响（positive）**：提升价格，如"全新未拆封"、"配件齐全"、"完美无瑕"
- **轻微影响（minor）**：略微影响价格，如"正常使用痕迹"、"有部分配件"
- **重大影响（major）**：显著降低价格，如"明显划痕"、"已维修"
- **严重影响（critical）**：大幅降低价格，如"碎裂"、"无法使用"、"主板维修"

**注意事项：**
- 此字段为可选，如果不设置，系统可能使用默认逻辑
- 建议根据实际情况设置，有助于更准确的估价

## 注意事项

1. **问题标识（key）必须唯一**：同一机型模板内，每个问题的key不能重复
2. **选项值（value）必须唯一**：同一问题内，每个选项的value不能重复
3. **步骤顺序**：建议从1开始，按顺序递增
4. **存储容量问题**：如果问题key为"storage"，选项会自动使用机型模板的storages字段
5. **启用状态**：只有启用的模板、问题、选项才会在用户端显示
6. **保持一致性**：建议在不同机型模板中使用相同的问题标识和选项值，便于数据分析和处理

## 权限要求

管理端页面需要以下权限：
- `recycle_template:view` - 查看
- `recycle_template:create` - 创建
- `recycle_template:update` - 更新
- `recycle_template:delete` - 删除

## 数据迁移

### 1. 数据库迁移

首次使用需要运行数据库迁移：
```bash
python manage.py migrate admin_api
```

### 2. 导入机型数据

#### 方式一：上传Excel/CSV文件导入（推荐）

**推荐流程：导出→修改→导入**

1. 在管理端页面点击"**导出完整模板**"按钮
   - 系统会导出所有现有机型及其完整问卷配置
   - 包含机型基础信息和所有问卷步骤、选项

2. 在Excel中修改数据：
   - 修改机型信息（设备类型、品牌、型号、存储容量等）
   - 修改问卷步骤（问题标题、选项等）
   - 添加新机型（复制现有行，修改机型信息）

3. 保存文件后，点击"**上传导入**"按钮，选择修改好的文件
4. 系统会自动解析并批量导入，每个机型使用自己的问卷配置

**或者使用空模板：**

1. 点击"**下载模板**"按钮，下载空模板文件
2. Excel文件包含多个工作表：
   - **机型模板**（必需）：填写机型基础信息
   - **问卷步骤**（可选）：自定义问卷问题配置
   - **问卷选项**（可选）：自定义问卷选项配置
   - **填写说明**：详细的使用说明

3. 填写数据：
   - **机型模板工作表**：
     - 设备类型：手机、平板、笔记本
     - 品牌：如苹果、华为、小米等
     - 型号：具体型号名称
     - 系列：可选，如"15系列"、"Pro系列"
     - 存储容量：多个容量用英文逗号分隔，如"128GB,256GB,512GB"
     - 是否启用：是/否
   
   - **问卷步骤工作表**（可选）：
     - 如果填写此工作表，导入时会使用此配置创建问卷，否则使用默认13步问卷
     - **设备类型、品牌、型号**：**必须填写**，用于指定该问卷配置适用于哪个机型
     - 步骤顺序：从1开始，控制问题显示顺序
     - 问题标识：唯一标识，如channel, color, storage
     - 问题标题：显示给用户的问题文本
     - 提示文本：辅助说明（可选）
     - 问题类型：single（单选）或multi（多选）
     - 是否必填：是/否
     - 是否启用：是/否
   
   - **问卷选项工作表**（可选）：
     - 如果填写问卷步骤，必须填写对应的选项
     - **设备类型、品牌、型号**：**必须填写**，对应机型模板中的机型
     - 问题标识：对应问卷步骤中的问题标识
     - 选项值：唯一标识，如official, black
     - 选项标签：显示给用户的文本
     - 选项描述：辅助说明（可选）
     - 对估价的影响：positive/minor/major/critical（可选）
     - 选项顺序：控制选项显示顺序
     - 是否启用：是/否

4. 保存文件后，点击"**上传导入**"按钮，选择填写好的文件
5. 系统会自动解析文件并批量导入：
   - 如果提供了问卷配置，会使用提供的配置创建完整问卷
   - 如果没有提供问卷配置，会使用默认13步问卷
   - 存储容量问题的选项会自动从机型模板的存储容量生成
   - **每个机型可以有自己独立的问卷配置**，实现个性化管理

**文件格式要求：**
- 支持 `.xlsx`、`.xls`、`.csv` 格式（CSV仅支持机型模板）
- Excel文件必须包含"机型模板"工作表
- 问卷步骤和问卷选项工作表为可选，如果提供则使用自定义配置
- 如果机型已存在，会更新存储容量和系列信息
- 如果提供了问卷配置，会替换现有问卷（如果存在）

#### 方式二：使用命令行导入（从LOCAL_PRICE_TABLE）

```bash
# 导入所有设备类型
python manage.py import_recycle_templates

# 只导入手机
python manage.py import_recycle_templates --device-type 手机

# 清空现有数据后重新导入
python manage.py import_recycle_templates --clear
```

### 3. 导入内容

导入命令会：
- 从 `LOCAL_PRICE_TABLE` 读取所有机型数据（设备类型、品牌、型号、存储容量）
- 为每个机型创建模板
- 为每个机型创建默认13步问卷（包含所有问题和选项）
- 存储容量问题会自动使用机型的存储容量列表

## 接口变更

### `/api/recycle-catalog/` 接口

该接口已修改为：
1. **优先从模板系统加载**：如果模板系统有数据，使用模板数据
2. **向后兼容**：如果模板系统没有数据，从 `LOCAL_PRICE_TABLE` 加载（保持原有行为）

这样可以平滑迁移，不影响现有功能。

## 兼容性

- 如果后端没有配置机型模板，接口会自动从 `LOCAL_PRICE_TABLE` 加载（向后兼容）
- 如果机型没有配置问卷模板，用户端会自动使用前端固定的默认问卷步骤
- 确保向后兼容，不影响现有功能












