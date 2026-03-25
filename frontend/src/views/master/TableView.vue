<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({ name: '', is_active: true })
const editingId = ref(null)
const saving = ref(false)

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
    err.value = 'Failed to load table numbers.'
  } finally {
    loading.value = false
  }
}

function startEdit(row) {
  editingId.value = row.id
  form.value = { name: row.name, is_active: row.is_active }
  err.value = ''
}

function cancelEdit() {
  editingId.value = null
  form.value = defaultForm()
}

function payloadFromForm() {
  const raw = String(form.value.name).trim()
  if (raw === '') {
    throw new Error('Number (name) is required.')
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
      err.value =
        e.response?.data?.detail ||
        (typeof e.response?.data === 'object' && JSON.stringify(e.response.data)) ||
        'Failed to save.'
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
    <div class="card">
      <h2 class="h2">{{ editingId != null ? 'Edit Table' : 'Add Table' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field narrow">
          <span>Name (number)</span>
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
      <p v-if="err" class="error">{{ err }}</p>
    </div>

    <div class="card">
      <h2 class="h2">Table List</h2>
      <div v-if="loading" class="muted">Loading…</div>
      <table v-else class="table">
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
            <td>{{ row.is_active ? 'Yes' : 'No' }}</td>
            <td class="col-actions">
              <button type="button" class="link-btn" @click="startEdit(row)">Edit</button>
              <button type="button" class="link-btn danger" @click="remove(row)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
