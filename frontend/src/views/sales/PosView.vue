<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../../api/client'
import { fetchAllPages } from '../../utils/fetchAllPages'
import { formatDateTimeIso, formatIdr, formatTransactionDisplay } from '../../utils/format'

const route = useRoute()

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

const draftResult = ref(null)
const saveDraftSaving = ref(false)
const saveDraftApiErr = ref('')
const confirmHint = ref('')
const partnerNotice = ref('')
const confirmSaving = ref(false)
const reopenSaving = ref(false)
const appendMode = ref(true)
const REPLACE_CONFIRM_TEXT = 'Are you sure to replace the existing items?'
const transactionErr = ref('')
const productCategoryErr = ref('')
const productErr = ref('')
const quantityErr = ref('')
const unitPriceErr = ref('')
const uomErr = ref('')

const ppnTax = ref(null)
const ppnTaxLoadErr = ref('')
const applyPpn = ref(false)
/** When loading a draft for edit, use tax_id from line; otherwise null → use ppnTax from master. */
const draftPpnTaxId = ref(null)
const skipCategoryWatch = ref(false)
const configReady = ref(false)
const editingLineId = ref(null)
const lineFormLocked = ref(false)
const isFormLocked = computed(() => Boolean(draftResult.value?.id) && lineFormLocked.value)

const ppnRateFraction = computed(() => {
  const t = ppnTax.value
  if (!t || t.rate_percent == null || t.rate_percent === '') return 0
  const n = Number(t.rate_percent)
  if (!Number.isFinite(n) || n < 0) return 0
  return n / 100
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
  const r = ppnRateFraction.value
  if (r <= 0) return 0
  return Math.round(subtotal.value * r)
})

const grandTotal = computed(() => subtotal.value + taxAmount.value)

const summaryTaxLabel = computed(() => {
  if (!applyPpn.value || !ppnTax.value) return 'PPN'
  const name = String(ppnTax.value.name ?? '').trim()
  const pct = ppnTax.value.rate_percent
  if (name && pct != null && pct !== '') return `${name} (${pct}%)`
  return name || 'PPN'
})

watch(ppnTax, (t) => {
  if (!t) applyPpn.value = false
})

async function loadProductsForCategory(categoryIdStr) {
  productsErr.value = ''
  if (!categoryIdStr) {
    products.value = []
    return
  }
  productsLoading.value = true
  try {
    products.value = await fetchAllPages('/products/', {
      product_category_id: categoryIdStr,
      product_types: 'storable,consumable',
    })
  } catch {
    productsErr.value = 'Failed to load products for this category.'
    products.value = []
  } finally {
    productsLoading.value = false
  }
}

watch(selectedCategoryId, async (id) => {
  if (skipCategoryWatch.value) return
  draftPpnTaxId.value = null
  selectedProductId.value = ''
  products.value = []
  if (id === '' || id == null) return
  await loadProductsForCategory(id)
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
    configErr.value = 'Failed to load main configuration.'
    isRestaurant.value = false
    isCustomerMaintained.value = false
  }

  try {
    categories.value = await fetchAllPages('/product-categories/')
  } catch {
    catalogErr.value = 'Failed to load product categories.'
    categories.value = []
  }

  ppnTaxLoadErr.value = ''
  try {
    const taxes = await fetchAllPages('/taxes/', { name_ilike: 'ppn' })
    ppnTax.value = taxes[0] ?? null
  } catch {
    ppnTaxLoadErr.value = 'Failed to load PPN tax from master.'
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
    applyOrderHeaderToForm(o)
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
  productCategoryErr.value = ''
  productErr.value = ''
  quantityErr.value = ''
  unitPriceErr.value = ''
  uomErr.value = ''
}

function resetLineFormFields() {
  draftPpnTaxId.value = null
  skipCategoryWatch.value = true
  selectedCategoryId.value = ''
  selectedProductId.value = ''
  products.value = []
  quantity.value = 1
  unitPriceStr.value = ''
  applyPpn.value = false
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
    saveDraftApiErr.value = 'This order cannot be saved as draft.'
    return
  }

  const t = transactionAt.value
  if (!(t instanceof Date) || Number.isNaN(t.getTime())) {
    transactionErr.value = 'Time transaction is required.'
    return
  }

  if (selectedCategoryId.value === '') {
    productCategoryErr.value = 'Product category is required.'
    return
  }
  if (selectedProductId.value === '') {
    productErr.value = 'Product is required.'
    return
  }

  const qtyVal = parsedQuantity()
  if (qtyVal == null || qtyVal <= 0) {
    quantityErr.value = 'Quantity is required (enter a positive number).'
    return
  }

  const unitPriceVal = parsedUnitPrice()
  if (unitPriceVal == null) {
    unitPriceErr.value = 'Unit price is required.'
    return
  }
  if (unitPriceVal < 0) {
    unitPriceErr.value = 'Unit price cannot be negative.'
    return
  }

  const prodId = Number(selectedProductId.value)
  const prod = selectedProduct.value

  if (prod?.uom_id == null) {
    uomErr.value = 'UOM is required (missing on product).'
    return
  }
  if (!uomDisplay.value) {
    uomErr.value = 'UOM is required.'
    return
  }

  if (applyPpn.value && !ppnTax.value && draftPpnTaxId.value == null) {
    saveDraftApiErr.value = 'PPN is checked but no PPN tax is loaded from master.'
    return
  }

  const ppnId =
    draftPpnTaxId.value != null ? draftPpnTaxId.value : ppnTax.value?.id
  const body = {
    transaction_at: t.toISOString(),
    product_id: prodId,
    quantity: qtyVal,
    unit_price: unitPriceVal,
    apply_ppn: applyPpn.value,
    ppn_tax_id: applyPpn.value ? ppnId ?? null : null,
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

  saveDraftSaving.value = true
  try {
    const { data } = await api.post('/pos/save-draft/', body)
    draftResult.value = data
    partnerNotice.value = data?.customer_notice || ''
    const lines = data?.lines
    const lastLine = lines?.length ? lines[lines.length - 1] : null
    const lt = lastLine?.line_taxes?.[0]
    draftPpnTaxId.value = lt?.tax_id != null ? Number(lt.tax_id) : null
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
    confirmHint.value = 'Save a draft first, then confirm.'
    return
  }
  if (draftResult.value?.state !== 'draft') {
    confirmHint.value = 'This order is not a draft.'
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
    confirmHint.value = 'Only confirmed orders can be reopened.'
    return
  }
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
  draftPpnTaxId.value = null
  transactionAt.value = new Date()
  skipCategoryWatch.value = true
  selectedCategoryId.value = ''
  selectedProductId.value = ''
  products.value = []
  quantity.value = 1
  unitPriceStr.value = ''
  applyPpn.value = false
  tableRef.value = ''
  partnerName.value = ''
  partnerPhone.value = ''
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
  draftPpnTaxId.value =
    taxes?.length && taxes[0]?.tax_id != null ? Number(taxes[0].tax_id) : null
  editingLineId.value = line.id
  lineFormLocked.value = false
  skipCategoryWatch.value = false
}

function startAddItem() {
  editingLineId.value = null
  lineFormLocked.value = false
  resetLineFormFields()
}

async function deleteLine(line) {
  const orderId = draftResult.value?.id
  if (!orderId || draftResult.value?.state !== 'draft') return
  if (!confirm(`Delete item "${line.product_name}" from this order?`)) return
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
    <section class="pos-top">
      <div class="card pos-form-card">
        <div class="pos-form-header">
          <div class="pos-form-header-top">
            <h2 class="h2">Point of Sale</h2>
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
              <div class="pos-header-grid">
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
                <template v-if="isCustomerMaintained">
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
                <label v-if="isRestaurant" class="field grow pos-header-table">
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
              <p v-if="transactionErr" class="error field-error">{{ transactionErr }}</p>
            </section>

            <section class="pos-section pos-section--lines" aria-labelledby="pos-lines-title">
              <h3 id="pos-lines-title" class="pos-section-title">Line item &amp; tax</h3>
              <div class="pos-catalog-grid">
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
                    <label class="field pos-check-ppn">
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
                <div class="pos-grid-spacer" aria-hidden="true" />
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
  background: #ea580c;
  color: #fff;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

.btn-new-order:hover {
  background: #c2410c;
}

.btn-new-order:focus-visible {
  outline: 2px solid #9a3412;
  outline-offset: 2px;
}

.pos-section {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 1rem 1.1rem;
  background: var(--card, var(--surface, #fff));
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

.pos-customer-notice {
  grid-column: 1 / -1;
  margin: -0.2rem 0 0;
}

.pos-header-time {
  grid-column: 1 / -1;
  max-width: min(22rem, 100%);
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

.pos-grid-spacer {
  grid-column: 2;
  grid-row: 2;
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
  background: #ea580c;
  color: #fff;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.btn-add-item:hover {
  background: #c2410c;
}

.draft-empty {
  margin: 0;
}

.draft-meta {
  margin: 0 0 0.75rem;
}

.draft-state {
  display: inline-block;
  margin-left: 0.35rem;
  padding: 0.12rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 650;
}

.draft-state--draft {
  background: rgba(80, 110, 200, 0.16);
  color: #2a3f9f;
}

.draft-state--confirmed {
  background: rgba(40, 140, 80, 0.2);
  color: #146632;
}

.draft-state--void {
  background: rgba(120, 120, 120, 0.15);
  color: var(--muted);
}

.draft-state--paid {
  background: rgba(22, 163, 74, 0.2);
  color: #166534;
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

.btn-edit {
  font-size: 0.8rem;
  padding: 0.28rem 0.55rem;
  border-radius: 4px;
  border: 1px solid var(--border);
  background: var(--card, #fff);
  cursor: pointer;
}

.btn-edit:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.05);
}

.btn-edit:disabled {
  opacity: 0.55;
  cursor: not-allowed;
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
