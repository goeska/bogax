<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({ name: '', rate_percent: '', is_active: true })
const editingId = ref(null)
const saving = ref(false)

function defaultForm() {
  return { name: '', rate_percent: '', is_active: true }
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/taxes/')
    rows.value = data.results ?? data
  } catch {
    err.value = 'Failed to load taxes.'
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
    throw new Error('Rate (%) must be a number.')
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
    const payload = payloadFromForm()
    if (editingId.value != null) {
      await api.patch(`/taxes/${editingId.value}/`, payload)
    } else {
      await api.post('/taxes/', payload)
    }
    cancelEdit()
    await load()
  } catch (e) {
    if (e.message && e.message.includes('Rate')) {
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
  if (!confirm(`Delete tax "${row.name}"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'taxes', row.id)
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
      <h2 class="h2">{{ editingId != null ? 'Edit Tax' : 'Add Tax' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field grow">
          <span>Name</span>
          <input v-model="form.name" required maxlength="100" />
        </label>
        <label class="field narrow">
          <span>Rate (%)</span>
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
      <h2 class="h2">Tax List</h2>
      <div v-if="loading" class="muted">Loading…</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Rate (%)</th>
            <th>Active</th>
            <th class="col-actions" />
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td>{{ row.name }}</td>
            <td>{{ row.rate_percent }}</td>
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
