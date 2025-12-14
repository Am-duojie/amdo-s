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
};

function loadPersistedState() {
  if (typeof localStorage === "undefined") return { ...baseState };
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return { ...baseState };
  try {
    const parsed = JSON.parse(raw);
    return { ...baseState, ...parsed, selection: { ...baseState.selection, ...(parsed.selection || {}) } };
  } catch (e) {
    console.warn("恢复回收草稿失败，使用默认值", e);
    return { ...baseState };
  }
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
    hydrate() {
      Object.assign(this, loadPersistedState());
    },
  },
});
