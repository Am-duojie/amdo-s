# UI 统一规范（解决“整体 UI 乱”）

## 目标
用最小成本让“核心演示链路”视觉一致、交互一致、可维护（毕业设计阶段优先）。

## 最小设计系统（建议）
1. 页面容器统一（max-width / padding）
2. 标题区统一（标题 + 描述 + 右侧操作）
3. 卡片/表单/按钮统一间距与圆角
4. CSS 收敛到 token（变量）

## 推荐落地方式
- 新建 `frontend/src/components/PageContainer.vue`
- 新建 `frontend/src/components/PageHeaderBar.vue`
- 新建 `frontend/src/styles/tokens.css` 并在 `frontend/src/main.js` 全局引入

## 回收链路优先统一（答辩演示必做）
- `frontend/src/pages/Recycle.vue`
- `frontend/src/pages/RecycleEstimateWizard.vue`
- `frontend/src/pages/RecycleCheckout.vue`
- `frontend/src/pages/MyRecycleOrders.vue`
- `frontend/src/pages/RecycleOrderDetail.vue`

## 管理端回收订单页（关键交互）
- “流程状态”和“打款状态”分别筛选（paid 不应作为流程状态）
- 列表列聚焦：订单号/用户/机型/状态/打款/更新时间/关键动作
- 关键动作二次确认（Dialog）
