<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/client'
import { fetchAllPages } from '../../utils/fetchAllPages'
import { formatDateTimeIso, formatIdr } from '../../utils/format'
import { buildOrderListParams } from '../../utils/listFilters'
import { usePagination } from '../../utils/pagination'

const router = useRouter()
const rows = ref([])
const loading = ref(true)
const err = ref('')
const deletingId = ref(null)
const reopeningId = ref(null)
const pag = usePagination(25)
const { currentPage, totalCount, totalPages, applyDrfResponse } = pag
const purchaseOrderOptions = ref([])
const purchaseOrderOptionsLoading = ref(false)
const filterPurchaseOrderCode = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
const lastAppliedHadFilters = ref(false)

function filterParams() {
  return {
    purchaseOrderCode: filterPurchaseOrderCode.value || undefined,
    dateFrom: filterDateFrom.value || undefined,
    dateTo: filterDateTo.value || undefined,
  }
}

async function load(page = 1) {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/purchase-orders/', {
      params: buildOrderListParams(page, filterParams()),
    })
    applyDrfResponse(data, rows, page)
  } catch (e) {
    err.value = e.response?.data?.detail || e.message || 'Could not load purchase orders.'
    rows.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  lastAppliedHadFilters.value = Boolean(
    filterPurchaseOrderCode.value || filterDateFrom.value || filterDateTo.value,
  )
  load(1)
}

function clearFilters() {
  filterPurchaseOrderCode.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  lastAppliedHadFilters.value = false
  load(1)
}

const { prevPage, nextPage } = pag.makePager(loading, load)

function openInPos(row) {
  router.push({ name: 'purchase-pos', query: { orderId: String(row.id) } })
}

async function remove(row) {
  const label = row.code || `#${row.id}`
  if (!confirm(`Trash purchase order ${label}? (soft delete)`)) return
  deletingId.value = row.id
  err.value = ''
  try {
    await api.delete(`/purchase-orders/${row.id}/`)
    await load(currentPage.value)
  } catch (e) {
    err.value = e.response?.data?.detail || e.message || 'Could not delete.'
  } finally {
    deletingId.value = null
  }
}

async function reopen(row) {
  reopeningId.value = row.id
  err.value = ''
  try {
    await api.post(`/purchase-orders/${row.id}/reopen/`, {})
    await load(currentPage.value)
  } catch (e) {
    err.value = e.response?.data?.detail || e.message || 'Could not reopen.'
  } finally {
    reopeningId.value = null
  }
}

onMounted(async () => {
  purchaseOrderOptionsLoading.value = true
  try {
    const orders = await fetchAllPages('/purchase-orders/')
    purchaseOrderOptions.value = orders
      .map((po) => ({ id: po.id, code: po.code || '' }))
      .filter((po) => po.code)
  } catch {
    purchaseOrderOptions.value = []
  } finally {
    purchaseOrderOptionsLoading.value = false
  }
  await load()
})
</script>

<template>
  <div class="stack purchase-order-page">
    <section class="card erp-head">
      <p class="erp-kicker">Purchase Control</p>
      <div class="erp-title-row">
        <h1 class="erp-title">PO List</h1>
        <span class="erp-chip">Draft • Confirmed • Reopen</span>
      </div>
      <p class="muted lead">Review and manage active purchase orders quickly and consistently.</p>
    </section>

    <div class="list-filters">
      <label class="filter-field">
        <span>Purchase Order Code</span>
        <select
          v-model="filterPurchaseOrderCode"
          class="filter-input"
          :disabled="purchaseOrderOptionsLoading"
        >
          <option value="">All purchase order codes</option>
          <option v-for="po in purchaseOrderOptions" :key="po.id" :value="po.code">
            {{ po.code }}
          </option>
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
      {{ lastAppliedHadFilters ? 'No matching orders.' : 'No purchase orders yet.' }}
    </div>
    <div v-else class="table-wrap">
      <table class="table purchase-order-table">
        <thead>
          <tr>
            <th scope="col">Code</th>
            <th scope="col">Transaction Time</th>
            <th scope="col" class="col-num">Sub Total</th>
            <th scope="col" class="col-num">Tax</th>
            <th scope="col" class="col-num">Total</th>
            <th scope="col">Vendor</th>
            <th scope="col">Phone</th>
            <th scope="col">State</th>
            <th scope="col" class="col-actions"> </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td>{{ row.code || '—' }}</td>
            <td>{{ formatDateTimeIso(row.time_transaction) }}</td>
            <td class="col-num">{{ formatIdr(row.subtotal) }}</td>
            <td class="col-num">{{ formatIdr(row.tax_total) }}</td>
            <td class="col-num">{{ formatIdr(row.grand_total) }}</td>
            <td>{{ row.vendor_name || '—' }}</td>
            <td>{{ row.vendor_phone || '—' }}</td>
            <td><span class="po-state" :class="'po-state--' + row.state">{{ row.state }}</span></td>
            <td class="col-actions">
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
                v-if="row.state === 'draft'"
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
.purchase-order-page {
  max-width: 1200px;
  gap: 0.7rem;
}

.lead {
  margin: 0.1rem 0 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.list-filters {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.55rem 0.8rem;
  margin-bottom: 0.4rem;
  padding: 0.68rem 0.8rem;
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
}
.filter-actions {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}
.table-wrap { overflow-x: auto; }
.purchase-order-table .col-num { text-align: right; font-variant-numeric: tabular-nums; }
.purchase-order-table .col-actions { white-space: nowrap; text-align: right; }
.btn-reopen { margin-right: 0.15rem; }
.po-state { font-size: 0.85rem; font-weight: 600; text-transform: capitalize; }
.po-state--draft { color: #2563eb; }
.po-state--confirmed { color: #15803d; }
.po-state--void { color: var(--muted); }
.pager {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  justify-content: flex-start;
}
</style>
