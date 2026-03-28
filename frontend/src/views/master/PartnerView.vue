<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'
import { extractApiErrorText } from '../../utils/apiError'
import { fetchAllPages } from '../../utils/fetchAllPages'
import { usePagination } from '../../utils/pagination'

const rows = ref([])
const legalEntityTypes = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({
  name: '',
  phone: '',
  address: '',
  legal_entity_type_id: null,
  parent_id: null,
  tax_id: '',
  is_customer: true,
  is_vendor: false,
  is_active: true,
})

/** Master list: active partners vs soft-deleted (reactivate via Edit + Active). */
const listTab = ref('active')
const editingId = ref(null)
const saving = ref(false)
const searchInput = ref('')
const search = ref('')
const isCorporateInput = ref('')
const isCorporate = ref('')
const filtersApplied = ref(false)

const pag = usePagination(25)
const { currentPage, totalCount, totalPages, applyDrfResponse } = pag
const { prevPage, nextPage } = pag.makePager(loading, load)

/** All active partners for parent dropdown (not tied to list pagination). */
const allActivePartners = ref([])

const legalEntityTypeById = computed(() => {
  const map = new Map()
  for (const t of legalEntityTypes.value || []) map.set(t.id, t)
  return map
})

/** Active partners only; exclude current row when editing (no self-parent). */
const parentOptions = computed(() => {
  const selfId = editingId.value
  return allActivePartners.value
    .filter((r) => selfId == null || r.id !== selfId)
    .slice()
    .sort((a, b) =>
      String(a.name || a.phone || '').localeCompare(String(b.name || b.phone || ''), undefined, {
        sensitivity: 'base',
      }),
    )
})

function buildListParams(page) {
  const p = { page }
  p.is_active = listTab.value === 'active' ? 'true' : 'false'
  const corp = isCorporate.value
  if (corp === 'yes') p.is_corporate = 'true'
  if (corp === 'no') p.is_corporate = 'false'
  const s = search.value.trim()
  if (s) p.search = s
  return p
}

function setListTab(tab) {
  listTab.value = tab
  load(1)
}

async function loadParentOptions() {
  try {
    allActivePartners.value = await fetchAllPages('/partners/', { is_active: 'true' })
  } catch {
    allActivePartners.value = []
  }
}

function applySearch() {
  search.value = searchInput.value
  isCorporate.value = isCorporateInput.value
  filtersApplied.value = Boolean(search.value.trim() || isCorporate.value)
  load(1)
}

function clearSearch() {
  searchInput.value = ''
  search.value = ''
  isCorporateInput.value = ''
  isCorporate.value = ''
  filtersApplied.value = false
  load(1)
}

async function loadLegalEntityTypes() {
  try {
    const { data } = await api.get('/legal-entity-types/')
    const list = data.results ?? data
    legalEntityTypes.value = Array.isArray(list)
      ? list.filter((t) => t.is_active !== false)
      : []
  } catch {
    legalEntityTypes.value = []
  }
}

async function load(page = 1) {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/partners/', { params: buildListParams(page) })
    applyDrfResponse(data, rows, page)
  } catch {
    err.value = 'Could not load partners.'
    rows.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

function startEdit(row) {
  editingId.value = row.id
  form.value = {
    name: row.name ?? '',
    phone: row.phone ?? '',
    address: row.address ?? '',
    legal_entity_type_id: row.legal_entity_type_id ?? null,
    parent_id: row.parent_id ?? null,
    tax_id: row.tax_id ?? '',
    is_customer: !!row.is_customer,
    is_vendor: !!row.is_vendor,
    is_active: row.is_active !== false,
  }
  err.value = ''
}

function cancelEdit() {
  editingId.value = null
  form.value = {
    name: '',
    phone: '',
    address: '',
    legal_entity_type_id: null,
    parent_id: null,
    tax_id: '',
    is_customer: true,
    is_vendor: false,
    is_active: true,
  }
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const taxTrim = String(form.value.tax_id || '').trim()
    const payload = {
      name: form.value.name,
      phone: form.value.phone,
      address: form.value.address,
      legal_entity_type_id: form.value.legal_entity_type_id || null,
      parent_id: form.value.parent_id != null && form.value.parent_id !== '' ? form.value.parent_id : null,
      tax_id: taxTrim ? taxTrim : null,
      is_customer: !!form.value.is_customer,
      is_vendor: !!form.value.is_vendor,
      is_active: !!form.value.is_active,
    }
    if (editingId.value != null) {
      await api.patch(`/partners/${editingId.value}/`, payload)
    } else {
      await api.post('/partners/', payload)
    }
    cancelEdit()
    await loadParentOptions()
    await load(currentPage.value)
  } catch (e) {
    const d = e.response?.data
    if (d && typeof d === 'object') {
      const pick = (k) => {
        const v = d[k]
        if (typeof v === 'string') return v
        if (Array.isArray(v) && typeof v[0] === 'string') return v[0]
        return ''
      }
      err.value =
        pick('name') ||
        pick('tax_id') ||
        pick('parent_id') ||
        extractApiErrorText(d) ||
        'Could not save.'
    } else {
      err.value = 'Could not save.'
    }
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  if (!confirm(`Delete partner "${row.name || row.phone || row.id}"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'partners', row.id)
    if (editingId.value === row.id) cancelEdit()
    await loadParentOptions()
    await load(currentPage.value)
  } catch (e) {
    err.value = deactivateErrorMessage(e)
  }
}

onMounted(async () => {
  await loadLegalEntityTypes()
  await loadParentOptions()
  await load(1)
})
</script>

<template>
  <div class="stack">
    <section class="card erp-head">
      <p class="erp-kicker">Master Data</p>
      <div class="erp-title-row partner-head-row">
        <h1 class="erp-title">Partner Management</h1>
        <div class="partner-tab-switch" role="tablist" aria-label="Partner list scope">
          <button
            type="button"
            role="tab"
            class="partner-tab"
            :class="{ 'is-active': listTab === 'active' }"
            :aria-selected="listTab === 'active'"
            @click="setListTab('active')"
          >
            Active partners
          </button>
          <button
            type="button"
            role="tab"
            class="partner-tab"
            :class="{ 'is-active': listTab === 'inactive' }"
            :aria-selected="listTab === 'inactive'"
            @click="setListTab('inactive')"
          >
            Non Active Partner
          </button>
        </div>
      </div>
      <p class="muted">Partners for sales and purchasing - keep them tidy.</p>
      <p class="muted small partner-name-uniq-hint">
        Names are unique within corporate vs non-corporate; caps don't matter (Adhimix = adhimix).
        Same spelling is fine once as corporate and once as non-corporate.
      </p>
    </section>

    <div class="card">
      <h2 class="h2">{{ editingId != null ? 'Edit Partner' : 'Add Partner' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field grow">
          <span>Name <span class="req" aria-hidden="true">*</span></span>
          <input v-model="form.name" required maxlength="100" />
        </label>
        <label class="field compact">
          <span>Phone</span>
          <input v-model="form.phone" maxlength="50" />
        </label>
        <label class="field grow">
          <span>Address</span>
          <input v-model="form.address" maxlength="255" />
        </label>
        <label class="field medium">
          <span>Legal Entity Type</span>
          <select v-model="form.legal_entity_type_id">
            <option :value="null">—</option>
            <option v-for="t in legalEntityTypes" :key="t.id" :value="t.id">
              {{ t.code }} — {{ t.name }}
            </option>
          </select>
          <p v-if="form.legal_entity_type_id != null" class="muted small partner-corporate-note">
            This partner will be treated as corporate.
          </p>
        </label>
        <label class="field medium">
          <span>Parent partner</span>
          <select v-model="form.parent_id">
            <option :value="null">— None —</option>
            <option v-for="p in parentOptions" :key="p.id" :value="p.id">
              {{ p.name || p.phone || '#' + p.id }}
            </option>
          </select>
        </label>
        <label class="field medium">
          <span>Tax ID (NPWP)</span>
          <input
            v-model="form.tax_id"
            maxlength="50"
            placeholder="Optional; unique when set (letter case ignored)"
          />
        </label>
        <label class="field check">
          <span>Is Customer</span>
          <input v-model="form.is_customer" type="checkbox" />
        </label>
        <label class="field check">
          <span>Is Vendor</span>
          <input v-model="form.is_vendor" type="checkbox" />
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

    <div class="card">
      <h2 class="h2">
        {{ listTab === 'active' ? 'Active partners' : 'Non active partners' }}
      </h2>
      <p v-if="listTab === 'inactive'" class="muted partner-tab-hint">
        Edit a partner and turn <strong>Active</strong> on, then save to use it again in sales and
        purchase.
      </p>
      <form class="form-row partner-search-row" @submit.prevent="applySearch">
        <label class="field partner-filter-search">
          <span>Search</span>
          <input
            v-model="searchInput"
            class="partner-filter-search-input"
            type="text"
            placeholder="Search name, phone, address, legal type, parent, or Tax ID"
          />
        </label>
        <label class="field compact">
          <span>Is Corporate</span>
          <select v-model="isCorporateInput">
            <option value="">All</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
          </select>
        </label>
        <button type="submit" class="btn-edit partner-filter-apply">Apply</button>
        <button type="button" class="btn-ghost" @click="clearSearch">Clear</button>
      </form>
      <div v-if="loading" class="muted">Loading…</div>
      <div v-else-if="rows.length === 0" class="muted">
        {{
          filtersApplied
            ? 'No matching partners.'
            : listTab === 'active'
              ? 'No active partners yet.'
              : 'No inactive partners.'
        }}
      </div>
      <div v-else class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Address</th>
            <th>Legal Type</th>
            <th>Parent</th>
            <th>Tax ID (NPWP)</th>
            <th>Corporate</th>
            <th>Is Customer</th>
            <th>Is Vendor</th>
            <th>Active</th>
            <th class="col-actions" />
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td>{{ row.name || '—' }}</td>
            <td>{{ row.phone || '—' }}</td>
            <td>{{ row.address || '—' }}</td>
            <td>
              {{
                row.legal_entity_type_code
                  ? row.legal_entity_type_code
                  : row.legal_entity_type_id != null
                    ? legalEntityTypeById.get(row.legal_entity_type_id)?.code || '—'
                    : '—'
              }}
            </td>
            <td>{{ row.parent_name || '—' }}</td>
            <td>{{ row.tax_id || '—' }}</td>
            <td>
              <span class="pill" :class="row.is_corporate ? 'pill--yes' : 'pill--no'">
                {{ row.is_corporate ? 'Yes' : 'No' }}
              </span>
            </td>
            <td>
              <span class="pill" :class="row.is_customer ? 'pill--yes' : 'pill--no'">
                {{ row.is_customer ? 'Yes' : 'No' }}
              </span>
            </td>
            <td>
              <span class="pill" :class="row.is_vendor ? 'pill--yes' : 'pill--no'">
                {{ row.is_vendor ? 'Yes' : 'No' }}
              </span>
            </td>
            <td>
              <span class="pill" :class="row.is_active !== false ? 'pill--yes' : 'pill--no'">
                {{ row.is_active !== false ? 'Yes' : 'No' }}
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
.partner-head-row {
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
}

.partner-tab-switch {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-left: auto;
}

.partner-tab {
  border: 1px solid #d4e0f3;
  background: #fff;
  color: #334155;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 650;
  padding: 0.28rem 0.72rem;
  cursor: pointer;
}

.partner-tab:hover {
  border-color: #bfd2ee;
  background: #f8fbff;
}

.partner-tab.is-active {
  border-color: #60a5fa;
  background: #eaf3ff;
  color: #1e40af;
}

.partner-tab-hint {
  margin: -0.35rem 0 0.65rem;
  font-size: 0.88rem;
  line-height: 1.4;
}

.partner-filter-apply {
  padding: 0.62rem 1.1rem;
  font-size: 1rem;
  font-weight: 700;
}

.partner-filter-search {
  min-width: 300px;
  max-width: 300px;
  flex: 0 0 300px;
}

.partner-filter-search-input {
  padding: 0.66rem 0.82rem;
  font-size: 1rem;
}

.partner-corporate-note {
  margin: 0;
}

.partner-name-uniq-hint {
  margin: 0.35rem 0 0;
  line-height: 1.35;
}

.partner-search-row {
  margin-bottom: 0.75rem;
}

.pager {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  justify-content: flex-start;
  margin-top: 0.75rem;
}
</style>
