<template>
  <div v-if="hasError" class="error-boundary">
    <el-result
      icon="error"
      title="页面加载失败"
      sub-title="页面渲染时出现错误，请尝试刷新或联系管理员"
    >
      <template #extra>
        <el-space>
          <el-button type="primary" @click="handleRetry">重试</el-button>
          <el-button @click="handleGoHome">返回首页</el-button>
        </el-space>
      </template>
    </el-result>
    <div v-if="errorInfo" class="error-details" style="margin-top: 20px; padding: 16px; background: #f5f5f5; border-radius: 4px;">
      <el-collapse>
        <el-collapse-item title="错误详情（点击展开）" name="error">
          <pre style="white-space: pre-wrap; word-break: break-all; font-size: 12px; color: #666;">{{ errorInfo }}</pre>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
  <slot v-else />
</template>

<script setup>
import { ref, onErrorCaptured, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElResult, ElButton, ElSpace, ElCollapse, ElCollapseItem } from 'element-plus'

const router = useRouter()
const hasError = ref(false)
const errorInfo = ref('')

onErrorCaptured((err, instance, info) => {
  console.error('ErrorBoundary caught error:', err, info)
  hasError.value = true
  errorInfo.value = `${err?.message || '未知错误'}\n\n堆栈信息:\n${err?.stack || '无'}\n\n组件信息: ${info || '无'}`
  return false // 阻止错误继续传播
})

const handleRetry = () => {
  hasError.value = false
  errorInfo.value = ''
  // 强制刷新当前路由
  router.replace({ path: '/redirect' + router.currentRoute.value.fullPath })
}

const handleGoHome = () => {
  hasError.value = false
  errorInfo.value = ''
  router.push('/admin/dashboard')
}

// 监听路由变化，清除错误状态
watch(() => router.currentRoute.value.fullPath, () => {
  if (hasError.value) {
    hasError.value = false
    errorInfo.value = ''
  }
})
</script>

<style scoped>
.error-boundary {
  padding: 40px 20px;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>










