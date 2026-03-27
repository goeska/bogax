<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'

const rows = ref([])
const legalEntityTypes = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({
  name: '',
  phone: '',
  address: '',
  legal_entity_type_id: null,
  is_customer: true,
  is_vendor: false,
})
const editingId = ref(null)
const saving = ref(false)
const searchInput = ref('')
const search = ref('')
const isCorporateInput = ref('')
const isCorporate = ref('')

const legalEntityTypeById = computed(() => {
  const map = new Map()
  for (const t of legalEntityTypes.value || []) map.set(t.id, t)
  return map
})

const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  const corp = isCorporate.value
  return rows.value
    .filter((row) => {
      if (corp === 'yes') return row.is_corporate === true
      if (corp === 'no') return row.is_corporate === false
      return true
    })
    .filter((row) => {
    const legalCode =
      row.legal_entity_type_code ||
      (row.legal_entity_type_id != null
        ? legalEntityTypeById.value.get(row.legal_entity_type_id)?.code || ''
        : '')
      if (!q) return true
      return [row.name, row.phone, row.address, legalCode].some((v) =>
        String(v || '')
          .toLowerCase()
          .includes(q),
      )
    })
})

function applySearch() {
  search.value = searchInput.value
  isCorporate.value = isCorporateInput.value
}

function clearSearch() {
  searchInput.value = ''
  search.value = ''
  isCorporateInput.value = ''
  isCorporate.value = ''
}

async function loadLegalEntityTypes() {
  try {
    const { data } = await api.get('/legal-entity-types/')
    legalEntityTypes.value = data.results ?? data
  } catch {
    legalEntityTypes.value = []
  }
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/partners/')
    rows.value = data.results ?? data
  } catch {
    err.value = 'Failed to load partners.'
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
    is_customer: !!row.is_customer,
    is_vendor: !!row.is_vendor,
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
    is_customer: true,
    is_vendor: false,
  }
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const payload = {
      name: form.value.name,
      phone: form.value.phone,
      address: form.value.address,
      legal_entity_type_id: form.value.legal_entity_type_id || null,
      is_customer: !!form.value.is_customer,
      is_vendor: !!form.value.is_vendor,
    }
    if (editingId.value != null) {
      await api.patch(`/partners/${editingId.value}/`, payload)
    } else {
      await api.post('/partners/', payload)
    }
    cancelEdit()
    await load()
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && JSON.stringify(e.response.data)) ||
      'Failed to save.'
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
    await load()
  } catch (e) {
    err.value = deactivateErrorMessage(e)
  }
}

onMounted(async () => {
  await loadLegalEntityTypes()
  await load()
})
</script>

<template>
  <div class="stack">
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
          <p v-if="form.legal_entity_type_id != null" class="muted small" style="margin: 0">
            This partner will be treated as corporate.
          </p>
        </label>
        <label class="field check">
          <span>Is Customer</span>
          <input v-model="form.is_customer" type="checkbox" />
        </label>
        <label class="field check">
          <span>Is Vendor</span>
          <input v-model="form.is_vendor" type="checkbox" />
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
      <h2 class="h2">Partner List</h2>
      <form class="form-row" style="margin-bottom: 0.75rem" @submit.prevent="applySearch">
        <label class="field partner-filter-search">
          <span>Search</span>
          <input
            v-model="searchInput"
            class="partner-filter-search-input"
            type="text"
            placeholder="Search name, phone, address, or legal type"
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
      <div v-else-if="filteredRows.length === 0" class="muted">No matching partners.</div>
      <div v-else class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Address</th>
            <th>Legal Type</th>
            <th>Corporate</th>
            <th>Is Customer</th>
            <th>Is Vendor</th>
            <th class="col-actions" />
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredRows" :key="row.id">
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
            <td class="col-actions">
              <button type="button" class="link-btn" @click="startEdit(row)">Edit</button>
              <button type="button" class="link-btn danger" @click="remove(row)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
</style>
