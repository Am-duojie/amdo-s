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

export const estimateRecyclePrice = (payload: EstimatePayload) => {
  return api.post('/recycle-orders/estimate/', payload)
}

// 获取机型模板的问卷内容
export type RecycleQuestionTemplateResponse = {
  id: number
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


