<template>
  <div class="wizard-wrap" v-if="deviceReady">
    <div class="top-bar">
      <div>
        <div class="title">估价信息</div>
        <div class="subtitle">步骤 {{ currentStep }} / {{ totalSteps }}</div>
        <div class="device-line">
          <span class="device-chip">{{ deviceType }}</span>
          <span class="sep">/</span>
          <span class="device-chip">{{ brand }}</span>
          <span class="sep">/</span>
          <span class="device-chip">{{ model }}</span>
          <el-tag v-if="selectedStorage" round size="small" class="storage-tag">{{ selectedStorage }}</el-tag>
        </div>
      </div>
      <div class="price-preview">
        <div class="price-label">预计到手价</div>
        <div class="price-value">{{ estimatedPriceText }}</div>
        <div class="condition-tip" v-if="draft.condition">按成色：{{ conditionText }}</div>
      </div>
    </div>

    <el-row :gutter="16" class="wizard-body">
      <el-col :span="16" :xs="24">
        <div class="questions-container">
          <!-- 已回答的问题（收起状态） -->
          <el-card
            v-for="(step, idx) in answeredSteps"
            :key="step.key"
            shadow="never"
            class="card question-card collapsed"
          >
            <div class="collapsed-question">
              <div class="collapsed-content">
                <div class="collapsed-title">{{ idx + 1 }}. {{ step.title }}</div>
                <div class="collapsed-answer">{{ getAnswerText(step.key) }}</div>
              </div>
              <el-button
                text
                type="primary"
                size="small"
                class="edit-btn"
                @click="expandQuestion(idx + 1)"
              >
                <el-icon><Edit /></el-icon>
                修改
              </el-button>
            </div>
          </el-card>

          <!-- 当前问题（展开状态） -->
          <el-card shadow="never" class="card question-card expanded">
            <div class="step-head">
              <div>
                <div class="step-title">{{ currentStep }}. {{ activeStep.title }}</div>
                <div class="step-hint" v-if="activeStep.helper">{{ activeStep.helper }}</div>
              </div>
              <el-tag size="small" v-if="activeStep.key === 'functional'">可多选</el-tag>
            </div>

            <el-alert
              v-if="loadError"
              :title="loadError"
              type="error"
              :closable="false"
              show-icon
              style="margin-bottom: 10px"
            />

            <div class="options-grid">
              <div
                v-for="opt in activeStep.options"
                :key="opt.value"
                class="option-card"
                :class="{ active: isSelected(activeStep.key, opt) }"
                @click="selectOption(activeStep, opt)"
              >
                <div class="option-label">{{ opt.label }}</div>
                <div class="option-desc" v-if="opt.desc">{{ opt.desc }}</div>
              </div>
            </div>

            <div v-if="activeStep.key === 'storage' && !storageOptions.length && !loadingCatalog" class="empty-tip">
              该机型暂未提供容量信息，请返回重新选择机型。
            </div>
            <div v-if="loadingCatalog" class="empty-tip">容量数据加载中...</div>

            <div class="nav">
              <el-button round :disabled="currentStep === 1" @click="goPrev">上一题</el-button>
              <div class="nav-right">
                <el-button v-if="currentStep < totalSteps" type="primary" round @click="goNext">下一题</el-button>
                <el-button v-else type="primary" round :disabled="!canCheckout" @click="goCheckout">去提交订单</el-button>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
      <el-col :span="8" :xs="24">
        <el-card shadow="never" class="card summary-card">
          <div class="summary-title">已选答案</div>
          <div class="summary-list">
            <div v-for="item in summaryList" :key="item.key" class="summary-item" @click="jumpTo(item.step)">
              <div class="summary-step">#{{ item.step }}</div>
              <div class="summary-content">
                <div class="summary-label">{{ item.title }}</div>
                <div class="summary-answer">{{ item.answer || "未填写" }}</div>
              </div>
              <el-button text type="primary" size="small">编辑</el-button>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="card price-card">
          <div class="summary-title">预计到手价</div>
          <div class="price-value large">{{ estimatedPriceText }}</div>
          <div class="condition-tip" v-if="draft.condition">按成色：{{ conditionText }}</div>
          <div class="estimate-status" v-if="estimateError">{{ estimateError }}</div>
          <div class="estimate-status" v-else-if="estimating">正在根据所选信息估价...</div>
          <div class="estimate-status" v-else-if="!shouldEstimate">选择容量与成色后自动估价</div>
        </el-card>
      </el-col>
    </el-row>
  </div>

  <div v-else class="wizard-wrap">
    <el-card shadow="never" class="card">
      <div class="title">请先选择机型</div>
      <div class="step-hint">从回收首页选择品牌与机型后再进入问卷。</div>
      <div style="margin-top: 12px">
        <el-button round @click="router.push('/recycle')">返回选择机型</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Edit } from "@element-plus/icons-vue";
import { getRecycleCatalog, estimateRecyclePrice } from "@/api/recycle";
import { useRecycleDraftStore, type ConditionLevel } from "@/stores/recycleDraft";

type Impact = "positive" | "minor" | "major" | "critical";
type StepKey =
  | "channel"
  | "color"
  | "storage"
  | "usage"
  | "accessories"
  | "screen_appearance"
  | "body"
  | "display"
  | "front_camera"
  | "rear_camera"
  | "repair"
  | "screen_repair"
  | "functional";
type StepOption = { value: string; label: string; desc?: string; impact?: Impact };
type StepItem = { key: StepKey; title: string; helper?: string; type?: "multi" | "single"; options: StepOption[] };

const route = useRoute();
const router = useRouter();
const draft = useRecycleDraftStore();

const storages = ref<string[]>([]);
const loadingCatalog = ref(false);
const loadError = ref("");

const estimating = ref(false);
const estimateError = ref("");

const deviceType = computed(() => (route.query.device_type as string) || draft.selection.device_type || "");
const brand = computed(() => (route.query.brand as string) || draft.selection.brand || "");
const model = computed(() => (route.query.model as string) || draft.selection.model || "");
const deviceReady = computed(() => !!(deviceType.value && brand.value && model.value));

const isApple = computed(() => brand.value?.includes("苹果") || brand.value?.toLowerCase()?.includes("apple"));

const storageOptions = computed<StepOption[]>(() => storages.value.map((s) => ({ value: s, label: s })));

const baseSteps = computed<StepItem[]>(() => [
  {
    key: "channel",
    title: "购买渠道",
    helper: "官方直营/运营商/第三方等",
    options: [
      { value: "official", label: "官方/直营", desc: "官网/直营店" },
      { value: "operator", label: "运营商/合约" },
      { value: "online", label: "第三方电商" },
      { value: "secondhand", label: "二手/转手" },
    ],
  },
  {
    key: "color",
    title: "颜色",
    options: [
      { value: "black", label: "黑/深色" },
      { value: "white", label: "白/浅色" },
      { value: "blue", label: "蓝/紫/冷色" },
      { value: "gold", label: "金/粉/暖色" },
      { value: "other", label: "其他颜色" },
    ],
  },
  {
    key: "storage",
    title: "内存 / 存储",
    helper: "选容量以便精准估价",
    options: storageOptions.value.length ? storageOptions.value : [],
  },
  {
    key: "usage",
    title: "使用情况",
    options: [
      { value: "unopened", label: "全新未拆封", impact: "positive" },
      { value: "light", label: "几乎全新，使用很少", impact: "positive" },
      { value: "normal", label: "正常使用痕迹", impact: "minor" },
      { value: "heavy", label: "明显使用痕迹/重度使用", impact: "major" },
    ],
  },
  {
    key: "accessories",
    title: "有无配件",
    options: [
      { value: "full", label: "配件齐全（盒/充/线）", impact: "positive" },
      { value: "partial", label: "有部分配件", impact: "minor" },
      { value: "none", label: "仅裸机", impact: "minor" },
    ],
  },
  {
    key: "screen_appearance",
    title: "屏幕外观",
    options: [
      { value: "perfect", label: "完美无瑕", impact: "positive" },
      { value: "micro-scratch", label: "细微划痕", impact: "minor" },
      { value: "light-scratch", label: "轻微划痕", impact: "minor" },
      { value: "obvious-scratch", label: "明显划痕/磕碰", impact: "major" },
      { value: "broken", label: "碎裂/脱胶", impact: "critical" },
    ],
  },
  {
    key: "body",
    title: "机身外壳",
    options: [
      { value: "body-perfect", label: "完美无瑕", impact: "positive" },
      { value: "body-micro", label: "细微划痕", impact: "minor" },
      { value: "body-light", label: "轻微划痕/掉漆", impact: "minor" },
      { value: "body-obvious", label: "明显磕碰/掉漆", impact: "major" },
      { value: "body-crack", label: "碎裂/缺角", impact: "critical" },
    ],
  },
  {
    key: "display",
    title: "屏幕显示",
    options: [
      { value: "display-ok", label: "显示正常", impact: "positive" },
      { value: "display-spot", label: "色差/亮斑/坏点", impact: "minor" },
      { value: "display-shadow", label: "残影/烧屏", impact: "major" },
      { value: "display-leak", label: "漏液/花屏", impact: "critical" },
    ],
  },
  {
    key: "front_camera",
    title: "前摄拍照",
    options: [
      { value: "front-ok", label: "正常", impact: "positive" },
      { value: "front-spot", label: "有斑/坏点", impact: "major" },
      { value: "front-fail", label: "无法拍照/已维修", impact: "critical" },
    ],
  },
  {
    key: "rear_camera",
    title: "后摄拍照",
    options: [
      { value: "rear-ok", label: "正常", impact: "positive" },
      { value: "rear-spot", label: "有斑/坏点", impact: "major" },
      { value: "rear-fail", label: "无法拍照/已维修", impact: "critical" },
    ],
  },
  {
    key: "repair",
    title: isApple.value ? "苹果维修情况" : "维修情况（机身）",
    options: [
      { value: "no-repair", label: "无拆修/无改", impact: "positive" },
      { value: "minor-repair", label: "后壳贴标/轻微溢胶", impact: "minor" },
      { value: "battery-repair", label: "维修或更换电池", impact: "major" },
      { value: "board-repair", label: "主板维修/扩容/进水", impact: "critical" },
    ],
  },
  {
    key: "screen_repair",
    title: "屏幕维修情况",
    options: [
      { value: "screen-none", label: "无拆修", impact: "positive" },
      { value: "glass", label: "更换外层玻璃", impact: "minor" },
      { value: "assembly", label: "屏幕总成维修/更换", impact: "major" },
      { value: "popup", label: "弹窗未知/第三方屏", impact: "major" },
    ],
  },
  {
    key: "functional",
    title: "功能性问题（可多选）",
    helper: "不勾选则视为全部正常",
    type: "multi",
    options: [
      { value: "none", label: "都没有问题", impact: "positive" },
      { value: "touch", label: "触控异常", impact: "major" },
      { value: "vibration", label: "震动/闪光灯异常", impact: "major" },
      { value: "biometric", label: "指纹/FaceID异常", impact: "critical" },
      { value: "audio", label: "听筒/麦克风/扬声器异常", impact: "major" },
      { value: "signal", label: "WiFi/信号弱", impact: "major" },
      { value: "buttons", label: "按键失灵", impact: "major" },
      { value: "charge", label: "无法充电或接触不良", impact: "critical" },
      { value: "water", label: "进水/潮湿腐蚀", impact: "critical" },
      { value: "pc", label: "无法连接电脑", impact: "major" },
      { value: "nfc", label: "NFC异常", impact: "minor" },
    ],
  },
]);

const totalSteps = computed(() => baseSteps.value.length);
const currentStep = computed(() => Math.min(Math.max(draft.currentStep || 1, 1), totalSteps.value));
const activeStep = computed(() => baseSteps.value[currentStep.value - 1] || baseSteps.value[0]);
const answers = computed(() => draft.answers as Record<StepKey, StepOption | StepOption[]>);

// 已回答的问题列表（收起状态）
const answeredSteps = computed(() => {
  return baseSteps.value
    .slice(0, currentStep.value - 1)
    .filter((step) => {
      const ans = answers.value[step.key];
      return ans !== undefined && ans !== null && (Array.isArray(ans) ? ans.length > 0 : true);
    });
});

const selectedStorage = computed(() => {
  const a = answers.value["storage"] as StepOption | undefined;
  if (!a) return undefined;
  return a.value;
});

const conditionText = computed(() => {
  const mapping: Record<ConditionLevel, string> = {
    new: "全新",
    like_new: "近新",
    good: "良好",
    fair: "一般",
    poor: "较差",
  };
  return draft.condition ? mapping[draft.condition] || draft.condition : "--";
});

const estimatedPriceText = computed(() => {
  if (draft.estimated_price != null) {
    return `¥${Number(draft.estimated_price).toFixed(2)}`;
  }
  return "--";
});

const shouldEstimate = computed(
  () => deviceReady.value && !!selectedStorage.value && !!draft.condition && !!model.value && !!brand.value
);

const canCheckout = computed(() => !!selectedStorage.value && !!draft.condition);

function isSelected(stepKey: StepKey, option: StepOption) {
  const ans = answers.value[stepKey];
  if (!ans) return false;
  if (Array.isArray(ans)) {
    return ans.some((x) => x.value === option.value);
  }
  return (ans as StepOption).value === option.value;
}

function goNext() {
  if (currentStep.value < totalSteps.value) {
    draft.setCurrentStep(currentStep.value + 1);
  }
}

function goPrev() {
  if (currentStep.value > 1) {
    draft.setCurrentStep(currentStep.value - 1);
  }
}

function jumpTo(step: number) {
  draft.setCurrentStep(step);
}

function selectOption(step: StepItem, option: StepOption) {
  if (step.type === "multi") {
    const current = Array.isArray(answers.value[step.key]) ? (answers.value[step.key] as StepOption[]) : [];
    let next = current.some((x) => x.value === option.value)
      ? current.filter((x) => x.value !== option.value)
      : [...current, option];
    if (option.value === "none") {
      next = [option];
    } else {
      next = next.filter((x) => x.value !== "none");
    }
    draft.setAnswer(step.key, next);
  } else {
    draft.setAnswer(step.key, option);
    if (step.key === "storage") {
      draft.setStorage(option.value);
    }
    // 单选问题：选择后自动跳转到下一个问题
    if (currentStep.value < totalSteps.value) {
      // 延迟跳转，让用户看到选择效果
      setTimeout(() => {
        goNext();
      }, 200);
    }
  }
  draft.setQuote(null, null);
  updateCondition();
}

// 获取答案文本
function getAnswerText(stepKey: StepKey): string {
  const ans = answers.value[stepKey];
  if (!ans) return "未填写";
  if (Array.isArray(ans)) {
    return ans.length > 0 ? ans.map((x: StepOption) => x.label).join("、") : "未填写";
  }
  return (ans as StepOption).label;
}

// 展开指定问题
function expandQuestion(step: number) {
  draft.setCurrentStep(step);
}

function deriveCondition(ans: Record<string, any>): ConditionLevel {
  const options: StepOption[] = [];
  Object.values(ans || {}).forEach((v) => {
    if (!v) return;
    if (Array.isArray(v)) {
      options.push(...(v as StepOption[]));
    } else if (typeof v === "object") {
      options.push(v as StepOption);
    }
  });

  const hasCritical = options.some((x) => x.impact === "critical");
  const hasMajor = options.some((x) => x.impact === "major");
  const hasMinor = options.some((x) => x.impact === "minor");
  const usage = (ans["usage"] as StepOption | undefined)?.value;

  if (hasCritical) return "poor";
  if (hasMajor) return "fair";
  if (usage === "unopened") return "new";
  if (usage === "light" && !hasMinor) return "like_new";
  if (hasMinor) return "good";
  if (usage === "heavy") return "fair";
  return "good";
}

function updateCondition() {
  const condition = deriveCondition(draft.answers || {});
  draft.setCondition(condition);
}

async function loadStorages() {
  if (!deviceReady.value) return;
  loadingCatalog.value = true;
  loadError.value = "";
  try {
    const { data } = await getRecycleCatalog({
      device_type: deviceType.value,
      brand: brand.value,
      model: model.value,
    });
    const modelList = data.models?.[deviceType.value]?.[brand.value] || [];
    const target = modelList.find((m) => m.name === model.value);
    storages.value = target?.storages || [];
  } catch (error: any) {
    loadError.value = error?.response?.data?.detail || error?.message || "获取容量数据失败";
    storages.value = [];
    ElMessage.error(loadError.value);
  } finally {
    loadingCatalog.value = false;
  }
}

let estimateTimer: number | undefined;

async function runEstimate() {
  if (!shouldEstimate.value) return;
  estimating.value = true;
  estimateError.value = "";
  try {
    const { data } = await estimateRecyclePrice({
      device_type: deviceType.value,
      brand: brand.value,
      model: model.value,
      storage: selectedStorage.value || "",
      condition: draft.condition || "good",
    });
    draft.setQuote(data?.estimated_price ?? null, data?.bonus ?? null);
  } catch (error: any) {
    estimateError.value = error?.response?.data?.error || error?.message || "估价失败";
    draft.setQuote(null, null);
    ElMessage.error(estimateError.value);
  } finally {
    estimating.value = false;
  }
}

watch(
  () => [selectedStorage.value, draft.condition, deviceType.value, brand.value, model.value],
  () => {
    if (estimateTimer) window.clearTimeout(estimateTimer);
    if (!shouldEstimate.value) return;
    estimateTimer = window.setTimeout(runEstimate, 300);
  }
);

watch(
  () => storages.value,
  (list) => {
    if (list.length && !selectedStorage.value) {
      const first = { value: list[0], label: list[0] };
      draft.setAnswer("storage", first);
      draft.setStorage(first.value);
      updateCondition();
    }
  }
);

const summaryList = computed(() =>
  baseSteps.value.map((s, idx) => {
    const ans = answers.value[s.key];
    let text = "";
    if (Array.isArray(ans)) {
      text = ans.map((x: StepOption) => x.label).join("、");
    } else if (ans) {
      text = (ans as StepOption).label;
    }
    return { key: s.key, step: idx + 1, title: s.title, answer: text };
  })
);

function goCheckout() {
  if (!canCheckout.value) {
    ElMessage.warning("请选择容量并完成必要步骤");
    return;
  }
  draft.setSelection({ device_type: deviceType.value, brand: brand.value, model: model.value });
  router.push("/recycle/checkout");
}

onMounted(async () => {
  if (!deviceReady.value) {
    ElMessage.warning("请选择机型后进入估价");
    return;
  }
  draft.setSelection({ device_type: deviceType.value, brand: brand.value, model: model.value });
  await loadStorages();
  updateCondition();
});
</script>

<style scoped>
.wizard-wrap { background: #f6f7fb; min-height: 100vh; padding: 18px; }
.card { border-radius: 18px; border: 1px solid #e6e8ee; }
.top-bar { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.title { font-size: 20px; font-weight: 900; }
.subtitle { color: #6b7280; margin-top: 4px; }
.device-line { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-top: 6px; color: #111827; }
.device-chip { font-weight: 700; }
.price-preview { background: #111827; color: #fff; padding: 12px 16px; border-radius: 12px; min-width: 200px; }
.price-label { font-size: 12px; opacity: 0.8; }
.price-value { font-size: 22px; font-weight: 900; margin-top: 2px; }
.price-value.large { font-size: 26px; }
.condition-tip { color: #6b7280; margin-top: 4px; }
.wizard-body { margin-top: 4px; }

/* 问题容器 */
.questions-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 收起状态的问题卡片 */
.question-card.collapsed {
  padding: 16px 20px;
}

.collapsed-question {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.collapsed-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapsed-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #111827);
  min-width: 100px;
}

.collapsed-answer {
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
  background: #f3f4f6;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.edit-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.edit-btn .el-icon {
  font-size: 14px;
}

/* 展开状态的问题卡片 */
.question-card.expanded {
  padding: 20px;
}

.step-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 16px; }
.step-title { font-size: 18px; font-weight: 800; color: var(--text-primary, #111827); }
.step-hint { color: #6b7280; margin-top: 6px; font-size: 13px; }
.options-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; margin-top: 12px; }
.option-card { border: 1px solid #e6e8ee; border-radius: 12px; padding: 12px; background: #fff; cursor: pointer; transition: all 0.2s; }
.option-card:hover { border-color: #cfd4df; transform: translateY(-1px); }
.option-card.active { border-color: var(--el-color-primary, #ff6a00); box-shadow: 0 0 0 1px var(--el-color-primary, #ff6a00) inset; background: #fff5e6; }
.option-label { font-weight: 700; }
.option-desc { color: #6b7280; font-size: 12px; margin-top: 4px; }
.nav { display: flex; align-items: center; justify-content: space-between; margin-top: 16px; }
.nav-right { display: flex; gap: 10px; }
.summary-card { margin-top: 12px; }
.summary-title { font-weight: 800; margin-bottom: 8px; }
.summary-list { display: flex; flex-direction: column; gap: 8px; }
.summary-item { display: flex; align-items: center; gap: 8px; padding: 10px; border: 1px dashed #e6e8ee; border-radius: 12px; cursor: pointer; background: #fff; }
.summary-step { width: 28px; height: 28px; border-radius: 50%; background: #f3f4f6; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #111827; }
.summary-label { font-weight: 700; }
.summary-answer { color: #6b7280; font-size: 12px; margin-top: 2px; }
.summary-content { flex: 1; }
.price-card { margin-top: 12px; }
.estimate-status { color: #6b7280; font-size: 12px; margin-top: 6px; }
.empty-tip { margin-top: 12px; padding: 12px; background: #f9fafb; border: 1px dashed #e6e8ee; border-radius: 12px; color: #6b7280; }
.storage-tag { margin-left: 6px; }
.device-line .sep { color: #9ca3af; }
@media (max-width: 1024px) {
  .top-bar { flex-direction: column; }
  .price-preview { width: 100%; }
  .options-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
}
</style>
