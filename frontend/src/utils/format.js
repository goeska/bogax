/**
 * IDR currency for display (lists, POS, confirmations).
 */
export function formatIdr(n) {
  const v = Number(n)
  if (!Number.isFinite(v)) return '—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(v)
}

/**
 * ISO date string → locale date/time (e.g. transaction lists, POS hints).
 * @param {string|undefined|null} iso
 * @param {{ empty?: string }} [opts]
 */
export function formatDateTimeIso(iso, { empty = '—' } = {}) {
  if (!iso) return empty
  try {
    return new Intl.DateTimeFormat('en-US', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return String(iso)
  }
}

/**
 * Live Date value for readonly POS time field: DD-MM-YYYY HH:mm
 * @param {Date|string|number} d
 */
export function formatTransactionDisplay(d) {
  const x = d instanceof Date ? d : new Date(d)
  if (Number.isNaN(x.getTime())) return ''
  const dd = String(x.getDate()).padStart(2, '0')
  const mm = String(x.getMonth() + 1).padStart(2, '0')
  const yyyy = x.getFullYear()
  const hh = String(x.getHours()).padStart(2, '0')
  const min = String(x.getMinutes()).padStart(2, '0')
  return `${dd}-${mm}-${yyyy} ${hh}:${min}`
}
