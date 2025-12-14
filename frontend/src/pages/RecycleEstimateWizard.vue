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
    </div>

    <!-- 估价信息卡片 - 只在完成所有必填问题后显示 -->
    <el-card shadow="never" class="card price-info-card" v-if="canCheckout && estimatedPriceText !== '--'">
      <div class="price-info-content">
        <div class="price-info-label">预计到手价</div>
        <div class="price-info-value">{{ estimatedPriceText }}</div>
        <div class="price-info-condition" v-if="draft.condition">按成色：{{ conditionText }}</div>
        <div class="price-info-status" v-if="estimateError">{{ estimateError }}</div>
        <div class="price-info-status" v-else-if="estimating">正在根据所选信息估价...</div>
      </div>
    </el-card>

    <el-row :gutter="16" class="wizard-body">
      <el-col :span="24">
        <el-card shadow="never" class="card questions-card">
          <el-collapse v-model="activeCollapseStep" accordion>
            <el-collapse-item
              v-for="(step, idx) in allSteps"
              :key="step.key"
              :name="String(idx + 1)"
            >
              <template #title>
                <div class="step-title">
                  <span class="step-num">
                    {{ idx + 1 }}. {{ step.title }}
                    <el-tag v-if="step.is_required !== false" size="small" type="danger" style="margin-left: 8px">必填</el-tag>
                    <el-tag v-else size="small" type="info" style="margin-left: 8px">选填</el-tag>
                  </span>
                  <span v-if="hasAnswer(step.key)" class="selected-val">
                    已选: {{ getAnswerText(step.key) }} <el-icon><Check /></el-icon>
                  </span>
                  <span v-else-if="step.is_required === false" class="optional-hint">
                    可选
                  </span>
                </div>
              </template>

              <div class="question-content">
                <div class="step-hint" v-if="step.helper">{{ step.helper }}</div>
                <el-tag v-if="step.type === 'multi'" size="small" style="margin-bottom: 12px">可多选</el-tag>

                <el-alert
                  v-if="loadError && step.key === 'storage'"
                  :title="loadError"
                  type="error"
                  :closable="false"
                  show-icon
                  style="margin-bottom: 12px"
                />

                <div class="options-grid">
                  <div
                    v-for="opt in step.options"
                    :key="opt.value"
                    class="option-item"
                    :class="{ active: isSelected(step.key, opt) }"
                    @click="handleSelectOption(step, opt, idx + 1)"
                  >
                    <div class="option-label">{{ opt.label }}</div>
                    <div class="option-desc" v-if="opt.desc">{{ opt.desc }}</div>
                  </div>
                </div>

                <div v-if="step.key === 'storage' && !storageOptions.length && !loadingCatalog" class="empty-tip">
                  该机型暂未提供容量信息，请返回重新选择机型。
                </div>
                <div v-if="loadingCatalog && step.key === 'storage'" class="empty-tip">容量数据加载中...</div>

                <!-- 最后一步显示提交按钮 -->
                <div v-if="idx + 1 === totalSteps" class="submit-area">
                  <el-button
                    type="primary"
                    size="large"
                    :disabled="!canCheckout"
                    @click="goCheckout"
                  >
                    立即查看报价
                  </el-button>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
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
import { Edit, Check } from "@element-plus/icons-vue";
import { getRecycleCatalog, estimateRecyclePrice, getRecycleQuestionTemplate, type RecycleQuestionTemplateResponse } from "@/api/recycle";
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
type StepItem = { key: StepKey; title: string; helper?: string; type?: "multi" | "single"; is_required?: boolean; options: StepOption[] };

const route = useRoute();
const router = useRouter();
const draft = useRecycleDraftStore();

const storages = ref<string[]>([]);
const loadingCatalog = ref(false);
const loadError = ref("");

const estimating = ref(false);
const estimateError = ref("");

const loadingTemplate = ref(false);
const templateFromBackend = ref<RecycleQuestionTemplateResponse | null>(null);

const deviceType = computed(() => (route.query.device_type as string) || draft.selection.device_type || "");
const brand = computed(() => (route.query.brand as string) || draft.selection.brand || "");
const model = computed(() => (route.query.model as string) || draft.selection.model || "");
const deviceReady = computed(() => !!(deviceType.value && brand.value && model.value));

const isApple = computed(() => brand.value?.includes("苹果") || brand.value?.toLowerCase()?.includes("apple"));

const storageOptions = computed<StepOption[]>(() => storages.value.map((s) => ({ value: s, label: s })));

// 从后端模板转换为前端格式
function convertTemplateToSteps(template: RecycleQuestionTemplateResponse | null): StepItem[] {
  if (!template || !template.questions || template.questions.length === 0) {
    return getDefaultSteps();
  }

  return template.questions.map((q) => {
    const step: StepItem = {
      key: q.key as StepKey,
      title: q.title,
      helper: q.helper || undefined,
      type: q.question_type === 'multi' ? 'multi' : 'single',
      is_required: q.is_required !== undefined ? q.is_required : true, // 默认必填
      options: q.options.map((opt) => ({
        value: opt.value,
        label: opt.label,
        desc: opt.desc || undefined,
        impact: (opt.impact as Impact) || undefined,
      })),
    };

    // 如果是存储容量问题，使用动态加载的storages
    if (q.key === 'storage') {
      step.options = storageOptions.value.length ? storageOptions.value : [];
    }

    return step;
  });
}

// 默认步骤（前端固定，作为fallback）
function getDefaultSteps(): StepItem[] {
  return [
  {
    key: "channel",
    title: "购买渠道",
    helper: "官方直营/运营商/第三方等",
    is_required: true,
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
    is_required: true,
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
    is_required: true,
    options: storageOptions.value.length ? storageOptions.value : [],
  },
  {
    key: "usage",
    title: "使用情况",
    is_required: true,
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
    is_required: true,
    options: [
      { value: "full", label: "配件齐全（盒/充/线）", impact: "positive" },
      { value: "partial", label: "有部分配件", impact: "minor" },
      { value: "none", label: "仅裸机", impact: "minor" },
    ],
  },
  {
    key: "screen_appearance",
    title: "屏幕外观",
    is_required: true,
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
    is_required: true,
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
    is_required: true,
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
    is_required: true,
    options: [
      { value: "front-ok", label: "正常", impact: "positive" },
      { value: "front-spot", label: "有斑/坏点", impact: "major" },
      { value: "front-fail", label: "无法拍照/已维修", impact: "critical" },
    ],
  },
  {
    key: "rear_camera",
    title: "后摄拍照",
    is_required: true,
    options: [
      { value: "rear-ok", label: "正常", impact: "positive" },
      { value: "rear-spot", label: "有斑/坏点", impact: "major" },
      { value: "rear-fail", label: "无法拍照/已维修", impact: "critical" },
    ],
  },
  {
    key: "repair",
    title: isApple.value ? "苹果维修情况" : "维修情况（机身）",
    is_required: true,
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
    is_required: true,
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
    is_required: false, // 功能检测是非必选的
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
];
}

const baseSteps = computed<StepItem[]>(() => {
  // 优先使用后端模板，如果没有则使用默认步骤
  const steps = convertTemplateToSteps(templateFromBackend.value);
  console.log('[问卷步骤] 当前使用的步骤数量:', steps.length, '来源:', templateFromBackend.value ? '后端模板' : '前端默认');
  return steps;
});

const totalSteps = computed(() => baseSteps.value.length);
const currentStep = computed(() => Math.min(Math.max(draft.currentStep || 1, 1), totalSteps.value));
const activeStep = computed(() => baseSteps.value[currentStep.value - 1] || baseSteps.value[0]);
const answers = computed(() => draft.answers as Record<StepKey, StepOption | StepOption[]>);

// collapse 当前展开的步骤（字符串格式，因为 el-collapse 的 v-model 需要字符串）
const activeCollapseStep = ref<string>('1');

// 所有步骤（用于渲染）
const allSteps = computed(() => baseSteps.value);

// 检查问题是否有答案
function hasAnswer(stepKey: StepKey): boolean {
  const ans = answers.value[stepKey];
  return ans !== undefined && ans !== null && (Array.isArray(ans) ? ans.length > 0 : true);
}

// 检查当前问题是否有答案
const hasCurrentAnswer = computed(() => {
  return hasAnswer(activeStep.value.key);
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

// 检查所有必填问题是否都已填写
const allRequiredAnswered = computed(() => {
  return baseSteps.value.every((step) => {
    const isRequired = step.is_required !== false; // 默认必填
    if (!isRequired) return true; // 非必填问题跳过检查
    return hasAnswer(step.key);
  });
});

const canCheckout = computed(() => {
  // 必须选择存储容量和成色，且所有必填问题都已填写
  return !!selectedStorage.value && !!draft.condition && allRequiredAnswered.value;
});

function isSelected(stepKey: StepKey, option: StepOption) {
  const ans = answers.value[stepKey];
  if (!ans) return false;
  if (Array.isArray(ans)) {
    return ans.some((x) => x.value === option.value);
  }
  return (ans as StepOption).value === option.value;
}

function goNext() {
  // 检查当前问题是否有答案
  if (!hasCurrentAnswer.value) {
    ElMessage.warning("请先回答当前问题");
    return;
  }
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
  }
  draft.setQuote(null, null);
  updateCondition();
}

// 处理选项选择（带自动跳转）
function handleSelectOption(step: StepItem, option: StepOption, currentIdx: number) {
  selectOption(step, option);
  
  // 单选问题：选择后自动跳转到下一个问题（必填问题必须填写后才能跳转）
  if (step.type !== "multi" && currentIdx < totalSteps.value) {
    const isRequired = step.is_required !== false; // 默认必填
    const hasAnswerForStep = hasAnswer(step.key);
    
    // 如果是必填问题，必须填写后才能跳转
    // 如果是非必填问题，选择后可以跳转，也可以不选择就跳过
    if (hasAnswerForStep || !isRequired) {
      // 延迟跳转，让用户看到选择效果
      setTimeout(() => {
        const nextStep = String(currentIdx + 1);
        activeCollapseStep.value = nextStep;
        draft.setCurrentStep(currentIdx + 1);
      }, 200);
    }
  }
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
  activeCollapseStep.value = String(step);
  draft.setCurrentStep(step);
}

// 监听 activeCollapseStep 变化，同步到 draft.currentStep
watch(activeCollapseStep, (newVal) => {
  const stepNum = parseInt(newVal);
  if (stepNum && stepNum !== currentStep.value) {
    draft.setCurrentStep(stepNum);
  }
});

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

async function loadQuestionTemplate() {
  if (!deviceReady.value) return;
  loadingTemplate.value = true;
  try {
    const { data } = await getRecycleQuestionTemplate({
      device_type: deviceType.value,
      brand: brand.value,
      model: model.value,
    });
    
    console.log('[问卷加载] 从后端获取到模板:', data);
    templateFromBackend.value = data;
    
    // 如果后端模板有storages，更新storages
    if (data.storages && data.storages.length > 0) {
      storages.value = data.storages;
    }
    
    // 检查是否有问题数据
    if (data.questions && data.questions.length > 0) {
      console.log(`[问卷加载] 成功加载 ${data.questions.length} 个问题`);
    } else {
      console.warn('[问卷加载] 后端返回的模板没有问题数据');
    }
  } catch (error) {
    // 如果后端没有模板，使用前端默认步骤（不显示错误）
    templateFromBackend.value = null;
    console.log('[问卷加载] 未找到后端问卷模板，使用默认步骤', error);
  } finally {
    loadingTemplate.value = false;
  }
}

let estimateTimer: number | undefined;

async function runEstimate() {
  if (!shouldEstimate.value) return;
  estimating.value = true;
  estimateError.value = "";
  try {
    console.log("开始估价:", {
      device_type: deviceType.value,
      brand: brand.value,
      model: model.value,
      storage: selectedStorage.value,
      condition: draft.condition
    });
    
    const { data } = await estimateRecyclePrice({
      device_type: deviceType.value,
      brand: brand.value,
      model: model.value,
      storage: selectedStorage.value || "",
      condition: draft.condition || "good",
    });
    
    console.log("估价API返回:", data);
    
    draft.setQuote(
      data?.estimated_price ?? null, 
      data?.bonus ?? null,
      data?.base_price ?? null
    );
    
    // 验证价格是否有效
    if (data?.estimated_price && data.estimated_price > 0) {
      console.log("估价成功:", {
        base_price: draft.base_price,
        estimated_price: draft.estimated_price,
        bonus: draft.bonus
      });
    } else {
      console.warn("估价返回的价格无效:", data?.estimated_price);
      estimateError.value = "估价返回的价格无效";
      ElMessage.warning("估价返回的价格无效，请检查设备信息");
    }
  } catch (error: any) {
    console.error("估价失败:", error);
    estimateError.value = error?.response?.data?.error || error?.response?.data?.detail || error?.message || "估价失败";
    draft.setQuote(null, null, null);
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


async function goCheckout() {
  if (!canCheckout.value) {
    if (!selectedStorage.value) {
      ElMessage.warning("请先选择存储容量");
      return;
    }
    if (!draft.condition) {
      ElMessage.warning("请完成所有必填问题");
      return;
    }
    if (!allRequiredAnswered.value) {
      ElMessage.warning("请完成所有必填问题后再提交");
      return;
    }
    ElMessage.warning("请完成所有必填问题后再提交");
    return;
  }
  
  // 确保估价已完成
  if (!draft.estimated_price) {
    ElMessage.info("正在获取最新估价...");
    try {
      // 直接调用估价API，不依赖 shouldEstimate
      estimating.value = true;
      const { data } = await estimateRecyclePrice({
        device_type: deviceType.value,
        brand: brand.value,
        model: model.value,
        storage: selectedStorage.value || "",
        condition: draft.condition || "good",
      });
      draft.setQuote(
        data?.estimated_price ?? null,
        data?.bonus ?? null,
        data?.base_price ?? null
      );
      estimating.value = false;
      
      // 等待估价完成，检查价格是否有效（大于0）
      if (!draft.estimated_price || draft.estimated_price <= 0) {
        console.error("估价失败：返回的价格无效", draft.estimated_price);
        ElMessage.error("估价失败，返回的价格无效，请稍后重试");
        return;
      }
      
      console.log("估价完成，准备跳转到提交订单页面", {
        base_price: draft.base_price,
        estimated_price: draft.estimated_price,
        bonus: draft.bonus
      });
    } catch (error: any) {
      estimating.value = false;
      ElMessage.error(error?.response?.data?.error || error?.message || "估价失败，请稍后重试");
      return;
    }
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
  
  // 先尝试从后端加载问卷模板
  await loadQuestionTemplate();
  
  // 如果后端没有模板，再加载storages（用于默认步骤）
  if (!templateFromBackend.value) {
    await loadStorages();
  }
  
  // 第一个问题默认展开
  activeCollapseStep.value = '1';
  draft.setCurrentStep(1);
  
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
.price-value.large { font-size: 26px; }
.condition-tip { color: #6b7280; margin-top: 4px; }
.wizard-body { margin-top: 4px; }

/* 问题卡片 */
.questions-card {
  padding: 20px;
}

/* 步骤标题 */
.step-title {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding-right: 20px;
  font-weight: bold;
  font-size: 16px;
}

.step-num {
  font-weight: 700;
}

.selected-val {
  color: #409EFF;
  font-weight: normal;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.selected-val .el-icon {
  font-size: 14px;
}

.optional-hint {
  color: #909399;
  font-size: 12px;
  font-weight: normal;
}

/* 问题内容 */
.question-content {
  padding: 10px 0;
}

.step-hint {
  color: #6b7280;
  margin-bottom: 12px;
  font-size: 13px;
}

/* 网格布局：PC端核心样式 */
.options-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 10px 0;
}

.option-item {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 30px 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
}

.option-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.option-item.active {
  background-color: #ecf5ff;
  border-color: #409EFF;
  color: #409EFF;
  font-weight: bold;
}

.option-label {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 5px;
}

.option-desc {
  font-size: 12px;
  color: #999;
  font-weight: normal;
  margin-top: 5px;
}

.submit-area {
  text-align: center;
  padding: 20px 0;
  margin-top: 20px;
}
/* 估价信息卡片 */
.price-info-card {
  margin-bottom: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.price-info-content {
  padding: 20px;
  color: #fff;
  text-align: center;
}

.price-info-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.price-info-value {
  font-size: 32px;
  font-weight: 900;
  margin-bottom: 8px;
}

.price-info-condition {
  font-size: 13px;
  opacity: 0.85;
  margin-top: 4px;
}

.price-info-status {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 8px;
}
.empty-tip { margin-top: 12px; padding: 12px; background: #f9fafb; border: 1px dashed #e6e8ee; border-radius: 12px; color: #6b7280; }
.storage-tag { margin-left: 6px; }
.device-line .sep { color: #9ca3af; }
@media (max-width: 1024px) {
  .top-bar { flex-direction: column; }
  .options-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .option-item { padding: 20px 10px; }
}
</style>
