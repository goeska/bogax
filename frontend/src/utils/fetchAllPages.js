import { api } from '../api/client'

/**
 * Load all pages from a DRF paginated list (bounded iterations).
 * @param {string} urlPath
 * @param {Record<string, unknown>} [extraParams]
 */
export async function fetchAllPages(urlPath, extraParams = {}) {
  const items = []
  let page = 1
  const maxPages = 50
  while (page <= maxPages) {
    const { data } = await api.get(urlPath, { params: { page, ...extraParams } })
    const chunk = Array.isArray(data) ? data : (data.results ?? [])
    items.push(...chunk)
    const hasNext = Boolean(data.next) && chunk.length > 0
    if (!hasNext) break
    page += 1
  }
  return items
}
