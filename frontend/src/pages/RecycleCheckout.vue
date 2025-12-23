<template>
  <div class="checkout-wrap">
    <el-card shadow="never" class="checkout-card">
      <div class="page-title">估价详情</div>
      <div class="page-desc">核对估价结果和收款信息，确认后提交订单</div>

      <el-alert
        v-if="!ready"
        type="warning"
        :closable="false"
        title="请先完成机型选择与问卷"
        description="返回估价问卷确认机型、容量与问答"
        style="margin: 16px 0"
      />

      <div v-if="ready" class="checkout-content">
        <!-- 订单信息 -->
        <div class="order-info-section">
          <div class="product-header">
            <div class="product-name">{{ deviceLine }}</div>
          </div>
          
          <div class="price-section">
            <div class="price-label">预计到手价</div>
            <div class="price-value">{{ estimatedPriceText }}</div>
            
            <!-- 报价明细 -->
            <div class="price-breakdown" v-if="draft.base_price || draft.bonus">
              <div class="breakdown-item" v-if="draft.base_price">
                <span class="breakdown-label">基础价格：</span>
                <span class="breakdown-value">¥{{ Number(draft.base_price).toFixed(2) }}</span>
              </div>
              <div class="breakdown-item" v-if="draft.base_price && draft.estimated_price && draft.base_price !== draft.estimated_price">
                <span class="breakdown-label">成色调整：</span>
                <span class="breakdown-value adjustment">
                  {{ conditionAdjustmentText }}
                </span>
              </div>
              <div class="breakdown-item" v-if="draft.bonus">
                <span class="breakdown-label">额外加价：</span>
                <span class="breakdown-value bonus">+¥{{ Number(draft.bonus).toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 邮寄方式 -->
        <div class="shipping-section">
          <div class="section-title">邮寄方式</div>
          
          <div class="self-post-info">
            <div class="recipient-info">
              <div class="recipient-item">
                <span class="recipient-label">收件人</span>
                <span class="recipient-value">{{ platformRecipient.name }} {{ platformRecipient.phone }}</span>
                <el-button 
                  size="small" 
                  text 
                  type="primary" 
                  @click="copyToClipboard(platformRecipient.name + ' ' + platformRecipient.phone)"
                >
                  复制
                </el-button>
              </div>
              <div class="recipient-item">
                <span class="recipient-label">收件地址</span>
                <span class="recipient-value">{{ platformRecipient.address }}</span>
                <el-button 
                  size="small" 
                  text 
                  type="primary" 
                  @click="copyToClipboard(platformRecipient.address)"
                >
                  复制
                </el-button>
              </div>
            </div>

          </div>
        </div>

        <!-- 收款信息 -->
        <div class="payment-section">
          <div class="section-header">
            <div class="section-title">收款信息</div>
            <el-link type="primary" :underline="false" @click="editPayment" style="display: flex; align-items: center; gap: 4px;">
              <el-icon><Edit /></el-icon>
              <span>{{ isAlipayBound ? '修改收款信息' : '去绑定收款信息' }}</span>
            </el-link>
          </div>

          <el-alert
            v-if="!isAlipayBound"
            type="warning"
            :closable="false"
            title="请先绑定支付宝收款账号"
            description="回收打款会使用钱包中绑定的支付宝账号"
            style="margin: 12px 0"
          />
          
          <div class="payment-info">
            <div class="payment-method-label">收款方式</div>
            <div class="payment-account">
              <div class="payment-icon">💳</div>
                <div class="payment-details">
                  <div class="account-name">支付宝姓名：{{ alipayRealName || '未填写' }}</div>
                  <div class="account-number">支付宝账号：{{ alipayLoginId || '未绑定' }}</div>
                </div>
              </div>
            </div>
          </div>

        <!-- 平台回收承担快递费用概览 -->
        <div class="fee-overview-section">
          <div class="section-title">平台回收承担快递费用概览</div>
          <el-table :data="feeOverviewData" border style="width: 100%">
            <el-table-column prop="category" label="回收品类" width="150" />
            <el-table-column prop="doorPickup" label="快递上门取件" />
            <el-table-column prop="selfPost" label="自己寄快递" />
          </el-table>
        </div>
      </div>

      <div class="actions">
        <el-button round @click="router.push('/recycle/estimate')">返回问卷</el-button>
        <el-button 
          type="primary" 
          round 
          :disabled="!canSubmit"
          @click="handleSubmit"
        >
          提交订单
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Edit } from "@element-plus/icons-vue";
import api from "@/utils/api";
import { useAuthStore } from "@/stores/auth";
import { useRecycleDraftStore, type ConditionLevel } from "@/stores/recycleDraft";
import { estimateRecyclePrice, createRecycleOrder } from "@/api/recycle";

const router = useRouter();
const authStore = useAuthStore();
const draft = useRecycleDraftStore();

// 订单信息
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

const conditionAdjustmentText = computed(() => {
  if (!draft.base_price || !draft.estimated_price || draft.base_price === draft.estimated_price) {
    return "";
  }
  const adjustment = draft.estimated_price - draft.base_price;
  const percentage = ((draft.estimated_price / draft.base_price) * 100).toFixed(0);
  if (adjustment > 0) {
    return `+¥${adjustment.toFixed(2)} (${percentage}%)`;
  } else {
    return `¥${adjustment.toFixed(2)} (${percentage}%)`;
  }
});

const estimatedPriceText = computed(() => {
  // 检查价格是否存在且大于0
  if (draft.estimated_price != null && draft.estimated_price > 0) {
    return `¥${Number(draft.estimated_price).toFixed(2)}`;
  }
  // 如果价格为0或null，显示"--"
  return "--";
});

const ready = computed(() => !!(draft.selection.device_type && draft.selection.brand && draft.selection.model && draft.storage));

// 邮寄方式（仅支持自行邮寄）
const shippingMethod = ref("self_post");

// 收款信息：使用钱包中绑定的支付宝信息
const walletAlipay = ref<{ login_id: string; real_name: string }>({ login_id: "", real_name: "" });

const alipayLoginId = computed(() => walletAlipay.value.login_id || authStore.user?.alipay_login_id || "");
const alipayRealName = computed(() => walletAlipay.value.real_name || authStore.user?.alipay_real_name || "");
const isAlipayBound = computed(() => Boolean(alipayLoginId.value));

const paymentAccount = computed(() => ({
  name: alipayRealName.value || "支付宝",
  number: alipayLoginId.value,
}));

const loadWalletAlipay = async () => {
  try {
    const res = await api.get("/users/me/");
    walletAlipay.value.login_id = res.data?.alipay_login_id || "";
    walletAlipay.value.real_name = res.data?.alipay_real_name || "";
  } catch {
    walletAlipay.value.login_id = authStore.user?.alipay_login_id || "";
    walletAlipay.value.real_name = authStore.user?.alipay_real_name || "";
  }
};

// 平台收件信息（自行邮寄时显示）
const platformRecipient = ref({
  name: "TESTV回收",
  phone: "15608348253",
  address: "重庆市九龙坡区经纬大道1099号附78号",
});

// 费用概览数据
const feeOverviewData = [
  {
    category: "笔记本/无人机",
    doorPickup: "承担上限 40元",
    selfPost: "承担上限12元",
  },
  {
    category: "其他品类",
    doorPickup: "承担上限 25元",
    selfPost: "承担上限12元",
  },
];


// 编辑收款信息
function editPayment() {
  router.push("/profile?tab=wallet-bind");
}

// 复制到剪贴板
async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success("已复制到剪贴板");
  } catch (error) {
    // 降级方案
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand("copy");
      ElMessage.success("已复制到剪贴板");
    } catch (e) {
      ElMessage.error("复制失败");
    }
    document.body.removeChild(textarea);
  }
}

// 页面加载时，如果没有价格数据，重新触发估价
onMounted(async () => {
  if (!authStore.user) {
    await authStore.init();
  }
  await loadWalletAlipay();

  // 检查是否有必要信息进行估价
  const hasBasicInfo = draft.selection.device_type && draft.selection.brand && draft.selection.model && draft.storage;
  
  // 如果没有价格数据（null、undefined 或 0），且有基本信息，则触发估价
  const needsEstimate = (draft.estimated_price == null || draft.estimated_price === 0) && hasBasicInfo;
  
  if (needsEstimate) {
    try {
      console.log("提交订单页面：检测到缺少价格数据，开始重新估价", {
        device_type: draft.selection.device_type,
        brand: draft.selection.brand,
        model: draft.selection.model,
        storage: draft.storage,
        condition: draft.condition,
        current_price: draft.estimated_price
      });
      
      ElMessage.info("正在获取最新估价...");
      const { data } = await estimateRecyclePrice({
        device_type: draft.selection.device_type,
        brand: draft.selection.brand,
        model: draft.selection.model,
        storage: draft.storage || "",
        condition: draft.condition || "good",
      });
      
      console.log("估价API返回数据:", data);
      
      draft.setQuote(
        data?.estimated_price ?? null,
        data?.bonus ?? null,
        data?.base_price ?? null
      );
      
      if (data?.estimated_price && data.estimated_price > 0) {
        ElMessage.success("估价完成");
        console.log("价格已更新:", {
          base_price: draft.base_price,
          estimated_price: draft.estimated_price,
          bonus: draft.bonus
        });
      } else {
        console.warn("估价返回的价格无效:", data?.estimated_price);
        ElMessage.warning("估价返回的价格无效，请重新填写问卷");
      }
    } catch (error: any) {
      console.error("重新估价失败:", error);
      const errorMsg = error?.response?.data?.error || error?.response?.data?.detail || error?.message || "获取估价失败";
      ElMessage.error(errorMsg);
    }
  } else {
    // 调试信息
    console.log("提交订单页面：价格检查", {
      hasBasicInfo,
      estimated_price: draft.estimated_price,
      needsEstimate,
      ready: ready.value
    });
  }
});

// 是否可以提交
const canSubmit = computed(() => {
  return ready.value && isAlipayBound.value;
});

// 提交订单
async function handleSubmit() {
  if (!canSubmit.value) {
    if (!ready.value) {
      ElMessage.warning("请完善机型与问卷信息");
      return;
    }
    ElMessage.warning("请先在钱包绑定支付宝收款账号");
    router.push("/profile?tab=wallet-bind");
    return;
  }

  // 验证必要信息
  if (!draft.selection.device_type || !draft.selection.brand || !draft.selection.model) {
    ElMessage.warning("请先完成机型选择");
    return;
  }

  if (!draft.storage) {
    ElMessage.warning("请选择存储容量");
    return;
  }

  if (!draft.estimated_price || draft.estimated_price <= 0) {
    ElMessage.warning("价格信息不完整，请重新填写问卷");
    return;
  }

  if (!isAlipayBound.value) {
    ElMessage.warning("请先在钱包绑定支付宝收款账号");
    router.push("/profile?tab=wallet-bind");
    return;
  }

  try {
    await ElMessageBox.confirm(
      "确认提交订单吗？提交后需要填写物流信息并寄出设备。",
      "确认提交",
      {
        confirmButtonText: "确认提交",
        cancelButtonText: "再想想",
        type: "info",
      }
    );

    // 准备订单数据
    const orderData = {
      // 模板信息（如果有）
      template: draft.template_id || null,
      // 设备基本信息（作为快照保留）
      device_type: draft.selection.device_type,
      brand: draft.selection.brand,
      model: draft.selection.model,
      storage: draft.storage || "",
      // 用户选择的配置
      selected_storage: draft.storage || "",
      selected_color: draft.selected_color || "",
      selected_ram: draft.selected_ram || "",
      selected_version: draft.selected_version || "",
      // 问卷答案
      questionnaire_answers: draft.answers || {},
      // 成色和价格
      condition: draft.condition || "good",
      estimated_price: draft.estimated_price,
      bonus: draft.bonus || 0,
      address: platformRecipient.value.address || "",
      // 打款信息：使用钱包绑定的支付宝
      payment_method: "alipay",
      payment_account: alipayLoginId.value,
      note: `基础价格: ¥${draft.base_price || 0}, 成色: ${conditionText.value}`,
    };

    console.log("提交订单数据:", orderData);

    // 调用创建订单API
    const response = await createRecycleOrder(orderData);
    
    console.log("订单创建成功:", response.data);

    ElMessage.success("订单提交成功！请填写物流信息");
    
    // 清空草稿数据（可选，根据业务需求决定）
    // draft.resetEstimate();
    
    // 跳转到回收订单详情页（用户端）
    const orderId = response.data.id;
    router.push(`/recycle-order/${orderId}`);
  } catch (error: any) {
    console.error("提交订单失败:", error);
    if (error !== "cancel") {
      const errorMsg = error?.response?.data?.detail || 
                      error?.response?.data?.error || 
                      error?.response?.data?.message ||
                      error?.message || 
                      "订单提交失败，请稍后重试";
      ElMessage.error(errorMsg);
    }
  }
}
</script>

<style scoped>
.checkout-wrap {
  background: #f6f7fb;
  min-height: 100vh;
  padding: 20px;
}

.checkout-card {
  border-radius: 12px;
  border: 1px solid #e6e8ee;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
}

.page-desc {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 24px;
}

.checkout-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 订单信息区域 */
.order-info-section {
  background: #fef9e7;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #fde68a;
  margin-bottom: 0;
}

.product-header {
  margin-bottom: 20px;
}

.product-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.price-section {
  margin-bottom: 20px;
}

.price-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.price-value {
  font-size: 36px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.price-feedback {
  margin-bottom: 8px;
}

.price-trend {
  font-size: 13px;
  color: #6b7280;
}

.price-breakdown {
  margin-top: 16px;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e6e8ee;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 13px;
}

.breakdown-label {
  color: #6b7280;
}

.breakdown-value {
  font-weight: 600;
  color: #1f2937;
}

.breakdown-value.adjustment {
  color: #409eff;
}

.breakdown-value.bonus {
  color: #67c23a;
}


/* 邮寄方式区域 */
.shipping-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e6e8ee;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #1f2937;
}

.self-post-info {
  padding: 16px 0;
}

.recipient-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recipient-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e6e8ee;
}

.recipient-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  min-width: 80px;
}

.recipient-value {
  flex: 1;
  font-size: 14px;
  color: #1f2937;
}

/* 收款信息区域 */
.payment-section {
  background: #fef9e7;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #fde68a;
  margin-bottom: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.payment-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-method-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.payment-account {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e6e8ee;
}

.payment-icon {
  font-size: 32px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 8px;
}

.payment-details {
  flex: 1;
}

.account-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.account-number {
  font-size: 14px;
  color: #6b7280;
}

/* 费用概览区域 */
.fee-overview-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e6e8ee;
  margin-bottom: 0;
}

.fee-overview-section :deep(.el-table) {
  font-size: 14px;
}

.fee-overview-section :deep(.el-table th) {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.fee-overview-section :deep(.el-table td) {
  color: #6b7280;
}

/* 操作按钮 */
.actions {
  margin-top: 32px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e6e8ee;
}

/* 响应式 */
@media (max-width: 768px) {
  .checkout-wrap {
    padding: 12px;
  }

  .order-info-section,
  .shipping-section,
  .payment-section,
  .fee-overview-section {
    padding: 16px;
  }

  .price-value {
    font-size: 28px;
  }

  .pickup-info {
    gap: 12px;
  }
}
</style>
