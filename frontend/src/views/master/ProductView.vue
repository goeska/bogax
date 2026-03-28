<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'
import { extractApiErrorText } from '../../utils/apiError'
import { fetchAllPages } from '../../utils/fetchAllPages'
import { formatIdr } from '../../utils/format'
import { usePagination } from '../../utils/pagination'

const rows = ref([])
const categories = ref([])
const uoms = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({
  name: '',
  product_type: 'storable',
  product_category_id: null,
  uom_id: null,
  is_active: true,
  unit_price: '',
})
const editingId = ref(null)
const saving = ref(false)
const listTab = ref('active')

const nameInput = ref('')
const nameFilter = ref('')
const listCategoryInput = ref('')
const listCategoryFilter = ref('')
const filtersApplied = ref(false)

const pag = usePagination(25)
const { currentPage, totalCount, totalPages, applyDrfResponse } = pag
const { prevPage, nextPage } = pag.makePager(loading, load)

const categoryById = computed(() => {
  const m = new Map()
  for (const c of categories.value) m.set(c.id, c.name)
  return m
})

const uomById = computed(() => {
  const m = new Map()
  for (const u of uoms.value) m.set(u.id, u.name)
  return m
})

/** Active categories for new products; when editing, include current category if inactive. */
const categorySelectOptions = computed(() => {
  const all = categories.value || []
  const active = all.filter((c) => c.is_active !== false)
  const sel = form.value.product_category_id
  if (sel == null) return active
  if (active.some((c) => c.id === sel)) return active
  const cur = all.find((c) => c.id === sel)
  return cur ? [...active, cur] : active
})

/** Active UOMs for new products; when editing, include current UOM even if inactive. */
const uomSelectOptions = computed(() => {
  const all = uoms.value || []
  const active = all.filter((u) => u.is_active !== false)
  const sel = form.value.uom_id
  if (sel == null) return active
  if (active.some((u) => u.id === sel)) return active
  const cur = all.find((u) => u.id === sel)
  return cur ? [...active, cur] : active
})

function buildListParams(page) {
  const p = { page }
  p.is_active = listTab.value === 'active' ? 'true' : 'false'
  const n = nameFilter.value.trim()
  if (n) p.name = n
  const cid = listCategoryFilter.value.trim()
  if (cid) p.product_category_id = cid
  return p
}

function applyFilters() {
  nameFilter.value = nameInput.value
  listCategoryFilter.value = listCategoryInput.value
  filtersApplied.value = Boolean(nameFilter.value.trim() || listCategoryFilter.value.trim())
  load(1)
}

function clearFilters() {
  nameInput.value = ''
  nameFilter.value = ''
  listCategoryInput.value = ''
  listCategoryFilter.value = ''
  filtersApplied.value = false
  load(1)
}

function defaultForm() {
  return {
    name: '',
    product_type: 'storable',
    product_category_id: null,
    uom_id: null,
    is_active: true,
    unit_price: '',
  }
}

async function loadRefs() {
  const [cat, uom] = await Promise.all([
    fetchAllPages('/product-categories/'),
    api.get('/uoms/'),
  ])
  categories.value = cat
  uoms.value = uom.data.results ?? uom.data
}

async function load(page = 1) {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/products/', { params: buildListParams(page) })
    applyDrfResponse(data, rows, page)
  } catch {
    err.value = 'Could not load products.'
    rows.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

function setListTab(tab) {
  listTab.value = tab
  load(1)
}

function startEdit(row) {
  editingId.value = row.id
  form.value = {
    name: row.name,
    product_type: row.product_type || 'storable',
    product_category_id: row.product_category_id,
    uom_id: row.uom_id,
    is_active: row.is_active,
    unit_price:
      row.unit_price === null || row.unit_price === undefined ? '' : String(row.unit_price),
  }
  err.value = ''
}

function cancelEdit() {
  editingId.value = null
  form.value = defaultForm()
}

function buildPayload() {
  const payload = {
    name: form.value.name,
    product_type: form.value.product_type || 'storable',
    product_category_id: form.value.product_category_id,
    uom_id: form.value.uom_id,
    is_active: form.value.is_active,
  }
  const up = String(form.value.unit_price).trim()
  if (up === '') {
    payload.unit_price = null
  } else {
    const n = Number(up)
    if (Number.isNaN(n)) {
      throw new Error('Unit price should be a number or blank.')
    }
    payload.unit_price = n
  }
  return payload
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const payload = buildPayload()
    const wasEditing = editingId.value != null
    if (wasEditing) {
      await api.patch(`/products/${editingId.value}/`, payload)
    } else {
      await api.post('/products/', payload)
    }
    cancelEdit()
    await load(wasEditing ? currentPage.value : 1)
  } catch (e) {
    if (e instanceof Error && !e.response) {
      err.value = e.message
    } else {
      err.value = extractApiErrorText(e.response?.data) || 'Could not save.'
    }
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  if (!confirm(`Delete product "${row.name}"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'products', row.id)
    if (editingId.value === row.id) cancelEdit()
    await load(currentPage.value)
  } catch (e) {
    err.value = deactivateErrorMessage(e)
  }
}

const listEmptyLabel = computed(() => {
  if (filtersApplied.value) return 'No matching products.'
  return listTab.value === 'active' ? 'No active products yet.' : 'No inactive products.'
})

const listCategoryOptions = computed(() => {
  const all = categories.value || []
  return all.slice().sort((a, b) => String(a.name || '').localeCompare(String(b.name || '')))
})

onMounted(async () => {
  await loadRefs()
  await load(1)
})
</script>

<template>
  <div class="stack product-page">
    <section class="card erp-head">
      <p class="erp-kicker">Master Data</p>
      <div class="erp-title-row">
        <h1 class="erp-title">Product Management</h1>
        <div class="category-tab-switch" role="tablist" aria-label="Product list scope">
          <button
            type="button"
            role="tab"
            class="category-tab"
            :class="{ 'is-active': listTab === 'active' }"
            :aria-selected="listTab === 'active'"
            @click="setListTab('active')"
          >
            Active products
          </button>
          <button
            type="button"
            role="tab"
            class="category-tab"
            :class="{ 'is-active': listTab === 'inactive' }"
            :aria-selected="listTab === 'inactive'"
            @click="setListTab('inactive')"
          >
            Non active products
          </button>
        </div>
      </div>
      <p class="muted product-subtitle">
        Manage products, categories, UOM, pricing, and active status in one workspace.
      </p>
      <div class="product-kpi-row">
        <span class="product-kpi product-kpi--ok">
          <strong>{{ totalCount }}</strong>
          {{ listTab === 'active' ? 'active' : 'inactive' }} products
          {{ filtersApplied ? '(filtered)' : '' }}
        </span>
      </div>
    </section>

    <div class="card product-form-card">
      <h2 class="h2">{{ editingId != null ? 'Edit Product' : 'Add Product' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field grow">
          <span>Name <span class="req" aria-hidden="true">*</span></span>
          <input v-model="form.name" required maxlength="255" />
        </label>
        <label class="field">
          <span>Type <span class="req" aria-hidden="true">*</span></span>
          <select v-model="form.product_type" required>
            <option value="storable">Storable</option>
            <option value="consumable">Consumable</option>
            <option value="service">Service</option>
          </select>
        </label>
        <label class="field grow">
          <span>Category <span class="req" aria-hidden="true">*</span></span>
          <select v-model="form.product_category_id" required>
            <option :value="null" disabled>Select…</option>
            <option v-for="c in categorySelectOptions" :key="c.id" :value="c.id">
              {{ c.name }}{{ c.is_active === false ? ' (inactive)' : '' }}
            </option>
          </select>
        </label>
        <label class="field grow">
          <span>UOM <span class="req" aria-hidden="true">*</span></span>
          <select v-model="form.uom_id" required>
            <option :value="null" disabled>Select…</option>
            <option v-for="u in uomSelectOptions" :key="u.id" :value="u.id">
              {{ u.name }}{{ u.is_active === false ? ' (inactive)' : '' }}
            </option>
          </select>
        </label>
        <label class="field narrow">
          <span>Unit Price (optional)</span>
          <input
            v-model="form.unit_price"
            type="number"
            step="0.01"
            min="0"
            placeholder="—"
          />
        </label>
        <label class="field check">
          <span>Active</span>
          <input v-model="form.is_active" type="checkbox" />
        </label>
        <button class="btn-primary" type="submit" :disabled="saving">
          {{ saving ? 'Saving…' : editingId != null ? 'Save Changes' : 'Save' }}
        </button>
        <button
          v-if="editingId != null"
          type="button"
          class="btn-ghost main-only"
          @click="cancelEdit"
        >
          Cancel
        </button>
      </form>
      <p v-if="err" class="error">{{ err }}</p>
    </div>

    <div class="card product-list-card">
      <div class="product-list-head">
        <h2 class="h2">{{ listTab === 'active' ? 'Active products' : 'Non active products' }}</h2>
      </div>
      <form class="form-row category-filter-row" @submit.prevent="applyFilters">
        <label class="field category-filter-name">
          <span class="category-filter-label">Name</span>
          <input
            v-model="nameInput"
            class="category-filter-input"
            type="text"
            maxlength="255"
            placeholder="Search…"
            autocomplete="off"
          />
        </label>
        <label class="field category-filter-category">
          <span class="category-filter-label">Category</span>
          <select v-model="listCategoryInput" class="category-filter-input">
            <option value="">All categories</option>
            <option v-for="c in listCategoryOptions" :key="c.id" :value="String(c.id)">
              {{ c.name }}{{ c.is_active === false ? ' (inactive)' : '' }}
            </option>
          </select>
        </label>
        <button type="submit" class="btn-edit category-filter-btn">Apply</button>
        <button type="button" class="btn-ghost category-filter-btn" @click="clearFilters">
          Clear
        </button>
      </form>
      <div v-if="loading" class="muted">Loading…</div>
      <div v-else-if="rows.length === 0" class="muted">{{ listEmptyLabel }}</div>
      <div v-else class="table-wrap">
        <table class="table product-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Category</th>
              <th>UOM</th>
              <th class="col-num">Price</th>
              <th>Active</th>
              <th class="col-actions" />
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>{{ row.name }}</td>
              <td>{{ row.product_type || '—' }}</td>
              <td>{{ categoryById.get(row.product_category_id) ?? row.product_category_id }}</td>
              <td>{{ uomById.get(row.uom_id) ?? row.uom_id }}</td>
              <td class="col-num">{{ row.unit_price == null ? '—' : formatIdr(Number(row.unit_price)) }}</td>
              <td>
                <span class="pill" :class="row.is_active ? 'pill--yes' : 'pill--no'">
                  {{ row.is_active ? 'Yes' : 'No' }}
                </span>
              </td>
              <td class="col-actions">
                <button type="button" class="link-btn" @click="startEdit(row)">Edit</button>
                <button
                  v-if="listTab === 'active'"
                  type="button"
                  class="link-btn danger"
                  @click="remove(row)"
                >
                  Delete
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
  </div>
</template>

<style scoped>
.product-page {
  max-width: 1240px;
}

.product-subtitle {
  margin: 0.35rem 0 0.7rem;
  font-size: 0.9rem;
}

.category-tab-switch {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-left: auto;
}

.category-tab {
  border: 1px solid #d4e0f3;
  background: #fff;
  color: #334155;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 650;
  padding: 0.28rem 0.72rem;
  cursor: pointer;
}

.category-tab:hover {
  border-color: #bfd2ee;
  background: #f8fbff;
}

.category-tab.is-active {
  border-color: #60a5fa;
  background: #eaf3ff;
  color: #1e40af;
}

.product-kpi-row {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.product-kpi {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.62rem;
  border-radius: 999px;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  color: #3730a3;
  font-size: 0.78rem;
  font-weight: 600;
}

.product-kpi strong {
  font-size: 0.84rem;
}

.product-kpi--ok {
  color: #166534;
  background: #e8f8ef;
  border-color: #b7e9ca;
}

.product-kpi--muted {
  color: #475569;
  background: #f1f5f9;
  border-color: #dce3ed;
}

.product-kpi--info {
  color: #0c4a6e;
  background: #e7f5ff;
  border-color: #bae6fd;
}

.product-list-head .h2 {
  margin-bottom: 0.6rem;
}

.product-table tbody tr:nth-child(even) {
  background: #fbfdff;
}

.category-filter-row {
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.35rem 0.45rem;
  margin-bottom: 0.65rem;
}

.category-filter-name {
  min-width: 0;
  max-width: 14rem;
  flex: 0 1 14rem;
  margin: 0;
}

.category-filter-category {
  min-width: 0;
  max-width: 16rem;
  flex: 0 1 16rem;
  margin: 0;
}

.category-filter-label {
  font-size: 0.78rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.category-filter-input {
  padding: 0.38rem 0.5rem;
  font-size: 0.8125rem;
  line-height: 1.25;
  width: 100%;
}

.category-filter-btn {
  padding: 0.38rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 600;
}

.pager {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  justify-content: flex-start;
  margin-top: 0.75rem;
}
</style>
