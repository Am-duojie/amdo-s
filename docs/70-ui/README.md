# UI 设计系统文档目录

欢迎使用项目 UI 设计系统！本目录包含了完整的设计规范、组件文档和使用指南。

## 📖 文档导航

### 🚀 [快速开始](./QUICK-START.md)
**推荐首先阅读** - 5分钟快速上手，了解核心概念和常用模式。

适合：
- 新加入项目的开发者
- 需要快速查阅的场景
- 了解基本用法

### 📐 [完整设计系统](./ui-design-system.md)
详细的设计规范和组件文档，包括设计令牌、核心组件、布局模式等。

适合：
- 深入了解设计系统
- 查阅组件完整 API
- 学习最佳实践

### 🔄 [迁移实施计划](./ui-migration-plan.md)
将现有页面迁移到新设计系统的详细计划和步骤。

适合：
- 项目负责人
- 需要改造旧页面
- 了解改造进度

### 📊 [OrderSteps 组件](./order-steps-component.md)
订单步骤条组件的详细文档，包括使用方法、Props、状态映射等。

适合：
- 使用订单步骤条
- 了解组件实现细节
- 自定义步骤配置

## 🎯 核心特性

### 1. 设计令牌系统
统一的颜色、字体、间距、圆角等设计规范，确保视觉一致性。

```css
/* 使用设计令牌 */
.my-element {
  color: var(--text-primary);
  padding: var(--space-4);
  border-radius: var(--radius-md);
}
```

### 2. 可复用组件库
开箱即用的基础组件，快速构建页面。

```vue
<PageContainer title="页面标题">
  <BaseCard title="卡片标题">
    内容
  </BaseCard>
</PageContainer>
```

### 3. 工具类系统
常用的 CSS 工具类，快速实现布局和样式。

```html
<div class="flex items-center gap-4 p-6 rounded-lg shadow-md">
  内容
</div>
```

### 4. 数据驱动组件
智能组件自动处理复杂逻辑，减少重复代码。

```vue
<OrderSteps :order="order" type="recycle" />
```

## 📦 已创建的资源

### 样式文件
```
frontend/src/styles/
├── design-tokens.css    # 设计令牌（颜色、字体、间距等）
└── utilities.css        # 工具类（flex、padding、margin等）
```

### 组件文件
```
frontend/src/components/
├── BaseCard.vue         # 卡片组件
├── PageContainer.vue    # 页面容器
├── BaseButton.vue       # 按钮组件
├── BaseInput.vue        # 输入框组件
└── OrderSteps.vue       # 订单步骤条组件
```

### 示例页面
```
frontend/src/pages/
├── UIShowcase.vue       # UI 展示页面（访问 /ui-showcase）
└── RecycleNew.vue       # 已使用新设计系统的示例
```

## 🎨 设计原则

1. **一致性** - 所有页面使用相同的设计语言
2. **简洁性** - 界面简洁明了，避免过度设计
3. **响应式** - 自动适配各种屏幕尺寸
4. **可访问性** - 符合无障碍标准
5. **可维护** - 集中管理样式，易于修改

## 🚀 快速示例

### 创建一个新页面

```vue
<template>
  <PageContainer 
    title="我的页面" 
    subtitle="页面描述"
    background="page"
  >
    <!-- 信息卡片 -->
    <BaseCard title="基本信息" class="mb-6">
      <div class="flex flex-col gap-4">
        <div class="flex items-center gap-2">
          <span class="text-secondary">用户名：</span>
          <span class="font-semibold">张三</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-secondary">邮箱：</span>
          <span class="font-semibold">zhangsan@example.com</span>
        </div>
      </div>
    </BaseCard>

    <!-- 订单进度 -->
    <BaseCard title="订单进度" shadow="sm">
      <OrderSteps :order="order" type="recycle" />
    </BaseCard>

    <!-- 操作按钮 -->
    <BaseCard>
      <div class="flex gap-3">
        <BaseButton variant="primary" @click="handleSubmit">
          提交
        </BaseButton>
        <BaseButton variant="secondary" @click="handleCancel">
          取消
        </BaseButton>
      </div>
    </BaseCard>
  </PageContainer>
</template>

<script setup>
import { ref } from 'vue'
import PageContainer from '@/components/PageContainer.vue'
import BaseCard from '@/components/BaseCard.vue'
import BaseButton from '@/components/BaseButton.vue'
import OrderSteps from '@/components/OrderSteps.vue'

const order = ref({
  status: 'shipped',
  created_at: '2025-12-14T17:47:13',
  shipped_at: '2025-12-14T18:30:00'
})

const handleSubmit = () => {
  console.log('提交')
}

const handleCancel = () => {
  console.log('取消')
}
</script>
```

## 📊 改造进度

### 已完成 ✅
- [x] 设计令牌系统
- [x] 工具类库
- [x] 核心组件（BaseCard、PageContainer、BaseButton、BaseInput）
- [x] OrderSteps 组件
- [x] RecycleNew.vue 页面改造
- [x] RecycleOrderDetail.vue 步骤条优化
- [x] OrderDetail.vue 步骤条优化
- [x] VerifiedOrderDetail.vue 步骤条优化

### 进行中 🚧
- [ ] 首页改造
- [ ] 商品列表页改造
- [ ] 用户中心改造

### 待开始 📋
- [ ] 其他页面逐步迁移
- [ ] 管理后台改造
- [ ] 添加更多组件（Select、Textarea、Checkbox等）

## 🛠️ 开发工具

### 查看 UI 展示页面
访问 `/ui-showcase` 路由查看所有组件的效果和用法。

### 使用 VS Code 插件
推荐安装以下插件提升开发体验：
- Volar - Vue 3 支持
- CSS Variable Autocomplete - CSS 变量自动补全
- Tailwind CSS IntelliSense - 工具类提示（参考）

## 📞 获取帮助

### 遇到问题？

1. **查阅文档** - 先查看相关文档是否有解答
2. **查看示例** - 参考 UIShowcase.vue 和 RecycleNew.vue
3. **查看源码** - 组件源码都有详细注释
4. **提出问题** - 在团队群里讨论

### 常见问题

- [设计系统 FAQ](./ui-design-system.md#最佳实践)
- [OrderSteps FAQ](./order-steps-component.md#注意事项)
- [快速开始 FAQ](./QUICK-START.md#常见问题)

## 🎯 下一步

1. **阅读快速开始** - [QUICK-START.md](./QUICK-START.md)
2. **查看示例页面** - 访问 `/ui-showcase`
3. **开始改造页面** - 从简单页面开始
4. **分享经验** - 帮助团队成员使用新系统

## 📝 更新日志

### 2025-12-14
- ✨ 创建设计令牌系统
- ✨ 创建核心组件库
- ✨ 创建 OrderSteps 组件
- ✨ 优化订单详情页面步骤条
- 📝 编写完整文档

---

**让我们一起打造更好的用户体验！** 🎉
