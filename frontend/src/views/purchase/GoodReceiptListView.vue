<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client'
import { fetchAllPages } from '../../utils/fetchAllPages'
import { formatDateTimeIso } from '../../utils/format'
import { buildOrderListParams } from '../../utils/listFilters'
import { usePagination } from '../../utils/pagination'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const deletingId = ref(null)
const confirmingId = ref(null)
const bulkConfirming = ref(false)
const openingEditId = ref(null)
const router = useRouter()
const selectedDraftIds = ref([])
const poOptions = ref([])
const poOptionsLoading = ref(false)

const filterPoCode = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
const filterRoState = ref('')
const lastAppliedHadFilters = ref(false)

const pag = usePagination(25)
const { currentPage, totalCount, totalPages, applyDrfResponse } = pag
const { prevPage, nextPage } = pag.makePager(loading, load)

function filterParams() {
  return {
    purchaseOrderCode: filterPoCode.value || undefined,
    state: filterRoState.value || undefined,
    dateFrom: filterDateFrom.value || undefined,
    dateTo: filterDateTo.value || undefined,
  }
}

async function load(page = 1) {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/receiving-orders/', {
      params: buildOrderListParams(page, filterParams()),
    })
    applyDrfResponse(data, rows, page)
    const draftIdSet = new Set(rows.value.filter((r) => r.state === 'draft').map((r) => r.id))
    selectedDraftIds.value = selectedDraftIds.value.filter((id) => draftIdSet.has(id))
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && e.response?.data != null
        ? JSON.stringify(e.response.data)
        : null) ||
      e.message ||
      'Failed to load good receipts.'
    rows.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

function toggleSelectAllDraftOnPage(checked) {
  if (checked) {
    selectedDraftIds.value = draftRowsOnPage.value.map((r) => r.id)
    return
  }
  selectedDraftIds.value = []
}

function applyFilters() {
  lastAppliedHadFilters.value = Boolean(
    filterPoCode.value || filterDateFrom.value || filterDateTo.value || filterRoState.value,
  )
  load(1)
}

function clearFilters() {
  filterPoCode.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  filterRoState.value = ''
  lastAppliedHadFilters.value = false
  load(1)
}

async function removeRow(row) {
  if (!confirm(`Delete receiving #${row.id}?`)) return
  deletingId.value = row.id
  err.value = ''
  try {
    await api.delete(`/receiving-orders/${row.id}/`)
    await load(currentPage.value)
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && e.response?.data != null
        ? JSON.stringify(e.response.data)
        : null) ||
      e.message ||
      'Failed to delete.'
  } finally {
    deletingId.value = null
  }
}

async function confirmRow(row) {
  confirmingId.value = row.id
  err.value = ''
  try {
    await api.post(`/receiving-orders/${row.id}/confirm/`, {})
    await load(currentPage.value)
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && e.response?.data != null
        ? JSON.stringify(e.response.data)
        : null) ||
      e.message ||
      'Failed to confirm.'
  } finally {
    confirmingId.value = null
  }
}

async function editRow(row) {
  openingEditId.value = row.id
  try {
    await router.push({ name: 'purchase-good-receipt', query: { receiptId: String(row.id) } })
  } finally {
    openingEditId.value = null
  }
}

const hasRows = computed(() => rows.value.length > 0)
const draftRowsOnPage = computed(() => rows.value.filter((r) => r.state === 'draft'))
const allDraftSelectedOnPage = computed(
  () =>
    draftRowsOnPage.value.length > 0 &&
    draftRowsOnPage.value.every((r) => selectedDraftIds.value.includes(r.id)),
)

async function bulkConfirmSelected() {
  if (selectedDraftIds.value.length === 0) return
  if (!confirm(`Confirm ${selectedDraftIds.value.length} selected draft receipts?`)) return
  bulkConfirming.value = true
  err.value = ''
  try {
    const { data } = await api.post('/receiving-orders/bulk-confirm/', {
      ids: selectedDraftIds.value.slice(),
    })
    selectedDraftIds.value = []
    await load(currentPage.value)
    if (data?.confirmed != null) {
      err.value = ''
    }
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && e.response?.data != null
        ? JSON.stringify(e.response.data)
        : null) ||
      e.message ||
      'Failed to bulk confirm.'
  } finally {
    bulkConfirming.value = false
  }
}

onMounted(async () => {
  poOptionsLoading.value = true
  try {
    const pos = await fetchAllPages('/purchase-orders/')
    poOptions.value = pos
      .map((po) => ({ id: po.id, code: po.code || '' }))
      .filter((po) => po.code)
  } catch {
    poOptions.value = []
  } finally {
    poOptionsLoading.value = false
  }
  await load()
})
</script>

<template>
  <div class="stack good-receipt-list-page">
    <h2 class="h2">Good Receipt List</h2>
    <p class="muted lead">List data receiving barang dari table receiving_order.</p>

    <div class="list-filters">
      <label class="filter-field">
        <span>PO Code</span>
        <select v-model="filterPoCode" class="filter-input" :disabled="poOptionsLoading">
          <option value="">All PO codes</option>
          <option v-for="po in poOptions" :key="po.id" :value="po.code">{{ po.code }}</option>
        </select>
      </label>
      <label class="filter-field">
        <span>Start date</span>
        <input v-model="filterDateFrom" type="date" class="filter-input" />
      </label>
      <label class="filter-field">
        <span>End date</span>
        <input v-model="filterDateTo" type="date" class="filter-input" />
      </label>
      <label class="filter-field">
        <span>RO State</span>
        <select v-model="filterRoState" class="filter-input">
          <option value="">All states</option>
          <option value="draft">draft</option>
          <option value="confirmed">confirmed</option>
        </select>
      </label>
      <div class="filter-actions">
        <button type="button" class="btn-edit" @click="applyFilters">Apply</button>
        <button type="button" class="btn-ghost" @click="clearFilters">Clear</button>
        <button
          type="button"
          class="btn-edit btn-confirm-selected"
          :disabled="bulkConfirming || selectedDraftIds.length === 0"
          @click="bulkConfirmSelected"
        >
          {{ bulkConfirming ? 'Confirming…' : `Confirm Selected (${selectedDraftIds.length})` }}
        </button>
      </div>
    </div>

    <p v-if="err" class="error">{{ err }}</p>

    <div v-if="loading" class="muted">Loading…</div>
    <div v-else-if="!hasRows" class="muted">
      {{ lastAppliedHadFilters ? 'No matching receipts.' : 'No good receipt data yet.' }}
    </div>
    <div v-else class="table-wrap">
      <table class="table good-receipt-table">
        <thead>
          <tr>
            <th class="col-check">
              <input
                type="checkbox"
                :checked="allDraftSelectedOnPage"
                :disabled="draftRowsOnPage.length === 0"
                @change="toggleSelectAllDraftOnPage($event.target.checked)"
              />
            </th>
            <th>Code</th>
            <th>PO Code</th>
            <th>Vendor</th>
            <th>Product</th>
            <th class="col-num">Qty Received</th>
            <th>Received Date</th>
            <th>State</th>
            <th class="col-actions"> </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td class="col-check">
              <input
                v-if="row.state === 'draft'"
                v-model="selectedDraftIds"
                type="checkbox"
                :value="row.id"
              />
            </td>
            <td>{{ row.code || `#${row.id}` }}</td>
            <td>{{ row.purchase_order_code || '—' }}</td>
            <td>{{ row.vendor_name || '—' }}</td>
            <td>{{ row.product_name || '—' }}</td>
            <td class="col-num">{{ row.quantity_received }}</td>
            <td>{{ formatDateTimeIso(row.received_date) }}</td>
            <td>{{ row.state || '—' }}</td>
            <td class="col-actions">
              <button
                v-if="row.state === 'draft'"
                type="button"
                class="link-btn"
                :disabled="openingEditId === row.id"
                @click="editRow(row)"
              >
                {{ openingEditId === row.id ? '…' : 'Edit' }}
              </button>
              <button
                v-if="row.state === 'draft'"
                type="button"
                class="link-btn"
                :disabled="confirmingId === row.id"
                @click="confirmRow(row)"
              >
                {{ confirmingId === row.id ? '…' : 'Confirm' }}
              </button>
              <button
                v-if="row.state === 'draft'"
                type="button"
                class="link-btn danger"
                :disabled="deletingId === row.id || confirmingId === row.id"
                @click="removeRow(row)"
              >
                {{ deletingId === row.id ? '…' : 'Delete' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="!loading && totalCount > 0" class="pager">
      <button type="button" class="btn-edit" :disabled="currentPage <= 1" @click="prevPage">
        Prev
      </button>
      <span class="muted small">Page {{ currentPage }} / {{ totalPages }} · {{ totalCount }} rows</span>
      <button type="button" class="btn-edit" :disabled="currentPage >= totalPages" @click="nextPage">
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
.good-receipt-list-page { max-width: 1200px; }
.lead { margin: -0.25rem 0 1rem; font-size: 0.95rem; }
.list-filters {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.75rem 1rem;
  margin-bottom: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border, #e5e7eb);
}
.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.85rem;
}
.filter-field span { color: var(--muted); }
.filter-input { min-width: 10rem; padding: 0.35rem 0.5rem; font-size: 0.9rem; }
.filter-actions { display: flex; gap: 0.5rem; align-items: center; }
.btn-confirm-selected { border: 1px solid #2563eb; }
.table-wrap { overflow-x: auto; }
.good-receipt-table .col-check { width: 2.2rem; text-align: center; }
.good-receipt-table .col-num { text-align: right; font-variant-numeric: tabular-nums; }
.good-receipt-table .col-actions { white-space: nowrap; text-align: right; }
.pager { display: flex; align-items: center; gap: 0.6rem; justify-content: flex-start; }
</style>
