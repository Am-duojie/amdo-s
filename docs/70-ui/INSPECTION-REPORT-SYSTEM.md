# 质检报告系统完整文档

## 系统概述

质检报告系统为官方验货商品提供完整的质检信息展示和管理功能。系统包括前端展示组件、后端 API 接口和管理后台编辑功能。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端展示层                              │
│  InspectionReport.vue - 质检报告展示组件                   │
│  - 左侧：商品摘要卡片                                       │
│  - 右侧：检测详情（4大类，66项检测）                         │
│  - 异常高亮、图片查看、折叠展开                              │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTP GET
┌─────────────────────────────────────────────────────────┐
│                    后端 API 层                            │
│  GET /api/verified-products/{id}/inspection_report/      │
│  - 返回商品基本信息 (baseInfo)                             │
│  - 返回质检分类数据 (categories)                           │
│  - 支持自定义报告或默认模板                                 │
└─────────────────────────────────────────────────────────┘
                            ↓ 读取
┌─────────────────────────────────────────────────────────┐
│                    数据存储层                              │
│  VerifiedProduct.inspection_reports (JSONField)          │
│  - 存储完整的质检报告数据                                   │
│  - 支持自定义检测项和结果                                   │
└─────────────────────────────────────────────────────────┘
                            ↑ 编辑
┌─────────────────────────────────────────────────────────┐
│                    管理后台                                │
│  Django Admin / Django Shell                            │
│  - 可视化编辑质检报告                                       │
│  - 批量更新功能                                            │
└─────────────────────────────────────────────────────────┘
```

## 质检项目清单

### 1. 外观检测（12项）

| 检测项 | 说明 |
|--------|------|
| 碎裂 | 检查外壳是否有碎裂 |
| 划痕 | 检查外壳划痕情况 |
| 机身弯曲 | 检查机身是否弯曲变形 |
| 脱胶/缝隙 | 检查边框脱胶或缝隙 |
| 外壳/其他 | 其他外壳问题 |
| 磕碰 | 检查磕碰痕迹 |
| 刻字/图 | 检查是否有刻字或图案 |
| 掉漆/磨损 | 检查掉漆或磨损情况 |
| 摄像头/闪光灯外观 | 检查摄像头和闪光灯外观 |
| 褶皱 | 检查是否有褶皱 |
| 卡托 | 检查SIM卡托 |
| 音频网罩 | 检查扬声器网罩 |

### 2. 屏幕检测（16项）

#### 屏幕触控（1项）
- 触控

#### 屏幕外观（7项）
- 屏幕/其它
- 碎裂
- 内屏掉漆/划伤
- 屏幕凸点（褶皱）
- 支架破损
- 浅划痕
- 深划痕

#### 屏幕显示（8项）
- 进灰
- 坏点
- 气泡
- 色斑
- 其它
- 亮点/亮斑
- 泛红/泛黄
- 图文残影

### 3. 设备功能（30项）

#### 按键（4项）
- 电源键、音量键、静音键、其它按键

#### 生物识别（2项）
- 面部识别、指纹识别

#### 传感器（4项）
- 重力感应、指南针、距离感应、光线感应

#### 接口（2项）
- 充电接口、耳机接口

#### 无线（4项）
- WiFi、蓝牙、GPS、NFC

#### 充电（2项）
- 充电功能、无线充电

#### 通话功能（2项）
- 通话、信号

#### 声音与振动（3项）
- 扬声器、麦克风、振动

#### 摄像头（3项）
- 前置摄像头、后置摄像头、闪光灯

#### 其它状况（1项）
- 电池健康

### 4. 维修浸液（8项）

| 检测项 | 说明 |
|--------|------|
| 屏幕 | 检查屏幕是否维修更换 |
| 主板 | 检查主板是否维修 |
| 机身 | 检查机身是否维修更换 |
| 零件维修/更换 | 检查零件维修更换情况 |
| 零件缺失 | 检查是否有零件缺失 |
| 后摄维修情况 | 检查后置摄像头维修情况 |
| 前摄维修情况 | 检查前置摄像头维修情况 |
| 浸液痕迹情况 | 检查是否有浸液痕迹 |

**备注**: 拆机检测 - 平台未拆机检测

## 数据结构

### API 响应格式

```json
{
  "baseInfo": {
    "model": "Apple iPhone 14 Pro Max",
    "level": "外观 99新",
    "spec": "256GB",
    "color": "深空黑",
    "price": "6899.00",
    "coverImage": "https://example.com/image.jpg"
  },
  "categories": [
    {
      "title": "外观检测",
      "images": ["url1", "url2"],
      "groups": [
        {
          "name": "外壳外观",
          "items": [
            {
              "label": "碎裂",
              "value": "无",
              "pass": true
            },
            {
              "label": "划痕",
              "value": "明显划痕",
              "pass": false,
              "image": "https://example.com/scratch.jpg"
            }
          ]
        }
      ]
    }
  ]
}
```

### 数据库存储格式

在 `VerifiedProduct` 模型中，`inspection_reports` 字段（JSONField）存储完整的质检报告数据：

```python
product.inspection_reports = [
    {
        'title': '外观检测',
        'images': ['url1', 'url2'],
        'groups': [
            {
                'name': '外壳外观',
                'items': [
                    {'label': '碎裂', 'value': '无', 'pass': True},
                    {'label': '划痕', 'value': '明显划痕', 'pass': False, 'image': 'url'}
                ]
            }
        ]
    }
]
```

## 使用指南

### 前端使用

```vue
<template>
  <InspectionReport :product-id="196" />
</template>

<script setup>
import InspectionReport from '@/components/InspectionReport.vue'
</script>
```

### 后端 API 调用

```bash
# 获取商品质检报告
curl http://localhost:8000/api/verified-products/196/inspection_report/
```

### 管理后台编辑

#### 方法1：Django Shell

```bash
cd backend
python manage.py shell
```

```python
from app.secondhand_app.models import VerifiedProduct

product = VerifiedProduct.objects.get(id=196)
product.inspection_reports = [
    # ... 质检报告数据
]
product.save()
```

#### 方法2：Django Admin

1. 访问 http://localhost:8000/admin/
2. 找到 **官方验货商品**
3. 编辑商品的 **Inspection reports** 字段

## 文件清单

### 前端文件
- `frontend/src/components/InspectionReport.vue` - 质检报告展示组件
- `frontend/src/pages/VerifiedProductDetail.vue` - 商品详情页（集成质检报告）

### 后端文件
- `backend/app/secondhand_app/models.py` - VerifiedProduct 模型
- `backend/app/secondhand_app/views.py` - inspection_report API 端点
- `backend/app/secondhand_app/serializers.py` - VerifiedProductSerializer

### 文档文件
- `docs/30-api/inspection-report-api.md` - API 文档
- `docs/40-dev-guide/admin-inspection-report.md` - 管理后台编辑指南
- `docs/70-ui/inspection-report-component.md` - 组件使用文档
- `docs/70-ui/INSPECTION-REPORT-SYSTEM.md` - 系统完整文档（本文件）

## 功能特性

### 已实现功能

✅ 前端质检报告展示组件
✅ 后端 API 接口
✅ 从数据库动态获取质检数据
✅ 支持自定义质检报告
✅ 默认质检报告模板（66项检测）
✅ 异常项红色高亮
✅ 异常图片查看功能
✅ 可折叠的分类卡片
✅ 全部展开/收起功能
✅ 响应式设计

### 待改进功能

⏳ 可视化的质检报告编辑界面
⏳ 质检报告模板管理
⏳ 批量编辑功能
⏳ 图片上传和管理
⏳ 质检报告导出（PDF）
⏳ 质检报告打印功能

## 注意事项

1. **数据格式**: 必须严格遵循 JSON 格式
2. **pass 字段**: 必须是布尔值（true/false）
3. **异常图片**: 只有当 `pass=false` 时才需要提供 `image` 字段
4. **默认模板**: 如果商品没有自定义质检报告，API 会返回默认模板（所有项目均为"正常"）
5. **图片URL**: 建议使用完整的 URL 路径

## 常见问题

### Q: 如何添加新的检测项？

A: 在管理后台编辑 `inspection_reports` 字段，在对应的 `groups` 中添加新的 `items`。

### Q: 如何批量更新质检报告？

A: 使用 Django Shell 编写脚本批量更新：

```python
from app.secondhand_app.models import VerifiedProduct

template = [...]  # 质检报告模板
products = VerifiedProduct.objects.filter(status='active')
for product in products:
    product.inspection_reports = template
    product.save()
```

### Q: 如何自定义检测分类？

A: 在 `inspection_reports` 数组中添加新的分类对象，包含 `title`、`images`、`groups` 等字段。

### Q: 异常图片如何上传？

A: 目前需要先上传图片到服务器或图床，然后在质检报告中填写图片 URL。未来会提供图片上传功能。

## 更新日志

### 2025-12-14
- ✅ 创建 InspectionReport 组件
- ✅ 实现后端 API 接口
- ✅ 添加默认质检报告模板（66项检测）
- ✅ 集成到商品详情页
- ✅ 编写完整文档

## 相关文档

- [API 文档](../30-api/inspection-report-api.md)
- [管理后台编辑指南](../40-dev-guide/admin-inspection-report.md)
- [组件使用文档](./inspection-report-component.md)
- [UI 设计系统](./ui-design-system.md)
