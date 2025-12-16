import api from '@/utils/api'

export type RecycleCatalogParams = {
  device_type?: string
  brand?: string
  model?: string
  q?: string
}

export type RecycleCatalogResponse = {
  device_types: string[]
  brands: Record<string, string[]>
  models: Record<
    string,
    Record<
      string,
      Array<{
        name: string
        storages?: string[]
        series?: string | null
      }>
    >
  >
}

export const getRecycleCatalog = (params?: RecycleCatalogParams) => {
  return api.get<RecycleCatalogResponse>('/recycle-catalog/', { params })
}

export type EstimatePayload = {
  device_type: string
  brand: string
  model: string
  storage?: string
  condition?: string
  release_year?: number | string
}

export type EstimateResponse = {
  base_price?: number | null  // 基础价格（从模板获取）
  estimated_price: number      // 根据成色调整后的价格
  bonus: number               // 额外加价
  total_price: number          // 总价
  price_source?: string        // 价格来源：template/api/model/local_model
  condition?: string           // 成色
  currency: string
  unit: string
}

export const estimateRecyclePrice = (payload: EstimatePayload) => {
  return api.post<EstimateResponse>('/recycle-orders/estimate/', payload)
}

// 获取机型模板的问卷内容
export type RecycleQuestionTemplateResponse = {
  id: number
  template_id: number  // 模板ID（用于提交订单时关联）
  device_type: string
  brand: string
  model: string
  storages?: string[]  // 存储容量列表
  questions: Array<{
    id: number
    step_order: number
    key: string
    title: string
    helper?: string
    question_type: 'single' | 'multi'
    is_required: boolean
    options: Array<{
      id: number
      value: string
      label: string
      desc?: string
      impact?: 'positive' | 'minor' | 'major' | 'critical'
      option_order: number
    }>
  }>
}

export const getRecycleQuestionTemplate = (params: { device_type: string; brand: string; model: string }) => {
  return api.get<RecycleQuestionTemplateResponse>('/recycle-templates/question-template/', { params })
}

// 创建回收订单
export type CreateRecycleOrderPayload = {
  device_type: string
  brand: string
  model: string
  storage?: string
  condition?: string
  estimated_price?: number
  bonus?: number
  contact_name: string
  contact_phone: string
  address: string
  note?: string
}

export type RecycleOrderResponse = {
  id: number
  user: number
  device_type: string
  brand: string
  model: string
  storage?: string
  condition: string
  estimated_price?: number
  final_price?: number
  bonus?: number
  status: string
  contact_name: string
  contact_phone: string
  address: string
  note?: string
  created_at: string
  updated_at: string
}

export const createRecycleOrder = (payload: CreateRecycleOrderPayload) => {
  return api.post<RecycleOrderResponse>('/recycle-orders/', payload)
}













