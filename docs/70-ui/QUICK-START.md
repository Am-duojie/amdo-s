# UI 设计系统快速开始

## 🎯 核心理念

**一次配置，全局统一** - 通过设计令牌和可复用组件，确保整个项目的视觉一致性。

## 📦 已创建的资源

### 1. 设计系统基础

```
frontend/src/styles/
├── design-tokens.css    # 颜色、字体、间距等设计规范
└── utilities.css        # 常用工具类（flex、padding、margin等）
```

### 2. 核心组件

```
frontend/src/components/
├── BaseCard.vue         # 卡片组件
├── PageContainer.vue    # 页面容器
├── BaseButton.vue       # 按钮组件
├── BaseInput.vue        # 输入框组件
└── OrderSteps.vue       # 订单步骤条组件 ⭐ 新增
```

### 3. 文档

```
docs/70-ui/
├── ui-design-system.md       # 完整设计系统文档
├── ui-migration-plan.md      # 迁移实施计划
├── order-steps-component.md  # OrderSteps 组件文档
└── QUICK-START.md           # 本文档
```

## 🚀 5分钟快速上手

### 步骤1：使用 PageContainer 包裹页面

**旧代码：**
```vue
<template>
  <div class="page-wrapper">
    <h1>页面标题</h1>
    <div class="content">...</div>
  </div>
</template>

<style>
.page-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>
```

**新代码：**
```vue
<template>
  <PageContainer title="页面标题" subtitle="页面描述">
    ...
  </PageContainer>
</template>

<script setup>
import PageContainer from '@/components/PageContainer.vue'
</script>
```

### 步骤2：使用 BaseCard 替换 el-card

**旧代码：**
```vue
<el-card>
  <template #header>标题</template>
  内容
</el-card>
```

**新代码：**
```vue
<BaseCard title="标题" shadow="md" hover>
  内容
</BaseCard>
```

### 步骤3：使用 OrderSteps 显示订单进度

**旧代码：**
```vue
<el-steps :space="200" :active="getStepActive()">
  <el-step title="提交订单" :description="formatDate(order.created_at)"></el-step>
  <el-step title="已寄出" :description="order.shipped_at ? formatDate(order.shipped_at) : '待寄出'"></el-step>
  <!-- 更多步骤... -->
</el-steps>

<script>
const getStepActive = () => {
  // 复杂的状态映射逻辑...
}
</script>
```

**新代码：**
```vue
<OrderSteps :order="order" type="recycle" />

<script setup>
import OrderSteps from '@/components/OrderSteps.vue'
</script>
```

### 步骤4：使用设计令牌替换硬编码样式

**旧代码：**
```css
.my-element {
  color: #111827;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
```

**新代码：**
```css
.my-element {
  color: var(--text-primary);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}
```

### 步骤5：使用工具类快速布局

**旧代码：**
```vue
<div style="display: flex; align-items: center; gap: 16px; padding: 20px;">
  <span>内容</span>
</div>
```

**新代码：**
```vue
<div class="flex items-center gap-4 p-5">
  <span>内容</span>
</div>
```

## 💡 常用模式

### 标准页面布局

```vue
<template>
  <PageContainer title="页面标题" subtitle="页面描述">
    <BaseCard title="区块1" class="mb-6">
      内容1
    </BaseCard>
    
    <BaseCard title="区块2">
      内容2
    </BaseCard>
  </PageContainer>
</template>

<script setup>
import PageContainer from '@/components/PageContainer.vue'
import BaseCard from '@/components/BaseCard.vue'
</script>
```

### 两栏布局

```vue
<template>
  <PageContainer>
    <div class="grid gap-6" style="grid-template-columns: 300px 1fr;">
      <aside>
        <BaseCard>侧边栏</BaseCard>
      </aside>
      <main>
        <BaseCard>主内容</BaseCard>
      </main>
    </div>
  </PageContainer>
</template>
```

### 订单详情页

```vue
<template>
  <PageContainer title="订单详情">
    <!-- 基本信息 -->
    <BaseCard title="订单信息" class="mb-6">
      <div class="order-info-grid">
        <div class="info-item">
          <span class="label">订单号：</span>
          <span class="value">#{{ order.id }}</span>
        </div>
        <!-- 更多信息... -->
      </div>
    </BaseCard>

    <!-- 订单进度 -->
    <BaseCard title="订单进度" shadow="sm">
      <OrderSteps :order="order" type="recycle" />
    </BaseCard>
  </PageContainer>
</template>

<script setup>
import PageContainer from '@/components/PageContainer.vue'
import BaseCard from '@/components/BaseCard.vue'
import OrderSteps from '@/components/OrderSteps.vue'
</script>

<style scoped>
.order-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-4);
}

.info-item {
  display: flex;
  gap: var(--space-2);
}

.label {
  color: var(--text-secondary);
  font-weight: var(--font-medium);
}

.value {
  color: var(--text-primary);
  font-weight: var(--font-semibold);
}
</style>
```

## 🎨 设计令牌速查

### 颜色

```css
/* 主色 */
--color-primary: #ff6a00;
--color-secondary: #ffd700;

/* 功能色 */
--color-success: #10b981;
--color-warning: #f59e0b;
--color-error: #ef4444;

/* 文字 */
--text-primary: #111827;
--text-secondary: #6b7280;
--text-tertiary: #9ca3af;
```

### 间距

```css
--space-2: 8px;   /* gap-2, p-2, m-2 */
--space-4: 16px;  /* gap-4, p-4, m-4 */
--space-6: 24px;  /* gap-6, p-6, m-6 */
--space-8: 32px;  /* gap-8, p-8, m-8 */
```

### 圆角

```css
--radius-sm: 8px;    /* rounded-sm */
--radius-md: 12px;   /* rounded-md */
--radius-lg: 16px;   /* rounded-lg */
--radius-full: 9999px; /* rounded-full */
```

### 阴影

```css
--shadow-sm: 0 2px 8px rgba(0,0,0,0.04);   /* shadow-sm */
--shadow-md: 0 4px 16px rgba(0,0,0,0.08);  /* shadow-md */
--shadow-lg: 0 8px 32px rgba(0,0,0,0.12);  /* shadow-lg */
```

## 🛠️ 工具类速查

### 布局

```html
<div class="flex items-center justify-between gap-4">
<div class="grid gap-6">
<div class="hidden-mobile">  <!-- 移动端隐藏 -->
<div class="hidden-desktop"> <!-- 桌面端隐藏 -->
```

### 间距

```html
<div class="p-4">      <!-- padding: 16px -->
<div class="px-6">     <!-- padding-left/right: 24px -->
<div class="py-4">     <!-- padding-top/bottom: 16px -->
<div class="m-4">      <!-- margin: 16px -->
<div class="mb-6">     <!-- margin-bottom: 24px -->
```

### 文字

```html
<div class="text-lg font-bold text-primary">
<div class="text-sm text-secondary">
<div class="text-center">
<div class="truncate">        <!-- 单行截断 -->
<div class="line-clamp-2">    <!-- 两行截断 -->
```

### 样式

```html
<div class="rounded-lg shadow-md bg-white border">
<div class="hover-lift">      <!-- 悬停上浮 -->
<div class="transition">      <!-- 过渡动画 -->
```

## 📋 组件 Props 速查

### BaseCard

```vue
<BaseCard
  title="标题"
  subtitle="副标题"
  shadow="md"        <!-- none/sm/md/lg -->
  padding="normal"   <!-- none/small/normal/large -->
  hover              <!-- 悬停效果 -->
  clickable          <!-- 可点击 -->
>
  内容
</BaseCard>
```

### PageContainer

```vue
<PageContainer
  title="页面标题"
  subtitle="页面描述"
  maxWidth="1200px"
  padding="normal"      <!-- none/small/normal/large -->
  background="page"     <!-- page/white/transparent -->
>
  内容
</PageContainer>
```

### BaseButton

```vue
<BaseButton
  variant="primary"     <!-- primary/secondary/outline/ghost/danger/success -->
  size="md"            <!-- sm/md/lg -->
  icon="🔍"
  loading
  disabled
  block                <!-- 占满宽度 -->
>
  按钮文字
</BaseButton>
```

### OrderSteps

```vue
<OrderSteps
  :order="order"       <!-- 必填：订单对象 -->
  type="recycle"       <!-- recycle/trade/verified -->
/>
```

## 🎯 最佳实践

### ✅ 推荐做法

1. **优先使用组件**
   ```vue
   <BaseCard title="标题">内容</BaseCard>
   ```

2. **使用设计令牌**
   ```css
   color: var(--text-primary);
   ```

3. **使用工具类**
   ```html
   <div class="flex items-center gap-4">
   ```

4. **数据驱动**
   ```vue
   <OrderSteps :order="order" type="recycle" />
   ```

### ❌ 避免做法

1. **硬编码样式**
   ```css
   color: #111827;  /* ❌ 应该用 var(--text-primary) */
   ```

2. **重复造轮子**
   ```vue
   <!-- ❌ 不要自己写卡片 -->
   <div class="custom-card">...</div>
   
   <!-- ✅ 使用现成组件 -->
   <BaseCard>...</BaseCard>
   ```

3. **固定宽度布局**
   ```vue
   <!-- ❌ 在弹窗中可能被截断 -->
   <el-steps :space="200">
   
   <!-- ✅ 自动适配 -->
   <el-steps align-center>
   ```

## 📚 进一步学习

- [完整设计系统文档](./ui-design-system.md)
- [OrderSteps 组件详细文档](./order-steps-component.md)
- [迁移实施计划](./ui-migration-plan.md)
- [UI 展示页面](../../frontend/src/pages/UIShowcase.vue) - 访问 `/ui-showcase` 查看所有组件效果

## 🆘 常见问题

### Q: 我需要完全替换 Element Plus 吗？

A: 不需要！继续使用 Element Plus 的复杂组件（表格、对话框、表单等），只在简单场景使用我们的基础组件。

### Q: 旧页面需要立即改造吗？

A: 不需要。新页面直接使用新设计系统，旧页面可以逐步迁移。

### Q: 如何添加新的设计令牌？

A: 在 `frontend/src/styles/design-tokens.css` 中添加新的 CSS 变量即可。

### Q: OrderSteps 支持自定义步骤吗？

A: 目前支持三种预设类型。如需自定义，可以修改组件源码或继续使用 `el-steps`。

### Q: 移动端适配怎么处理？

A: 所有组件都已内置响应式支持，使用 `hidden-mobile` 和 `hidden-desktop` 工具类控制显示。

## 🎉 开始使用

现在你已经掌握了基础知识，可以开始改造你的页面了！

建议从访问频率最高的页面开始：
1. 首页
2. 回收订单详情页（已完成 ✅）
3. 商品列表页
4. 用户中心

祝你改造顺利！🚀
