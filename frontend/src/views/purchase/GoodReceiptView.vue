<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../../api/client'
import { fetchAllPages } from '../../utils/fetchAllPages'
import { formatDateTimeIso } from '../../utils/format'

const route = useRoute()
const router = useRouter()

const poOptions = ref([])
const poLoading = ref(false)
const poErr = ref('')

const selectedPoId = ref('')
const poDetail = ref(null)
const lineOptions = computed(() => poDetail.value?.lines || [])

const selectedLineId = ref('')
const quantityReceived = ref('')
const receivedAt = ref(new Date().toISOString().slice(0, 16))
const selectedLine = computed(
  () => lineOptions.value.find((ln) => ln.id === Number(selectedLineId.value)) || null,
)
const orderedQuantityDisplay = computed(() => {
  if (!selectedLine.value) return ''
  return String(selectedLine.value.quantity ?? '')
})
const outstandingQuantityDisplay = computed(() => {
  if (!selectedLine.value) return ''
  const ordered = Number(selectedLine.value.quantity)
  if (!Number.isFinite(ordered)) return ''
  const receivedTotal = receiptRows.value
    .filter((r) => r.purchase_order_line_id === Number(selectedLineId.value))
    .reduce((acc, r) => acc + Number(r.quantity_received || 0), 0)
  const outstanding = ordered - receivedTotal
  return String(Math.max(0, outstanding))
})
const outstandingQuantityValue = computed(() => {
  const n = Number(outstandingQuantityDisplay.value)
  return Number.isFinite(n) ? n : null
})
const isReceivedExceedsOutstanding = computed(() => {
  const qty = Number(quantityReceived.value)
  const outstanding = outstandingQuantityValue.value
  if (!Number.isFinite(qty) || outstanding == null) return false
  return qty > outstanding
})

const saveLoading = ref(false)
const formErr = ref('')
const hint = ref('')
const editingReceiptId = ref(null)
const editingReceiptState = ref('')

const receiptRows = ref([])
const receiptLoading = ref(false)
const deletingId = ref(null)

function truncateVendorName(name, max = 15) {
  const s = String(name || '').trim()
  if (s.length <= max) return s || 'Vendor'
  return `${s.slice(0, max)}...`
}

function formatDateOnlyIso(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium' }).format(new Date(iso))
  } catch {
    return String(iso)
  }
}

async function loadPurchaseOrders() {
  poLoading.value = true
  poErr.value = ''
  try {
    const rows = await fetchAllPages('/purchase-orders/')
    poOptions.value = rows.filter((r) => r.state === 'confirmed' || r.state === 'received')
  } catch (e) {
    poErr.value = e.response?.data?.detail || e.message || 'Failed to load purchase orders.'
    poOptions.value = []
  } finally {
    poLoading.value = false
  }
}

async function loadPoDetail(id) {
  poDetail.value = null
  selectedLineId.value = ''
  if (!id) return
  try {
    const { data } = await api.get(`/purchase-orders/${id}/`)
    poDetail.value = data
  } catch (e) {
    formErr.value = e.response?.data?.detail || e.message || 'Failed to load purchase order detail.'
  }
}

async function loadReceipts() {
  receiptRows.value = []
  if (!selectedPoId.value) return
  receiptLoading.value = true
  try {
    receiptRows.value = await fetchAllPages('/receiving-orders/', {
      purchase_order_id: Number(selectedPoId.value),
    })
  } catch (e) {
    formErr.value = e.response?.data?.detail || e.message || 'Failed to load receiving orders.'
  } finally {
    receiptLoading.value = false
  }
}

async function saveReceipt() {
  formErr.value = ''
  hint.value = ''
  if (editingReceiptId.value != null && editingReceiptState.value !== 'draft') {
    formErr.value = 'Only draft receiving orders can be edited.'
    return
  }
  if (!selectedPoId.value) {
    formErr.value = 'Purchase order is required.'
    return
  }
  if (!selectedLineId.value) {
    formErr.value = 'Purchase order line is required.'
    return
  }
  const qty = Number(quantityReceived.value)
  if (!Number.isFinite(qty) || qty <= 0) {
    formErr.value = 'Quantity received must be greater than zero.'
    return
  }
  if (outstandingQuantityValue.value != null && qty > outstandingQuantityValue.value) {
    formErr.value = 'Invalid Quantity: Exceeds PO Balance.'
    return
  }
  if (!receivedAt.value) {
    formErr.value = 'Received date is required.'
    return
  }
  saveLoading.value = true
  try {
    const body = {
      purchase_order_line_id: Number(selectedLineId.value),
      quantity_received: qty,
      received_date: new Date(receivedAt.value).toISOString(),
    }
    if (editingReceiptId.value != null) {
      await api.patch(`/receiving-orders/${editingReceiptId.value}/`, body)
      hint.value = 'Good receipt draft updated.'
    } else {
      await api.post('/receiving-orders/', body)
      hint.value = 'Good receipt draft saved.'
    }
    quantityReceived.value = ''
    editingReceiptId.value = null
    editingReceiptState.value = ''
    await router.replace({ query: {} })
    await loadReceipts()
  } catch (e) {
    formErr.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && e.response?.data != null
        ? JSON.stringify(e.response.data)
        : null) ||
      e.message ||
      'Failed to save good receipt.'
  } finally {
    saveLoading.value = false
  }
}

async function loadReceiptForEdit(rawId) {
  if (rawId == null || rawId === '') {
    editingReceiptId.value = null
    editingReceiptState.value = ''
    return
  }
  const id = Number(rawId)
  if (!Number.isFinite(id)) return
  formErr.value = ''
  try {
    const { data } = await api.get(`/receiving-orders/${id}/`)
    editingReceiptId.value = data.id
    editingReceiptState.value = data.state || ''
    selectedPoId.value = String(data.purchase_order_id)
    await loadPoDetail(selectedPoId.value)
    await loadReceipts()
    selectedLineId.value = String(data.purchase_order_line_id)
    quantityReceived.value = String(data.quantity_received ?? '')
    const dt = new Date(data.received_date)
    receivedAt.value = Number.isNaN(dt.getTime())
      ? new Date().toISOString().slice(0, 16)
      : new Date(dt.getTime() - dt.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
  } catch (e) {
    formErr.value = e.response?.data?.detail || e.message || 'Failed to load receiving draft.'
  }
}

async function removeReceipt(row) {
  if (!confirm(`Delete receiving #${row.id}?`)) return
  deletingId.value = row.id
  formErr.value = ''
  hint.value = ''
  try {
    await api.delete(`/receiving-orders/${row.id}/`)
    await loadReceipts()
  } catch (e) {
    formErr.value = e.response?.data?.detail || e.message || 'Failed to delete receiving.'
  } finally {
    deletingId.value = null
  }
}

watch(selectedPoId, async (id) => {
  formErr.value = ''
  hint.value = ''
  await loadPoDetail(id)
  await loadReceipts()
})

watch(
  () => route.query.receiptId,
  async (rawId) => {
    await loadReceiptForEdit(rawId)
  },
)

onMounted(async () => {
  await loadPurchaseOrders()
  await loadReceiptForEdit(route.query.receiptId)
})
</script>

<template>
  <div class="stack good-receipt-page">
    <h2 class="h2">Good Receipt</h2>
    <p class="muted">Post Goods Receipt by PO Line</p>

    <section class="card stack">
      <h3 class="section-title">Form</h3>
      <p v-if="poErr" class="error">{{ poErr }}</p>
      <div class="form-grid">
        <label class="field">
          <span>Purchase Order <abbr class="req" title="Required">*</abbr></span>
          <select v-model="selectedPoId" :disabled="poLoading">
            <option value="">Select purchase order</option>
            <option v-for="po in poOptions" :key="po.id" :value="String(po.id)">
              {{
                `${po.code || `#${po.id}`} - ${truncateVendorName(po.vendor_name)} - ${formatDateOnlyIso(po.time_transaction)}`
              }}
            </option>
          </select>
        </label>
        <label class="field">
          <span>Ordered Quantity</span>
          <input :value="orderedQuantityDisplay" type="text" readonly class="input-readonly" />
        </label>
        <label class="field">
          <span>PO Line (Product) <abbr class="req" title="Required">*</abbr></span>
          <select v-model="selectedLineId" :disabled="!selectedPoId || lineOptions.length === 0">
            <option value="">Select line</option>
            <option v-for="ln in lineOptions" :key="ln.id" :value="String(ln.id)">
              {{ ln.product_name }} (Qty PO: {{ ln.quantity }})
            </option>
          </select>
        </label>
        <label class="field">
          <span>Outstanding Quantity</span>
          <input :value="outstandingQuantityDisplay" type="text" readonly class="input-readonly" />
        </label>
        <label
          class="field"
          :title="isReceivedExceedsOutstanding ? 'Invalid Quantity: Exceeds PO Balance.' : ''"
        >
          <span>Quantity Received <abbr class="req" title="Required">*</abbr></span>
          <input
            v-model="quantityReceived"
            type="number"
            min="0.01"
            step="any"
            :max="outstandingQuantityValue ?? undefined"
            :title="isReceivedExceedsOutstanding ? 'Invalid Quantity: Exceeds PO Balance.' : ''"
            :class="{ 'input-invalid': isReceivedExceedsOutstanding }"
          />
          <small
            v-if="isReceivedExceedsOutstanding"
            class="error small"
            title="Invalid Quantity: Exceeds PO Balance."
          >
            Invalid Quantity: Exceeds PO Balance.
          </small>
        </label>
        <label class="field">
          <span>Received Date <abbr class="req" title="Required">*</abbr></span>
          <input v-model="receivedAt" type="datetime-local" />
        </label>
      </div>
      <p v-if="formErr" class="error">{{ formErr }}</p>
      <p v-if="hint" class="muted small">{{ hint }}</p>
      <button type="button" class="btn-primary btn-save" :disabled="saveLoading" @click="saveReceipt">
        {{ saveLoading ? 'Saving…' : 'Save Draft' }}
      </button>
    </section>

    <section class="card stack">
      <h3 class="section-title">Receiving List</h3>
      <div v-if="receiptLoading" class="muted">Loading…</div>
      <p v-else-if="!selectedPoId" class="muted">Select purchase order first.</p>
      <p v-else-if="receiptRows.length === 0" class="muted">No receiving data yet.</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Product</th>
              <th class="col-num">Qty Received</th>
              <th>Received Date</th>
              <th>State</th>
              <th class="col-actions"> </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in receiptRows" :key="row.id">
              <td>{{ row.code || `#${row.id}` }}</td>
              <td>{{ row.product_name || '—' }}</td>
              <td class="col-num">{{ row.quantity_received }}</td>
              <td>{{ formatDateTimeIso(row.received_date) }}</td>
              <td>{{ row.state || '—' }}</td>
              <td class="col-actions">
                <button
                  type="button"
                  class="link-btn danger"
                  :disabled="deletingId === row.id"
                  @click="removeReceipt(row)"
                >
                  {{ deletingId === row.id ? '…' : 'Delete' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.good-receipt-page { max-width: 1100px; }
.section-title { margin: 0; font-size: 1rem; font-weight: 650; }
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem 1rem;
}
.field-wide { grid-column: 1 / -1; }
.btn-save { justify-self: start; width: auto; }
.table-wrap { overflow-x: auto; }
.input-readonly { cursor: default; background: #f8fafc; color: var(--text); }
.input-invalid { border-color: var(--danger, #dc2626); }
.col-num { text-align: right; font-variant-numeric: tabular-nums; }
.col-actions { text-align: right; white-space: nowrap; }
.req { color: var(--danger); text-decoration: none; font-weight: 700; cursor: help; }
@media (max-width: 800px) {
  .form-grid { grid-template-columns: 1fr; }
  .field-wide { grid-column: auto; }
}
</style>
