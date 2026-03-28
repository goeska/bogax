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

function setListTab(tab) {
  listTab.value = tab
  load(1)
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

async function load(page = 1) {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/product-categories/', { params: buildListParams(page) })
    applyDrfResponse(data, rows, page)
  } catch {
    err.value = 'Could not load categories.'
    rows.value = []
    totalCount.value = 0
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
    const payload = { name: form.value.name, is_active: form.value.is_active }
    if (editingId.value != null) {
      await api.patch(`/product-categories/${editingId.value}/`, payload)
    } else {
      await api.post('/product-categories/', payload)
    }
    cancelEdit()
    await load(currentPage.value)
  } catch (e) {
    const raw = extractApiErrorText(e.response?.data) || ''
    const msg = String(raw).toLowerCase()
    if (
      msg.includes('category') &&
      (msg.includes('taken') ||
        msg.includes('already') ||
        msg.includes('upper') ||
        msg.includes('letter case'))
    ) {
      err.value =
        "That category name's already taken - try another (upper/lower doesn't matter)."
    } else {
      err.value = raw || 'Could not save - try again.'
    }
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  if (!confirm(`Drop category "${row.name}"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'product-categories', row.id)
    if (editingId.value === row.id) cancelEdit()
    await load(currentPage.value)
  } catch (e) {
    err.value = deactivateErrorMessage(e)
  }
}

const listEmptyLabel = computed(() => {
  if (filtersApplied.value) return 'No matching categories.'
  return listTab.value === 'active' ? 'No active categories yet.' : 'No inactive categories.'
})

onMounted(() => load(1))
</script>

<template>
  <div class="stack">
    <section class="card erp-head">
      <p class="erp-kicker">Master Data</p>
      <div class="erp-title-row category-head-row">
        <h1 class="erp-title">Product Category</h1>
        <div class="category-tab-switch" role="tablist" aria-label="Category list scope">
          <button
            type="button"
            role="tab"
            class="category-tab"
            :class="{ 'is-active': listTab === 'active' }"
            :aria-selected="listTab === 'active'"
            @click="setListTab('active')"
          >
            Active categories
          </button>
          <button
            type="button"
            role="tab"
            class="category-tab"
            :class="{ 'is-active': listTab === 'inactive' }"
            :aria-selected="listTab === 'inactive'"
            @click="setListTab('inactive')"
          >
            Non active categories
          </button>
        </div>
      </div>
      <p class="muted">Bucket your products so search and reports stay sane.</p>
      <p class="muted small category-name-hint">
        Names are one-of-a-kind; caps don't matter (e.g. Rice and rice clash).
      </p>
    </section>

    <div class="card">
      <h2 class="h2">{{ editingId != null ? 'Edit Category' : 'Add Category' }}</h2>
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
      <p class="muted small category-unique-hint">
        No duplicate names anywhere - inactive rows count too.
      </p>
      <p v-if="err" class="error">{{ err }}</p>
    </div>

    <div class="card">
      <h2 class="h2">
        {{ listTab === 'active' ? 'Active categories' : 'Non active categories' }}
      </h2>
      <p v-if="listTab === 'inactive'" class="muted category-tab-hint">
        Edit a category and turn <strong>Active</strong> on, then save to use it again on products.
      </p>
      <form class="form-row category-filter-row" @submit.prevent="applyNameFilter">
        <label class="field category-filter-name">
          <span class="category-filter-label">Name</span>
          <input
            v-model="nameInput"
            class="category-filter-input"
            type="text"
            maxlength="100"
            placeholder="Search…"
            autocomplete="off"
          />
        </label>
        <button type="submit" class="btn-edit category-filter-btn">Apply</button>
        <button type="button" class="btn-ghost category-filter-btn" @click="clearNameFilter">
          Clear
        </button>
      </form>
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
.category-head-row {
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
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

.category-tab-hint {
  margin: -0.35rem 0 0.65rem;
  font-size: 0.88rem;
  line-height: 1.4;
}

.category-name-hint {
  margin-top: 0.35rem;
}

.category-unique-hint {
  margin: 0.5rem 0 0;
  line-height: 1.35;
}

.category-filter-row {
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.35rem 0.45rem;
  margin-bottom: 0.5rem;
}

.category-filter-name {
  min-width: 0;
  max-width: 11rem;
  flex: 0 1 11rem;
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
