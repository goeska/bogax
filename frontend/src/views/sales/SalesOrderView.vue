<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../../api/client'
import { fetchAllPages } from '../../utils/fetchAllPages'
import { formatDateTimeIso, formatIdr } from '../../utils/format'
import { buildOrderListParams } from '../../utils/listFilters'
import { usePagination } from '../../utils/pagination'

const router = useRouter()
const route = useRoute()
const rows = ref([])
const loading = ref(true)
const err = ref('')
const deletingId = ref(null)
const reopeningId = ref(null)
const salesOrderOptions = ref([])
const salesOrderOptionsLoading = ref(false)
const pag = usePagination(25)
const { currentPage, totalCount, totalPages, applyDrfResponse } = pag
const filterSalesOrderCode = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
/** True after Apply when at least one filter was set (drives empty-state copy). */
const lastAppliedHadFilters = ref(false)
const viewMode = ref('table')
const compactTable = ref(false)
const selectedQuickRange = ref('')
const stateOrder = ['draft', 'confirmed', 'paid', 'void']

function filterParams() {
  return {
    salesOrderCode: filterSalesOrderCode.value || undefined,
    orderType: route.query.order_type || undefined,
    dateFrom: filterDateFrom.value || undefined,
    dateTo: filterDateTo.value || undefined,
  }
}

async function load(page = 1) {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/sales-orders/', {
      params: buildOrderListParams(page, filterParams()),
    })
    applyDrfResponse(data, rows, page)
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && e.response?.data != null
        ? JSON.stringify(e.response.data)
        : null) ||
      e.message ||
      'Could not load sales orders.'
    rows.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  lastAppliedHadFilters.value = Boolean(
    filterSalesOrderCode.value || filterDateFrom.value || filterDateTo.value,
  )
  load(1)
}

function toIsoDate(inputDate) {
  const year = inputDate.getFullYear()
  const month = String(inputDate.getMonth() + 1).padStart(2, '0')
  const day = String(inputDate.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function applyQuickRange(rangeKey) {
  const today = new Date()
  const endDate = new Date(today)
  const startDate = new Date(today)

  if (rangeKey === 'today') {
    // keep start and end on today's date
  } else if (rangeKey === '7d') {
    startDate.setDate(today.getDate() - 6)
  } else if (rangeKey === 'month') {
    startDate.setDate(1)
  } else if (rangeKey === 'year') {
    startDate.setMonth(0, 1)
  } else {
    return
  }

  filterDateFrom.value = toIsoDate(startDate)
  filterDateTo.value = toIsoDate(endDate)
  selectedQuickRange.value = rangeKey
  applyFilters()
}

function clearFilters() {
  filterSalesOrderCode.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  selectedQuickRange.value = ''
  lastAppliedHadFilters.value = false
  load(1)
}

function onDateInputChange() {
  selectedQuickRange.value = ''
}

const groupedRows = computed(() => {
  const groups = stateOrder.map((state) => ({ state, items: [] }))
  const byState = new Map(groups.map((g) => [g.state, g]))
  for (const row of rows.value) {
    const key = String(row.state || '').toLowerCase()
    if (!byState.has(key)) {
      const extra = { state: key || 'other', items: [] }
      groups.push(extra)
      byState.set(key, extra)
    }
    byState.get(key).items.push(row)
  }
  return groups
})

const { prevPage, nextPage } = pag.makePager(loading, load)

function openInPos(row) {
  const currentOrderType = route.query.order_type || row.order_type
  const targetName =
    currentOrderType === 'delivery_order'
      ? 'sales-do-form'
      : currentOrderType === 'non_retail'
        ? 'sales-so-form'
        : 'sales-pos'
  router.push({ name: targetName, query: { orderId: String(row.id) } })
}

function canDelete(row) {
  return row.state === 'draft'
}

function stateLabel(state) {
  if (state === 'draft') return 'Draft'
  if (state === 'confirmed') return 'Confirmed'
  if (state === 'paid') return 'Paid'
  if (state === 'void') return 'Void'
  return state || 'Unknown'
}

async function remove(row) {
  const label = row.code || `#${row.id}`
  if (!confirm(`Trash sales order ${label}? (soft delete)`)) return
  deletingId.value = row.id
  err.value = ''
  try {
    await api.delete(`/sales-orders/${row.id}/`)
    await load(currentPage.value)
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && e.response?.data != null
        ? JSON.stringify(e.response.data)
        : null) ||
      e.message ||
      'Could not delete.'
  } finally {
    deletingId.value = null
  }
}

async function reopen(row) {
  const label = row.code || `#${row.id}`
  const ok = confirm(`Reopen ${label} as a draft?`)
  if (!ok) return
  reopeningId.value = row.id
  err.value = ''
  try {
    await api.post(`/sales-orders/${row.id}/reopen/`, {})
    await load(currentPage.value)
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && e.response?.data != null
        ? JSON.stringify(e.response.data)
        : null) ||
      e.message ||
      'Could not reopen.'
  } finally {
    reopeningId.value = null
  }
}

onMounted(async () => {
  salesOrderOptionsLoading.value = true
  try {
    const orders = await fetchAllPages('/sales-orders/')
    salesOrderOptions.value = orders
      .map((so) => ({ id: so.id, code: so.code || '' }))
      .filter((so) => so.code)
  } catch {
    salesOrderOptions.value = []
  } finally {
    salesOrderOptionsLoading.value = false
  }
  await load()
})
</script>

<template>
  <div class="stack sales-order-page">
    <section class="card erp-head so-head-compact">
      <p class="erp-kicker">Sales Control</p>
      <div class="erp-title-row">
        <h1 class="erp-title">SO List</h1>
        <span class="erp-chip">Draft • Confirmed • Reopen</span>
      </div>
    </section>

    <section class="so-controls">
      <div class="list-filters so-filters">
        <label class="filter-field">
          <span>Sales Order Code</span>
          <select v-model="filterSalesOrderCode" class="filter-input" :disabled="salesOrderOptionsLoading">
            <option value="">All sales order codes</option>
            <option v-for="so in salesOrderOptions" :key="so.id" :value="so.code">{{ so.code }}</option>
          </select>
        </label>
        <label class="filter-field">
          <span>Start date</span>
          <input v-model="filterDateFrom" type="date" class="filter-input" @change="onDateInputChange" />
        </label>
        <label class="filter-field">
          <span>End date</span>
          <input v-model="filterDateTo" type="date" class="filter-input" @change="onDateInputChange" />
        </label>
        <div class="filter-actions">
          <button type="button" class="btn-edit" @click="applyFilters">Apply</button>
          <button type="button" class="btn-ghost" @click="clearFilters">Clear</button>
        </div>
      </div>
      <div class="quick-range-row">
        <span class="quick-range-label">Quick range</span>
        <button
          type="button"
          class="quick-range-chip"
          :class="{ 'is-active': selectedQuickRange === 'today' }"
          @click="applyQuickRange('today')"
        >
          Today
        </button>
        <button
          type="button"
          class="quick-range-chip"
          :class="{ 'is-active': selectedQuickRange === '7d' }"
          @click="applyQuickRange('7d')"
        >
          Last 7 Days
        </button>
        <button
          type="button"
          class="quick-range-chip"
          :class="{ 'is-active': selectedQuickRange === 'month' }"
          @click="applyQuickRange('month')"
        >
          This Month
        </button>
        <button
          type="button"
          class="quick-range-chip"
          :class="{ 'is-active': selectedQuickRange === 'year' }"
          @click="applyQuickRange('year')"
        >
          This Year
        </button>
      </div>
      <div class="list-toolbar so-toolbar">
        <div class="view-switch">
          <button
            type="button"
            class="btn-edit"
            :class="{ 'is-active': viewMode === 'table' }"
            @click="viewMode = 'table'"
          >
            Table
          </button>
          <button
            type="button"
            class="btn-edit"
            :class="{ 'is-active': viewMode === 'kanban' }"
            @click="viewMode = 'kanban'"
          >
            Kanban
          </button>
        </div>
        <label class="density-switch">
          <input v-model="compactTable" type="checkbox" />
          <span>Compact table</span>
        </label>
      </div>
    </section>

    <p v-if="err" class="error">{{ err }}</p>

    <div v-if="loading" class="muted">Loading…</div>
    <div v-else-if="rows.length === 0" class="muted">
      {{ lastAppliedHadFilters ? 'No matching orders.' : 'No sales orders yet.' }}
    </div>
    <div v-else-if="viewMode === 'table'" class="table-wrap">
      <table class="table sales-order-table" :class="{ 'sales-order-table--compact': compactTable }">
        <thead>
          <tr>
            <th scope="col">Code</th>
            <th scope="col">Type</th>
            <th scope="col">Transaction Time</th>
            <th scope="col" class="col-num">Sub Total</th>
            <th scope="col" class="col-num">Tax Amount</th>
            <th scope="col" class="col-num">Total</th>
            <th scope="col">Partner</th>
            <th scope="col">Phone</th>
            <th scope="col">State</th>
            <th scope="col" class="col-actions"> </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td>{{ row.code || '—' }}</td>
            <td>{{ row.order_type || '—' }}</td>
            <td>{{ formatDateTimeIso(row.time_transaction) }}</td>
            <td class="col-num">{{ formatIdr(row.subtotal) }}</td>
            <td class="col-num">{{ formatIdr(row.tax_total) }}</td>
            <td class="col-num">{{ formatIdr(row.grand_total) }}</td>
            <td>{{ row.partner?.name || row.customer?.name || '—' }}</td>
            <td>{{ row.partner?.phone || row.customer?.phone || '—' }}</td>
            <td>
              <span class="so-state" :class="'so-state--' + row.state">{{ row.state }}</span>
            </td>
            <td class="col-actions">
              <button
                type="button"
                class="link-btn"
                @click="openInPos(row)"
              >
                {{ row.state === 'draft' ? 'Edit' : 'View' }}
              </button>
              <button
                v-if="row.state === 'confirmed'"
                type="button"
                class="link-btn btn-reopen"
                :disabled="reopeningId === row.id"
                @click="reopen(row)"
              >
                {{ reopeningId === row.id ? '…' : 'Reopen' }}
              </button>
              <button
                v-if="canDelete(row)"
                type="button"
                class="link-btn danger"
                :disabled="deletingId === row.id || reopeningId === row.id"
                @click="remove(row)"
              >
                {{ deletingId === row.id ? '…' : 'Delete' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="kanban-wrap">
      <section v-for="group in groupedRows" :key="group.state" class="kanban-col">
        <header class="kanban-col-head">
          <h3>{{ stateLabel(group.state) }}</h3>
          <span>{{ group.items.length }}</span>
        </header>
        <div v-if="group.items.length === 0" class="kanban-empty muted">No orders</div>
        <article v-for="row in group.items" :key="row.id" class="kanban-card">
          <div class="kanban-card-top">
            <strong>{{ row.code || `#${row.id}` }}</strong>
            <span class="so-state" :class="'so-state--' + row.state">{{ row.state }}</span>
          </div>
          <p class="kanban-meta muted small">{{ formatDateTimeIso(row.time_transaction) }}</p>
          <p class="kanban-meta">{{ row.partner?.name || row.customer?.name || '—' }}</p>
          <p class="kanban-total">{{ formatIdr(row.grand_total) }}</p>
          <div class="kanban-actions">
            <button type="button" class="link-btn" @click="openInPos(row)">
              {{ row.state === 'draft' ? 'Edit' : 'View' }}
            </button>
            <button
              v-if="row.state === 'confirmed'"
              type="button"
              class="link-btn btn-reopen"
              :disabled="reopeningId === row.id"
              @click="reopen(row)"
            >
              {{ reopeningId === row.id ? '…' : 'Reopen' }}
            </button>
            <button
              v-if="canDelete(row)"
              type="button"
              class="link-btn danger"
              :disabled="deletingId === row.id || reopeningId === row.id"
              @click="remove(row)"
            >
              {{ deletingId === row.id ? '…' : 'Delete' }}
            </button>
          </div>
        </article>
      </section>
    </div>
    <div v-if="!loading && totalCount > 0" class="pager">
      <button type="button" class="btn-edit" :disabled="currentPage <= 1" @click="prevPage">
        Prev
      </button>
      <span class="muted small">Page {{ currentPage }} / {{ totalPages }} · {{ totalCount }} rows</span>
      <button
        type="button"
        class="btn-edit"
        :disabled="currentPage >= totalPages"
        @click="nextPage"
      >
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
.sales-order-page {
  max-width: 1200px;
  gap: 0.26rem;
}

.so-head-compact {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 0.1rem;
  padding: 0.44rem 0.78rem 0.3rem;
}

.so-head-compact .erp-title-row {
  width: 100%;
}

.so-controls {
  margin-bottom: 0.1rem;
  padding: 0.62rem 0.78rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 12px;
  background: linear-gradient(180deg, #fffffff2 0%, #f8fbfff2 100%);
  display: grid;
  gap: 0.38rem;
}

.so-filters {
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  display: grid;
  grid-template-columns: minmax(180px, 1.35fr) repeat(2, minmax(145px, 0.9fr)) auto;
  gap: 0.45rem 0.65rem;
  align-items: end;
}

.so-filters .filter-actions {
  margin-left: auto;
}

.list-filters {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.75rem 1rem;
  margin-bottom: 1rem;
  padding: 0.85rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 12px;
  background: #fbfdff;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.85rem;
}

.filter-field span {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.15;
}

.filter-input {
  min-width: 9.2rem;
  padding: 0.42rem 0.56rem;
  font-size: 0.86rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 10px;
  background: #fff;
}

.filter-actions {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}

.table-wrap {
  overflow-x: auto;
}

.sales-order-table {
  font-size: 0.88rem;
}

.sales-order-table th,
.sales-order-table td {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.sales-order-table thead th {
  position: sticky;
  top: 0;
  z-index: 2;
  font-size: 0.76rem;
  letter-spacing: 0.03em;
}

.sales-order-table--compact th,
.sales-order-table--compact td {
  padding-top: 0.34rem;
  padding-bottom: 0.34rem;
  font-size: 0.84rem;
}

.sales-order-table .col-num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.sales-order-table .col-actions {
  white-space: nowrap;
  text-align: right;
  min-width: 8.8rem;
}

.pager {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  justify-content: flex-start;
  padding-top: 0.35rem;
}

.list-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.so-toolbar {
  border-top: 1px dashed #d8e2f0;
  padding-top: 0.45rem;
  justify-content: flex-start;
}

.quick-range-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.quick-range-label {
  font-size: 0.74rem;
  color: var(--muted);
  margin-right: 0.1rem;
}

.quick-range-chip {
  border: 1px solid #d4e0f3;
  background: #fff;
  color: #334155;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  cursor: pointer;
}

.quick-range-chip:hover {
  border-color: #bfd2ee;
  background: #f8fbff;
}

.quick-range-chip.is-active {
  border-color: #8eb5ed;
  background: #eaf3ff;
  color: #1e40af;
}

.so-toolbar .density-switch {
  margin-left: auto;
}

.view-switch {
  display: inline-flex;
  gap: 0.4rem;
}

.view-switch .btn-edit {
  padding: 0.36rem 0.72rem;
  font-size: 0.82rem;
}

.view-switch .btn-edit.is-active {
  border-color: #60a5fa;
  background: #eaf3ff;
  color: #1e40af;
}

.density-switch {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.79rem;
  color: var(--muted);
}

.density-switch input {
  margin: 0;
}

.kanban-wrap {
  display: grid;
  grid-template-columns: repeat(4, minmax(220px, 1fr));
  gap: 0.8rem;
  align-items: start;
}

@media (max-width: 1180px) {
  .so-filters {
    grid-template-columns: repeat(2, minmax(180px, 1fr));
  }

  .so-filters .filter-actions {
    margin-left: 0;
  }

  .quick-range-row {
    gap: 0.3rem;
  }

  .kanban-wrap {
    grid-template-columns: repeat(2, minmax(220px, 1fr));
  }
}

@media (max-width: 640px) {
  .so-filters {
    grid-template-columns: 1fr;
  }

  .so-filters .filter-field {
    width: 100%;
  }

  .so-filters .filter-input {
    width: 100%;
  }

  .so-filters .filter-actions {
    margin-left: 0;
    width: 100%;
  }

  .so-filters .filter-actions button {
    flex: 1 1 auto;
  }

  .so-toolbar .density-switch {
    margin-left: 0;
  }

  .kanban-wrap {
    grid-template-columns: 1fr;
  }
}

.kanban-col {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  padding: 0.65rem;
  display: grid;
  gap: 0.5rem;
}

.kanban-col-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px dashed #d6e0ef;
}

.kanban-col-head h3 {
  margin: 0;
  font-size: 0.86rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #334155;
}

.kanban-col-head span {
  font-size: 0.75rem;
  color: #1e40af;
  background: #eaf3ff;
  border: 1px solid #c7dcff;
  border-radius: 999px;
  padding: 0.15rem 0.45rem;
  font-weight: 700;
}

.kanban-empty {
  font-size: 0.83rem;
  padding: 0.5rem 0.35rem;
}

.kanban-card {
  border: 1px solid #dbe5f3;
  border-radius: 10px;
  background: #fff;
  padding: 0.55rem 0.6rem;
  display: grid;
  gap: 0.32rem;
}

.kanban-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.kanban-meta {
  margin: 0;
  font-size: 0.82rem;
}

.kanban-total {
  margin: 0.18rem 0 0;
  font-size: 0.92rem;
  font-weight: 700;
  color: #0f172a;
}

.kanban-actions {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  flex-wrap: wrap;
}

.btn-reopen {
  margin-right: 0.15rem;
}

.so-state {
  display: inline-flex;
  align-items: center;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.22rem 0.48rem;
  border-radius: 999px;
  border: 1px solid transparent;
  text-transform: capitalize;
}

.so-state--draft {
  color: #1d4ed8;
  background: #dbeafe;
  border-color: #bfdbfe;
}

.so-state--confirmed {
  color: #15803d;
  background: #dcfce7;
  border-color: #bbf7d0;
}

.so-state--paid {
  color: #166534;
  background: #d1fae5;
  border-color: #a7f3d0;
}

.so-state--void {
  color: #64748b;
  background: #f1f5f9;
  border-color: #e2e8f0;
}
</style>
