# 支付宝签名验证错误修复总结

## 错误信息

```
错误代码: invalid-signature
错误原因: 验签出错，建议检查签名字符串或签名私钥与应用公钥是否匹配
```

## 问题原因分析

### 1. **`sign_type` 参数被错误排除**（主要原因）

**问题**：
- 在签名计算时，代码错误地将 `sign_type` 和 `sign` 都排除了
- 根据支付宝官方文档，只有 `sign` 参数不参与签名，`sign_type` 必须参与签名

**错误代码**：
```python
# 错误的实现
if k in ['sign', 'sign_type']:  # ❌ sign_type 被错误排除
    continue
```

**正确实现**：
```python
# 正确的实现
if k == 'sign':  # ✅ 只排除 sign，sign_type 参与签名
    continue
```

**影响**：
- 签名原文缺少 `sign_type=RSA2` 参数
- 导致签名原文与支付宝期望的格式不一致
- 签名验证失败

### 2. **JSON 字符串格式问题**（次要原因）

**问题**：
- 最初使用 `ensure_ascii=True`，将中文字符转义为 `\uXXXX` 格式
- 支付宝期望的是原始中文字符

**错误代码**：
```python
# 错误的实现
'biz_content': json.dumps(biz_content, ensure_ascii=True, ...)  # ❌ 中文字符被转义
```

**正确实现**：
```python
# 正确的实现
'biz_content': json.dumps(biz_content, ensure_ascii=False, ...)  # ✅ 保持中文字符原样
```

**影响**：
- 签名原文中的中文字符格式与支付宝期望不一致
- 虽然不影响签名计算，但可能导致其他问题

## 修复过程

### 步骤 1：检查密钥配置
- 验证应用私钥和支付宝公钥是否正确配置
- 确认应用公钥已正确上传到支付宝平台

### 步骤 2：对比签名原文
- 创建测试脚本，对比我们的签名原文和支付宝期望的格式
- 发现两个差异：
  1. 缺少 `sign_type=RSA2` 参数
  2. 中文字符格式不一致

### 步骤 3：修复签名逻辑
1. **修复 `sign_type` 排除问题**：
   ```python
   # 修改前
   if k in ['sign', 'sign_type']:
       continue
   
   # 修改后
   if k == 'sign':
       continue
   ```

2. **修复 JSON 格式问题**：
   ```python
   # 修改前
   'biz_content': json.dumps(biz_content, ensure_ascii=True, ...)
   
   # 修改后
   'biz_content': json.dumps(biz_content, ensure_ascii=False, ...)
   ```

### 步骤 4：验证修复
- 运行测试脚本，确认签名原文完全匹配
- 重新测试支付功能，验证通过

## 支付宝签名规范（重要）

根据支付宝官方文档（https://opendocs.alipay.com/common/02kipl），签名计算规则：

1. **筛选参数**：
   - 获取所有请求参数
   - **只排除 `sign` 参数**（不参与签名）
   - **`sign_type` 必须参与签名**

2. **排序**：
   - 按照参数名 ASCII 码从小到大排序（字典序）

3. **拼接**：
   - 将排序后的参数与其对应值，组合成 `参数=参数值` 的格式
   - 用 `&` 字符连接起来

4. **签名**：
   - 使用 RSA2 算法（SHA256），对拼接后的字符串进行签名
   - Base64 编码签名结果

## 关键要点

1. **`sign_type` 必须参与签名**：这是最容易出错的地方
2. **JSON 字符串格式**：中文字符应保持原样，不使用 Unicode 转义
3. **参数顺序**：必须按字典序排序
4. **空值处理**：空值（None、空字符串）不参与签名

## 调试工具

创建了两个调试工具：

1. **`check_alipay_config.py`**：
   - 检查支付宝配置
   - 验证密钥格式
   - 测试签名和验签

2. **`test_alipay_signature.py`**：
   - 对比签名原文格式
   - 验证参数是否正确
   - 帮助定位签名问题

## 预防措施

1. **严格按照官方文档实现**：不要凭经验猜测哪些参数参与签名
2. **使用测试工具验证**：在集成前先用测试工具验证签名格式
3. **详细日志记录**：记录完整的签名原文，便于对比和调试
4. **参考官方示例**：支付宝提供了官方示例代码，可以参考

## 相关文档

- [支付宝开放平台文档](https://opendocs.alipay.com/common/02kkv7)
- [签名验签文档](https://opendocs.alipay.com/common/02kipl)
- [电脑网站支付接口](https://opendocs.alipay.com/apis/api_1/alipay.trade.page.pay)











