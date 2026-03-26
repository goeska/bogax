<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'
import { extractApiErrorText } from '../../utils/apiError'

const rows = ref([])
const loading = ref(true)
const err = ref('')
const saving = ref(false)
const editingId = ref(null)

const form = ref({ code: '', name: '', is_active: true })

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
    err.value = 'Could not load legal entity types. Please try again.'
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
    if (!payload.code) throw new Error('Code is required.')
    if (!payload.name) throw new Error('Name is required.')

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
        msg.includes('duplicate') ||
        msg.includes('telah ada'))

    if (looksLikeDuplicateCode) {
      err.value = 'That code already exists. Please use a different one.'
    } else {
      err.value = raw || e.message || 'Could not save. Please try again.'
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
      <h2 class="h2">Legal Entity Type List</h2>
      <div v-if="loading" class="muted">Loading…</div>
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
            <tr v-for="row in rows" :key="row.id">
              <td>{{ row.code }}</td>
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

<style scoped>
.table-wrap {
  overflow-x: auto;
}
</style>

