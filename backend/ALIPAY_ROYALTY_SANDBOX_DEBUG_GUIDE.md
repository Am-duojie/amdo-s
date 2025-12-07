# 支付宝商家分账沙箱调试说明

**文档来源**: [支付宝开放平台](https://opendocs.alipay.com/open/08456h?pathHash=37644751)  
**更新时间**: 2025-07-17 14:42:17

---

## 一、沙箱环境概述

### 1.1 定义

沙箱环境是支付宝开放平台为开发者提供的与生产环境完全隔离的联调测试环境，开发者在沙箱环境中完成的接口调用不会对生产环境中的数据造成任何影响。

### 1.2 功能范围

沙箱为开放的产品提供有限功能范围的支持（覆盖的功能范围查看以下业务用例），可以覆盖产品的绝大部分核心链路和对接逻辑，便于开发者快速学习/尝试/开发/调试，推荐开发者遵循业务用例来使用沙箱。

### 1.3 优势

沙箱环境会自动完成或忽略一些场景的业务门槛，例如：开发者无需等待产品开通，即可直接在沙箱环境调用接口，使得开发集成工作可以与商务流程并行，从而提高项目整体的交付效率。

### 1.4 重要注意事项

**注意：**

1. **环境差异**：由于沙箱环境并非 100% 与生产环境一致，接口的实际响应逻辑请以生产环境为准，沙箱环境开发调试完成后，仍然需要在生产环境进行测试验收。

2. **数据独立性**：沙箱环境拥有完全独立的数据体系，沙箱环境下返回的数据（比如用户ID等）在生产环境中都是不存在的，开发者不可将沙箱环境返回的数据与生产环境中的数据混淆。

3. **文档范围**：本文仅说明如何在沙箱环境中调试商家分账，非沙箱环境调试通用说明。更多沙箱介绍和沙箱控制台使用说明可查看[沙箱环境](https://opendocs.alipay.com/open/200/105311)。

---

## 二、业务用例说明

沙箱通过业务用例定义支持的功能范围。业务用例描述了典型业务场景下，开发者可通过先后对接哪些接口来实现业务目标，每个业务用例会为开发者提供接口调用时序与参数示例值。

**推荐开发者遵循业务用例来使用沙箱。**

**注意：**

- 示例参数值中与沙箱当前账号、应用上下文相关的参数，需开发者自行参照接入指南调用配套接口获取。
- 其他交易辅助接口可以根据需求进行调用调试。

---

## 三、分账关系维护（1.1）

### 3.1 分账关系绑定（1.1.1）

**OpenAPI**: `alipay.trade.royalty.relation.bind`（分账关系绑定接口）

#### 入参示例

```json
{
  "out_request_no": "904d6656c72b4b12b378252c32a51119",
  "receiver_list": [
    {
      "account": "208872****140864",
      "memo": "沙箱测试商家分账",
      "name": "沙箱测试分账接收方",
      "type": "userId"
    }
  ]
}
```

#### 出参示例

```json
{
  "alipay_trade_royalty_relation_bind_response": {
    "code": "10000",
    "msg": "Success",
    "result_code": "SUCCESS"
  },
  "sign": "..."
}
```

### 3.2 分账关系查询（1.1.2）

**OpenAPI**: `alipay.trade.royalty.relation.batchquery`（分账关系查询接口）

#### 入参示例

```json
{
  "page_num": 1,
  "page_size": 20
}
```

#### 出参示例

```json
{
  "alipay_trade_royalty_relation_batchquery_response": {
    "code": "10000",
    "msg": "Success",
    "current_page_num": 1,
    "current_page_size": 20,
    "receiver_list": [
      {
        "account": "208872****140864",
        "login_name": "ogtewv4012@sandbox.com",
        "memo": "沙箱测试商家分账",
        "type": "userId"
      }
    ],
    "result_code": "SUCCESS",
    "total_page_num": 1,
    "total_record_num": 1
  }
}
```

### 3.3 分账比例查询（1.1.3）

**OpenAPI**: `alipay.trade.royalty.rate.query`（分账比例查询接口）

#### 入参示例

```json
{
  "out_request_no": "查询分账比例请求号"
}
```

#### 出参示例

```json
{
  "alipay_trade_royalty_rate_query_response": {
    "code": "10000",
    "msg": "Success",
    "royalty_rate": "0.10",
    "result_code": "SUCCESS"
  }
}
```

### 3.4 分账关系解绑（1.1.4）

**OpenAPI**: `alipay.trade.royalty.relation.unbind`（分账关系解绑接口）

#### 入参示例

```json
{
  "out_request_no": "解绑请求号",
  "receiver_list": [
    {
      "account": "208872****140864",
      "type": "userId"
    }
  ]
}
```

#### 出参示例

```json
{
  "alipay_trade_royalty_relation_unbind_response": {
    "code": "10000",
    "msg": "Success",
    "result_code": "SUCCESS"
  }
}
```

---

## 四、同步分账（1.2）

### 4.1 下单并支付（1.2.1）

**OpenAPI**: `alipay.trade.create`（统一收单交易创建接口）

#### 入参示例

```json
{
  "buyer_id": "208862****162656",
  "extend_params": {
    "royalty_freeze": "true"
  },
  "out_trade_no": "4ab4149fdd78430184a91e6a06004df4",
  "product_code": "JSAPI_PAY",
  "subject": "沙箱 JSAPI 分账测试",
  "total_amount": "238"
}
```

#### 出参示例

```json
{
  "alipay_trade_create_response": {
    "code": "10000",
    "msg": "Success",
    "out_trade_no": "4ab4149fdd78430184a91e6a06004df4",
    "trade_no": "2023060122001462650500142964"
  },
  "sign": "..."
}
```

**说明**：
- 通过小程序 IDE（切换到沙箱环境(新)）扫码并支付
- 支付成功后，订单状态变为已支付，可以进行分账操作

### 4.2 请求分账（1.2.2）

**OpenAPI**: `alipay.trade.order.settle`（统一收单交易结算接口）

#### 入参示例

```json
{
  "extend_params": {
    "royalty_finish": "true"
  },
  "out_request_no": "4347fc926bf948678da6a33dd1a26cd7",
  "royalty_parameters": [
    {
      "amount": "10",
      "desc": "沙箱商家分账测试",
      "royalty_scene": "平台服务费",
      "trans_in": "208872****140864",
      "trans_in_type": "userId",
      "trans_out": "208862****856735",
      "trans_out_type": "userId"
    }
  ],
  "trade_no": "2023053022001462650500141239"
}
```

#### 出参示例

```json
{
  "alipay_trade_order_settle_response": {
    "code": "10000",
    "msg": "Success",
    "settle_no": "20230601002530020065620300064709",
    "trade_no": "2023060122001462650500142964"
  },
  "sign": "..."
}
```

**参数说明**：
- `royalty_finish`: 是否完成分账，`"true"` 表示分账完成
- `out_request_no`: 分账请求号，商户自定义
- `royalty_parameters`: 分账明细列表
  - `amount`: 分账金额
  - `desc`: 分账描述
  - `royalty_scene`: 分账场景
  - `trans_in`: 分账接收方账号
  - `trans_in_type`: 分账接收方账号类型（userId/loginName）
  - `trans_out`: 分账转出方账号
  - `trans_out_type`: 分账转出方账号类型
- `trade_no`: 支付宝交易号

### 4.3 分账查询（1.2.3）

**OpenAPI**: `alipay.trade.order.settle.query`（交易分账查询接口）

#### 入参示例

```json
{
  "settle_no": "20230601002530020065620300064709"
}
```

#### 出参示例

```json
{
  "alipay_trade_order_settle_query_response": {
    "code": "10000",
    "msg": "Success",
    "royalty_detail_list": [
      {
        "amount": "10.00",
        "detail_id": "2023060122001462650500142964",
        "operation_type": "transfer",
        "state": "SUCCESS",
        "trans_in": "208872****140864"
      }
    ],
    "result_code": "SUCCESS",
    "settle_no": "20230601002530020065620300064709"
  }
}
```

---

## 五、异步分账（1.3）

### 5.1 下单并支付（1.3.1）

**OpenAPI**: `alipay.trade.create`（统一收单交易创建接口）

参考同步分账中的下单并支付接口。

### 5.2 请求分账（1.3.2）

**OpenAPI**: `alipay.trade.order.settle`（统一收单交易结算接口）

参考同步分账中的请求分账接口。

### 5.3 接收异步分账消息（1.3.3）

**MsgAPI**: `alipay.trade.order.settle.notify`（交易分账结果通知接口）

#### 通知消息示例

```json
{
  "operation_dt": "2023-06-01 17:35:26",
  "royalty_detail_list": [
    {
      "amount": "10.00",
      "operation_type": "transfer",
      "trans_in": "208872****140864",
      "state": "SUCCESS",
      "detail_id": "2023060122001462650500142964"
    }
  ],
  "settle_no": "20230601002530020065620300064709",
  "trade_no": "2023060122001462650500142964"
}
```

**消息字段说明**：
- `operation_dt`: 操作时间
- `royalty_detail_list`: 分账明细列表
  - `amount`: 分账金额
  - `operation_type`: 操作类型（transfer 表示转账）
  - `trans_in`: 分账接收方账号（部分隐藏）
  - `state`: 状态（SUCCESS 表示成功）
  - `detail_id`: 明细ID
- `settle_no`: 分账批次号
- `trade_no`: 支付宝交易号

**配置说明**：
- 需要在沙箱控制台的"沙箱应用-消息服务"中配置异步通知地址
- 确保服务器能够接收并处理支付宝的异步通知

---

## 六、相关接口列表

### 6.1 分账关系相关接口

1. **alipay.trade.royalty.relation.bind** - 分账关系绑定接口
2. **alipay.trade.royalty.relation.batchquery** - 分账关系查询接口
3. **alipay.trade.royalty.rate.query** - 分账比例查询接口
4. **alipay.trade.royalty.relation.unbind** - 分账关系解绑接口

### 6.2 交易分账相关接口

1. **alipay.trade.create** - 统一收单交易创建接口
2. **alipay.trade.order.settle** - 统一收单交易结算接口
3. **alipay.trade.order.settle.query** - 交易分账查询接口
4. **alipay.trade.order.settle.notify** - 交易分账结果通知接口（异步）

---

## 七、沙箱控制台使用

### 7.1 账号管理

在沙箱控制台的"账号管理"中，可以：
- 查看沙箱账号信息
- 获取买家账号和卖家账号
- 查看账号余额等信息

### 7.2 消息服务配置

在沙箱控制台的"沙箱应用-消息服务"中，可以：
- 配置异步通知地址
- 查看消息推送记录
- 测试消息推送功能

---

## 八、测试流程建议

### 8.1 完整测试流程

1. **分账关系维护**
   - 绑定分账关系
   - 查询分账关系
   - 查询分账比例
   - （可选）解绑分账关系

2. **同步分账测试**
   - 创建订单并支付
   - 请求分账
   - 查询分账结果

3. **异步分账测试**
   - 创建订单并支付
   - 请求分账
   - 接收并处理异步通知
   - 验证分账结果

### 8.2 注意事项

1. 确保使用沙箱环境的 AppID 和密钥
2. 使用沙箱账号进行支付测试
3. 异步通知地址需要能够被支付宝访问（可使用 ngrok 等工具进行内网穿透）
4. 所有示例参数中的账号信息需要替换为实际的沙箱账号
5. 测试完成后，需要在生产环境进行验证

---

## 九、常见问题

### 9.1 如何获取沙箱账号？

在沙箱控制台的"账号管理"中可以查看和创建沙箱账号。

### 9.2 如何配置异步通知？

在沙箱控制台的"沙箱应用-消息服务"中配置异步通知地址。

### 9.3 分账失败如何处理？

1. 检查分账关系是否已正确绑定
2. 检查分账金额是否超过订单金额
3. 检查分账接收方账号是否正确
4. 查看错误码和错误信息，参考接入指南进行排查

### 9.4 沙箱环境与生产环境的区别？

- 沙箱环境数据与生产环境完全隔离
- 沙箱环境可能不支持某些高级功能
- 接口响应可能与生产环境略有差异
- 必须在生产环境进行最终测试验收

---

## 十、相关文档链接

- [沙箱环境](https://opendocs.alipay.com/open/200/105311)
- [商家分账接入指南](https://opendocs.alipay.com/open/08456h)
- [alipay.trade.royalty.relation.bind（分账关系绑定接口）](https://opendocs.alipay.com/open/08456h)
- [alipay.trade.order.settle（统一收单交易结算接口）](https://opendocs.alipay.com/open/08456h)
- [沙箱控制台](https://open.alipay.com/develop/sandbox/app)

---

**文档结束**




