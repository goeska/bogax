<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { deactivateErrorMessage, softDeactivate } from '../../api/softDeactivate'

const rows = ref([])
const categories = ref([])
const uoms = ref([])
const loading = ref(true)
const err = ref('')
const form = ref({
  name: '',
  product_category_id: null,
  uom_id: null,
  is_active: true,
  unit_price: '',
})
const editingId = ref(null)
const saving = ref(false)

const categoryById = computed(() => {
  const m = new Map()
  for (const c of categories.value) m.set(c.id, c.name)
  return m
})

const uomById = computed(() => {
  const m = new Map()
  for (const u of uoms.value) m.set(u.id, u.name)
  return m
})

function defaultForm() {
  return {
    name: '',
    product_category_id: null,
    uom_id: null,
    is_active: true,
    unit_price: '',
  }
}

async function loadRefs() {
  const [cat, uom] = await Promise.all([
    api.get('/product-categories/'),
    api.get('/uoms/'),
  ])
  categories.value = cat.data.results ?? cat.data
  uoms.value = uom.data.results ?? uom.data
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    await loadRefs()
    const { data } = await api.get('/products/')
    rows.value = data.results ?? data
  } catch {
    err.value = 'Failed to load products.'
  } finally {
    loading.value = false
  }
}

function startEdit(row) {
  editingId.value = row.id
  form.value = {
    name: row.name,
    product_category_id: row.product_category_id,
    uom_id: row.uom_id,
    is_active: row.is_active,
    unit_price:
      row.unit_price === null || row.unit_price === undefined ? '' : String(row.unit_price),
  }
  err.value = ''
}

function cancelEdit() {
  editingId.value = null
  form.value = defaultForm()
}

function buildPayload() {
  const payload = {
    name: form.value.name,
    product_category_id: form.value.product_category_id,
    uom_id: form.value.uom_id,
    is_active: form.value.is_active,
  }
  const up = String(form.value.unit_price).trim()
  if (up === '') {
    payload.unit_price = null
  } else {
    const n = Number(up)
    if (Number.isNaN(n)) {
      throw new Error('Unit price must be numeric or empty.')
    }
    payload.unit_price = n
  }
  return payload
}

async function submit() {
  saving.value = true
  err.value = ''
  try {
    const payload = buildPayload()
    if (editingId.value != null) {
      await api.patch(`/products/${editingId.value}/`, payload)
    } else {
      await api.post('/products/', payload)
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
  if (!confirm(`Delete product "${row.name}"?`)) return
  err.value = ''
  try {
    await softDeactivate(api, 'products', row.id)
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
      <h2 class="h2">{{ editingId != null ? 'Edit Product' : 'Add Product' }}</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field grow">
          <span>Name</span>
          <input v-model="form.name" required maxlength="255" />
        </label>
        <label class="field grow">
          <span>Category</span>
          <select v-model="form.product_category_id" required>
            <option :value="null" disabled>Select…</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>
        </label>
        <label class="field grow">
          <span>UOM</span>
          <select v-model="form.uom_id" required>
            <option :value="null" disabled>Select…</option>
            <option v-for="u in uoms" :key="u.id" :value="u.id">
              {{ u.name }}
            </option>
          </select>
        </label>
        <label class="field narrow">
          <span>Unit Price (optional)</span>
          <input
            v-model="form.unit_price"
            type="number"
            step="0.01"
            min="0"
            placeholder="—"
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
      <h2 class="h2">Product List</h2>
      <div v-if="loading" class="muted">Loading…</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>UOM</th>
            <th>Price</th>
            <th>Active</th>
            <th class="col-actions" />
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td>{{ row.name }}</td>
            <td>{{ categoryById.get(row.product_category_id) ?? row.product_category_id }}</td>
            <td>{{ uomById.get(row.uom_id) ?? row.uom_id }}</td>
            <td>{{ row.unit_price ?? '—' }}</td>
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
