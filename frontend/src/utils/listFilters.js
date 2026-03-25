/** Query params for paginated order lists (sales / purchase). */
export function buildOrderListParams(
  page,
  { productId, salesOrderCode, purchaseOrderCode, state, dateFrom, dateTo },
) {
  const params = { page }
  if (productId) params.product_id = productId
  if (salesOrderCode) params.sales_order_code = salesOrderCode
  if (purchaseOrderCode) params.purchase_order_code = purchaseOrderCode
  if (state) params.state = state
  if (dateFrom) params.date_from = dateFrom
  if (dateTo) params.date_to = dateTo
  return params
}

/** Query params for paginated payment list. */
export function buildPaymentListParams(page, { txType, dateFrom, dateTo }) {
  const params = { page }
  if (txType === 'i' || txType === 'o') params.tx_type = txType
  if (dateFrom) params.date_from = dateFrom
  if (dateTo) params.date_to = dateTo
  return params
}
