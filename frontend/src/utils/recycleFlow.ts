export type RecycleOrderLike = {
  status?: string
  final_price?: number | string | null
  final_price_confirmed?: boolean
  price_dispute?: boolean
  payment_status?: string
  paid_at?: string | null
}

export type TagType = '' | 'info' | 'success' | 'warning' | 'danger' | 'primary'

export type RecycleStage =
  | 'pending'
  | 'shipped'
  | 'received'
  | 'inspected'
  | 'completed'
  | 'paid'
  | 'cancelled'

export const RECYCLE_STEP_VALUES: RecycleStage[] = [
  'pending',
  'shipped',
  'received',
  'inspected',
  'completed',
  'paid'
]

const toBool = (v: unknown) => v === true

export function getRecycleStage(order: RecycleOrderLike | null | undefined): RecycleStage {
  const status = (order?.status || 'pending') as string
  if (status === 'cancelled') return 'cancelled'

  const paid = order?.payment_status === 'paid' || !!order?.paid_at
  if (paid) return 'paid'

  if (status === 'pending' || status === 'shipped' || status === 'received') return status

  const hasFinalPrice = order?.final_price !== null && order?.final_price !== undefined && order?.final_price !== ''
  const confirmed = toBool(order?.final_price_confirmed)
  const dispute = toBool(order?.price_dispute)

  if (dispute) return 'inspected'
  if (hasFinalPrice && !confirmed) return 'inspected'

  if (status === 'inspected') return 'inspected'
  if (status === 'completed') return 'completed'

  // fallback
  return 'pending'
}

export function getRecycleStatusTag(order: RecycleOrderLike | null | undefined): { text: string; type: TagType } {
  const status = (order?.status || 'pending') as string
  const stage = getRecycleStage(order)

  if (stage === 'paid') return { text: '已打款', type: 'success' }
  if (status === 'cancelled') return { text: '已取消', type: 'danger' }

  const hasFinalPrice = order?.final_price !== null && order?.final_price !== undefined && order?.final_price !== ''
  const confirmed = toBool(order?.final_price_confirmed)
  const dispute = toBool(order?.price_dispute)

  if (dispute) return { text: '价格异议处理中', type: 'warning' }
  if (hasFinalPrice && !confirmed && (status === 'inspected' || status === 'completed')) {
    return { text: '待确认价格', type: 'warning' }
  }
  if (status === 'completed' && confirmed) return { text: '待打款', type: 'warning' }

  const base: Record<string, { text: string; type: TagType }> = {
    pending: { text: '待寄出', type: 'info' },
    shipped: { text: '已寄出', type: 'primary' },
    received: { text: '已收货', type: 'success' },
    inspected: { text: '已检测', type: 'success' },
    completed: { text: '已完成', type: 'success' }
  }
  return base[status] || { text: status || '-', type: 'info' }
}

export function getRecycleProcessSteps(
  order: RecycleOrderLike | null | undefined
): Array<{ value: RecycleStage; label: string }> {
  const status = (order?.status || 'pending') as string
  const hasFinalPrice = order?.final_price !== null && order?.final_price !== undefined && order?.final_price !== ''
  const confirmed = toBool(order?.final_price_confirmed)
  const dispute = toBool(order?.price_dispute)

  const inspectedLabel = dispute ? '价格异议' : hasFinalPrice && !confirmed ? '待确认价格' : '已检测'
  const completedLabel = status === 'completed' && confirmed ? '待打款' : '已完成'

  return [
    { label: '提交订单', value: 'pending' },
    { label: '已寄出', value: 'shipped' },
    { label: '已收货', value: 'received' },
    { label: inspectedLabel, value: 'inspected' },
    { label: completedLabel, value: 'completed' },
    { label: '已打款', value: 'paid' }
  ]
}

export function getRecycleStageIndex(order: RecycleOrderLike | null | undefined): number {
  const stage = getRecycleStage(order)
  if (stage === 'cancelled') return 0
  const idx = RECYCLE_STEP_VALUES.indexOf(stage)
  return idx >= 0 ? idx : 0
}

export function isRecycleStepCompleted(order: RecycleOrderLike | null | undefined, step: RecycleStage): boolean {
  if (step === 'pending') return true
  const stage = getRecycleStage(order)
  if (stage === 'cancelled') return false
  const stepIndex = RECYCLE_STEP_VALUES.indexOf(step)
  const currentIndex = RECYCLE_STEP_VALUES.indexOf(stage)
  if (stepIndex === -1 || currentIndex === -1) return false
  return currentIndex > stepIndex
}

export function isRecycleStepActive(order: RecycleOrderLike | null | undefined, step: RecycleStage): boolean {
  const stage = getRecycleStage(order)
  if (stage === 'cancelled') return step === 'pending'
  return stage === step
}

export function getRecycleElementStepStatus(
  order: RecycleOrderLike | null | undefined,
  step: RecycleStage
): 'wait' | 'process' | 'success' {
  if (isRecycleStepCompleted(order, step)) return 'success'
  if (isRecycleStepActive(order, step)) return 'process'
  return 'wait'
}
