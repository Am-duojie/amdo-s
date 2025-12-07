<template>
  <div class="wallet-page">
    <div class="wallet-container">
      <!-- 钱包余额卡片 -->
      <el-card class="balance-card" shadow="hover">
        <div class="balance-content">
          <div class="balance-label">钱包余额</div>
          <div class="balance-amount">¥{{ walletInfo.balance || '0.00' }}</div>
          <div class="balance-frozen" v-if="walletInfo.frozen_balance > 0">
            冻结余额: ¥{{ walletInfo.frozen_balance }}
          </div>
          <div style="margin-top: 12px; font-size: 12px">
            <el-tag v-if="bindForm.alipay_login_id" type="success" size="small">已绑定：{{ bindForm.alipay_login_id }}</el-tag>
            <el-tag v-else type="warning" size="small">未绑定支付宝账户</el-tag>
          </div>
        </div>
      </el-card>

      <!-- 标签页导航 -->
      <el-card class="tabs-card" shadow="hover">
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <!-- 交易记录 -->
          <el-tab-pane label="交易记录" name="transactions">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
              <span style="font-size: 16px; font-weight: 500">交易记录</span>
              <el-button text @click="loadTransactions">刷新</el-button>
            </div>
            <el-table :data="transactions" v-loading="loading" style="width: 100%">
              <el-table-column prop="created_at" label="时间" width="180">
                <template #default="{ row }">
                  {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="transaction_type_display" label="类型" width="120">
                <template #default="{ row }">
                  <el-tag :type="getTransactionType(row.transaction_type)">
                    {{ row.transaction_type_display }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="金额" width="120">
                <template #default="{ row }">
                  <span :class="row.amount >= 0 ? 'amount-income' : 'amount-expense'">
                    {{ row.amount >= 0 ? '+' : '' }}¥{{ Math.abs(row.amount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="balance_after" label="余额" width="120">
                <template #default="{ row }">
                  ¥{{ row.balance_after }}
                </template>
              </el-table-column>
              <el-table-column prop="note" label="备注" min-width="200">
                <template #default="{ row }">
                  {{ row.note || '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="alipay_order_id" label="支付宝订单号" width="220">
                <template #default="{ row }">
                  <span v-if="row.alipay_order_id">{{ row.alipay_order_id }}</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="withdraw_status_display" label="提现状态" width="120" v-if="hasWithdrawStatus">
                <template #default="{ row }">
                  <el-tag v-if="row.withdraw_status" :type="getWithdrawStatusType(row.withdraw_status)" size="small">
                    {{ row.withdraw_status_display }}
                  </el-tag>
                  <span v-else>-</span>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="transactions.length === 0 && !loading" style="text-align: center; padding: 40px; color: #909399">
              <el-empty description="暂无交易记录" :image-size="100" />
            </div>
            <div v-if="pagination.total > 0" style="display: flex; justify-content: flex-end; margin-top: 16px">
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
          </el-tab-pane>

          <!-- 提现 -->
          <el-tab-pane label="提现" name="withdraw">
            <div style="margin-bottom: 20px">
              <el-alert
                type="info"
                :closable="false"
              >
                <template #title>
                  <div>提现将转账到您的支付宝账户（支持沙箱环境）</div>
                </template>
              </el-alert>
            </div>
            <el-form :model="withdrawForm" label-width="120px" style="max-width: 600px">
              <el-form-item label="可提现金额">
                <div style="font-size: 24px; color: #f56c6c; font-weight: bold">
                  ¥{{ walletInfo.balance || '0.00' }}
                </div>
              </el-form-item>
              <el-form-item label="提现金额" required>
                <el-input-number
                  v-model="withdrawForm.amount"
                  :precision="2"
                  :min="0.01"
                  :max="walletInfo.balance && walletInfo.balance > 0.01 ? walletInfo.balance : 0.01"
                  :step="100"
                  :disabled="!walletInfo.balance || walletInfo.balance <= 0"
                  style="width: 100%"
                  placeholder="请输入提现金额"
                />
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  可提现金额: ¥{{ walletInfo.balance || '0.00' }}
                </div>
              </el-form-item>
              <el-form-item label="支付宝账号" required>
                <el-input
                  v-model="withdrawForm.alipay_account"
                  placeholder="请输入支付宝账号（手机号或邮箱）"
                />
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  支持沙箱环境测试账号。如果已绑定支付宝账户，将自动填充
                </div>
              </el-form-item>
              <el-form-item label="支付宝姓名">
                <el-input
                  v-model="withdrawForm.alipay_name"
                  placeholder="请输入支付宝真实姓名（可选，建议填写）"
                />
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  填写真实姓名可提高提现成功率
                </div>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="withdrawing" @click="handleWithdraw" :disabled="!walletInfo.balance || walletInfo.balance <= 0">
                  确认提现
                </el-button>
                <el-button @click="resetWithdrawForm">重置</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 绑定支付宝 -->
          <el-tab-pane label="绑定支付宝" name="bind">
            <div style="margin-bottom: 20px">
              <el-alert
                type="info"
                :closable="false"
              >
                <template #title>
                  <div>绑定后，买家确认收货时的分账将直接打到该支付宝账户</div>
                </template>
              </el-alert>
            </div>
            <el-form :model="bindForm" label-width="120px" style="max-width: 600px">
              <el-form-item label="支付宝登录账号" required>
                <el-input v-model="bindForm.alipay_login_id" placeholder="请输入支付宝登录账号（手机号或邮箱）" />
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  该账号用于分账收款，请确保为您的支付宝登录账号
                </div>
              </el-form-item>
              <el-form-item label="支付宝姓名">
                <el-input v-model="bindForm.alipay_real_name" placeholder="请输入支付宝真实姓名（可选，建议填写）" />
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  填写真实姓名有助于提高分账成功率
                </div>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="binding" @click="handleBindAlipay">保存绑定</el-button>
                <el-button @click="loadUser">刷新</el-button>
              </el-form-item>
            </el-form>
            <div v-if="bindForm.alipay_login_id" style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 4px; border: 1px solid #b3d8ff">
              <div style="font-size: 14px; font-weight: 500; margin-bottom: 8px; color: #409eff">当前绑定信息</div>
              <div style="font-size: 13px; color: #606266">
                <div>支付宝账号：{{ bindForm.alipay_login_id }}</div>
                <div v-if="bindForm.alipay_real_name">支付宝姓名：{{ bindForm.alipay_real_name }}</div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()
const walletInfo = ref({ balance: 0, frozen_balance: 0 })
const transactions = ref([])
const loading = ref(false)
const withdrawing = ref(false)
const pagination = reactive({ current: 1, pageSize: 20, total: 0 })
const userInfo = ref(null)
const binding = ref(false)
const activeTab = ref('transactions')

const withdrawForm = reactive({
  amount: null,
  alipay_account: '',
  alipay_name: ''
})

const bindForm = reactive({
  alipay_login_id: '',
  alipay_real_name: ''
})

const hasWithdrawStatus = computed(() => {
  return transactions.value.some(t => t.withdraw_status)
})

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getTransactionType = (type) => {
  const typeMap = {
    income: 'success',
    expense: 'danger',
    withdraw: 'warning',
    refund: 'info'
  }
  return typeMap[type] || 'info'
}

const getWithdrawStatusType = (status) => {
  const statusMap = {
    pending: 'warning',
    processing: 'primary',
    success: 'success',
    failed: 'danger'
  }
  return statusMap[status] || 'info'
}

const loadWallet = async () => {
  loading.value = true
  try {
    const res = await api.get('/users/wallet/', {
      params: {
        page: pagination.current,
        page_size: pagination.pageSize
      }
    })
    walletInfo.value = {
      balance: res.data.balance || 0,
      frozen_balance: res.data.frozen_balance || 0
    }
    transactions.value = res.data.transactions || []
    pagination.total = res.data.total || 0
  } catch (error) {
    ElMessage.error('加载钱包信息失败')
  } finally {
    loading.value = false
  }
}

const loadUser = async () => {
  try {
    const res = await api.get('/users/me/')
    userInfo.value = res.data || null
    bindForm.alipay_login_id = userInfo.value?.alipay_login_id || ''
    bindForm.alipay_real_name = userInfo.value?.alipay_real_name || ''
    // 如果已绑定支付宝，自动填充到提现表单
    if (bindForm.alipay_login_id && !withdrawForm.alipay_account) {
      withdrawForm.alipay_account = bindForm.alipay_login_id
    }
    if (bindForm.alipay_real_name && !withdrawForm.alipay_name) {
      withdrawForm.alipay_name = bindForm.alipay_real_name
    }
  } catch (error) {
    // 忽略错误，仅用于展示绑定表单
  }
}

const loadTransactions = async () => {
  await loadWallet()
}

const handlePageChange = () => {
  loadWallet()
}

const handleSizeChange = () => {
  pagination.current = 1
  loadWallet()
}

const handleTabChange = (tabName) => {
  // 切换标签页时，如果是提现标签且已绑定支付宝，自动填充
  if (tabName === 'withdraw') {
    if (bindForm.alipay_login_id && !withdrawForm.alipay_account) {
      withdrawForm.alipay_account = bindForm.alipay_login_id
    }
    if (bindForm.alipay_real_name && !withdrawForm.alipay_name) {
      withdrawForm.alipay_name = bindForm.alipay_real_name
    }
  }
}

const resetWithdrawForm = () => {
  withdrawForm.amount = null
  withdrawForm.alipay_account = bindForm.alipay_login_id || ''
  withdrawForm.alipay_name = bindForm.alipay_real_name || ''
}

const handleWithdraw = async () => {
  if (!withdrawForm.amount || withdrawForm.amount <= 0) {
    ElMessage.warning('请输入提现金额')
    return
  }
  if (withdrawForm.amount > walletInfo.value.balance) {
    ElMessage.warning('提现金额不能超过余额')
    return
  }
  if (!withdrawForm.alipay_account) {
    ElMessage.warning('请输入支付宝账号')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认提现 ¥${withdrawForm.amount} 到支付宝账号 ${withdrawForm.alipay_account}？`,
      '确认提现',
      { type: 'warning' }
    )
    
    withdrawing.value = true
    const res = await api.post('/users/withdraw/', {
      amount: withdrawForm.amount,
      alipay_account: withdrawForm.alipay_account,
      alipay_name: withdrawForm.alipay_name
    })
    
    if (res.data.success) {
      ElMessage.success(res.data.message || '提现成功')
      resetWithdrawForm()
      await loadWallet()
      // 提现成功后切换到交易记录标签页
      activeTab.value = 'transactions'
    } else {
      ElMessage.error(res.data.detail || '提现失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      const errorDetail = error.response?.data?.detail || '提现失败'
      ElMessage.error(errorDetail)
    }
  } finally {
    withdrawing.value = false
  }
}

const handleBindAlipay = async () => {
  if (!bindForm.alipay_login_id) {
    ElMessage.warning('请输入支付宝登录账号')
    return
  }
  try {
    binding.value = true
    const res = await api.patch('/users/me/', {
      alipay_login_id: bindForm.alipay_login_id,
      alipay_real_name: bindForm.alipay_real_name
    })
    ElMessage.success('绑定成功')
    // 更新用户信息和绑定表单
    userInfo.value = res.data
    // 确保 bindForm 与返回的数据同步
    if (res.data) {
      bindForm.alipay_login_id = res.data.alipay_login_id || bindForm.alipay_login_id
      bindForm.alipay_real_name = res.data.alipay_real_name || bindForm.alipay_real_name
    }
    // 同时更新 authStore 中的用户信息
    if (authStore.user) {
      authStore.user.alipay_login_id = res.data?.alipay_login_id || ''
      authStore.user.alipay_real_name = res.data?.alipay_real_name || ''
      localStorage.setItem('user', JSON.stringify(authStore.user))
    }
    // 如果提现表单中的账号为空，自动填充
    if (!withdrawForm.alipay_account && bindForm.alipay_login_id) {
      withdrawForm.alipay_account = bindForm.alipay_login_id
    }
    if (!withdrawForm.alipay_name && bindForm.alipay_real_name) {
      withdrawForm.alipay_name = bindForm.alipay_real_name
    }
  } catch (error) {
    const detail = error.response?.data?.detail || '绑定失败'
    ElMessage.error(detail)
  } finally {
    binding.value = false
  }
}

onMounted(() => {
  loadWallet()
  loadUser()
})
</script>

<style scoped>
.wallet-page {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
}

.wallet-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.balance-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.balance-card :deep(.el-card__body) {
  padding: 40px;
}

.balance-content {
  text-align: center;
}

.balance-label {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 16px;
}

.balance-amount {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 12px;
}

.balance-frozen {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 12px;
}

.tabs-card {
  background: white;
}

.amount-income {
  color: #67c23a;
  font-weight: 500;
}

.amount-expense {
  color: #f56c6c;
  font-weight: 500;
}
</style>
