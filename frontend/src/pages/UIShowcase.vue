<template>
  <PageContainer 
    title="UI 设计系统展示" 
    subtitle="查看所有可用的组件和样式"
    background="page"
  >
    <!-- 颜色系统 -->
    <BaseCard title="颜色系统" class="mb-6">
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 16px;">
        <div style="text-align: center;">
          <div style="width: 80px; height: 80px; background: #ff6a00; border-radius: 12px; margin: 0 auto 8px;"></div>
          <span>Primary</span>
        </div>
        <div style="text-align: center;">
          <div style="width: 80px; height: 80px; background: #ffd700; border-radius: 12px; margin: 0 auto 8px;"></div>
          <span>Secondary</span>
        </div>
        <div style="text-align: center;">
          <div style="width: 80px; height: 80px; background: #10b981; border-radius: 12px; margin: 0 auto 8px;"></div>
          <span>Success</span>
        </div>
        <div style="text-align: center;">
          <div style="width: 80px; height: 80px; background: #f59e0b; border-radius: 12px; margin: 0 auto 8px;"></div>
          <span>Warning</span>
        </div>
        <div style="text-align: center;">
          <div style="width: 80px; height: 80px; background: #ef4444; border-radius: 12px; margin: 0 auto 8px;"></div>
          <span>Error</span>
        </div>
      </div>
    </BaseCard>

    <!-- 卡片组件 -->
    <BaseCard title="卡片组件" subtitle="不同样式的卡片" class="mb-6">
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
        <BaseCard shadow="sm" hover>
          <div style="padding: 16px;">
            <h3 style="font-size: 18px; font-weight: 700; margin-bottom: 8px;">默认卡片</h3>
            <p style="font-size: 14px; color: #6b7280;">这是一个带悬停效果的卡片</p>
          </div>
        </BaseCard>

        <BaseCard title="带标题的卡片" shadow="md">
          <p style="font-size: 14px;">卡片内容区域</p>
        </BaseCard>

        <BaseCard title="完整卡片" subtitle="包含标题、内容和底部" shadow="lg">
          <p style="font-size: 14px; margin-bottom: 16px;">这是卡片的主要内容区域</p>
          
          <template #footer>
            <div style="display: flex; justify-content: flex-end; gap: 8px;">
              <el-button size="small">取消</el-button>
              <el-button type="primary" size="small">确定</el-button>
            </div>
          </template>
        </BaseCard>
      </div>
    </BaseCard>

    <!-- 字体系统 -->
    <BaseCard title="字体系统" class="mb-6">
      <div style="display: flex; flex-direction: column; gap: 12px;">
        <div style="font-size: 12px;">Extra Small (12px)</div>
        <div style="font-size: 13px;">Small (13px)</div>
        <div style="font-size: 14px;">Base (14px)</div>
        <div style="font-size: 16px;">Large (16px)</div>
        <div style="font-size: 18px;">Extra Large (18px)</div>
        <div style="font-size: 20px;">2XL (20px)</div>
        <div style="font-size: 24px;">3XL (24px)</div>
      </div>

      <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid #e6e8ee;">
        <div style="font-weight: 400; margin-bottom: 8px;">Normal Weight (400)</div>
        <div style="font-weight: 500; margin-bottom: 8px;">Medium Weight (500)</div>
        <div style="font-weight: 600; margin-bottom: 8px;">Semibold Weight (600)</div>
        <div style="font-weight: 700; margin-bottom: 8px;">Bold Weight (700)</div>
        <div style="font-weight: 800; margin-bottom: 8px;">Extrabold Weight (800)</div>
      </div>
    </BaseCard>

    <!-- 工具类展示 -->
    <BaseCard title="工具类" class="mb-6">
      <div style="margin-bottom: 24px;">
        <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">间距</h4>
        <div class="flex gap-4">
          <div class="p-2 bg-gray-100 rounded-md">p-2</div>
          <div class="p-4 bg-gray-100 rounded-md">p-4</div>
          <div class="p-6 bg-gray-100 rounded-md">p-6</div>
        </div>
      </div>

      <div style="margin-bottom: 24px;">
        <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">圆角</h4>
        <div class="flex gap-4">
          <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #ff6a00, #ffd700);" class="rounded-sm"></div>
          <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #ff6a00, #ffd700);" class="rounded-md"></div>
          <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #ff6a00, #ffd700);" class="rounded-lg"></div>
          <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #ff6a00, #ffd700);" class="rounded-full"></div>
        </div>
      </div>

      <div>
        <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">阴影</h4>
        <div class="flex gap-4">
          <div style="width: 80px; height: 80px; background: white;" class="shadow-sm rounded-md"></div>
          <div style="width: 80px; height: 80px; background: white;" class="shadow-md rounded-md"></div>
          <div style="width: 80px; height: 80px; background: white;" class="shadow-lg rounded-md"></div>
        </div>
      </div>
    </BaseCard>

    <!-- 布局示例 -->
    <BaseCard title="布局示例">
      <div style="margin-bottom: 24px;">
        <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Flex 布局</h4>
        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <span>左侧内容</span>
          <span>中间内容</span>
          <span>右侧内容</span>
        </div>
      </div>

      <div>
        <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Grid 布局</h4>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
          <div class="p-4 bg-gray-50 rounded-lg text-center">Grid 1</div>
          <div class="p-4 bg-gray-50 rounded-lg text-center">Grid 2</div>
          <div class="p-4 bg-gray-50 rounded-lg text-center">Grid 3</div>
        </div>
      </div>
    </BaseCard>
  </PageContainer>
</template>

<script setup>
import PageContainer from '@/components/PageContainer.vue'
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
.mb-6 {
  margin-bottom: 24px;
}
</style>
