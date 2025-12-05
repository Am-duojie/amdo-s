/**
 * @typedef {Object} PaginatedResponse
 * @property {Array<any>} results
 * @property {number} [count]
 */

/**
 * 判断是否为 DRF 分页响应
 * @param {any} data
 * @returns {data is PaginatedResponse}
 */
export function isPaginated(data) {
  return data && typeof data === 'object' && Array.isArray(data.results)
}

/**
 * 获取统一的结果数组
 * @param {any} data
 * @returns {Array<any>}
 */
export function getResults(data) {
  if (isPaginated(data)) return data.results
  if (Array.isArray(data)) return data
  return []
}

/**
 * 获取统一的总数
 * @param {any} data
 * @returns {number}
 */
export function getCount(data) {
  if (isPaginated(data)) return typeof data.count === 'number' ? data.count : getResults(data).length
  if (Array.isArray(data)) return data.length
  return 0
}
