# 支付宝商家转账功能使用指南

## 功能概述

商家转账功能用于回收订单完成后，平台自动打款给用户。使用支付宝官方接口 `alipay.fund.trans.uni.transfer` 实现自动化转账。

**参考文档**：
- [商家转账接入指南](https://opendocs.alipay.com/open/03dcrm?pathHash=4ba3b20b)
- [接口文档](https://opendocs.alipay.com/open/03dcrm)

## 前置条件

### 1. 企业支付宝账号

- ✅ 必须是企业支付宝账号（个人账号不支持）
- ✅ 完成企业实名认证
- ✅ 开通商家转账功能（需要在支付宝开放平台申请）

### 2. 应用配置

- ✅ 已创建应用并获取 APPID
- ✅ 已配置应用公钥和私钥
- ✅ 已获取支付宝公钥

### 3. 功能开通

1. 登录支付宝开放平台：https://open.alipay.com/
2. 进入应用管理 → 选择您的应用
3. 在"功能列表"中申请开通"商家转账"功能
4. 等待支付宝审核通过（通常需要1-3个工作日）

## 接口说明

### 接口名称

`alipay.fund.trans.uni.transfer`（新版本，推荐）

### 请求参数

```python
{
    'out_biz_no': '商户转账唯一订单号',  # 必填，商户系统内唯一
    'trans_amount': '转账金额',  # 必填，单位：元，精确到小数点后两位
    'product_code': 'TRANS_ACCOUNT_NO_PWD',  # 产品码，转账到支付宝账户
    'biz_scene': 'DIRECT_TRANSFER',  # 业务场景：直接转账
    'payee_info': {
        'identity': '收款方账户',  # 必填，支付宝登录账号（手机号或邮箱）
        'identity_type': 'ALIPAY_LOGON_ID',  # 账户类型
        'name': '收款方真实姓名'  # 可选，但建议填写以提高成功率
    },
    'remark': '转账备注'  # 可选，最长200字符
}
```

### 响应参数

**成功响应**：
```json
{
    "alipay_fund_trans_uni_transfer_response": {
        "code": "10000",
        "msg": "Success",
        "order_id": "支付宝转账订单号",
        "pay_fund_order_id": "支付宝资金流水号",
        "out_biz_no": "商户订单号",
        "status": "SUCCESS",
        "trans_date": "2025-12-06"
    }
}
```

**失败响应**：
```json
{
    "alipay_fund_trans_uni_transfer_response": {
        "code": "40004",
        "msg": "Business Failed",
        "sub_code": "PAYEE_NOT_EXIST",
        "sub_msg": "收款账户不存在"
    }
}
```

## 代码实现

### 1. 转账方法（已实现）

在 `backend/app/secondhand_app/alipay_client.py` 中已实现 `transfer_to_account` 方法：

```python
alipay = AlipayClient()
result = alipay.transfer_to_account(
    out_biz_no='recycle_123_1234567890',  # 商户转账唯一订单号
    payee_account='13800138000',  # 收款方账户（支付宝账号）
    amount=195.00,  # 转账金额
    payee_real_name='张三',  # 收款方真实姓名（可选，但建议填写）
    remark='回收订单#123打款，设备：iPhone 13'  # 转账备注
)

if result.get('success'):
    print(f'转账成功，支付宝订单号：{result.get("order_id")}')
else:
    print(f'转账失败：{result.get("sub_msg")}')
```

### 2. 回收订单打款集成（已实现）

在 `backend/app/admin_api/views.py` 的 `InspectionOrderPaymentView` 中已集成：

- ✅ 自动调用支付宝转账接口
- ✅ 处理转账成功/失败
- ✅ 更新订单打款状态
- ✅ 记录支付宝订单号

## 使用流程

### 1. 管理员操作

1. 进入管理后台 → 回收订单管理
2. 选择已完成质检的订单（状态为 `inspected` 或 `completed`）
3. 点击"打款"按钮
4. 填写打款信息：
   - **打款方式**：选择"支付宝"
   - **打款账户**：输入用户的支付宝账号（手机号或邮箱）
   - **打款备注**：可选
5. 点击"确认打款"

### 2. 系统处理

1. **验证订单状态**：检查订单是否已完成质检
2. **验证配置**：检查支付宝配置是否完整
3. **调用转账接口**：调用支付宝商家转账接口
4. **处理结果**：
   - **成功**：更新订单状态为 `paid`，记录支付宝订单号
   - **失败**：更新打款状态为 `failed`，返回错误信息

### 3. 转账结果

**成功**：
- 订单打款状态更新为 `paid`
- 记录打款时间 `paid_at`
- 在备注中记录支付宝订单号
- 如果订单状态是 `inspected`，自动更新为 `completed`

**失败**：
- 订单打款状态更新为 `failed`
- 返回详细错误信息（错误码、错误原因）
- 管理员可以查看错误信息，重新尝试打款

## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `PAYEE_NOT_EXIST` | 收款账户不存在 | 检查支付宝账号是否正确 |
| `PAYEE_USER_INFO_ERROR` | 收款方信息错误 | 检查账号和姓名是否匹配 |
| `INSUFFICIENT_BALANCE` | 账户余额不足 | 检查企业支付宝账户余额 |
| `TRANSFER_AMOUNT_ERROR` | 转账金额错误 | 检查金额格式和范围 |
| `PERMISSION_DENIED` | 权限不足 | 检查是否已开通商家转账功能 |

### 错误处理逻辑

1. **配置错误**：如果支付宝配置不完整，记录警告日志，但不阻止打款操作（可能是手动打款）
2. **转账失败**：更新打款状态为 `failed`，返回详细错误信息
3. **转账异常**：捕获异常，更新打款状态为 `failed`，记录异常日志

## 测试

### 沙箱环境测试

1. **使用沙箱账号**：
   - 登录支付宝开放平台沙箱环境
   - 获取沙箱买家账号（用于测试收款）

2. **测试转账**：
   ```python
   # 在管理后台使用沙箱买家账号测试转账
   # 打款账户：沙箱买家账号（手机号或邮箱）
   # 金额：任意金额（沙箱环境）
   ```

3. **验证结果**：
   - 查看后端日志，确认转账请求和响应
   - 检查订单打款状态是否更新
   - 在支付宝沙箱环境查看转账记录

### 生产环境

1. **确保功能已开通**：在支付宝开放平台确认商家转账功能已审核通过
2. **测试小额转账**：先测试小额转账，确认功能正常
3. **监控日志**：定期检查转账日志，确保无异常

## 注意事项

### 1. 账户要求

- ⚠️ **必须是企业支付宝账号**：个人账号不支持商家转账
- ⚠️ **需要开通功能**：需要在支付宝开放平台申请开通
- ⚠️ **需要审核**：功能开通需要支付宝审核，通常1-3个工作日

### 2. 转账限制

- **单笔限额**：根据企业资质不同，限额不同（通常单笔最高5万元）
- **日累计限额**：根据企业资质不同，日累计限额不同
- **手续费**：免费（支付宝不收取手续费）

### 3. 安全建议

- ✅ **验证收款账户**：建议填写收款方真实姓名，提高成功率
- ✅ **记录转账日志**：所有转账操作都记录详细日志
- ✅ **错误处理**：妥善处理转账失败情况，提供重试机制
- ✅ **定期对账**：定期与支付宝对账，确保账目一致

### 4. 转账备注

- 转账备注会显示在用户的支付宝账单中
- 建议包含订单号、设备信息等，方便用户识别
- 最长200字符

## 接口调用示例

### Python 示例

```python
from app.secondhand_app.alipay_client import AlipayClient
import time

# 创建支付宝客户端
alipay = AlipayClient()

# 验证配置
is_valid, error_msg = alipay.validate_config()
if not is_valid:
    print(f'配置错误: {error_msg}')
    exit()

# 调用转账接口
result = alipay.transfer_to_account(
    out_biz_no=f'recycle_123_{int(time.time())}',
    payee_account='13800138000',  # 用户支付宝账号
    amount=195.00,
    payee_real_name='张三',  # 用户真实姓名
    remark='回收订单#123打款，设备：iPhone 13 128GB'
)

if result.get('success'):
    print(f'转账成功')
    print(f'支付宝订单号: {result.get("order_id")}')
    print(f'资金流水号: {result.get("pay_fund_order_id")}')
    print(f'状态: {result.get("status")}')
else:
    print(f'转账失败')
    print(f'错误码: {result.get("code")}')
    print(f'错误信息: {result.get("msg")}')
    print(f'子错误码: {result.get("sub_code")}')
    print(f'子错误信息: {result.get("sub_msg")}')
```

## 相关文档

- [商家转账接入指南](https://opendocs.alipay.com/open/03dcrm?pathHash=4ba3b20b)
- [接口文档](https://opendocs.alipay.com/open/03dcrm)
- [支付宝开放平台](https://open.alipay.com/)

## 总结

商家转账功能已完整实现，包括：

1. ✅ **转账接口实现**：`alipay.fund.trans.uni.transfer`
2. ✅ **回收订单集成**：自动调用转账接口
3. ✅ **错误处理**：完善的错误处理和日志记录
4. ✅ **状态管理**：自动更新订单打款状态

**使用前请确保**：
- 已开通商家转账功能
- 已配置正确的支付宝参数
- 已在沙箱环境测试通过





