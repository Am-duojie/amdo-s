<template>
  <div class="base-card" :class="cardClass">
    <!-- 卡片头部 -->
    <header v-if="title || subtitle || $slots.header" class="card-header">
      <div v-if="title || subtitle" class="card-title-section">
        <h3 v-if="title" class="card-title">{{ title }}</h3>
        <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.header" class="card-header-extra">
        <slot name="header"></slot>
      </div>
    </header>

    <!-- 卡片内容 -->
    <div class="card-body" :class="{ 'no-header': !title && !subtitle && !$slots.header }">
      <slot></slot>
    </div>

    <!-- 卡片底部 -->
    <footer v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  shadow: {
    type: String,
    default: 'sm', // 'none', 'sm', 'md', 'lg'
    validator: (value) => ['none', 'sm', 'md', 'lg'].includes(value)
  },
  padding: {
    type: String,
    default: 'normal', // 'none', 'small', 'normal', 'large'
    validator: (value) => ['none', 'small', 'normal', 'large'].includes(value)
  },
  hover: {
    type: Boolean,
    default: false
  },
  clickable: {
    type: Boolean,
    default: false
  }
})

const cardClass = computed(() => ({
  [`shadow-${props.shadow}`]: true,
  [`padding-${props.padding}`]: true,
  'hover-effect': props.hover,
  'clickable': props.clickable
}))
</script>

<style scoped>
.base-card {
  background: var(--bg-white, #fff);
  border-radius: var(--radius-lg, 16px);
  border: 1px solid #e6e8ee;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

/* 阴影变体 */
.base-card.shadow-none {
  box-shadow: none;
}

.base-card.shadow-sm {
  box-shadow: var(--shadow-sm, 0 2px 8px rgba(0,0,0,0.04));
}

.base-card.shadow-md {
  box-shadow: var(--shadow-md, 0 4px 16px rgba(0,0,0,0.08));
}

.base-card.shadow-lg {
  box-shadow: var(--shadow-lg, 0 8px 32px rgba(0,0,0,0.12));
}

/* Hover效果 */
.base-card.hover-effect:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg, 0 8px 32px rgba(0,0,0,0.12));
}

.base-card.clickable {
  cursor: pointer;
}

.base-card.clickable:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md, 0 4px 16px rgba(0,0,0,0.08));
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.card-title-section {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary, #111827);
  margin: 0 0 4px 0;
  line-height: 1.3;
}

.card-subtitle {
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
  margin: 0;
  line-height: 1.4;
}

.card-header-extra {
  flex-shrink: 0;
}

/* 卡片内容 */
.card-body {
  flex: 1;
}

.card-body.no-header {
  /* 当没有header时的特殊样式 */
}

/* 卡片底部 */
.card-footer {
  border-top: 1px solid #f0f0f0;
}

/* 内边距变体 */
.base-card.padding-none .card-header,
.base-card.padding-none .card-body,
.base-card.padding-none .card-footer {
  padding: 0;
}

.base-card.padding-small .card-header,
.base-card.padding-small .card-body,
.base-card.padding-small .card-footer {
  padding: 16px;
}

.base-card.padding-normal .card-header,
.base-card.padding-normal .card-body,
.base-card.padding-normal .card-footer {
  padding: 20px;
}

.base-card.padding-large .card-header,
.base-card.padding-large .card-body,
.base-card.padding-large .card-footer {
  padding: 24px;
}

/* 响应式 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .card-subtitle {
    font-size: 13px;
  }
  
  .base-card.padding-small .card-header,
  .base-card.padding-small .card-body,
  .base-card.padding-small .card-footer {
    padding: 12px;
  }
  
  .base-card.padding-normal .card-header,
  .base-card.padding-normal .card-body,
  .base-card.padding-normal .card-footer {
    padding: 16px;
  }
  
  .base-card.padding-large .card-header,
  .base-card.padding-large .card-body,
  .base-card.padding-large .card-footer {
    padding: 20px;
  }
}
</style>