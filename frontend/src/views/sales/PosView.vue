<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../../api/client'
import { fetchAllPages } from '../../utils/fetchAllPages'
import { formatDateTimeIso, formatIdr, formatTransactionDisplay } from '../../utils/format'

const route = useRoute()
const isDeliveryOrder = computed(() => route.name === 'sales-do-form')
const isNonRetail = computed(() => route.name === 'sales-so-form' || isDeliveryOrder.value)
const saveDraftEndpoint = computed(() => {
  if (isDeliveryOrder.value) return '/sales/delivery-order/save-draft/'
  if (isNonRetail.value) return '/sales/non-retail/save-draft/'
  return '/pos/save-draft/'
})

const configLoading = ref(true)
const configErr = ref('')
const isRestaurant = ref(false)
const isCustomerMaintained = ref(false)

const categories = ref([])
const catalogErr = ref('')
const productsErr = ref('')

const selectedCategoryId = ref('')
const selectedProductId = ref('')
const products = ref([])
const productsLoading = ref(false)

const quantity = ref(1)
const unitPriceStr = ref('')
const transactionAt = ref(new Date())

const tableRef = ref('')
const partnerName = ref('')
const partnerPhone = ref('')
const selectedPartnerId = ref('')
const selectedProjectId = ref('')
const corporatePartners = ref([])
const partnersLoading = ref(false)
const partnerLoadErr = ref('')
const projects = ref([])
const projectsLoading = ref(false)
const projectLoadErr = ref('')
const partnerIdErr = ref('')
const projectIdErr = ref('')

const draftResult = ref(null)
const saveDraftSaving = ref(false)
const saveDraftApiErr = ref('')
const confirmHint = ref('')
const partnerNotice = ref('')
const confirmSaving = ref(false)
const reopenSaving = ref(false)
const appendMode = ref(true)
const REPLACE_CONFIRM_TEXT =
  "Replace the lines already on this order? You can't auto-undo that here."
const transactionErr = ref('')
const productCategoryErr = ref('')
const productErr = ref('')
const quantityErr = ref('')
const unitPriceErr = ref('')
const uomErr = ref('')

const ppnTax = ref(null)
const taxOptions = ref([])
const ppnTaxLoadErr = ref('')
const applyPpn = ref(false)
const selectedTaxIds = ref([])
/** When loading a draft for edit, keep selected tax ids from line. */
const draftTaxIds = ref([])
const skipCategoryWatch = ref(false)
const configReady = ref(false)
const editingLineId = ref(null)
const lineFormLocked = ref(false)
const isFormLocked = computed(() => Boolean(draftResult.value?.id) && lineFormLocked.value)

const selectedTaxes = computed(() => {
  if (isNonRetail.value) {
    const selectedIds = new Set(
      (selectedTaxIds.value || []).map((v) => Number(v)).filter((v) => Number.isFinite(v) && v > 0),
    )
    return taxOptions.value.filter((t) => selectedIds.has(Number(t.id)))
  }
  return ppnTax.value ? [ppnTax.value] : []
})

const selectedTaxRateFractions = computed(() => {
  return selectedTaxes.value
    .map((t) => {
      if (!t || t.rate_percent == null || t.rate_percent === '') return 0
      const n = Number(t.rate_percent)
      if (!Number.isFinite(n) || n < 0) return 0
      return n / 100
    })
    .filter((r) => r > 0)
})

const selectedProduct = computed(() => {
  if (selectedProductId.value === '') return null
  const id = Number(selectedProductId.value)
  return products.value.find((p) => p.id === id) ?? null
})

const uomDisplay = computed(() => {
  const name = selectedProduct.value?.uom_name
  return name != null ? String(name).trim() : ''
})

const productSelectHint = computed(() => {
  if (productsLoading.value) return 'Loading…'
  if (!selectedCategoryId.value) return 'Select category first'
  if (products.value.length === 0) return 'No products in category'
  return 'Select product'
})

function parsedQuantity() {
  const v = quantity.value
  if (v === '' || v === null || v === undefined) return null
  const n = Number(v)
  if (!Number.isFinite(n)) return null
  return n
}

function parsedUnitPrice() {
  const s = String(unitPriceStr.value ?? '').trim()
  if (s === '') return null
  const n = Number(s)
  if (!Number.isFinite(n)) return null
  return n
}

watch(
  () => selectedProduct.value,
  (p) => {
    if (!p) {
      unitPriceStr.value = ''
      return
    }
    const raw = p.unit_price
    if (raw == null || raw === '') {
      unitPriceStr.value = ''
      return
    }
    const n = Number(raw)
    unitPriceStr.value = Number.isFinite(n) ? String(n) : ''
  },
  { immediate: true },
)

const subtotal = computed(() => {
  const u = parsedUnitPrice()
  const q = parsedQuantity()
  if (u == null || u < 0 || q == null || q <= 0) return 0
  return Math.round(u * q)
})

const taxAmount = computed(() => {
  if (!applyPpn.value) return 0
  if (!selectedTaxRateFractions.value.length) return 0
  return selectedTaxRateFractions.value.reduce((sum, r) => sum + Math.round(subtotal.value * r), 0)
})

const grandTotal = computed(() => subtotal.value + taxAmount.value)

const summaryTaxLabel = computed(() => {
  if (!applyPpn.value || selectedTaxes.value.length === 0) return isNonRetail.value ? 'Taxes' : 'PPN'
  if (isNonRetail.value) return `Taxes (${selectedTaxes.value.length})`
  const t = selectedTaxes.value[0]
  const name = String(t.name ?? '').trim()
  const pct = t.rate_percent
  if (name && pct != null && pct !== '') return `${name} (${pct}%)`
  return name || 'PPN'
})

watch(ppnTax, (t) => {
  if (!t && !isNonRetail.value) applyPpn.value = false
})

watch(selectedTaxIds, (ids) => {
  if (isNonRetail.value) applyPpn.value = Array.isArray(ids) && ids.length > 0
})

async function loadProductsForCategory(categoryIdStr) {
  productsErr.value = ''
  if (!categoryIdStr) {
    products.value = []
    return
  }
  productsLoading.value = true
  try {
    const params = {
      product_category_id: categoryIdStr,
    }
    // Retail POS keeps product type restriction; non-retail can sell any type (including service).
    if (!isNonRetail.value) {
      params.product_types = 'storable,consumable'
    }
    products.value = await fetchAllPages('/products/', params)
  } catch {
    productsErr.value = 'Could not load products for this category.'
    products.value = []
  } finally {
    productsLoading.value = false
  }
}

async function loadProjectsForPartner(partnerIdStr) {
  projectLoadErr.value = ''
  if (!partnerIdStr) {
    projects.value = []
    return
  }
  projectsLoading.value = true
  try {
    projects.value = await fetchAllPages('/projects/', { partner_id: partnerIdStr })
  } catch {
    projectLoadErr.value = 'Could not load projects for this customer.'
    projects.value = []
  } finally {
    projectsLoading.value = false
  }
}

watch(selectedCategoryId, async (id) => {
  if (skipCategoryWatch.value) return
  draftTaxIds.value = []
  selectedProductId.value = ''
  products.value = []
  if (id === '' || id == null) return
  await loadProductsForCategory(id)
})

watch(selectedPartnerId, async (id) => {
  if (!isNonRetail.value) return
  selectedProjectId.value = ''
  projects.value = []
  if (!id) return
  await loadProjectsForPartner(id)
})

onMounted(async () => {
  configLoading.value = true
  configErr.value = ''
  catalogErr.value = ''
  try {
    const { data } = await api.get('/main-config/')
    isRestaurant.value = Boolean(data.is_restaurant)
    isCustomerMaintained.value = data.is_customer_maintained === true
  } catch {
    configErr.value = 'Could not load app config.'
    isRestaurant.value = false
    isCustomerMaintained.value = false
  }

  try {
    const allCat = await fetchAllPages('/product-categories/')
    categories.value = allCat.filter((c) => c.is_active !== false)
  } catch {
    catalogErr.value = 'Could not load categories.'
    categories.value = []
  }

  if (isNonRetail.value) {
    partnerLoadErr.value = ''
    partnersLoading.value = true
    try {
      const allCorp = await fetchAllPages('/partners/', { is_corporate: 'true' })
      corporatePartners.value = allCorp.filter((p) => p.is_active !== false)
    } catch {
      partnerLoadErr.value = 'Could not load corporate customers.'
      corporatePartners.value = []
    } finally {
      partnersLoading.value = false
    }
  }

  ppnTaxLoadErr.value = ''
  try {
    const taxes = await fetchAllPages('/taxes/')
    taxOptions.value = taxes
    ppnTax.value = taxes.find((t) => String(t.name || '').toLowerCase().includes('ppn')) ?? null
    if (isNonRetail.value) selectedTaxIds.value = []
  } catch {
    ppnTaxLoadErr.value = 'Could not load tax master data.'
    taxOptions.value = []
    ppnTax.value = null
  } finally {
    configLoading.value = false
  }

  configReady.value = true
  await handleOrderRouteChange(route.query.orderId)
})

function applyOrderHeaderToForm(o) {
  draftResult.value = o
  transactionAt.value = new Date(o.time_transaction)
  if (isNonRetail.value) {
    selectedPartnerId.value = o.partner?.id != null ? String(o.partner.id) : ''
    selectedProjectId.value = o.project_id != null ? String(o.project_id) : ''
  }
  if (isRestaurant.value) {
    tableRef.value = o.table_name != null ? String(o.table_name) : ''
  }
  if (isCustomerMaintained.value) {
    partnerName.value = o.partner?.name ?? o.customer?.name ?? ''
    partnerPhone.value = o.partner?.phone ?? o.customer?.phone ?? ''
  }
}

/** If orderId exists in query, load it; otherwise reset to a new order. */
async function handleOrderRouteChange(raw) {
  if (raw == null || raw === '') {
    newSalesOrder()
    return
  }
  const id = Number(raw)
  if (!Number.isFinite(id)) {
    newSalesOrder()
    return
  }
  saveDraftApiErr.value = ''
  try {
    const { data: o } = await api.get(`/sales-orders/${id}/`)
    const expectedOrderType = isDeliveryOrder.value
      ? 'delivery_order'
      : isNonRetail.value
        ? 'non_retail'
        : 'retail'
    if (o.order_type && o.order_type !== expectedOrderType) {
      saveDraftApiErr.value =
        expectedOrderType === 'delivery_order'
          ? 'This page only supports delivery orders.'
          : expectedOrderType === 'non_retail'
            ? 'This page only supports non-retail sales orders.'
            : 'This page only supports retail sales orders.'
      newSalesOrder()
      return
    }
    applyOrderHeaderToForm(o)
    if (isNonRetail.value && selectedPartnerId.value) {
      await loadProjectsForPartner(selectedPartnerId.value)
    }
    if (o.state === 'draft') {
      startAddItem()
      lineFormLocked.value = true
    } else {
      editingLineId.value = null
      lineFormLocked.value = true
    }
  } catch (e) {
    saveDraftApiErr.value = formatApiError(e)
  }
}

watch(
  () => route.query.orderId,
  async (raw) => {
    if (!configReady.value) return
    await handleOrderRouteChange(raw)
  },
)

watch(
  () => route.name,
  async () => {
    if (!configReady.value) return
    // POS and SO Form reuse this component; reset lock/header state when switching mode.
    await handleOrderRouteChange(route.query.orderId)
  },
)

function formatApiError(err) {
  const d = err?.response?.data
  if (!d) return err?.message || 'Request failed.'
  if (typeof d === 'string') return d
  if (d.detail) return typeof d.detail === 'string' ? d.detail : JSON.stringify(d.detail)
  const parts = []
  for (const k of Object.keys(d)) {
    const v = d[k]
    parts.push(`${k}: ${Array.isArray(v) ? v.join(' ') : typeof v === 'object' ? JSON.stringify(v) : v}`)
  }
  return parts.join(' ') || JSON.stringify(d)
}

function lineSubtotal(line) {
  if (!line) return 0
  return Math.round(Number(line.quantity) * Number(line.unit_price))
}

function lineTaxAmount(line) {
  let tax = 0
  const sub = lineSubtotal(line)
  for (const lt of line.line_taxes || []) {
    const r = Number(lt.rate_percent)
    if (Number.isFinite(r)) tax += Math.round(sub * (r / 100))
  }
  return tax
}

function orderComputedTotal(order) {
  const lines = order?.lines
  if (!lines?.length) return 0
  let total = 0
  for (const line of lines) {
    total += lineSubtotal(line) + lineTaxAmount(line)
  }
  return total
}

const draftOrderTotals = computed(() => {
  const lines = draftResult.value?.lines
  if (!lines?.length) return { sub: 0, tax: 0, total: 0 }
  let sub = 0
  let tax = 0
  for (const line of lines) {
    sub += lineSubtotal(line)
    tax += lineTaxAmount(line)
  }
  return { sub, tax, total: sub + tax }
})

const summaryDisplaySub = computed(() =>
  draftResult.value?.lines?.length ? draftOrderTotals.value.sub : subtotal.value,
)
const summaryDisplayTax = computed(() =>
  draftResult.value?.lines?.length ? draftOrderTotals.value.tax : taxAmount.value,
)
const summaryDisplayGrand = computed(() =>
  draftResult.value?.lines?.length ? draftOrderTotals.value.total : grandTotal.value,
)
const summaryDisplayTaxLabel = computed(() =>
  draftResult.value?.lines?.length ? 'Tax' : summaryTaxLabel.value,
)

function clearDraftFieldErrors() {
  transactionErr.value = ''
  partnerIdErr.value = ''
  projectIdErr.value = ''
  productCategoryErr.value = ''
  productErr.value = ''
  quantityErr.value = ''
  unitPriceErr.value = ''
  uomErr.value = ''
}

function resetLineFormFields() {
  draftTaxIds.value = []
  skipCategoryWatch.value = true
  selectedCategoryId.value = ''
  selectedProductId.value = ''
  products.value = []
  quantity.value = 1
  unitPriceStr.value = ''
  applyPpn.value = false
  selectedTaxIds.value = []
  nextTick(() => {
    skipCategoryWatch.value = false
  })
}

function setAppendMode(next) {
  if (next === false) {
    const ok = confirm(REPLACE_CONFIRM_TEXT)
    appendMode.value = ok ? false : true
    return
  }
  appendMode.value = true
}

async function saveDraft() {
  confirmHint.value = ''
  saveDraftApiErr.value = ''
  partnerNotice.value = ''
  clearDraftFieldErrors()

  if (draftResult.value?.state === 'confirmed' || draftResult.value?.state === 'paid') {
    saveDraftApiErr.value = "Can't save this order as a draft anymore."
    return
  }

  const t = transactionAt.value
  if (!(t instanceof Date) || Number.isNaN(t.getTime())) {
    transactionErr.value = 'Pick a date and time.'
    return
  }

  if (isNonRetail.value) {
    if (!selectedPartnerId.value) {
      partnerIdErr.value = 'Pick a customer.'
      return
    }
    if (!selectedProjectId.value) {
      projectIdErr.value = 'Pick a project.'
      return
    }
  }

  if (selectedCategoryId.value === '') {
    productCategoryErr.value = 'Pick a product category.'
    return
  }
  if (selectedProductId.value === '') {
    productErr.value = 'Pick a product.'
    return
  }

  const qtyVal = parsedQuantity()
  if (qtyVal == null || qtyVal <= 0) {
    quantityErr.value = 'Use a positive quantity.'
    return
  }

  const unitPriceVal = parsedUnitPrice()
  if (unitPriceVal == null) {
    unitPriceErr.value = 'Add a unit price.'
    return
  }
  if (unitPriceVal < 0) {
    unitPriceErr.value = "Unit price can't be negative."
    return
  }

  const prodId = Number(selectedProductId.value)
  const prod = selectedProduct.value

  if (prod?.uom_id == null) {
    uomErr.value = 'This product has no UOM on file.'
    return
  }
  if (!uomDisplay.value) {
    uomErr.value = 'UOM missing.'
    return
  }

  if (applyPpn.value && selectedTaxes.value.length === 0 && draftTaxIds.value.length === 0) {
    saveDraftApiErr.value = isNonRetail.value
      ? 'Tax is on but we have no tax rows loaded.'
      : 'PPN is on but no PPN tax came from master.'
    return
  }

  const taxIds =
    draftTaxIds.value.length > 0
      ? [...draftTaxIds.value]
      : isNonRetail.value
        ? (selectedTaxIds.value || []).map((v) => Number(v)).filter((v) => Number.isFinite(v) && v > 0)
        : ppnTax.value?.id
          ? [Number(ppnTax.value.id)]
          : []
  const body = {
    transaction_at: t.toISOString(),
    product_id: prodId,
    quantity: qtyVal,
    unit_price: unitPriceVal,
    apply_ppn: applyPpn.value,
    ppn_tax_id: applyPpn.value && taxIds.length > 0 ? taxIds[0] : null,
    tax_ids: applyPpn.value ? taxIds : [],
  }
  if (draftResult.value?.id) {
    body.sales_order_id = draftResult.value.id
    body.append_line = appendMode.value
    if (editingLineId.value != null) {
      body.sales_order_line_id = editingLineId.value
    }
  }
  if (isRestaurant.value) {
    body.table = tableRef.value.trim()
  }
  if (isCustomerMaintained.value) {
    body.partner_name = partnerName.value.trim()
    body.partner_phone = partnerPhone.value.trim()
  }
  if (isNonRetail.value) {
    body.partner_id = Number(selectedPartnerId.value)
    body.project_id = Number(selectedProjectId.value)
    body.order_type = isDeliveryOrder.value ? 'delivery_order' : 'non_retail'
  }

  saveDraftSaving.value = true
  try {
    const { data } = await api.post(saveDraftEndpoint.value, body)
    draftResult.value = data
    partnerNotice.value = data?.customer_notice || ''
    const lines = data?.lines
    const lastLine = lines?.length ? lines[lines.length - 1] : null
    draftTaxIds.value = (lastLine?.line_taxes || [])
      .map((lt) => Number(lt.tax_id))
      .filter((v) => Number.isFinite(v) && v > 0)
    editingLineId.value = null
    lineFormLocked.value = true
  } catch (e) {
    saveDraftApiErr.value = formatApiError(e)
  } finally {
    saveDraftSaving.value = false
  }
}

async function confirmSale() {
  confirmHint.value = ''
  const id = draftResult.value?.id
  if (!id) {
    confirmHint.value = 'Save a draft first, then hit confirm.'
    return
  }
  if (draftResult.value?.state !== 'draft') {
    confirmHint.value = "This isn't a draft anymore."
    return
  }
  confirmSaving.value = true
  try {
    const { data } = await api.post(`/sales-orders/${id}/confirm/`, {})
    draftResult.value = data
    confirmHint.value = `Order #${id} confirmed. Total ${formatIdr(orderComputedTotal(data))}.`
  } catch (e) {
    confirmHint.value = formatApiError(e)
  } finally {
    confirmSaving.value = false
  }
}

async function reopenSale() {
  confirmHint.value = ''
  const id = draftResult.value?.id
  if (!id) return
  if (draftResult.value?.state !== 'confirmed') {
    confirmHint.value = 'Only confirmed orders can go back to draft.'
    return
  }
  const label = draftResult.value?.code || `#${id}`
  const ok = confirm(`Reopen ${label} as a draft?`)
  if (!ok) return
  reopenSaving.value = true
  try {
    const { data } = await api.post(`/sales-orders/${id}/reopen/`, {})
    draftResult.value = data
    lineFormLocked.value = true
    confirmHint.value = `Order #${id} reopened as draft.`
  } catch (e) {
    confirmHint.value = formatApiError(e)
  } finally {
    reopenSaving.value = false
  }
}

function newSalesOrder() {
  confirmHint.value = ''
  saveDraftApiErr.value = ''
  partnerNotice.value = ''
  draftResult.value = null
  editingLineId.value = null
  lineFormLocked.value = false
  draftTaxIds.value = []
  transactionAt.value = new Date()
  skipCategoryWatch.value = true
  selectedCategoryId.value = ''
  selectedProductId.value = ''
  products.value = []
  quantity.value = 1
  unitPriceStr.value = ''
  applyPpn.value = false
  selectedTaxIds.value = []
  tableRef.value = ''
  partnerName.value = ''
  partnerPhone.value = ''
  selectedPartnerId.value = ''
  selectedProjectId.value = ''
  projects.value = []
  appendMode.value = true
  nextTick(() => {
    skipCategoryWatch.value = false
  })
}

async function startEditLine(line) {
  if (!draftResult.value || draftResult.value.state !== 'draft') return
  const catId = line.product_category_id
  skipCategoryWatch.value = true
  selectedProductId.value = ''
  products.value = []
  selectedCategoryId.value = catId != null && catId !== '' ? String(catId) : ''
  await loadProductsForCategory(selectedCategoryId.value)
  await nextTick()
  selectedProductId.value = String(line.product_id)
  quantity.value = Number(line.quantity)
  unitPriceStr.value = line.unit_price != null ? String(line.unit_price) : ''
  const taxes = line.line_taxes
  applyPpn.value = Boolean(taxes?.length)
  if (isNonRetail.value) {
    selectedTaxIds.value = (taxes || [])
      .map((lt) => String(lt.tax_id))
      .filter((v) => v && v !== 'undefined' && v !== 'null')
  }
  draftTaxIds.value = (taxes || [])
    .map((lt) => Number(lt.tax_id))
    .filter((v) => Number.isFinite(v) && v > 0)
  editingLineId.value = line.id
  lineFormLocked.value = false
  skipCategoryWatch.value = false
}

async function startAddItem() {
  if (isNonRetail.value && draftResult.value) {
    const partnerId = draftResult.value.partner?.id
    const projectId = draftResult.value.project_id
    if (partnerId != null) {
      selectedPartnerId.value = String(partnerId)
      // Keep project options in sync with selected customer.
      await loadProjectsForPartner(selectedPartnerId.value)
    }
    if (projectId != null) {
      selectedProjectId.value = String(projectId)
    }
  }
  editingLineId.value = null
  lineFormLocked.value = false
  resetLineFormFields()
}

async function deleteLine(line) {
  const orderId = draftResult.value?.id
  if (!orderId || draftResult.value?.state !== 'draft') return
  if (!confirm(`Drop "${line.product_name}" from this order?`)) return
  saveDraftApiErr.value = ''
  try {
    const { data } = await api.post(`/sales-orders/${orderId}/delete-line/`, {
      sales_order_line_id: line.id,
    })
    draftResult.value = data
    if (editingLineId.value === line.id) {
      editingLineId.value = null
      resetLineFormFields()
    }
  } catch (e) {
    saveDraftApiErr.value = formatApiError(e)
  }
}
</script>

<template>
  <div class="pos-page stack">
    <section class="card erp-head">
      <p class="erp-kicker">{{ isNonRetail ? 'Sales Workspace' : 'Retail Workspace' }}</p>
      <div class="erp-title-row">
        <h1 class="erp-title">
          {{
            isDeliveryOrder
              ? 'Delivery Order Form'
              : isNonRetail
                ? 'Sales Order Form (Non Retail)'
                : 'Point of Sale'
          }}
        </h1>
        <span class="erp-chip">Fast entry • Accurate totals</span>
      </div>
      <p class="pos-page-subtitle muted">
        Run transactions with a clear layout, explicit validation, and live order totals.
      </p>
    </section>

    <section class="pos-top">
      <div class="card pos-form-card">
        <div class="pos-form-header">
          <div class="pos-form-header-top">
            <h2 class="h2">
              {{
                isDeliveryOrder
                  ? 'Delivery Order Form'
                  : isNonRetail
                    ? 'Sales Order Form (Non Retail)'
                    : 'Point of Sale'
              }}
            </h2>
            <button type="button" class="btn-new-order" @click="newSalesOrder">
              New Sales Order
            </button>
          </div>
        </div>

        <div v-if="configLoading" class="muted">Loading…</div>

        <template v-else>
          <p v-if="configErr" class="error">{{ configErr }}</p>
          <p v-if="catalogErr" class="error">{{ catalogErr }}</p>

          <div class="pos-form-fields stack-tight">
            <section class="pos-section pos-section--header" aria-labelledby="pos-header-title">
              <h3 id="pos-header-title" class="pos-section-title">Header sales order</h3>
              <div class="pos-header-grid" :class="{ 'pos-header-grid--non-retail': isNonRetail }">
                <label class="field grow pos-header-time">
                  <span>Time transaction <abbr class="req" title="Required">*</abbr></span>
                  <input
                    type="text"
                    class="pos-readonly"
                    readonly
                    required
                    aria-required="true"
                    tabindex="-1"
                    :value="formatTransactionDisplay(transactionAt)"
                  />
                </label>
                <template v-if="isNonRetail">
                  <label class="field grow pos-header-customer">
                    <span>Customer <abbr class="req" title="Required">*</abbr></span>
                    <select
                      v-model="selectedPartnerId"
                      required
                      aria-required="true"
                      :disabled="isFormLocked || partnersLoading"
                    >
                      <option value="" disabled>
                        {{ partnersLoading ? 'Loading…' : 'Select corporate customer' }}
                      </option>
                      <option v-for="p in corporatePartners" :key="p.id" :value="String(p.id)">
                        {{ p.name || `#${p.id}` }}
                      </option>
                    </select>
                  </label>
                  <label class="field grow pos-header-project">
                    <span>Project <abbr class="req" title="Required">*</abbr></span>
                    <select
                      v-model="selectedProjectId"
                      required
                      aria-required="true"
                      :disabled="isFormLocked || !selectedPartnerId || projectsLoading"
                    >
                      <option value="" disabled>
                        {{
                          !selectedPartnerId
                            ? 'Select customer first'
                            : projectsLoading
                              ? 'Loading…'
                              : 'Select project'
                        }}
                      </option>
                      <option v-for="p in projects" :key="p.id" :value="String(p.id)">
                        {{ p.name }}
                      </option>
                    </select>
                  </label>
                </template>
                <template v-else-if="isCustomerMaintained">
                  <label class="field grow">
                    <span>Partner name</span>
                    <input
                      v-model="partnerName"
                      type="text"
                      placeholder="Optional"
                      maxlength="200"
                      :disabled="isFormLocked"
                    />
                  </label>
                  <label class="field grow">
                    <span>Phone</span>
                    <input
                      v-model="partnerPhone"
                      type="text"
                      placeholder="Optional"
                      maxlength="50"
                      :disabled="isFormLocked"
                    />
                  </label>
                  <p v-if="partnerNotice" class="pos-customer-notice muted small">
                    {{ partnerNotice }}
                  </p>
                </template>
                <label v-if="isRestaurant && !isNonRetail" class="field grow pos-header-table">
                  <span>Table <span class="optional-hint">(optional)</span></span>
                  <input
                    v-model="tableRef"
                    type="text"
                    placeholder="e.g. 1, 2, etc"
                    maxlength="50"
                    :disabled="isFormLocked"
                  />
                </label>
              </div>
              <p v-if="partnerLoadErr" class="error field-error">{{ partnerLoadErr }}</p>
              <p v-if="projectLoadErr" class="error field-error">{{ projectLoadErr }}</p>
              <p v-if="partnerIdErr" class="error field-error">{{ partnerIdErr }}</p>
              <p v-if="projectIdErr" class="error field-error">{{ projectIdErr }}</p>
              <p v-if="transactionErr" class="error field-error">{{ transactionErr }}</p>
            </section>

            <section class="pos-section pos-section--lines" aria-labelledby="pos-lines-title">
              <h3 id="pos-lines-title" class="pos-section-title">Line item &amp; tax</h3>
              <div class="pos-catalog-grid" :class="{ 'pos-catalog-grid--non-retail': isNonRetail }">
                <label class="field grow pos-grid-cat">
                  <span>Product category <abbr class="req" title="Required">*</abbr></span>
                  <select
                    v-model="selectedCategoryId"
                    required
                    aria-required="true"
                    :disabled="isFormLocked || categories.length === 0"
                  >
                    <option value="" disabled>Select category</option>
                    <option v-for="c in categories" :key="c.id" :value="String(c.id)">
                      {{ c.name }}
                    </option>
                  </select>
                </label>
                <label class="field grow pos-grid-prod">
                  <span>Product <abbr class="req" title="Required">*</abbr></span>
                  <select
                    v-model="selectedProductId"
                    required
                    aria-required="true"
                    :disabled="isFormLocked || !selectedCategoryId || productsLoading"
                  >
                    <option value="" disabled>{{ productSelectHint }}</option>
                    <option v-for="p in products" :key="p.id" :value="String(p.id)">
                      {{ p.name }}
                    </option>
                  </select>
                </label>
                <div class="pos-grid-qty-row">
                  <label class="field pos-inline-qty">
                    <span>Quantity <abbr class="req" title="Required">*</abbr></span>
                    <input
                      v-model.number="quantity"
                      type="number"
                      min="0.0001"
                      step="any"
                      inputmode="decimal"
                      required
                      aria-required="true"
                      :placeholder="selectedProductId ? '1' : ''"
                      :disabled="isFormLocked || !selectedProductId"
                    />
                  </label>
                  <label class="field pos-inline-uom">
                    <span>UOM <abbr class="req" title="Required">*</abbr></span>
                    <input
                      type="text"
                      class="pos-readonly"
                      readonly
                      tabindex="-1"
                      aria-required="true"
                      :value="selectedProductId ? uomDisplay || '—' : ''"
                      placeholder="—"
                    />
                  </label>
                  <div class="pos-price-ppn-row">
                    <label class="field pos-inline-price">
                      <span>Unit price <abbr class="req" title="Required">*</abbr></span>
                      <input
                        v-model="unitPriceStr"
                        type="number"
                        min="0"
                        step="any"
                        inputmode="decimal"
                        required
                        aria-required="true"
                        placeholder="From product"
                        :disabled="isFormLocked || !selectedProductId"
                      />
                    </label>
                    <label v-if="!isNonRetail" class="field pos-check-ppn">
                      <span>PPN</span>
                      <input
                        v-model="applyPpn"
                        type="checkbox"
                        :disabled="isFormLocked || !selectedProductId || !ppnTax"
                        :title="ppnTax ? String(ppnTax.name) : 'No active PPN tax in master data'"
                      />
                    </label>
                  </div>
                </div>
                <div v-if="isNonRetail" class="field pos-tax-row">
                  <span>Taxes</span>
                  <div class="tax-checkbox-list" :aria-disabled="isFormLocked || !selectedProductId">
                    <label
                      v-for="t in taxOptions"
                      :key="t.id"
                      class="tax-checkbox-item"
                    >
                      <input
                        v-model="selectedTaxIds"
                        type="checkbox"
                        :value="String(t.id)"
                        :disabled="isFormLocked || !selectedProductId || taxOptions.length === 0"
                      />
                      <span>{{ t.name }} ({{ t.rate_percent }}%)</span>
                    </label>
                    <span v-if="taxOptions.length === 0" class="muted small">No taxes found.</span>
                  </div>
                </div>
                <div v-if="!isNonRetail" class="pos-grid-spacer" aria-hidden="true" />
              </div>
              <p v-if="productsErr" class="error field-error">{{ productsErr }}</p>
              <p v-if="productCategoryErr" class="error field-error">{{ productCategoryErr }}</p>
              <p v-if="productErr" class="error field-error">{{ productErr }}</p>
              <p v-if="quantityErr" class="error field-error">{{ quantityErr }}</p>
              <p v-if="unitPriceErr" class="error field-error">{{ unitPriceErr }}</p>
              <p v-if="uomErr" class="error field-error">{{ uomErr }}</p>
              <p v-if="ppnTaxLoadErr" class="error field-error">{{ ppnTaxLoadErr }}</p>
            </section>

            <p v-if="saveDraftApiErr" class="error field-error">{{ saveDraftApiErr }}</p>

            <button
              type="button"
              class="btn-primary btn-draft"
              :disabled="isFormLocked || saveDraftSaving || draftResult?.state === 'confirmed' || draftResult?.state === 'paid'"
              @click="saveDraft"
            >
              {{
                saveDraftSaving ? 'Saving…' : editingLineId != null ? 'Update Item' : 'Save Draft'
              }}
            </button>
            <div
              v-if="draftResult?.id && draftResult?.state === 'draft' && editingLineId == null"
              class="append-mode-wrap"
            >
              <span class="muted small">Save mode:</span>
              <label class="append-mode-opt">
                <input
                  :checked="appendMode === true"
                  type="radio"
                  :disabled="isFormLocked"
                  @change="setAppendMode(true)"
                />
                <span>Append item</span>
              </label>
              <label class="append-mode-opt">
                <input
                  :checked="appendMode === false"
                  type="radio"
                  :disabled="isFormLocked"
                  @change="setAppendMode(false)"
                />
                <span>Replace existing items</span>
              </label>
            </div>
          </div>
        </template>
      </div>

      <aside class="card pos-summary">
        <h3 class="summary-title">Summary</h3>
        <dl class="summary-rows">
          <div class="summary-row">
            <dt>Subtotal</dt>
            <dd>{{ formatIdr(summaryDisplaySub) }}</dd>
          </div>
          <div class="summary-row">
            <dt>{{ summaryDisplayTaxLabel }}</dt>
            <dd>{{ formatIdr(summaryDisplayTax) }}</dd>
          </div>
          <div class="summary-row summary-total">
            <dt>Total</dt>
            <dd>{{ formatIdr(summaryDisplayGrand) }}</dd>
          </div>
        </dl>
        <p v-if="draftResult?.lines?.length" class="muted small summary-draft-note">
          The total above includes all saved lines. New lines are added from the form after
          <strong>Save Draft</strong>.
        </p>
        <button
          type="button"
          class="btn-primary summary-confirm"
          :disabled="confirmSaving || !draftResult || draftResult.state !== 'draft'"
          @click="confirmSale"
        >
          {{ confirmSaving ? 'Confirming…' : 'Confirm' }}
        </button>
        <button
          v-if="draftResult?.state === 'confirmed'"
          type="button"
          class="btn-primary summary-reopen"
          :disabled="reopenSaving"
          @click="reopenSale"
        >
          {{ reopenSaving ? 'Reopening…' : 'Reopen' }}
        </button>
        <p v-if="confirmHint" class="confirm-hint muted small">{{ confirmHint }}</p>
      </aside>
    </section>

    <section class="card pos-draft">
      <div class="draft-title-row">
        <h3 class="draft-title">Current Order</h3>
      </div>
      <div v-if="draftResult?.state === 'draft'" class="add-item-wrap">
        <button type="button" class="btn-add-item" @click="startAddItem">Add Item</button>
      </div>
      <p v-if="!draftResult" class="muted draft-empty">
        No order saved yet. Click <strong>Save Draft</strong> to store it on the server, or
        <strong>New Sales Order</strong> above to start fresh.
      </p>
      <template v-else>
        <div class="draft-order-head">
          <p class="draft-meta muted small">
            <strong>#{{ draftResult.id }}</strong>
            <template v-if="draftResult.code">
              · <span class="draft-code">{{ draftResult.code }}</span>
            </template>
            <span class="draft-state" :class="'draft-state--' + draftResult.state">{{
              draftResult.state
            }}</span>
            ·
            {{
              formatDateTimeIso(
                draftResult.time_transaction || draftResult.updated_at || draftResult.created_at,
                { empty: '' },
              )
            }}
            · total {{ formatIdr(orderComputedTotal(draftResult)) }}
          </p>
          <p v-if="editingLineId != null" class="muted small">Editing item #{{ editingLineId }}</p>
        </div>

        <div v-if="draftResult.lines?.length" class="pos-lines-wrap">
          <table class="pos-lines-table">
            <thead>
              <tr>
                <th scope="col" class="col-idx">#</th>
                <th scope="col">Product</th>
                <th scope="col" class="col-num">Qty</th>
                <th scope="col" class="col-num">Unit Price</th>
                <th scope="col" class="col-num">Line Total</th>
                <th scope="col" class="col-actions"> </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ln, idx) in draftResult.lines" :key="ln.id">
                <td class="col-idx">{{ idx + 1 }}</td>
                <td>{{ ln.product_name || '—' }}</td>
                <td class="col-num">{{ ln.quantity }}</td>
                <td class="col-num">{{ formatIdr(Number(ln.unit_price) || 0) }}</td>
                <td class="col-num">{{ formatIdr(lineSubtotal(ln) + lineTaxAmount(ln)) }}</td>
                <td class="col-actions">
                  <button
                    v-if="draftResult.state === 'draft'"
                    type="button"
                    class="link-btn"
                    @click="startEditLine(ln)"
                  >
                    Edit
                  </button>
                  <button
                    v-if="draftResult.state === 'draft'"
                    type="button"
                    class="link-btn danger"
                    @click="deleteLine(ln)"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="muted small">This order has no lines yet.</p>
      </template>
    </section>
  </div>
</template>

<style scoped>
.pos-page {
  max-width: 1200px;
}

.pos-page-subtitle {
  margin: 0.35rem 0 0;
  font-size: 0.9rem;
}

.stack-tight {
  display: grid;
  gap: 1rem;
}

.pos-top {
  display: grid;
  grid-template-columns: 1fr minmax(240px, 280px);
  gap: 1rem;
  align-items: start;
}

@media (max-width: 900px) {
  .pos-top {
    grid-template-columns: 1fr;
  }
}

.pos-form-card {
  min-width: 0;
}

.pos-form-header {
  margin-bottom: 0;
}

.pos-form-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.pos-form-header-top .h2 {
  margin: 0;
}

.btn-new-order {
  flex-shrink: 0;
  white-space: nowrap;
  border: none;
  border-radius: 10px;
  padding: 0.55rem 1rem;
  background: var(--warn);
  color: #fff;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

.btn-new-order:hover {
  background: var(--warn-hover);
}

.btn-new-order:focus-visible {
  outline: 2px solid var(--warn-focus);
  outline-offset: 2px;
}

.pos-section {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1rem 1.1rem;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.pos-section--lines {
  margin-top: 0.15rem;
}

.pos-section-title {
  margin: 0 0 0.25rem;
  font-size: 0.98rem;
  font-weight: 650;
  color: var(--text);
}

.pos-header-grid {
  display: grid;
  gap: 0.75rem 1rem;
  grid-template-columns: repeat(auto-fit, minmax(12.5rem, 1fr));
  align-items: end;
}

.pos-header-grid .field {
  min-width: 0;
}

.pos-header-grid select,
.pos-header-grid input {
  width: 100%;
}

.pos-header-customer {
  grid-column: 1;
}

.pos-header-project {
  grid-column: 2;
}

.pos-header-grid--non-retail .pos-header-customer,
.pos-header-grid--non-retail .pos-header-project {
  grid-column: auto;
  max-width: 100%;
}

.pos-customer-notice {
  grid-column: 1 / -1;
  margin: -0.2rem 0 0;
}

.pos-header-time {
  grid-column: 1 / -1;
  max-width: min(22rem, 100%);
}

@media (max-width: 640px) {
  .pos-header-customer,
  .pos-header-project {
    grid-column: 1 / -1;
  }
}

.pos-catalog-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 0.75rem 1rem;
  align-items: end;
  min-width: 0;
}

.pos-grid-cat {
  grid-column: 1;
  grid-row: 1;
  min-width: 0;
}

.pos-grid-prod {
  grid-column: 2;
  grid-row: 1;
  min-width: 0;
}

.pos-grid-qty-row {
  grid-column: 1;
  grid-row: 2;
  display: grid;
  grid-template-columns: minmax(10rem, 1fr) minmax(11rem, 1fr);
  grid-template-rows: auto auto;
  gap: 0.65rem 1rem;
  align-items: end;
  align-self: start;
  width: 100%;
  min-width: 0;
}

/* Global .field has min-width: 160px — override in this row */
.pos-grid-qty-row .field {
  min-width: 0;
  margin: 0;
}

.pos-inline-qty {
  grid-column: 1;
  grid-row: 1;
  width: 100%;
}

.pos-inline-qty input {
  width: 100%;
  min-width: 8rem;
  box-sizing: border-box;
}

.pos-inline-uom {
  grid-column: 2;
  grid-row: 1;
  width: 100%;
}

.pos-inline-uom input {
  width: 100%;
  min-width: 9rem;
  box-sizing: border-box;
}

.pos-inline-uom .pos-readonly {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pos-price-ppn-row {
  grid-column: 1 / -1;
  grid-row: 2;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.65rem 1rem;
  align-items: end;
  min-width: 0;
}

.pos-inline-price {
  width: 100%;
  min-width: 0;
}

.pos-inline-price input {
  width: 100%;
  box-sizing: border-box;
}

.pos-check-ppn {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin: 0;
  min-width: 0;
  white-space: nowrap;
}

.pos-check-ppn input[type='checkbox'] {
  width: 1.1rem;
  height: 1.1rem;
  margin: 0;
  align-self: flex-start;
}

.pos-inline-tax {
  width: 100%;
  min-width: 0;
}

.tax-checkbox-list {
  display: grid;
  gap: 0.35rem;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: #fff;
}

.tax-checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.9rem;
}

.tax-checkbox-item input[type='checkbox'] {
  width: 1rem;
  height: 1rem;
  margin: 0;
}

.pos-grid-spacer {
  grid-column: 2;
  grid-row: 2;
}

.pos-catalog-grid--non-retail .pos-grid-qty-row {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1.35fr);
  grid-template-rows: auto;
}

.pos-catalog-grid--non-retail .pos-inline-qty {
  grid-column: 1;
  grid-row: 1;
}

.pos-catalog-grid--non-retail .pos-inline-uom {
  grid-column: 2;
  grid-row: 1;
}

.pos-catalog-grid--non-retail .pos-price-ppn-row {
  grid-column: 3;
  grid-row: 1;
  display: block;
}

.pos-catalog-grid--non-retail .pos-tax-row {
  grid-column: 1 / -1;
  grid-row: 3;
}

@media (max-width: 640px) {
  .pos-catalog-grid {
    grid-template-columns: 1fr;
  }

  .pos-grid-cat,
  .pos-grid-prod,
  .pos-grid-qty-row,
  .pos-grid-spacer {
    grid-column: 1;
  }

  .pos-grid-cat {
    grid-row: 1;
  }

  .pos-grid-prod {
    grid-row: 2;
  }

  .pos-grid-qty-row {
    grid-row: 3;
    max-width: none;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    grid-template-rows: auto auto;
    gap: 0.65rem 0.85rem;
  }

  .pos-inline-qty {
    grid-column: 1;
    grid-row: 1;
  }

  .pos-inline-uom {
    grid-column: 2;
    grid-row: 1;
  }

  .pos-inline-qty input {
    min-width: min(8rem, 100%);
  }

  .pos-inline-uom input {
    min-width: min(9rem, 100%);
  }

  .pos-grid-spacer {
    display: none;
  }
}

.pos-readonly {
  cursor: default;
  color: var(--text);
  background: #f8fafc;
}

.pos-form-fields {
  margin-bottom: 1rem;
}

.btn-draft {
  justify-self: start;
  width: auto;
}

.append-mode-wrap {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
  margin-top: -0.35rem;
}

.append-mode-opt {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.86rem;
}

.append-mode-opt input {
  margin: 0;
}

.pos-summary {
  position: sticky;
  top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
}

.summary-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 650;
}

.summary-rows {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  font-size: 0.92rem;
}

.summary-row dt {
  margin: 0;
  color: var(--muted);
  font-weight: 500;
}

.summary-row dd {
  margin: 0;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.summary-total {
  padding-top: 0.5rem;
  border-top: 1px solid var(--border);
  font-size: 1.05rem;
}

.summary-total dt {
  color: var(--text);
}

.summary-confirm {
  width: 100%;
}

.summary-reopen {
  width: 100%;
}

.confirm-hint {
  margin: 0;
}

.pos-draft {
  min-height: 120px;
}

.draft-title {
  margin: 0 0 0.75rem;
  font-size: 1rem;
  font-weight: 650;
}

.draft-title-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.draft-title-row .draft-title {
  margin: 0;
}

.add-item-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.btn-add-item {
  border: none;
  border-radius: 10px;
  padding: 0.45rem 0.9rem;
  background: var(--warn);
  color: #fff;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.btn-add-item:hover {
  background: var(--warn-hover);
}

.draft-empty {
  margin: 0;
}

.draft-meta {
  margin: 0 0 0.75rem;
}

.draft-state {
  display: inline-flex;
  align-items: center;
  margin-left: 0.35rem;
  padding: 0.2rem 0.52rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 650;
  border: 1px solid transparent;
}

.draft-state--draft {
  background: #dbeafe;
  color: #1d4ed8;
  border-color: #bfdbfe;
}

.draft-state--confirmed {
  background: #dcfce7;
  color: #15803d;
  border-color: #bbf7d0;
}

.draft-state--void {
  background: #f1f5f9;
  color: #64748b;
  border-color: #e2e8f0;
}

.draft-state--paid {
  background: #d1fae5;
  color: #166534;
  border-color: #a7f3d0;
}

.draft-code {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  color: var(--text, inherit);
}

.draft-order-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.draft-order-head .draft-meta {
  margin: 0;
  flex: 1;
  min-width: 0;
}

.summary-draft-note {
  margin: 0.5rem 0 0;
  font-size: 0.8rem;
}

.pos-lines-wrap {
  overflow-x: auto;
}

.pos-lines-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}

.pos-lines-table th,
.pos-lines-table td {
  padding: 0.45rem 0.6rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.pos-lines-table th {
  font-weight: 650;
  color: var(--muted);
  font-size: 0.8rem;
  background: #fbfdff;
}

.pos-lines-table tbody tr:hover {
  background: #f8fbff;
}

.pos-lines-table .col-num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.pos-lines-table .col-idx {
  width: 2rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

.pos-lines-table .col-actions {
  width: 1%;
  white-space: nowrap;
  text-align: right;
}

.error {
  margin: 0 0 1rem;
}

.field-error {
  margin: -0.5rem 0 0;
  font-size: 0.88rem;
}

.req {
  color: var(--danger);
  text-decoration: none;
  font-weight: 700;
  cursor: help;
}

.optional-hint {
  font-weight: 400;
  color: var(--muted);
  font-size: 0.85em;
}
</style>
