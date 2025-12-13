<template>
  <div class="page-container" :class="containerClass">
    <div class="page-content">
      <!-- 页面标题区域 -->
      <header v-if="title || subtitle || $slots.header" class="page-header">
        <div v-if="title || subtitle" class="page-title-section">
          <h1 v-if="title" class="page-title">{{ title }}</h1>
          <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
        </div>
        <div v-if="$slots.header" class="page-header-extra">
          <slot name="header"></slot>
        </div>
      </header>

      <!-- 主要内容区域 -->
      <main class="page-main">
        <slot></slot>
      </main>
    </div>
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
  maxWidth: {
    type: String,
    default: '1200px'
  },
  padding: {
    type: String,
    default: 'normal' // 'none', 'small', 'normal', 'large'
  },
  background: {
    type: String,
    default: 'page' // 'page', 'white', 'transparent'
  }
})

const containerClass = computed(() => ({
  [`padding-${props.padding}`]: true,
  [`bg-${props.background}`]: true
}))
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  width: 100%;
}

.page-container.bg-page {
  background: var(--bg-page, #f6f7fb);
}

.page-container.bg-white {
  background: var(--bg-white, #fff);
}

.page-container.bg-transparent {
  background: transparent;
}

.page-content {
  max-width: v-bind('props.maxWidth');
  margin: 0 auto;
  width: 100%;
}

/* 内边距变体 */
.page-container.padding-none .page-content {
  padding: 0;
}

.page-container.padding-small .page-content {
  padding: 16px 20px;
}

.page-container.padding-normal .page-content {
  padding: 24px 20px;
}

.page-container.padding-large .page-content {
  padding: 32px 20px;
}

/* 页面标题区域 */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  gap: 20px;
}

.page-title-section {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary, #111827);
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-secondary, #6b7280);
  margin: 0;
  line-height: 1.5;
}

.page-header-extra {
  flex-shrink: 0;
}

.page-main {
  width: 100%;
}

/* 响应式 */
@media (max-width: 768px) {
  .page-container.padding-small .page-content {
    padding: 12px 16px;
  }
  
  .page-container.padding-normal .page-content {
    padding: 16px 16px;
  }
  
  .page-container.padding-large .page-content {
    padding: 20px 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    margin-bottom: 20px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .page-subtitle {
    font-size: 14px;
  }
}
</style>