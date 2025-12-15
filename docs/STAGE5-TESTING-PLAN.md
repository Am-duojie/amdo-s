# Stage 5 测试计划 - 回收系统模板化架构

**创建时间**: 2025-12-15  
**状态**: 进行中

## 测试目标

验证回收系统模板化架构的完整性、稳定性和性能，确保：
1. 所有功能正常工作
2. 数据流转正确
3. 用户体验流畅
4. 系统性能良好
5. 向后兼容性

## 测试环境

- **前端**: http://localhost:5173
- **后端**: http://127.0.0.1:8000
- **数据库**: MySQL
- **浏览器**: Chrome/Firefox/Safari

## 一、功能测试

### 1.1 用户端完整流程测试

#### 测试用例 1: 新机型回收流程（有模板）

**前置条件**: 
- 管理员已创建机型模板（如：iPhone 15 Pro Max）
- 模板包含完整的问卷配置

**测试步骤**:
1. 访问回收首页 `/recycle`
2. 选择设备类型：手机
3. 选择品牌：苹果
4. 选择机型：iPhone 15 Pro Max
5. 进入估价问卷页面
6. 验证问卷从后端加载（检查控制台日志）
7. 填写所有必填问题：
   - 购买渠道：官方/直营
   - 颜色：深空黑
   - 存储容量：256GB
   - 使用情况：正常使用痕迹
   - 配件情况：配件齐全
   - 屏幕外观：完美无瑕
   - 机身外壳：完美无瑕
   - 屏幕显示：显示正常
   - 前置摄像头：正常
   - 后置摄像头：正常
   - 维修情况：无拆修/无改
   - 屏幕维修：无拆修
   - 功能检测：都没有问题
8. 查看实时估价（应显示价格）
9. 点击"立即查看报价"
10. 进入提交订单页面
11. 验证显示的信息：
    - 设备信息正确
    - 预估价格显示
    - 收款信息显示
12. 点击"提交订单"
13. 验证订单创建成功
14. 跳转到订单详情页面
15. 验证订单详情显示：
    - 关联模板标签显示
    - 用户选择的配置显示（存储、颜色）
    - 问卷答案显示（格式化正确）

**预期结果**:
- ✅ 问卷从后端模板加载
- ✅ 实时估价正常工作
- ✅ 订单提交成功
- ✅ 订单详情显示完整
- ✅ 模板信息正确关联

**数据验证**:
```sql
-- 检查订单数据
SELECT id, template_id, device_type, brand, model, 
       selected_storage, selected_color, 
       questionnaire_answers, estimated_price
FROM secondhand_app_recycleorder 
ORDER BY id DESC LIMIT 1;

-- 验证 template_id 不为空
-- 验证 questionnaire_answers 是有效的 JSON
-- 验证 selected_storage 和 selected_color 有值
```

---

#### 测试用例 2: 旧机型回收流程（无模板）

**前置条件**: 
- 选择一个没有创建模板的机型（如：iPhone 12）

**测试步骤**:
1. 访问回收首页
2. 选择：手机 > 苹果 > iPhone 12
3. 进入估价问卷页面
4. 验证使用前端默认问卷（检查控制台日志）
5. 填写问卷
6. 提交订单
7. 验证订单创建成功（template_id 为 null）

**预期结果**:
- ✅ 前端默认问卷正常工作
- ✅ 订单可以正常提交（向后兼容）
- ✅ template_id 为 null 但不影响功能

---

#### 测试用例 3: 订单状态流转

**测试步骤**:
1. 创建一个回收订单（状态：pending）
2. 填写物流信息（快递公司、运单号）
3. 验证状态自动变为 shipped
4. 管理员标记为已收货（状态：received）
5. 管理员完成质检（状态：inspected）
6. 用户确认最终价格（状态：completed）
7. 管理员打款（payment_status: paid）

**预期结果**:
- ✅ 每个状态流转正确
- ✅ 时间戳正确记录
- ✅ 用户和管理员权限正确

---

### 1.2 管理端完整流程测试

#### 测试用例 4: 创建机型模板

**测试步骤**:
1. 登录管理后台
2. 进入"回收模板管理"
3. 点击"新增模板"
4. 填写基本信息：
   - 设备类型：手机
   - 品牌：苹果
   - 型号：iPhone 16 Pro
   - 系列：16系列
5. 填写规格信息：
   - 存储容量：["128GB", "256GB", "512GB", "1TB"]
   - 基础价格：{"128GB": 6000, "256GB": 6800, "512GB": 7800, "1TB": 8800}
   - RAM选项：["8GB"]
   - 版本选项：["国行", "港版", "美版"]
   - 颜色选项：["原色钛金属", "白色钛金属", "黑色钛金属", "自然钛金属"]
6. 填写设备参数：
   - 屏幕尺寸：6.3英寸
   - 电池容量：3582mAh
   - 充电类型：USB-C
7. 上传默认图片
8. 填写商品描述模板
9. 选择分类
10. 点击"保存"

**预期结果**:
- ✅ 模板创建成功
- ✅ 所有字段正确保存
- ✅ 可以在列表中看到新模板

---

#### 测试用例 5: 创建问卷模板

**测试步骤**:
1. 选择刚创建的机型模板
2. 点击"管理问卷"
3. 添加问题：
   - 问题1：购买渠道（单选，必填）
   - 问题2：颜色（单选，必填）
   - 问题3：使用情况（单选，必填）
   - 问题4：功能检测（多选，选填）
4. 为每个问题添加选项
5. 设置选项的影响（positive/minor/major/critical）
6. 保存问卷

**预期结果**:
- ✅ 问卷创建成功
- ✅ 问题顺序正确
- ✅ 选项配置正确

---

#### 测试用例 6: 回收订单管理

**测试步骤**:
1. 进入"回收订单管理"
2. 查看订单列表
3. 验证显示：
   - 模板信息（如果有）
   - 用户选择的配置
   - 订单状态
4. 点击订单详情
5. 验证详情页显示：
   - 完整的设备信息
   - 问卷答案
   - 质检报告（如果有）
6. 执行质检操作：
   - 填写质检数据
   - 设置最终价格
   - 保存质检报告
7. 标记订单为已完成

**预期结果**:
- ✅ 订单列表显示正确
- ✅ 订单详情完整
- ✅ 质检流程正常
- ✅ 状态更新正确

---

#### 测试用例 7: 官方验商品创建（从模板）

**测试步骤**:
1. 进入"官方验商品管理"
2. 点击"新增商品"
3. 选择创建方式：手动创建
4. 选择机型模板：iPhone 16 Pro
5. 验证自动填充：
   - 品牌：苹果
   - 型号：iPhone 16 Pro
   - 设备类型：手机
   - 默认图片
6. 选择配置：
   - 存储容量：256GB
   - 颜色：黑色钛金属
   - RAM：8GB
   - 版本：国行
7. 填写价格和库存
8. 验证商品描述自动生成（使用模板）
9. 保存商品

**预期结果**:
- ✅ 模板选择正常
- ✅ 自动填充正确
- ✅ 商品创建成功
- ✅ template 关联正确

---

## 二、数据一致性测试

### 2.1 模板关联测试

**测试 SQL**:
```sql
-- 测试1: 检查回收订单的模板关联
SELECT 
    ro.id,
    ro.template_id,
    rdt.device_type,
    rdt.brand,
    rdt.model,
    ro.device_type AS order_device_type,
    ro.brand AS order_brand,
    ro.model AS order_model
FROM secondhand_app_recycleorder ro
LEFT JOIN admin_api_recycledevicetemplate rdt ON ro.template_id = rdt.id
WHERE ro.template_id IS NOT NULL
LIMIT 10;

-- 验证: 模板信息与订单快照一致

-- 测试2: 检查官方验商品的模板关联
SELECT 
    vp.id,
    vp.template_id,
    rdt.brand,
    rdt.model,
    vp.title
FROM secondhand_app_verifiedproduct vp
LEFT JOIN admin_api_recycledevicetemplate rdt ON vp.template_id = rdt.id
WHERE vp.template_id IS NOT NULL
LIMIT 10;

-- 验证: 商品标题包含模板的品牌和型号

-- 测试3: 检查问卷答案的完整性
SELECT 
    id,
    template_id,
    questionnaire_answers,
    JSON_LENGTH(questionnaire_answers) AS answer_count
FROM secondhand_app_recycleorder
WHERE questionnaire_answers IS NOT NULL
AND questionnaire_answers != '{}'
LIMIT 10;

-- 验证: questionnaire_answers 是有效的 JSON
-- 验证: 答案数量合理（通常 5-15 个）
```

**预期结果**:
- ✅ 所有模板关联正确
- ✅ 数据快照与模板一致
- ✅ 问卷答案格式正确

---

### 2.2 价格计算测试

**测试场景**:
1. 基础价格从模板获取
2. 根据成色调整价格
3. 加上额外加价（bonus）
4. 最终价格 = 调整后价格 + bonus

**测试 SQL**:
```sql
SELECT 
    id,
    template_id,
    storage,
    selected_storage,
    condition,
    estimated_price,
    bonus,
    (estimated_price + IFNULL(bonus, 0)) AS total_price
FROM secondhand_app_recycleorder
WHERE template_id IS NOT NULL
ORDER BY id DESC
LIMIT 10;
```

**手动验证**:
1. 从模板获取基础价格（如 256GB = 6800）
2. 根据成色调整（如 good = 85%，6800 * 0.85 = 5780）
3. 加上 bonus（如 100）
4. 最终价格 = 5780 + 100 = 5880

**预期结果**:
- ✅ 价格计算逻辑正确
- ✅ 成色调整合理
- ✅ bonus 正确累加

---

## 三、性能测试

### 3.1 API 响应时间测试

**测试工具**: Postman / curl

**测试端点**:

1. **机型目录 API**
```bash
# 测试1: 获取所有机型
curl -w "@curl-format.txt" -o /dev/null -s \
  "http://127.0.0.1:8000/api/recycle-catalog/"

# 预期: < 500ms

# 测试2: 按品牌筛选
curl -w "@curl-format.txt" -o /dev/null -s \
  "http://127.0.0.1:8000/api/recycle-catalog/?brand=苹果"

# 预期: < 300ms
```

2. **问卷模板 API**
```bash
curl -w "@curl-format.txt" -o /dev/null -s \
  "http://127.0.0.1:8000/api/recycle-templates/question-template/?device_type=手机&brand=苹果&model=iPhone%2015%20Pro%20Max"

# 预期: < 400ms
```

3. **估价 API**
```bash
curl -X POST -w "@curl-format.txt" -o /dev/null -s \
  -H "Content-Type: application/json" \
  -d '{"device_type":"手机","brand":"苹果","model":"iPhone 15 Pro Max","storage":"256GB","condition":"good"}' \
  "http://127.0.0.1:8000/api/recycle-orders/estimate/"

# 预期: < 600ms
```

**curl-format.txt**:
```
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_pretransfer:  %{time_pretransfer}\n
time_redirect:  %{time_redirect}\n
time_starttransfer:  %{time_starttransfer}\n
----------\n
time_total:  %{time_total}\n
```

---

### 3.2 数据库查询优化

**慢查询检测**:
```sql
-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.5;  -- 超过 0.5 秒的查询

-- 检查慢查询
SELECT * FROM mysql.slow_log 
ORDER BY start_time DESC 
LIMIT 10;
```

**索引优化建议**:
```sql
-- 1. 回收订单表
CREATE INDEX idx_template_status ON secondhand_app_recycleorder(template_id, status);
CREATE INDEX idx_user_created ON secondhand_app_recycleorder(user_id, created_at DESC);

-- 2. 官方验商品表
CREATE INDEX idx_template_status ON secondhand_app_verifiedproduct(template_id, status);
CREATE INDEX idx_category_status ON secondhand_app_verifiedproduct(category_id, status);

-- 3. 机型模板表
CREATE INDEX idx_device_brand_model ON admin_api_recycledevicetemplate(device_type, brand, model);
CREATE INDEX idx_active ON admin_api_recycledevicetemplate(is_active);

-- 4. 问卷模板表
CREATE INDEX idx_template_active ON admin_api_recyclequestiontemplate(device_template_id, is_active);
CREATE INDEX idx_step_order ON admin_api_recyclequestiontemplate(step_order);
```

---

### 3.3 前端性能优化

**测试指标**:
1. **首屏加载时间** (FCP - First Contentful Paint)
   - 目标: < 1.5s
   - 测试工具: Chrome DevTools Lighthouse

2. **页面交互时间** (TTI - Time to Interactive)
   - 目标: < 3s
   - 测试工具: Chrome DevTools Lighthouse

3. **问卷加载时间**
   - 目标: < 1s
   - 测试: 从点击机型到问卷显示的时间

**优化建议**:
```javascript
// 1. 问卷数据缓存
const questionnaireCache = new Map();

async function loadQuestionTemplate(deviceType, brand, model) {
  const cacheKey = `${deviceType}-${brand}-${model}`;
  
  if (questionnaireCache.has(cacheKey)) {
    return questionnaireCache.get(cacheKey);
  }
  
  const data = await api.get('/recycle-templates/question-template/', {
    params: { device_type: deviceType, brand, model }
  });
  
  questionnaireCache.set(cacheKey, data);
  return data;
}

// 2. 图片懒加载
<img 
  :src="template.default_cover_image" 
  loading="lazy"
  alt="机型图片"
/>

// 3. 列表虚拟滚动（如果机型很多）
import { VirtualScroller } from 'vue-virtual-scroller';
```

---

## 四、用户体验测试

### 4.1 表单验证测试

**测试场景**:
1. 必填字段未填写
2. 价格输入非数字
3. 存储容量选项为空
4. 问卷未完成就提交

**预期结果**:
- ✅ 显示清晰的错误提示
- ✅ 错误提示位置准确
- ✅ 提示文案友好

---

### 4.2 加载状态测试

**测试场景**:
1. 问卷加载中
2. 估价计算中
3. 订单提交中
4. 图片上传中

**预期结果**:
- ✅ 显示加载动画
- ✅ 禁用提交按钮
- ✅ 显示加载文案

---

### 4.3 错误处理测试

**测试场景**:
1. 网络错误（断网）
2. API 返回 500 错误
3. 数据格式错误
4. 权限不足

**预期结果**:
- ✅ 显示友好的错误提示
- ✅ 提供重试选项
- ✅ 不影响其他功能

---

## 五、兼容性测试

### 5.1 浏览器兼容性

**测试浏览器**:
- ✅ Chrome (最新版)
- ✅ Firefox (最新版)
- ✅ Safari (最新版)
- ✅ Edge (最新版)
- ✅ 移动端浏览器 (iOS Safari, Chrome Mobile)

**测试功能**:
- 页面布局
- 表单交互
- 图片上传
- 问卷填写

---

### 5.2 向后兼容性测试

**测试场景**:
1. 旧订单（没有 template_id）
2. 旧订单（没有 questionnaire_answers）
3. 旧商品（没有 template_id）

**测试 SQL**:
```sql
-- 创建测试数据：旧订单
INSERT INTO secondhand_app_recycleorder 
(user_id, device_type, brand, model, storage, condition, estimated_price, status, created_at, updated_at)
VALUES 
(1, '手机', '苹果', 'iPhone 13', '256GB', 'good', 4500, 'pending', NOW(), NOW());

-- 验证旧订单可以正常显示
SELECT * FROM secondhand_app_recycleorder WHERE template_id IS NULL;
```

**预期结果**:
- ✅ 旧订单正常显示
- ✅ 不显示模板信息（优雅降级）
- ✅ 不显示问卷答案
- ✅ 其他功能正常

---

## 六、安全测试

### 6.1 权限测试

**测试场景**:
1. 未登录用户访问管理端
2. 普通用户访问管理端
3. 用户访问他人订单
4. 管理员权限边界

**预期结果**:
- ✅ 正确的权限拦截
- ✅ 返回 401/403 错误
- ✅ 不泄露敏感信息

---

### 6.2 数据验证测试

**测试场景**:
1. SQL 注入测试
2. XSS 攻击测试
3. CSRF 攻击测试
4. 文件上传安全

**测试方法**:
```bash
# SQL 注入测试
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"brand":"苹果' OR '1'='1","model":"test"}' \
  "http://127.0.0.1:8000/api/recycle-orders/estimate/"

# 预期: 参数验证失败，不执行查询

# XSS 测试
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"note":"<script>alert(1)</script>"}' \
  "http://127.0.0.1:8000/api/recycle-orders/"

# 预期: 内容被转义或过滤
```

---

## 七、测试报告模板

### 测试执行记录

| 测试用例 | 执行时间 | 执行人 | 结果 | 问题描述 | 优先级 |
|---------|---------|--------|------|---------|--------|
| UC1: 新机型回收流程 | 2025-12-15 | - | ⏳ | - | P0 |
| UC2: 旧机型回收流程 | 2025-12-15 | - | ⏳ | - | P1 |
| UC3: 订单状态流转 | 2025-12-15 | - | ⏳ | - | P0 |
| UC4: 创建机型模板 | 2025-12-15 | - | ⏳ | - | P0 |
| UC5: 创建问卷模板 | 2025-12-15 | - | ⏳ | - | P0 |
| UC6: 回收订单管理 | 2025-12-15 | - | ⏳ | - | P0 |
| UC7: 官方验商品创建 | 2025-12-15 | - | ⏳ | - | P1 |

### 问题追踪

| 问题ID | 问题描述 | 严重程度 | 状态 | 负责人 | 解决方案 |
|-------|---------|---------|------|--------|---------|
| BUG-001 | - | - | - | - | - |

### 性能指标

| 指标 | 目标值 | 实际值 | 状态 |
|-----|--------|--------|------|
| 机型目录 API | < 500ms | - | ⏳ |
| 问卷模板 API | < 400ms | - | ⏳ |
| 估价 API | < 600ms | - | ⏳ |
| 首屏加载 (FCP) | < 1.5s | - | ⏳ |
| 页面交互 (TTI) | < 3s | - | ⏳ |

---

## 八、测试优先级

### P0 - 阻塞性问题（必须修复）
- 用户无法提交订单
- 管理员无法创建模板
- 数据丢失或损坏
- 安全漏洞

### P1 - 严重问题（尽快修复）
- 功能不完整
- 性能严重下降
- 用户体验差

### P2 - 一般问题（可以延后）
- UI 细节问题
- 非关键功能缺失
- 轻微性能问题

### P3 - 优化建议（可选）
- 代码优化
- 文档完善
- 功能增强

---

## 九、测试工具

### 自动化测试工具
- **Postman**: API 测试
- **Lighthouse**: 性能测试
- **Chrome DevTools**: 调试和性能分析
- **MySQL Workbench**: 数据库测试

### 手动测试工具
- **浏览器**: Chrome, Firefox, Safari
- **移动设备**: iOS, Android
- **网络模拟**: Chrome DevTools Network Throttling

---

## 十、测试完成标准

- ✅ 所有 P0 问题已修复
- ✅ 所有 P1 问题已修复或有解决方案
- ✅ 核心功能测试通过率 100%
- ✅ 性能指标达标
- ✅ 兼容性测试通过
- ✅ 安全测试通过
- ✅ 测试报告完成

---

## 下一步

完成测试后，进入 **Stage 6: 部署和上线**。
