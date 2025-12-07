<template>
  <div class="verified-product-form">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="商品标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入商品标题" />
      </el-form-item>
      <el-form-item label="品牌" prop="brand">
        <el-input v-model="form.brand" placeholder="如：苹果、华为" />
      </el-form-item>
      <el-form-item label="型号" prop="model">
        <el-input v-model="form.model" placeholder="如：iPhone 13" />
      </el-form-item>
      <el-form-item label="存储容量">
        <el-input v-model="form.storage" placeholder="如：128GB" />
      </el-form-item>
      <el-form-item label="成色" prop="condition">
        <el-select v-model="form.condition" style="width: 100%">
          <el-option label="全新" value="new" />
          <el-option label="99成新" value="like_new" />
          <el-option label="95成新" value="good" />
        </el-select>
      </el-form-item>
      <el-form-item label="价格" prop="price">
        <el-input-number v-model="form.price" :precision="2" :min="0" style="width: 100%" />
      </el-form-item>
      <el-form-item label="原价">
        <el-input-number v-model="form.original_price" :precision="2" :min="0" style="width: 100%" />
      </el-form-item>
      <el-form-item label="商品描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入商品描述" />
      </el-form-item>
    </el-form>
    <div style="text-align: right; margin-top: 20px">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">创建</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['created', 'cancel'])

const formRef = ref()
const saving = ref(false)

const form = reactive({
  title: '',
  brand: '',
  model: '',
  storage: '',
  condition: 'good',
  price: 0,
  original_price: 0,
  description: ''
})

const rules = {
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  brand: [{ required: true, message: '请输入品牌', trigger: 'blur' }],
  model: [{ required: true, message: '请输入型号', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }]
}

const submit = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    await adminApi.post('/verified-listings', form)
    ElMessage.success('创建成功')
    emit('created')
  } catch (error) {
    if (error !== false) {
      ElMessage.error('创建失败')
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.verified-product-form {
  padding: 0;
}
</style>









