<template>
  <div class="recycle-templates admin-page">
    <div class="page-header">
      <div>
        <div class="page-title">回收机型模板管理</div>
        <div class="page-desc">管理可回收的机型、品牌、问卷内容等</div>
      </div>
      <el-space>
        <el-button :loading="loading" text :icon="Refresh" @click="handleRefresh">刷新</el-button>
        <el-button
          v-if="hasPerm('recycle_template:view')"
          type="info"
          :icon="Download"
          @click="handleDownloadTemplate"
        >
          下载模板
        </el-button>
        <el-button
          v-if="hasPerm('recycle_template:view')"
          type="warning"
          :icon="Download"
          @click="handleExportFullTemplate"
        >
          导出完整模板
        </el-button>
        <el-button
          v-if="hasPerm('recycle_template:create')"
          type="success"
          :icon="Upload"
          @click="handleUploadImport"
          :loading="importing"
        >
          上传导入
        </el-button>
        <el-button v-if="hasPerm('recycle_template:create')" type="primary" :icon="Plus" @click="handleCreate">
          新增模板
        </el-button>
      </el-space>
    </div>

    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" class="filter-form" @submit.prevent>
        <el-form-item label="设备类型">
          <el-select v-model="filters.device_type" placeholder="全部" clearable style="width: 160px" @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="手机" value="手机" />
            <el-option label="平板" value="平板" />
            <el-option label="笔记本" value="笔记本" />
          </el-select>
        </el-form-item>
        <el-form-item label="品牌">
          <el-input
            v-model="filters.brand"
            placeholder="搜索品牌"
            clearable
            style="width: 160px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="filters.search"
            placeholder="搜索机型/型号"
            clearable
            style="width: 260px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <el-table :data="items" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="device_type" label="设备类型" width="100" />
        <el-table-column prop="brand" label="品牌" width="120" />
        <el-table-column prop="model" label="型号" min-width="200" />
        <el-table-column prop="series" label="系列" width="120" />
        <el-table-column label="存储容量" width="150">
          <template #default="{ row }">
            <el-tag v-for="s in row.storages" :key="s" size="small" style="margin-right: 4px">{{ s }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="问卷数量" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.question_count || 0 }} 题</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_username" label="创建人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-space wrap>
              <el-button size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button size="small" type="primary" @click="handleManageQuestions(row)">管理问卷</el-button>
              <el-button
                v-if="hasPerm('recycle_template:delete')"
                size="small"
                type="danger"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.current"
          :total="pagination.total"
          :page-size="pagination.pageSize"
          layout="prev, pager, next, total, sizes"
          :page-sizes="[10, 20, 50, 100]"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑机型模板' : '新增机型模板'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="form" label-width="120px" :rules="formRules" ref="formRef">
        <el-form-item label="设备类型" prop="device_type">
          <el-select v-model="form.device_type" placeholder="请选择设备类型" style="width: 100%">
            <el-option label="手机" value="手机" />
            <el-option label="平板" value="平板" />
            <el-option label="笔记本" value="笔记本" />
          </el-select>
        </el-form-item>
        <el-form-item label="品牌" prop="brand">
          <el-input v-model="form.brand" placeholder="请输入品牌" />
        </el-form-item>
        <el-form-item label="型号" prop="model">
          <el-input v-model="form.model" placeholder="请输入型号" />
        </el-form-item>
        <el-form-item label="系列">
          <el-input v-model="form.series" placeholder="请输入系列（可选）" />
        </el-form-item>
        <el-form-item label="存储容量">
          <el-select
            v-model="form.storages"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入存储容量"
            style="width: 100%"
          >
            <el-option label="128GB" value="128GB" />
            <el-option label="256GB" value="256GB" />
            <el-option label="512GB" value="512GB" />
            <el-option label="1TB" value="1TB" />
          </el-select>
          <div class="form-hint">可多选，也可以输入自定义容量</div>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 问卷管理对话框 -->
    <el-dialog
      v-model="questionDialogVisible"
      :title="`管理问卷 - ${currentTemplate?.brand} ${currentTemplate?.model}`"
      width="900px"
      @close="handleQuestionDialogClose"
    >
      <div v-if="currentTemplate">
        <div style="margin-bottom: 16px">
          <el-button type="primary" :icon="Plus" @click="handleAddQuestion">新增问题</el-button>
        </div>

        <el-table :data="questions" style="width: 100%">
          <el-table-column prop="step_order" label="顺序" width="80" />
          <el-table-column prop="key" label="标识" width="120" />
          <el-table-column prop="title" label="问题标题" min-width="200" />
          <el-table-column prop="question_type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="row.question_type === 'multi' ? 'warning' : 'primary'">
                {{ row.question_type === 'multi' ? '多选' : '单选' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="选项数量" width="100">
            <template #default="{ row }">
              <el-tag>{{ row.options?.length || 0 }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <el-space wrap>
                <el-button size="small" @click="handleEditQuestion(row)">编辑</el-button>
                <el-button size="small" type="primary" @click="handleManageOptions(row)">管理选项</el-button>
                <el-button size="small" type="danger" @click="handleDeleteQuestion(row)">删除</el-button>
              </el-space>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 问题编辑对话框 -->
    <el-dialog
      v-model="questionFormVisible"
      :title="isEditQuestion ? '编辑问题' : '新增问题'"
      width="700px"
      @close="handleQuestionFormClose"
    >
      <el-form :model="questionForm" label-width="120px" :rules="questionFormRules" ref="questionFormRef">
        <el-form-item label="步骤顺序" prop="step_order">
          <el-input-number v-model="questionForm.step_order" :min="1" :max="50" />
          <div class="form-hint">
            <strong>用途：</strong>控制问题在问卷中的显示顺序，从1开始依次递增
            <div style="margin-top: 4px;"><strong>示例：</strong>1（第一步）、2（第二步）... 13（最后一步）</div>
          </div>
        </el-form-item>
        <el-form-item label="问题标识" prop="key">
          <el-input v-model="questionForm.key" placeholder="如：channel, color, storage" />
          <div class="form-hint">
            <div><strong>用途：</strong>系统内部识别问题的唯一代码，用于程序处理和数据分析</div>
            <div><strong>填写规范：</strong>使用英文小写字母，多个单词用下划线连接（如：purchase_channel）</div>
            <div><strong>示例：</strong>channel（购买渠道）、color（颜色）、storage（存储容量）</div>
            <div style="color: #f56c6c; margin-top: 4px;"><strong>注意：</strong>同一机型模板内，问题标识不能重复</div>
          </div>
        </el-form-item>
        <el-form-item label="问题标题" prop="title">
          <el-input v-model="questionForm.title" placeholder="请输入问题标题" />
        </el-form-item>
        <el-form-item label="提示文本">
          <el-input v-model="questionForm.helper" placeholder="请输入提示文本（可选）" />
        </el-form-item>
        <el-form-item label="问题类型" prop="question_type">
          <el-radio-group v-model="questionForm.question_type">
            <el-radio label="single">单选</el-radio>
            <el-radio label="multi">多选</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="是否必填">
          <el-switch v-model="questionForm.is_required" active-text="必填" inactive-text="选填" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="questionForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="questionFormVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingQuestion" @click="handleSaveQuestion">保存</el-button>
      </template>
    </el-dialog>

    <!-- 选项管理对话框 -->
    <el-dialog
      v-model="optionDialogVisible"
      :title="`管理选项 - ${currentQuestion?.title}`"
      width="800px"
      @close="handleOptionDialogClose"
    >
      <div v-if="currentQuestion">
        <div style="margin-bottom: 16px">
          <el-button type="primary" :icon="Plus" @click="handleAddOption">新增选项</el-button>
        </div>

        <el-table :data="options" style="width: 100%">
          <el-table-column prop="option_order" label="顺序" width="80" />
          <el-table-column prop="value" label="选项值" width="150" />
          <el-table-column prop="label" label="选项标签" min-width="150" />
          <el-table-column prop="desc" label="描述" min-width="150" />
          <el-table-column prop="impact" label="影响" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.impact" :type="getImpactType(row.impact)">{{ getImpactLabel(row.impact) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-space wrap>
                <el-button size="small" @click="handleEditOption(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteOption(row)">删除</el-button>
              </el-space>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 选项编辑对话框 -->
    <el-dialog
      v-model="optionFormVisible"
      :title="isEditOption ? '编辑选项' : '新增选项'"
      width="600px"
      @close="handleOptionFormClose"
    >
      <el-form :model="optionForm" label-width="120px" :rules="optionFormRules" ref="optionFormRef">
        <el-form-item label="选项顺序" prop="option_order">
          <el-input-number v-model="optionForm.option_order" :min="0" />
        </el-form-item>
        <el-form-item label="选项值" prop="value">
          <el-input v-model="optionForm.value" placeholder="如：official, black, 256GB" />
          <div class="form-hint">
            <div><strong>用途：</strong>系统内部识别选项的唯一代码，用于程序处理和存储用户选择</div>
            <div><strong>填写规范：</strong>使用英文小写字母、数字，多个单词用下划线或连字符连接</div>
            <div><strong>示例：</strong></div>
            <div style="margin-left: 16px;">
              • 购买渠道：official（官方/直营）、operator（运营商/合约）<br/>
              • 颜色：black（黑/深色）、white（白/浅色）<br/>
              • 存储：256GB、512GB（直接使用容量值）
            </div>
            <div style="color: #f56c6c; margin-top: 4px;"><strong>注意：</strong>同一问题内，选项值不能重复</div>
          </div>
        </el-form-item>
        <el-form-item label="选项标签" prop="label">
          <el-input v-model="optionForm.label" placeholder="显示给用户的文本" />
          <div class="form-hint">
            <strong>用途：</strong>显示给用户看的选项文本，用户友好、清晰易懂即可
            <div style="margin-top: 4px;"><strong>示例：</strong>"官方/直营"、"黑/深色"、"256GB"</div>
          </div>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="optionForm.desc" placeholder="辅助说明文本（可选）" />
          <div class="form-hint">
            <strong>用途：</strong>对选项的补充说明，帮助用户更好地理解选项含义（可选）
            <div style="margin-top: 4px;"><strong>示例：</strong>"官网/直营店"、"几乎全新，使用很少"</div>
          </div>
        </el-form-item>
        <el-form-item label="对估价的影响">
          <el-select v-model="optionForm.impact" placeholder="选择影响类型" clearable style="width: 100%">
            <el-option label="正面影响" value="positive" />
            <el-option label="轻微影响" value="minor" />
            <el-option label="重大影响" value="major" />
            <el-option label="严重影响" value="critical" />
          </el-select>
          <div class="form-hint">
            <strong>用途：</strong>该选项对回收估价的影响程度，用于价格计算（可选）
            <div style="margin-top: 4px;">
              • <strong>正面影响：</strong>提升价格（如：全新未拆封、配件齐全）<br/>
              • <strong>轻微影响：</strong>略微影响价格（如：正常使用痕迹）<br/>
              • <strong>重大影响：</strong>显著降低价格（如：明显划痕、已维修）<br/>
              • <strong>严重影响：</strong>大幅降低价格（如：碎裂、无法使用）
            </div>
          </div>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="optionForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="optionFormVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingOption" @click="handleSaveOption">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 隐藏的文件上传输入 -->
    <input
      ref="uploadFileRef"
      type="file"
      accept=".xlsx,.xls,.csv"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Search, Upload, Download } from '@element-plus/icons-vue'
import adminApi from '@/utils/adminApi'
import { useAdminAuthStore } from '@/stores/adminAuth'

const admin = useAdminAuthStore()
const hasPerm = (p) => admin.hasPerm(p)

// 数据
const items = ref([])
const loading = ref(false)
const saving = ref(false)
const savingQuestion = ref(false)
const savingOption = ref(false)
const importing = ref(false)
const uploadFileRef = ref(null)

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
})

// 筛选
const filters = reactive({
  device_type: '',
  brand: '',
  search: '',
})

// 对话框
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const formRef = ref(null)

// 表单
const form = reactive({
  device_type: '',
  brand: '',
  model: '',
  series: '',
  storages: [],
  is_active: true,
})

const formRules = {
  device_type: [{ required: true, message: '请选择设备类型', trigger: 'change' }],
  brand: [{ required: true, message: '请输入品牌', trigger: 'blur' }],
  model: [{ required: true, message: '请输入型号', trigger: 'blur' }],
}

// 问卷管理
const questionDialogVisible = ref(false)
const currentTemplate = ref(null)
const questions = ref([])

// 问题表单
const questionFormVisible = ref(false)
const isEditQuestion = ref(false)
const currentQuestionId = ref(null)
const questionFormRef = ref(null)
const questionForm = reactive({
  step_order: 1,
  key: '',
  title: '',
  helper: '',
  question_type: 'single',
  is_required: true,
  is_active: true,
})

const questionFormRules = {
  step_order: [{ required: true, message: '请输入步骤顺序', trigger: 'blur' }],
  key: [{ required: true, message: '请输入问题标识', trigger: 'blur' }],
  title: [{ required: true, message: '请输入问题标题', trigger: 'blur' }],
  question_type: [{ required: true, message: '请选择问题类型', trigger: 'change' }],
}

// 选项管理
const optionDialogVisible = ref(false)
const currentQuestion = ref(null)
const options = ref([])

// 选项表单
const optionFormVisible = ref(false)
const isEditOption = ref(false)
const currentOptionId = ref(null)
const optionFormRef = ref(null)
const optionForm = reactive({
  option_order: 0,
  value: '',
  label: '',
  desc: '',
  impact: '',
  is_active: true,
})

const optionFormRules = {
  value: [{ required: true, message: '请输入选项值', trigger: 'blur' }],
  label: [{ required: true, message: '请输入选项标签', trigger: 'blur' }],
}

// 加载列表
const load = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
    }
    if (filters.device_type) params.device_type = filters.device_type
    if (filters.brand) params.brand = filters.brand
    if (filters.search) params.search = filters.search

    const res = await adminApi.get('/recycle-templates', { params })
    items.value = res.data.results || []
    pagination.total = res.data.count || 0
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

// 刷新
const handleRefresh = () => {
  load()
}

// 下载模板文件（空模板）
const handleDownloadTemplate = async () => {
  try {
    const response = await adminApi.get('/recycle-templates/download-template', {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // 从响应头获取文件名，如果没有则使用默认名称
    const contentDisposition = response.headers['content-disposition']
    let filename = '机型模板导入文件.xlsx'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = decodeURIComponent(filenameMatch[1].replace(/['"]/g, ''))
      }
    }
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('模板文件下载成功')
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '下载模板失败')
  }
}

// 导出完整模板（包含现有机型和问卷配置）
const handleExportFullTemplate = async () => {
  try {
    const response = await adminApi.get('/recycle-templates/download-template?export_existing=true', {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // 从响应头获取文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = '机型模板完整导出.xlsx'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = decodeURIComponent(filenameMatch[1].replace(/['"]/g, ''))
      }
    }
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('完整模板导出成功，包含所有现有机型和问卷配置')
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '导出完整模板失败')
  }
}

// 上传文件并导入
const handleUploadImport = () => {
  uploadFileRef.value?.click()
}

// 处理文件选择
const handleFileChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  // 验证文件类型
  const fileName = file.name.toLowerCase()
  if (!fileName.endsWith('.xlsx') && !fileName.endsWith('.xls') && !fileName.endsWith('.csv')) {
    ElMessage.error('请上传Excel(.xlsx/.xls)或CSV文件')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要导入文件 "${file.name}" 吗？导入时会自动为每个机型创建默认13步问卷。`,
      '确认导入',
      {
        type: 'warning',
        confirmButtonText: '确认导入',
        cancelButtonText: '取消',
      }
    )
    
    importing.value = true
    
    const formData = new FormData()
    formData.append('file', file)
    formData.append('clear', false)  // 不清空现有数据
    
    try {
      const res = await adminApi.post('/recycle-templates/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      const stats = res.data.statistics || {}
      let message = `导入成功！`
      if (stats.templates) {
        message += ` 新增模板: ${stats.templates} 个`
      }
      if (stats.total_devices) {
        message += `，共处理: ${stats.total_devices} 个机型`
      }
      if (res.data.error_count > 0) {
        message += `，${res.data.error_count} 个机型导入失败`
      }
      
      ElMessage.success(message)
      
      if (res.data.errors && res.data.errors.length > 0) {
        console.error('导入错误详情:', res.data.errors)
      }
      
      load()  // 重新加载列表
    } catch (error) {
      ElMessage.error(error?.response?.data?.detail || '导入失败')
    } finally {
      importing.value = false
      // 清空文件选择，以便可以重复选择同一文件
      if (event.target) {
        event.target.value = ''
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('导入失败')
    }
    // 清空文件选择
    if (event.target) {
      event.target.value = ''
    }
  }
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  load()
}

// 重置
const handleReset = () => {
  filters.device_type = ''
  filters.brand = ''
  filters.search = ''
  handleSearch()
}

// 分页
const handlePageChange = (page) => {
  pagination.current = page
  load()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.current = 1
  load()
}

// 创建
const handleCreate = () => {
  isEdit.value = false
  currentId.value = null
  Object.assign(form, {
    device_type: '',
    brand: '',
    model: '',
    series: '',
    storages: [],
    is_active: true,
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form, {
    device_type: row.device_type,
    brand: row.brand,
    model: row.model,
    series: row.series || '',
    storages: row.storages || [],
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

// 保存
const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      if (isEdit.value) {
        await adminApi.put(`/recycle-templates/${currentId.value}`, form)
        ElMessage.success('更新成功')
      } else {
        await adminApi.post('/recycle-templates', form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      load()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除机型模板 "${row.brand} ${row.model}" 吗？`, '确认删除', {
      type: 'warning',
    })
    await adminApi.delete(`/recycle-templates/${row.id}`)
    ElMessage.success('删除成功')
    load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 对话框关闭
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 管理问卷
const handleManageQuestions = async (row) => {
  currentTemplate.value = row
  try {
    const res = await adminApi.get(`/recycle-templates/${row.id}/questions`)
    questions.value = res.data.results || []
    questionDialogVisible.value = true
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载问卷失败')
  }
}

// 新增问题
const handleAddQuestion = () => {
  isEditQuestion.value = false
  currentQuestionId.value = null
  Object.assign(questionForm, {
    step_order: questions.value.length + 1,
    key: '',
    title: '',
    helper: '',
    question_type: 'single',
    is_required: true,
    is_active: true,
  })
  questionFormVisible.value = true
}

// 编辑问题
const handleEditQuestion = (row) => {
  isEditQuestion.value = true
  currentQuestionId.value = row.id
  Object.assign(questionForm, {
    step_order: row.step_order,
    key: row.key,
    title: row.title,
    helper: row.helper || '',
    question_type: row.question_type,
    is_required: row.is_required,
    is_active: row.is_active,
  })
  questionFormVisible.value = true
}

// 保存问题
const handleSaveQuestion = async () => {
  if (!questionFormRef.value) return
  await questionFormRef.value.validate(async (valid) => {
    if (!valid) return
    savingQuestion.value = true
    try {
      if (isEditQuestion.value) {
        await adminApi.put(`/recycle-templates/${currentTemplate.value.id}/questions/${currentQuestionId.value}`, questionForm)
        ElMessage.success('更新成功')
      } else {
        await adminApi.post(`/recycle-templates/${currentTemplate.value.id}/questions`, questionForm)
        ElMessage.success('创建成功')
      }
      questionFormVisible.value = false
      handleManageQuestions(currentTemplate.value)
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      savingQuestion.value = false
    }
  })
}

// 删除问题
const handleDeleteQuestion = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除问题 "${row.title}" 吗？`, '确认删除', {
      type: 'warning',
    })
    await adminApi.delete(`/recycle-templates/${currentTemplate.value.id}/questions/${row.id}`)
    ElMessage.success('删除成功')
    handleManageQuestions(currentTemplate.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 问卷对话框关闭
const handleQuestionDialogClose = () => {
  currentTemplate.value = null
  questions.value = []
}

// 问题表单关闭
const handleQuestionFormClose = () => {
  questionFormRef.value?.resetFields()
}

// 管理选项
const handleManageOptions = async (row) => {
  currentQuestion.value = row
  try {
    const res = await adminApi.get(`/recycle-templates/${currentTemplate.value.id}/questions/${row.id}/options`)
    options.value = res.data.results || []
    optionDialogVisible.value = true
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载选项失败')
  }
}

// 新增选项
const handleAddOption = () => {
  isEditOption.value = false
  currentOptionId.value = null
  Object.assign(optionForm, {
    option_order: options.value.length,
    value: '',
    label: '',
    desc: '',
    impact: '',
    is_active: true,
  })
  optionFormVisible.value = true
}

// 编辑选项
const handleEditOption = (row) => {
  isEditOption.value = true
  currentOptionId.value = row.id
  Object.assign(optionForm, {
    option_order: row.option_order,
    value: row.value,
    label: row.label,
    desc: row.desc || '',
    impact: row.impact || '',
    is_active: row.is_active,
  })
  optionFormVisible.value = true
}

// 保存选项
const handleSaveOption = async () => {
  if (!optionFormRef.value) return
  await optionFormRef.value.validate(async (valid) => {
    if (!valid) return
    savingOption.value = true
    try {
      if (isEditOption.value) {
        await adminApi.put(
          `/recycle-templates/${currentTemplate.value.id}/questions/${currentQuestion.value.id}/options/${currentOptionId.value}`,
          optionForm
        )
        ElMessage.success('更新成功')
      } else {
        await adminApi.post(
          `/recycle-templates/${currentTemplate.value.id}/questions/${currentQuestion.value.id}/options`,
          optionForm
        )
        ElMessage.success('创建成功')
      }
      optionFormVisible.value = false
      handleManageOptions(currentQuestion.value)
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      savingOption.value = false
    }
  })
}

// 删除选项
const handleDeleteOption = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除选项 "${row.label}" 吗？`, '确认删除', {
      type: 'warning',
    })
    await adminApi.delete(
      `/recycle-templates/${currentTemplate.value.id}/questions/${currentQuestion.value.id}/options/${row.id}`
    )
    ElMessage.success('删除成功')
    handleManageOptions(currentQuestion.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 选项对话框关闭
const handleOptionDialogClose = () => {
  currentQuestion.value = null
  options.value = []
}

// 选项表单关闭
const handleOptionFormClose = () => {
  optionFormRef.value?.resetFields()
}

// 影响类型标签
const getImpactType = (impact) => {
  const map = {
    positive: 'success',
    minor: 'info',
    major: 'warning',
    critical: 'danger',
  }
  return map[impact] || 'info'
}

const getImpactLabel = (impact) => {
  const map = {
    positive: '正面影响',
    minor: '轻微影响',
    major: '重大影响',
    critical: '严重影响',
  }
  return map[impact] || impact
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.recycle-templates {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}

.page-desc {
  color: #6b7280;
  font-size: 14px;
}

.filter-card {
  margin-bottom: 16px;
}

.filter-form {
  margin: 0;
}

.table-card {
  margin-bottom: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.form-hint {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
  line-height: 1.6;
  padding: 8px 12px;
  background: #f9fafb;
  border-left: 3px solid #e5e7eb;
  border-radius: 4px;
  margin-top: 6px;
}

.form-hint strong {
  color: #374151;
  font-weight: 600;
}

.form-hint div {
  margin-top: 4px;
}
</style>
