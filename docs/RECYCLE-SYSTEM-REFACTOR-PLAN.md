# 回收系统重构方案

## 当前问题分析

### 1. 数据流混乱
- **回收订单 (RecycleOrder)**: 直接存储 `device_type`, `brand`, `model`, `storage` 等字段
- **官方验商品 (VerifiedProduct)**: 也直接存储相同的字段
- **问题**: 没有统一的机型模板作为数据源，导致数据冗余和不一致

### 2. 业务流程不清晰
- 用户在回收界面看到的机型选项来自前端硬编码或临时API
- 回收订单的基础信息没有关联到机型模板
- 质检数据分散存储，没有统一管理
- 上架官方验商品时需要重新填写所有信息

### 3. 缺少核心数据模型
- 没有独立的"机型模板"表作为数据中心
- 回收订单、官方验商品、质检数据之间缺少关联

## 重构目标

建立以"机型模板"为核心的数据架构：

```
机型模板 (RecycleTemplate)
    ↓
用户回收订单 (RecycleOrder) → 质检数据 → 官方验库存 (VerifiedDevice) → 官方验商品 (VerifiedProduct)
```

## 详细方案

### 一、数据模型重构

#### 1. 机型模板 (RecycleTemplate) - 已存在，需增强

**当前字段**:
```python
class RecycleTemplate(models.Model):
    device_type = models.CharField(max_length=50)  # 手机、平板、笔记本
    brand = models.CharField(max_length=50)  # 苹果、华为
    model = models.CharField(max_length=100)  # iPhone 13
    series = models.CharField(max_length=50, blank=True)  # Pro Max
    storages = models.JSONField(default=list)  # ["128GB", "256GB"]
    base_prices = models.JSONField(default=dict)  # {"128GB": 4500, "256GB": 5200}
    is_active = models.BooleanField(default=True)
```

**需要新增的字段**:
```python
# 规格信息（用于前端展示和官方验商品）
ram_options = models.JSONField(default=list)  # ["6GB", "8GB"]
version_options = models.JSONField(default=list)  # ["国行", "港版"]
color_options = models.JSONField(default=list)  # ["黑色", "白色"]
screen_size = models.CharField(max_length=20, blank=True)  # "6.1英寸"
battery_capacity = models.CharField(max_length=20, blank=True)  # "3095mAh"
charging_type = models.CharField(max_length=50, blank=True)  # "Lightning"

# 默认图片（用于官方验商品）
default_cover_image = models.CharField(max_length=500, blank=True)
default_detail_images = models.JSONField(default=list)

# 商品描述模板
description_template = models.TextField(blank=True)  # 用于生成官方验商品描述

# 分类关联
category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
```

#### 2. 回收订单 (RecycleOrder) - 需修改

**修改方案**:
```python
class RecycleOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 核心关联：关联到机型模板
    template = models.ForeignKey(
        RecycleTemplate, 
        on_delete=models.PROTECT,  # 保护：不允许删除已有订单的模板
        related_name='recycle_orders',
        verbose_name='机型模板'
    )
    
    # 用户选择的具体配置（从模板的选项中选择）
    selected_storage = models.CharField(max_length=50)  # 从 template.storages 中选择
    selected_color = models.CharField(max_length=50, blank=True)  # 从 template.color_options 中选择
    selected_ram = models.CharField(max_length=20, blank=True)  # 从 template.ram_options 中选择
    selected_version = models.CharField(max_length=50, blank=True)  # 从 template.version_options 中选择
    
    # 保留原有字段作为快照（避免模板修改后影响历史订单）
    device_type = models.CharField(max_length=50)  # 从 template 复制
    brand = models.CharField(max_length=50)  # 从 template 复制
    model = models.CharField(max_length=100)  # 从 template 复制
    storage = models.CharField(max_length=50)  # = selected_storage
    
    # 估价相关
    condition = models.CharField(max_length=20)  # 用户问卷得出的成色
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # 问卷答案（JSON格式存储）
    questionnaire_answers = models.JSONField(default=dict)  # 存储用户的所有问卷答案
    
    # 质检数据（66项检测）
    inspection_reports = models.JSONField(default=list)  # 详细质检数据
    inspection_result = models.CharField(max_length=10, default='pass')
    inspection_date = models.DateField(null=True, blank=True)
    inspection_staff = models.CharField(max_length=100, blank=True)
    
    # 其他字段保持不变...
    status = models.CharField(max_length=20)
    contact_name = models.CharField(max_length=50)
    contact_phone = models.CharField(max_length=20)
    # ...
```

#### 3. 官方验库存 (VerifiedDevice) - 需修改

```python
class VerifiedDevice(models.Model):
    # 来源关联
    recycle_order = models.ForeignKey(
        RecycleOrder, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_devices'
    )
    
    # 机型模板关联（必填）
    template = models.ForeignKey(
        RecycleTemplate,
        on_delete=models.PROTECT,
        related_name='verified_devices',
        verbose_name='机型模板'
    )
    
    # 具体配置（从回收订单或手动输入）
    storage = models.CharField(max_length=50)
    ram = models.CharField(max_length=20, blank=True)
    version = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    
    # 设备唯一标识
    sn = models.CharField(max_length=100, unique=True)
    imei = models.CharField(max_length=100, blank=True)
    
    # 质检数据（从回收订单继承或重新质检）
    inspection_reports = models.JSONField(default=list)
    inspection_result = models.CharField(max_length=10, default='pass')
    battery_health = models.CharField(max_length=20, blank=True)
    
    # 库存管理
    status = models.CharField(max_length=20)  # pending, ready, listed, sold
    location = models.CharField(max_length=100, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # 关联的商品
    linked_product = models.ForeignKey(
        'VerifiedProduct',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='devices'
    )
    
    # 其他字段...
```

#### 4. 官方验商品 (VerifiedProduct) - 需修改

```python
class VerifiedProduct(models.Model):
    # 机型模板关联（必填）
    template = models.ForeignKey(
        RecycleTemplate,
        on_delete=models.PROTECT,
        related_name='verified_products',
        verbose_name='机型模板'
    )
    
    # 商品基本信息（从模板自动填充）
    title = models.CharField(max_length=200)  # 自动生成：品牌 + 型号 + 存储
    brand = models.CharField(max_length=50)  # 从 template 复制
    model = models.CharField(max_length=100)  # 从 template 复制
    device_type = models.CharField(max_length=50)  # 从 template 复制
    
    # 具体配置
    storage = models.CharField(max_length=50)
    ram = models.CharField(max_length=20, blank=True)
    version = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    
    # 价格和库存
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    stock = models.IntegerField(default=1)
    
    # 成色和质检
    condition = models.CharField(max_length=20)
    repair_status = models.CharField(max_length=100, blank=True)
    
    # 质检数据（从关联的 VerifiedDevice 继承）
    inspection_reports = models.JSONField(default=list)
    inspection_result = models.CharField(max_length=10, default='pass')
    
    # 媒体（从模板继承或自定义）
    cover_image = models.CharField(max_length=500, blank=True)
    detail_images = models.JSONField(default=list)
    
    # 商品描述（从模板生成或自定义）
    description = models.TextField()
    
    # 其他字段保持不变...
    status = models.CharField(max_length=20, default='draft')
    # ...
```

### 二、业务流程重构

#### 流程 1: 用户回收流程

```
1. 用户选择机型
   - 前端从 RecycleTemplate 获取可回收机型列表
   - 按 device_type → brand → model 层级展示
   
2. 用户填写估价问卷
   - 从 RecycleTemplate 关联的 RecycleQuestion 获取问卷
   - 用户选择存储容量（从 template.storages）
   - 用户回答问卷问题
   
3. 系统估价
   - 基于 template.base_prices[storage] 和用户成色计算
   - 创建 RecycleOrder，关联 template
   
4. 用户提交订单
   - 状态: pending
   - 保存 questionnaire_answers
   
5. 用户填写物流信息
   - 状态: pending → shipped
   
6. 平台收货
   - 管理员确认收货
   - 状态: shipped → received
   
7. 平台质检
   - 管理员填写 66 项质检数据
   - 保存到 order.inspection_reports
   - 设置 final_price
   - 状态: received → inspected
   
8. 用户确认价格
   - 用户确认或提出异议
   - 状态: inspected → completed
   
9. 平台打款
   - 管理员打款
   - payment_status: pending → paid
```

#### 流程 2: 官方验商品上架流程

```
1. 从回收订单创建库存
   - 回收订单完成后，自动或手动创建 VerifiedDevice
   - 继承回收订单的质检数据
   - 关联 template
   
2. 管理员选择库存上架
   - 在管理端"官方验库存"列表中选择设备
   - 点击"上架为商品"
   
3. 自动填充商品信息
   - 从 template 获取基础信息：
     * title = f"{template.brand} {template.model} {device.storage}"
     * brand, model, device_type 从 template 复制
     * description 从 template.description_template 生成
     * cover_image, detail_images 从 template 或 device 获取
   - 从 device 获取具体配置：
     * storage, ram, version, color
     * inspection_reports, condition
     * suggested_price → price
   
4. 管理员调整和发布
   - 可以修改价格、描述、图片
   - 点击"保存并上架"
   - 状态: draft → active
   
5. 关联库存
   - device.linked_product = product
   - device.status = 'listed'
```

### 三、API 接口设计

#### 1. 用户端 API

```python
# 获取可回收机型列表
GET /api/recycle-catalog
Response: {
  "手机": {
    "苹果": [
      {
        "id": 1,
        "model": "iPhone 13",
        "series": "Pro Max",
        "storages": ["128GB", "256GB", "512GB"],
        "base_prices": {"128GB": 4500, "256GB": 5200}
      }
    ]
  }
}

# 获取机型问卷
GET /api/recycle-templates/{id}/questionnaire
Response: {
  "template_id": 1,
  "brand": "苹果",
  "model": "iPhone 13",
  "storages": ["128GB", "256GB"],
  "questions": [...]
}

# 估价
POST /api/recycle/estimate
Request: {
  "template_id": 1,
  "storage": "256GB",
  "condition": "good",
  "questionnaire_answers": {...}
}
Response: {
  "estimated_price": 5200,
  "base_price": 5200,
  "bonus": 0
}

# 创建回收订单
POST /api/recycle-orders
Request: {
  "template_id": 1,
  "selected_storage": "256GB",
  "selected_color": "黑色",
  "condition": "good",
  "estimated_price": 5200,
  "questionnaire_answers": {...},
  "contact_name": "张三",
  "contact_phone": "13800138000",
  "address": "..."
}
```

#### 2. 管理端 API

```python
# 机型模板管理
GET /admin-api/recycle-templates
POST /admin-api/recycle-templates
PUT /admin-api/recycle-templates/{id}
DELETE /admin-api/recycle-templates/{id}

# 回收订单管理
GET /admin-api/inspection-orders
GET /admin-api/inspection-orders/{id}
PUT /admin-api/inspection-orders/{id}  # 质检、设置价格等

# 官方验库存管理
GET /admin-api/verified-devices
POST /admin-api/verified-devices  # 手动创建库存
PUT /admin-api/verified-devices/{id}
POST /admin-api/verified-devices/{id}/create-product  # 从库存创建商品

# 官方验商品管理
GET /admin-api/verified-listings
POST /admin-api/verified-listings
PUT /admin-api/verified-listings/{id}
POST /admin-api/verified-listings/{id}/publish
```

### 四、前端页面详细调整方案

#### 1. 用户端页面

##### 1.1 回收首页 (Recycle.vue) - 需修改
**当前状态**: 可能使用硬编码或临时数据
**修改内容**:
- API 调用: 从 `/api/recycle-catalog` 获取机型列表
- 数据结构: 按 `device_type → brand → model` 三级展示
- 显示内容: 每个机型显示基础价格范围
- 点击跳转: 跳转到估价问卷时传递 `template_id`

**代码变更**:
```javascript
// 修改前
const brands = ['苹果', '华为', '小米'] // 硬编码

// 修改后
const { data } = await api.get('/recycle-catalog')
const catalog = data // { "手机": { "苹果": [{ id, model, storages, base_prices }] } }
```

##### 1.2 估价问卷 (RecycleEstimateWizard.vue) - 需修改
**当前状态**: 使用前端固定的 13 步问卷或从后端获取
**修改内容**:
- 路由参数: 从 `?device_type=手机&brand=苹果&model=iPhone13` 改为 `?template_id=1`
- API 调用: 从 `/api/recycle-templates/{template_id}/questionnaire` 获取问卷
- 存储容量: 从 `template.storages` 动态获取，不再硬编码
- 提交数据: 保存 `template_id` 和 `questionnaire_answers`

**代码变更**:
```javascript
// 修改前
const route = useRoute()
const deviceType = route.query.device_type
const brand = route.query.brand
const model = route.query.model

// 修改后
const templateId = route.query.template_id
const { data } = await api.get(`/recycle-templates/${templateId}/questionnaire`)
const template = data.template
const questions = data.questions
const storages = data.storages
```

##### 1.3 估价详情 (RecycleCheckout.vue) - 需修改
**当前状态**: 显示用户选择的机型信息
**修改内容**:
- 数据来源: 从 draft store 中获取 `template_id`
- 显示内容: 显示模板的完整信息（品牌、型号、图片等）
- 提交订单: 传递 `template_id`, `selected_storage`, `questionnaire_answers`

**代码变更**:
```javascript
// 修改前
const orderData = {
  device_type: draft.device_type,
  brand: draft.brand,
  model: draft.model,
  storage: draft.storage,
  // ...
}

// 修改后
const orderData = {
  template_id: draft.template_id,
  selected_storage: draft.selected_storage,
  selected_color: draft.selected_color, // 新增
  questionnaire_answers: draft.answers,
  // ...
}
```

##### 1.4 回收订单详情 (RecycleOrderDetail.vue) - 需修改
**当前状态**: 显示订单的 device_type, brand, model 等字段
**修改内容**:
- 显示内容: 优先显示 `order.template` 的信息，如果没有则显示快照字段
- 新增显示: 显示用户选择的配置（颜色、版本等）

**代码变更**:
```vue
<!-- 修改前 -->
<div>{{ order.brand }} {{ order.model }} {{ order.storage }}</div>

<!-- 修改后 -->
<div>{{ order.template?.brand || order.brand }} {{ order.template?.model || order.model }}</div>
<div>存储: {{ order.selected_storage || order.storage }}</div>
<div v-if="order.selected_color">颜色: {{ order.selected_color }}</div>
<div v-if="order.selected_version">版本: {{ order.selected_version }}</div>
```

##### 1.5 不需要修改的用户端页面
- `MyRecycleOrders.vue` - 订单列表，只需确保显示字段正确
- `VerifiedProducts.vue` - 官方验商品列表，不受影响
- `VerifiedProductDetail.vue` - 商品详情，已经从后端获取数据

#### 2. 管理端页面

##### 2.1 机型模板管理 (RecycleTemplates.vue) - 需增强
**当前状态**: 已有基础的 CRUD 功能
**需要新增的功能**:

1. **规格选项编辑**
   - 添加 `ram_options` 字段（多选输入框）
   - 添加 `version_options` 字段（多选输入框）
   - 添加 `color_options` 字段（多选输入框）
   - 添加 `screen_size` 字段（单行输入）
   - 添加 `battery_capacity` 字段（单行输入）
   - 添加 `charging_type` 字段（单行输入）

2. **默认图片管理**
   - 添加 `default_cover_image` 上传
   - 添加 `default_detail_images` 多图上传

3. **商品描述模板**
   - 添加 `description_template` 富文本编辑器
   - 支持变量替换（如 `{brand}`, `{model}`, `{storage}`）

4. **分类关联**
   - 添加 `category` 下拉选择

**表单新增字段示例**:
```vue
<el-form-item label="运行内存选项">
  <el-select v-model="form.ram_options" multiple filterable allow-create>
    <el-option label="6GB" value="6GB" />
    <el-option label="8GB" value="8GB" />
    <el-option label="12GB" value="12GB" />
  </el-select>
</el-form-item>

<el-form-item label="版本选项">
  <el-select v-model="form.version_options" multiple filterable allow-create>
    <el-option label="国行" value="国行" />
    <el-option label="港版" value="港版" />
    <el-option label="美版" value="美版" />
  </el-select>
</el-form-item>

<el-form-item label="默认封面图">
  <el-upload
    :http-request="handleUploadCover"
    list-type="picture-card"
    :limit="1"
  >
    <el-icon><Plus /></el-icon>
  </el-upload>
</el-form-item>

<el-form-item label="商品描述模板">
  <el-input
    v-model="form.description_template"
    type="textarea"
    :rows="6"
    placeholder="支持变量: {brand} {model} {storage} {condition}"
  />
</el-form-item>
```

##### 2.2 回收订单管理 (RecycleOrderManagement.vue) - 需修改
**当前状态**: 显示订单列表和详情
**修改内容**:

1. **列表页显示**
   - 机型信息从 `order.template` 获取
   - 显示用户选择的配置

2. **详情页新增功能**
   - 在订单完成后，显示"创建库存"按钮
   - 点击后自动创建 `VerifiedDevice`，继承订单的质检数据

**代码变更**:
```vue
<!-- 列表页 -->
<el-table-column label="设备信息">
  <template #default="{ row }">
    <div>{{ row.template?.brand || row.brand }} {{ row.template?.model || row.model }}</div>
    <div>{{ row.selected_storage || row.storage }}</div>
  </template>
</el-table-column>

<!-- 详情页新增按钮 -->
<el-button
  v-if="order.status === 'completed' && !order.verified_devices?.length"
  type="success"
  @click="createInventory"
>
  创建库存
</el-button>
```

##### 2.3 官方验库存管理 (VerifiedDeviceInventory.vue) - 需修改
**当前状态**: 已有基础功能
**需要修改的内容**:

1. **列表页显示**
   - 显示 `template` 信息而不是直接字段
   - 显示来源（回收订单 ID）

2. **新增设备表单**
   - 添加"选择机型模板"下拉框（必填）
   - 选择模板后自动填充品牌、型号
   - 存储容量从模板的 `storages` 中选择
   - RAM、版本、颜色从模板的选项中选择

3. **一键上架功能增强**
   - 选择库存后，自动从模板获取商品信息
   - 自动填充质检数据
   - 自动生成商品标题和描述

**表单修改示例**:
```vue
<el-form-item label="机型模板" prop="template_id">
  <el-select
    v-model="deviceForm.template_id"
    placeholder="请选择机型模板"
    filterable
    @change="handleTemplateChange"
  >
    <el-option
      v-for="tpl in templates"
      :key="tpl.id"
      :label="`${tpl.brand} ${tpl.model}`"
      :value="tpl.id"
    />
  </el-select>
</el-form-item>

<el-form-item label="存储容量" v-if="selectedTemplate">
  <el-select v-model="deviceForm.storage">
    <el-option
      v-for="storage in selectedTemplate.storages"
      :key="storage"
      :label="storage"
      :value="storage"
    />
  </el-select>
</el-form-item>

<el-form-item label="运行内存" v-if="selectedTemplate?.ram_options?.length">
  <el-select v-model="deviceForm.ram">
    <el-option
      v-for="ram in selectedTemplate.ram_options"
      :key="ram"
      :label="ram"
      :value="ram"
    />
  </el-select>
</el-form-item>
```

##### 2.4 官方验商品管理 (VerifiedProductForm.vue) - 需大幅修改
**当前状态**: 手动填写所有字段
**修改后的流程**:

**方式一：从库存创建（推荐）**
1. 点击"从库存选择"按钮
2. 弹出库存列表对话框（只显示 status='ready' 的设备）
3. 选择一个库存设备
4. 自动填充所有信息：
   - 从 `device.template` 获取: brand, model, device_type, category
   - 从 `device` 获取: storage, ram, version, color, condition
   - 从 `device` 获取: inspection_reports, inspection_result
   - 从 `device` 获取: suggested_price → price
   - 从 `template` 获取: default_cover_image, default_detail_images
   - 从 `template.description_template` 生成 description
5. 管理员可以调整价格、描述、图片
6. 保存时自动关联 `device.linked_product = product.id`

**方式二：手动创建（保留）**
1. 选择机型模板
2. 自动填充模板信息
3. 手动填写配置和价格
4. 不关联库存设备

**表单结构**:
```vue
<template>
  <el-form :model="form" ref="formRef">
    <!-- 创建方式选择 -->
    <el-radio-group v-model="createMode" @change="handleModeChange">
      <el-radio label="from-inventory">从库存创建（推荐）</el-radio>
      <el-radio label="manual">手动创建</el-radio>
    </el-radio-group>

    <!-- 从库存创建 -->
    <div v-if="createMode === 'from-inventory'">
      <el-button @click="openInventorySelector">选择库存设备</el-button>
      <div v-if="selectedDevice" class="selected-device-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="设备">
            {{ selectedDevice.brand }} {{ selectedDevice.model }}
          </el-descriptions-item>
          <el-descriptions-item label="SN">
            {{ selectedDevice.sn }}
          </el-descriptions-item>
          <el-descriptions-item label="配置">
            {{ selectedDevice.storage }} / {{ selectedDevice.ram }} / {{ selectedDevice.version }}
          </el-descriptions-item>
          <el-descriptions-item label="成色">
            {{ selectedDevice.condition }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>

    <!-- 手动创建 -->
    <div v-if="createMode === 'manual'">
      <el-form-item label="机型模板" prop="template_id">
        <el-select
          v-model="form.template_id"
          @change="handleTemplateSelect"
        >
          <el-option
            v-for="tpl in templates"
            :key="tpl.id"
            :label="`${tpl.brand} ${tpl.model}`"
            :value="tpl.id"
          />
        </el-select>
      </el-form-item>
    </div>

    <!-- 自动填充的基础信息（只读） -->
    <el-card shadow="never" class="auto-filled-section">
      <template #header>基础信息（自动填充）</template>
      <el-form-item label="商品标题">
        <el-input v-model="form.title" readonly />
      </el-form-item>
      <el-form-item label="品牌">
        <el-input v-model="form.brand" readonly />
      </el-form-item>
      <el-form-item label="型号">
        <el-input v-model="form.model" readonly />
      </el-form-item>
      <!-- ... 其他只读字段 -->
    </el-card>

    <!-- 可编辑的字段 -->
    <el-card shadow="never">
      <template #header>价格和库存</template>
      <el-form-item label="售价" prop="price">
        <el-input-number v-model="form.price" :min="0.01" :precision="2" />
      </el-form-item>
      <el-form-item label="原价">
        <el-input-number v-model="form.original_price" :min="0" :precision="2" />
      </el-form-item>
      <el-form-item label="库存">
        <el-input-number v-model="form.stock" :min="1" />
      </el-form-item>
    </el-card>

    <!-- 商品描述（可编辑） -->
    <el-card shadow="never">
      <template #header>商品描述</template>
      <el-form-item>
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="6"
        />
      </el-form-item>
    </el-card>

    <!-- 图片（可编辑） -->
    <el-card shadow="never">
      <template #header>商品图片</template>
      <!-- 图片上传组件 -->
    </el-card>

    <!-- 质检报告（只读，从库存继承） -->
    <el-card shadow="never" v-if="form.inspection_reports?.length">
      <template #header>质检报告（继承自库存）</template>
      <!-- 显示质检数据 -->
    </el-card>
  </el-form>
</template>

<script setup>
const createMode = ref('from-inventory')
const selectedDevice = ref(null)
const templates = ref([])

const openInventorySelector = () => {
  // 打开库存选择对话框
  inventorySelectorVisible.value = true
}

const handleDeviceSelect = (device) => {
  selectedDevice.value = device
  // 自动填充表单
  fillFormFromDevice(device)
}

const fillFormFromDevice = (device) => {
  const template = device.template
  
  // 自动生成标题
  form.title = `${template.brand} ${template.model} ${device.storage} ${device.condition}`
  
  // 从模板填充
  form.brand = template.brand
  form.model = template.model
  form.device_type = template.device_type
  form.category_id = template.category_id
  
  // 从设备填充
  form.storage = device.storage
  form.ram = device.ram
  form.version = device.version
  form.color = device.color
  form.condition = device.condition
  form.repair_status = device.repair_status
  
  // 价格
  form.price = device.suggested_price || template.base_prices[device.storage]
  
  // 质检数据
  form.inspection_reports = device.inspection_reports
  form.inspection_result = device.inspection_result
  
  // 图片
  form.cover_image = device.cover_image || template.default_cover_image
  form.detail_images = device.detail_images?.length ? device.detail_images : template.default_detail_images
  
  // 描述（使用模板生成）
  form.description = generateDescription(template, device)
}

const generateDescription = (template, device) => {
  let desc = template.description_template || ''
  desc = desc.replace('{brand}', template.brand)
  desc = desc.replace('{model}', template.model)
  desc = desc.replace('{storage}', device.storage)
  desc = desc.replace('{condition}', device.condition)
  desc = desc.replace('{ram}', device.ram || '')
  desc = desc.replace('{version}', device.version || '')
  return desc
}
</script>
```

##### 2.5 需要删除或合并的管理端页面

**删除的页面**:
- `RecycledProducts.vue` - 功能重复，已被 `VerifiedDeviceInventory.vue` 替代
- `VerifiedProductManagement.vue` - 如果与 `VerifiedListings.vue` 功能重复

**保留但需要更新的页面**:
- `VerifiedListings.vue` - 商品列表，显示字段需要更新
- `VerifiedOrderManagement.vue` - 订单管理，不受影响

##### 2.6 不需要修改的管理端页面
- `AdminDashboard.vue` - 仪表板
- `Categories.vue` - 分类管理
- `FrontendUsers.vue` - 用户管理
- `Shops.vue` - 店铺管理
- `Statistics.vue` - 统计
- 其他通用管理页面

#### 3. 前端路由调整

**需要修改的路由**:
```javascript
// router/index.js

// 用户端
{
  path: '/recycle/estimate',
  component: RecycleEstimateWizard,
  // 修改前: ?device_type=手机&brand=苹果&model=iPhone13
  // 修改后: ?template_id=1
}

// 管理端 - 删除重复路由
// 删除: /admin/recycled-products (如果存在)
// 保留: /admin/verified-devices
```

#### 4. 前端 Store 调整

**RecycleDraft Store** - 需修改
```javascript
// stores/recycleDraft.js

export const useRecycleDraftStore = defineStore('recycleDraft', {
  state: () => ({
    // 修改前
    device_type: '',
    brand: '',
    model: '',
    storage: '',
    
    // 修改后
    template_id: null,
    template: null, // 存储完整的模板信息
    selected_storage: '',
    selected_color: '',
    selected_ram: '',
    selected_version: '',
    
    // 保持不变
    condition: '',
    estimated_price: null,
    answers: {},
  }),
  
  actions: {
    setTemplate(template) {
      this.template_id = template.id
      this.template = template
    },
    
    setSelectedConfig(config) {
      this.selected_storage = config.storage
      this.selected_color = config.color
      this.selected_ram = config.ram
      this.selected_version = config.version
    },
  }
})
```

#### 5. 前端 API 调整

**新增 API**:
```javascript
// api/recycle.js

// 获取回收目录
export const getRecycleCatalog = () => {
  return api.get('/recycle-catalog')
}

// 获取机型问卷
export const getRecycleQuestionnaire = (templateId) => {
  return api.get(`/recycle-templates/${templateId}/questionnaire`)
}

// 估价（修改参数）
export const estimateRecyclePrice = (params) => {
  return api.post('/recycle/estimate', {
    template_id: params.template_id,
    storage: params.storage,
    condition: params.condition,
    questionnaire_answers: params.questionnaire_answers
  })
}

// 创建回收订单（修改参数）
export const createRecycleOrder = (data) => {
  return api.post('/recycle-orders', {
    template_id: data.template_id,
    selected_storage: data.selected_storage,
    selected_color: data.selected_color,
    selected_ram: data.selected_ram,
    selected_version: data.selected_version,
    condition: data.condition,
    estimated_price: data.estimated_price,
    questionnaire_answers: data.questionnaire_answers,
    // ... 其他字段
  })
}
```

**管理端 API**:
```javascript
// utils/adminApi.js

// 机型模板
export const getRecycleTemplates = (params) => {
  return adminApi.get('/recycle-templates', { params })
}

// 创建库存（从回收订单）
export const createInventoryFromOrder = (orderId) => {
  return adminApi.post(`/inspection-orders/${orderId}/create-inventory`)
}

// 获取可用库存（用于商品创建）
export const getAvailableDevices = (params) => {
  return adminApi.get('/verified-devices', {
    params: { status: 'ready', ...params }
  })
}

// 从库存创建商品
export const createProductFromDevice = (deviceId, data) => {
  return adminApi.post(`/verified-devices/${deviceId}/create-product`, data)
}
```

#### 6. 前端组件调整

**新增组件**:
- `InventorySelector.vue` - 库存选择器（用于商品创建）
- `TemplateSelector.vue` - 机型模板选择器（可复用）

**修改组件**:
- `RecycleOrderDetail.vue` - 显示模板信息
- `VerifiedProductForm.vue` - 大幅重构

#### 7. 前端页面删除清单

**确认删除的页面**:
1. `frontend/src/admin/pages/RecycledProducts.vue` - 功能已被 `VerifiedDeviceInventory.vue` 替代
2. 如果 `VerifiedProductManagement.vue` 与 `VerifiedListings.vue` 功能重复，删除其中一个

**删除步骤**:
1. 删除页面文件
2. 删除路由配置
3. 删除菜单项
4. 更新相关文档

### 五、数据迁移方案

#### 步骤 1: 创建新字段

```python
# 0024_add_template_fields.py
operations = [
    # RecycleTemplate 新增字段
    migrations.AddField('RecycleTemplate', 'ram_options', models.JSONField(default=list)),
    migrations.AddField('RecycleTemplate', 'version_options', models.JSONField(default=list)),
    migrations.AddField('RecycleTemplate', 'color_options', models.JSONField(default=list)),
    # ... 其他字段
    
    # RecycleOrder 新增字段
    migrations.AddField('RecycleOrder', 'template', models.ForeignKey(..., null=True)),
    migrations.AddField('RecycleOrder', 'selected_storage', models.CharField(..., blank=True)),
    migrations.AddField('RecycleOrder', 'questionnaire_answers', models.JSONField(default=dict)),
    
    # VerifiedDevice 新增字段
    migrations.AddField('VerifiedDevice', 'template', models.ForeignKey(..., null=True)),
    
    # VerifiedProduct 新增字段
    migrations.AddField('VerifiedProduct', 'template', models.ForeignKey(..., null=True)),
]
```

#### 步骤 2: 数据迁移脚本

```python
# scripts/migrate_recycle_data.py
def migrate_recycle_orders():
    """为现有回收订单关联机型模板"""
    for order in RecycleOrder.objects.filter(template__isnull=True):
        # 查找或创建对应的模板
        template, created = RecycleTemplate.objects.get_or_create(
            device_type=order.device_type,
            brand=order.brand,
            model=order.model,
            defaults={
                'storages': [order.storage] if order.storage else [],
                'base_prices': {},
                'is_active': True
            }
        )
        
        # 关联模板
        order.template = template
        order.selected_storage = order.storage
        order.save()

def migrate_verified_products():
    """为现有官方验商品关联机型模板"""
    for product in VerifiedProduct.objects.filter(template__isnull=True):
        template, created = RecycleTemplate.objects.get_or_create(
            device_type=product.device_type or '手机',
            brand=product.brand,
            model=product.model,
            defaults={
                'storages': [product.storage] if product.storage else [],
                'base_prices': {},
                'is_active': True
            }
        )
        
        product.template = template
        product.save()
```

#### 步骤 3: 设置外键为必填

```python
# 0025_make_template_required.py
operations = [
    migrations.AlterField('RecycleOrder', 'template', models.ForeignKey(..., null=False)),
    migrations.AlterField('VerifiedDevice', 'template', models.ForeignKey(..., null=False)),
    migrations.AlterField('VerifiedProduct', 'template', models.ForeignKey(..., null=False)),
]
```

### 六、实施步骤

#### 阶段 1: 数据模型准备（1-2天）
1. 创建数据库迁移文件
2. 增强 RecycleTemplate 模型
3. 修改 RecycleOrder, VerifiedDevice, VerifiedProduct 模型
4. 运行迁移和数据迁移脚本

#### 阶段 2: 后端 API 开发（2-3天）
1. 更新 RecycleTemplate 相关 API
2. 修改回收订单创建和估价 API
3. 开发官方验库存管理 API
4. 修改官方验商品创建 API

#### 阶段 3: 管理端开发（2-3天）
1. 增强机型模板管理页面
2. 修改回收订单详情页面
3. 创建官方验库存管理页面
4. 修改官方验商品表单

#### 阶段 4: 用户端开发（1-2天）
1. 修改回收首页机型选择
2. 更新估价问卷数据源
3. 调整订单提交逻辑

#### 阶段 5: 测试和优化（1-2天）
1. 完整流程测试
2. 数据一致性检查
3. 性能优化
4. 文档更新

### 七、预期效果

#### 1. 数据一致性
- 所有机型信息统一来源于 RecycleTemplate
- 避免数据冗余和不一致

#### 2. 业务流程清晰
- 回收 → 质检 → 库存 → 上架，每个环节职责明确
- 数据流向清晰，易于追溯

#### 3. 管理效率提升
- 机型模板统一管理，修改一处即可
- 上架商品时自动填充信息，减少重复劳动
- 质检数据自动继承，无需重复录入

#### 4. 扩展性增强
- 新增机型只需添加模板
- 问卷配置灵活，可按机型定制
- 支持批量导入机型数据

## 总结

这个重构方案的核心思想是：

1. **建立数据中心**: RecycleTemplate 作为所有机型数据的唯一来源
2. **明确数据流向**: 模板 → 订单 → 库存 → 商品
3. **减少数据冗余**: 通过外键关联而不是字段复制
4. **提升业务效率**: 自动填充、数据继承、流程自动化

实施后，整个回收和官方验系统将更加规范、高效、易维护。
