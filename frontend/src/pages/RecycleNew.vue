<!-- src/pages/RecycleNew.vue  (优化后的回收主页) -->
<template>
  <PageContainer 
    title="设备回收估价" 
    subtitle="专业质检，极速打款，让闲置设备变现更简单"
    background="page"
    padding="normal"
  >
    <div class="recycle-layout">
      <!-- 左侧：引导与入口 -->
      <aside class="sidebar">
        <!-- 主要引导卡片 -->
        <BaseCard class="hero-card" shadow="md" hover>
          <div class="hero-content">
            <div class="hero-badge">
              <span class="badge-icon">💰</span>
              <span class="badge-text">回收估价</span>
            </div>
            <h2 class="hero-title">选择设备，获取专业估价</h2>
            <p class="hero-description">
              三步完成：选择机型 → 填写设备信息 → 获得准确估价
            </p>
            
            <div class="feature-tags">
              <span class="feature-tag">
                <span class="tag-icon">🔍</span>
                专业质检
              </span>
              <span class="feature-tag">
                <span class="tag-icon">⚡</span>
                极速打款
              </span>
              <span class="feature-tag">
                <span class="tag-icon">📱</span>
                线上估价
              </span>
              <span class="feature-tag">
                <span class="tag-icon">✅</span>
                透明复检
              </span>
            </div>
          </div>
        </BaseCard>

        <!-- 热门推荐卡片 -->
        <BaseCard class="hot-card" shadow="sm" hover clickable @click="quickToModel('手机', '苹果', 'iPhone 13')">
          <div class="hot-content">
            <div class="hot-info">
              <div class="hot-label">热门估价</div>
              <div class="hot-model">苹果 iPhone 13</div>
              <div class="hot-tip">点击快速开始估价</div>
            </div>
            <div class="hot-action">
              <div class="action-button">
                <span class="action-text">立即估价</span>
                <span class="action-arrow">→</span>
              </div>
            </div>
          </div>
        </BaseCard>
      </aside>

      <!-- 右侧：机型选择器 -->
      <main class="main-content">
        <BaseCard 
          class="picker-card" 
          shadow="md"
          v-loading="loadingCatalog"
          element-loading-text="正在加载机型数据..."
        >
          <template #header>
            <div class="picker-header-content">
              <div>
                <h3 class="picker-title">选择设备机型</h3>
                <p class="picker-subtitle">从设备类型开始，逐步选择品牌和具体机型</p>
              </div>
            </div>
          </template>

          <div class="picker-content">
            <!-- 错误提示 -->
            <el-alert
              v-if="loadError"
              :title="loadError"
              type="error"
              :closable="false"
              show-icon
              class="error-alert"
            />

            <!-- 搜索框 -->
            <div class="search-section">
              <el-input
                v-model="keyword"
                clearable
                size="large"
                placeholder="搜索品牌或机型，如：iPhone 15 Pro"
                @input="syncQuery"
                @clear="syncQuery"
                class="search-input"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>

            <!-- 设备类型标签页 -->
            <el-tabs v-model="activeDeviceType" class="device-tabs" @tab-change="onDeviceTypeTabChange">
              <el-tab-pane v-for="t in primaryTabs" :key="t" :label="t" :name="t" />
            </el-tabs>

            <!-- 选择器主体 -->
            <div class="picker-body">
              <!-- 品牌选择列 -->
              <div class="brand-column">
                <div class="column-header">
                  <h4 class="column-title">品牌</h4>
                </div>
                <el-scrollbar height="420px" class="brand-scrollbar">
                  <div class="brand-list">
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
                  </div>

                  <div v-if="brands.length === 0" class="empty-state">
                    <div class="empty-icon">📱</div>
                    <div class="empty-text">
                      {{ loadError ? "品牌列表加载失败" : "当前分类暂无品牌数据" }}
                    </div>
                  </div>
                </el-scrollbar>
              </div>

              <!-- 机型选择列 -->
              <div class="model-column">
                <!-- 系列筛选 -->
                <div class="series-filter" v-if="seriesOptions.length">
                  <span class="series-label">系列筛选：</span>
                  <div class="series-chips">
                    <button
                      v-for="s in seriesOptions"
                      :key="s"
                      type="button"
                      class="series-chip"
                      :class="{ active: selection.series === s }"
                      @click="pickSeries(s)"
                    >
                      {{ s }}
                    </button>
                  </div>
                </div>

                <div class="column-header">
                  <h4 class="column-title">机型</h4>
                  <span class="column-hint">点击机型开始估价</span>
                </div>

                <el-scrollbar height="360px" class="model-scrollbar">
                  <div class="model-list">
                    <button
                      v-for="m in models"
                      :key="m"
                      type="button"
                      class="model-item"
                      @click="pickModel(m)"
                    >
                      <span class="model-radio"></span>
                      <span class="model-name">{{ m }}</span>
                      <span class="model-arrow">→</span>
                    </button>
                  </div>

                  <div v-if="models.length === 0" class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <div class="empty-text">
                      {{ loadError ? "机型数据加载失败" : keyword ? "没有找到匹配的机型" : "请先选择品牌" }}
                    </div>
                  </div>
                </el-scrollbar>

                <!-- 底部提示 -->
                <div class="picker-footer">
                  <div class="footer-tip">
                    <span class="tip-icon">💡</span>
                    <span class="tip-text">选择机型后将进入详细估价问卷，大约需要 3-5 分钟完成</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </BaseCard>
      </main>
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
/* ==================== 布局结构 ==================== */
.recycle-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
  align-items: start;
}

/* ==================== 左侧边栏 ==================== */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 24px;
}

/* 主要引导卡片 */
.hero-card {
  background: linear-gradient(135deg, #fff5e6 0%, #fff 100%);
  border: 1px solid #ffe4b3;
}

.hero-content {
  padding: 24px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--el-color-primary), #ffd700);
  border-radius: var(--radius-full, 50px);
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.badge-icon {
  font-size: 16px;
}

.hero-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-primary, #111827);
  margin: 0 0 12px 0;
  line-height: 1.3;
}

.hero-description {
  font-size: 15px;
  color: var(--text-secondary, #6b7280);
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.feature-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #f0f0f0;
  border-radius: var(--radius-md, 12px);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #111827);
  transition: all 0.2s ease;
}

.feature-tag:hover {
  background: #fff;
  border-color: var(--el-color-primary);
  transform: translateY(-1px);
}

.tag-icon {
  font-size: 14px;
}

/* 热门推荐卡片 */
.hot-card {
  border: 1px solid #e6f7ff;
  background: linear-gradient(135deg, #f0f9ff 0%, #fff 100%);
}

.hot-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  gap: 16px;
}

.hot-info {
  flex: 1;
}

.hot-label {
  font-size: 12px;
  color: var(--text-light, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.hot-model {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary, #111827);
  margin-bottom: 4px;
}

.hot-tip {
  font-size: 13px;
  color: var(--text-secondary, #6b7280);
}

.hot-action {
  flex-shrink: 0;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, var(--el-color-primary), #ffd700);
  border-radius: var(--radius-md, 12px);
  font-weight: 600;
  color: #333;
  transition: all 0.3s ease;
}

.action-button:hover {
  transform: translateX(2px);
  box-shadow: 0 4px 12px rgba(255, 106, 0, 0.3);
}

.action-arrow {
  font-size: 16px;
  transition: transform 0.2s ease;
}

.hot-card:hover .action-arrow {
  transform: translateX(2px);
}

/* ==================== 主内容区域 ==================== */
.main-content {
  min-height: 600px;
}

.picker-card {
  min-height: 700px;
}

.picker-header-content h3 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary, #111827);
}

.picker-header-content p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
}

.picker-content {
  padding: 0;
}

/* 错误提示 */
.error-alert {
  margin-bottom: 20px;
  border-radius: var(--radius-md, 12px);
}

/* 搜索区域 */
.search-section {
  margin-bottom: 20px;
}

.search-input {
  border-radius: var(--radius-md, 12px);
}

.search-input :deep(.el-input__wrapper) {
  border-radius: var(--radius-md, 12px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(255, 106, 0, 0.1), 0 4px 12px rgba(0,0,0,0.08);
}

/* 设备类型标签页 */
.device-tabs {
  margin-bottom: 20px;
}

.device-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.device-tabs :deep(.el-tabs__item) {
  font-weight: 600;
  padding: 0 20px;
  height: 44px;
  line-height: 44px;
}

.device-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 2px;
}

/* ==================== 选择器主体 ==================== */
.picker-body {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 20px;
  min-height: 500px;
}

/* 列标题 */
.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.column-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary, #111827);
  margin: 0;
}

.column-hint {
  font-size: 12px;
  color: var(--text-light, #6b7280);
}

/* 品牌列 */
.brand-column {
  background: #fafbfc;
  border-radius: var(--radius-md, 12px);
  padding: 16px;
}

.brand-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.brand-item {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e6e8ee;
  border-radius: var(--radius-md, 12px);
  background: #fff;
  color: var(--text-primary, #111827);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.brand-item:hover {
  border-color: var(--el-color-primary);
  background: #fff5e6;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(255, 106, 0, 0.1);
}

.brand-item.active {
  background: linear-gradient(135deg, var(--el-color-primary), #ffd700);
  border-color: var(--el-color-primary);
  color: #333;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(255, 106, 0, 0.2);
}

/* 机型列 */
.model-column {
  display: flex;
  flex-direction: column;
}

/* 系列筛选 */
.series-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.series-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary, #6b7280);
}

.series-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.series-chip {
  padding: 6px 14px;
  border: 1px solid #e5e7eb;
  border-radius: var(--radius-full, 50px);
  background: #f9fafb;
  color: var(--text-primary, #111827);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.series-chip:hover {
  border-color: var(--el-color-primary);
  background: #fff5e6;
}

.series-chip.active {
  background: var(--el-color-primary);
  border-color: var(--el-color-primary);
  color: #333;
  font-weight: 600;
}

/* 机型列表 */
.model-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.model-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e6e8ee;
  border-radius: var(--radius-md, 12px);
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.model-item:hover {
  border-color: var(--el-color-primary);
  background: #fff5e6;
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(255, 106, 0, 0.1);
}

.model-radio {
  width: 16px;
  height: 16px;
  border: 2px solid #d1d5db;
  border-radius: 50%;
  background: #fff;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.model-item:hover .model-radio {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary);
  box-shadow: inset 0 0 0 3px #fff;
}

.model-name {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #111827);
  text-align: left;
}

.model-arrow {
  font-size: 18px;
  color: #9ca3af;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.model-item:hover .model-arrow {
  color: var(--el-color-primary);
  transform: translateX(2px);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 14px;
  color: var(--text-light, #6b7280);
  line-height: 1.5;
}

/* 底部提示 */
.picker-footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.footer-tip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-md, 12px);
}

.tip-icon {
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 1px;
}

.tip-text {
  font-size: 13px;
  color: var(--text-secondary, #374151);
  line-height: 1.5;
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 1200px) {
  .recycle-layout {
    grid-template-columns: 320px 1fr;
    gap: 20px;
  }
  
  .picker-body {
    grid-template-columns: 180px 1fr;
    gap: 16px;
  }
}

@media (max-width: 992px) {
  .recycle-layout {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .sidebar {
    position: static;
    order: 2;
  }
  
  .main-content {
    order: 1;
  }
  
  .picker-body {
    grid-template-columns: 160px 1fr;
  }
}

@media (max-width: 768px) {
  .hero-content {
    padding: 20px;
  }
  
  .hero-title {
    font-size: 20px;
  }
  
  .hot-content {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    padding: 16px;
  }
  
  .action-button {
    justify-content: center;
  }
  
  .picker-body {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .brand-column {
    order: 2;
  }
  
  .model-column {
    order: 1;
  }
  
  .series-filter {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .series-chips {
    justify-content: flex-start;
  }
}

@media (max-width: 480px) {
  .feature-tags {
    gap: 6px;
  }
  
  .feature-tag {
    padding: 6px 10px;
    font-size: 12px;
  }
  
  .model-item {
    padding: 12px;
  }
  
  .model-name {
    font-size: 14px;
  }
}
</style>