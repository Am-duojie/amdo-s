# 质检报告 API 文档

## 概述

质检报告 API 提供官方验货商品的详细质检信息，包括外观检测、屏幕检测、设备功能和维修浸液等四大类检测项目。

## API 端点

### 获取质检报告

```
GET /api/verified-products/{id}/inspection_report/
```

获取指定官方验货商品的质检报告详情。

#### 请求参数

- `id` (路径参数): 商品ID

#### 响应示例

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
      "images": [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg"
      ],
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
    },
    {
      "title": "屏幕检测",
      "images": [],
      "groups": [
        {
          "name": "屏幕触控",
          "items": [
            {
              "label": "触控",
              "value": "正常",
              "pass": true
            }
          ]
        },
        {
          "name": "屏幕外观",
          "items": [
            {
              "label": "屏幕/其它",
              "value": "正常",
              "pass": true
            },
            {
              "label": "碎裂",
              "value": "无",
              "pass": true
            }
          ]
        },
        {
          "name": "屏幕显示",
          "items": [
            {
              "label": "进灰",
              "value": "无",
              "pass": true
            },
            {
              "label": "坏点",
              "value": "无",
              "pass": true
            }
          ]
        }
      ]
    },
    {
      "title": "设备功能",
      "images": [],
      "groups": [
        {
          "name": "按键",
          "items": [
            {
              "label": "电源键",
              "value": "正常",
              "pass": true
            }
          ]
        },
        {
          "name": "生物识别",
          "items": [
            {
              "label": "面部识别",
              "value": "正常",
              "pass": true
            }
          ]
        }
      ]
    },
    {
      "title": "维修浸液",
      "images": [],
      "groups": [
        {
          "name": "维修浸液",
          "items": [
            {
              "label": "屏幕",
              "value": "未检出维修更换",
              "pass": true
            },
            {
              "label": "主板",
              "value": "未检出维修",
              "pass": true
            }
          ]
        }
      ],
      "footer": {
        "label": "拆机检测",
        "value": "平台未拆机检测"
      }
    }
  ]
}
```

## 数据结构说明

### baseInfo 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| model | string | 设备型号 |
| level | string | 成色等级 |
| spec | string | 规格（存储容量） |
| color | string | 颜色 |
| price | string | 价格 |
| coverImage | string | 封面图URL |

### categories 数组

每个分类包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | 分类标题（外观检测、屏幕检测、设备功能、维修浸液） |
| images | array | 检测图片URL数组 |
| groups | array | 检测项分组数组 |
| footer | object | 底部备注（可选） |

### group 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 分组名称 |
| items | array | 检测项数组 |

### item 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| label | string | 检测项名称 |
| value | string | 检测结果 |
| pass | boolean | 是否通过（true=正常，false=异常） |
| image | string | 异常图片URL（可选，仅当pass=false时） |

## 质检项目清单

### 1. 外观检测（12项）

- 碎裂
- 划痕
- 机身弯曲
- 脱胶/缝隙
- 外壳/其他
- 磕碰
- 刻字/图
- 掉漆/磨损
- 摄像头/闪光灯外观
- 褶皱
- 卡托
- 音频网罩

### 2. 屏幕检测（16项）

**屏幕触控（1项）**
- 触控

**屏幕外观（7项）**
- 屏幕/其它
- 碎裂
- 内屏掉漆/划伤
- 屏幕凸点（褶皱）
- 支架破损
- 浅划痕
- 深划痕

**屏幕显示（8项）**
- 进灰
- 坏点
- 气泡
- 色斑
- 其它
- 亮点/亮斑
- 泛红/泛黄
- 图文残影

### 3. 设备功能（30项）

**按键（4项）**
- 电源键
- 音量键
- 静音键
- 其它按键

**生物识别（2项）**
- 面部识别
- 指纹识别

**传感器（4项）**
- 重力感应
- 指南针
- 距离感应
- 光线感应

**接口（2项）**
- 充电接口
- 耳机接口

**无线（4项）**
- WiFi
- 蓝牙
- GPS
- NFC

**充电（2项）**
- 充电功能
- 无线充电

**通话功能（2项）**
- 通话
- 信号

**声音与振动（3项）**
- 扬声器
- 麦克风
- 振动

**摄像头（3项）**
- 前置摄像头
- 后置摄像头
- 闪光灯

**其它状况（1项）**
- 电池健康

### 4. 维修浸液（8项）

- 屏幕
- 主板
- 机身
- 零件维修/更换
- 零件缺失
- 后摄维修情况
- 前摄维修情况
- 浸液痕迹情况

## 自定义质检报告

### 方法1：通过数据库直接设置

在 `VerifiedProduct` 模型中，`inspection_reports` 字段是一个 JSONField，可以存储完整的质检报告数据。

```python
product = VerifiedProduct.objects.get(id=1)
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
product.save()
```

### 方法2：通过管理后台编辑

在 Django Admin 中，可以直接编辑 `inspection_reports` 字段的 JSON 数据。

## 前端使用

```vue
<template>
  <InspectionReport :product-id="productId" />
</template>

<script setup>
import InspectionReport from '@/components/InspectionReport.vue'

const productId = 1
</script>
```

## 注意事项

1. 如果商品没有自定义质检报告数据，API 会返回默认的质检报告结构（所有项目均为"正常"/"无"）
2. 异常项（pass=false）会在前端以红色高亮显示，并提供"查看异常图"按钮
3. 质检报告数据存储在 `VerifiedProduct.inspection_reports` JSONField 中
4. 建议在管理后台提供可视化的质检报告编辑界面
