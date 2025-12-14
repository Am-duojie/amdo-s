# InspectionReport 验机评估报告组件

## 概述

`InspectionReport` 是一个专业的验机评估报告组件，用于展示官翻商品的详细检测结果。组件采用"官方专业版"的高级设计风格，支持异常高亮、图片查看等交互功能。

## 特性

✅ **专业设计** - 高级感的视觉风格，包含阴影、圆角、渐变等细节
✅ **异常高亮** - 自动标红检测不通过的项目
✅ **图片查看** - 点击查看异常部位的证据图片
✅ **数据驱动** - 从后端 API 动态获取质检数据
✅ **响应式** - 自动适配移动端和桌面端
✅ **可折叠** - 支持展开/收起检测分类
✅ **完整质检项** - 包含外观、屏幕、功能、维修浸液四大类共66项检测

## 使用方法

### 基础用法

```vue
<template>
  <InspectionReport :product-id="productId" />
</template>

<script setup>
import InspectionReport from '@/components/InspectionReport.vue'

const productId = 123
</script>
```

### 传入数据

```vue
<template>
  <InspectionReport :report-data-prop="reportData" />
</template>

<script setup>
import { ref } from 'vue'
import InspectionReport from '@/components/InspectionReport.vue'

const reportData = ref({
  baseInfo: {
    model: 'iPhone 12 Pro Max',
    level: '外观 99新',
    spec: '256G',
    color: '海蓝色',
    price: '3,850',
    coverImage: 'https://example.com/cover.jpg'
  },
  categories: [
    // ... 检测分类数据
  ]
})
</script>
```

## Props

| 参数 | 说明 | 类型 | 必填 | 默认值 |
|------|------|------|------|--------|
| productId | 商品ID，用于获取报告数据 | String/Number | 否 | - |
| reportDataProp | 直接传入的报告数据 | Object | 否 | null |

**注意：** `productId` 和 `reportDataProp` 至少需要提供一个。

## 数据结构

### 完整数据格式

```typescript
{
  // 基本信息
  baseInfo: {
    model: string,          // 机型名称
    level: string,          // 成色等级
    spec: string,           // 规格（如 256G）
    color: string,          // 颜色
    price: string,          // 价格
    coverImage?: string     // 封面图片 URL（可选）
  },
  
  // 检测分类
  categories: [
    {
      title: string,        // 分类标题（如"外观检测"）
      images?: string[],    // 分类图片列表（可选）
      groups: [             // 检测项分组
        {
          name?: string,    // 分组名称（可选）
          items: [          // 检测项列表
            {
              label: string,    // 检测项名称
              value: string,    // 检测结果文字
              pass: boolean,    // 是否通过
              image?: string    // 异常图片 URL（仅在 pass=false 时）
            }
          ]
        }
      ],
      footer?: {            // 底部备注（可选）
        label: string,
        value: string
      }
    }
  ]
}
```

### 示例数据

```javascript
{
  baseInfo: {
    model: 'iPhone 12 Pro Max',
    level: '外观 99新',
    spec: '256G',
    color: '海蓝色',
    price: '3,850',
    coverImage: 'https://example.com/iphone.jpg'
  },
  categories: [
    {
      title: '外观检测',
      images: [
        'https://example.com/img1.jpg',
        'https://example.com/img2.jpg'
      ],
      groups: [
        {
          name: '外壳外观',
          items: [
            {
              label: '碎裂',
              value: '无',
              pass: true
            },
            {
              label: '划痕',
              value: '明显划痕',
              pass: false,
              image: 'https://example.com/scratch.jpg'
            }
          ]
        }
      ]
    }
  ]
}
```

## 核心功能

### 1. 异常高亮

当检测项 `pass` 为 `false` 时：
- 文字自动标红
- 显示"查看异常图"按钮
- 统计显示异常数量

```javascript
{
  label: '屏幕',
  value: '检测到坏点',
  pass: false,  // ❌ 不通过
  image: 'https://example.com/screen-issue.jpg'
}
```

### 2. 图片查看

点击以下位置可以查看图片：
- 分类顶部的图片画廊
- 异常项旁边的"查看异常图"按钮

图片会在弹窗中居中展示，支持点击关闭。

### 3. 展开/收起

- 点击分类标题可以展开/收起该分类
- 点击右上角"全部展开/收起"可以批量操作

### 4. 自动统计

组件会自动统计：
- 每个分类的总检测项数
- 每个分类的异常项数
- 显示"X项全部通过"或"X项异常"

## 后端 API 对接

### API 端点

```
GET /api/verified-products/{productId}/inspection-report/
```

### 返回格式

```json
{
  "baseInfo": {
    "model": "iPhone 12 Pro Max",
    "level": "外观 99新",
    "spec": "256G",
    "color": "海蓝色",
    "price": "3850",
    "coverImage": "https://cdn.example.com/products/123/cover.jpg"
  },
  "categories": [
    {
      "title": "外观检测",
      "images": [
        "https://cdn.example.com/inspection/123/img1.jpg"
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
              "image": "https://cdn.example.com/inspection/123/scratch.jpg"
            }
          ]
        }
      ]
    }
  ]
}
```

### Django 后端示例

```python
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_inspection_report(request, product_id):
    product = VerifiedProduct.objects.get(id=product_id)
    report = product.inspection_report
    
    data = {
        'baseInfo': {
            'model': product.model,
            'level': product.condition_display,
            'spec': product.storage,
            'color': product.color,
            'price': str(product.price),
            'coverImage': product.cover_image.url if product.cover_image else None
        },
        'categories': []
    }
    
    # 外观检测
    appearance_items = []
    for check in report.appearance_checks.all():
        appearance_items.append({
            'label': check.item_name,
            'value': check.result_text,
            'pass': check.is_pass,
            'image': check.issue_image.url if not check.is_pass and check.issue_image else None
        })
    
    data['categories'].append({
        'title': '外观检测',
        'images': [img.url for img in report.appearance_images.all()],
        'groups': [{
            'name': '外壳外观',
            'items': appearance_items
        }]
    })
    
    return Response(data)
```

## 样式定制

### 修改主题色

```vue
<style scoped>
.inspection-report {
  --primary-color: #52c41a;   /* 成功绿 */
  --danger-color: #ff4d4f;    /* 警示红 */
  --link-color: #1890ff;      /* 链接蓝 */
}
</style>
```

### 调整布局

```vue
<style scoped>
/* 修改侧边栏宽度 */
.sidebar {
  width: 400px;
}

/* 修改卡片圆角 */
.check-card {
  border-radius: 20px;
}
</style>
```

## 完整示例

### 在商品详情页中使用

```vue
<template>
  <div class="product-detail-page">
    <!-- 商品基本信息 -->
    <div class="product-info">
      <h1>{{ product.title }}</h1>
      <div class="price">¥{{ product.price }}</div>
    </div>

    <!-- 验机报告 -->
    <div class="inspection-section">
      <h2>验机评估报告</h2>
      <InspectionReport :product-id="product.id" />
    </div>

    <!-- 其他内容 -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import InspectionReport from '@/components/InspectionReport.vue'
import api from '@/utils/api'

const route = useRoute()
const product = ref(null)

onMounted(async () => {
  const res = await api.get(`/verified-products/${route.params.id}/`)
  product.value = res.data
})
</script>

<style scoped>
.inspection-section {
  margin-top: 40px;
  padding: 40px 20px;
  background: #f5f7fa;
  border-radius: 16px;
}

.inspection-section h2 {
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: 700;
}
</style>
```

## 注意事项

1. **图片 URL** - 确保图片 URL 可访问，建议使用 CDN
2. **数据完整性** - 检测项的 `label`、`value`、`pass` 字段必填
3. **异常图片** - 只在 `pass=false` 时提供 `image` 字段
4. **性能优化** - 大量图片时建议使用懒加载
5. **移动端** - 在小屏幕下会自动切换为单栏布局

## 常见问题

### Q: 如何隐藏某个分类？

A: 在后端不返回该分类数据即可。

### Q: 如何自定义异常按钮样式？

A: 修改 `.view-image-btn` 的样式：

```css
.view-image-btn {
  background: #your-color;
  /* 其他样式 */
}
```

### Q: 如何添加更多检测分类？

A: 在 `categories` 数组中添加新的分类对象即可。

### Q: 图片查看器可以自定义吗？

A: 可以，修改 `.image-viewer-dialog` 和 `.image-viewer-content` 的样式。

## 相关组件

- [BaseCard](./ui-design-system.md#1-basecard---卡片组件) - 卡片容器
- [PageContainer](./ui-design-system.md#2-pagecontainer---页面容器) - 页面容器
- [Element Plus Dialog](https://element-plus.org/zh-CN/component/dialog.html) - 弹窗组件

## 更新日志

### 2025-12-14
- ✨ 创建 InspectionReport 组件
- ✨ 支持异常高亮和图片查看
- ✨ 集成到官翻商品详情页
- 📝 编写完整文档
