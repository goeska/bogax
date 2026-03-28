/**
 * Soft delete via PATCH { is_active: false }.
 * Pair with backend SoftDeactivateDestroyMixin on the same resource.
 */
const DEFAULT_DEACTIVATE_ERROR = "Couldn't deactivate that row."

export function deactivateErrorMessage(error, fallback = DEFAULT_DEACTIVATE_ERROR) {
  const data = error.response?.data
  if (data?.detail) {
    return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
  }
  if (data && typeof data === 'object') {
    return JSON.stringify(data)
  }
  return fallback
}

/**
 * @param {import('axios').AxiosInstance} client
 * @param {string} pathSegment API path without base, e.g. "uoms" or "product-categories"
 * @param {string|number} id
 */
export function softDeactivate(client, pathSegment, id) {
  const seg = String(pathSegment).replace(/^\/+|\/+$/g, '')
  return client.patch(`/${seg}/${id}/`, { is_active: false })
}
