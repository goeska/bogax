export function extractApiErrorText(data) {
  if (!data) return ''
  if (typeof data === 'string') return data
  if (typeof data !== 'object') return String(data)
  if (typeof data.detail === 'string') return data.detail
  if (Array.isArray(data.detail) && typeof data.detail[0] === 'string') return data.detail[0]
  if (Array.isArray(data.non_field_errors) && typeof data.non_field_errors[0] === 'string') {
    return data.non_field_errors[0]
  }
  for (const k of Object.keys(data)) {
    const v = data[k]
    if (typeof v === 'string') return v
    if (Array.isArray(v) && typeof v[0] === 'string') return v[0]
  }
  try {
    return JSON.stringify(data)
  } catch {
    return ''
  }
}

