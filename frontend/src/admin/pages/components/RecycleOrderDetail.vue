<template>
  <div class="recycle-order-detail" v-loading="loading">
    <!-- 流程状态可视化 -->
    <el-card class="detail-section" shadow="never">
      <template #header>
        <span>订单流程</span>
      </template>
      <div class="process-timeline">
        <div 
          v-for="(step, index) in processSteps" 
          :key="step.value"
          class="timeline-step"
          :class="{ 
            'completed': isStepCompleted(step.value),
            'active': isStepActive(step.value),
            'pending': !isStepCompleted(step.value) && !isStepActive(step.value)
          }"
        >
          <div class="timeline-marker">
            <el-icon v-if="isStepCompleted(step.value)"><Check /></el-icon>
            <el-icon v-else-if="isStepActive(step.value)"><Loading /></el-icon>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="timeline-content">
            <div class="step-title">{{ getProcessStepLabel(step.value) }}</div>
            <div class="step-time">{{ getStepTime(step.value) }}</div>
          </div>
          <div v-if="index < processSteps.length - 1" class="timeline-line"></div>
        </div>
      </div>
    </el-card>

    <!-- 订单基本信息 -->
    <el-card class="detail-section" shadow="never">
      <template #header>
        <div class="card-header">
        <span>订单信息</span>
        <div class="card-actions">
          <el-button
            v-if="detail.status === 'completed' && hasPerm('verified:write')"
            size="small"
            type="primary"
            plain
            :loading="creatingDevice"
            @click="createVerifiedDevice"
            >
              生成官方验库存
            </el-button>
             <el-tag :type="displayStatusTag.type" size="large">{{ displayStatusTag.text }}</el-tag>
            <el-tag v-if="detail.payment_status === 'failed'" type="danger" size="large" style="margin-left: 8px">打款失败</el-tag>
          </div>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">#{{ detail.id }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ detail.user?.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ detail.device_type }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ detail.brand }}</el-descriptions-item>
        <el-descriptions-item label="型号">{{ detail.model }}</el-descriptions-item>
        <el-descriptions-item label="存储容量">{{ detail.storage || '-' }}</el-descriptions-item>
        <el-descriptions-item label="成色">
          <el-tag :type="getConditionType(detail.condition)">{{ getConditionText(detail.condition) }}</el-tag>
        </el-descriptions-item>
        <!-- 模板信息 -->
        <el-descriptions-item v-if="detail.template_info" label="关联模板" :span="2">
          <el-tag type="info">
            {{ detail.template_info.device_type }} / {{ detail.template_info.brand }} / {{ detail.template_info.model }}
            <span v-if="detail.template_info.series"> ({{ detail.template_info.series }})</span>
          </el-tag>
        </el-descriptions-item>
        <!-- 用户选择的配置 -->
        <el-descriptions-item v-if="detail.selected_storage" label="选择的存储">{{ detail.selected_storage }}</el-descriptions-item>
        <el-descriptions-item v-if="detail.selected_color" label="选择的颜色">{{ detail.selected_color }}</el-descriptions-item>
        <el-descriptions-item v-if="detail.selected_ram" label="选择的内存">{{ detail.selected_ram }}</el-descriptions-item>
        <el-descriptions-item v-if="detail.selected_version" label="选择的版本">{{ detail.selected_version }}</el-descriptions-item>
        <el-descriptions-item label="预估价格">
          <span v-if="detail.estimated_price" style="font-size: 16px; color: #909399">
            ¥{{ detail.estimated_price }}
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="最终价格">
          <span v-if="detail.final_price" style="font-size: 18px; color: #f56c6c; font-weight: bold">
            ¥{{ detail.final_price }}
            <span v-if="detail.bonus > 0" style="color: #67c23a; font-size: 14px">(+¥{{ detail.bonus }})</span>
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="总金额">
          <span v-if="detail.total_price" style="font-size: 20px; color: #f56c6c; font-weight: bold">
            ¥{{ detail.total_price }}
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item v-if="detail.ml" label="智能建议价">
          <span style="font-size: 18px; font-weight: bold">¥{{ detail.ml.suggested_final_price }}</span>
          <el-tag size="small" type="info" style="margin-left: 8px">{{ detail.ml.model_version }}</el-tag>
          <div style="margin-top: 6px; color: #909399; font-size: 12px" v-if="detail.ml.suggested_range?.length === 2">
            区间：¥{{ detail.ml.suggested_range[0] }} ~ ¥{{ detail.ml.suggested_range[1] }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item v-if="detail.ml" label="风险提示">
          <div style="display: flex; gap: 8px; flex-wrap: wrap">
            <el-tag :type="getRiskTagType(detail.ml.risk_dispute)">异议 {{ formatRisk(detail.ml.risk_dispute) }}</el-tag>
            <el-tag :type="getRiskTagType(detail.ml.risk_cancel)">取消 {{ formatRisk(detail.ml.risk_cancel) }}</el-tag>
          </div>
          <div style="margin-top: 6px; color: #909399; font-size: 12px" v-if="detail.ml.top_factors?.length">
            {{ detail.ml.top_factors.map((f) => `${f.label}：${f.value}`).join('；') }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="联系人">{{ detail.contact_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detail.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ detail.address }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detail.note || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(detail.updated_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 物流信息 -->
    <el-card v-if="detail.status !== 'pending'" class="detail-section" shadow="never">
      <template #header>
        <span>物流信息</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="物流公司">{{ detail.shipping_carrier || '-' }}</el-descriptions-item>
        <el-descriptions-item label="运单号">{{ detail.tracking_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="寄出时间">{{ formatTime(detail.shipped_at) }}</el-descriptions-item>
        <el-descriptions-item label="收到时间">
          <span v-if="detail.received_at">{{ formatTime(detail.received_at) }}</span>
          <el-button 
            v-else-if="detail.status === 'shipped' && hasPerm('inspection:write')"
            size="small"
            type="primary"
            @click="markReceived"
            :loading="markingReceived"
          >
            确认收到设备
          </el-button>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 问卷答案 -->
    <el-card v-if="detail.questionnaire_answers && Object.keys(detail.questionnaire_answers).length > 0" class="detail-section" shadow="never">
      <template #header>
        <span>问卷答案</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item
          v-for="(value, key) in detail.questionnaire_answers"
          :key="key"
          :label="formatQuestionKey(key)"
        >
          {{ value }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 质检报告 / 检测详情（完成后在订单详情中展示） -->
    <el-card v-if="!isShippedStage" class="detail-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>质检报告</span>
          <el-button
            v-if="canCreateReport && hasPerm('inspection:write')"
            size="small"
            type="primary"
            @click="showReportDialog = true"
          >
            {{ detail.report ? '更新报告' : '创建报告' }}
          </el-button>
        </div>
      </template>
      <div v-if="inspectionReportData">
        <InspectionReport
          :product-id="detail.id"
          :report-data-prop="inspectionReportData"
        />
      </div>
      <div v-else style="color: #909399; text-align: center; padding: 20px">
        <el-empty description="暂无质检报告" />
      </div>
    </el-card>

    <!-- 价格管理 -->
    <el-card v-if="canManagePrice && !isShippedStage" class="detail-section" shadow="never">
      <template #header>
        <span>价格管理</span>
      </template>
      <el-form :model="priceForm" label-width="120px" style="max-width: 600px">
        <el-form-item label="预估价格">
          <el-input-number
            v-model="priceForm.estimated_price"
            :precision="2"
            :min="0"
            style="width: 100%"
            :disabled="detail.status !== 'pending'"
          />
        </el-form-item>
        <el-form-item label="最终价格" required>
          <el-input-number
            v-model="priceForm.final_price"
            :precision="2"
            :min="0"
            style="width: 100%"
            :disabled="detail.status === 'completed' || detail.payment_status === 'paid'"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px">
            根据质检结果调整最终回收价格
          </div>
        </el-form-item>
        <el-form-item label="加价">
          <el-input-number
            v-model="priceForm.bonus"
            :precision="2"
            :min="0"
            style="width: 100%"
            :disabled="detail.status === 'completed' || detail.payment_status === 'paid'"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px">
            额外加价金额（可选）
          </div>
        </el-form-item>
        <el-form-item>
          <el-button 
            v-if="detail.status === 'pending' && hasPerm('inspection:price')"
            type="primary" 
            :loading="savingPrice" 
            @click="saveEstimatedPrice"
          >
            设置预估价格并标记为已估价
          </el-button>
          <el-button 
            v-if="detail.status === 'inspected' && hasPerm('inspection:price')"
            type="primary" 
            :loading="savingPrice" 
            @click="saveFinalPrice"
          >
            更新最终价格
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 打款信息 -->
    <el-card v-if="detail.status === 'completed' || detail.payment_status === 'paid'" class="detail-section" shadow="never">
      <template #header>
        <span>打款信息</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="打款状态">
          <el-tag :type="detail.payment_status === 'paid' ? 'success' : 'warning'">
            {{ detail.payment_status === 'paid' ? '已打款' : '待打款' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="打款方式">{{ detail.payment_method || '-' }}</el-descriptions-item>
        <el-descriptions-item label="打款账户">{{ detail.payment_account || '-' }}</el-descriptions-item>
        <el-descriptions-item label="打款时间">{{ formatTime(detail.paid_at) }}</el-descriptions-item>
        <el-descriptions-item label="打款备注" :span="2">{{ detail.payment_note || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 价格异议 -->
    <el-card v-if="detail.price_dispute" class="detail-section" shadow="never">
      <template #header>
        <span>价格异议</span>
      </template>
      <el-alert type="warning" :closable="false">
        <div>
          <div style="font-weight: bold; margin-bottom: 8px">异议原因：</div>
          <div>{{ detail.price_dispute_reason || '-' }}</div>
        </div>
      </el-alert>
    </el-card>

    <!-- 操作流程 -->
    <el-card class="detail-section" shadow="never">
      <template #header>
        <span>流程操作</span>
      </template>
      <div class="action-buttons">
        <!-- 估价操作 -->
        <el-button
          v-if="detail.status === 'pending' && hasPerm('inspection:write')"
          type="primary"
          @click="showPriceDialog('estimated')"
        >
          给出预估价格
        </el-button>
        
        <!-- 确认收货操作 -->
        <el-button
          v-if="detail.status === 'shipped' && !detail.received_at && hasPerm('inspection:write')"
          type="success"
          @click="markReceived"
          :loading="markingReceived"
        >
          确认收到设备
        </el-button>
        
        <!-- 开始质检 -->
        <el-button
          v-if="detail.status === 'received' && hasPerm('inspection:write')"
          type="primary"
          @click="showReportDialog = true"
        >
          开始质检
        </el-button>
        
        <!-- 等待用户确认价格提示 -->
        <el-alert
          v-if="detail.status === 'inspected' && detail.final_price && !detail.final_price_confirmed"
          type="warning"
          :closable="false"
          style="margin-bottom: 16px"
        >
          <template #title>
            <div style="display: flex; align-items: center; gap: 8px;">
              <el-icon><Clock /></el-icon>
              <span>等待用户确认最终价格 ¥{{ detail.final_price }}{{ detail.bonus > 0 ? ` (+¥${detail.bonus})` : '' }}</span>
            </div>
          </template>
          用户确认价格后，订单将自动进入打款阶段
        </el-alert>
        
        <!-- 完成订单（已废弃，由用户确认价格后自动完成） -->
        <el-button
          v-if="detail.status === 'inspected' && detail.final_price && detail.final_price_confirmed && hasPerm('inspection:write')"
          type="success"
          @click="completeOrder"
          :loading="completing"
          style="display: none"
        >
          完成订单
        </el-button>
        
        <!-- 打款操作 -->
        <el-button
          v-if="canShowPaymentButton"
          type="warning"
          @click="openPaymentDialog"
        >
          打款给用户
        </el-button>
        <el-tag
          v-if="paymentBlockedReason"
          type="info"
          size="small"
          style="margin-left: 8px"
        >
          {{ paymentBlockedReason }}
        </el-tag>
        
        <!-- 发布为官方验商品 -->
        <el-button
          v-if="detail.status === 'inspected' && detail.final_price && hasPerm('recycled:write')"
          type="success"
          @click="publishToVerified"
          :loading="publishing"
        >
          发布为官方验商品
        </el-button>
        
        <!-- 取消订单 -->
        <el-button
          v-if="['pending', 'shipped'].includes(detail.status) && hasPerm('inspection:write')"
          type="danger"
          @click="cancelOrder"
        >
          取消订单
        </el-button>
      </div>
    </el-card>

    <!-- 质检报告对话框 -->
    <el-dialog
      v-model="showReportDialog"
      title="质检报告"
      width="900px"
      @close="resetReportForm"
    >
      <el-form :model="reportForm" label-width="100px">
        <!-- 详细质检报告（66项检测） -->
        <el-form-item label="">
          <div class="inspection-editor-wrapper">
            <div class="inspection-header">
              <span class="inspection-title">详细质检报告（66项检测）</span>
              <el-button size="small" @click="toggleAllInspectionCategories">
                {{ allInspectionExpanded ? '全部收起' : '全部展开' }}
              </el-button>
            </div>
            
            <el-collapse v-model="activeInspectionCategories" class="inspection-collapse">
              <!-- 外观检测 -->
              <el-collapse-item name="appearance" title="外观检测（12项）">
                <div class="inspection-group">
                  <div class="group-title">外壳外观</div>
                  <div class="inspection-items">
                    <div v-for="(item, idx) in inspectionData.appearance.items" :key="idx" class="inspection-item">
                      <span class="item-label">{{ item.label }}</span>
                      <el-input v-model="item.value" placeholder="检测结果" size="small" style="width: 150px;" />
                      <el-select v-model="item.pass" size="small" style="width: 100px;">
                        <el-option label="正常" :value="true" />
                        <el-option label="异常" :value="false" />
                      </el-select>
                      <div v-if="!item.pass" class="item-image">
                        <el-input
                          v-model="item.image"
                          placeholder="异常图片URL"
                          size="small"
                          style="width: 200px;"
                        />
                        <el-upload
                          :show-file-list="false"
                          accept="image/*"
                          :http-request="(options) => handleInspectionImageUpload(options, item)"
                        >
                          <el-button size="small" :icon="Plus">上传</el-button>
                        </el-upload>
                        <el-image
                          v-if="item.image"
                          class="item-image-thumb"
                          :src="normalizeToUrl(item.image)"
                          fit="cover"
                          @click="openInspectionPreview(item.image)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </el-collapse-item>

              <!-- 屏幕检测 -->
              <el-collapse-item name="screen" title="屏幕检测（16项）">
                <div class="inspection-group">
                  <div class="group-title">屏幕触控</div>
                  <div class="inspection-items">
                    <div v-for="(item, idx) in inspectionData.screen.touch" :key="idx" class="inspection-item">
                      <span class="item-label">{{ item.label }}</span>
                      <el-input v-model="item.value" placeholder="检测结果" size="small" style="width: 150px;" />
                      <el-select v-model="item.pass" size="small" style="width: 100px;">
                        <el-option label="正常" :value="true" />
                        <el-option label="异常" :value="false" />
                      </el-select>
                      <div v-if="!item.pass" class="item-image">
                        <el-input
                          v-model="item.image"
                          placeholder="异常图片URL"
                          size="small"
                          style="width: 200px;"
                        />
                        <el-upload
                          :show-file-list="false"
                          accept="image/*"
                          :http-request="(options) => handleInspectionImageUpload(options, item)"
                        >
                          <el-button size="small" :icon="Plus">上传</el-button>
                        </el-upload>
                        <el-image
                          v-if="item.image"
                          class="item-image-thumb"
                          :src="normalizeToUrl(item.image)"
                          fit="cover"
                          @click="openInspectionPreview(item.image)"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div class="inspection-group">
                  <div class="group-title">屏幕外观</div>
                  <div class="inspection-items">
                    <div v-for="(item, idx) in inspectionData.screen.appearance" :key="idx" class="inspection-item">
                      <span class="item-label">{{ item.label }}</span>
                      <el-input v-model="item.value" placeholder="检测结果" size="small" style="width: 150px;" />
                      <el-select v-model="item.pass" size="small" style="width: 100px;">
                        <el-option label="正常" :value="true" />
                        <el-option label="异常" :value="false" />
                      </el-select>
                      <div v-if="!item.pass" class="item-image">
                        <el-input
                          v-model="item.image"
                          placeholder="异常图片URL"
                          size="small"
                          style="width: 200px;"
                        />
                        <el-upload
                          :show-file-list="false"
                          accept="image/*"
                          :http-request="(options) => handleInspectionImageUpload(options, item)"
                        >
                          <el-button size="small" :icon="Plus">上传</el-button>
                        </el-upload>
                        <el-image
                          v-if="item.image"
                          class="item-image-thumb"
                          :src="normalizeToUrl(item.image)"
                          fit="cover"
                          @click="openInspectionPreview(item.image)"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div class="inspection-group">
                  <div class="group-title">屏幕显示</div>
                  <div class="inspection-items">
                    <div v-for="(item, idx) in inspectionData.screen.display" :key="idx" class="inspection-item">
                      <span class="item-label">{{ item.label }}</span>
                      <el-input v-model="item.value" placeholder="检测结果" size="small" style="width: 150px;" />
                      <el-select v-model="item.pass" size="small" style="width: 100px;">
                        <el-option label="正常" :value="true" />
                        <el-option label="异常" :value="false" />
                      </el-select>
                      <div v-if="!item.pass" class="item-image">
                        <el-input
                          v-model="item.image"
                          placeholder="异常图片URL"
                          size="small"
                          style="width: 200px;"
                        />
                        <el-upload
                          :show-file-list="false"
                          accept="image/*"
                          :http-request="(options) => handleInspectionImageUpload(options, item)"
                        >
                          <el-button size="small" :icon="Plus">上传</el-button>
                        </el-upload>
                        <el-image
                          v-if="item.image"
                          class="item-image-thumb"
                          :src="normalizeToUrl(item.image)"
                          fit="cover"
                          @click="openInspectionPreview(item.image)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </el-collapse-item>

              <!-- 设备功能 -->
              <el-collapse-item name="function" title="设备功能（30项）">
                <div v-for="(group, groupKey) in inspectionData.function" :key="groupKey" class="inspection-group">
                  <div class="group-title">{{ group.name }}</div>
                  <div class="inspection-items">
                    <div v-for="(item, idx) in group.items" :key="idx" class="inspection-item">
                      <span class="item-label">{{ item.label }}</span>
                      <el-input v-model="item.value" placeholder="检测结果" size="small" style="width: 150px;" />
                      <el-select v-model="item.pass" size="small" style="width: 100px;">
                        <el-option label="正常" :value="true" />
                        <el-option label="异常" :value="false" />
                      </el-select>
                      <div v-if="!item.pass" class="item-image">
                        <el-input
                          v-model="item.image"
                          placeholder="异常图片URL"
                          size="small"
                          style="width: 200px;"
                        />
                        <el-upload
                          :show-file-list="false"
                          accept="image/*"
                          :http-request="(options) => handleInspectionImageUpload(options, item)"
                        >
                          <el-button size="small" :icon="Plus">上传</el-button>
                        </el-upload>
                        <el-image
                          v-if="item.image"
                          class="item-image-thumb"
                          :src="normalizeToUrl(item.image)"
                          fit="cover"
                          @click="openInspectionPreview(item.image)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </el-collapse-item>

              <!-- 维修浸液 -->
              <el-collapse-item name="repair" title="维修浸液（8项）">
                <div class="inspection-group">
                  <div class="group-title">维修浸液</div>
                  <div class="inspection-items">
                    <div v-for="(item, idx) in inspectionData.repair.items" :key="idx" class="inspection-item">
                      <span class="item-label">{{ item.label }}</span>
                      <el-input v-model="item.value" placeholder="检测结果" size="small" style="width: 150px;" />
                      <el-select v-model="item.pass" size="small" style="width: 100px;">
                        <el-option label="正常" :value="true" />
                        <el-option label="异常" :value="false" />
                      </el-select>
                      <div v-if="!item.pass" class="item-image">
                        <el-input
                          v-model="item.image"
                          placeholder="异常图片URL"
                          size="small"
                          style="width: 200px;"
                        />
                        <el-upload
                          :show-file-list="false"
                          accept="image/*"
                          :http-request="(options) => handleInspectionImageUpload(options, item)"
                        >
                          <el-button size="small" :icon="Plus">上传</el-button>
                        </el-upload>
                        <el-image
                          v-if="item.image"
                          class="item-image-thumb"
                          :src="normalizeToUrl(item.image)"
                          fit="cover"
                          @click="openInspectionPreview(item.image)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-form-item>

        <el-form-item label="质检备注">
          <el-input
            v-model="reportForm.remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入质检备注信息"
          />
        </el-form-item>

        <el-form-item label="最终价格" required>
          <el-input-number
            v-model="reportForm.final_price"
            :precision="2"
            :min="0"
            style="width: 100%"
            placeholder="根据质检结果设置最终价格"
          />
        </el-form-item>
        <el-form-item label="加价">
          <el-input-number
            v-model="reportForm.bonus"
            :precision="2"
            :min="0"
            style="width: 100%"
            placeholder="额外加价金额（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReportDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingReport" @click="saveReport">
          保存并完成质检
        </el-button>
      </template>
    </el-dialog>

    <!-- 价格对话框 -->
    <el-dialog
      v-model="priceDialogVisible"
      title="设置预估价格"
      width="500px"
      @close="priceDialogVisible = false"
    >
      <el-form :model="priceForm" label-width="120px">
        <el-form-item label="预估价格" required>
          <el-input-number
            v-model="priceForm.estimated_price"
            :precision="2"
            :min="0"
            style="width: 100%"
            placeholder="请输入预估价格"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px">
            设置预估价格（订单提交后已自动进入"已寄出"状态）
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="priceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingPrice" @click="saveEstimatedPrice">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 打款对话框 -->
    <el-dialog
      v-model="showPaymentDialog"
      title="打款给用户"
      width="500px"
    >
      <el-alert
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <div>
          <div>打款金额：<strong style="color: #f56c6c; font-size: 18px">¥{{ detail.total_price || detail.final_price }}</strong></div>
          <div style="margin-top: 8px; font-size: 12px">
            请确认用户已同意最终价格，打款后订单将标记为已打款
          </div>
        </div>
      </el-alert>
      <el-form :model="paymentForm" label-width="100px">
        <el-form-item label="打款方式" required>
          <el-select v-model="paymentForm.payment_method" style="width: 100%">
            <el-option label="存入易淘钱包" value="wallet" />
            <el-option label="支付方直接转账" value="transfer" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="paymentForm.payment_method === 'transfer'" label="打款账户" required>
          <el-input
            v-model="paymentForm.payment_account"
            :placeholder="(detail.user && detail.user.alipay_login_id) ? ('已绑定：' + detail.user.alipay_login_id) : '请输入用户的收款账户'"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="paymentForm.note"
            type="textarea"
            :rows="3"
            placeholder="打款备注信息（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPaymentDialog = false">取消</el-button>
        <el-button type="primary" :loading="processingPayment" @click="processPayment">
          确认打款
        </el-button>
      </template>
    </el-dialog>


    <!-- 参考用户端回收订单详情的全屏预览效果（Teleport 到 body，避免被管理端布局 transform/overflow 限制） -->
    <teleport to="body">
      <el-image-viewer
        v-if="inspectionPreviewVisible"
        :url-list="inspectionPreviewSrcList"
        :initial-index="0"
        teleported
        show-progress
        @close="inspectionPreviewVisible = false"
      />
    </teleport>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import adminApi from '@/utils/adminApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Loading, Clock, Plus } from '@element-plus/icons-vue'
import { useAdminAuthStore } from '@/stores/adminAuth'
import InspectionReport from '@/components/InspectionReport.vue'
import { getImageUrl } from '@/utils/image'
import { getRecycleProcessSteps, getRecycleStatusTag, getRecycleStage, isRecycleStepActive, isRecycleStepCompleted } from '@/utils/recycleFlow'

const router = useRouter()

const props = defineProps({
  orderId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['updated'])

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)

const loading = ref(false)
const detail = ref({})
const savingPrice = ref(false)
const savingReport = ref(false)
const markingReceived = ref(false)
const updatingStatus = ref(false)
const completing = ref(false)
const processingPayment = ref(false)
const publishing = ref(false)
const creatingDevice = ref(false)

const showReportDialog = ref(false)
const priceDialogVisible = ref(false)
const showPaymentDialog = ref(false)
const inspectionPreviewVisible = ref(false)
const inspectionPreviewSrcList = ref([])

const priceForm = reactive({
  estimated_price: 0,
  final_price: 0,
  bonus: 0
})

const reportForm = reactive({
  remarks: '',
  checkItemsJson: '{}',
  final_price: 0,
  bonus: 0
})

const uploadEndpoint = import.meta.env.VITE_ADMIN_UPLOAD_URL || '/uploads/images/'
const normalizeToUrl = (url) => (url ? getImageUrl(url) || url : '')

const openInspectionPreview = (url) => {
  const resolved = normalizeToUrl(url)
  if (!resolved) return
  inspectionPreviewSrcList.value = [resolved]
  inspectionPreviewVisible.value = true
}

const handleInspectionImageUpload = async (options, item) => {
  const { file, onError, onSuccess } = options
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await adminApi.post(uploadEndpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const url = res.data?.url || res.data?.image || res.data?.path
    if (!url) throw new Error('上传返回空URL')
    item.image = url
    onSuccess?.(res.data)
  } catch (err) {
    ElMessage.error('上传失败')
    onError?.(err)
  }
}

// 检测详情（供 InspectionReport 展示）
const inspectionReportData = computed(() => {
  if (!detail.value || !detail.value.report) return null
  const baseInfo = {
    model: `${detail.value.brand || ''} ${detail.value.model || ''}`.trim(),
    level: `外观 ${getConditionText(detail.value.condition) || ''}`,
    spec: detail.value.storage || '',
    color: detail.value.selected_color || detail.value.color || '',
    price: detail.value.final_price || detail.value.estimated_price || '',
    coverImage: detail.value.cover_image || ''
  }

  let categories = detail.value.report.categories || []
  const checkItems = detail.value.report.check_items

  if ((!categories || categories.length === 0) && checkItems) {
    if (Array.isArray(checkItems) && checkItems.length) {
      // 若本身是分类结构（带 title / groups），直接使用
      if (checkItems[0].title || checkItems[0].groups) {
        categories = checkItems
      } else {
        categories = [{
          title: '检测结果',
          groups: [{
            name: '',
            items: checkItems.map(item => ({
              label: item.label || item.key || '',
              value: item.value ?? item.result ?? '',
              pass: typeof item.pass === 'boolean' ? item.pass : (item.value === 'pass' || item.value === true)
            }))
          }]
        }]
      }
    } else if (typeof checkItems === 'object') {
      categories = [{
        title: '检测结果',
        groups: [{
          name: '',
          items: Object.entries(checkItems).map(([key, val]) => ({
            label: key,
            value: val,
            pass: val === 'pass' || val === true
          }))
        }]
      }]
    }
  }

  return { baseInfo, categories }
})

// 质检报告数据结构
const activeInspectionCategories = ref([])
const allInspectionExpanded = ref(false)

const inspectionData = reactive({
  appearance: {
    items: [
      { label: '碎裂', value: '无', pass: true, image: '' },
      { label: '划痕', value: '无', pass: true, image: '' },
      { label: '机身弯曲', value: '无', pass: true, image: '' },
      { label: '脱胶/缝隙', value: '无', pass: true, image: '' },
      { label: '外壳/其他', value: '正常', pass: true, image: '' },
      { label: '磕碰', value: '几乎不可见', pass: true, image: '' },
      { label: '刻字/图', value: '无', pass: true, image: '' },
      { label: '掉漆/磨损', value: '几乎不可见', pass: true, image: '' },
      { label: '摄像头/闪光灯外观', value: '正常', pass: true, image: '' },
      { label: '褶皱', value: '无', pass: true, image: '' },
      { label: '卡托', value: '正常', pass: true, image: '' },
      { label: '音频网罩', value: '正常', pass: true, image: '' }
    ]
  },
  screen: {
    touch: [
      { label: '触控', value: '正常', pass: true, image: '' }
    ],
    appearance: [
      { label: '屏幕/其它', value: '正常', pass: true, image: '' },
      { label: '碎裂', value: '无', pass: true, image: '' },
      { label: '内屏掉漆/划伤', value: '无', pass: true, image: '' },
      { label: '屏幕凸点（褶皱）', value: '正常', pass: true, image: '' },
      { label: '支架破损', value: '无', pass: true, image: '' },
      { label: '浅划痕', value: '几乎不可见', pass: true, image: '' },
      { label: '深划痕', value: '几乎不可见', pass: true, image: '' }
    ],
    display: [
      { label: '进灰', value: '无', pass: true, image: '' },
      { label: '坏点', value: '无', pass: true, image: '' },
      { label: '气泡', value: '无', pass: true, image: '' },
      { label: '色斑', value: '无', pass: true, image: '' },
      { label: '其它', value: '正常', pass: true, image: '' },
      { label: '亮点/亮斑', value: '无', pass: true, image: '' },
      { label: '泛红/泛黄', value: '无', pass: true, image: '' },
      { label: '图文残影', value: '无', pass: true, image: '' }
    ]
  },
  function: {
    buttons: {
      name: '按键',
      items: [
        { label: '电源键', value: '正常', pass: true, image: '' },
        { label: '音量键', value: '正常', pass: true, image: '' },
        { label: '静音键', value: '正常', pass: true, image: '' },
        { label: '其它按键', value: '正常', pass: true, image: '' }
      ]
    },
    biometric: {
      name: '生物识别',
      items: [
        { label: '面部识别', value: '正常', pass: true, image: '' },
        { label: '指纹识别', value: '正常', pass: true, image: '' }
      ]
    },
    sensors: {
      name: '传感器',
      items: [
        { label: '重力感应', value: '正常', pass: true, image: '' },
        { label: '指南针', value: '正常', pass: true, image: '' },
        { label: '距离感应', value: '正常', pass: true, image: '' },
        { label: '光线感应', value: '正常', pass: true, image: '' }
      ]
    },
    ports: {
      name: '接口',
      items: [
        { label: '充电接口', value: '正常', pass: true, image: '' },
        { label: '耳机接口', value: '正常', pass: true, image: '' }
      ]
    },
    wireless: {
      name: '无线',
      items: [
        { label: 'WiFi', value: '正常', pass: true, image: '' },
        { label: '蓝牙', value: '正常', pass: true, image: '' },
        { label: 'GPS', value: '正常', pass: true, image: '' },
        { label: 'NFC', value: '正常', pass: true, image: '' }
      ]
    },
    charging: {
      name: '充电',
      items: [
        { label: '充电功能', value: '正常', pass: true, image: '' },
        { label: '无线充电', value: '正常', pass: true, image: '' }
      ]
    },
    call: {
      name: '通话功能',
      items: [
        { label: '通话', value: '正常', pass: true, image: '' },
        { label: '信号', value: '正常', pass: true, image: '' }
      ]
    },
    audio: {
      name: '声音与振动',
      items: [
        { label: '扬声器', value: '正常', pass: true, image: '' },
        { label: '麦克风', value: '正常', pass: true, image: '' },
        { label: '振动', value: '正常', pass: true, image: '' }
      ]
    },
    camera: {
      name: '摄像头',
      items: [
        { label: '前置摄像头', value: '正常', pass: true, image: '' },
        { label: '后置摄像头', value: '正常', pass: true, image: '' },
        { label: '闪光灯', value: '正常', pass: true, image: '' }
      ]
    },
    other: {
      name: '其它状况',
      items: [
        { label: '电池健康', value: '未检测', pass: true, image: '' }
      ]
    }
  },
  repair: {
    items: [
      { label: '屏幕', value: '未检出维修更换', pass: true, image: '' },
      { label: '主板', value: '未检出维修', pass: true, image: '' },
      { label: '机身', value: '未检出维修更换', pass: true, image: '' },
      { label: '零件维修/更换', value: '未检出维修更换', pass: true, image: '' },
      { label: '零件缺失', value: '未检出缺失', pass: true, image: '' },
      { label: '后摄维修情况', value: '未检出维修更换', pass: true, image: '' },
      { label: '前摄维修情况', value: '未检出维修更换', pass: true, image: '' },
      { label: '浸液痕迹情况', value: '未检出浸液痕迹', pass: true, image: '' }
    ]
  }
})

const toggleAllInspectionCategories = () => {
  if (allInspectionExpanded.value) {
    activeInspectionCategories.value = []
  } else {
    activeInspectionCategories.value = ['appearance', 'screen', 'function', 'repair']
  }
  allInspectionExpanded.value = !allInspectionExpanded.value
}

// 将质检数据转换为API格式
const convertInspectionDataToAPI = () => {
  return [
    {
      title: '外观检测',
      images: [],
      groups: [
        {
          name: '外壳外观',
          items: inspectionData.appearance.items.map(item => ({
            label: item.label,
            value: item.value,
            pass: item.pass,
            ...(item.image && !item.pass ? { image: item.image } : {})
          }))
        }
      ]
    },
    {
      title: '屏幕检测',
      images: [],
      groups: [
        {
          name: '屏幕触控',
          items: inspectionData.screen.touch.map(item => ({
            label: item.label,
            value: item.value,
            pass: item.pass,
            ...(item.image && !item.pass ? { image: item.image } : {})
          }))
        },
        {
          name: '屏幕外观',
          items: inspectionData.screen.appearance.map(item => ({
            label: item.label,
            value: item.value,
            pass: item.pass,
            ...(item.image && !item.pass ? { image: item.image } : {})
          }))
        },
        {
          name: '屏幕显示',
          items: inspectionData.screen.display.map(item => ({
            label: item.label,
            value: item.value,
            pass: item.pass,
            ...(item.image && !item.pass ? { image: item.image } : {})
          }))
        }
      ]
    },
    {
      title: '设备功能',
      images: [],
      groups: Object.values(inspectionData.function).map(group => ({
        name: group.name,
        items: group.items.map(item => ({
          label: item.label,
          value: item.value,
          pass: item.pass,
          ...(item.image && !item.pass ? { image: item.image } : {})
        }))
      }))
    },
    {
      title: '维修浸液',
      images: [],
      groups: [
        {
          name: '维修浸液',
          items: inspectionData.repair.items.map(item => ({
            label: item.label,
            value: item.value,
            pass: item.pass,
            ...(item.image && !item.pass ? { image: item.image } : {})
          }))
        }
      ],
      footer: {
        label: '拆机检测',
        value: '平台未拆机检测'
      }
    }
  ]
}

const paymentForm = reactive({
  payment_method: 'wallet',
  payment_account: '',
  note: ''
})

// 打款按钮显示条件计算属性
const canShowPaymentButton = computed(() => {
  if (!detail.value) return false

  const isCompleted = detail.value.status === 'completed'
  const notPaid = detail.value.payment_status !== 'paid'
  const hasFinalPrice = !!detail.value.final_price
  const isConfirmed = !!detail.value.final_price_confirmed
  const noDispute = !detail.value.price_dispute
  const hasPermission = hasPerm('inspection:payment')

  return (
    isCompleted &&
    notPaid &&
    hasFinalPrice &&
    isConfirmed &&
    noDispute &&
    hasPermission
  )
})

const paymentBlockedReason = computed(() => {
  if (!detail.value) return ''
  if (detail.value.payment_status === 'paid') return ''
  if (canShowPaymentButton.value) return ''

  if (detail.value.status !== 'completed' && detail.value.payment_status !== 'failed') return ''
  if (!detail.value.final_price) return ''
  if (detail.value.price_dispute) return '用户已提交价格异议'
  if (!detail.value.final_price_confirmed) return '等待用户确认最终价格'
  if (!hasPerm('inspection:payment')) return '无打款权限'
  return '暂无法打款'
})

// 流程步骤
const processSteps = [
  { label: '提交订单', value: 'pending' },
  { label: '已寄出', value: 'shipped' },
  { label: '已收货', value: 'received' },
  { label: '已检测', value: 'inspected' },
  { label: '已完成', value: 'completed' },
  { label: '已打款', value: 'paid' }
]

const statusMap = {
  pending: { text: '待估价', type: 'info' },
  received: { text: '已收货', type: 'success' },
  shipped: { text: '已寄出', type: 'primary' },
  inspected: { text: '已检测', type: 'success' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'info' }
} 

const openPaymentDialog = () => {
  const loginId = (detail.value && detail.value.user && detail.value.user.alipay_login_id) ? detail.value.user.alipay_login_id : ''
  paymentForm.payment_method = loginId ? 'transfer' : 'wallet'
  paymentForm.payment_account = loginId || ''
  showPaymentDialog.value = true
}

const conditionMap = {
  new: { text: '全新', type: 'success' },
  like_new: { text: '几乎全新', type: 'success' },
  good: { text: '良好', type: 'primary' },
  fair: { text: '一般', type: 'warning' },
  poor: { text: '较差', type: 'danger' }
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'
const getConditionText = (condition) => conditionMap[condition]?.text || condition
const getConditionType = (condition) => conditionMap[condition]?.type || 'info'

const progressStage = computed(() => getRecycleStage(detail.value))
const displayStatusTag = computed(() => getRecycleStatusTag(detail.value))
const getProcessStepLabel = (stepValue) => getRecycleProcessSteps(detail.value).find(s => s.value === stepValue)?.label || stepValue

const isStepCompleted = (stepValue) => {
  return isRecycleStepCompleted(detail.value, stepValue)
}

const isStepActive = (stepValue) => {
  return isRecycleStepActive(detail.value, stepValue)
}

const getStepTime = (stepValue) => {
  const timeMap = {
    pending: detail.value.created_at,
    quoted: detail.value.created_at,
    confirmed: detail.value.created_at,
    shipped: detail.value.shipped_at,
    inspected: detail.value.inspected_at,
    completed: detail.value.updated_at,
    paid: detail.value.paid_at
  }
  return formatTime(timeMap[stepValue])
}

const canCreateReport = computed(() => {
  return ['shipped', 'received'].includes(detail.value.status) && detail.value.received_at
})

const canManagePrice = computed(() => {
  return detail.value && ['pending', 'received', 'inspected'].includes(detail.value.status)
})

const isShippedStage = computed(() => detail.value?.status === 'shipped')

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await adminApi.get(`/inspection-orders/${props.orderId}`)
    if (res.data?.success) {
      detail.value = res.data.item || {}
      priceForm.estimated_price = detail.value.estimated_price || 0
      priceForm.final_price = detail.value.final_price || 0
      priceForm.bonus = detail.value.bonus || 0
      
      if (detail.value.report) {
        reportForm.remarks = detail.value.report.remarks || ''
        reportForm.checkItemsJson = JSON.stringify(detail.value.report.check_items || {}, null, 2)
      }
      reportForm.final_price = detail.value.final_price || detail.value.estimated_price || 0
      reportForm.bonus = detail.value.bonus || 0
    } else {
      ElMessage.error('加载失败')
    }
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

watch(
  () => props.orderId,
  (val) => {
    if (val) {
      loadDetail()
    }
  },
  { immediate: true }
)

const markReceived = async () => {
  try {
    await ElMessageBox.confirm('确认已收到设备？确认后将更新订单状态为"已收货"', '确认收货', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消'
    })
    markingReceived.value = true
    const res = await adminApi.post(`/inspection-orders/${props.orderId}/logistics`, {
      action: 'receive'
    })
    if (res.data?.success) {
      ElMessage.success('已确认收到设备')
      await loadDetail()
      emit('updated')
    } else {
      ElMessage.error(res.data?.detail || '操作失败')
    }
  } catch (error) {
    console.error('确认收到设备失败:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.error || error.message || '操作失败'
    ElMessage.error(errorMsg)
  } finally {
    markingReceived.value = false
  }
}

const showPriceDialog = (type) => {
  if (type === 'estimated') {
    priceForm.estimated_price = detail.value.estimated_price || 0
  }
  priceDialogVisible.value = true
}

const saveEstimatedPrice = async () => {
  if (!priceForm.estimated_price || priceForm.estimated_price <= 0) {
    ElMessage.warning('请输入有效的预估价格')
    return
  }
  
  // 检查token是否存在
  const token = localStorage.getItem('ADMIN_TOKEN')
  if (!token) {
    ElMessage.error('登录已过期，请重新登录')
    setTimeout(() => {
      window.location.href = '/admin/login'
    }, 1000)
    return
  }
  
  try {
    savingPrice.value = true
    
    // 直接发送请求，让拦截器处理token
    await adminApi.put(`/inspection-orders/${props.orderId}/price`, {
      price_type: 'estimated',
      estimated_price: priceForm.estimated_price
    })
    ElMessage.success('预估价格设置成功')
    priceDialogVisible.value = false
    await loadDetail()
    emit('updated')
  } catch (error) {
    console.error('保存预估价格失败:', error, error.response)
    
    // 如果是401错误，拦截器已经处理了跳转和错误提示，这里不需要重复处理
    if (error.response?.status === 401) {
      // 拦截器已经显示了错误提示并会跳转，这里不需要额外处理
      return
    }
    
    // 其他错误显示具体错误信息
    const errorMsg = error.response?.data?.detail || error.response?.data?.error || error.message || '保存失败'
    ElMessage.error(errorMsg)
  } finally {
    savingPrice.value = false
  }
}

const saveFinalPrice = async () => {
  if (!priceForm.final_price || priceForm.final_price <= 0) {
    ElMessage.warning('请输入有效的最终价格')
    return
  }
  try {
    savingPrice.value = true
    await adminApi.put(`/inspection-orders/${props.orderId}/price`, {
      price_type: 'final',
      final_price: priceForm.final_price,
      bonus: priceForm.bonus || 0
    })
    ElMessage.success('价格更新成功')
    await loadDetail()
    emit('updated')
  } catch (error) {
    console.error('保存最终价格失败:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.error || error.message || '更新失败'
    ElMessage.error(errorMsg)
    
    // 如果是认证错误，提示用户重新登录
    if (error.response?.status === 401) {
      ElMessage.warning('登录已过期，请重新登录')
    }
  } finally {
    savingPrice.value = false
  }
}

  const saveReport = async () => {
    try {
      if (!reportForm.final_price || reportForm.final_price <= 0) {
        ElMessage.warning('请输入有效的最终价格')
        return
      }
      savingReport.value = true
    
    // 将质检数据转换为API格式
    const inspectionReportData = convertInspectionDataToAPI()
    
    // 先保存质检报告
    await adminApi.post(`/inspection-orders/${props.orderId}/report`, {
      check_items: inspectionReportData,
      remarks: reportForm.remarks
    })
    
    // 再更新最终价格
    await adminApi.put(`/inspection-orders/${props.orderId}/price`, {
      price_type: 'final',
      final_price: reportForm.final_price,
      bonus: reportForm.bonus || 0
    })
    
    ElMessage.success('质检报告保存成功，订单状态已更新为已检测')
    showReportDialog.value = false
    await loadDetail()
    emit('updated')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    savingReport.value = false
  }
}

const completeOrder = async () => {
  try {
    await ElMessageBox.confirm(
      '完成订单后，将等待用户确认价格。确认后可以进行打款操作。',
      '确认完成订单',
      { type: 'warning' }
    )
    completing.value = true
    await adminApi.put(`/inspection-orders/${props.orderId}`, { status: 'completed' })
    ElMessage.success('订单已完成')
    await loadDetail()
    emit('updated')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    completing.value = false
  }
}

const processPayment = async () => {
  if (!paymentForm.payment_method) {
    ElMessage.warning('请选择打款方式')
    return
  }
  if (paymentForm.payment_method === 'transfer' && !paymentForm.payment_account) {
    ElMessage.warning('请输入收款账户')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认向用户打款 ¥${detail.value.total_price || detail.value.final_price} 吗？`,
      '确认打款',
      { type: 'warning' }
    )
    processingPayment.value = true
    await adminApi.post(`/inspection-orders/${props.orderId}/payment`, {
      payment_method: paymentForm.payment_method,
      payment_account: paymentForm.payment_account,
      note: paymentForm.note
    })
    ElMessage.success('打款成功')
    showPaymentDialog.value = false
    await loadDetail()
    emit('updated')
  } catch (error) {
    if (error !== 'cancel') {
      const errorData = error.response?.data
      let errorMessage = '打款失败'
      if (errorData?.detail) {
        errorMessage = errorData.detail
        // 显示更详细的错误信息
        if (errorData.current_status) {
          errorMessage += ` (当前状态: ${errorData.current_status})`
        }
        if (errorData.payment_status) {
          errorMessage += ` (打款状态: ${errorData.payment_status})`
        }
      }
      ElMessage.error(errorMessage)
      console.error('打款失败详情:', errorData)
    }
  } finally {
    processingPayment.value = false
  }
}

const createVerifiedDevice = async () => {
  try {
    creatingDevice.value = true
    const res = await adminApi.post(`/recycle-orders/${props.orderId}/create-verified-device/`)
    const msg = res.data?.detail || '已生成官方验库存'
    ElMessage.success(msg)
    await loadDetail()
    emit('updated')
  } catch (error) {
    const msg = error.response?.data?.detail || '生成失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    creatingDevice.value = false
  }
}

const publishToVerified = async () => {
  try {
    await ElMessageBox.confirm(
      '确认将此回收商品发布为官方验商品吗？',
      '确认发布',
      { type: 'warning' }
    )
    publishing.value = true
    await adminApi.post(`/inspection-orders/${props.orderId}/publish-verified`)
    ElMessage.success('发布成功')
    await loadDetail()
    emit('updated')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('发布失败')
    }
  } finally {
    publishing.value = false
  }
}

const cancelOrder = async () => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      '请输入取消原因',
      '取消订单',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '请输入取消原因'
      }
    )
    await adminApi.put(`/inspection-orders/${props.orderId}`, {
      status: 'cancelled',
      reject_reason: reason
    })
    ElMessage.success('订单已取消')
    await loadDetail()
    emit('updated')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

const resetReportForm = () => {
  if (detail.value.report) {
    reportForm.remarks = detail.value.report.remarks || ''
    reportForm.checkItemsJson = JSON.stringify(detail.value.report.check_items || {}, null, 2)
  } else {
    reportForm.remarks = ''
    reportForm.checkItemsJson = '{}'
  }
  reportForm.final_price = detail.value.final_price || detail.value.estimated_price || 0
  reportForm.bonus = detail.value.bonus || 0
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getRiskTagType = (risk) => {
  const r = Number(risk || 0)
  if (r >= 0.7) return 'danger'
  if (r >= 0.4) return 'warning'
  return 'success'
}

const formatRisk = (risk) => {
  const r = Math.round(Number(risk || 0) * 100)
  return `${r}%`
}

// 格式化问卷问题的 key 为可读文本
const formatQuestionKey = (key) => {
  const keyMap = {
    channel: '购买渠道',
    color: '颜色',
    storage: '存储容量',
    screen_condition: '屏幕状况',
    battery_health: '电池健康度',
    appearance: '外观状况',
    function: '功能状况',
    accessories: '配件情况',
    warranty: '保修情况',
    purchase_time: '购买时间',
    usage_time: '使用时长',
    repair_history: '维修历史',
    water_damage: '进水情况'
  }
  return keyMap[key] || key
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.recycle-order-detail {
  padding: 0;
}

.detail-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.check-items {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 13px;
  margin: 0;
  max-height: 300px;
  overflow: auto;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.process-timeline {
  display: flex;
  align-items: flex-start;
  gap: 0;
  padding: 20px 0;
  overflow-x: auto;
}

.timeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  min-width: 120px;
  flex: 1;
}

.timeline-marker {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  position: relative;
  z-index: 2;
  transition: all 0.3s;
}

.timeline-step.pending .timeline-marker {
  background: #e4e7ed;
  color: #909399;
}

.timeline-step.active .timeline-marker {
  background: #409eff;
  color: #fff;
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
}

.timeline-step.completed .timeline-marker {
  background: #67c23a;
  color: #fff;
}

.timeline-content {
  margin-top: 8px;
  text-align: center;
}

.step-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.timeline-step.pending .step-title {
  color: #909399;
}

.step-time {
  font-size: 12px;
  color: #909399;
}

.timeline-line {
  position: absolute;
  top: 16px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #e4e7ed;
  z-index: 1;
}

.timeline-step:last-child .timeline-line {
  display: none;
}

.timeline-step.completed .timeline-line {
  background: #67c23a;
}

/* 质检报告编辑器样式 */
.inspection-editor-wrapper {
  width: 100%;
}

.inspection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.inspection-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.inspection-collapse {
  border: none;
}

.inspection-group {
  margin-bottom: 20px;
}

.group-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #409eff;
}

.inspection-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.inspection-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.item-label {
  min-width: 120px;
  font-size: 13px;
  color: #606266;
}

.item-image {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-image-thumb {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  border: 1px solid #e6e8ee;
  background: #fff;
  cursor: pointer;
}
</style>
