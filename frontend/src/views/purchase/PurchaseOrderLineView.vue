<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { fetchAllPages } from '../../utils/fetchAllPages'
import { formatDateTimeIso, formatIdr } from '../../utils/format'
import { buildOrderListParams } from '../../utils/listFilters'
import { usePagination } from '../../utils/pagination'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const pag = usePagination(25)
const { currentPage, totalCount, totalPages, applyDrfResponse } = pag
const products = ref([])
const productsLoading = ref(false)
const purchaseOrderOptions = ref([])
const purchaseOrderOptionsLoading = ref(false)
const filterPurchaseOrderCode = ref('')
const filterProductId = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
const lastAppliedHadFilters = ref(false)

function filterParams() {
  return {
    purchaseOrderCode: filterPurchaseOrderCode.value.trim() || undefined,
    productId: filterProductId.value || undefined,
    dateFrom: filterDateFrom.value || undefined,
    dateTo: filterDateTo.value || undefined,
  }
}

async function load(page = 1) {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/purchase-order-lines/', {
      params: buildOrderListParams(page, filterParams()),
    })
    applyDrfResponse(data, rows, page)
  } catch (e) {
    err.value = e.response?.data?.detail || e.message || 'Failed to load purchase order lines.'
    rows.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  lastAppliedHadFilters.value = Boolean(
    filterPurchaseOrderCode.value.trim() ||
      filterProductId.value ||
      filterDateFrom.value ||
      filterDateTo.value,
  )
  load(1)
}

function clearFilters() {
  filterPurchaseOrderCode.value = ''
  filterProductId.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  lastAppliedHadFilters.value = false
  load(1)
}

const { prevPage, nextPage } = pag.makePager(loading, load)

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
  productsLoading.value = true
  try {
    products.value = await fetchAllPages('/products/')
  } catch {
    products.value = []
  } finally {
    productsLoading.value = false
  }
  await load()
})
</script>

<template>
  <div class="stack purchase-order-line-page">
    <h2 class="h2">PO Item List</h2>
    <p class="muted lead">All transaction lines from purchase orders.</p>

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
        <span>Product</span>
        <select v-model="filterProductId" class="filter-input" :disabled="productsLoading">
          <option value="">All products</option>
          <option v-for="pr in products" :key="pr.id" :value="String(pr.id)">
            {{ pr.name }}
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
      {{ lastAppliedHadFilters ? 'No matching purchase order lines.' : 'No purchase order lines yet.' }}
    </div>
    <div v-else class="table-wrap">
      <table class="table purchase-order-line-table">
        <thead>
          <tr>
            <th scope="col">Purchase Order</th>
            <th scope="col">Transaction Time</th>
            <th scope="col">Vendor</th>
            <th scope="col">Product</th>
            <th scope="col" class="col-num">Quantity</th>
            <th scope="col" class="col-num">Received Quantity</th>
            <th scope="col" class="col-num">Outstanding Quantity</th>
            <th scope="col" class="col-num">Unit Price</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td>{{ row.purchase_order_code || `#${row.purchase_order_id}` }}</td>
            <td>{{ formatDateTimeIso(row.transaction_at) }}</td>
            <td>{{ row.vendor_name || '—' }}</td>
            <td>{{ row.product_name || '—' }}</td>
            <td class="col-num">{{ row.ordered_quantity }}</td>
            <td class="col-num">{{ row.received_quantity }}</td>
            <td class="col-num">{{ row.outstanding_quantity }}</td>
            <td class="col-num">{{ formatIdr(row.unit_price) }}</td>
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
.purchase-order-line-page { max-width: 1300px; }
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
.table-wrap { overflow-x: auto; }
.purchase-order-line-table .col-num { text-align: right; font-variant-numeric: tabular-nums; }
.pager {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  justify-content: flex-start;
}
</style>
