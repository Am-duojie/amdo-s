# 管理后台质检报告编辑指南

## 概述

本文档介绍如何在 Django Admin 管理后台编辑官方验货商品的质检报告。

## 访问管理后台

1. 启动后端服务：
```bash
cd backend
python manage.py runserver
```

2. 访问管理后台：
```
http://localhost:8000/admin/
```

3. 使用管理员账号登录

## 编辑质检报告

### 方法1：通过 Django Admin 界面

1. 在管理后台中，找到 **官方验货商品 (Verified Products)** 模块
2. 点击要编辑的商品
3. 找到 **Inspection reports** 字段
4. 在 JSON 编辑器中输入质检报告数据

### 方法2：通过 Django Shell

```bash
cd backend
python manage.py shell
```

```python
from app.secondhand_app.models import VerifiedProduct

# 获取商品
product = VerifiedProduct.objects.get(id=196)

# 设置质检报告数据
product.inspection_reports = [
    {
        'title': '外观检测',
        'images': [
            'https://example.com/image1.jpg',
            'https://example.com/image2.jpg'
        ],
        'groups': [
            {
                'name': '外壳外观',
                'items': [
                    {'label': '碎裂', 'value': '无', 'pass': True},
                    {
                        'label': '划痕', 
                        'value': '明显划痕', 
                        'pass': False,
                        'image': 'https://example.com/scratch.jpg'
                    },
                    {'label': '机身弯曲', 'value': '无', 'pass': True},
                    {'label': '脱胶/缝隙', 'value': '无', 'pass': True},
                    {'label': '外壳/其他', 'value': '正常', 'pass': True},
                    {'label': '磕碰', 'value': '几乎不可见', 'pass': True},
                    {'label': '刻字/图', 'value': '无', 'pass': True},
                    {'label': '掉漆/磨损', 'value': '几乎不可见', 'pass': True},
                    {'label': '摄像头/闪光灯外观', 'value': '正常', 'pass': True},
                    {'label': '褶皱', 'value': '无', 'pass': True},
                    {'label': '卡托', 'value': '正常', 'pass': True},
                    {'label': '音频网罩', 'value': '正常', 'pass': True}
                ]
            }
        ]
    },
    {
        'title': '屏幕检测',
        'images': [],
        'groups': [
            {
                'name': '屏幕触控',
                'items': [
                    {'label': '触控', 'value': '正常', 'pass': True}
                ]
            },
            {
                'name': '屏幕外观',
                'items': [
                    {'label': '屏幕/其它', 'value': '正常', 'pass': True},
                    {'label': '碎裂', 'value': '无', 'pass': True},
                    {'label': '内屏掉漆/划伤', 'value': '无', 'pass': True},
                    {'label': '屏幕凸点（褶皱）', 'value': '正常', 'pass': True},
                    {'label': '支架破损', 'value': '无', 'pass': True},
                    {'label': '浅划痕', 'value': '几乎不可见', 'pass': True},
                    {'label': '深划痕', 'value': '几乎不可见', 'pass': True}
                ]
            },
            {
                'name': '屏幕显示',
                'items': [
                    {'label': '进灰', 'value': '无', 'pass': True},
                    {
                        'label': '坏点', 
                        'value': '检测到坏点', 
                        'pass': False,
                        'image': 'https://example.com/dead-pixel.jpg'
                    },
                    {'label': '气泡', 'value': '无', 'pass': True},
                    {'label': '色斑', 'value': '无', 'pass': True},
                    {'label': '其它', 'value': '正常', 'pass': True},
                    {'label': '亮点/亮斑', 'value': '无', 'pass': True},
                    {'label': '泛红/泛黄', 'value': '无', 'pass': True},
                    {'label': '图文残影', 'value': '无', 'pass': True}
                ]
            }
        ]
    },
    {
        'title': '设备功能',
        'images': [],
        'groups': [
            {
                'name': '按键',
                'items': [
                    {'label': '电源键', 'value': '正常', 'pass': True},
                    {'label': '音量键', 'value': '正常', 'pass': True},
                    {'label': '静音键', 'value': '正常', 'pass': True},
                    {'label': '其它按键', 'value': '正常', 'pass': True}
                ]
            },
            {
                'name': '生物识别',
                'items': [
                    {'label': '面部识别', 'value': '正常', 'pass': True},
                    {'label': '指纹识别', 'value': '正常', 'pass': True}
                ]
            },
            {
                'name': '传感器',
                'items': [
                    {'label': '重力感应', 'value': '正常', 'pass': True},
                    {'label': '指南针', 'value': '正常', 'pass': True},
                    {'label': '距离感应', 'value': '正常', 'pass': True},
                    {'label': '光线感应', 'value': '正常', 'pass': True}
                ]
            },
            {
                'name': '接口',
                'items': [
                    {'label': '充电接口', 'value': '正常', 'pass': True},
                    {'label': '耳机接口', 'value': '正常', 'pass': True}
                ]
            },
            {
                'name': '无线',
                'items': [
                    {'label': 'WiFi', 'value': '正常', 'pass': True},
                    {'label': '蓝牙', 'value': '正常', 'pass': True},
                    {'label': 'GPS', 'value': '正常', 'pass': True},
                    {'label': 'NFC', 'value': '正常', 'pass': True}
                ]
            },
            {
                'name': '充电',
                'items': [
                    {'label': '充电功能', 'value': '正常', 'pass': True},
                    {'label': '无线充电', 'value': '正常', 'pass': True}
                ]
            },
            {
                'name': '通话功能',
                'items': [
                    {'label': '通话', 'value': '正常', 'pass': True},
                    {'label': '信号', 'value': '正常', 'pass': True}
                ]
            },
            {
                'name': '声音与振动',
                'items': [
                    {'label': '扬声器', 'value': '正常', 'pass': True},
                    {'label': '麦克风', 'value': '正常', 'pass': True},
                    {'label': '振动', 'value': '正常', 'pass': True}
                ]
            },
            {
                'name': '摄像头',
                'items': [
                    {'label': '前置摄像头', 'value': '正常', 'pass': True},
                    {'label': '后置摄像头', 'value': '正常', 'pass': True},
                    {'label': '闪光灯', 'value': '正常', 'pass': True}
                ]
            },
            {
                'name': '其它状况',
                'items': [
                    {'label': '电池健康', 'value': '98%', 'pass': True}
                ]
            }
        ]
    },
    {
        'title': '维修浸液',
        'images': [],
        'groups': [
            {
                'name': '维修浸液',
                'items': [
                    {'label': '屏幕', 'value': '未检出维修更换', 'pass': True},
                    {'label': '主板', 'value': '未检出维修', 'pass': True},
                    {'label': '机身', 'value': '未检出维修更换', 'pass': True},
                    {'label': '零件维修/更换', 'value': '未检出维修更换', 'pass': True},
                    {'label': '零件缺失', 'value': '未检出缺失', 'pass': True},
                    {'label': '后摄维修情况', 'value': '未检出维修更换', 'pass': True},
                    {'label': '前摄维修情况', 'value': '未检出维修更换', 'pass': True},
                    {'label': '浸液痕迹情况', 'value': '未检出浸液痕迹', 'pass': True}
                ]
            }
        ],
        'footer': {
            'label': '拆机检测',
            'value': '平台未拆机检测'
        }
    }
]

# 保存
product.save()

print(f"✓ 已更新商品 {product.id} 的质检报告")
```

## 质检报告数据结构

### 完整结构示例

```json
[
  {
    "title": "分类标题",
    "images": ["图片URL1", "图片URL2"],
    "groups": [
      {
        "name": "分组名称",
        "items": [
          {
            "label": "检测项名称",
            "value": "检测结果",
            "pass": true
          },
          {
            "label": "异常项名称",
            "value": "异常描述",
            "pass": false,
            "image": "异常图片URL"
          }
        ]
      }
    ],
    "footer": {
      "label": "备注标签",
      "value": "备注内容"
    }
  }
]
```

### 字段说明

- **title**: 分类标题（外观检测、屏幕检测、设备功能、维修浸液）
- **images**: 该分类的检测图片URL数组（可选）
- **groups**: 检测项分组数组
  - **name**: 分组名称
  - **items**: 检测项数组
    - **label**: 检测项名称
    - **value**: 检测结果描述
    - **pass**: 是否通过（true=正常，false=异常）
    - **image**: 异常图片URL（仅当pass=false时需要）
- **footer**: 底部备注（可选）
  - **label**: 备注标签
  - **value**: 备注内容

## 批量更新示例

如果需要为多个商品设置相同的质检报告模板：

```python
from app.secondhand_app.models import VerifiedProduct

# 定义模板
template = [
    # ... 完整的质检报告结构
]

# 批量更新
products = VerifiedProduct.objects.filter(status='active')
for product in products:
    product.inspection_reports = template
    product.save()
    print(f"✓ 已更新商品 {product.id}")
```

## 注意事项

1. **数据格式**: 必须严格遵循 JSON 格式，注意逗号、引号等
2. **pass 字段**: 必须是布尔值（true/false），不能是字符串
3. **异常图片**: 只有当 `pass=false` 时才需要提供 `image` 字段
4. **图片URL**: 建议使用完整的 URL 路径
5. **备份数据**: 在批量更新前，建议先备份数据库

## 未来改进

建议开发专门的质检报告编辑界面，提供：
- 可视化的表单编辑
- 图片上传功能
- 检测项模板管理
- 批量编辑功能
- 数据验证和预览
