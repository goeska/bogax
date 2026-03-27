<script setup>
import { onMounted, ref } from 'vue'
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
      'Failed to load sales orders.'
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

function clearFilters() {
  filterSalesOrderCode.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  lastAppliedHadFilters.value = false
  load(1)
}

const { prevPage, nextPage } = pag.makePager(loading, load)

function openInPos(row) {
  const targetName = route.query.order_type === 'non_retail' ? 'sales-so-form' : 'sales-pos'
  router.push({ name: targetName, query: { orderId: String(row.id) } })
}

function canDelete(row) {
  return row.state === 'draft'
}

async function remove(row) {
  const label = row.code || `#${row.id}`
  if (!confirm(`Delete sales order ${label}? It will be soft-deleted.`)) return
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
      'Failed to delete.'
  } finally {
    deletingId.value = null
  }
}

async function reopen(row) {
  const label = row.code || `#${row.id}`
  const ok = confirm(`Reopen sales order ${label} and set it back to draft?`)
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
      'Failed to reopen.'
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
    <h2 class="h2">SO List</h2>
    <p class="muted lead">
      List of your active orders (draft and confirmed). Delete performs a soft delete.
    </p>

    <div class="list-filters">
      <label class="filter-field">
        <span>Sales Order Code</span>
        <select v-model="filterSalesOrderCode" class="filter-input" :disabled="salesOrderOptionsLoading">
          <option value="">All sales order codes</option>
          <option v-for="so in salesOrderOptions" :key="so.id" :value="so.code">{{ so.code }}</option>
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
      <div class="filter-actions">
        <button type="button" class="btn-edit" @click="applyFilters">Apply</button>
        <button type="button" class="btn-ghost" @click="clearFilters">Clear</button>
      </div>
    </div>

    <p v-if="err" class="error">{{ err }}</p>

    <div v-if="loading" class="muted">Loading…</div>
    <div v-else-if="rows.length === 0" class="muted">
      {{ lastAppliedHadFilters ? 'No matching orders.' : 'No sales orders yet.' }}
    </div>
    <div v-else class="table-wrap">
      <table class="table sales-order-table">
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
}

.lead {
  margin: -0.25rem 0 1rem;
  font-size: 0.95rem;
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
  gap: 0.25rem;
  font-size: 0.85rem;
}

.filter-field span {
  color: var(--muted);
}

.filter-input {
  min-width: 10rem;
  padding: 0.45rem 0.62rem;
  font-size: 0.9rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 10px;
  background: #fff;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.table-wrap {
  overflow-x: auto;
}

.sales-order-table {
  font-size: 0.9rem;
}

.sales-order-table .col-num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.sales-order-table .col-actions {
  white-space: nowrap;
  text-align: right;
}

.pager {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  justify-content: flex-start;
  padding-top: 0.35rem;
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
