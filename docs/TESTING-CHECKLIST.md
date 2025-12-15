# 测试检查清单 - 回收系统模板化架构

**创建时间**: 2025-12-15  
**最后更新**: 2025-12-15

## 快速测试指南

这是一个简化的测试检查清单，用于快速验证回收系统的核心功能。

---

## 一、用户端测试（30分钟）

### ✅ 测试 1: 新机型回收流程（有模板）

**步骤**:
1. [ ] 访问 http://localhost:5173/recycle
2. [ ] 选择：手机 > 苹果 > iPhone 15 Pro Max
3. [ ] 进入问卷页面，验证问卷从后端加载
4. [ ] 填写所有必填问题
5. [ ] 查看实时估价（应显示价格）
6. [ ] 点击"立即查看报价"
7. [ ] 验证订单提交页面信息正确
8. [ ] 点击"提交订单"
9. [ ] 验证订单详情显示：
   - [ ] 关联模板标签
   - [ ] 用户选择的配置
   - [ ] 问卷答案

**预期**: ✅ 所有步骤正常，数据完整

---

### ✅ 测试 2: 旧机型回收流程（无模板）

**步骤**:
1. [ ] 选择一个没有模板的机型（如 iPhone 12）
2. [ ] 验证使用前端默认问卷
3. [ ] 填写问卷并提交订单
4. [ ] 验证订单创建成功（template_id 为 null）

**预期**: ✅ 前端默认问卷正常工作，向后兼容

---

### ✅ 测试 3: 订单状态流转

**步骤**:
1. [ ] 创建订单（状态：pending）
2. [ ] 填写物流信息
3. [ ] 验证状态变为 shipped
4. [ ] 查看订单详情，验证物流信息显示

**预期**: ✅ 状态流转正确

---

## 二、管理端测试（30分钟）

### ✅ 测试 4: 创建机型模板

**步骤**:
1. [ ] 登录管理后台
2. [ ] 进入"回收模板管理"
3. [ ] 点击"新增模板"
4. [ ] 填写基本信息：
   - 设备类型：手机
   - 品牌：苹果
   - 型号：iPhone 16 Pro
   - 系列：16系列
5. [ ] 填写规格信息：
   - 存储容量：["128GB", "256GB", "512GB", "1TB"]
   - 基础价格：{"128GB": 6000, "256GB": 6800}
   - 颜色选项：["黑色", "白色", "蓝色", "金色"]
6. [ ] 填写设备参数：
   - 屏幕尺寸：6.3英寸
   - 电池容量：3582mAh
7. [ ] 保存模板

**预期**: ✅ 模板创建成功，所有字段正确保存

---

### ✅ 测试 5: 创建问卷模板

**步骤**:
1. [ ] 选择刚创建的机型模板
2. [ ] 点击"管理问卷"
3. [ ] 添加问题：
   - 购买渠道（单选，必填）
   - 颜色（单选，必填）
   - 使用情况（单选，必填）
4. [ ] 为每个问题添加选项
5. [ ] 保存问卷

**预期**: ✅ 问卷创建成功

---

### ✅ 测试 6: 回收订单管理

**步骤**:
1. [ ] 进入"回收订单管理"
2. [ ] 查看订单列表
3. [ ] 点击订单详情
4. [ ] 验证显示：
   - [ ] 模板信息
   - [ ] 用户配置
   - [ ] 问卷答案
5. [ ] 执行质检操作
6. [ ] 标记订单为已完成

**预期**: ✅ 订单管理功能正常

---

### ✅ 测试 7: 官方验商品创建

**步骤**:
1. [ ] 进入"官方验商品管理"
2. [ ] 点击"新增商品"
3. [ ] 选择机型模板
4. [ ] 验证自动填充：品牌、型号、设备类型
5. [ ] 选择配置：存储、颜色
6. [ ] 填写价格和库存
7. [ ] 保存商品

**预期**: ✅ 商品创建成功，template 关联正确

---

## 三、数据验证（10分钟）

### ✅ SQL 验证

```sql
-- 1. 检查回收订单的模板关联
SELECT 
    id, template_id, device_type, brand, model,
    selected_storage, selected_color,
    JSON_LENGTH(questionnaire_answers) AS answer_count
FROM secondhand_app_recycleorder 
WHERE template_id IS NOT NULL
ORDER BY id DESC LIMIT 5;

-- 预期: template_id 不为空，questionnaire_answers 有数据

-- 2. 检查官方验商品的模板关联
SELECT 
    id, template_id, device_type, title, price, status
FROM secondhand_app_verifiedproduct 
WHERE template_id IS NOT NULL
ORDER BY id DESC LIMIT 5;

-- 预期: template_id 不为空，商品信息完整

-- 3. 检查问卷答案格式
SELECT 
    id,
    questionnaire_answers,
    JSON_VALID(questionnaire_answers) AS is_valid_json
FROM secondhand_app_recycleorder
WHERE questionnaire_answers IS NOT NULL
LIMIT 5;

-- 预期: is_valid_json = 1（JSON 格式正确）
```

---

## 四、性能测试（10分钟）

### ✅ API 响应时间

```bash
# 1. 机型目录 API
curl -w "\nTime: %{time_total}s\n" \
  "http://127.0.0.1:8000/api/recycle-catalog/"

# 预期: < 0.5s

# 2. 问卷模板 API
curl -w "\nTime: %{time_total}s\n" \
  "http://127.0.0.1:8000/api/recycle-templates/question-template/?device_type=手机&brand=苹果&model=iPhone%2015%20Pro%20Max"

# 预期: < 0.4s

# 3. 估价 API
curl -X POST -w "\nTime: %{time_total}s\n" \
  -H "Content-Type: application/json" \
  -d '{"device_type":"手机","brand":"苹果","model":"iPhone 15 Pro Max","storage":"256GB","condition":"good"}' \
  "http://127.0.0.1:8000/api/recycle-orders/estimate/"

# 预期: < 0.6s
```

---

## 五、兼容性测试（10分钟）

### ✅ 旧数据兼容性

**步骤**:
1. [ ] 查看没有 template_id 的旧订单
2. [ ] 验证旧订单正常显示
3. [ ] 验证不显示模板信息（优雅降级）
4. [ ] 验证其他功能正常

**SQL**:
```sql
-- 查看旧订单
SELECT * FROM secondhand_app_recycleorder 
WHERE template_id IS NULL 
LIMIT 5;
```

**预期**: ✅ 旧订单正常显示，不影响功能

---

## 六、浏览器兼容性（10分钟）

### ✅ 测试浏览器

- [ ] Chrome（最新版）
- [ ] Firefox（最新版）
- [ ] Safari（最新版）
- [ ] Edge（最新版）

**测试内容**:
- [ ] 页面布局正常
- [ ] 表单交互正常
- [ ] 问卷填写正常
- [ ] 图片显示正常

---

## 七、错误处理测试（10分钟）

### ✅ 测试场景

1. [ ] 网络错误（断网后提交订单）
   - 预期：显示友好错误提示

2. [ ] 表单验证（必填字段未填写）
   - 预期：显示验证错误

3. [ ] API 错误（后端返回 500）
   - 预期：显示错误提示，不崩溃

4. [ ] 权限错误（未登录访问管理端）
   - 预期：跳转到登录页

---

## 八、测试结果记录

### 测试执行记录

| 测试项 | 执行时间 | 结果 | 问题 | 备注 |
|-------|---------|------|------|------|
| 用户端-新机型流程 | - | ⏳ | - | - |
| 用户端-旧机型流程 | - | ⏳ | - | - |
| 用户端-订单状态 | - | ⏳ | - | - |
| 管理端-创建模板 | - | ⏳ | - | - |
| 管理端-创建问卷 | - | ⏳ | - | - |
| 管理端-订单管理 | - | ⏳ | - | - |
| 管理端-商品创建 | - | ⏳ | - | - |
| 数据验证 | - | ⏳ | - | - |
| 性能测试 | - | ⏳ | - | - |
| 兼容性测试 | - | ⏳ | - | - |
| 浏览器兼容 | - | ⏳ | - | - |
| 错误处理 | - | ⏳ | - | - |

### 问题追踪

| 问题ID | 描述 | 严重程度 | 状态 | 解决方案 |
|-------|------|---------|------|---------|
| - | - | - | - | - |

---

## 九、测试完成标准

- [ ] 所有核心功能测试通过
- [ ] 数据验证通过
- [ ] 性能指标达标
- [ ] 兼容性测试通过
- [ ] 错误处理正常
- [ ] 无阻塞性问题（P0）
- [ ] 测试报告完成

---

## 十、下一步

测试完成后，进入 **Stage 6: 部署和上线**。

---

## 附录：快速测试脚本

### A. 创建测试数据

```sql
-- 创建测试用户
INSERT INTO auth_user (username, password, email, is_staff, is_active, date_joined)
VALUES ('testuser', 'pbkdf2_sha256$...', 'test@example.com', 0, 1, NOW());

-- 创建测试模板
INSERT INTO admin_api_recycledevicetemplate 
(device_type, brand, model, series, storages, base_prices, is_active, created_at, updated_at)
VALUES 
('手机', '苹果', 'iPhone 15 Pro Max', '15系列', 
 '["128GB","256GB","512GB","1TB"]',
 '{"128GB":7000,"256GB":7800,"512GB":8800,"1TB":9800}',
 1, NOW(), NOW());
```

### B. 清理测试数据

```sql
-- 删除测试订单
DELETE FROM secondhand_app_recycleorder WHERE user_id = (SELECT id FROM auth_user WHERE username = 'testuser');

-- 删除测试模板
DELETE FROM admin_api_recycledevicetemplate WHERE model = 'iPhone 15 Pro Max';
```

---

**测试愉快！** 🚀
