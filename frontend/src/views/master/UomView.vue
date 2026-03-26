<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'
import { extractApiErrorText } from '../../utils/apiError'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({ name: '', is_active: true })
const editingId = ref(null)
const saving = ref(false)

async function load() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/uoms/')
    rows.value = data.results ?? data
  } catch {
    err.value = 'Failed to load UOMs.'
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
  form.value = { name: '', is_active: true }
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const payload = { name: form.value.name, is_active: form.value.is_active }
    if (editingId.value != null) {
      await api.patch(`/uoms/${editingId.value}/`, payload)
    } else {
      await api.post('/uoms/', payload)
    }
    cancelEdit()
    await load()
  } catch (e) {
    const raw = extractApiErrorText(e.response?.data) || ''
    const msg = String(raw).toLowerCase()
    if (msg.includes('uom') && msg.includes('already exists')) {
      err.value = 'That UOM name already exists. Please choose another one.'
    } else {
      err.value = raw || 'Could not save. Please try again.'
    }
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
      <p v-if="err" class="error">{{ err }}</p>
    </div>

    <div class="card">
      <h2 class="h2">UOM List</h2>
      <div v-if="loading" class="muted">Loading…</div>
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
              <span class="pill" :class="row.is_active ? 'pill--yes' : 'pill--no'">
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
