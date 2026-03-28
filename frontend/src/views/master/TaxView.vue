<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'
import { extractApiErrorText } from '../../utils/apiError'
import { usePagination } from '../../utils/pagination'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({ name: '', rate_percent: '', is_active: true })
const editingId = ref(null)
const saving = ref(false)
const listTab = ref('active')
const nameInput = ref('')
const nameFilter = ref('')
const filtersApplied = ref(false)

const pag = usePagination(25)
const { currentPage, totalCount, totalPages, applyDrfResponse } = pag
const { prevPage, nextPage } = pag.makePager(loading, load)

function defaultForm() {
  return { name: '', rate_percent: '', is_active: true }
}

function buildListParams(page) {
  const p = { page }
  p.is_active = listTab.value === 'active' ? 'true' : 'false'
  const n = nameFilter.value.trim()
  if (n) p.name = n
  return p
}

function applyNameFilter() {
  nameFilter.value = nameInput.value
  filtersApplied.value = Boolean(nameFilter.value.trim())
  load(1)
}

function clearNameFilter() {
  nameInput.value = ''
  nameFilter.value = ''
  filtersApplied.value = false
  load(1)
}

function setListTab(tab) {
  listTab.value = tab
  load(1)
}

async function load(page = 1) {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/taxes/', { params: buildListParams(page) })
    applyDrfResponse(data, rows, page)
  } catch {
    rows.value = []
    totalCount.value = 0
    err.value = 'Could not load taxes.'
  } finally {
    loading.value = false
  }
}

function startEdit(row) {
  editingId.value = row.id
  form.value = {
    name: row.name,
    rate_percent: row.rate_percent,
    is_active: row.is_active,
  }
  err.value = ''
}

function cancelEdit() {
  editingId.value = null
  form.value = defaultForm()
}

function payloadFromForm() {
  const rate = String(form.value.rate_percent).trim()
  const num = rate === '' ? NaN : Number(rate)
  if (Number.isNaN(num)) {
    throw new Error('Rate needs to be a number.')
  }
  return {
    name: form.value.name,
    rate_percent: num,
    is_active: form.value.is_active,
  }
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const wasEditing = editingId.value != null
    const payload = payloadFromForm()
    if (wasEditing) {
      await api.patch(`/taxes/${editingId.value}/`, payload)
    } else {
      await api.post('/taxes/', payload)
    }
    cancelEdit()
    await load(wasEditing ? currentPage.value : 1)
  } catch (e) {
    if (e.message && e.message.includes('Rate')) {
      err.value = e.message
    } else {
      err.value = extractApiErrorText(e.response?.data) || 'Could not save.'
    }
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  if (!confirm(`Delete tax "${row.name}"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'taxes', row.id)
    if (editingId.value === row.id) cancelEdit()
    await load(currentPage.value)
  } catch (e) {
    err.value = deactivateErrorMessage(e)
  }
}

const listEmptyLabel = computed(() => {
  if (filtersApplied.value) return 'No matching taxes.'
  return listTab.value === 'active' ? 'No active taxes yet.' : 'No inactive taxes yet.'
})

onMounted(() => load(1))
</script>

<template>
  <div class="stack">
    <section class="card erp-head">
      <p class="erp-kicker">Master Data</p>
      <div class="erp-title-row tax-head-row">
        <h1 class="erp-title">Tax Management</h1>
        <div class="tax-tab-switch" role="tablist" aria-label="Tax list scope">
          <button
            type="button"
            role="tab"
            class="tax-tab"
            :class="{ 'is-active': listTab === 'active' }"
            :aria-selected="listTab === 'active'"
            @click="setListTab('active')"
          >
            Active taxes
          </button>
          <button
            type="button"
            role="tab"
            class="tax-tab"
            :class="{ 'is-active': listTab === 'inactive' }"
            :aria-selected="listTab === 'inactive'"
            @click="setListTab('inactive')"
          >
            Inactive taxes
          </button>
        </div>
      </div>
      <p class="muted">Maintain tax definitions used on sales and purchase transactions.</p>
    </section>

    <div class="card">
      <h2 class="h2">{{ editingId != null ? 'Edit Tax' : 'Add Tax' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field tax-name-field">
          <span>Name <span class="req" aria-hidden="true">*</span></span>
          <input v-model="form.name" required maxlength="100" />
        </label>
        <label class="field narrow">
          <span>Rate (%) <span class="req" aria-hidden="true">*</span></span>
          <input
            v-model="form.rate_percent"
            type="number"
            step="0.01"
            min="0"
            required
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

    <div class="card">
      <h2 class="h2">{{ listTab === 'active' ? 'Active taxes' : 'Inactive taxes' }}</h2>
      <form class="form-row tax-filter-row" @submit.prevent="applyNameFilter">
        <label class="field tax-filter-name">
          <span class="tax-filter-label">Name</span>
          <input
            v-model="nameInput"
            class="tax-filter-input"
            type="text"
            maxlength="100"
            placeholder="Search…"
            autocomplete="off"
          />
        </label>
        <button type="submit" class="btn-edit tax-filter-btn">Apply</button>
        <button type="button" class="btn-ghost tax-filter-btn" @click="clearNameFilter">
          Clear
        </button>
      </form>
      <div v-if="loading" class="muted">Loading…</div>
      <div v-else-if="rows.length === 0" class="muted">{{ listEmptyLabel }}</div>
      <div v-else class="table-wrap">
        <table class="table tax-table">
          <thead>
            <tr>
              <th class="tax-col-name">Name</th>
              <th class="tax-col-rate">Rate (%)</th>
              <th>Active</th>
              <th class="col-actions" />
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td class="tax-col-name" :title="row.name">{{ row.name }}</td>
              <td class="tax-col-rate">{{ row.rate_percent }}</td>
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
.tax-head-row {
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
}

.tax-tab-switch {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-left: auto;
}

.tax-tab {
  border: 1px solid #d4e0f3;
  background: #fff;
  color: #334155;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 650;
  padding: 0.28rem 0.72rem;
  cursor: pointer;
}

.tax-tab:hover {
  border-color: #bfd2ee;
  background: #f8fbff;
}

.tax-tab.is-active {
  border-color: #60a5fa;
  background: #eaf3ff;
  color: #1e40af;
}

.tax-filter-row {
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.35rem 0.45rem;
  margin-bottom: 0.5rem;
}

.tax-filter-name {
  min-width: 0;
  max-width: 11rem;
  flex: 0 1 11rem;
  margin: 0;
}

.tax-filter-label {
  font-size: 0.78rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.tax-filter-input {
  padding: 0.38rem 0.5rem;
  font-size: 0.8125rem;
  line-height: 1.25;
}

.tax-filter-btn {
  padding: 0.38rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 600;
}

.tax-name-field {
  min-width: 0;
  max-width: 18rem;
  flex: 0 1 18rem;
}

.tax-table {
  table-layout: fixed;
  width: 100%;
}

.tax-col-name {
  width: 36%;
  max-width: 24rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tax-col-rate {
  width: 8.5rem;
}

.pager {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  justify-content: flex-start;
  margin-top: 0.75rem;
}
</style>
