<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { formatDateTimeIso, formatIdr } from '../../utils/format'
import { buildPaymentListParams } from '../../utils/listFilters'
import { usePagination } from '../../utils/pagination'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const pag = usePagination(50)
const { currentPage, totalCount, totalPages, applyDrfResponse } = pag
const filterTxType = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
const lastAppliedHadFilters = ref(false)

function filterParams() {
  const tx = filterTxType.value
  return {
    txType: tx === 'i' || tx === 'o' ? tx : undefined,
    dateFrom: filterDateFrom.value || undefined,
    dateTo: filterDateTo.value || undefined,
  }
}

async function load(page = 1) {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/payments/', {
      params: buildPaymentListParams(page, filterParams()),
    })
    applyDrfResponse(data, rows, page)
  } catch (e) {
    err.value = e.response?.data?.detail || e.message || 'Failed to load payments.'
    rows.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  lastAppliedHadFilters.value = Boolean(
    filterTxType.value || filterDateFrom.value || filterDateTo.value,
  )
  load(1)
}

function clearFilters() {
  filterTxType.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  lastAppliedHadFilters.value = false
  load(1)
}

const { prevPage, nextPage } = pag.makePager(loading, load)

function sourceLabel(p) {
  const s = p.source_summary
  if (!s) return `${p.source_table} #${p.source_pk}`
  const table = s.table === 'sales_order' ? 'Sales Order' : s.table === 'purchase_order' ? 'Purchase Order' : s.table
  return `${table} #${s.id}`
}

onMounted(() => load())
</script>

<template>
  <div class="stack payment-page">
    <h2 class="h2">Payment</h2>
    <p class="muted">Incoming and outgoing cash transactions.</p>

    <div class="list-filters">
      <label class="filter-field">
        <span>Payment type</span>
        <select v-model="filterTxType" class="filter-input">
          <option value="">All types</option>
          <option value="i">Incoming</option>
          <option value="o">Outgoing</option>
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
      {{ lastAppliedHadFilters ? 'No matching payments.' : 'No payments found.' }}
    </div>
    <div v-else class="table-wrap">
      <table class="table payment-table">
        <thead>
          <tr>
            <th scope="col">Transaction Time</th>
            <th scope="col">Type</th>
            <th scope="col">Source</th>
            <th scope="col">Document</th>
            <th scope="col">Source State</th>
            <th scope="col">Party</th>
            <th scope="col">Phone</th>
            <th scope="col" class="col-num">Amount</th>
            <th scope="col">Created By</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in rows" :key="p.id">
            <td>{{ formatDateTimeIso(p.transaction_at) }}</td>
            <td>{{ p.type_label }}</td>
            <td>{{ sourceLabel(p) }}</td>
            <td>{{ p.source_summary?.code || p.reference_code || '—' }}</td>
            <td>{{ p.source_summary?.state || '—' }}</td>
            <td>{{ p.source_summary?.party_name || '—' }}</td>
            <td>{{ p.source_summary?.party_phone || '—' }}</td>
            <td class="col-num">{{ formatIdr(p.amount) }}</td>
            <td>{{ p.created_by_email || '—' }}</td>
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
.payment-page {
  max-width: 1300px;
}
.table-wrap {
  overflow-x: auto;
}
.payment-table {
  font-size: 0.9rem;
}
.payment-table .col-num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.list-filters {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.75rem 1rem;
  margin: 0.75rem 0 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border, #e5e7eb);
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
  min-width: 11rem;
  padding: 0.35rem 0.5rem;
  font-size: 0.9rem;
}
.filter-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.pager {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  justify-content: flex-start;
}
</style>
