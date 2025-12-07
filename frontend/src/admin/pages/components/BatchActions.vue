<template>
  <div class="batch-actions" v-if="selectedItems.length > 0">
    <el-alert
      :closable="false"
      type="info"
      style="margin-bottom: 12px"
    >
      <template #default>
        <span>已选择 <strong>{{ selectedItems.length }}</strong> 项</span>
        <el-button
          type="text"
          style="margin-left: 12px"
          @click="clearSelection"
        >
          清空选择
        </el-button>
      </template>
    </el-alert>
    <div class="action-buttons">
      <slot :selectedItems="selectedItems" :clearSelection="clearSelection" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  selectedItems: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['clear'])

const clearSelection = () => {
  emit('clear')
}
</script>

<style scoped>
.batch-actions {
  margin-bottom: 16px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>





