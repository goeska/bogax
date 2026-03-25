<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({ name: '', phone: '', is_customer: true, is_vendor: false })
const editingId = ref(null)
const saving = ref(false)

async function load() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/partners/')
    rows.value = data.results ?? data
  } catch {
    err.value = 'Failed to load partners.'
  } finally {
    loading.value = false
  }
}

function startEdit(row) {
  editingId.value = row.id
  form.value = {
    name: row.name ?? '',
    phone: row.phone ?? '',
    is_customer: !!row.is_customer,
    is_vendor: !!row.is_vendor,
  }
  err.value = ''
}

function cancelEdit() {
  editingId.value = null
  form.value = { name: '', phone: '', is_customer: true, is_vendor: false }
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const payload = {
      name: form.value.name,
      phone: form.value.phone,
      is_customer: !!form.value.is_customer,
      is_vendor: !!form.value.is_vendor,
    }
    if (editingId.value != null) {
      await api.patch(`/partners/${editingId.value}/`, payload)
    } else {
      await api.post('/partners/', payload)
    }
    cancelEdit()
    await load()
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && JSON.stringify(e.response.data)) ||
      'Failed to save.'
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  if (!confirm(`Delete partner "${row.name || row.phone || row.id}"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'partners', row.id)
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
      <h2 class="h2">{{ editingId != null ? 'Edit Partner' : 'Add Partner' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field grow">
          <span>Name</span>
          <input v-model="form.name" required maxlength="100" />
        </label>
        <label class="field grow">
          <span>Phone</span>
          <input v-model="form.phone" maxlength="50" />
        </label>
        <label class="field check">
          <span>Is Customer</span>
          <input v-model="form.is_customer" type="checkbox" />
        </label>
        <label class="field check">
          <span>Is Vendor</span>
          <input v-model="form.is_vendor" type="checkbox" />
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
      <h2 class="h2">Partner List</h2>
      <div v-if="loading" class="muted">Loading…</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Is Customer</th>
            <th>Is Vendor</th>
            <th class="col-actions" />
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td>{{ row.name || '—' }}</td>
            <td>{{ row.phone || '—' }}</td>
            <td>{{ row.is_customer ? 'Yes' : 'No' }}</td>
            <td>{{ row.is_vendor ? 'Yes' : 'No' }}</td>
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
