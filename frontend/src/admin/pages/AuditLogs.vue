
<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">审计日志</h2>
    </div>

    <el-table :data="items" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="actor" label="操作者" width="140" />
      <el-table-column prop="target_type" label="对象类型" width="160">
        <template #default="{row}">
          {{ getTargetTypeLabel(row.target_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="target_id" label="对象ID" width="100" />
      <el-table-column prop="action" label="动作" width="140">
        <template #default="{row}">
          {{ getActionLabel(row.action) }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="200" />
      <el-table-column label="详情">
        <template #default="{row}">
          <pre style="white-space:pre-wrap">{{ formatSnapshot(row.snapshot_json) }}</pre>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
      <el-pagination
        v-model:current-page="pagination.current"
        :total="pagination.total"
        :page-size="pagination.pageSize"
        layout="prev, pager, next, total"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminApi from '@/utils/adminApi'
import { ElMessage } from 'element-plus'

const items = ref([])
const pagination = ref({ current: 1, pageSize: 10, total: 0 })

const targetTypeLabels = {
  RecycleOrder: '回收订单',
  VerifiedProduct: '官方验机商品',
  VerifiedOrder: '官方验机订单',
  Order: '订单',
  AdminUser: '管理员',
  AdminRole: '角色',
  AdminAuditQueueItem: '审核队列'
}

const actionLabels = {
  status_change: '状态变更',
  inspection_report: '生成质检报告',
  logistics_ship: '回收单发货',
  logistics_receive: '回收单收货',
  payment: '回收打款',
  publish_verified: '发布验机商品',
  batch_update: '批量更新',
  create_verified_device: '生成验机设备',
  approve: '审核通过',
  reject: '审核驳回',
  'admin_user:create': '创建管理员',
  'admin_user:update': '更新管理员',
  'admin_user:delete': '删除管理员',
  'role:upsert': '更新角色权限',
  ship: '发货',
  settlement_auto: '自动分账',
  settlement_retry: '分账重试',
  settlement_retry_transfer: '分账重试打款',
  'mark-paid': '标记已支付',
  complete: '确认完成',
  cancel: '取消订单'
}

const snapshotLabels = {
  bonus: '补贴',
  final_price: '最终价',
  estimated_price: '预估价',
  amount: '金额',
  commission_amount: '平台佣金',
  recommend_price: '建议价',
  payment_method: '打款方式',
  payment_account: '打款账户',
  note: '备注',
  status: '状态',
  old_status: '原状态',
  new_status: '新状态',
  carrier: '物流公司',
  tracking_number: '运单号',
  received_at: '收货时间',
  device_id: '设备ID',
  verified_product_id: '验机商品ID',
  product_id: '商品ID',
  template_name: '模板名称',
  template_version: '模板版本',
  check_items_count: '检测项数量',
  evidence_count: '证据数量',
  overall_result: '综合结果',
  score: '评分',
  reject_reason: '拒绝原因',
  title: '标题',
  name: '名称',
  username: '用户名',
  role: '角色',
  permissions: '权限',
  result: '结果',
  code: '错误码',
  sub_code: '子错误码',
  msg: '错误信息',
  sub_msg: '子错误信息',
  ids: '对象列表',
  count: '数量',
  trade_no: '支付单号',
  refund_amount: '退款金额',
  refund_reason: '退款原因',
  gmt_refund_pay: '退款时间',
  seller_amount: '卖家应收',
  out_request_no: '请求号'
}

const getTargetTypeLabel = (value) => targetTypeLabels[value] || value || '-'

const getActionLabel = (value) => {
  if (!value) return '-'
  if (value === 'update_estimated_price') return '更新预估价'
  if (value === 'update_final_price') return '更新最终价'
  return actionLabels[value] || value
}

const formatSnapshot = (snapshot) => {
  if (!snapshot || Object.keys(snapshot).length === 0) return '-'
  const lines = []
  Object.entries(snapshot).forEach(([key, value]) => {
    const label = snapshotLabels[key] || key
    let text = value
    if (Array.isArray(value)) {
      text = value.join(', ')
    } else if (value && typeof value === 'object') {
      text = JSON.stringify(value)
    }
    lines.push(`${label}: ${text}`)
  })
  return lines.join('\n')
}

const load = async () => {
  try {
    const res = await adminApi.get('/audit/logs', {
      params: {
        page: pagination.value.current,
        page_size: pagination.value.pageSize
      }
    })
    items.value = res.data?.results || []
    pagination.value.total = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const handlePageChange = () => load()

onMounted(load)
</script>
