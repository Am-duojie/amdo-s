<template>
  <el-page-header class="app-page-header" @back="handleBack">
    <template #breadcrumb />
    <template #icon />
    <template #title />
    <template #content>
      <div class="header-main">
        <div class="header-title">{{ title }}</div>
        <div v-if="subtitle" class="header-subtitle">{{ subtitle }}</div>
      </div>
    </template>
    <template #extra>
      <div class="header-extra">
        <slot name="extra" />
      </div>
    </template>
    <template #default>
      <slot />
    </template>
  </el-page-header>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  showBack: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

const handleBack = () => {
  if (!props.showBack) return
  router.back()
}
</script>

<style scoped>
.app-page-header {
  background: #fff;
  border-bottom: 1px solid #eef1f5;
  padding: 12px 20px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.header-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.header-subtitle {
  font-size: 12px;
  color: #6b7280;
}

.header-extra {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
