<!-- src/pages/RecycleEstimateWizard.vue (占位页：后续替换为 13 步问卷) -->
<template>
  <div class="wrap">
    <el-card shadow="never" class="card">
      <div class="title">估价信息（问卷）</div>
      <div class="desc">
        当前选择：<b>{{ deviceType }}</b> / <b>{{ brand }}</b> / <b>{{ model }}</b>
      </div>
      <el-alert
        type="info"
        :closable="false"
        title="这里先放一个占位页，下一步我们把 13 步问卷完整实现进来（与你提供的截图一致）。"
        style="margin-top: 12px"
      />
      <div class="actions">
        <el-button round @click="router.push('/recycle')">返回选择机型</el-button>
        <el-button type="primary" round @click="router.push('/recycle/checkout')">进入提交订单（占位）</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useRecycleDraftStore } from "@/stores/recycleDraft";

const route = useRoute();
const router = useRouter();
const draft = useRecycleDraftStore();

const deviceType = computed(() => (route.query.device_type as string) || draft.selection.device_type || "");
const brand = computed(() => (route.query.brand as string) || draft.selection.brand || "");
const model = computed(() => (route.query.model as string) || draft.selection.model || "");

onMounted(() => {
  draft.setSelection({ device_type: deviceType.value, brand: brand.value, model: model.value });
});
</script>

<style scoped>
.wrap { background:#f6f7fb; min-height:100vh; padding: 18px; }
.card { max-width: 900px; margin: 0 auto; border-radius: 18px; border: 1px solid #e6e8ee; }
.title { font-size: 18px; font-weight: 900; }
.desc { margin-top: 10px; color: #374151; }
.actions { margin-top: 16px; display:flex; gap: 10px; justify-content:flex-end; }
</style>
