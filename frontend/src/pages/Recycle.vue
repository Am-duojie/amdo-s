<!-- src/pages/Recycle.vue  (改造成：回收主页 / 选机型入口页) -->
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
              <div class="hero-desc">先选机型 → 进入 13 步"估价信息"问卷 → 再提交回收订单</div>
            </div>

            <div class="hero-pills">
              <el-tag round>专业质检</el-tag>
              <el-tag round>极速打款</el-tag>
              <el-tag round>线上估价</el-tag>
              <el-tag round>透明复检</el-tag>
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
          <el-card
            shadow="never"
            class="card picker"
            v-loading="loadingCatalog"
            element-loading-text="正在加载机型..."
          >
            <div class="picker-header">
              <div class="picker-title">机型选择</div>
              <div class="picker-subtitle">从大类开始，按品牌与机型进一步选择</div>
            </div>

            <el-alert
              v-if="loadError"
              :title="loadError"
              type="error"
              :closable="false"
              show-icon
              class="error-alert"
            />

            <div class="search-section">
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
                    {{ loadError ? "品牌列表加载失败" : "当前大类暂无品牌数据" }}
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
                    {{ loadError ? "机型数据加载失败" : keyword ? "没有匹配的机型" : "请选择品牌后查看机型" }}
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
import { ElMessage } from "element-plus";
import { getRecycleCatalog, type RecycleCatalogResponse } from "@/api/recycle";
import { useRecycleDraftStore } from "@/stores/recycleDraft";

type CatalogModel = { name: string; storages?: string[]; series?: string | null };

const router = useRouter();
const route = useRoute();
const draft = useRecycleDraftStore();

const catalog = ref<RecycleCatalogResponse>({ device_types: [], brands: {}, models: {} });
const loadingCatalog = ref(false);
const loadError = ref<string>("");

const selection = computed(() => draft.selection);
const activeDeviceType = ref<string>(selection.value.device_type || "手机");
const keyword = ref<string>(selection.value.q || "");

const deviceTypes = computed(() => (catalog.value.device_types?.length ? catalog.value.device_types : ["手机"]));
const primaryTabs = computed(() => deviceTypes.value.slice(0, 5));

const brands = computed(() => catalog.value.brands?.[activeDeviceType.value] || []);

const selectedBrand = computed(() => {
  const b = selection.value.brand;
  if (b && brands.value.includes(b)) return b;
  return brands.value[0];
});

const allModelsInType = computed(() => {
  const out: Array<{ brand: string; model: string; series?: string | null }> = [];
  const map = catalog.value.models?.[activeDeviceType.value] || {};
  Object.entries(map).forEach(([b, ms]) => {
    ms.forEach((m) => out.push({ brand: b, model: m.name, series: m.series }));
  });
  return out;
});

function toSeries(modelName: string, provided?: string | null): string | null {
  if (provided) return provided;
  const m = modelName.match(/(\d{2})/);
  if (m?.[1]) return `${m[1]}系列`;
  return null;
}

const seriesOptions = computed(() => {
  if (!selectedBrand.value || keyword.value.trim()) return [];
  const models = catalog.value.models?.[activeDeviceType.value]?.[selectedBrand.value] || [];
  const set = new Set<string>();
  models.forEach((m) => {
    const s = toSeries(m.name, m.series);
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

  const list: CatalogModel[] = catalog.value.models?.[activeDeviceType.value]?.[selectedBrand.value] || [];
  const s = selection.value.series;

  if (!s || s === "全部") return list.map((m) => m.name);

  const n = s.replace("系列", "");
  return list.filter((m) => (m.series && m.series.includes(n)) || m.name.includes(n)).map((m) => m.name);
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

  const device_type = typeof q.device_type === "string" ? q.device_type : activeDeviceType.value || "手机";
  const brand = typeof q.brand === "string" ? q.brand : undefined;
  const series = typeof q.series === "string" ? q.series : "全部";
  const kw = typeof q.q === "string" ? q.q : "";

  activeDeviceType.value = device_type;
  keyword.value = kw;
  draft.setSelection({ device_type, brand, series, q: kw });

  syncingFromRoute.value = false;
}

function ensureSelection() {
  if (!deviceTypes.value.includes(activeDeviceType.value) && deviceTypes.value.length) {
    activeDeviceType.value = deviceTypes.value[0];
    draft.setSelection({ device_type: activeDeviceType.value });
  }
  if (brands.value.length && (!selection.value.brand || !brands.value.includes(selection.value.brand))) {
    draft.setSelection({ brand: brands.value[0] });
  }
}

async function fetchCatalog(params?: { device_type?: string; brand?: string; model?: string }) {
  loadingCatalog.value = true;
  loadError.value = "";
  try {
    const { data } = await getRecycleCatalog(params);
    catalog.value = data || { device_types: [], brands: {}, models: {} };
    ensureSelection();
  } catch (error: any) {
    loadError.value = error?.response?.data?.detail || error?.message || "获取机型数据失败";
    catalog.value = { device_types: [], brands: {}, models: {} };
    ElMessage.error(loadError.value);
  } finally {
    loadingCatalog.value = false;
  }
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
  ensureSelection();
  syncQuery();
});

onMounted(async () => {
  if (Object.keys(route.query || {}).length) {
    applyFromRoute();
  }
  await fetchCatalog();
  if (!selection.value.brand && brands.value.length) {
    draft.setSelection({ brand: brands.value[0] });
  }
  syncQuery();
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
.recycle-home { 
  background: var(--bg-page, #f6f7fb); 
  min-height: 100vh; 
  padding-bottom: 24px;
}

.container { 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 24px 20px; 
}

.grid { 
  display: grid; 
  grid-template-columns: 400px 1fr; 
  gap: 20px; 
}

.card { 
  border-radius: var(--radius-lg, 18px); 
  border: 1px solid #e6e8ee; 
  background: var(--bg-white, #fff);
  box-shadow: var(--shadow-sm, 0 2px 8px rgba(0,0,0,0.04));
}

.left .card + .card { 
  margin-top: 16px; 
}

/* Hero 卡片 */
.hero-main { 
  padding: 20px 20px 16px; 
}

.hero-subtitle { 
  color: var(--text-light, #6b7280); 
  font-size: 12px; 
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hero-title { 
  font-size: 24px; 
  font-weight: 800; 
  margin-top: 8px; 
  color: var(--text-primary, #111827);
  line-height: 1.3;
}

.hero-desc { 
  color: var(--text-secondary, #6b7280); 
  margin-top: 12px; 
  font-size: 13px; 
  line-height: 1.6; 
}

.hero-pills { 
  display: flex; 
  gap: 8px; 
  flex-wrap: wrap; 
  padding-top: 16px; 
  margin-top: 16px;
  border-top: 1px solid #f0f0f0;
}

/* 通用卡片标题 */
.card-title { 
  font-weight: 800; 
  color: var(--text-primary, #111827); 
  font-size: 16px;
}

.card-sub { 
  color: var(--text-secondary, #6b7280); 
  margin-top: 6px; 
  font-size: 12px; 
}

/* 热门估价卡片 */
.hot { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 20px;
}

.hot-left {
  flex: 1;
}

.hot-model { 
  margin-top: 8px; 
  font-weight: 700; 
  font-size: 16px;
  color: var(--text-primary, #111827);
}

.hot-tip { 
  margin-top: 6px; 
  font-size: 12px; 
  color: var(--text-light, #6b7280); 
}

/* 机型选择器 */
.picker { 
  padding: 20px; 
}

.picker-header {
  margin-bottom: 16px;
}

.picker-title { 
  font-weight: 800; 
  font-size: 18px; 
  color: var(--text-primary, #111827);
  margin-bottom: 6px;
}

.picker-subtitle {
  color: var(--text-secondary, #6b7280);
  font-size: 13px;
  margin-top: 4px;
}

.error-alert {
  margin-bottom: 16px;
}

.search-section {
  margin-bottom: 16px;
}

.device-tabs { 
  margin-bottom: 16px; 
}

.picker-body { 
  display: grid; 
  grid-template-columns: 180px 1fr; 
  gap: 16px; 
}

.col-title { 
  font-weight: 800; 
  margin-bottom: 12px; 
  color: var(--text-primary, #111827); 
  font-size: 14px;
}

/* 品牌列表 */
.brand-item { 
  width: 100%; 
  text-align: center; 
  padding: 12px 16px; 
  border-radius: var(--radius-md, 12px); 
  border: 1px solid #e6e8ee; 
  background: var(--bg-white, #fff); 
  cursor: pointer; 
  margin-bottom: 8px; 
  transition: all 0.2s ease;
  font-size: 14px;
  color: var(--text-primary, #111827);
}

.brand-item:hover { 
  background: #f7f8fb; 
  border-color: var(--el-color-primary, #ff6a00);
}

.brand-item.active { 
  background: var(--el-color-primary, #ff6a00); 
  color: #fff; 
  border-color: var(--el-color-primary, #ff6a00);
  font-weight: 600;
}

/* 系列筛选 */
.series-row { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  margin-bottom: 12px; 
  flex-wrap: wrap; 
}

.series-label { 
  color: var(--text-secondary, #6b7280); 
  font-size: 13px; 
  font-weight: 500;
}

.series-chips { 
  display: flex; 
  gap: 8px; 
  flex-wrap: wrap; 
}

.chip { 
  padding: 6px 14px; 
  border-radius: var(--radius-full, 999px); 
  background: #f3f4f6; 
  border: 1px solid #e5e7eb; 
  cursor: pointer; 
  transition: all 0.2s ease;
  font-size: 12px;
  color: var(--text-primary, #111827);
}

.chip:hover {
  background: #e5e7eb;
}

.chip.active { 
  background: var(--el-color-primary, #ff6a00); 
  color: #fff; 
  border-color: var(--el-color-primary, #ff6a00);
  font-weight: 500;
}

.model-hint { 
  color: var(--text-light, #6b7280); 
  font-size: 12px; 
  margin: 0 0 12px; 
}

/* 机型列表 */
.model-item { 
  width: 100%; 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  padding: 14px 16px; 
  border-radius: var(--radius-md, 12px); 
  border: 1px solid #e6e8ee; 
  background: var(--bg-white, #fff); 
  cursor: pointer; 
  margin-bottom: 8px; 
  transition: all 0.2s ease;
}

.model-item:hover { 
  background: #f7f8fb; 
  border-color: var(--el-color-primary, #ff6a00);
  transform: translateX(2px);
}

.radio { 
  width: 14px; 
  height: 14px; 
  border-radius: 50%; 
  background: #d1d5db; 
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.model-item:hover .radio {
  background: var(--el-color-primary, #ff6a00);
}

.model-name { 
  flex: 1; 
  font-weight: 600; 
  text-align: left; 
  color: var(--text-primary, #111827);
  font-size: 14px;
}

.arrow { 
  color: #9ca3af; 
  font-size: 18px; 
  flex-shrink: 0;
}

.model-item:hover .arrow {
  color: var(--el-color-primary, #ff6a00);
}

/* 底部提示 */
.picker-foot { 
  margin-top: 16px; 
  padding: 14px 16px; 
  border-radius: var(--radius-md, 12px); 
  background: #f7f8fb; 
  color: var(--text-secondary, #374151); 
  font-size: 12px; 
  border: 1px solid #eef0f4; 
  line-height: 1.6;
}

.empty { 
  padding: 24px 12px; 
  color: var(--text-light, #6b7280); 
  font-size: 13px; 
  text-align: center; 
}

.models-empty { 
  margin-top: 12px; 
}

/* 响应式 */
@media (max-width: 1100px) { 
  .grid { 
    grid-template-columns: 1fr; 
  } 
  
  .left .card + .card {
    margin-top: 16px;
  }
  
  .picker-body {
    grid-template-columns: 160px 1fr;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 16px 12px;
  }
  
  .hero-title {
    font-size: 20px;
  }
  
  .picker-body {
    grid-template-columns: 1fr;
  }
  
  .brand-col {
    display: none;
  }
}
</style>
