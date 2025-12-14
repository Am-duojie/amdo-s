# 质检报告数据格式说明

## 概述

质检报告的 `check_items` 字段支持两种格式：

1. **对象格式**（旧格式）：简单的键值对
2. **数组格式**（新格式）：66项详细检测数据

## 格式对比

### 对象格式（旧格式）

```json
{
  "外观": "良好",
  "屏幕": "无划痕",
  "功能": "正常"
}
```

**特点**：
- 简单的键值对
- 适合快速记录
- 缺少详细结构

### 数组格式（新格式）

```json
[
  {
    "title": "外观检测",
    "images": [],
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
```

**特点**：
- 结构化的66项检测
- 支持异常标记
- 支持异常图片
- 分类清晰

## 后端支持

### API 端点

```
POST /admin-api/inspection-orders/{order_id}/report
```

### 请求参数

```json
{
  "check_items": {},  // 对象格式或数组格式
  "remarks": "质检备注",
  "evidence": []
}
```

### 验证规则

- `check_items` 必须是对象（dict）或数组（list）
- 如果是字符串，会尝试解析为 JSON
- 其他类型会返回 400 错误

## 前端使用

### 官方验商品编辑

使用数组格式（66项检测）：

```javascript
const inspectionReports = convertInspectionDataToAPI()
// 返回数组格式
```

### 回收订单质检

使用数组格式（66项检测）：

```javascript
const inspectionReportData = convertInspectionDataToAPI()
await adminApi.post(`/inspection-orders/${orderId}/report`, {
  check_items: inspectionReportData,
  remarks: reportForm.remarks
})
```

## 数据迁移

### 从对象格式迁移到数组格式

如果需要将旧的对象格式数据迁移到新的数组格式：

```python
from app.admin_api.models import AdminInspectionReport

# 获取所有使用对象格式的报告
reports = AdminInspectionReport.objects.filter(
    check_items__isnull=False
)

for report in reports:
    if isinstance(report.check_items, dict):
        # 转换为数组格式
        new_format = convert_to_array_format(report.check_items)
        report.check_items = new_format
        report.save()
```

## 兼容性

- ✅ 后端同时支持对象和数组格式
- ✅ 前端新界面使用数组格式
- ✅ 旧数据仍然可以正常读取
- ✅ 不需要数据迁移

## 推荐使用

- **新项目**：使用数组格式（66项检测）
- **旧项目**：可以继续使用对象格式，或逐步迁移到数组格式
- **混合使用**：后端支持两种格式共存

## 相关文档

- [回收订单质检报告编辑器](./recycle-order-inspection-report.md)
- [官方验商品质检报告编辑器](./admin-inspection-report-editor.md)
- [质检报告系统完整文档](../70-ui/INSPECTION-REPORT-SYSTEM.md)
