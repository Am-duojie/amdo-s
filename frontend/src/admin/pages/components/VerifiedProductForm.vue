<template>
  <div class="verified-product-form">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" class="form-grid">
      <!-- 基础信息 -->
      <el-card shadow="never" class="card-block">
        <template #header>基础信息</template>
      <el-form-item label="商品标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入商品标题" />
      </el-form-item>
      <el-form-item label="品牌" prop="brand">
        <el-input v-model="form.brand" placeholder="如：苹果、华为" />
      </el-form-item>
      <el-form-item label="型号" prop="model">
        <el-input v-model="form.model" placeholder="如：iPhone 13" />
      </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类">
            <el-option label="手机数码" value="phone" />
            <el-option label="平板/笔记本" value="tablet" />
            <el-option label="电脑办公" value="computer" />
            <el-option label="智能穿戴" value="watch" />
            <el-option label="耳机音响" value="audio" />
          </el-select>
        </el-form-item>
      <el-form-item label="存储容量">
        <el-input v-model="form.storage" placeholder="如：128GB" />
      </el-form-item>
      <el-form-item label="运行内存">
        <el-input v-model="form.ram" placeholder="如：6GB、8GB" />
      </el-form-item>
      <el-form-item label="版本">
        <el-input v-model="form.version" placeholder="如：国行、港版" />
      </el-form-item>
      <el-form-item label="拆修和功能">
        <el-input v-model="form.repair_status" placeholder="如：未拆未修、功能正常" />
      </el-form-item>
      <el-form-item label="成色" prop="condition">
        <el-select v-model="form.condition" style="width: 100%">
          <el-option label="全新" value="new" />
          <el-option label="99成新" value="like_new" />
          <el-option label="95成新" value="good" />
            <el-option label="9成新" value="fair" />
            <el-option label="8成新" value="poor" />
        </el-select>
      </el-form-item>
      <el-form-item label="价格" prop="price">
          <el-input-number v-model="form.price" :precision="2" :min="0.01" style="width: 100%" />
      </el-form-item>
      <el-form-item label="原价">
        <el-input-number v-model="form.original_price" :precision="2" :min="0" style="width: 100%" />
      </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="form.stock" :min="1" :max="9999" />
        </el-form-item>
        <el-form-item label="所在地" prop="location">
          <el-input v-model="form.location" placeholder="如：广东 深圳" />
        </el-form-item>
      <el-form-item label="商品描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入商品描述" />
      </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="form.tags" multiple filterable allow-create default-first-option placeholder="选择或输入标签">
            <el-option label="官方质检" value="官方质检" />
            <el-option label="正品保障" value="正品保障" />
            <el-option label="7天无理由" value="7天无理由" />
          </el-select>
        </el-form-item>
      </el-card>

      <!-- 媒体上传 -->
      <el-card shadow="never" class="card-block">
        <template #header>媒体上传</template>
        <el-form-item label="封面图" prop="cover_image">
          <el-upload
            class="upload-cover"
            :limit="1"
            accept="image/*"
            list-type="picture-card"
            :http-request="(options) => handleUpload(options, 'cover')"
            :file-list="coverFileList"
            :on-remove="() => (form.cover_image = '', coverFileList.splice(0))"
            :on-preview="handlePreview"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <el-form-item label="详情图(3~9)" prop="detail_images">
          <el-upload
            class="upload-detail"
            multiple
            list-type="picture-card"
            :limit="9"
            accept="image/*"
            :http-request="(options) => handleUpload(options, 'detail')"
            :file-list="detailFileList"
            :on-remove="handleDetailRemove"
            :on-preview="handlePreview"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-card>

      <!-- 详细质检报告 -->
      <el-card shadow="never" class="card-block full-width">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>详细质检报告（66项检测）</span>
            <el-button size="small" @click="toggleAllCategories">
              {{ allCategoriesExpanded ? '全部收起' : '全部展开' }}
            </el-button>
          </div>
        </template>
        
        <div class="inspection-editor">
          <el-collapse v-model="activeCategories">
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
                    <el-input 
                      v-if="!item.pass" 
                      v-model="item.image" 
                      placeholder="异常图片URL" 
                      size="small" 
                      style="width: 200px;"
                    />
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
                    <el-input 
                      v-if="!item.pass" 
                      v-model="item.image" 
                      placeholder="异常图片URL" 
                      size="small" 
                      style="width: 200px;"
                    />
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
                    <el-input 
                      v-if="!item.pass" 
                      v-model="item.image" 
                      placeholder="异常图片URL" 
                      size="small" 
                      style="width: 200px;"
                    />
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
                    <el-input 
                      v-if="!item.pass" 
                      v-model="item.image" 
                      placeholder="异常图片URL" 
                      size="small" 
                      style="width: 200px;"
                    />
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
                    <el-input 
                      v-if="!item.pass" 
                      v-model="item.image" 
                      placeholder="异常图片URL" 
                      size="small" 
                      style="width: 200px;"
                    />
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
                    <el-input 
                      v-if="!item.pass" 
                      v-model="item.image" 
                      placeholder="异常图片URL" 
                      size="small" 
                      style="width: 200px;"
                    />
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>
    </el-form>

    <div class="actions">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button :loading="saving" @click="submit(false)">{{ isEdit ? '保存' : '创建' }}</el-button>
      <el-button type="primary" :loading="saving" @click="submit(true)">保存并上架</el-button>
      <el-button v-if="isEdit && form.status === 'active'" type="warning" plain :loading="saving" @click="unpublish">
        下架
      </el-button>
    </div>

    <el-image-viewer
      v-if="previewVisible"
      :url-list="previewImages"
      :initial-index="previewIndex"
      @close="previewVisible = false"
    />
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getImageUrl } from '@/utils/image'

const props = defineProps({
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['created', 'cancel', 'updated'])

const formRef = ref()
const saving = ref(false)
const coverFileList = ref([])
const detailFileList = ref([])
const previewVisible = ref(false)
const previewImages = ref([])
const previewIndex = ref(0)

const isEdit = computed(() => !!props.product?.id)

const form = reactive({
  title: '',
  brand: '',
  model: '',
  storage: '',
  ram: '',  // 运行内存
  version: '',  // 版本
  repair_status: '',  // 拆修和功能
  condition: 'good',
  price: 0,
  original_price: 0,
  stock: 1,
  location: '',
  description: '',
  tags: [],
  cover_image: '',
  detail_images: [],
  inspection_reports: [], // 存储详细质检报告数据
  inspection_result: 'pass',
  inspection_date: '',
  inspection_staff: '',
  inspection_note: '',
  category: '',
  category_id: null,
  status: 'draft'
})

// 质检报告数据结构
const activeCategories = ref([])
const allCategoriesExpanded = ref(false)

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

const toggleAllCategories = () => {
  if (allCategoriesExpanded.value) {
    activeCategories.value = []
  } else {
    activeCategories.value = ['appearance', 'screen', 'function', 'repair']
  }
  allCategoriesExpanded.value = !allCategoriesExpanded.value
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

// 从API格式加载质检数据
const loadInspectionDataFromAPI = (data) => {
  if (!Array.isArray(data) || data.length === 0) return
  
  try {
    // 外观检测
    const appearance = data.find(cat => cat.title === '外观检测')
    if (appearance && appearance.groups && appearance.groups[0]) {
      const items = appearance.groups[0].items
      if (items) {
        inspectionData.appearance.items.forEach((item, idx) => {
          if (items[idx]) {
            item.value = items[idx].value || item.value
            item.pass = items[idx].pass !== undefined ? items[idx].pass : item.pass
            item.image = items[idx].image || ''
          }
        })
      }
    }

    // 屏幕检测
    const screen = data.find(cat => cat.title === '屏幕检测')
    if (screen && screen.groups) {
      const touchGroup = screen.groups.find(g => g.name === '屏幕触控')
      if (touchGroup && touchGroup.items) {
        inspectionData.screen.touch.forEach((item, idx) => {
          if (touchGroup.items[idx]) {
            item.value = touchGroup.items[idx].value || item.value
            item.pass = touchGroup.items[idx].pass !== undefined ? touchGroup.items[idx].pass : item.pass
            item.image = touchGroup.items[idx].image || ''
          }
        })
      }

      const appearanceGroup = screen.groups.find(g => g.name === '屏幕外观')
      if (appearanceGroup && appearanceGroup.items) {
        inspectionData.screen.appearance.forEach((item, idx) => {
          if (appearanceGroup.items[idx]) {
            item.value = appearanceGroup.items[idx].value || item.value
            item.pass = appearanceGroup.items[idx].pass !== undefined ? appearanceGroup.items[idx].pass : item.pass
            item.image = appearanceGroup.items[idx].image || ''
          }
        })
      }

      const displayGroup = screen.groups.find(g => g.name === '屏幕显示')
      if (displayGroup && displayGroup.items) {
        inspectionData.screen.display.forEach((item, idx) => {
          if (displayGroup.items[idx]) {
            item.value = displayGroup.items[idx].value || item.value
            item.pass = displayGroup.items[idx].pass !== undefined ? displayGroup.items[idx].pass : item.pass
            item.image = displayGroup.items[idx].image || ''
          }
        })
      }
    }

    // 设备功能
    const func = data.find(cat => cat.title === '设备功能')
    if (func && func.groups) {
      Object.keys(inspectionData.function).forEach(key => {
        const group = inspectionData.function[key]
        const apiGroup = func.groups.find(g => g.name === group.name)
        if (apiGroup && apiGroup.items) {
          group.items.forEach((item, idx) => {
            if (apiGroup.items[idx]) {
              item.value = apiGroup.items[idx].value || item.value
              item.pass = apiGroup.items[idx].pass !== undefined ? apiGroup.items[idx].pass : item.pass
              item.image = apiGroup.items[idx].image || ''
            }
          })
        }
      })
    }

    // 维修浸液
    const repair = data.find(cat => cat.title === '维修浸液')
    if (repair && repair.groups && repair.groups[0]) {
      const items = repair.groups[0].items
      if (items) {
        inspectionData.repair.items.forEach((item, idx) => {
          if (items[idx]) {
            item.value = items[idx].value || item.value
            item.pass = items[idx].pass !== undefined ? items[idx].pass : item.pass
            item.image = items[idx].image || ''
          }
        })
      }
    }
  } catch (error) {
    console.error('加载质检数据失败:', error)
  }
}

const rules = {
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  brand: [{ required: true, message: '请输入品牌', trigger: 'blur' }],
  model: [{ required: true, message: '请输入型号', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }],
  cover_image: [{ required: true, message: '请上传封面图', trigger: 'change' }],
  detail_images: [{ type: 'array', required: true, min: 1, message: '请至少上传1张详情图', trigger: 'change' }],
  inspection_result: [{ required: true, message: '请选择质检结果', trigger: 'change' }],
  inspection_date: [{ required: true, message: '请选择质检日期', trigger: 'change' }],
  inspection_staff: [{ required: true, message: '请输入质检员', trigger: 'blur' }],
  stock: [{ required: true, type: 'number', min: 1, message: '库存至少1', trigger: 'change' }],
  location: [{ required: true, message: '请输入所在地', trigger: 'blur' }],
}

// 上传接口：请根据后端实际路径修改。优先取环境变量 VITE_ADMIN_UPLOAD_URL
// 注意 adminApi 已带 baseURL=/admin-api，故这里默认用 /uploads/...，拼起来就是 /admin-api/uploads/...
const uploadEndpoint = import.meta.env.VITE_ADMIN_UPLOAD_URL || '/uploads/images/'

const handleUpload = async (options, type) => {
  const { file, onError, onSuccess } = options
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await adminApi.post(uploadEndpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const url = res.data?.url || res.data?.image || res.data?.path
    if (!url) throw new Error('上传返回空URL')
    if (type === 'cover') {
      form.cover_image = url
      coverFileList.value = [{ name: file.name, url }]
    } else if (type === 'detail') {
      form.detail_images.push(url)
      detailFileList.value.push({ name: file.name, url })
    }
    onSuccess(res.data)
  } catch (err) {
    ElMessage.error('上传失败')
    onError(err)
  }
}

const handleDetailRemove = (file) => {
  form.detail_images = form.detail_images.filter((u) => u !== file.url)
  detailFileList.value = detailFileList.value.filter((f) => f.url !== file.url)
}

const handlePreview = (file) => {
  const allImages = [
    ...coverFileList.value.map((f) => f.url),
    ...detailFileList.value.map((f) => f.url),
  ].filter(Boolean)
  const idx = allImages.findIndex((u) => u === file.url)
  if (allImages.length === 0) return
  previewImages.value = allImages
  previewIndex.value = idx >= 0 ? idx : 0
  previewVisible.value = true
}

const normalizeToUrl = (url) => (url ? getImageUrl(url) || url : '')

const fillForm = (data = {}) => {
  form.title = data.title || ''
  form.brand = data.brand || ''
  form.model = data.model || ''
  form.storage = data.storage || ''
  form.ram = data.ram || ''
  form.version = data.version || ''
  form.repair_status = data.repair_status || ''
  form.condition = data.condition || 'good'
  form.price = Number(data.price || 0)
  form.original_price = Number(data.original_price || 0)
  form.stock = Number(data.stock || 1)
  form.location = data.location || ''
  form.description = data.description || ''
  form.tags = data.tags || []
  form.cover_image = data.cover_image || ''
  form.detail_images = data.detail_images || []
  form.inspection_result = data.inspection_result || 'pass'
  form.inspection_date = data.inspection_date || ''
  form.inspection_staff = data.inspection_staff || ''
  form.inspection_note = data.inspection_note || ''
  form.category = data.category || ''
  form.category_id = (data.category && data.category.id) || data.category_id || null
  form.status = data.status || 'draft'

  // inspection_reports 字段用于存储详细质检数据
  form.inspection_reports = data.inspection_reports || []

  coverFileList.value = form.cover_image
    ? [{ name: 'cover', url: normalizeToUrl(form.cover_image) }]
    : []
  detailFileList.value = (form.detail_images || []).map((u, idx) => ({
    name: `detail-${idx + 1}`,
    url: normalizeToUrl(u)
  }))

  // 加载详细质检数据
  if (data.inspection_reports && Array.isArray(data.inspection_reports) && data.inspection_reports.length > 0) {
    // 检查是否是新格式的质检数据（包含 title, groups 等）
    if (data.inspection_reports[0] && typeof data.inspection_reports[0] === 'object' && data.inspection_reports[0].title) {
      loadInspectionDataFromAPI(data.inspection_reports)
    }
  }
}

watch(
  () => props.product,
  (val) => {
    if (val) fillForm(val)
  },
  { immediate: true, deep: true }
)

const submit = async (publishNow = false) => {
  try {
    await formRef.value.validate()
    saving.value = true
    // 组装 payload，去掉只读/无用字段
    const {
      category,
      tags,
      detail_images,
      ...rest
    } = form
    const payload = {
      ...rest,
      price: Number(rest.price || 0),
      original_price: Number(rest.original_price || 0),
      stock: Number(rest.stock || 1),
      detail_images: Array.isArray(detail_images) ? [...detail_images] : [],
      inspection_reports: convertInspectionDataToAPI() // 存储详细质检数据
    }
    // 日期格式化
    if (rest.inspection_date) {
      const d = rest.inspection_date
      const dateStr = d instanceof Date
        ? `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
        : rest.inspection_date
      payload.inspection_date = dateStr
    }
    if (Array.isArray(tags)) {
      payload.tags = [...tags]
    }
    // 处理分类：优先 category_id，没有则尝试 category（若是数字字符串）
    if (form.category_id) {
      payload.category_id = form.category_id
    } else if (form.category && !isNaN(Number(form.category))) {
      payload.category_id = Number(form.category)
    }
    let id = props.product?.id
    if (isEdit.value) {
      await adminApi.put(`/verified-listings/${id}/`, payload)
    } else {
      const res = await adminApi.post('/verified-listings/', payload)
      id = res.data?.id
    }
    if (publishNow && id) {
      await adminApi.post(`/verified-listings/${id}/publish/`)
      ElMessage.success('已发布')
    } else {
      ElMessage.success(isEdit.value ? '保存成功' : '创建成功')
    }
    emit(isEdit.value ? 'updated' : 'created')
  } catch (error) {
    if (error !== false) {
      ElMessage.error('提交失败')
    }
  } finally {
    saving.value = false
  }
}

const unpublish = async () => {
  if (!props.product?.id) return
  try {
    saving.value = true
    await adminApi.post(`/verified-listings/${props.product.id}/unpublish`)
    ElMessage.success('已下架')
    emit('updated')
  } catch (error) {
    ElMessage.error('下架失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.verified-product-form {
  padding: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 16px;
}

.card-block {
  width: 100%;
}

.actions {
  text-align: right;
  margin-top: 20px;
}

.upload-cover :deep(.el-upload) {
  width: 120px;
  height: 120px;
}

.upload-detail :deep(.el-upload) {
  width: 120px;
  height: 120px;
}

.upload-report :deep(.el-upload-list__item) {
  width: 240px;
}

.full-width {
  grid-column: 1 / -1;
}

.inspection-editor {
  padding: 10px 0;
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
</style>













