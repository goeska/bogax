<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'
import { extractApiErrorText } from '../../utils/apiError'
import { usePagination } from '../../utils/pagination'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({ name: '', is_active: true })
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
  return { name: '', is_active: true }
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
    const { data } = await api.get('/uoms/', { params: buildListParams(page) })
    applyDrfResponse(data, rows, page)
  } catch (e) {
    rows.value = []
    totalCount.value = 0
    err.value =
      extractApiErrorText(e.response?.data) ||
      (e.response?.status ? `Could not load UOMs (HTTP ${e.response.status}).` : '') ||
      e.message ||
      'Could not load UOMs.'
  } finally {
    loading.value = false
  }
}

function startEdit(row) {
  editingId.value = row.id
  form.value = { name: row.name, is_active: row.is_active !== false }
  err.value = ''
}

function cancelEdit() {
  editingId.value = null
  form.value = defaultForm()
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const wasEditing = editingId.value != null
    const payload = { name: form.value.name, is_active: form.value.is_active }
    if (wasEditing) {
      await api.patch(`/uoms/${editingId.value}/`, payload)
    } else {
      await api.post('/uoms/', payload)
    }
    cancelEdit()
    await load(wasEditing ? currentPage.value : 1)
  } catch (e) {
    err.value = extractApiErrorText(e.response?.data) || 'Could not save - try again.'
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  if (!confirm(`Delete UOM "${row.name}"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'uoms', row.id)
    if (editingId.value === row.id) cancelEdit()
    await load(currentPage.value)
  } catch (e) {
    err.value = deactivateErrorMessage(e)
  }
}

const listEmptyLabel = computed(() => {
  if (filtersApplied.value) return 'No matching UOMs.'
  return listTab.value === 'active' ? 'No active UOMs yet.' : 'No inactive UOMs yet.'
})

onMounted(() => load(1))
</script>

<template>
  <div class="stack">
    <section class="card erp-head">
      <p class="erp-kicker">Master Data</p>
      <div class="erp-title-row uom-head-row">
        <h1 class="erp-title">UOM Management</h1>
        <div class="uom-tab-switch" role="tablist" aria-label="UOM list scope">
          <button
            type="button"
            role="tab"
            class="uom-tab"
            :class="{ 'is-active': listTab === 'active' }"
            :aria-selected="listTab === 'active'"
            @click="setListTab('active')"
          >
            Active UOMs
          </button>
          <button
            type="button"
            role="tab"
            class="uom-tab"
            :class="{ 'is-active': listTab === 'inactive' }"
            :aria-selected="listTab === 'inactive'"
            @click="setListTab('inactive')"
          >
            Inactive UOMs
          </button>
        </div>
      </div>
      <p class="muted">Keep units of measure consistent across transactions and reports.</p>
    </section>

    <div class="card">
      <h2 class="h2">{{ editingId != null ? 'Edit UOM' : 'Add UOM' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field compact">
          <span>Name <span class="req" aria-hidden="true">*</span></span>
          <input v-model="form.name" required maxlength="100" />
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
      <p class="muted small uom-unique-hint">
        One UOM name for the whole list (caps do not matter); inactive rows still count.
      </p>
      <p v-if="err" class="error">{{ err }}</p>
    </div>

    <div class="card">
      <h2 class="h2">
        {{ listTab === 'active' ? 'Active UOMs' : 'Inactive UOMs' }}
      </h2>
      <form class="form-row uom-filter-row" @submit.prevent="applyNameFilter">
        <label class="field uom-filter-name">
          <span class="uom-filter-label">Name</span>
          <input
            v-model="nameInput"
            class="uom-filter-input"
            type="text"
            maxlength="100"
            placeholder="Search…"
            autocomplete="off"
          />
        </label>
        <button type="submit" class="btn-edit uom-filter-btn">Apply</button>
        <button type="button" class="btn-ghost uom-filter-btn" @click="clearNameFilter">
          Clear
        </button>
      </form>
      <p v-if="listTab === 'inactive'" class="muted uom-tab-hint">
        Edit a unit and turn <strong>Active</strong> on, then save to use it again on products.
      </p>
      <div v-if="loading" class="muted">Loading…</div>
      <div v-else-if="rows.length === 0" class="muted">
        {{ listEmptyLabel }}
      </div>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Active</th>
              <th class="col-actions" />
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>{{ row.name }}</td>
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
.uom-head-row {
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
}

.uom-tab-switch {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-left: auto;
}

.uom-tab {
  border: 1px solid #d4e0f3;
  background: #fff;
  color: #334155;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 650;
  padding: 0.28rem 0.72rem;
  cursor: pointer;
}

.uom-tab:hover {
  border-color: #bfd2ee;
  background: #f8fbff;
}

.uom-tab.is-active {
  border-color: #60a5fa;
  background: #eaf3ff;
  color: #1e40af;
}

.uom-tab-hint {
  margin: -0.35rem 0 0.65rem;
  font-size: 0.88rem;
  line-height: 1.4;
}

.uom-filter-row {
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.35rem 0.45rem;
  margin-bottom: 0.5rem;
}

.uom-filter-name {
  min-width: 0;
  max-width: 11rem;
  flex: 0 1 11rem;
  margin: 0;
}

.uom-filter-label {
  font-size: 0.78rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.uom-filter-input {
  padding: 0.38rem 0.5rem;
  font-size: 0.8125rem;
  line-height: 1.25;
}

.uom-filter-btn {
  padding: 0.38rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 600;
}

.uom-unique-hint {
  margin: 0.5rem 0 0;
  line-height: 1.35;
}

.pager {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  justify-content: flex-start;
  margin-top: 0.75rem;
}
</style>
