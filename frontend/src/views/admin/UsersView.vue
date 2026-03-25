<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'
import { fetchAllPages } from '../../utils/fetchAllPages'

const rows = ref([])
const loading = ref(true)
const err = ref('')

async function load() {
  loading.value = true
  err.value = ''
  try {
    rows.value = await fetchAllPages('/users/')
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (e.response?.status === 403
        ? 'You do not have permission to view users.'
        : 'Failed to load users.')
    rows.value = []
  } finally {
    loading.value = false
  }
}

function fullName(u) {
  const parts = [u.first_name, u.last_name].map((x) => String(x || '').trim()).filter(Boolean)
  return parts.join(' ') || '—'
}

onMounted(load)
</script>

<template>
  <div class="stack users-page">
    <h2 class="h2">Users</h2>
    <p class="muted">User accounts and roles used by this app.</p>
    <p v-if="err" class="error">{{ err }}</p>

    <div v-if="loading" class="muted">Loading…</div>
    <div v-else-if="rows.length === 0" class="muted">No users found.</div>
    <div v-else class="table-wrap">
      <table class="table users-table">
        <thead>
          <tr>
            <th scope="col">Email</th>
            <th scope="col">Username</th>
            <th scope="col">Name</th>
            <th scope="col">Role</th>
            <th scope="col">Phone</th>
            <th scope="col">Active</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in rows" :key="u.id">
            <td>{{ u.email || '—' }}</td>
            <td>{{ u.username || '—' }}</td>
            <td>{{ fullName(u) }}</td>
            <td>{{ u.role || '—' }}</td>
            <td>{{ u.phone || '—' }}</td>
            <td>{{ u.is_active ? 'Yes' : 'No' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.users-page {
  max-width: 1200px;
}
.table-wrap {
  overflow-x: auto;
}
.users-table {
  font-size: 0.9rem;
}
</style>
