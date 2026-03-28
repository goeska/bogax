<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'
import { extractApiErrorText } from '../../utils/apiError'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const saving = ref(false)
const editingId = ref(null)

const form = ref({ code: '', name: '', is_active: true })

/** 'active' = active types only; 'inactive' = soft-deleted / inactive, editable back to active */
const listTab = ref('active')

const activeRows = computed(() => rows.value.filter((r) => r.is_active !== false))
const inactiveRows = computed(() => rows.value.filter((r) => r.is_active === false))
const displayedRows = computed(() =>
  listTab.value === 'active' ? activeRows.value : inactiveRows.value,
)

function resetForm() {
  editingId.value = null
  form.value = { code: '', name: '', is_active: true }
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/legal-entity-types/')
    rows.value = data.results ?? data
  } catch {
    err.value = 'Could not load legal entity types.'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function startEdit(row) {
  editingId.value = row.id
  form.value = {
    code: row.code ?? '',
    name: row.name ?? '',
    is_active: row.is_active !== false,
  }
  err.value = ''
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const payload = {
      code: String(form.value.code || '').trim(),
      name: String(form.value.name || '').trim(),
      is_active: !!form.value.is_active,
    }
    if (!payload.code) throw new Error('Add a code.')
    if (!payload.name) throw new Error('Add a name.')

    if (editingId.value != null) {
      await api.patch(`/legal-entity-types/${editingId.value}/`, payload)
    } else {
      await api.post('/legal-entity-types/', payload)
    }
    resetForm()
    await load()
  } catch (e) {
    const raw = extractApiErrorText(e.response?.data) || ''
    const msg = String(raw).toLowerCase()

    const looksLikeDuplicateCode =
      msg.includes('code') &&
      (msg.includes('already exists') ||
        msg.includes('unique') ||
        msg.includes('duplicate'))

    if (looksLikeDuplicateCode) {
      err.value = "That code's taken - try another."
    } else {
      err.value = raw || e.message || 'Could not save - try again.'
    }
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  if (!confirm(`Delete legal entity type "${row.code} - ${row.name}"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'legal-entity-types', row.id)
    if (editingId.value === row.id) resetForm()
    await load()
  } catch (e) {
    err.value = deactivateErrorMessage(e)
  }
}

onMounted(load)
</script>

<template>
  <div class="stack">
    <section class="card erp-head">
      <p class="erp-kicker">Master Data</p>
      <div class="erp-title-row let-head-row">
        <h1 class="erp-title">Legal Entity Type</h1>
        <div class="let-tab-switch" role="tablist" aria-label="Legal entity type scope">
          <button
            type="button"
            role="tab"
            class="let-tab"
            :class="{ 'is-active': listTab === 'active' }"
            :aria-selected="listTab === 'active'"
            @click="listTab = 'active'"
          >
            Active types
          </button>
          <button
            type="button"
            role="tab"
            class="let-tab"
            :class="{ 'is-active': listTab === 'inactive' }"
            :aria-selected="listTab === 'inactive'"
            @click="listTab = 'inactive'"
          >
            Non Active Type
          </button>
        </div>
      </div>
      <p class="muted">Classification of your organization's legal status.</p>
    </section>

    <div class="card">
      <h2 class="h2">{{ editingId != null ? 'Edit Legal Entity Type' : 'Add Legal Entity Type' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field compact">
          <span>Code <span class="req" aria-hidden="true">*</span></span>
          <input v-model="form.code" required maxlength="10" />
        </label>
        <label class="field medium">
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
        <button v-if="editingId != null" type="button" class="btn-ghost main-only" @click="resetForm">
          Cancel
        </button>
      </form>
      <p v-if="err" class="error">{{ err }}</p>
    </div>

    <div class="card">
      <h2 class="h2">
        {{ listTab === 'active' ? 'Active types' : 'Non active types' }}
      </h2>
      <p v-if="listTab === 'inactive'" class="muted let-tab-hint">
        Edit a row and turn <strong>Active</strong> on, then save to use it again for corporate partners.
      </p>
      <div v-if="loading" class="muted">Loading…</div>
      <div v-else-if="displayedRows.length === 0" class="muted">
        {{ listTab === 'active' ? 'No active legal entity types yet.' : 'No inactive types.' }}
      </div>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Active</th>
              <th class="col-actions" />
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in displayedRows" :key="row.id">
              <td>{{ row.code }}</td>
              <td>{{ row.name }}</td>
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
    </div>
  </div>
</template>

<style scoped>
.let-head-row {
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
}

.let-tab-switch {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-left: auto;
}

.let-tab {
  border: 1px solid #d4e0f3;
  background: #fff;
  color: #334155;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 650;
  padding: 0.28rem 0.72rem;
  cursor: pointer;
}

.let-tab:hover {
  border-color: #bfd2ee;
  background: #f8fbff;
}

.let-tab.is-active {
  border-color: #60a5fa;
  background: #eaf3ff;
  color: #1e40af;
}

.let-tab-hint {
  margin: -0.35rem 0 0.65rem;
  font-size: 0.88rem;
  line-height: 1.4;
}

.table-wrap {
  overflow-x: auto;
}
</style>

