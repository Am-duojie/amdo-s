// src/stores/recycleDraft.ts
import { defineStore } from "pinia";

export type RecycleSelection = {
  device_type?: string; // 手机/平板/...
  brand?: string;       // 苹果/华为/...
  series?: string;      // 17系列/16系列/全部
  model?: string;       // iPhone 17 Pro Max
  q?: string;           // 搜索关键词（可选）
};

export const useRecycleDraftStore = defineStore("recycleDraft", {
  state: () => ({
    selection: {
      device_type: "手机",
      series: "全部",
    } as RecycleSelection,
  }),
  actions: {
    setSelection(patch: Partial<RecycleSelection>) {
      // 上游变更时清空下游，避免脏数据
      if (patch.device_type && patch.device_type !== this.selection.device_type) {
        this.selection = { device_type: patch.device_type, series: "全部" };
        return;
      }
      if (patch.brand && patch.brand !== this.selection.brand) {
        this.selection = { ...this.selection, brand: patch.brand, series: "全部", model: undefined };
        return;
      }
      if (patch.series && patch.series !== this.selection.series) {
        this.selection = { ...this.selection, series: patch.series, model: undefined };
        return;
      }
      this.selection = { ...this.selection, ...patch };
    },
    resetSelection() {
      this.selection = { device_type: "手机", series: "全部" };
    },
  },
});
