// src/stores/recycleDraft.ts
import { defineStore } from "pinia";

export type RecycleSelection = {
  device_type?: string; // 手机/平板/...
  brand?: string;       // 苹果/华为/...
  series?: string;      // 17系列/16系列/全部
  model?: string;       // iPhone 17 Pro Max
  q?: string;           // 搜索关键词（可选）
};

export type ConditionLevel = "new" | "like_new" | "good" | "fair" | "poor";

type AnswerValue = any;

const STORAGE_KEY = "recycleDraft";

const baseState = {
  selection: {
    device_type: "手机",
    series: "全部",
  } as RecycleSelection,
  answers: {} as Record<string, AnswerValue>,
  currentStep: 1,
  storage: undefined as string | undefined,
  condition: undefined as ConditionLevel | undefined,
  base_price: null as number | null,  // 基础价格（从模板获取）
  estimated_price: null as number | null,  // 根据成色调整后的价格
  bonus: null as number | null,  // 额外加价
  // 新增字段：模板化架构支持
  template_id: null as number | null,  // 关联的模板ID
  selected_storage: undefined as string | undefined,  // 用户选择的存储容量
  selected_color: undefined as string | undefined,  // 用户选择的颜色
  selected_ram: undefined as string | undefined,  // 用户选择的运行内存
  selected_version: undefined as string | undefined,  // 用户选择的版本
};

function loadPersistedState() {
  // 不再从 localStorage 加载历史数据，每次都是全新状态
  // 这样用户每次进入问卷都是空白状态，不会保留上次的填写信息
  return { ...baseState };
}

export const useRecycleDraftStore = defineStore("recycleDraft", {
  state: () => loadPersistedState(),
  actions: {
    persist() {
      if (typeof localStorage === "undefined") return;
      const snapshot = {
        selection: this.selection,
        answers: this.answers,
        currentStep: this.currentStep,
        storage: this.storage,
        condition: this.condition,
        base_price: this.base_price,
        estimated_price: this.estimated_price,
        bonus: this.bonus,
        // 新增字段
        template_id: this.template_id,
        selected_storage: this.selected_storage,
        selected_color: this.selected_color,
        selected_ram: this.selected_ram,
        selected_version: this.selected_version,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
    },
    resetEstimate() {
      this.answers = {};
      this.currentStep = 1;
      this.storage = undefined;
      this.condition = undefined;
      this.base_price = null;
      this.estimated_price = null;
      this.bonus = null;
      // 重置新增字段
      this.template_id = null;
      this.selected_storage = undefined;
      this.selected_color = undefined;
      this.selected_ram = undefined;
      this.selected_version = undefined;
    },
    setSelection(patch: Partial<RecycleSelection>) {
      // 上游变更时清空下游，避免脏数据
      if (patch.device_type && patch.device_type !== this.selection.device_type) {
        this.selection = { device_type: patch.device_type, series: "全部" };
        this.resetEstimate();
        this.persist();
        return;
      }
      if (patch.brand && patch.brand !== this.selection.brand) {
        this.selection = { ...this.selection, brand: patch.brand, series: "全部", model: undefined };
        this.resetEstimate();
        this.persist();
        return;
      }
      if (patch.series && patch.series !== this.selection.series) {
        this.selection = { ...this.selection, series: patch.series, model: undefined };
        this.resetEstimate();
        this.persist();
        return;
      }
      if (patch.model && patch.model !== this.selection.model) {
        this.resetEstimate();
      }
      this.selection = { ...this.selection, ...patch };
      this.persist();
    },
    resetSelection() {
      this.selection = { device_type: "手机", series: "全部" };
      this.resetEstimate();
      this.persist();
    },
    setAnswer(stepKey: string, value: AnswerValue) {
      this.answers = { ...this.answers, [stepKey]: value };
      this.persist();
    },
    setCurrentStep(step: number) {
      this.currentStep = step;
      this.persist();
    },
    setStorage(storage?: string) {
      this.storage = storage;
      this.persist();
    },
    setCondition(condition?: ConditionLevel) {
      this.condition = condition;
      this.persist();
    },
    setQuote(estimated_price?: number | null, bonus?: number | null, base_price?: number | null) {
      this.base_price = base_price ?? null;
      this.estimated_price = estimated_price ?? null;
      this.bonus = bonus ?? null;
      this.persist();
    },
    getImpactCounts() {
      const counts = { minor: 0, major: 0, critical: 0 };
      const consume = (item: any) => {
        if (!item || typeof item !== "object") return;
        const impact = String(item.impact || "").trim();
        if (impact in counts) {
          counts[impact as "minor" | "major" | "critical"] += 1;
        }
      };
      Object.values(this.answers || {}).forEach((v) => {
        if (!v) return;
        if (Array.isArray(v)) {
          v.forEach(consume);
        } else {
          consume(v);
        }
      });
      return counts;
    },
    // 新增 actions：设置模板和用户选择的配置
    setTemplate(templateId: number | null) {
      this.template_id = templateId;
      this.persist();
    },
    setSelectedConfig(config: {
      storage?: string;
      color?: string;
      ram?: string;
      version?: string;
    }) {
      if (config.storage !== undefined) this.selected_storage = config.storage;
      if (config.color !== undefined) this.selected_color = config.color;
      if (config.ram !== undefined) this.selected_ram = config.ram;
      if (config.version !== undefined) this.selected_version = config.version;
      this.persist();
    },
    hydrate() {
      Object.assign(this, loadPersistedState());
    },
  },
});
