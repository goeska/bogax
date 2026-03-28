<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'
import { extractApiErrorText } from '../../utils/apiError'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({ name: '', is_active: true })
const editingId = ref(null)
const saving = ref(false)

const listTab = ref('active')

const activeRows = computed(() => rows.value.filter((r) => r.is_active !== false))
const inactiveRows = computed(() => rows.value.filter((r) => r.is_active === false))
const displayedRows = computed(() =>
  listTab.value === 'active' ? activeRows.value : inactiveRows.value,
)

function defaultForm() {
  return { name: '', is_active: true }
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/table-numbers/')
    rows.value = data.results ?? data
  } catch {
    err.value = 'Could not load table numbers.'
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

function payloadFromForm() {
  const raw = String(form.value.name).trim()
  if (raw === '') {
    throw new Error('Add a table number.')
  }
  const n = Number.parseInt(raw, 10)
  if (Number.isNaN(n) || String(n) !== raw) {
    throw new Error('Number must be an integer (smallint column).')
  }
  if (n < -32768 || n > 32767) {
    throw new Error('Number is out of smallint range.')
  }
  return { name: n, is_active: form.value.is_active }
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const payload = payloadFromForm()
    if (editingId.value != null) {
      await api.patch(`/table-numbers/${editingId.value}/`, payload)
    } else {
      await api.post('/table-numbers/', payload)
    }
    cancelEdit()
    await load()
  } catch (e) {
    if (e instanceof Error && !e.response) {
      err.value = e.message
    } else {
      const status = e.response?.status
      const data = e.response?.data
      const raw = extractApiErrorText(data) || ''
      const msg = String(raw).toLowerCase()

      const looksLikeUnique =
        msg.includes('duplicate') ||
        msg.includes('unique') ||
        msg.includes('already exists') ||
        msg.includes('unique_table_number_name') ||
        msg.includes('ux_table_number_name_active') ||
        msg.includes('table_number') ||
        msg.includes('table number')

      if ((status === 400 || status === 409 || status === 500) && looksLikeUnique) {
        err.value =
          'This table number is already used (unique on all rows, including inactive). ' +
          'Pick another number or open Non Active Table, edit the row, and set Active.'
      } else {
        err.value = raw || 'Could not save - try again.'
      }
    }
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  if (!confirm(`Delete table number ${row.name}?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'table-numbers', row.id)
    if (editingId.value === row.id) cancelEdit()
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
      <div class="erp-title-row table-head-row">
        <h1 class="erp-title">Resto Table</h1>
        <div class="table-tab-switch" role="tablist" aria-label="Table list scope">
          <button
            type="button"
            role="tab"
            class="table-tab"
            :class="{ 'is-active': listTab === 'active' }"
            :aria-selected="listTab === 'active'"
            @click="listTab = 'active'"
          >
            Active tables
          </button>
          <button
            type="button"
            role="tab"
            class="table-tab"
            :class="{ 'is-active': listTab === 'inactive' }"
            :aria-selected="listTab === 'inactive'"
            @click="listTab = 'inactive'"
          >
            Non Active Table
          </button>
        </div>
      </div>
      <p class="muted">Configure table numbers for restaurant operations.</p>
    </section>

    <div class="card">
      <h2 class="h2">{{ editingId != null ? 'Edit Table' : 'Add Table' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field narrow">
          <span>Name (number) <span class="req" aria-hidden="true">*</span></span>
          <input
            v-model="form.name"
            type="number"
            step="1"
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
      <p class="muted small table-unique-hint">
        Table numbers don't repeat - inactive rows still count.
      </p>
      <p v-if="err" class="error">{{ err }}</p>
    </div>

    <div class="card">
      <h2 class="h2">
        {{ listTab === 'active' ? 'Active tables' : 'Non active tables' }}
      </h2>
      <p v-if="listTab === 'inactive'" class="muted table-tab-hint">
        Edit a table and turn <strong>Active</strong> on, then save to use it again on POS.
        You cannot add a duplicate number while an inactive row still holds that value—database
        enforces <code class="table-code">UNIQUE (name)</code> on all rows.
      </p>
      <div v-if="loading" class="muted">Loading…</div>
      <div v-else-if="displayedRows.length === 0" class="muted">
        {{ listTab === 'active' ? 'No active tables yet.' : 'No inactive tables.' }}
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
            <tr v-for="row in displayedRows" :key="row.id">
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
    </div>
  </div>
</template>

<style scoped>
.table-head-row {
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
}

.table-tab-switch {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-left: auto;
}

.table-tab {
  border: 1px solid #d4e0f3;
  background: #fff;
  color: #334155;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 650;
  padding: 0.28rem 0.72rem;
  cursor: pointer;
}

.table-tab:hover {
  border-color: #bfd2ee;
  background: #f8fbff;
}

.table-tab.is-active {
  border-color: #60a5fa;
  background: #eaf3ff;
  color: #1e40af;
}

.table-tab-hint {
  margin: -0.35rem 0 0.65rem;
  font-size: 0.88rem;
  line-height: 1.4;
}

.table-unique-hint {
  margin: 0.5rem 0 0;
  line-height: 1.35;
}

.table-code {
  font-size: 0.85em;
}
</style>
