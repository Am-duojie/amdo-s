<!-- src/pages/Recycle.vue  (改造成：回收主页 / 选机型入口页) -->
<template>
  <PageContainer background="page" padding="normal">
    <div class="recycle-home">
      <div class="grid">
        <!-- 左侧：引导与入口 -->
        <section class="left">
          <BaseCard class="hero-card" padding="normal">
            <template #header>
              <div class="hero-header">
                <div class="hero-title">选择设备，填写估价信息</div>
                <div class="hero-desc">先选机型 → 进入 13 步"估价信息"问卷 → 再提交回收订单</div>
              </div>
            </template>
            
            <div class="hero-pills">
              <button
                v-for="(option, index) in estimateOptions"
                :key="index"
                class="pill-button"
                :class="{ active: selectedEstimateOption === index }"
                @click="selectedEstimateOption = index"
              >
                {{ option }}
              </button>
            </div>
          </BaseCard>

          <BaseCard class="hot-card" padding="normal">
            <div class="hot-content">
              <div class="hot-left">
                <div class="hot-title">热门估价</div>
                <div class="hot-model">苹果 iPhone 13</div>
                <div class="hot-tip">点击后进入问卷（示例）</div>
              </div>
              <el-button 
                type="primary" 
                round 
                size="large"
                class="hot-button"
                @click="quickToModel('手机', '苹果', 'iPhone 13')"
              >
                立即估价
              </el-button>
            </div>
          </BaseCard>
        </section>

        <!-- 右侧：机型选择器 -->
        <section class="right">
          <BaseCard
            class="picker-card"
            padding="normal"
            v-loading="loadingCatalog"
            element-loading-text="正在加载机型..."
          >
            <template #header>
              <div class="picker-header">
                <div class="picker-title">机型选择</div>
                <div class="picker-subtitle">从大类开始，按品牌与机型进一步选择</div>
              </div>
            </template>

            <div class="picker-content">
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

                <!-- 系列和机型列 -->
                <div class="model-col">
                  <div class="series-section" v-if="seriesOptions.length">
                    <div class="col-title">系列</div>
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
            </div>
          </BaseCard>
        </section>
      </div>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { getRecycleCatalog, type RecycleCatalogResponse } from "@/api/recycle";
import { useRecycleDraftStore } from "@/stores/recycleDraft";
import PageContainer from "@/components/PageContainer.vue";
import BaseCard from "@/components/BaseCard.vue";

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
const selectedEstimateOption = ref<number>(0);
const estimateOptions = ["专业估价", "深度时间", "华上估价", "资料便捷"];

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
  width: 100%;
}

.grid { 
  display: grid; 
  grid-template-columns: 400px 1fr; 
  gap: 20px; 
}

.left > * + * { 
  margin-top: 16px; 
}

/* Hero 卡片 */
.hero-card {
  margin-bottom: 0;
}

.hero-header {
  width: 100%;
}

.hero-title { 
  font-size: 20px; 
  font-weight: 700; 
  color: var(--text-primary, #111827);
  line-height: 1.4;
  margin-bottom: 8px;
}

.hero-desc { 
  color: var(--text-secondary, #6b7280); 
  font-size: 13px; 
  line-height: 1.6; 
}

.hero-pills { 
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 16px;
}

.pill-button {
  padding: 12px 16px;
  border-radius: var(--radius-md, 12px);
  border: 1px solid #e5e7eb;
  background: #f3f4f6;
  color: var(--text-primary, #111827);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.pill-button:hover {
  background: #e5e7eb;
  border-color: var(--el-color-primary, #ff6a00);
}

.pill-button.active {
  background: var(--el-color-primary, #ff6a00);
  color: #fff;
  border-color: var(--el-color-primary, #ff6a00);
  font-weight: 600;
}

/* 热门估价卡片 */
.hot-card {
  margin-bottom: 0;
}

.hot-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.hot-left {
  flex: 1;
}

.hot-title {
  font-weight: 700;
  color: var(--text-primary, #111827);
  font-size: 16px;
  margin-bottom: 8px;
}

.hot-model { 
  font-weight: 600; 
  font-size: 16px;
  color: var(--text-primary, #111827);
  margin-bottom: 6px;
}

.hot-tip { 
  font-size: 12px; 
  color: var(--text-light, #6b7280); 
}

.hot-button {
  flex-shrink: 0;
  padding: 12px 24px;
  font-weight: 600;
}

/* 机型选择器 */
.picker-card {
  margin-bottom: 0;
}

.picker-header {
  width: 100%;
}

.picker-title { 
  font-weight: 700; 
  font-size: 18px; 
  color: var(--text-primary, #111827);
  margin-bottom: 6px;
}

.picker-subtitle {
  color: var(--text-secondary, #6b7280);
  font-size: 13px;
  line-height: 1.5;
}

.picker-content {
  width: 100%;
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
.series-section {
  margin-bottom: 16px;
}

.series-chips { 
  display: flex; 
  gap: 8px; 
  flex-wrap: wrap; 
  margin-top: 10px;
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
  
  .picker-body {
    grid-template-columns: 160px 1fr;
    gap: 12px;
  }
  
  .hero-pills {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 18px;
  }
  
  .picker-body {
    grid-template-columns: 1fr;
  }
  
  .brand-col {
    display: none;
  }
  
  .hero-pills {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .hot-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .hot-button {
    width: 100%;
  }
}
</style>
