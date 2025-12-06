<template>
  <div class="wallet-page">
    <div class="wallet-container">
      <!-- 钱包余额卡片 -->
      <el-card class="balance-card" shadow="hover">
        <div class="balance-content">
          <div class="balance-label">钱包余额</div>
          <div class="balance-amount">¥{{ walletInfo.balance || '0.00' }}</div>
          <div class="balance-actions">
            <el-button type="primary" @click="showWithdrawDialog = true" :disabled="!walletInfo.balance || walletInfo.balance <= 0">
              提现
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 交易记录 -->
      <el-card class="transactions-card" shadow="hover">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center">
            <span>交易记录</span>
            <el-button text @click="loadTransactions">刷新</el-button>
          </div>
        </template>
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
      </el-card>
    </div>

    <!-- 提现对话框 -->
    <el-dialog
      v-model="showWithdrawDialog"
      title="提现到支付宝"
      width="500px"
    >
      <el-alert
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      >
        <template #title>
          <div>提现将转账到您的支付宝账户（支持沙箱环境）</div>
        </template>
      </el-alert>
      <el-form :model="withdrawForm" label-width="100px">
        <el-form-item label="提现金额" required>
          <el-input-number
            v-model="withdrawForm.amount"
            :precision="2"
            :min="0.01"
            :max="walletInfo.balance"
            :step="100"
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
            支持沙箱环境测试账号
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
      </el-form>
      <template #footer>
        <el-button @click="showWithdrawDialog = false">取消</el-button>
        <el-button type="primary" :loading="withdrawing" @click="handleWithdraw">确认提现</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()
const walletInfo = ref({ balance: 0, frozen_balance: 0 })
const transactions = ref([])
const loading = ref(false)
const showWithdrawDialog = ref(false)
const withdrawing = ref(false)
const pagination = reactive({ current: 1, pageSize: 20, total: 0 })

const withdrawForm = reactive({
  amount: null,
  alipay_account: '',
  alipay_name: ''
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
      showWithdrawDialog.value = false
      withdrawForm.amount = null
      withdrawForm.alipay_account = ''
      withdrawForm.alipay_name = ''
      await loadWallet()
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

onMounted(() => {
  loadWallet()
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
  margin-bottom: 24px;
}

.balance-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.transactions-card {
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

