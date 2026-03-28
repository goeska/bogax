<script setup>
import { ref } from 'vue'

const loading = ref(false)
const err = ref('')
const rows = ref([])
const saving = ref(false)

const form = ref({
  name: '',
  is_active: true,
})

function submit() {
  // TODO: Replace with real API call.
  saving.value = true
  err.value = ''
  setTimeout(() => {
    saving.value = false
  }, 300)
}
</script>

<template>
  <div class="stack">
    <section class="card erp-head">
      <p class="erp-kicker">Module Name</p>
      <div class="erp-title-row">
        <h1 class="erp-title">New Menu Name</h1>
        <span class="erp-chip">Context Label</span>
      </div>
      <p class="muted">Short description for this page purpose.</p>
    </section>

    <section class="card">
      <h2 class="h2">Form</h2>
      <form class="form-row" @submit.prevent="submit">
        <label class="field grow">
          <span>Name <span class="req" aria-hidden="true">*</span></span>
          <input v-model="form.name" required maxlength="100" />
        </label>
        <label class="field check">
          <span>Active</span>
          <input v-model="form.is_active" type="checkbox" />
        </label>
        <button class="btn-primary" type="submit" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save' }}
        </button>
      </form>
      <p v-if="err" class="error">{{ err }}</p>
    </section>

    <section class="card">
      <h2 class="h2">List</h2>
      <div class="list-filters">
        <label class="filter-field">
          <span>Search</span>
          <input class="filter-input" type="text" placeholder="Keyword" />
        </label>
        <div class="filter-actions">
          <button type="button" class="btn-edit">Apply</button>
          <button type="button" class="btn-ghost">Clear</button>
        </div>
      </div>

      <div v-if="loading" class="muted">Loading...</div>
      <div v-else-if="rows.length === 0" class="muted">No data yet.</div>
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
                <button type="button" class="link-btn">Edit</button>
                <button type="button" class="link-btn danger">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
