<template>
  <section class="app-main">
    <router-view v-slot="{ Component }">
      <transition name="fade-transform" mode="out-in">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </transition>
    </router-view>
  </section>
</template>

<style scoped>
.app-main {
  padding: 12px;
  min-height: calc(100vh - 50px);
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

