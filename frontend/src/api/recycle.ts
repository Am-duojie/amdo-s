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


