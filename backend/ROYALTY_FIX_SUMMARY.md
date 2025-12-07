# 分账功能修复总结

## 修复时间
2025-12-07

## 问题分析

根据支付宝分账沙箱调试说明文档，发现以下问题导致分账功能无法正常使用：

### 1. 创建订单时缺少分账冻结参数
**问题**：在创建支付订单时，没有设置 `extend_params.royalty_freeze = "true"`，导致订单无法进行分账操作。

**修复**：
- 在 `AlipayClient.create_trade()` 方法中添加 `enable_royalty` 参数
- 当启用分账时，自动设置 `extend_params.royalty_freeze = "true"`
- 在 `payment_views.py` 中调用 `create_trade` 时传入 `enable_royalty` 参数

### 2. 分账接口缺少关键参数
**问题**：
- 缺少 `extend_params.royalty_finish = "true"`（表示完成分账）
- 缺少 `royalty_scene`（分账场景）
- 缺少 `trans_out` 和 `trans_out_type`（转出方信息，可选但建议提供）

**修复**：
- 在 `AlipayClient.settle_order()` 方法中自动添加 `extend_params.royalty_finish = "true"`
- 添加 `royalty_scene` 参数支持（默认值："平台服务费"）
- 添加 `trans_out` 和 `trans_out_type` 参数支持（可选）
- 更新所有调用 `settle_order` 的地方，添加 `royalty_scene` 参数

### 3. trans_in_type 值不正确
**问题**：代码中部分地方使用了 `ALIPAY_LOGON_ID` 和 `ALIPAY_USER_ID`，但根据支付宝文档，应该使用 `userId` 或 `loginName`。

**修复**：
- 在 `settle_order` 方法中添加类型转换逻辑，自动将 `ALIPAY_LOGON_ID` 转换为 `loginName`，`ALIPAY_USER_ID` 转换为 `userId`
- 更新所有调用处，确保使用正确的值：
  - `userId`：支付宝用户ID（2088开头的16位数字）
  - `loginName`：支付宝登录账号（手机号或邮箱）

## 修复的文件

1. **backend/app/secondhand_app/alipay_client.py**
   - `create_trade()`: 添加 `enable_royalty` 参数和分账冻结逻辑
   - `settle_order()`: 添加 `extend_params.royalty_finish`、`royalty_scene`、`trans_out` 等参数支持

2. **backend/app/secondhand_app/payment_views.py**
   - `create_payment()`: 在创建支付时传入 `enable_royalty` 参数

3. **backend/app/secondhand_app/views.py**
   - 更新普通订单和官方验订单的分账调用，添加 `royalty_scene` 参数

4. **backend/app/admin_api/views.py**
   - 更新管理员重试分账的调用，添加 `royalty_scene` 参数

5. **backend/app/secondhand_app/serializers.py**
   - 更新自动结算的分账调用，添加 `royalty_scene` 参数

## 分账流程说明

### 1. 创建订单并支付
```python
# 创建支付订单时，如果启用分账，会自动设置分账冻结参数
alipay.create_trade(
    out_trade_no='normal_123',
    subject='商品标题',
    total_amount=100.00,
    enable_royalty=True  # 启用分账冻结
)
```

### 2. 订单完成后分账结算
```python
# 分账结算时，需要提供完整的参数
alipay.settle_order(
    trade_no='2023060122001462650500142964',  # 支付宝交易号
    out_request_no='settle_123_1234567890',   # 分账请求号
    splits=[{
        'trans_in': '208872****140864',        # 分账接收方账号
        'trans_in_type': 'userId',             # 账号类型：userId 或 loginName
        'amount': 90.00,                       # 分账金额
        'desc': '易淘分账-卖家',               # 分账描述
        'royalty_scene': '平台服务费'          # 分账场景
    }],
    # trans_out 和 trans_out_type 可选，如果不提供则使用商户账号
)
```

## 配置检查清单

确保以下配置正确：

1. **settings.py 配置**
   ```python
   ENABLE_ALIPAY_ROYALTY = True  # 启用分账功能
   SETTLE_ON_ORDER_COMPLETED = True  # 订单完成后自动分账
   ALIPAY_GATEWAY_URL = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'  # 沙箱环境
   ```

2. **卖家支付宝账号绑定**
   - 卖家需要在个人资料中绑定支付宝登录账号（`alipay_login_id`）
   - 建议同时绑定支付宝真实姓名（`alipay_real_name`）

3. **分账关系绑定**（可选）
   - 根据支付宝文档，在分账前需要先绑定分账关系
   - 当前实现中，如果分账失败，会自动降级到转账方式（如果启用了 `SETTLEMENT_FALLBACK_TO_TRANSFER`）

## 测试建议

1. **创建订单测试**
   - 创建一个订单并支付
   - 检查订单创建时的请求参数，确认包含 `extend_params.royalty_freeze = "true"`

2. **分账结算测试**
   - 完成订单后，检查分账请求参数
   - 确认包含 `extend_params.royalty_finish = "true"`
   - 确认 `royalty_parameters` 中包含所有必需字段

3. **错误处理测试**
   - 测试卖家未绑定支付宝账号的情况
   - 测试分账失败后的降级处理（转账方式）

## 注意事项

1. **沙箱环境限制**
   - 沙箱环境的数据与生产环境完全隔离
   - 必须在生产环境进行最终测试验收

2. **分账关系绑定**
   - 根据支付宝文档，分账前需要先绑定分账关系
   - 当前实现中，如果分账失败，会尝试使用转账方式（如果启用）
   - 如果需要，可以添加分账关系自动绑定功能

3. **账号类型**
   - `userId`：支付宝用户ID（2088开头的16位数字）
   - `loginName`：支付宝登录账号（手机号或邮箱）
   - 根据实际情况选择合适的类型

4. **分账金额**
   - 分账金额不能超过订单总金额
   - 平台佣金 = 订单总金额 - 卖家分账金额

## 相关文档

- [支付宝分账沙箱调试说明](./ALIPAY_ROYALTY_SANDBOX_DEBUG_GUIDE.md)
- [支付宝商家分账接入指南](https://opendocs.alipay.com/open/08456h)

## 后续优化建议

1. **分账关系自动绑定**
   - 在卖家绑定支付宝账号时，自动调用 `alipay.trade.royalty.relation.bind` 接口绑定分账关系
   - 在分账前检查分账关系是否存在，如果不存在则先绑定

2. **分账结果通知**
   - 配置异步分账结果通知接口
   - 处理分账成功/失败的异步通知

3. **分账查询**
   - 添加分账查询功能，可以查询分账状态和结果
   - 在订单详情中显示分账信息

4. **错误日志优化**
   - 记录详细的分账请求和响应日志
   - 提供分账失败的原因分析




