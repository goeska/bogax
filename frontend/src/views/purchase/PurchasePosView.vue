<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../../api/client'
import { fetchAllPages } from '../../utils/fetchAllPages'
import { formatDateTimeIso, formatIdr, formatTransactionDisplay } from '../../utils/format'

const route = useRoute()

const categories = ref([])
const products = ref([])
const selectedCategoryId = ref('')
const selectedProductId = ref('')
const productsLoading = ref(false)
const productsErr = ref('')
const catalogErr = ref('')
const quantity = ref(1)
const unitPriceStr = ref('')
const transactionAt = ref(new Date())
const vendorName = ref('')
const vendorPhone = ref('')
const vendorNotice = ref('')

const draftResult = ref(null)
const saveDraftSaving = ref(false)
const saveDraftApiErr = ref('')
const confirmSaving = ref(false)
const reopenSaving = ref(false)
const confirmHint = ref('')
const appendMode = ref(true)
const REPLACE_CONFIRM_TEXT = 'Are you sure to replace the existing items?'

const transactionErr = ref('')
const productCategoryErr = ref('')
const productErr = ref('')
const quantityErr = ref('')
const unitPriceErr = ref('')
const uomErr = ref('')

const availableTaxes = ref([])
const taxLoadErr = ref('')
const selectedTaxIds = ref([])

const skipCategoryWatch = ref(false)
const configReady = ref(false)
const editingLineId = ref(null)
const lineFormLocked = ref(false)
const isFormLocked = computed(() => Boolean(draftResult.value?.id) && lineFormLocked.value)

const selectedProduct = computed(() => {
  if (!selectedProductId.value) return null
  return products.value.find((p) => p.id === Number(selectedProductId.value)) ?? null
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
  const n = Number(quantity.value)
  return Number.isFinite(n) ? n : null
}
function parsedUnitPrice() {
  const n = Number(String(unitPriceStr.value ?? '').trim())
  return Number.isFinite(n) ? n : null
}
function lineSubtotal(line) {
  return Math.round(Number(line.quantity) * Number(line.unit_price))
}
function lineTaxAmount(line) {
  let total = 0
  const sub = lineSubtotal(line)
  for (const lt of line.line_taxes || []) {
    const r = Number(lt.rate_percent)
    if (Number.isFinite(r)) total += Math.round(sub * (r / 100))
  }
  return total
}
function lineTaxBreakdown(line) {
  const out = []
  const sub = lineSubtotal(line)
  for (const lt of line.line_taxes || []) {
    const r = Number(lt.rate_percent)
    if (!Number.isFinite(r)) continue
    out.push({
      key: `${lt.tax_id}:${lt.tax_name}`,
      label: lt.tax_name || `Tax #${lt.tax_id}`,
      amount: Math.round(sub * (r / 100)),
    })
  }
  return out
}
function orderTotal(order) {
  let total = 0
  for (const ln of order?.lines || []) total += lineSubtotal(ln) + lineTaxAmount(ln)
  return total
}
function selectedTaxBreakdown(subtotal) {
  return selectedTaxIds.value
    .map((id) => availableTaxes.value.find((t) => t.id === id))
    .filter(Boolean)
    .map((t) => {
      const rate = Number(t.rate_percent)
      return {
        key: `selected:${t.id}`,
        label: t.name || `Tax #${t.id}`,
        amount: Number.isFinite(rate) ? Math.round(subtotal * (rate / 100)) : 0,
      }
    })
}
const summaryTotals = computed(() => {
  const lines = draftResult.value?.lines || []
  if (lines.length) {
    let subtotal = 0
    let tax = 0
    for (const ln of lines) {
      subtotal += lineSubtotal(ln)
      tax += lineTaxAmount(ln)
    }
    return { subtotal, tax, total: subtotal + tax }
  }
  const qty = parsedQuantity()
  const up = parsedUnitPrice()
  const subtotal = qty != null && up != null && qty > 0 && up >= 0 ? Math.round(qty * up) : 0
  const tax = selectedTaxBreakdown(subtotal).reduce((acc, t) => acc + t.amount, 0)
  return { subtotal, tax, total: subtotal + tax }
})
const summaryTaxBreakdown = computed(() => {
  const lines = draftResult.value?.lines || []
  if (lines.length) {
    const bucket = new Map()
    for (const ln of lines) {
      for (const item of lineTaxBreakdown(ln)) {
        const prev = bucket.get(item.label) || 0
        bucket.set(item.label, prev + item.amount)
      }
    }
    return Array.from(bucket.entries()).map(([label, amount], idx) => ({
      key: `draft:${idx}:${label}`,
      label,
      amount,
    }))
  }
  return selectedTaxBreakdown(summaryTotals.value.subtotal)
})

async function loadProductsForCategory(id) {
  productsErr.value = ''
  if (!id) {
    products.value = []
    return
  }
  productsLoading.value = true
  try {
    products.value = await fetchAllPages('/products/', {
      product_category_id: id,
      product_types: 'storable,consumable',
    })
  } catch {
    productsErr.value = 'Failed to load products.'
    products.value = []
  } finally {
    productsLoading.value = false
  }
}

watch(selectedCategoryId, async (id) => {
  if (skipCategoryWatch.value) return
  selectedProductId.value = ''
  products.value = []
  if (!id) return
  await loadProductsForCategory(id)
})

watch(
  () => selectedProduct.value,
  (p) => {
    if (!p) {
      unitPriceStr.value = ''
      return
    }
    const n = Number(p.unit_price)
    unitPriceStr.value = Number.isFinite(n) ? String(n) : ''
  },
  { immediate: true },
)

function clearErrors() {
  transactionErr.value = ''
  productCategoryErr.value = ''
  productErr.value = ''
  quantityErr.value = ''
  unitPriceErr.value = ''
  uomErr.value = ''
}

function resetLineFormFields() {
  skipCategoryWatch.value = true
  selectedCategoryId.value = ''
  selectedProductId.value = ''
  products.value = []
  quantity.value = 1
  unitPriceStr.value = ''
  selectedTaxIds.value = []
  nextTick(() => {
    skipCategoryWatch.value = false
  })
}

function newPurchaseOrder() {
  confirmHint.value = ''
  saveDraftApiErr.value = ''
  vendorNotice.value = ''
  draftResult.value = null
  editingLineId.value = null
  lineFormLocked.value = false
  transactionAt.value = new Date()
  vendorName.value = ''
  vendorPhone.value = ''
  appendMode.value = true
  resetLineFormFields()
}

function applyOrderHeader(po) {
  draftResult.value = po
  transactionAt.value = new Date(po.time_transaction)
  vendorName.value = po.vendor_name || ''
  vendorPhone.value = po.vendor_phone || ''
}

async function startEditLine(line) {
  if (!draftResult.value || draftResult.value.state !== 'draft') return
  skipCategoryWatch.value = true
  selectedProductId.value = ''
  products.value = []
  selectedCategoryId.value = String(line.product_category_id)
  await loadProductsForCategory(selectedCategoryId.value)
  await nextTick()
  selectedProductId.value = String(line.product_id)
  quantity.value = Number(line.quantity)
  unitPriceStr.value = String(line.unit_price)
  selectedTaxIds.value = (line.line_taxes || []).map((t) => t.tax_id)
  editingLineId.value = line.id
  lineFormLocked.value = false
  skipCategoryWatch.value = false
}

function startAddItem() {
  editingLineId.value = null
  lineFormLocked.value = false
  resetLineFormFields()
}

function setAppendMode(next) {
  if (next === false) {
    const ok = confirm(REPLACE_CONFIRM_TEXT)
    appendMode.value = ok ? false : true
    return
  }
  appendMode.value = true
}

async function loadOrderFromRoute(raw) {
  if (raw == null || raw === '') {
    newPurchaseOrder()
    return
  }
  const id = Number(raw)
  if (!Number.isFinite(id)) {
    newPurchaseOrder()
    return
  }
  saveDraftApiErr.value = ''
  try {
    const { data } = await api.get(`/purchase-orders/${id}/`)
    applyOrderHeader(data)
    if (data.state === 'draft') {
      startAddItem()
      lineFormLocked.value = true
    } else {
      editingLineId.value = null
      lineFormLocked.value = true
    }
  } catch (e) {
    saveDraftApiErr.value = e.response?.data?.detail || e.message || 'Failed to load order.'
  }
}

async function saveDraft() {
  confirmHint.value = ''
  saveDraftApiErr.value = ''
  vendorNotice.value = ''
  clearErrors()
  if (draftResult.value?.state === 'confirmed') {
    saveDraftApiErr.value = 'Confirmed orders cannot be changed.'
    return
  }
  if (!(transactionAt.value instanceof Date) || Number.isNaN(transactionAt.value.getTime())) {
    transactionErr.value = 'Time transaction is required.'
    return
  }
  if (!selectedCategoryId.value) {
    productCategoryErr.value = 'Product category is required.'
    return
  }
  if (!selectedProductId.value) {
    productErr.value = 'Product is required.'
    return
  }
  const qty = parsedQuantity()
  if (qty == null || qty <= 0) {
    quantityErr.value = 'Quantity is required.'
    return
  }
  const up = parsedUnitPrice()
  if (up == null || up < 0) {
    unitPriceErr.value = 'Unit price is required.'
    return
  }
  if (!uomDisplay.value) {
    uomErr.value = 'UOM is required.'
    return
  }
  saveDraftSaving.value = true
  try {
    const body = {
      transaction_at: transactionAt.value.toISOString(),
      product_id: Number(selectedProductId.value),
      quantity: qty,
      unit_price: up,
      tax_ids: selectedTaxIds.value.slice(),
      vendor_name: vendorName.value.trim(),
      vendor_phone: vendorPhone.value.trim(),
    }
    if (draftResult.value?.id) {
      body.purchase_order_id = draftResult.value.id
      body.append_line = appendMode.value
    }
    if (editingLineId.value != null) body.purchase_order_line_id = editingLineId.value
    const { data } = await api.post('/purchase/pos/save-draft/', body)
    draftResult.value = data
    vendorNotice.value = data?.vendor_notice || ''
    editingLineId.value = null
    lineFormLocked.value = true
  } catch (e) {
    saveDraftApiErr.value = e.response?.data?.detail || JSON.stringify(e.response?.data || '') || e.message
  } finally {
    saveDraftSaving.value = false
  }
}

async function deleteLine(line) {
  const orderId = draftResult.value?.id
  if (!orderId || draftResult.value?.state !== 'draft') return
  if (!confirm(`Delete item "${line.product_name}"?`)) return
  try {
    const { data } = await api.post(`/purchase-orders/${orderId}/delete-line/`, {
      purchase_order_line_id: line.id,
    })
    draftResult.value = data
    if (editingLineId.value === line.id) {
      editingLineId.value = null
      resetLineFormFields()
    }
  } catch (e) {
    saveDraftApiErr.value = e.response?.data?.detail || e.message || 'Failed to delete line.'
  }
}

async function confirmOrder() {
  confirmHint.value = ''
  const id = draftResult.value?.id
  if (!id || draftResult.value?.state !== 'draft') return
  confirmSaving.value = true
  try {
    const { data } = await api.post(`/purchase-orders/${id}/confirm/`, {})
    draftResult.value = data
    confirmHint.value = `Purchase order #${id} confirmed.`
  } catch (e) {
    confirmHint.value = e.response?.data?.detail || e.message || 'Failed to confirm.'
  } finally {
    confirmSaving.value = false
  }
}

async function reopenOrder() {
  confirmHint.value = ''
  const id = draftResult.value?.id
  if (!id || draftResult.value?.state !== 'confirmed') return
  reopenSaving.value = true
  try {
    const { data } = await api.post(`/purchase-orders/${id}/reopen/`, {})
    draftResult.value = data
    lineFormLocked.value = true
    confirmHint.value = `Purchase order #${id} reopened.`
  } catch (e) {
    confirmHint.value = e.response?.data?.detail || e.message || 'Failed to reopen.'
  } finally {
    reopenSaving.value = false
  }
}

onMounted(async () => {
  try {
    categories.value = await fetchAllPages('/product-categories/')
  } catch {
    catalogErr.value = 'Failed to load product categories.'
  }
  try {
    const taxes = await fetchAllPages('/taxes/')
    const allowed = ['ppn', 'pph 21', 'pph21', 'pph 22', 'pph22', 'pph 23', 'pph23']
    availableTaxes.value = taxes.filter((t) =>
      allowed.includes(String(t.name || '').trim().toLowerCase().replace(/\s+/g, ' ')),
    )
  } catch {
    taxLoadErr.value = 'Failed to load purchase taxes.'
  }
  configReady.value = true
  await loadOrderFromRoute(route.query.orderId)
})

watch(
  () => route.query.orderId,
  async (raw) => {
    if (!configReady.value) return
    await loadOrderFromRoute(raw)
  },
)
</script>

<template>
  <div class="purchase-pos-page stack">
    <section class="pos-top">
      <div class="card pos-form-card">
        <div class="pos-form-header-top">
          <h2 class="h2">PO Form</h2>
          <button type="button" class="btn-new-order" @click="newPurchaseOrder">New PO</button>
        </div>

        <p v-if="catalogErr" class="error">{{ catalogErr }}</p>
        <div class="stack-tight">
          <section class="pos-section">
            <h3 class="pos-section-title">Header purchase order</h3>
            <div class="pos-header-grid">
              <label class="field grow pos-header-time">
                <span>Time transaction <abbr class="req" title="Required">*</abbr></span>
                <input type="text" class="pos-readonly" readonly :value="formatTransactionDisplay(transactionAt)" />
              </label>
              <label class="field grow">
                <span>Vendor name</span>
                <input v-model="vendorName" type="text" maxlength="100" :disabled="isFormLocked" />
              </label>
              <label class="field grow">
                <span>Phone</span>
                <input v-model="vendorPhone" type="text" maxlength="50" :disabled="isFormLocked" />
              </label>
              <p v-if="vendorNotice" class="po-vendor-notice muted small">{{ vendorNotice }}</p>
            </div>
            <p v-if="transactionErr" class="error field-error">{{ transactionErr }}</p>
          </section>

          <section class="pos-section">
            <h3 class="pos-section-title">Line item & taxes</h3>
            <div class="pos-catalog-grid">
              <label class="field grow">
                <span>Product category <abbr class="req" title="Required">*</abbr></span>
                <select v-model="selectedCategoryId" :disabled="isFormLocked || categories.length === 0">
                  <option value="" disabled>Select category</option>
                  <option v-for="c in categories" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
                </select>
              </label>
              <label class="field grow">
                <span>Product <abbr class="req" title="Required">*</abbr></span>
                <select v-model="selectedProductId" :disabled="isFormLocked || !selectedCategoryId || productsLoading">
                  <option value="" disabled>{{ productSelectHint }}</option>
                  <option v-for="p in products" :key="p.id" :value="String(p.id)">{{ p.name }}</option>
                </select>
              </label>
              <label class="field">
                <span>Quantity <abbr class="req" title="Required">*</abbr></span>
                <input v-model.number="quantity" type="number" min="0.0001" step="any" :disabled="isFormLocked || !selectedProductId" />
              </label>
              <label class="field">
                <span>UOM</span>
                <input type="text" class="pos-readonly" readonly :value="selectedProductId ? uomDisplay || '—' : ''" />
              </label>
              <label class="field">
                <span>Unit price <abbr class="req" title="Required">*</abbr></span>
                <input v-model="unitPriceStr" type="number" min="0" step="any" :disabled="isFormLocked || !selectedProductId" />
              </label>
            </div>
            <div class="tax-list">
              <span class="muted small">Taxes (PPN/PPH21/22/23)</span>
              <div class="tax-items-grid">
                <label v-for="t in availableTaxes" :key="t.id" class="tax-item">
                  <input
                    v-model="selectedTaxIds"
                    :value="t.id"
                    type="checkbox"
                    :disabled="isFormLocked || !selectedProductId"
                  />
                  <span class="tax-label">{{ t.name }}</span>
                  <span class="tax-rate muted">({{ t.rate_percent }}%)</span>
                </label>
              </div>
            </div>
            <p v-if="taxLoadErr" class="error field-error">{{ taxLoadErr }}</p>
            <p v-if="productsErr" class="error field-error">{{ productsErr }}</p>
            <p v-if="productCategoryErr" class="error field-error">{{ productCategoryErr }}</p>
            <p v-if="productErr" class="error field-error">{{ productErr }}</p>
            <p v-if="quantityErr" class="error field-error">{{ quantityErr }}</p>
            <p v-if="unitPriceErr" class="error field-error">{{ unitPriceErr }}</p>
            <p v-if="uomErr" class="error field-error">{{ uomErr }}</p>
          </section>

          <p v-if="saveDraftApiErr" class="error field-error">{{ saveDraftApiErr }}</p>
          <button
            type="button"
            class="btn-primary btn-draft"
            :disabled="isFormLocked || saveDraftSaving || draftResult?.state === 'confirmed'"
            @click="saveDraft"
          >
            {{ saveDraftSaving ? 'Saving…' : editingLineId != null ? 'Update Item' : 'Save Draft' }}
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
      </div>

      <aside class="card pos-summary">
        <h3 class="summary-title">Summary</h3>
        <div class="summary-row"><span>Subtotal</span><strong>{{ formatIdr(summaryTotals.subtotal) }}</strong></div>
        <div class="summary-row"><span>Tax</span><strong>{{ formatIdr(summaryTotals.tax) }}</strong></div>
        <div v-if="summaryTaxBreakdown.length" class="summary-tax-list">
          <div v-for="tax in summaryTaxBreakdown" :key="tax.key" class="summary-tax-row">
            <span class="muted small">{{ tax.label }}</span>
            <strong class="small">{{ formatIdr(tax.amount) }}</strong>
          </div>
        </div>
        <div class="summary-row summary-total-row">
          <span>Total</span>
          <strong>{{ formatIdr(summaryTotals.total) }}</strong>
        </div>
        <button
          type="button"
          class="btn-primary summary-confirm"
          :disabled="confirmSaving || !draftResult || draftResult.state !== 'draft'"
          @click="confirmOrder"
        >
          {{ confirmSaving ? 'Confirming…' : 'Confirm' }}
        </button>
        <button
          v-if="draftResult?.state === 'confirmed'"
          type="button"
          class="btn-primary summary-reopen"
          :disabled="reopenSaving"
          @click="reopenOrder"
        >
          {{ reopenSaving ? 'Reopening…' : 'Reopen' }}
        </button>
        <p v-if="confirmHint" class="muted small">{{ confirmHint }}</p>
      </aside>
    </section>

    <section class="card">
      <div class="draft-title-row">
        <h3 class="draft-title">Current Purchase Order</h3>
      </div>
      <div v-if="draftResult?.state === 'draft'" class="add-item-wrap">
        <button type="button" class="btn-add-item" @click="startAddItem">Add Item</button>
      </div>
      <p v-if="!draftResult" class="muted">No order saved yet.</p>
      <template v-else>
        <p class="muted small">
          <strong>#{{ draftResult.id }}</strong> · {{ draftResult.code || '—' }} ·
          {{ draftResult.state }} ·
          {{ formatDateTimeIso(draftResult.time_transaction, { empty: '' }) }}
        </p>
        <div class="pos-lines-wrap" v-if="draftResult.lines?.length">
          <table class="pos-lines-table">
            <thead>
              <tr>
                <th>#</th><th>Product</th><th class="col-num">Qty</th><th class="col-num">Unit Price</th><th class="col-num">Line Total</th><th class="col-actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ln, idx) in draftResult.lines" :key="ln.id">
                <td>{{ idx + 1 }}</td>
                <td>{{ ln.product_name }}</td>
                <td class="col-num">{{ ln.quantity }}</td>
                <td class="col-num">{{ formatIdr(ln.unit_price) }}</td>
                <td class="col-num">{{ formatIdr(lineSubtotal(ln) + lineTaxAmount(ln)) }}</td>
                <td class="col-actions">
                  <button v-if="draftResult.state === 'draft'" class="link-btn" @click="startEditLine(ln)">Edit</button>
                  <button v-if="draftResult.state === 'draft'" class="link-btn danger" @click="deleteLine(ln)">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </section>
  </div>
</template>

<style scoped>
.purchase-pos-page { max-width: 1200px; }
.stack-tight { display: grid; gap: 1rem; }
.pos-top { display: grid; grid-template-columns: 1fr minmax(240px, 280px); gap: 1rem; align-items: start; }
@media (max-width: 900px) { .pos-top { grid-template-columns: 1fr; } }
.pos-form-header-top { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; }
.pos-section { border: 1px solid var(--border); border-radius: 10px; padding: 1rem; background: var(--card, #fff); }
.pos-section-title { margin: 0 0 0.5rem; font-size: 0.98rem; font-weight: 650; }
.pos-header-grid { display: grid; gap: 0.75rem 1rem; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: end; }
.pos-header-time { grid-column: 1 / -1; max-width: min(22rem, 100%); }
.pos-header-grid .field { min-width: 0; }
.pos-header-grid .field input { width: 100%; box-sizing: border-box; }
.po-vendor-notice { grid-column: 1 / -1; margin: -0.2rem 0 0; }
.pos-catalog-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem 1rem;
  align-items: end;
}
.pos-catalog-grid .field {
  min-width: 0;
}
.pos-catalog-grid .field input,
.pos-catalog-grid .field select {
  width: 100%;
  box-sizing: border-box;
}
.tax-list {
  display: grid;
  gap: 0.35rem;
  margin-top: 0.6rem;
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card, #fff);
}
.tax-items-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.35rem 0.75rem;
}
.tax-item {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.86rem;
  line-height: 1.2;
  min-width: 0;
}
.tax-item input {
  margin: 0;
}
.tax-label {
  font-weight: 500;
}
.tax-rate {
  white-space: nowrap;
}
.pos-readonly { cursor: default; color: var(--text); background: #f8fafc; }
.btn-new-order, .btn-add-item { border: none; border-radius: 10px; padding: 0.5rem 0.9rem; background: #ea580c; color: #fff; font: inherit; font-weight: 600; cursor: pointer; }
.btn-new-order:hover, .btn-add-item:hover { background: #c2410c; }
.btn-draft { justify-self: start; width: auto; }
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
.pos-summary { position: sticky; top: 0.75rem; display: flex; flex-direction: column; gap: 1rem; }
.summary-title { margin: 0; font-size: 1rem; font-weight: 650; }
.summary-row { display: flex; justify-content: space-between; }
.summary-tax-list {
  display: grid;
  gap: 0.25rem;
  margin: -0.35rem 0 0.2rem;
}
.summary-tax-row {
  display: flex;
  justify-content: space-between;
  gap: 0.6rem;
}
.summary-total-row {
  padding-top: 0.45rem;
  border-top: 1px solid var(--border);
}
.summary-confirm { width: 100%; }
.draft-title-row, .add-item-wrap { display: flex; justify-content: center; margin-bottom: 0.75rem; }
.draft-title { margin: 0; font-size: 1rem; font-weight: 650; }
.pos-lines-wrap { overflow-x: auto; }
.pos-lines-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.pos-lines-table th, .pos-lines-table td { padding: 0.45rem 0.6rem; border-bottom: 1px solid var(--border); }
.pos-lines-table .col-num { text-align: right; font-variant-numeric: tabular-nums; }
.pos-lines-table .col-actions { white-space: nowrap; text-align: right; }
.field-error { margin: 0; font-size: 0.88rem; }
.req { color: var(--danger); text-decoration: none; font-weight: 700; cursor: help; }
@media (max-width: 700px) {
  .pos-header-grid {
    grid-template-columns: 1fr;
  }
  .pos-catalog-grid {
    grid-template-columns: 1fr;
  }
  .tax-items-grid {
    grid-template-columns: 1fr;
  }
}
</style>
