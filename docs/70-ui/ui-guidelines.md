# UI 设计规范

## 概述

本文档定义了易淘二手交易平台的UI设计规范，确保整个应用的视觉一致性和用户体验。

## 设计原则

### 1. 一致性 (Consistency)
- 使用统一的设计tokens（颜色、字体、间距、圆角等）
- 保持组件行为和交互模式的一致性
- 统一的信息架构和导航模式

### 2. 简洁性 (Simplicity)
- 减少不必要的视觉元素
- 清晰的信息层次
- 直观的操作流程

### 3. 可访问性 (Accessibility)
- 足够的颜色对比度
- 清晰的焦点状态
- 支持键盘导航

## 设计系统

### 颜色系统

#### 主色调
```css
--el-color-primary: #ff6a00;        /* 主品牌色 */
--brand: #ffe400;                    /* 品牌黄色 */
--price-color: #ff2442;              /* 价格红色 */
```

#### 文字颜色
```css
--text-primary: #111827;             /* 主要文字 */
--text-secondary: #6b7280;           /* 次要文字 */
--text-light: #9ca3af;               /* 辅助文字 */
--text-muted: #d1d5db;               /* 禁用文字 */
```

#### 背景颜色
```css
--bg-page: #f6f7fb;                  /* 页面背景 */
--bg-white: #ffffff;                 /* 卡片背景 */
--bg-gray-50: #f9fafb;               /* 浅灰背景 */
--bg-gray-100: #f3f4f6;              /* 中灰背景 */
```

### 字体系统

#### 字体大小
- **大标题**: 28px (font-size: 28px; font-weight: 800)
- **中标题**: 22px (font-size: 22px; font-weight: 700)
- **小标题**: 18px (font-size: 18px; font-weight: 600)
- **正文**: 14px (font-size: 14px; font-weight: 400)
- **小字**: 12px (font-size: 12px; font-weight: 400)

#### 字体权重
- **特粗**: 800 (用于主标题)
- **粗体**: 700 (用于副标题)
- **中粗**: 600 (用于强调文字)
- **中等**: 500 (用于按钮文字)
- **常规**: 400 (用于正文)

### 间距系统

```css
--spacing-xs: 4px;                   /* 极小间距 */
--spacing-sm: 8px;                   /* 小间距 */
--spacing-md: 12px;                  /* 中间距 */
--spacing-lg: 16px;                  /* 大间距 */
--spacing-xl: 20px;                  /* 特大间距 */
--spacing-2xl: 24px;                 /* 超大间距 */
--spacing-3xl: 32px;                 /* 巨大间距 */
```

### 圆角系统

```css
--radius-xs: 4px;                    /* 极小圆角 */
--radius-sm: 8px;                    /* 小圆角 */
--radius-md: 12px;                   /* 中圆角 */
--radius-lg: 16px;                   /* 大圆角 */
--radius-xl: 20px;                   /* 特大圆角 */
--radius-full: 9999px;               /* 完全圆角 */
```

### 阴影系统

```css
--shadow-xs: 0 1px 2px rgba(0,0,0,0.05);      /* 极轻阴影 */
--shadow-sm: 0 2px 8px rgba(0,0,0,0.04);      /* 轻阴影 */
--shadow-md: 0 4px 16px rgba(0,0,0,0.08);     /* 中阴影 */
--shadow-lg: 0 8px 32px rgba(0,0,0,0.12);     /* 重阴影 */
--shadow-xl: 0 16px 48px rgba(0,0,0,0.16);    /* 超重阴影 */
```

## 组件规范

### 页面容器 (PageContainer)

用于统一页面布局和间距的容器组件。

**使用场景:**
- 所有页面的根容器
- 需要统一标题和副标题的页面

**属性:**
- `title`: 页面标题
- `subtitle`: 页面副标题
- `maxWidth`: 最大宽度 (默认: 1200px)
- `padding`: 内边距 (none/small/normal/large)
- `background`: 背景色 (page/white/transparent)

### 基础卡片 (BaseCard)

统一的卡片组件，用于内容分组。

**使用场景:**
- 信息展示卡片
- 表单容器
- 功能模块容器

**属性:**
- `title`: 卡片标题
- `subtitle`: 卡片副标题
- `shadow`: 阴影级别 (none/sm/md/lg)
- `padding`: 内边距 (none/small/normal/large)
- `hover`: 是否启用hover效果
- `clickable`: 是否可点击

### 按钮规范

#### 主要按钮
- 背景: 渐变色 (--el-color-primary 到 #ffd700)
- 圆角: var(--radius-md, 12px)
- 内边距: 12px 20px
- 字体权重: 600

#### 次要按钮
- 背景: 透明
- 边框: 1px solid var(--border-default)
- 文字颜色: var(--text-primary)

#### 危险按钮
- 背景: #ef4444
- 文字颜色: #ffffff

### 表单规范

#### 输入框
- 圆角: var(--radius-md, 12px)
- 边框: 1px solid var(--border-default)
- 聚焦状态: 2px 橙色外发光
- 内边距: 12px 16px

#### 标签
- 字体大小: 14px
- 字体权重: 600
- 颜色: var(--text-primary)
- 下边距: 8px

## 交互规范

### 悬停效果 (Hover)

#### 卡片悬停
```css
transform: translateY(-2px);
box-shadow: var(--shadow-lg);
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

#### 按钮悬停
```css
transform: translateY(-1px);
box-shadow: 0 4px 12px rgba(255, 106, 0, 0.3);
```

#### 列表项悬停
```css
transform: translateX(4px);
border-color: var(--el-color-primary);
background: #fff5e6;
```

### 过渡动画

#### 标准过渡
```css
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

#### 快速过渡
```css
transition: all 0.15s ease;
```

#### 慢速过渡
```css
transition: all 0.5s ease;
```

## 响应式设计

### 断点系统

```css
/* 手机 */
@media (max-width: 480px) { }

/* 平板 */
@media (max-width: 768px) { }

/* 小桌面 */
@media (max-width: 992px) { }

/* 中桌面 */
@media (max-width: 1200px) { }

/* 大桌面 */
@media (min-width: 1201px) { }
```

### 响应式原则

1. **移动优先**: 从小屏幕开始设计，逐步适配大屏幕
2. **内容优先**: 确保核心内容在所有设备上都能正常显示
3. **触摸友好**: 移动端按钮最小尺寸 44px × 44px
4. **性能优化**: 移动端减少动画和特效

## 可访问性规范

### 颜色对比度
- 正文文字: 至少 4.5:1
- 大文字 (18px+): 至少 3:1
- 非文字元素: 至少 3:1

### 焦点状态
```css
:focus-visible {
  outline: 2px solid var(--el-color-primary);
  outline-offset: 2px;
}
```

### 语义化HTML
- 使用正确的HTML标签 (header, main, nav, section, article)
- 为图片添加alt属性
- 为表单元素添加label

## 图标规范

### 图标大小
- **小图标**: 14px (用于按钮内)
- **中图标**: 16px (用于列表项)
- **大图标**: 20px (用于标题旁)
- **特大图标**: 24px (用于空状态)

### 图标颜色
- 默认: var(--text-secondary)
- 激活: var(--el-color-primary)
- 禁用: var(--text-muted)

## 最佳实践

### 1. 组件复用
- 优先使用 PageContainer 和 BaseCard
- 避免重复定义相同的样式
- 使用设计tokens而不是硬编码值

### 2. 性能优化
- 使用 CSS 变量减少重复代码
- 合理使用过渡动画，避免过度动画
- 图片使用适当的格式和尺寸

### 3. 维护性
- 样式文件按功能模块组织
- 使用有意义的类名
- 添加必要的注释

### 4. 测试
- 在不同设备和浏览器上测试
- 检查颜色对比度
- 验证键盘导航功能

## 更新记录

- 2024-12-13: 初始版本，定义基础设计系统和组件规范
- 2024-12-13: 优化回收主页布局，统一设计tokens