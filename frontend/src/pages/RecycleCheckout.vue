<template>
  <div class="wrap">
    <el-card shadow="never" class="card">
      <div class="title">提交订单</div>
      <div class="desc">核对估价结果与问卷答案，下一步可补充收件/收款信息。</div>

      <el-alert
        v-if="!ready"
        type="warning"
        :closable="false"
        title="请先完成机型选择与问卷"
        description="返回估价问卷确认机型、容量与问答"
        style="margin: 12px 0"
      />

      <div class="checkout-grid" v-if="ready">
        <div class="section">
          <div class="section-title">设备信息</div>
          <div class="row"><span>机型：</span><b>{{ deviceLine }}</b></div>
          <div class="row"><span>容量：</span><b>{{ draft.storage || "--" }}</b></div>
          <div class="row"><span>成色：</span><b>{{ conditionText }}</b></div>
        </div>

        <div class="section">
          <div class="section-title">预计到手价</div>
          <div class="price">{{ estimatedPriceText }}</div>
          <div class="row" v-if="draft.bonus">包含额外加价：¥{{ Number(draft.bonus).toFixed(2) }}</div>
          <div class="row" v-else>无额外加价</div>
        </div>

        <div class="section">
          <div class="section-title">问卷答案</div>
          <div class="answer-list">
            <div v-for="item in answersSummary" :key="item.key" class="answer-item">
              <div class="answer-label">{{ item.label }}</div>
              <div class="answer-value">{{ item.value || "未填写" }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="actions">
        <el-button round @click="router.push('/recycle/estimate')">返回问卷</el-button>
        <el-button type="primary" round :disabled="!ready">提交（占位）</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useRecycleDraftStore, type ConditionLevel } from "@/stores/recycleDraft";

const router = useRouter();
const draft = useRecycleDraftStore();

const deviceLine = computed(() => {
  const arr = [draft.selection.device_type, draft.selection.brand, draft.selection.model].filter(Boolean);
  return arr.join(" / ") || "--";
});

const conditionText = computed(() => {
  const map: Record<ConditionLevel, string> = {
    new: "全新",
    like_new: "近新",
    good: "良好",
    fair: "一般",
    poor: "较差",
  };
  return draft.condition ? map[draft.condition] || draft.condition : "--";
});

const estimatedPriceText = computed(() => {
  if (draft.estimated_price != null) return `¥${Number(draft.estimated_price).toFixed(2)}`;
  return "--";
});

const ready = computed(() => !!(draft.selection.device_type && draft.selection.brand && draft.selection.model && draft.storage));

const stepLabels: Record<string, string> = {
  channel: "购买渠道",
  color: "颜色",
  storage: "内存/存储",
  usage: "使用情况",
  accessories: "有无配件",
  screen_appearance: "屏幕外观",
  body: "机身外壳",
  display: "屏幕显示",
  front_camera: "前摄拍照",
  rear_camera: "后摄拍照",
  repair: "维修情况",
  screen_repair: "屏幕维修情况",
  functional: "功能性问题",
};

function formatAnswer(val: any) {
  if (!val) return "";
  if (Array.isArray(val)) {
    return val.map((v) => v.label || v.value || "").filter(Boolean).join("、");
  }
  return val.label || val.value || "";
}

const answersSummary = computed(() =>
  Object.entries(draft.answers || {}).map(([key, value]) => ({
    key,
    label: stepLabels[key] || key,
    value: formatAnswer(value),
  }))
);
</script>

<style scoped>
.wrap { background: #f6f7fb; min-height: 100vh; padding: 18px; }
.card { border-radius: 18px; border: 1px solid #e6e8ee; }
.title { font-size: 18px; font-weight: 900; }
.desc { margin-top: 6px; color: #6b7280; }
.checkout-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; margin-top: 12px; }
.section { padding: 12px; border: 1px solid #eef0f4; border-radius: 12px; background: #fff; }
.section-title { font-weight: 800; margin-bottom: 8px; }
.row { color: #374151; margin-bottom: 6px; }
.price { font-size: 22px; font-weight: 900; }
.answer-list { display: flex; flex-direction: column; gap: 8px; }
.answer-item { padding: 10px; border: 1px dashed #e6e8ee; border-radius: 10px; background: #f9fafb; }
.answer-label { font-weight: 700; }
.answer-value { color: #6b7280; margin-top: 4px; }
.actions { margin-top: 16px; display: flex; gap: 10px; justify-content: flex-end; }
</style>
