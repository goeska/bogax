<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'

const rows = ref([])
const partners = ref([])
const loading = ref(true)
const partnersLoading = ref(false)
const err = ref('')
const saving = ref(false)
const editingId = ref(null)

const form = ref({
  name: '',
  partner_id: null,
  is_active: true,
})

const partnerById = computed(() => {
  const map = new Map()
  for (const p of partners.value || []) map.set(p.id, p)
  return map
})

function resetForm() {
  editingId.value = null
  form.value = { name: '', partner_id: null, is_active: true }
}

async function loadPartners() {
  partnersLoading.value = true
  try {
    const { data } = await api.get('/partners/', { params: { is_corporate: '1' } })
    partners.value = data.results ?? data
  } catch {
    partners.value = []
  } finally {
    partnersLoading.value = false
  }
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/projects/')
    rows.value = data.results ?? data
  } catch {
    err.value = 'Could not load projects. Please try again.'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function startEdit(row) {
  editingId.value = row.id
  form.value = {
    name: row.name ?? '',
    partner_id: row.partner_id ?? null,
    is_active: row.is_active !== false,
  }
  err.value = ''
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const payload = {
      name: String(form.value.name || '').trim(),
      partner_id: form.value.partner_id,
      is_active: !!form.value.is_active,
    }
    if (!payload.name) throw new Error('Project name is required.')
    if (!payload.partner_id) throw new Error('Corporate partner is required.')

    if (editingId.value != null) {
      await api.patch(`/projects/${editingId.value}/`, payload)
    } else {
      await api.post('/projects/', payload)
    }
    resetForm()
    await load()
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && JSON.stringify(e.response.data)) ||
      e.message ||
      'Could not save. Please try again.'
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  const label = row.code || row.name || `#${row.id}`
  if (!confirm(`Delete project "${label}"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'projects', row.id)
    if (editingId.value === row.id) resetForm()
    await load()
  } catch (e) {
    err.value = deactivateErrorMessage(e)
  }
}

onMounted(async () => {
  await loadPartners()
  await load()
})
</script>

<template>
  <div class="stack">
    <div class="card">
      <h2 class="h2">{{ editingId != null ? 'Edit Project' : 'Add Project' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field grow">
          <span>Name <span class="req" aria-hidden="true">*</span></span>
          <input v-model="form.name" required maxlength="255" />
        </label>
        <label class="field grow">
          <span>Corporate Partner <span class="req" aria-hidden="true">*</span></span>
          <select v-model="form.partner_id" :disabled="partnersLoading" required>
            <option :value="null" disabled>Select…</option>
            <option v-for="p in partners" :key="p.id" :value="p.id">
              {{ p.name || `#${p.id}` }}{{ p.phone ? ` — ${p.phone}` : '' }}
            </option>
          </select>
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
      <h2 class="h2">Project List</h2>
      <div v-if="loading" class="muted">Loading…</div>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Partner</th>
              <th>Active</th>
              <th class="col-actions" />
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>{{ row.code || '—' }}</td>
              <td>{{ row.name || '—' }}</td>
              <td>{{ (partnerById.get(row.partner_id)?.name ?? row.partner_name) || '—' }}</td>
              <td>
                <span class="state-pill" :class="row.is_active ? 'state-pill--active' : 'state-pill--inactive'">
                  {{ row.is_active ? 'Yes' : 'No' }}
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
.table-wrap {
  overflow-x: auto;
}

.state-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.45rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1px solid transparent;
}

.state-pill--active {
  color: #15803d;
  background: #dcfce7;
  border-color: #bbf7d0;
}

.state-pill--inactive {
  color: #64748b;
  background: #f1f5f9;
  border-color: #e2e8f0;
}
</style>

