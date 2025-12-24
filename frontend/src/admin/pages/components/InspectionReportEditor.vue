<template>
  <div class="inspection-editor">
    <div style="display:flex; justify-content: space-between; align-items:center; margin-bottom: 8px;">
      <el-button size="small" @click="toggleAllCategories">
        {{ allCategoriesExpanded ? '全部收起' : '全部展开' }}
      </el-button>
      <el-tag size="small" type="info">按回收质检表结构编辑</el-tag>
    </div>

    <el-collapse v-model="activeCategories">
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
                <el-input v-model="item.image" placeholder="异常图片URL" size="small" style="width: 220px;" />
                <el-upload :show-file-list="false" accept="image/*" :http-request="(opt) => handleInspectionImageUpload(opt, item)">
                  <el-button size="small">上传</el-button>
                </el-upload>
                <el-image
                  v-if="item.image"
                  class="item-image-thumb"
                  :src="normalizeToUrl(item.image)"
                  fit="cover"
                  :preview-src-list="[normalizeToUrl(item.image)]"
                  preview-teleported
                />
              </div>
            </div>
          </div>
        </div>
      </el-collapse-item>

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
                <el-input v-model="item.image" placeholder="异常图片URL" size="small" style="width: 220px;" />
                <el-upload :show-file-list="false" accept="image/*" :http-request="(opt) => handleInspectionImageUpload(opt, item)">
                  <el-button size="small">上传</el-button>
                </el-upload>
                <el-image
                  v-if="item.image"
                  class="item-image-thumb"
                  :src="normalizeToUrl(item.image)"
                  fit="cover"
                  :preview-src-list="[normalizeToUrl(item.image)]"
                  preview-teleported
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
                <el-input v-model="item.image" placeholder="异常图片URL" size="small" style="width: 220px;" />
                <el-upload :show-file-list="false" accept="image/*" :http-request="(opt) => handleInspectionImageUpload(opt, item)">
                  <el-button size="small">上传</el-button>
                </el-upload>
                <el-image
                  v-if="item.image"
                  class="item-image-thumb"
                  :src="normalizeToUrl(item.image)"
                  fit="cover"
                  :preview-src-list="[normalizeToUrl(item.image)]"
                  preview-teleported
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
                <el-input v-model="item.image" placeholder="异常图片URL" size="small" style="width: 220px;" />
                <el-upload :show-file-list="false" accept="image/*" :http-request="(opt) => handleInspectionImageUpload(opt, item)">
                  <el-button size="small">上传</el-button>
                </el-upload>
                <el-image
                  v-if="item.image"
                  class="item-image-thumb"
                  :src="normalizeToUrl(item.image)"
                  fit="cover"
                  :preview-src-list="[normalizeToUrl(item.image)]"
                  preview-teleported
                />
              </div>
            </div>
          </div>
        </div>
      </el-collapse-item>

      <el-collapse-item name="function" title="设备功能（27项）">
        <div class="inspection-group" v-for="(group, groupKey) in inspectionData.function" :key="groupKey">
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
                <el-input v-model="item.image" placeholder="异常图片URL" size="small" style="width: 220px;" />
                <el-upload :show-file-list="false" accept="image/*" :http-request="(opt) => handleInspectionImageUpload(opt, item)">
                  <el-button size="small">上传</el-button>
                </el-upload>
                <el-image
                  v-if="item.image"
                  class="item-image-thumb"
                  :src="normalizeToUrl(item.image)"
                  fit="cover"
                  :preview-src-list="[normalizeToUrl(item.image)]"
                  preview-teleported
                />
              </div>
            </div>
          </div>
        </div>
      </el-collapse-item>

      <el-collapse-item name="repair" title="维修浸液（8项）">
        <div class="inspection-group">
          <div class="group-title">维修/浸液</div>
          <div class="inspection-items">
            <div v-for="(item, idx) in inspectionData.repair.items" :key="idx" class="inspection-item">
              <span class="item-label">{{ item.label }}</span>
              <el-input v-model="item.value" placeholder="检测结果" size="small" style="width: 150px;" />
              <el-select v-model="item.pass" size="small" style="width: 100px;">
                <el-option label="正常" :value="true" />
                <el-option label="异常" :value="false" />
              </el-select>
              <div v-if="!item.pass" class="item-image">
                <el-input v-model="item.image" placeholder="异常图片URL" size="small" style="width: 220px;" />
                <el-upload :show-file-list="false" accept="image/*" :http-request="(opt) => handleInspectionImageUpload(opt, item)">
                  <el-button size="small">上传</el-button>
                </el-upload>
                <el-image
                  v-if="item.image"
                  class="item-image-thumb"
                  :src="normalizeToUrl(item.image)"
                  fit="cover"
                  :preview-src-list="[normalizeToUrl(item.image)]"
                  preview-teleported
                />
              </div>
            </div>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'
import { getImageUrl } from '@/utils/image'

const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  }
})

const uploadEndpoint = import.meta.env.VITE_ADMIN_UPLOAD_URL || '/uploads/images/'
const normalizeToUrl = (url) => (url ? (getImageUrl(url) || url) : '')

const activeCategories = ref([])
const allCategoriesExpanded = ref(false)
const extraCategories = ref([])

const inspectionData = reactive({
  appearance: {
    items: [
      { label: '碎裂', value: '无', pass: true, image: '' },
      { label: '划痕', value: '无', pass: true, image: '' },
      { label: '机身弯曲', value: '无', pass: true, image: '' },
      { label: '脱胶/缝隙', value: '无', pass: true, image: '' },
      { label: '外壳/其他', value: '正常', pass: true, image: '' },
      { label: '磕碰', value: '几乎不可见', pass: true, image: '' },
      { label: '刻字/印', value: '无', pass: true, image: '' },
      { label: '掉漆/磨损', value: '几乎不可见', pass: true, image: '' },
      { label: '摄像头闪光灯外观', value: '正常', pass: true, image: '' },
      { label: '褶皱', value: '无', pass: true, image: '' },
      { label: '卡托', value: '正常', pass: true, image: '' },
      { label: '音频网罩', value: '正常', pass: true, image: '' }
    ]
  },
  screen: {
    touch: [{ label: '触控', value: '正常', pass: true, image: '' }],
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
        { label: '听筒', value: '正常', pass: true, image: '' },
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
      name: '其他',
      items: [
        { label: '陀螺仪', value: '正常', pass: true, image: '' },
        { label: '指南针校准', value: '正常', pass: true, image: '' },
        { label: '屏幕自动旋转', value: '正常', pass: true, image: '' }
      ]
    }
  },
  repair: {
    items: [
      { label: '维修', value: '无', pass: true, image: '' },
      { label: '浸液', value: '无', pass: true, image: '' },
      { label: '拆修', value: '无', pass: true, image: '' },
      { label: '改装', value: '无', pass: true, image: '' },
      { label: '异常', value: '无', pass: true, image: '' },
      { label: '更换屏幕', value: '无', pass: true, image: '' },
      { label: '更换电池', value: '无', pass: true, image: '' },
      { label: '更换主板', value: '无', pass: true, image: '' }
    ]
  }
})

const toggleAllCategories = () => {
  allCategoriesExpanded.value = !allCategoriesExpanded.value
  activeCategories.value = allCategoriesExpanded.value
    ? ['appearance', 'screen', 'function', 'repair']
    : []
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

const convertInspectionDataToAPI = () => {
  const main = [
    {
      title: '外观检测',
      groups: [
        {
          name: '外壳外观',
          items: inspectionData.appearance.items.map(item => ({
            label: item.label,
            value: item.value,
            pass: item.pass,
            ...(item.image ? { image: item.image } : {})
          }))
        }
      ]
    },
    {
      title: '屏幕检测',
      groups: [
        {
          name: '屏幕触控',
          items: inspectionData.screen.touch.map(item => ({
            label: item.label,
            value: item.value,
            pass: item.pass,
            ...(item.image ? { image: item.image } : {})
          }))
        },
        {
          name: '屏幕外观',
          items: inspectionData.screen.appearance.map(item => ({
            label: item.label,
            value: item.value,
            pass: item.pass,
            ...(item.image ? { image: item.image } : {})
          }))
        },
        {
          name: '屏幕显示',
          items: inspectionData.screen.display.map(item => ({
            label: item.label,
            value: item.value,
            pass: item.pass,
            ...(item.image ? { image: item.image } : {})
          }))
        }
      ]
    },
    {
      title: '设备功能',
      groups: Object.values(inspectionData.function).map(group => ({
        name: group.name,
        items: group.items.map(item => ({
          label: item.label,
          value: item.value,
          pass: item.pass,
          ...(item.image ? { image: item.image } : {})
        }))
      }))
    },
    {
      title: '维修浸液',
      groups: [
        {
          name: '维修/浸液',
          items: inspectionData.repair.items.map(item => ({
            label: item.label,
            value: item.value,
            pass: item.pass,
            ...(item.image ? { image: item.image } : {})
          }))
        }
      ]
    }
  ]

  return [...main, ...(extraCategories.value || [])]
}

const loadInspectionDataFromAPI = (categories) => {
  if (!Array.isArray(categories) || categories.length === 0) {
    extraCategories.value = []
    return
  }
  const byTitle = (title) => categories.find(cat => cat && cat.title === title)

  const appearance = byTitle('外观检测')
  const screen = byTitle('屏幕检测')
  const functionCat = byTitle('设备功能')
  const repair = byTitle('维修浸液')

  const knownTitles = new Set([appearance?.title, screen?.title, functionCat?.title, repair?.title].filter(Boolean))
  extraCategories.value = categories.filter(cat => cat && !knownTitles.has(cat.title))

  if (appearance?.groups?.[0]?.items) {
    inspectionData.appearance.items.forEach((item, idx) => {
      const src = appearance.groups[0].items[idx]
      if (!src) return
      item.value = src.value ?? item.value
      item.pass = typeof src.pass === 'boolean' ? src.pass : item.pass
      item.image = src.image || item.image || ''
    })
  }
  if (screen?.groups?.length) {
    const touch = screen.groups.find(g => g.name === '屏幕触控')
    const appearanceGroup = screen.groups.find(g => g.name === '屏幕外观')
    const display = screen.groups.find(g => g.name === '屏幕显示')
    if (touch?.items) {
      inspectionData.screen.touch.forEach((item, idx) => {
        const src = touch.items[idx]
        if (!src) return
        item.value = src.value ?? item.value
        item.pass = typeof src.pass === 'boolean' ? src.pass : item.pass
        item.image = src.image || item.image || ''
      })
    }
    if (appearanceGroup?.items) {
      inspectionData.screen.appearance.forEach((item, idx) => {
        const src = appearanceGroup.items[idx]
        if (!src) return
        item.value = src.value ?? item.value
        item.pass = typeof src.pass === 'boolean' ? src.pass : item.pass
        item.image = src.image || item.image || ''
      })
    }
    if (display?.items) {
      inspectionData.screen.display.forEach((item, idx) => {
        const src = display.items[idx]
        if (!src) return
        item.value = src.value ?? item.value
        item.pass = typeof src.pass === 'boolean' ? src.pass : item.pass
        item.image = src.image || item.image || ''
      })
    }
  }
  if (functionCat?.groups?.length) {
    const groupMap = Object.fromEntries(functionCat.groups.map(g => [g.name, g]))
    Object.keys(inspectionData.function).forEach(key => {
      const group = inspectionData.function[key]
      const srcGroup = groupMap[group.name]
      if (!srcGroup?.items) return
      group.items.forEach((item, idx) => {
        const src = srcGroup.items[idx]
        if (!src) return
        item.value = src.value ?? item.value
        item.pass = typeof src.pass === 'boolean' ? src.pass : item.pass
        item.image = src.image || item.image || ''
      })
    })
  }
  if (repair?.groups?.[0]?.items) {
    inspectionData.repair.items.forEach((item, idx) => {
      const src = repair.groups[0].items[idx]
      if (!src) return
      item.value = src.value ?? item.value
      item.pass = typeof src.pass === 'boolean' ? src.pass : item.pass
      item.image = src.image || item.image || ''
    })
  }
}

watch(
  () => props.categories,
  (val) => loadInspectionDataFromAPI(val),
  { immediate: true, deep: true }
)

const getCategories = () => convertInspectionDataToAPI()
const setCategories = (categories) => loadInspectionDataFromAPI(categories)

defineExpose({ getCategories, setCategories })
</script>

<style scoped>
.inspection-group {
  padding: 12px 8px;
}
.group-title {
  font-weight: 600;
  margin: 8px 0 10px;
}
.inspection-item {
  padding: 8px 0;
  border-bottom: 1px dashed #f0f0f0;
  display: flex;
  gap: 10px;
  align-items: flex-start;
  flex-wrap: wrap;
}
.item-label {
  width: 110px;
  flex: 0 0 110px;
  color: #333;
}
.item-image {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.item-image-thumb {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid #eee;
}
</style>
