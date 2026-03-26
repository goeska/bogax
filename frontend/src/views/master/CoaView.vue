<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const saving = ref(false)
const editingId = ref(null)

const form = ref({
  code: '',
  name: '',
  parent_id: null,
  is_active: true,
})

const topLevelOptions = computed(() =>
  (rows.value || []).filter((r) => r.parent_id == null),
)

function resetForm() {
  editingId.value = null
  form.value = {
    code: '',
    name: '',
    parent_id: null,
    is_active: true,
  }
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/coas/')
    rows.value = data.results ?? data
  } catch (e) {
    err.value = e.response?.data?.detail || 'Failed to load CoA.'
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
    parent_id: row.parent_id ?? null,
    is_active: Boolean(row.is_active),
  }
  err.value = ''
}

function cancelEdit() {
  resetForm()
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const payload = {
      code: form.value.code.trim(),
      name: form.value.name.trim(),
      parent_id: form.value.parent_id || null,
      is_active: form.value.is_active,
    }
    if (!payload.code || !payload.name) throw new Error('Code and Name are required.')

    if (editingId.value != null) {
      await api.patch(`/coas/${editingId.value}/`, payload)
    } else {
      await api.post('/coas/', payload)
    }
    resetForm()
    await load()
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && JSON.stringify(e.response.data)) ||
      e.message ||
      'Failed to save.'
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  const label = `${row.code} ${row.name}`.trim()
  if (!confirm(`Delete CoA \"${label}\"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'coas', row.id)
    if (editingId.value === row.id) resetForm()
    await load()
  } catch (e) {
    err.value = deactivateErrorMessage(e)
  }
}

const childrenByParent = computed(() => {
  const map = new Map()
  for (const r of rows.value || []) {
    const pid = r.parent_id ?? null
    if (!map.has(pid)) map.set(pid, [])
    map.get(pid).push(r)
  }
  for (const [k, arr] of map.entries()) {
    arr.sort((a, b) => String(a.code || '').localeCompare(String(b.code || '')))
    map.set(k, arr)
  }
  return map
})

const topLevelRows = computed(() => childrenByParent.value.get(null) || [])

onMounted(load)
</script>

<template>
  <div class="stack">
    <div class="card">
      <h2 class="h2">{{ editingId != null ? 'Edit CoA' : 'Add CoA' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field">
          <span>Code <span class="req" aria-hidden="true">*</span></span>
          <input v-model="form.code" required maxlength="50" placeholder="e.g. 1000" />
        </label>
        <label class="field">
          <span>Parent (optional)</span>
          <select v-model="form.parent_id">
            <option :value="null">— Top level —</option>
            <option v-for="p in topLevelOptions" :key="p.id" :value="p.id">
              {{ p.code }} — {{ p.name }}
            </option>
          </select>
        </label>
        <label class="field grow">
          <span>Name <span class="req" aria-hidden="true">*</span></span>
          <input v-model="form.name" required maxlength="255" placeholder="e.g. Cash" />
        </label>
        <label class="field check">
          <span>Active</span>
          <input v-model="form.is_active" type="checkbox" />
        </label>
        <button class="btn-primary" type="submit" :disabled="saving">
          {{ saving ? 'Saving…' : editingId != null ? 'Save Changes' : 'Save' }}
        </button>
        <button v-if="editingId != null" type="button" class="btn-ghost main-only" @click="cancelEdit">
          Cancel
        </button>
      </form>
      <p v-if="err" class="error">{{ err }}</p>
      <p class="muted small" style="margin: 0.5rem 0 0">
        2-level only: parent must be a top-level CoA.
      </p>
    </div>

    <div class="card">
      <h2 class="h2">CoA List</h2>
      <div v-if="loading" class="muted">Loading…</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Code</th>
            <th>Parent</th>
            <th>Name</th>
            <th>Active</th>
            <th class="col-actions" />
          </tr>
        </thead>
        <tbody>
          <template v-for="p in topLevelRows" :key="p.id">
            <tr>
              <td><strong>{{ p.code }}</strong></td>
              <td>—</td>
              <td><strong>{{ p.name }}</strong></td>
              <td>{{ p.is_active ? 'Yes' : 'No' }}</td>
              <td class="col-actions">
                <button type="button" class="link-btn" @click="startEdit(p)">Edit</button>
                <button type="button" class="link-btn danger" @click="remove(p)">Delete</button>
              </td>
            </tr>
            <tr v-for="c in (childrenByParent.get(p.id) || [])" :key="c.id">
              <td style="padding-left: 1.25rem">↳ {{ c.code }}</td>
              <td>{{ p.code }}</td>
              <td>{{ c.name }}</td>
              <td>{{ c.is_active ? 'Yes' : 'No' }}</td>
              <td class="col-actions">
                <button type="button" class="link-btn" @click="startEdit(c)">Edit</button>
                <button type="button" class="link-btn danger" @click="remove(c)">Delete</button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

