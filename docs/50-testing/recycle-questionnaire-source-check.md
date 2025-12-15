# 回收问卷内容来源检查指南

## 检查目的

验证前端问卷内容是否从后端模板系统加载，而不是使用前端固定的默认步骤。

## 检查方法

### 1. 浏览器控制台检查

1. 打开浏览器开发者工具（F12）
2. 切换到"控制台"（Console）标签
3. 访问回收问卷页面：`/recycle/estimate?device_type=手机&brand=vivo&model=X100 Pro`
4. 查看控制台日志，应该看到以下信息：

**如果从后端加载成功：**
```
[问卷加载] 从后端获取到模板: {id: 1, device_type: "手机", brand: "vivo", model: "X100 Pro", ...}
[问卷加载] 成功加载 13 个问题
[问卷步骤] 当前使用的步骤数量: 13 来源: 后端模板
```

**如果使用前端默认步骤：**
```
[问卷加载] 未找到后端问卷模板，使用默认步骤
[问卷步骤] 当前使用的步骤数量: 13 来源: 前端默认
```

### 2. 网络请求检查

1. 打开浏览器开发者工具（F12）
2. 切换到"网络"（Network）标签
3. 访问回收问卷页面
4. 查找以下请求：
   - `GET /api/recycle-templates/question-template/?device_type=手机&brand=vivo&model=X100+Pro`

**如果请求成功（200）：**
- 说明后端有模板数据
- 查看响应内容，应该包含 `questions` 数组

**如果请求失败（404）：**
- 说明后端没有该机型的模板
- 前端会使用默认步骤（fallback机制）

### 3. 数据库检查

检查后端是否有该机型的模板数据：

```bash
python manage.py shell
```

```python
from app.admin_api.models import RecycleDeviceTemplate, RecycleQuestionTemplate

# 检查机型模板
template = RecycleDeviceTemplate.objects.filter(
    device_type='手机',
    brand='vivo',
    model='X100 Pro',
    is_active=True
).first()

if template:
    print(f"找到模板: {template}")
    print(f"存储容量: {template.storages}")
    
    # 检查问卷问题
    questions = RecycleQuestionTemplate.objects.filter(
        device_template=template,
        is_active=True
    ).order_by('step_order')
    
    print(f"问题数量: {questions.count()}")
    for q in questions:
        print(f"  {q.step_order}. {q.title} ({q.key})")
else:
    print("未找到模板，前端将使用默认步骤")
```

## 当前实现逻辑

### 前端加载流程

1. **页面加载时**（`onMounted`）：
   - 调用 `loadQuestionTemplate()` 尝试从后端加载问卷模板
   - 如果成功，设置 `templateFromBackend.value = data`
   - 如果失败（404），设置 `templateFromBackend.value = null`

2. **步骤生成**（`baseSteps` 计算属性）：
   - 优先使用 `convertTemplateToSteps(templateFromBackend.value)`
   - 如果 `templateFromBackend.value` 为 `null`，使用 `getDefaultSteps()`

3. **存储容量处理**：
   - 如果后端模板有 `storages`，使用后端的存储容量列表
   - 如果后端没有模板，从 `/api/recycle-catalog/` 加载存储容量

### 后端接口

- **接口路径**：`GET /api/recycle-templates/question-template/`
- **参数**：`device_type`, `brand`, `model`
- **返回**：
  ```json
  {
    "id": 1,
    "device_type": "手机",
    "brand": "vivo",
    "model": "X100 Pro",
    "storages": ["256GB", "512GB"],
    "questions": [
      {
        "id": 1,
        "step_order": 1,
        "key": "channel",
        "title": "购买渠道",
        "helper": "官方直营/运营商/第三方等",
        "question_type": "single",
        "is_required": true,
        "options": [...]
      },
      ...
    ]
  }
  ```

## 常见问题

### Q: 为什么看到"使用默认步骤"？

**A:** 可能的原因：
1. 后端没有该机型的模板数据（需要运行导入命令）
2. 机型名称不匹配（注意大小写、空格等）
3. 模板被禁用（`is_active=False`）

**解决方法：**
1. 运行导入命令：`python manage.py import_recycle_templates`
2. 在管理端检查模板是否存在且启用
3. 检查 URL 参数中的机型名称是否与数据库中的完全一致

### Q: 如何确认数据来源？

**A:** 查看浏览器控制台日志：
- `[问卷加载] 从后端获取到模板` → 从后端加载
- `[问卷加载] 未找到后端问卷模板` → 使用前端默认

### Q: 如何强制使用后端模板？

**A:** 确保：
1. 已运行导入命令创建模板数据
2. 模板的 `is_active=True`
3. 机型名称完全匹配（设备类型、品牌、型号）

## 验证清单

- [ ] 浏览器控制台显示"从后端获取到模板"
- [ ] 网络请求 `/api/recycle-templates/question-template/` 返回 200
- [ ] 响应数据包含 `questions` 数组
- [ ] 问卷步骤数量与后端模板一致
- [ ] 问题标题和选项与后端模板一致










