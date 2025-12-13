<template>
  <section class="app-main">
    <router-view v-slot="{ Component, route }">
      <transition name="fade-transform" mode="out-in">
        <ErrorBoundary>
          <Suspense>
            <template #default>
              <keep-alive :include="cachedViews">
                <component :is="Component" :key="route.fullPath" />
              </keep-alive>
            </template>
            <template #fallback>
              <div class="loading-container">
                <el-skeleton :rows="8" animated />
              </div>
            </template>
          </Suspense>
        </ErrorBoundary>
      </transition>
    </router-view>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ErrorBoundary from './ErrorBoundary.vue'
import { ElSkeleton } from 'element-plus'

const route = useRoute()

// 只缓存需要保持状态的页面，避免内存泄漏和状态混乱
// 默认不缓存，避免多标签页切换时的状态混乱
// 如果需要缓存某个页面，可以在路由 meta 中添加 keepAlive: true，并在这里添加对应的组件名称
const cachedViews = computed(() => {
  // 可以根据路由 meta 中的 keepAlive 属性来决定是否缓存
  // 暂时不缓存任何页面，避免多标签页场景下的状态混乱
  return []
})
</script>

<style scoped>
.app-main {
  padding: 12px;
  min-height: calc(100vh - 50px);
}

.loading-container {
  padding: 20px;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.15s ease;
}

.fade-transform-enter-from,
.fade-transform-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
</style>

