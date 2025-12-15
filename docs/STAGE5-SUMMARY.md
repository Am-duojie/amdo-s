# Stage 5 开始 - 测试和优化

**创建时间**: 2025-12-15  
**状态**: 进行中

## 概述

Stage 5 的目标是全面测试回收系统模板化架构，确保系统稳定、性能良好、用户体验流畅。

## 已创建的文档

### 1. 详细测试计划
**文件**: `docs/STAGE5-TESTING-PLAN.md`

包含完整的测试用例、测试步骤、预期结果和数据验证方法。适合深入测试和问题排查。

**内容**:
- 用户端完整流程测试（7个测试用例）
- 管理端完整流程测试（7个测试用例）
- 数据一致性测试（SQL验证）
- 性能测试（API响应时间、数据库优化）
- 用户体验测试
- 兼容性测试
- 安全测试

### 2. 快速测试检查清单
**文件**: `docs/TESTING-CHECKLIST.md`

简化的测试清单，可以在 **2小时内** 完成核心功能的快速验证。

**内容**:
- 用户端测试（3个核心流程）
- 管理端测试（4个核心功能）
- 数据验证（SQL查询）
- 性能测试（API响应时间）
- 兼容性测试（浏览器）
- 错误处理测试

### 3. 性能优化建议
**文件**: `docs/PERFORMANCE-OPTIMIZATION.md`

详细的性能优化方案，包括后端、前端、数据库和网络优化。

**内容**:
- 数据库索引优化（SQL脚本）
- 查询优化（N+1问题解决）
- 缓存优化（API缓存、前端缓存）
- 前端性能优化（懒加载、代码分割、防抖节流）
- 网络优化（请求合并、Gzip压缩）
- 性能监控（后端和前端）

## 测试优先级

### P0 - 核心功能（必须测试）
1. ✅ 用户端新机型回收流程（有模板）
2. ✅ 用户端旧机型回收流程（无模板）
3. ✅ 管理端创建机型模板
4. ✅ 管理端创建问卷模板
5. ✅ 数据一致性验证

### P1 - 重要功能（尽快测试）
1. ⏳ 订单状态流转
2. ⏳ 官方验商品创建
3. ⏳ 性能测试
4. ⏳ 兼容性测试

### P2 - 次要功能（可选测试）
1. ⏳ 错误处理
2. ⏳ 边界情况
3. ⏳ 安全测试

## 快速开始

### 方案 A: 快速测试（2小时）

使用 `docs/TESTING-CHECKLIST.md`，按照清单逐项测试：

1. **用户端测试**（30分钟）
   - 新机型回收流程
   - 旧机型回收流程
   - 订单状态流转

2. **管理端测试**（30分钟）
   - 创建机型模板
   - 创建问卷模板
   - 回收订单管理
   - 官方验商品创建

3. **数据验证**（10分钟）
   - 运行 SQL 查询验证数据

4. **性能测试**（10分钟）
   - 测试 API 响应时间

5. **兼容性测试**（10分钟）
   - 测试不同浏览器

6. **错误处理测试**（10分钟）
   - 测试错误场景

### 方案 B: 完整测试（1-2天）

使用 `docs/STAGE5-TESTING-PLAN.md`，进行全面测试：

1. **第1天上午**: 功能测试
   - 用户端完整流程
   - 管理端完整流程

2. **第1天下午**: 数据和性能测试
   - 数据一致性测试
   - 性能测试
   - 应用性能优化

3. **第2天上午**: 兼容性和安全测试
   - 浏览器兼容性
   - 向后兼容性
   - 安全测试

4. **第2天下午**: 问题修复和验证
   - 修复发现的问题
   - 回归测试
   - 编写测试报告

## 性能优化实施

### 立即优化（P0）

1. **数据库索引**
```sql
-- 运行 docs/PERFORMANCE-OPTIMIZATION.md 中的索引创建脚本
CREATE INDEX idx_recycleorder_template_status 
ON secondhand_app_recycleorder(template_id, status);

CREATE INDEX idx_verifiedproduct_template_status 
ON secondhand_app_verifiedproduct(template_id, status);

-- ... 其他索引
```

2. **查询优化**
```python
# 在 RecycleOrderViewSet 中添加 select_related
def get_queryset(self):
    return RecycleOrder.objects.select_related(
        'user', 'template'
    ).filter(user=self.request.user)
```

3. **API 缓存**
```python
# 在 RecycleCatalogView 中添加缓存
from django.core.cache import cache

def get(self, request):
    cache_key = f"recycle_catalog:{device_type}:{brand}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)
    # ... 查询数据库
    cache.set(cache_key, data, 900)  # 15分钟
```

### 后续优化（P1）

1. 前端缓存（问卷数据）
2. 图片懒加载
3. 代码分割
4. 防抖节流

## 测试工具

### 必备工具
- **浏览器**: Chrome DevTools
- **API测试**: Postman 或 curl
- **数据库**: MySQL Workbench
- **性能分析**: Chrome Lighthouse

### 可选工具
- **自动化测试**: Selenium
- **压力测试**: Apache JMeter
- **监控**: Sentry, New Relic

## 测试数据准备

### 创建测试模板

```sql
-- 创建测试机型模板
INSERT INTO admin_api_recycledevicetemplate 
(device_type, brand, model, series, storages, base_prices, is_active, created_at, updated_at)
VALUES 
('手机', '苹果', 'iPhone 15 Pro Max', '15系列', 
 '["128GB","256GB","512GB","1TB"]',
 '{"128GB":7000,"256GB":7800,"512GB":8800,"1TB":9800}',
 1, NOW(), NOW());
```

### 创建测试用户

```sql
-- 创建测试用户（密码: test123）
INSERT INTO auth_user (username, password, email, is_staff, is_active, date_joined)
VALUES ('testuser', 'pbkdf2_sha256$...', 'test@example.com', 0, 1, NOW());
```

## 问题追踪

### 已知问题

| 问题ID | 描述 | 严重程度 | 状态 | 解决方案 |
|-------|------|---------|------|---------|
| - | - | - | - | - |

### 待验证功能

- [ ] 问卷模板的动态加载
- [ ] 用户配置的保存和显示
- [ ] 问卷答案的格式化显示
- [ ] 模板关联的数据一致性
- [ ] 向后兼容性（旧订单）

## 测试报告模板

### 测试执行记录

```markdown
## 测试日期: 2025-12-15

### 测试环境
- 前端: http://localhost:5173
- 后端: http://127.0.0.1:8000
- 数据库: MySQL 8.0
- 浏览器: Chrome 120

### 测试结果
- 总测试用例: 12
- 通过: 10
- 失败: 2
- 跳过: 0

### 发现的问题
1. [BUG-001] 问卷加载慢（响应时间 > 1s）
   - 严重程度: P1
   - 解决方案: 添加缓存

2. [BUG-002] 旧订单显示异常
   - 严重程度: P2
   - 解决方案: 添加空值检查

### 性能指标
- 机型目录 API: 350ms ✅
- 问卷模板 API: 280ms ✅
- 估价 API: 520ms ✅
- 首屏加载: 1.8s ⚠️ (目标 < 1.5s)

### 建议
1. 优化首屏加载时间
2. 添加更多错误提示
3. 改进移动端体验
```

## 下一步

完成测试和优化后，进入 **Stage 6: 部署和上线**。

---

## 附录：测试命令速查

### API 测试
```bash
# 机型目录
curl "http://127.0.0.1:8000/api/recycle-catalog/"

# 问卷模板
curl "http://127.0.0.1:8000/api/recycle-templates/question-template/?device_type=手机&brand=苹果&model=iPhone%2015%20Pro%20Max"

# 估价
curl -X POST -H "Content-Type: application/json" \
  -d '{"device_type":"手机","brand":"苹果","model":"iPhone 15 Pro Max","storage":"256GB","condition":"good"}' \
  "http://127.0.0.1:8000/api/recycle-orders/estimate/"
```

### 数据验证
```sql
-- 检查模板关联
SELECT COUNT(*) FROM secondhand_app_recycleorder WHERE template_id IS NOT NULL;

-- 检查问卷答案
SELECT COUNT(*) FROM secondhand_app_recycleorder WHERE questionnaire_answers IS NOT NULL;

-- 检查数据完整性
SELECT * FROM secondhand_app_recycleorder 
WHERE template_id IS NOT NULL 
AND (selected_storage IS NULL OR questionnaire_answers IS NULL);
```

---

**开始测试！** 🚀
