# 质检报告系统快速开始

## 5分钟快速上手

### 1. 查看测试数据

已创建 6 个测试商品，可以直接查看：

```bash
# 启动后端
cd backend
python manage.py runserver

# 启动前端
cd frontend
npm run dev
```

访问: http://localhost:5173/verified-products

### 2. 查看质检报告

点击任意商品，进入详情页，即可看到质检报告组件。

### 3. 编辑质检报告

#### 方法1：Django Shell（推荐）

```bash
cd backend
python manage.py shell
```

```python
from app.secondhand_app.models import VerifiedProduct

# 获取商品
product = VerifiedProduct.objects.get(id=196)

# 添加一个异常项示例
product.inspection_reports = [
    {
        'title': '外观检测',
        'images': [],
        'groups': [
            {
                'name': '外壳外观',
                'items': [
                    {'label': '碎裂', 'value': '无', 'pass': True},
                    {
                        'label': '划痕', 
                        'value': '明显划痕', 
                        'pass': False,
                        'image': 'https://via.placeholder.com/600x400/ff4d4f/ffffff?text=划痕异常图'
                    },
                    {'label': '机身弯曲', 'value': '无', 'pass': True}
                ]
            }
        ]
    }
]

product.save()
print("✓ 质检报告已更新")
```

#### 方法2：Django Admin

1. 访问 http://localhost:8000/admin/
2. 登录管理员账号
3. 找到 **官方验货商品**
4. 编辑商品的 **Inspection reports** 字段

### 4. API 测试

```bash
# 获取质检报告
curl http://localhost:8000/api/verified-products/196/inspection_report/
```

## 质检报告数据结构

### 最简示例

```json
[
  {
    "title": "外观检测",
    "images": [],
    "groups": [
      {
        "name": "外壳外观",
        "items": [
          {"label": "碎裂", "value": "无", "pass": true},
          {"label": "划痕", "value": "明显划痕", "pass": false, "image": "图片URL"}
        ]
      }
    ]
  }
]
```

### 字段说明

- `title`: 分类标题（外观检测、屏幕检测、设备功能、维修浸液）
- `images`: 检测图片数组（可选）
- `groups`: 检测项分组
  - `name`: 分组名称
  - `items`: 检测项数组
    - `label`: 检测项名称
    - `value`: 检测结果
    - `pass`: 是否通过（true=正常，false=异常）
    - `image`: 异常图片URL（仅当pass=false时）

## 完整的4大分类模板

复制以下代码到 Django Shell 中使用：

```python
product.inspection_reports = [
    {
        'title': '外观检测',
        'images': [],
        'groups': [
            {
                'name': '外壳外观',
                'items': [
                    {'label': '碎裂', 'value': '无', 'pass': True},
                    {'label': '划痕', 'value': '无', 'pass': True},
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
                    {'label': '坏点', 'value': '无', 'pass': True},
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
product.save()
```

## 常用操作

### 添加异常项

```python
# 在某个检测项中设置 pass=False 并添加图片
{
    'label': '划痕',
    'value': '明显划痕',
    'pass': False,
    'image': 'https://example.com/scratch.jpg'
}
```

### 批量更新所有商品

```python
from app.secondhand_app.models import VerifiedProduct

template = [...]  # 上面的完整模板

products = VerifiedProduct.objects.filter(status='active')
for product in products:
    product.inspection_reports = template
    product.save()
    print(f"✓ 已更新商品 {product.id}")
```

## 详细文档

- [API 文档](./30-api/inspection-report-api.md)
- [管理后台指南](./40-dev-guide/admin-inspection-report.md)
- [系统完整文档](./70-ui/INSPECTION-REPORT-SYSTEM.md)
- [实施报告](./INSPECTION-REPORT-IMPLEMENTATION.md)

## 需要帮助？

查看完整文档或联系开发团队。
