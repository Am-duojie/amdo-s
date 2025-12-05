<template>
  <div class="quick-sidebar">
    <button class="qs-item" @click="$router.push('/publish')">➕<span>发闲置</span></button>
    <button class="qs-item" @click="$router.push('/messages')">💬<span>消息</span></button>
    <button class="qs-item" @click="openService">👤<span>客服</span></button>
    <div class="qs-divider"></div>
    <button class="qs-item back-top" @click="backToTop">⬆️<span>回到顶部</span></button>
  </div>
</template>

<script setup>
const openService = () => {}
const backToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.quick-sidebar {
  position: fixed;
  right: 16px;
  top: 30%;
  z-index: 999;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 12px 10px;
  background: #fff;
  border-radius: 28px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  border: 1px solid #eee;
}
.qs-item {
  width: 72px;
  height: 56px;
  border: none;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  font-size: 16px;
}
.qs-item span { font-size: 12px; color: #333; }
.qs-item:hover { background: #f7f7f7; }
.qs-divider { width: 100%; height: 1px; background: #eee; margin: 2px 0; }
.back-top { background: #ffe400; }
.back-top:hover { background: #ffd600; }
</style>
