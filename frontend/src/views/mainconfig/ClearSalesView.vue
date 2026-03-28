<script setup>
import { computed, ref } from 'vue'
import { api } from '../../api/client'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const canUse = computed(() => auth.user?.role === 'administrator')

const clearing = ref(false)
const err = ref('')
const result = ref(null)
const confirmPhrase = ref('')

async function runClear() {
  err.value = ''
  result.value = null
  if (confirmPhrase.value.trim() !== 'CLEAR') {
    err.value = 'Type CLEAR in all caps in the box to continue.'
    return
  }
  clearing.value = true
  try {
    const { data } = await api.post('/sales/clear-development-data/')
    result.value = data
    confirmPhrase.value = ''
  } catch (e) {
    result.value = null
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && e.response?.data != null
        ? JSON.stringify(e.response.data)
        : null) ||
      e.message ||
      'Something went wrong.'
  } finally {
    clearing.value = false
  }
}
</script>

<template>
  <div class="stack clear-sales-page">
    <section class="card erp-head erp-head--danger">
      <p class="erp-kicker">Maintenance</p>
      <div class="erp-title-row">
        <h1 class="erp-title">Clear Sales</h1>
        <span class="erp-chip">Development / UAT Only</span>
      </div>
      <p class="muted lead">
        Wipes sales transactions for dev/UAT - don't run this in prod.
      </p>
    </section>

    <div class="card card--danger">
      <h2 class="h2">Clear Sales</h2>
      <p class="muted lead">
        Permanently removes all sales orders, lines, line taxes, and resets sales order document
        codes (<code>SO/…</code>). For development and UAT only — not for production.
      </p>

      <ol class="steps muted small">
        <li>Delete <code>sales_order_line_tax</code></li>
        <li>Delete <code>sales_order_line</code></li>
        <li>Delete <code>sales_order</code></li>
        <li>Reset <code>code_counter</code> for sales order codes (family <code>SO</code>)</li>
      </ol>

      <p v-if="!canUse" class="error">
        Only users with role <strong>Administrator</strong> can use this screen.
      </p>

      <template v-else>
        <label class="field">
          <span>Type <strong>CLEAR</strong> to confirm</span>
          <input
            v-model="confirmPhrase"
            type="text"
            autocomplete="off"
            placeholder="CLEAR"
            :disabled="clearing"
          />
        </label>
        <p v-if="err" class="error">{{ err }}</p>
        <div v-if="result" class="ok-block">
          <p class="ok">{{ result.detail }}</p>
          <ul class="deleted-list muted small">
            <li v-for="(n, key) in result.deleted" :key="key">
              <code>{{ key }}</code>: {{ n }}
            </li>
          </ul>
        </div>
        <button
          type="button"
          class="btn-danger"
          :disabled="clearing"
          @click="runClear"
        >
          {{ clearing ? 'Clearing…' : 'Clear all sales data' }}
        </button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.clear-sales-page {
  max-width: 640px;
}
.lead {
  margin: 0.25rem 0 1rem;
  font-size: 0.95rem;
}
.card--danger {
  border-color: #fecaca;
  background: #fffafa;
}
.steps {
  margin: 0 0 1.25rem;
  padding-left: 1.25rem;
  line-height: 1.5;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1rem;
  max-width: 20rem;
}
.btn-danger {
  padding: 0.5rem 1rem;
  font-weight: 600;
  color: #fff;
  background: #b91c1c;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.btn-danger:hover:not(:disabled) {
  background: #991b1b;
}
.btn-danger:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.ok-block {
  margin-bottom: 1rem;
}
.ok {
  color: #15803d;
  font-weight: 600;
  margin: 0 0 0.5rem;
}
.deleted-list {
  margin: 0;
  padding-left: 1.25rem;
}
code {
  font-size: 0.85em;
}
</style>
