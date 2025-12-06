# 支付宝签名验证错误解决方案

## 问题描述

错误代码：`invalid-signature`
错误原因：验签出错，建议检查签名字符串或签名私钥与应用公钥是否匹配

## 问题分析

从测试结果来看，我们的签名实现是正确的：
- ✅ 签名字符串正确排除了 `sign_type`
- ✅ 参数排序正确
- ✅ 签名算法实现正确

**问题根源：应用私钥与应用公钥不匹配**

## 解决方案

### 方案一：使用自定义密钥（推荐）

#### 步骤1：确认应用公钥

已生成的应用公钥（保存在 `app_public_key.pem` 文件）：

```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsIBLYDDaOOzNx5WO/Ctd
KJA9O7An3ghw3PlqHU/+YhN4MmN1QZhtxheX/FfxWZ2jQ2KzxcJkrnQ9pix/Alil
7gGeeawRGX+0B/WWsvmNk/LT01bICSMnym8P80J4Q29exh+yXS/b5pEAo7W63tp9
rjzZ63O1aKwqydcL1gagoUNDgIOC0i75BOwtiFm9QPNtySDmuN9OMw+aWJnpYGje
jQ0Tbj7uv9ctitzS45lH1ayxxa/oyrqsVpzGHFU9ZnplcNwrS11fId0ECFEPZN4u
tBnw3j5ZBjuRxhV6DTL/E2X2WGTXMkdZnpKY3pI/u6y5A2mQTy8rzjiawIwU6G6k
/wIDAQAB
-----END PUBLIC KEY-----
```

#### 步骤2：上传应用公钥到支付宝

1. 登录支付宝开放平台沙箱控制台：
   https://openhome.alipay.com/develop/sandbox/app

2. 选择您的应用（APPID: `9021000158624650`）

3. 点击"接口加签方式" -> "设置"

4. 选择"公钥"模式（沙箱环境仅支持公钥模式）

5. **将上面显示的公钥内容（包含头尾标记）完整复制到"应用公钥"输入框**

6. 点击"保存"

7. **重要**：保存后，支付宝会返回"支付宝公钥"，请复制这个公钥

#### 步骤3：更新支付宝公钥

将支付宝返回的"支付宝公钥"更新到 `backend/core/settings.py` 中的 `ALIPAY_SANDBOX_PUBLIC_KEY`

```python
ALIPAY_SANDBOX_PUBLIC_KEY = '支付宝返回的公钥（Base64格式）'
```

#### 步骤4：等待生效

上传公钥后，需要等待 **2-5分钟** 才能生效。

### 方案二：使用沙箱默认密钥

如果您想使用沙箱分配的默认密钥（如官方示例所示），需要：

1. 在支付宝沙箱控制台获取默认的应用私钥和支付宝公钥
2. 更新 `settings.py` 中的配置：
   - `ALIPAY_SANDBOX_APP_PRIVATE_KEY` = 沙箱默认应用私钥
   - `ALIPAY_SANDBOX_PUBLIC_KEY` = 沙箱默认支付宝公钥

## 验证步骤

1. 上传应用公钥后，等待2-5分钟
2. 重新尝试创建支付订单
3. 如果仍然失败，检查日志中的签名原文，确认与支付宝期望的格式一致

## 常见问题

### Q: 为什么签名验证失败？

A: 最常见的原因是：
- 应用公钥未正确上传到支付宝平台
- 上传的应用公钥与代码中的私钥不匹配
- 支付宝公钥配置错误（不是从支付宝控制台获取的）

### Q: 如何确认应用公钥是否正确上传？

A: 
1. 登录支付宝开放平台沙箱控制台
2. 进入应用详情页
3. 查看"接口加签方式" -> "应用公钥"
4. 确认显示的公钥与 `app_public_key.pem` 文件中的公钥一致

### Q: 应用公钥和支付宝公钥有什么区别？

A:
- **应用公钥**：从应用私钥生成的公钥，需要上传到支付宝平台
- **支付宝公钥**：上传应用公钥后，支付宝返回的公钥，用于验证支付宝返回的数据签名

### Q: 上传公钥后多久生效？

A: 通常需要等待 2-5 分钟才能生效。

## 测试工具

可以使用以下工具进行测试：

```bash
# 生成应用公钥
python generate_app_public_key.py

# 测试签名
python test_alipay_signature.py
```

## 参考文档

- 支付宝开放平台文档：https://opendocs.alipay.com/common/02kkv7
- 沙箱应用管理：https://openhome.alipay.com/develop/sandbox/app
- 签名验签文档：https://opendocs.alipay.com/common/02kipl

