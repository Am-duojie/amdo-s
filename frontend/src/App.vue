<template>
  <div class="app-wrapper">
    <el-main class="main-content">
      <router-view />
    </el-main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
}

.main-content {
  flex: 1;
  padding: 0 !important;
  margin: 0;
  background: #f5f5f5;
}

:deep(.el-main) {
  padding: 0 !important;
}
</style>
