# 测试计划与用例（毕业设计版）

## 测试范围与策略
- 集成测试（推荐）：核心 API 链路（订单、回收、管理端）
- E2E/手工回归（答辩必备）：准备一套“演示用例 + 截图证据”

## 核心回归用例
### 用户端：回收链路
1. 回收入口 → 选择机型 → 进入估价问卷
2. 完成问卷 → 提交回收订单
3. “我的回收订单”可见新订单；详情页状态显示正确

### 管理端：回收订单管理
1. 状态筛选可用（pending/quoted/confirmed/shipped/inspected/completed/cancelled）
2. 打款筛选可用（pending/paid/failed）且参数为 `payment_status`
3. 更新流程状态后，用户端状态同步
4. 更新打款状态后，列表/详情同步显示

### 支付（如纳入演示）
1. 创建支付 URL
2. 回调 notify：验签与幂等
3. 查询支付：状态一致

## 现有脚本
- `backend/scripts/settlement_self_check.py`：结算自检
- `backend/scripts/retry_settlement.py`：结算重试
