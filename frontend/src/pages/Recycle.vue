<!-- src/pages/Recycle.vue  (改造成：回收主页 / 选机型入口页) -->
import { DEVICE_CATALOG, DEVICE_TYPES } from "@/data/deviceCatalog.js";
<template>
  <div class="recycle-home">
    <div class="container">
      <div class="grid">
        <!-- 左侧：引导与入口 -->
        <section class="left">
          <el-card shadow="never" class="card hero">
            <div class="hero-main">
              <div class="hero-subtitle">回收估价</div>
              <div class="hero-title">选择设备，填写估价信息</div>
              <div class="hero-desc">先选机型 → 进入 13 步“估价信息”问卷 → 再提交回收订单</div>
            </div>

            <div class="hero-pills">
              <el-tag round>专业质检</el-tag>
              <el-tag round>极速打款</el-tag>
              <el-tag round>线上估价</el-tag>
              <el-tag round>透明复检</el-tag>
            </div>
          </el-card>

          <el-card shadow="never" class="card">
            <div class="card-title">选择你要回收的设备</div>
            <div class="card-sub">从大类开始，按品牌与机型进一步选择</div>

            <div class="category-grid">
              <button
                v-for="t in deviceTypes"
                :key="t"
                class="category-item"
                :class="{ active: selection.device_type === t }"
                type="button"
                @click="pickDeviceType(t)"
              >
                <span class="dot" />
                <span class="text">{{ t }}</span>
              </button>
            </div>
          </el-card>

          <el-card shadow="never" class="card hot">
            <div class="hot-left">
              <div class="card-title">热门估价</div>
              <div class="hot-model">苹果 iPhone 13</div>
              <div class="hot-tip">点击后进入问卷（示例）</div>
            </div>

            <el-button type="primary" round @click="quickToModel('手机', '苹果', 'iPhone 13')">
              立即估价
            </el-button>
          </el-card>
        </section>

        <!-- 右侧：机型选择器 -->
        <section class="right">
          <el-card shadow="never" class="card picker">
            <div class="picker-header">
              <div class="picker-title">机型选择</div>

              <el-input
                v-model="keyword"
                clearable
                size="large"
                placeholder="搜索品牌 / 机型（如：iPhone 15 Pro）"
                @input="syncQuery"
                @clear="syncQuery"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>

            <el-tabs v-model="activeDeviceType" class="device-tabs" @tab-change="onDeviceTypeTabChange">
              <el-tab-pane v-for="t in primaryTabs" :key="t" :label="t" :name="t" />
            </el-tabs>

            <div class="picker-body">
              <!-- 品牌列 -->
              <div class="brand-col">
                <div class="col-title">品牌</div>
                <el-scrollbar height="420px">
                  <button
                    v-for="b in brands"
                    :key="b"
                    type="button"
                    class="brand-item"
                    :class="{ active: selection.brand === b }"
                    @click="pickBrand(b)"
                  >
                    {{ b }}
                  </button>

                  <div v-if="brands.length === 0" class="empty">
                    当前大类暂无品牌数据
                  </div>
                </el-scrollbar>
              </div>

              <!-- 机型列 -->
              <div class="model-col">
                <div class="series-row" v-if="seriesOptions.length">
                  <span class="series-label">系列：</span>
                  <div class="series-chips">
                    <button
                      v-for="s in seriesOptions"
                      :key="s"
                      type="button"
                      class="chip"
                      :class="{ active: selection.series === s }"
                      @click="pickSeries(s)"
                    >
                      {{ s }}
                    </button>
                  </div>
                </div>

                <div class="model-hint">点击机型开始估价 →</div>

                <el-scrollbar height="360px">
                  <button
                    v-for="m in models"
                    :key="m"
                    type="button"
                    class="model-item"
                    @click="pickModel(m)"
                  >
                    <span class="radio" />
                    <span class="model-name">{{ m }}</span>
                    <span class="arrow">›</span>
                  </button>

                  <div v-if="models.length === 0" class="empty models-empty">
                    {{ keyword ? "没有匹配的机型" : "请选择品牌后查看机型" }}
                  </div>
                </el-scrollbar>

                <div class="picker-foot">
                  提示：选择机型后将进入 <b>13 步</b>「估价信息」问卷，完成后再进入提交订单页。
                </div>
              </div>
            </div>
          </el-card>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Search } from "@element-plus/icons-vue";
import { DEVICE_CATALOG, DEVICE_TYPES, type DeviceType } from "@/data/deviceCatalog";
import { useRecycleDraftStore } from "@/stores/recycleDraft";

const router = useRouter();
const route = useRoute();
const draft = useRecycleDraftStore();

const deviceTypes = DEVICE_TYPES;
const primaryTabs = computed(() => deviceTypes.slice(0, 5));

const selection = computed(() => draft.selection);

const activeDeviceType = ref<string>(selection.value.device_type || "手机");
const keyword = ref<string>(selection.value.q || "");

const catalog = computed(() => DEVICE_CATALOG[activeDeviceType.value as DeviceType] || { brands: {} });

const brands = computed(() => Object.keys(catalog.value.brands || {}));

const selectedBrand = computed(() => {
  const b = selection.value.brand;
  if (b && brands.value.includes(b)) return b;
  return brands.value[0];
});

const allModelsInType = computed(() => {
  const out: Array<{ brand: string; model: string }> = [];
  Object.entries(catalog.value.brands || {}).forEach(([b, ms]) => {
    ms.forEach((m) => out.push({ brand: b, model: m }));
  });
  return out;
});

function toSeries(modelName: string): string | null {
  const m = modelName.match(/(\d{2})/);
  if (m?.[1]) return `${m[1]}系列`;
  return null;
}

const seriesOptions = computed(() => {
  if (!selectedBrand.value || keyword.value.trim()) return [];
  const models = catalog.value.brands[selectedBrand.value] || [];
  const set = new Set<string>();
  models.forEach((m) => {
    const s = toSeries(m);
    if (s) set.add(s);
  });
  const arr = Array.from(set);
  arr.sort((a, b) => b.localeCompare(a));
  return ["全部", ...arr];
});

const models = computed(() => {
  const q = keyword.value.trim().toLowerCase();

  if (q) {
    return allModelsInType.value
      .filter((x) => `${x.brand} ${x.model}`.toLowerCase().includes(q))
      .slice(0, 80)
      .map((x) => x.model);
  }

  if (!selectedBrand.value) return [];

  const list = catalog.value.brands[selectedBrand.value] || [];
  const s = selection.value.series;

  if (!s || s === "全部") return list;

  const n = s.replace("系列", "");
  return list.filter((m) => m.includes(n));
});

const syncingFromRoute = ref(false);

function syncQuery() {
  const q = {
    device_type: activeDeviceType.value,
    brand: selectedBrand.value,
    series: selection.value.series || "全部",
    q: keyword.value || undefined,
  } as Record<string, any>;

  router.replace({ path: "/recycle", query: q });
}

function applyFromRoute() {
  syncingFromRoute.value = true;
  const q = route.query;

  const device_type = typeof q.device_type === "string" ? q.device_type : "手机";
  const brand = typeof q.brand === "string" ? q.brand : undefined;
  const series = typeof q.series === "string" ? q.series : "全部";
  const kw = typeof q.q === "string" ? q.q : "";

  activeDeviceType.value = device_type;
  keyword.value = kw;
  draft.setSelection({ device_type, brand, series, q: kw });

  syncingFromRoute.value = false;
}

watch(
  () => route.query,
  () => {
    if (syncingFromRoute.value) return;
    applyFromRoute();
  }
);

watch(activeDeviceType, (v) => {
  if (syncingFromRoute.value) return;
  draft.setSelection({ device_type: v });

  if (brands.value.length) draft.setSelection({ brand: brands.value[0] });
  syncQuery();
});

onMounted(() => {
  if (Object.keys(route.query || {}).length) {
    applyFromRoute();
  } else {
    if (brands.value.length) draft.setSelection({ brand: brands.value[0] });
    syncQuery();
  }
});

function pickDeviceType(t: string) {
  activeDeviceType.value = t;
}

function onDeviceTypeTabChange() {
  // no-op
}

function pickBrand(b: string) {
  draft.setSelection({ brand: b });
  syncQuery();
}

function pickSeries(s: string) {
  draft.setSelection({ series: s });
  syncQuery();
}

function pickModel(m: string) {
  let brand = selectedBrand.value;
  const q = keyword.value.trim().toLowerCase();
  if (q) {
    const hit = allModelsInType.value.find((x) => x.model === m);
    if (hit?.brand) brand = hit.brand;
  }

  draft.setSelection({ brand, model: m });

  router.push({
    path: "/recycle/estimate",
    query: { device_type: activeDeviceType.value, brand, model: m },
  });
}

function quickToModel(device_type: string, brand: string, model: string) {
  activeDeviceType.value = device_type;
  draft.setSelection({ device_type, brand, series: "全部", model, q: "" });
  keyword.value = "";
  router.push({ path: "/recycle/estimate", query: { device_type, brand, model } });
}
</script>

<style scoped>
.recycle-home { background: #f6f7fb; min-height: 100vh; }
.container { max-width: 1200px; margin: 0 auto; padding: 18px; }
.grid { display: grid; grid-template-columns: 520px 1fr; gap: 16px; }
.card { border-radius: 18px; border: 1px solid #e6e8ee; }
.left .card + .card { margin-top: 14px; }

.hero-main { padding: 8px 4px 10px; }
.hero-subtitle { color: #6b7280; font-size: 12px; }
.hero-title { font-size: 22px; font-weight: 800; margin-top: 6px; }
.hero-desc { color: #6b7280; margin-top: 8px; font-size: 13px; line-height: 1.4; }
.hero-pills { display: flex; gap: 8px; flex-wrap: wrap; padding-top: 10px; }

.card-title { font-weight: 800; color: #111827; }
.card-sub { color: #6b7280; margin-top: 6px; font-size: 12px; }

.category-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 12px; }
.category-item { display: flex; align-items: center; gap: 10px; padding: 12px; border-radius: 14px; background: #f7f8fb; border: 1px solid #eef0f4; cursor: pointer; }
.category-item.active { background: #fff; border-color: #111827; box-shadow: 0 0 0 1px #111827 inset; }
.dot { width: 10px; height: 10px; border-radius: 999px; background: #d1d5db; }
.text { font-weight: 700; }

.hot { display: flex; justify-content: space-between; align-items: center; }
.hot-model { margin-top: 6px; font-weight: 700; }
.hot-tip { margin-top: 6px; font-size: 12px; color: #6b7280; }

.picker { padding-bottom: 2px; }
.picker-header { display: grid; grid-template-columns: 96px 1fr; gap: 12px; align-items: center; }
.picker-title { font-weight: 900; font-size: 14px; }
.device-tabs { margin-top: 12px; }

.picker-body { display: grid; grid-template-columns: 180px 1fr; gap: 12px; margin-top: 12px; }
.col-title { font-weight: 800; margin-bottom: 10px; color: #111827; }

.brand-item { width: 100%; text-align: center; padding: 10px 12px; border-radius: 12px; border: 1px solid #e6e8ee; background: #fff; cursor: pointer; margin-bottom: 10px; }
.brand-item:hover { background: #f7f8fb; }
.brand-item.active { background: #111827; color: #fff; border-color: #111827; }

.series-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
.series-label { color: #6b7280; font-size: 12px; }
.series-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip { padding: 7px 12px; border-radius: 999px; background: #f3f4f6; border: 1px solid #e5e7eb; cursor: pointer; }
.chip.active { background: #111827; color: #fff; border-color: #111827; }

.model-hint { color: #6b7280; font-size: 12px; margin: 6px 0 8px; }

.model-item { width: 100%; display: flex; align-items: center; gap: 10px; padding: 12px; border-radius: 14px; border: 1px solid #e6e8ee; background: #f9fafb; cursor: pointer; margin-bottom: 10px; }
.model-item:hover { background: #f3f4f6; }
.radio { width: 12px; height: 12px; border-radius: 999px; background: #d1d5db; }
.model-name { flex: 1; font-weight: 700; text-align: left; }
.arrow { color: #9ca3af; font-size: 18px; }

.picker-foot { margin-top: 10px; padding: 12px; border-radius: 14px; background: #f7f8fb; color: #374151; font-size: 12px; border: 1px solid #eef0f4; }
.empty { padding: 12px; color: #6b7280; font-size: 12px; text-align: center; }
.models-empty { margin-top: 12px; }

@media (max-width: 1100px) { .grid { grid-template-columns: 1fr; } }
</style>
