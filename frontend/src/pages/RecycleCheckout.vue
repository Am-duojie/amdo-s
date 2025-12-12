<!-- src/pages/RecycleCheckout.vue (占位页：后续替换为“提交订单”页) -->
<template>
  <div class="wrap">
    <el-card shadow="never" class="card">
      <div class="title">提交订单（占位）</div>
      <el-alert
        type="warning"
        :closable="false"
        title="这里后续会实现：预计到手价、取件方式（顺丰/京东/自寄）、收款信息弹窗、协议勾选与提交。"
        style="margin-top: 12px"
      />
      <div class="actions">
        <el-button round @click="router.push('/recycle/estimate')">返回问卷</el-button>
        <el-button type="primary" round @click="router.push('/my/recycle-orders')">去我的回收单</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
const router = useRouter();
</script>

<style scoped>
.wrap { background:#f6f7fb; min-height:100vh; padding: 18px; }
.card { max-width: 900px; margin: 0 auto; border-radius: 18px; border: 1px solid #e6e8ee; }
.title { font-size: 18px; font-weight: 900; }
.actions { margin-top: 16px; display:flex; gap: 10px; justify-content:flex-end; }
</style>
