# Stage 2 完成总结 - 后端 API 开发

**完成时间**: 2025-12-15  
**状态**: ✅ 已完成

## 完成的工作

### 1. 更新 RecycleDeviceTemplate 序列化器

**文件**: `backend/app/admin_api/serializers.py`

#### RecycleDeviceTemplateSerializer (管理端)
添加了以下新字段到序列化器：
- `ram_options` - 运行内存选项列表
- `version_options` - 版本选项列表
- `color_options` - 颜色选项列表
- `screen_size` - 屏幕尺寸
- `battery_capacity` - 电池容量
- `charging_type` - 充电方式
- `default_cover_image` - 默认封面图
- `default_detail_images` - 默认详情图列表
- `description_template` - 商品描述模板
- `category` / `category_name` - 分类信息

#### RecycleDeviceTemplateListSerializer (管理端列表)
同样添加了新字段，用于管理端列表展示。

### 2. 创建用户端序列化器

**文件**: `backend/app/secondhand_app/serializers.py`

新增了以下序列化器：

#### RecycleQuestionOptionPublicSerializer
用于序列化问卷选项（用户端）
- `value` - 选项值
- `label` - 选项标签
- `desc` - 选项描述
- `impact` - 对估价的影响

#### RecycleQuestionPublicSerializer
用于序列化问卷问题（用户端）
- `key` - 问题标识
- `title` - 问题标题
- `helper` - 提示文本
- `question_type` - 问题类型（单选/多选）
- `is_required` - 是否必填
- `options` - 选项列表

#### RecycleDeviceTemplateCatalogSerializer
用于机型目录列表展示（用户端）
- 基本信息：id, device_type, brand, model, series
- 配置选项：storages, base_prices
- 规格信息：screen_size, battery_capacity, charging_type
- 媒体：default_cover_image

#### RecycleDeviceTemplateDetailSerializer
用于机型详情展示（用户端）
- 包含所有字段，包括 ram_options, version_options, color_options
- 完整的规格和媒体信息

### 3. 更新 RecycleOrder 序列化器

**文件**: `backend/app/secondhand_app/serializers.py`

#### RecycleOrderSerializer
添加了以下新字段：
- `template` - 关联的机型模板 ID
- `template_info` - 模板基本信息（SerializerMethodField）
- `selected_storage` - 用户选择的存储容量
- `selected_color` - 用户选择的颜色
- `selected_ram` - 用户选择的运行内存
- `selected_version` - 用户选择的版本
- `questionnaire_answers` - 问卷答案（JSON格式）

### 4. 更新机型目录 API

**文件**: `backend/app/secondhand_app/views.py`

#### RecycleCatalogView
- **端点**: `GET /api/recycle-catalog`
- **状态**: 已存在，已更新
- **更新内容**: 在返回的机型列表中添加了新字段
  - `id` - 模板 ID
  - `base_prices` - 基础价格表
  - `ram_options` - 运行内存选项
  - `version_options` - 版本选项
  - `color_options` - 颜色选项
  - `screen_size` - 屏幕尺寸
  - `battery_capacity` - 电池容量
  - `charging_type` - 充电方式
  - `default_cover_image` - 默认封面图

**返回数据结构**:
```json
{
  "device_types": ["手机", "平板"],
  "brands": {
    "手机": ["苹果", "华为", "小米"]
  },
  "models": {
    "手机": {
      "苹果": [
        {
          "id": 1,
          "name": "iPhone 13",
          "storages": ["128GB", "256GB", "512GB"],
          "series": "iPhone 13系列",
          "base_prices": {"128GB": 4500, "256GB": 5200, "512GB": 6500},
          "ram_options": ["4GB", "6GB"],
          "version_options": ["国行", "港版"],
          "color_options": ["黑色", "白色", "蓝色"],
          "screen_size": "6.1英寸",
          "battery_capacity": "3095mAh",
          "charging_type": "Lightning",
          "default_cover_image": "/media/..."
        }
      ]
    }
  }
}
```

### 5. 问卷 API

**端点**: `GET /api/recycle-templates/{id}/questionnaire`
**状态**: 已存在，无需修改
**功能**: 获取指定机型模板的问卷问题和选项

### 6. RecycleOrder API 更新

**端点**: `POST /api/recycle-orders/`
**更新**: RecycleOrderSerializer 已支持新字段
**提交数据示例**:
```json
{
  "template": 1,
  "device_type": "手机",
  "brand": "苹果",
  "model": "iPhone 13",
  "storage": "256GB",
  "selected_storage": "256GB",
  "selected_color": "黑色",
  "selected_ram": "6GB",
  "selected_version": "国行",
  "questionnaire_answers": {
    "channel": "official",
    "color": "black",
    "storage": "256GB",
    "screen_condition": "perfect",
    "battery_health": "90"
  },
  "condition": "good",
  "estimated_price": 5200,
  "contact_name": "张三",
  "contact_phone": "13800138000",
  "address": "北京市朝阳区xxx"
}
```

## API 端点总结

### 用户端 API

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/recycle-catalog` | GET | 获取机型目录 | ✅ 已更新 |
| `/api/recycle-templates/{id}/questionnaire` | GET | 获取问卷 | ✅ 已存在 |
| `/api/recycle-orders/` | POST | 创建回收订单 | ✅ 已更新 |
| `/api/recycle-orders/` | GET | 获取订单列表 | ✅ 已更新 |
| `/api/recycle-orders/{id}/` | GET | 获取订单详情 | ✅ 已更新 |
| `/api/recycle-orders/{id}/inspection_report` | GET | 获取质检报告 | ✅ 已存在 |
| `/api/recycle-orders/{id}/confirm_final_price` | POST | 确认最终价格 | ✅ 已存在 |
| `/api/recycle-orders/estimate` | POST | 估价接口 | ✅ 已存在 |

### 管理端 API

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/admin-api/recycle-templates/` | GET | 模板列表 | ✅ 已更新 |
| `/admin-api/recycle-templates/` | POST | 创建模板 | ✅ 已更新 |
| `/admin-api/recycle-templates/{id}/` | GET | 模板详情 | ✅ 已更新 |
| `/admin-api/recycle-templates/{id}/` | PUT | 更新模板 | ✅ 已更新 |
| `/admin-api/inspection-orders/` | GET | 回收订单列表 | ✅ 已存在 |
| `/admin-api/inspection-orders/{id}/` | GET | 订单详情 | ✅ 已存在 |
| `/admin-api/inspection-orders/{id}/` | PUT | 更新订单状态 | ✅ 已存在 |
| `/admin-api/inspection-orders/{id}/` | POST | 提交质检报告 | ✅ 已存在 |
| `/admin-api/inspection-orders/{id}/price` | PUT | 更新价格 | ✅ 已存在 |
| `/admin-api/inspection-orders/{id}/payment` | POST | 打款 | ✅ 已存在 |

## 数据流验证

### 用户提交回收订单流程

1. **获取机型目录**
   ```
   GET /api/recycle-catalog?device_type=手机&brand=苹果
   ```
   返回包含新字段的机型列表

2. **获取问卷**
   ```
   GET /api/recycle-templates/1/questionnaire
   ```
   返回问卷问题和选项

3. **提交订单**
   ```
   POST /api/recycle-orders/
   {
     "template": 1,
     "selected_storage": "256GB",
     "selected_color": "黑色",
     "questionnaire_answers": {...},
     ...
   }
   ```
   创建订单，关联到模板

4. **查看订单**
   ```
   GET /api/recycle-orders/123/
   ```
   返回包含 template_info 的订单详情

## 向后兼容性

所有新字段都设置为可选（blank=True, null=True），确保：
- 旧的订单数据不受影响
- 不使用模板的订单仍然可以正常创建
- 前端可以渐进式升级

## 测试建议

### 1. 机型目录 API 测试
```bash
# 测试获取所有机型
curl http://localhost:8000/api/recycle-catalog

# 测试筛选
curl http://localhost:8000/api/recycle-catalog?device_type=手机&brand=苹果

# 测试搜索
curl http://localhost:8000/api/recycle-catalog?q=iPhone
```

### 2. 问卷 API 测试
```bash
# 获取指定模板的问卷
curl http://localhost:8000/api/recycle-templates/1/questionnaire
```

### 3. 订单创建测试
```bash
# 使用模板创建订单
curl -X POST http://localhost:8000/api/recycle-orders/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "template": 1,
    "device_type": "手机",
    "brand": "苹果",
    "model": "iPhone 13",
    "selected_storage": "256GB",
    "selected_color": "黑色",
    "questionnaire_answers": {},
    "contact_name": "测试",
    "contact_phone": "13800138000",
    "address": "测试地址"
  }'
```

## 下一步工作

根据 `docs/RECYCLE-REFACTOR-CHECKLIST.md`，下一阶段是：

**阶段 3: 管理端前端开发（第 5-6 天）**

主要任务：
1. 创建机型模板管理页面
2. 创建问卷模板管理页面
3. 更新回收订单详情页面，显示模板信息
4. 更新官方验商品表单，支持从模板选择

## 文件修改清单

### 序列化器文件
- `backend/app/admin_api/serializers.py` - 更新管理端序列化器
- `backend/app/secondhand_app/serializers.py` - 更新用户端序列化器，添加新序列化器

### 视图文件
- `backend/app/secondhand_app/views.py` - 更新 RecycleCatalogView

### 文档文件
- `docs/RECYCLE-REFACTOR-CHECKLIST.md` - 更新进度
- `docs/STAGE2-COMPLETION-SUMMARY.md` - 本文档

## 验证清单

- [x] 所有序列化器已更新
- [x] 机型目录 API 返回新字段
- [x] RecycleOrder 序列化器支持新字段
- [x] 向后兼容性保持
- [ ] API 测试（待前端集成时测试）
- [ ] 文档已更新

## 备注

Stage 2 的核心目标是更新后端 API 以支持模板化回收流程。所有必要的序列化器和视图都已更新，API 已准备好供前端使用。由于很多端点已经存在（如 catalog 和 questionnaire），主要工作是添加新字段到序列化器中。
